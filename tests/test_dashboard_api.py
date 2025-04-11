import unittest
from flask_testing import TestCase
from sqlalchemy import create_engine
from backend.app import app  # Import your Flask application
from backend.database import Base, get_db
from sqlalchemy.orm import Session, sessionmaker
from backend.models import data_model
from datetime import date

# Override get_db for testing to use an in-memory SQLite database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

from backend import database
database.get_db = override_get_db

# Create the tables *after* setting up the engine
Base.metadata.create_all(bind=engine)
print(Base.metadata.tables)

class TestDashboardAPI(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.db: Session = next(override_get_db())
        # Create a test company
        company = data_model.Company(company_name="Test Corp", ticker_symbol="TCP")
        self.db.add(company)
        self.db.commit()
        self.test_company_id = company.company_id

        # Add some test financial data for different dates to test aggregation
        today = date.today()
        yesterday = date(today.year, today.month, today.day - 1)
        two_days_ago = date(today.year, today.month, today.day - 2)
        last_week = date(today.year, today.month, today.day - 7)
        last_month_same_day = date(today.year, today.month - 1, today.day)
        last_year_same_day = date(today.year - 1, today.month, today.day)

        self.db.add(data_model.FinancialData(company_id=self.test_company_id, date=today, open=10.0, close=11.0, volume=100))
        self.db.add(data_model.FinancialData(company_id=self.test_company_id, date=yesterday, open=10.5, close=11.5, volume=110))
        self.db.add(data_model.FinancialData(company_id=self.test_company_id, date=two_days_ago, open=11.0, close=12.0, volume=120))
        self.db.add(data_model.FinancialData(company_id=self.test_company_id, date=last_week, open=12.0, close=13.0, volume=130))
        self.db.add(data_model.FinancialData(company_id=self.test_company_id, date=last_month_same_day, open=13.0, close=14.0, volume=140))
        self.db.add(data_model.FinancialData(company_id=self.test_company_id, date=last_year_same_day, open=14.0, close=15.0, volume=150))
        self.db.commit()

        # Add some test news
        self.db.add(data_model.News(company_id=self.test_company_id, title="News 1", url="http://news1.com"))
        self.db.add(data_model.News(company_id=self.test_company_id, title="News 2", url="http://news2.com"))
        self.db.commit()

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_get_daily_financial_data(self):
        print("\n--- Testing get_daily_financial_data ---")
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=daily')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = response.json
        print(f"Response data: {data}")
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)
        self.assertIn('date', data[0])
        self.assertIn('open', data[0])
        self.assertIn('close', data[0])
        self.assertIn('volume', data[0])

    def test_get_weekly_financial_data(self):
        print("\n--- Testing get_weekly_financial_data ---")
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=weekly')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = response.json
        print(f"Response data: {data}")
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        if data:
            self.assertIn('week', data[0])
            self.assertIn('avg_open', data[0])
            self.assertIn('avg_close', data[0])
            self.assertIn('total_volume', data[0])

    def test_get_monthly_financial_data(self):
        print("\n--- Testing get_monthly_financial_data ---")
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=monthly')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = response.json
        print(f"Response data: {data}")
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        if data:
            self.assertIn('month', data[0])
            self.assertIn('avg_open', data[0])
            self.assertIn('avg_close', data[0])
            self.assertIn('total_volume', data[0])

    def test_get_yearly_financial_data(self):
        print("\n--- Testing get_yearly_financial_data ---")
        response = self.client.get(f'/api/companies/{self.test_company_id}/financials?period=yearly')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = response.json
        print(f"Response data: {data}")
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        if data:
            self.assertIn('year', data[0])
            self.assertIn('avg_open', data[0])
            self.assertIn('avg_close', data[0])
            self.assertIn('total_volume', data[0])

    def test_get_latest_news(self):
        print("\n--- Testing get_latest_news ---")
        with self.client.session_transaction() as sess:
            sess['selected_company_id'] = self.test_company_id
        response = self.client.get('/api/news')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = response.json
        print(f"Response data: {data}")
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertIn('title', data[0])
        self.assertIn('url', data[0])

if __name__ == '__main__':
    unittest.main()