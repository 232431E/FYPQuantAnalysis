# tests/test_tasks.py
# test for autoamted data retrieval
import sys
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import pytz
import unittest
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Add the path to the 'backend' directory to sys.path
# This assumes that 'backend' is a sibling directory to 'tests'
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

# Import the necessary modules from backend.app
from backend.app import create_app
from backend.tasks import daily_financial_data_update, daily_news_update  # Import the functions directly
from backend.database import get_db  # Import get_db
from backend.models.data_model import Company, FinancialData, News  # Import your models


class TestDailyFinancialDataUpdate(unittest.TestCase):
    def setUp(self):
        # Setup a test Flask app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        self.Base = declarative_base()
        self.Base.metadata.create_all(self.engine)
        self.TestingSessionLocal = sessionmaker(bind=self.engine)
        self.db = SQLAlchemy()
        self.db.init_app(self.app)

        # Create an application context for the tests
        self.app_context = self.app.app_context()
        self.app_context.push()
        with self.app_context:
            self.db.create_all()

    def tearDown(self):
        # Clean up the application context
        self.app_context.pop()

    @patch('backend.tasks.get_db')  # Mock get_db at the tasks level
    def test_daily_update_weekday_6am(self, mock_get_db):
        """Test daily update on a weekday at 6:00 AM."""
        sgt_tz = pytz.timezone('Asia/Singapore')
        now = sgt_tz.localize(datetime(2025, 4, 22, 6, 0))

        # Create a mock session
        mock_session = MagicMock()
        mock_get_db.return_value = mock_session

        # Patch datetime.now to return the desired time
        with patch('backend.tasks.datetime') as mock_datetime:
            mock_datetime.now.return_value = now

            # Create mock companies
            company1 = Company(ticker_symbol='AAPL')
            company2 = Company(ticker_symbol='GOOG')

            # Patch get_all_companies
            with patch('backend.tasks.get_all_companies') as mock_get_all:
                mock_get_all.return_value = [company1, company2]

                # Patch store_financial_data
                with patch('backend.tasks.store_financial_data') as mock_store:
                    # Call the function within the application context
                    with self.app.app_context():
                        daily_financial_data_update(self.app)
                        mock_get_all.assert_called_once_with(mock_session)
                        expected_calls = [
                            call(mock_session, 'AAPL', period='1d'),
                            call(mock_session, 'GOOG', period='1d'),
                        ]
                        actual_calls = mock_store.mock_calls
                        # Check if all expected calls are present, ignoring extra calls
                        self.assertTrue(all(ec in actual_calls for ec in expected_calls))

    def test_daily_update_weekend(self):
        """Test daily update on a weekend."""
        sgt_tz = pytz.timezone('Asia/Singapore')
        now = sgt_tz.localize(datetime(2025, 4, 26, 6, 0))

        # Patch datetime.now to return the desired time
        with patch('backend.tasks.datetime') as mock_datetime:
            mock_datetime.now.return_value = now
            with patch('backend.tasks.get_all_companies') as mock_get_all:
                # Call the function
                daily_financial_data_update(self.app)

                # Assertions
                mock_get_all.assert_not_called()

    @patch('backend.tasks.get_db')  # Mock get_db at the tasks level
    def test_daily_news_update(self, mock_get_db):
        """Tests the daily_news_update task."""
        sgt_tz = pytz.timezone('Asia/Singapore')
        now = sgt_tz.localize(datetime(2024, 1, 2, 6, 0))

        # Create a mock session
        mock_session = MagicMock()  # Define mock_session here
        mock_get_db.return_value = mock_session

        # Patch datetime.now
        with patch('backend.tasks.datetime') as mock_datetime:
            mock_datetime.now.return_value = now
            # Create mock companies in the database
            company1 = Company(company_name="Test Company 1", ticker_symbol="TEST1", industry="Test Industry",
                               exchange="Test Exchange", company_id=1)  # Added company_id
            company2 = Company(company_name="Test Company 2", ticker_symbol="TEST2", industry="Test Industry",
                               exchange="Test Exchange", company_id=2)  # Added company_id

            # Mock the news fetching to return some sample data
            mock_fetch_news_return = (
                [{"title": "Test News 1", "link": "http://example.com/news1", "published_date": now,
                  "summary": "Summary 1"}],
                [{"title": "Industry News 1", "link": "http://example.com/industry1",
                  "published_date": now,
                  "summary": "Industry Summary 1"}]
            )
            # Patch fetch_latest_news
            with patch('backend.tasks.fetch_latest_news') as mock_fetch_news:
                mock_fetch_news.return_value = mock_fetch_news_return
                # Patch get_all_companies
                with patch('backend.tasks.get_all_companies') as mock_get_all_companies:
                    mock_get_all_companies.return_value = [company1, company2]
                    # Patch store_news_articles
                    with patch('backend.tasks.store_news_articles') as mock_store_news:

                        # Call the task function directly with the test app
                        with self.app.app_context():
                            daily_news_update(self.app)

                            expected_calls = [
                                call(mock_session, 1, [{"title": "Test News 1", "link": "http://example.com/news1", "published_date": now, "summary": "Summary 1"}], "company"),
                                call(mock_session, 1, [{"title": "Industry News 1", "link": "http://example.com/industry1", "published_date": now, "summary": "Industry Summary 1"}], "industry"),
                                call(mock_session, 2, [{"title": "Test News 1", "link": "http://example.com/news1", "published_date": now, "summary": "Summary 1"}], "company"),
                                call(mock_session, 2, [{"title": "Industry News 1", "link": "http://example.com/industry1", "published_date": now, "summary": "Industry Summary 1"}], "industry"),
                            ]
                            actual_calls = mock_store_news.mock_calls
                            # Check if all expected calls are present, ignoring order or extra calls
                            self.assertTrue(all(ec in actual_calls for ec in expected_calls))
