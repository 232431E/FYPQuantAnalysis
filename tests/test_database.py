import unittest
from backend.models.data_model import Company, News  # Adjust import paths
from datetime import date, datetime, timedelta
import pytest  # Import pytest

from backend.database import get_company_by_ticker, create_company, create_news, get_news_by_company, delete_news_by_date


class TestDatabaseOperations:  # Remove the inheritance from unittest.TestCase

    def test_create_and_get_company(self, db_session):  # Use db_session fixture
        company_data = {"company_name": "Test Company", "ticker_symbol": "TEST", "exchange": "TESTEX"}
        created_company = create_company(db_session, company_data)
        assert created_company.company_id is not None
        retrieved_company = get_company_by_ticker(db_session, "TEST")
        assert retrieved_company.company_name == "Test Company"
        assert retrieved_company.ticker_symbol == "TEST"

    def test_create_and_get_news(self, db_session):  # Use db_session
        company_data = {"company_name": "News Company", "ticker_symbol": "NEWS"}
        company = create_company(db_session, company_data)
        assert company.company_id is not None

        news_item = {
            "company_id": company.company_id,
            "title": "Test News Title",
            "description": "Test news description.",
            "url": "http://test.com",
            "published_at": datetime.now()
        }
        created_news = create_news(db_session, news_item)
        assert created_news.news_id is not None

        retrieved_news = get_news_by_company(db_session, company.company_id)
        assert len(retrieved_news) == 1
        assert retrieved_news[0].title == "Test News Title"

    def test_delete_news_by_date(self, db_session): # Use db_session
        company_data = {"company_name": "Delete News Co", "ticker_symbol": "DELNEWS"}
        company = create_company(db_session, company_data)
        assert company.company_id is not None

        today = date.today()
        yesterday = today - timedelta(days=1)

        news_today = {"company_id": company.company_id, "title": "Today's News", "published_at": datetime.combine(today, datetime.min.time())}
        news_yesterday = {"company_id": company.company_id, "title": "Yesterday's News", "published_at": datetime.combine(yesterday, datetime.min.time())}

        create_news(db_session, news_today)
        create_news(db_session, news_yesterday)

        deleted_count = delete_news_by_date(db_session, company.company_id, today)
        assert deleted_count == 1

        remaining_news = get_news_by_company(db_session, company.company_id)
        assert len(remaining_news) == 1
        assert remaining_news[0].title == "Yesterday's News"