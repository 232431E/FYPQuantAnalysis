import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from flask import g
from flask_testing import TestCase
from sqlalchemy import create_engine
from backend.app import app  # Import your Flask application
from sqlalchemy.orm import Session, sessionmaker
from backend.models import data_model
from backend.models.data_model import Base
from datetime import date
from backend.database import get_engine, get_session_local, get_db, close_db, init_db
import backend.database as database
from backend.models import report_model, user_model
import sqlalchemy

class TestDashboardAPI(TestCase):
    test_session = None
    test_company_id = None

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # Force in-memory SQLite
        return app

    @classmethod
    def setUpClass(cls):
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        cls.test_session = get_session_local()()
        db = cls.test_session
        try:
            company = db.query(data_model.Company).filter_by(ticker_symbol="TCP").first()
            if not company:
                company = data_model.Company(company_name="Test Corp", ticker_symbol="TCP")
                db.add(company)
                db.commit()
            cls.test_company_id = company.company_id

            # Add news items once in setUpClass
            cls.news_items = [
                data_model.News(company_id=cls.test_company_id, title="News 1", link="http://news1.com"),
                data_model.News(company_id=cls.test_company_id, title="News 2", link="http://news2.com")
            ]
            db.add_all(cls.news_items)
            db.commit()

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls):
        engine = get_engine()
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Disable foreign key checks
                connection.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 0"))

                # Drop all tables
                Base.metadata.drop_all(bind=connection) # Bind to the connection

                # Re-enable foreign key checks
                connection.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 1"))

                trans.commit()
            except:
                trans.rollback()
                raise
            finally:
                pass # Connection is automatically closed by the context manager

        if cls.test_session:
            cls.test_session.close()
    
    def setUp(self):
        self.db = TestDashboardAPI.test_session # Use the class-level session
        self.db.rollback() # Ensure a clean state for each test

        # Clear existing news for the test company
        self.db.query(data_model.News).filter(data_model.News.company_id == TestDashboardAPI.test_company_id).delete()
        self.db.commit()

        # Add test financial data
        today = date(2025, 4, 11)
        yesterday = date(2025, 4, 10)
        two_days_ago = date(2025, 4, 9)
        last_week = date(2025, 4, 4)
        last_month_same_day = date(2025, 3, 11)
        last_year_same_day = date(2024, 4, 11)

        self.financial_data = [
            data_model.FinancialData(company_id=TestDashboardAPI.test_company_id, date=today, open=10.0, close=11.0, volume=100),
            data_model.FinancialData(company_id=TestDashboardAPI.test_company_id, date=yesterday, open=10.5, close=11.5, volume=110),
            data_model.FinancialData(company_id=TestDashboardAPI.test_company_id, date=two_days_ago, open=11.0, close=12.0, volume=120),
            data_model.FinancialData(company_id=TestDashboardAPI.test_company_id, date=last_week, open=12.0, close=13.0, volume=130),
            data_model.FinancialData(company_id=TestDashboardAPI.test_company_id, date=last_month_same_day, open=13.0, close=14.0, volume=140),
            data_model.FinancialData(company_id=TestDashboardAPI.test_company_id, date=last_year_same_day, open=14.0, close=15.0, volume=150)
        ]
        self.db.add_all(self.financial_data)
        self.db.commit()

        # Add news items
        self.news_items = [
            data_model.News(company_id=TestDashboardAPI.test_company_id, title="News 1", link="http://news1.com"),
            data_model.News(company_id=TestDashboardAPI.test_company_id, title="News 2", link="http://news2.com")
        ]
        self.db.add_all(self.news_items)
        self.db.commit()

        with self.client.session_transaction() as sess:
            sess['selected_company_id'] = TestDashboardAPI.test_company_id

    def tearDown(self):
        self.db.rollback()

    def get_db_override():
        return TestDashboardAPI.test_session

    database.get_db = get_db_override

    def test_get_daily_financial_data(self):
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=daily')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(f"Daily financial data in test: {data}")
        self.assertGreaterEqual(len(data), 2)

    def test_get_weekly_financial_data(self):
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=weekly')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(f"Weekly financial data in test: {data}")
        self.assertGreaterEqual(len(data), 1)

    def test_get_monthly_financial_data(self):
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=monthly')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(f"Monthly financial data in test: {data}")
        self.assertGreaterEqual(len(data), 1)

    def test_get_yearly_financial_data(self):
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=yearly')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(f"Yearly financial data in test: {data}")
        self.assertGreaterEqual(len(data), 1)

    def test_get_latest_news(self):
        with self.client.session_transaction() as sess:
            sess['selected_company_id'] = self.test_company_id
        response = self.client.get('/api/news')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(f"Latest news in test: {data}")
        self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main()