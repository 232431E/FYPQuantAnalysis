#tests/test_news_retrieval.py

import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import pytest # Import pytest
import time
from backend.services.data_service import fetch_daily_news
from backend.database import get_company_by_ticker
from backend.models.data_model import News # Import News

class TestNewsRetrieval: # Remove unittest inheritance

    def test_fetch_daily_news_success(self, db_session): # Use db_session
        mock_ticker = MagicMock()
        mock_news_data = [
            {"title": "News 1", "summary": "Summary 1", "link": "http://news1.com", "publishedAt": int(time.time())},
            {"title": "News 2", "summary": "Summary 2", "link": "http://news2.com", "publishedAt": int(time.time()) + 100},
        ]
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.news = mock_news_data
        mock_ticker.return_value = mock_ticker_instance

        company_data = {"company_name": "Yahoo Test Co", "ticker_symbol": "YHOO"}
        if get_company_by_ticker(db_session, "YHOO") is None:
            create_company(db_session, company_data)
        test_company = get_company_by_ticker(db_session, "YHOO")
        assert test_company is not None

        today = date.today()
        fetch_daily_news(db_session, "YHOO", today)

        retrieved_news = db_session.query(News).filter_by(company_id=test_company.company_id).all()
        assert len(retrieved_news) == 2
        assert retrieved_news[0].title == "News 1"
        assert retrieved_news[1].title == "News 2"
        assert isinstance(retrieved_news[0].published_at, datetime)

    def test_fetch_daily_news_empty(self, db_session): # Use db_session
        mock_ticker = MagicMock()
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.news = []
        mock_ticker.return_value = mock_ticker_instance
        company_data = {"company_name": "Yahoo Test Co", "ticker_symbol": "YHOO"}
        if get_company_by_ticker(db_session, "YHOO") is None:
            create_company(db_session, company_data)
        test_company = get_company_by_ticker(db_session, "YHOO")


        today = date.today()
        fetch_daily_news(db_session, "YHOO", today)
        retrieved_news = db_session.query(News).filter_by(company_id=test_company.company_id).all()
        assert len(retrieved_news) == 0

    def test_fetch_daily_news_duplicate_prevention(self, db_session): # Use db_session
        mock_ticker = MagicMock()
        mock_news_data = [{"title": "Existing News", "summary": "...", "link": "...", "publishedAt": int(time.time())}]
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.news = mock_news_data
        mock_ticker.return_value = mock_ticker_instance
        company_data = {"company_name": "Yahoo Test Co", "ticker_symbol": "YHOO"}
        if get_company_by_ticker(db_session, "YHOO") is None:
            create_company(db_session, company_data)
        test_company = get_company_by_ticker(db_session, "YHOO")

        today = date.today()
        existing_news = News(company_id=test_company.company_id, title="Existing News", published_at=datetime.combine(today, datetime.min.time()))
        db_session.add(existing_news)
        db_session.commit()

        fetch_daily_news(db_session, "YHOO", today)
        retrieved_news = db_session.query(News).filter_by(company_id=test_company.company_id).all()
        assert len(retrieved_news) == 1
        assert retrieved_news[0].title == "Existing News"
        assert isinstance(retrieved_news[0].published_at, datetime)