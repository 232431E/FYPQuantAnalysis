# tests/test_news_retrieval.py
import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from sqlalchemy.orm import Session
from backend.services.data_service import fetch_daily_news
from backend.database import get_company_by_ticker, create_company, delete_news_by_date
from backend.models.data_model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time  # Import the time module

# Use an in-memory SQLite database for testing
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

class TestNewsRetrieval(unittest.TestCase):

    def setUp(self):
        self.db = next(override_get_db())
        # Create a test company only if it doesn't exist
        if get_company_by_ticker(self.db, "YHOO") is None:
            company_data = {"company_name": "Yahoo Test Co", "ticker_symbol": "YHOO"}
            create_company(self.db, company_data)
        self.test_company = get_company_by_ticker(self.db, "YHOO")
        self.assertIsNotNone(self.test_company)

    def tearDown(self):
        self.db.rollback()  # Rollback any open transactions
        self.db.close()

    @patch('yfinance.Ticker')
    def test_fetch_daily_news_success(self, mock_ticker):
        mock_news_data = [
            {"title": "News 1", "summary": "Summary 1", "link": "http://news1.com", "publishedAt": int(time.time())}, # Use current timestamp as int
            {"title": "News 2", "summary": "Summary 2", "link": "http://news2.com", "publishedAt": int(time.time()) + 100}, # Use current timestamp + 100
        ]
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.news = mock_news_data
        mock_ticker.return_value = mock_ticker_instance

        today = date.today()
        fetch_daily_news(self.db, "YHOO", today)

        retrieved_news = self.db.query(database.data_model.News).filter_by(company_id=self.test_company.company_id).all()
        self.assertEqual(len(retrieved_news), 2)
        self.assertEqual(retrieved_news[0].title, "News 1")
        self.assertEqual(retrieved_news[1].title, "News 2")

        # Optionally check if published_at is a datetime object
        self.assertIsInstance(retrieved_news[0].published_at, datetime)

    @patch('yfinance.Ticker')
    def test_fetch_daily_news_empty(self, mock_ticker):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.news = []
        mock_ticker.return_value = mock_ticker_instance

        today = date.today()
        fetch_daily_news(self.db, "YHOO", today)
        retrieved_news = self.db.query(database.data_model.News).filter_by(company_id=self.test_company.company_id).all()
        self.assertEqual(len(retrieved_news), 0)

    @patch('yfinance.Ticker')
    def test_fetch_daily_news_duplicate_prevention(self, mock_ticker):
        mock_news_data = [{"title": "Existing News", "summary": "...", "link": "...", "publishedAt": int(time.time())}]
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.news = mock_news_data
        mock_ticker.return_value = mock_ticker_instance

        today = date.today()
        # Create some existing news for today
        existing_news = database.data_model.News(company_id=self.test_company.company_id, title="Existing News", published_at=datetime.combine(today, datetime.min.time()))
        self.db.add(existing_news)
        self.db.commit()

        fetch_daily_news(self.db, "YHOO", today)
        retrieved_news = self.db.query(database.data_model.News).filter_by(company_id=self.test_company.company_id).all()
        # Should still be 1 (the new one overwrites the old one for the same day)
        self.assertEqual(len(retrieved_news), 1)
        self.assertEqual(retrieved_news[0].title, "Existing News")
        self.assertIsInstance(retrieved_news[0].published_at, datetime)

if __name__ == '__main__':
    unittest.main()