# tests/test_database.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.models.data_model import Base, Company, News
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import get_company_by_ticker, create_company, create_news, get_news_by_company, delete_news_by_date
from datetime import date, datetime, timedelta

# Use an in-memory SQLite database for testing to avoid affecting your main database
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency for testing
from backend import database
database.get_db = override_get_db

class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        self.db = next(override_get_db())

    def tearDown(self):
        self.db.close()

    def test_create_and_get_company(self):
        company_data = {"company_name": "Test Company", "ticker_symbol": "TEST", "exchange": "TESTEX"}
        print(f"Testing create_company with: {company_data}") # Debug print
        created_company = create_company(self.db, company_data)
        self.assertIsNotNone(created_company.company_id)
        retrieved_company = get_company_by_ticker(self.db, "TEST")
        print(f"Retrieved company: {retrieved_company.__dict__ if retrieved_company else None}") # Debug print
        self.assertEqual(retrieved_company.company_name, "Test Company")
        self.assertEqual(retrieved_company.ticker_symbol, "TEST")
        
    def test_create_and_get_news(self):
        company_data = {"company_name": "News Company", "ticker_symbol": "NEWS"}
        company = create_company(self.db, company_data)
        self.assertIsNotNone(company.company_id)

        news_item = {
            "company_id": company.company_id,
            "title": "Test News Title",
            "description": "Test news description.",
            "url": "http://test.com",
            "published_at": datetime.now()
        }
        created_news = create_news(self.db, news_item)
        self.assertIsNotNone(created_news.news_id)

        retrieved_news = get_news_by_company(self.db, company.company_id)
        self.assertEqual(len(retrieved_news), 1)
        self.assertEqual(retrieved_news[0].title, "Test News Title")

    def test_delete_news_by_date(self):
        company_data = {"company_name": "Delete News Co", "ticker_symbol": "DELNEWS"}
        company = create_company(self.db, company_data)
        self.assertIsNotNone(company.company_id)

        today = date.today()
        yesterday = today - timedelta(days=1)

        news_today = {"company_id": company.company_id, "title": "Today's News", "published_at": datetime.combine(today, datetime.min.time())}
        news_yesterday = {"company_id": company.company_id, "title": "Yesterday's News", "published_at": datetime.combine(yesterday, datetime.min.time())}

        create_news(self.db, news_today)
        create_news(self.db, news_yesterday)

        deleted_count = delete_news_by_date(self.db, company.company_id, today)
        self.assertEqual(deleted_count, 1)

        remaining_news = get_news_by_company(self.db, company.company_id)
        self.assertEqual(len(remaining_news), 1)
        self.assertEqual(remaining_news[0].title, "Yesterday's News")

if __name__ == '__main__':
    unittest.main()