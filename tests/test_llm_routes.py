# tests/test_llm_routes.py
import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from backend.app import create_app, db  # Import create_app AND db
from backend.database import Base, close_db, get_company, get_db
from backend.models import News, Company  # Import your SQLAlchemy models
from backend.services.llm_service import analyze_news_sentiment_gemini  # Import the LLM service function
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from flask_sqlalchemy import SQLAlchemy
import json
import logging
import datetime
import importlib
import backend.routes.llm_routes 
from werkzeug.exceptions import NotFound 

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestLLMRoutes(unittest.TestCase):
    """
    Comprehensive test case for LLM routes, verifying:
    - Fetching company details and news from the database.
    - Generating prompts for the LLM based on fetched data.
    - Mocking the LLM service to isolate testing.
    - Checking response structure and content for various scenarios.
    """

    def setUp(self):
        # 1. Set up a test Flask application
        self.app = create_app(testing=True, start_scheduler =False)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        @self.app.errorhandler(NotFound)
        def not_found_error(error):
            logger.debug(f"Handling NotFound error on app in test context: {error}")
            response = jsonify({'error': error.description})
            response.status_code = 404
            return response
             
        logger.debug("NotFound error handler registered in setUp.")
        logger.debug(f"App config SQLALCHEMY_DATABASE_URI: {self.app.config.get('SQLALCHEMY_DATABASE_URI')}")

        # 4. Create database tables and populate with test data (within context)
        with self.app_context:
            db.create_all()  # Use the imported 'db' instance
            db_session = get_db()
            logger.debug(f"Database session in setUp: {db_session}")
            logger.debug(f"Database engine in setUp: {db_session.bind}")
            try:
                existing_company = db_session.query(Company).filter_by(company_id=1).first()
                if not existing_company:
                    # Create a sample company for testing
                    self.test_company = Company(
                        company_id=1,
                        company_name="Tech Innovators Corp",
                        ticker_symbol="TINC",
                        industry="Technology",
                        exchange="NASDAQ"
                    )
                    db_session.add(self.test_company)
                    db_session.commit()
                    logger.debug("Test company created in setUp.")
                else:
                    self.test_company = existing_company
                    logger.debug("Test company already exists in setUp.")

                retrieved_company = db_session.query(Company).filter_by(company_id=1).first()
                self.assertIsNotNone(retrieved_company, "Test company not created in setUp")
                self.assertEqual(retrieved_company.company_name, "Tech Innovators Corp", "Company name mismatch in setUp")
                self.assertEqual(retrieved_company.ticker_symbol, "TINC", "Ticker symbol mismatch in setUp")
                logger.debug(f"Test company in DB: {retrieved_company}")
            finally:
                db_session.close()

        importlib.reload(backend.routes.llm_routes)
        # 5. Scheduler should not start because testing=True
        pass

    def tearDown(self):
        # 1. Clean up the database and application context
        self.app_context.pop()
        with self.app.app_context():
            db.drop_all()  # Use the imported 'db' instance
            logger.debug(f"Database dropped in tearDown.")

    def test_get_company_from_db(self):
         with self.app.app_context():
            db_session = get_db()
            company = get_company(db_session, 1)
            self.assertEqual(company.company_name, "Tech Innovators Corp")
            self.assertEqual(company.ticker_symbol, "TINC")
            company_not_found = get_company(db_session, 999)
            self.assertIsNone(company_not_found)
            close_db()

    @patch('backend.routes.llm_routes.analyze_news_sentiment_gemini')
    def test_get_llm_report_generation_success(self, mock_analyze_gemini):
        """
        Tests the /api/llm/report/<company_id> endpoint with valid data.
        - Mocks the LLM service function.
        - Verifies successful response, data structure, and LLM input.
        """
        logger.debug("Running test_get_llm_report_generation_success")

        # 2. Add news to the database for the test company
        with self.app.app_context():
            db_session = get_db()
            test_news = [
                News(company_id=1, title="Product Launch Success", summary="New product launch successful.",
                     link="https://example.com/launch", published_date=datetime.date(2025, 5, 15)),
                News(company_id=1, title="Supply Chain Issues", summary="Supply chain disruptions reported.",
                     link="https://example.com/supplychain", published_date=datetime.date(2025, 5, 10)),
                News(company_id=1, title="Positive Earnings", summary="Earnings exceed expectations.",
                     link="https://example.com/earnings", published_date=datetime.date(2025, 5, 1)),
            ]
            db_session.add_all(test_news)
            try:
                db_session.commit()
                logger.debug("Test news added to the database.")
            except Exception as e:
                logger.error(f"Error adding test news: {e}")
                db_session.rollback()
                raise
            finally:
                db_session.close()

        # 3. Configure the mock to return a JSON-serializable dict
        mock_analyze_gemini.return_value = {
            "overall_summary": "Positive outlook",
            "sentiment_analysis": {"brief": "Positive", "sentiment": "Positive"},
            "full_report": "Detailed analysis...",
            "company_name": "Tech Innovators Corp",
            "ticker_symbol": "TINC"
        }
        logger.debug(f"Mock return value set to: {mock_analyze_gemini.return_value}")
        # 4. Call the LLM report endpoint
        response = self.client.get('/api/llm/report/1')
        print(f"Mock return value: {mock_analyze_gemini.return_value}")  # Add this
        data = response.get_json()
        print(f"Response data: {json.dumps(data, indent=2)}")
        
        # 5. Assertions
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        logger.debug(f"Response data: {json.dumps(data, indent=2)}")

        self.assertIn('report', data)
        report = data['report']
        self.assertIn('company_name', report)
        self.assertEqual(report['company_name'], "Tech Innovators Corp")
        self.assertEqual(report['ticker_symbol'], "TINC")

        # 6. Verify LLM call
        mock_analyze_gemini.assert_called_once()
        args, kwargs = mock_analyze_gemini.call_args
        news_articles_passed = args[0]

        # Verify the news articles passed to the LLM.
        self.assertEqual(len(news_articles_passed), 3)
        self.assertEqual(news_articles_passed[0]['title'], "Product Launch Success")
        self.assertEqual(news_articles_passed[1]['title'], "Supply Chain Issues")
        self.assertEqual(news_articles_passed[2]['title'], "Positive Earnings")

        self.assertEqual(kwargs['llm_model'], 'gemini-pro')

        
    def test_get_llm_report_generation_company_not_found(self):
        """
        Tests /api/llm/report/<company_id> with a non-existent company ID.
        - Verifies 404 response and error message.
        """
        logger.debug("Running test_get_llm_report_generation_company_not_found")
        with self.app.app_context():
            with self.assertRaises(NotFound) as context:
                self.client.get('/api/llm/report/999')
            self.assertEqual(context.exception.code, 404)
            self.assertEqual(context.exception.description, "Company not found")

    @patch('backend.routes.llm_routes.analyze_news_sentiment_gemini')
    def test_get_llm_report_generation_no_news(self, mock_analyze_gemini):
        """
        Tests /api/llm/report/<company_id> when no news is available for a company.
        - Verifies that the LLM is called with empty news.
        - Verifies that a default neutral report is returned.
        """
        logger.debug("Running test_get_llm_report_generation_no_news")

        response = self.client.get('/api/llm/report/1')
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response data: {response.get_json()}")
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('report', data)
        report = data['report']
        self.assertEqual(report['company_name'], "Tech Innovators Corp")
        self.assertEqual(report['ticker_symbol'], "TINC")
        self.assertEqual(report['overall_news_summary'], "No news available.")
        self.assertEqual(report['sentiment_analysis']['sentiment'], "Neutral")

        # Verify LLM call: Crucially, check that it was NOT called.
        mock_analyze_gemini.assert_not_called()