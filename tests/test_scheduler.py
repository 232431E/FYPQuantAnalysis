import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
import pytz
from backend.services.data_service import scheduled_news_update, store_news_articles
from backend import create_app, db  # Import the db instance from Flask-SQLAlchemy
from backend.models import Company, News
from backend import database  # Import the database module

class TestScheduledNewsUpdate(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.mock_db_session = MagicMock(spec=db.session)
        self.mock_db_session.add = MagicMock()
        self.mock_db_session.add_all = MagicMock()
        self.mock_db_session.commit = MagicMock()
        self.news_constructor_call_count = 0

    def tearDown(self):
        self.app_context.pop()

    def _mock_news_constructor(self, *args, **kwargs):
        self.news_constructor_call_count += 1
        mock_news_instance = MagicMock()
        mock_state = MagicMock()
        mock_state.session = self.mock_db_session
        setattr(mock_news_instance, '__sa_instance_state__', mock_state)
        return mock_news_instance

    @patch('backend.services.data_service.datetime')
    @patch('backend.services.data_service.fetch_latest_news')
    @patch('backend.database.get_db')
    @patch('backend.services.data_service.News') # Patch News where it's used
    def test_scheduled_news_update_runs_at_6am_sgt_weekday(self, MockNews, mock_get_db, mock_fetch_news, mock_datetime):
        MockNews.side_effect = self._mock_news_constructor

        sgt = pytz.timezone('Asia/Singapore')
        mock_datetime.now.return_value = sgt.localize(datetime(2025, 4, 21, 6, 0, 0))
        mock_get_db.return_value = self.mock_db_session

        mock_companies = [MagicMock(spec=Company, company_id=i, ticker_symbol=f'TICKER{i}', industry='Tech', exchange='EX') for i in range(39)]
        self.mock_db_session.query.return_value.all.return_value = mock_companies
        mock_fetch_news.side_effect = [[{'title': f'News {i}', 'url': f'http://example.com/{i}', 'publishedAt': '2025-04-21T10:00:00Z', 'description': f'Summary {i}'}] for i in range(39)] # Ensure 'url' key

        self.news_constructor_call_count = 0 # Reset counter

        with self.app.app_context():
            scheduled_news_update(self.app)

            self.assertEqual(mock_fetch_news.call_count, 39)
            self.assertEqual(self.news_constructor_call_count, 39) # Expect 39 News objects to be created
            self.mock_db_session.add_all.assert_called_once() # Assert add_all() is called once
            args, _ = self.mock_db_session.add_all.call_args
            self.assertEqual(len(args[0]), 39) # Assert that add_all was called with a list of 39 News objects
            self.mock_db_session.commit.assert_called_once()

    @patch('backend.database.get_db')
    @patch('backend.services.data_service.News') # Patch News where it's used
    def test_store_single_news_article(self, MockNews, mock_get_db):
        MockNews.side_effect = self._mock_news_constructor

        mock_company = MagicMock(spec=Company, company_id=1)
        news_article = {'title': 'Test News', 'url': 'http://example.com', 'publishedAt': '2025-04-21T10:00:00Z', 'description': 'Test summary'} # Use 'url' key
        mock_get_db.return_value = self.mock_db_session
        self.news_constructor_call_count = 0 # Reset counter

        with self.app.app_context():
            store_news_articles(database.get_db(), mock_company.company_id, [news_article])
            self.assertEqual(self.news_constructor_call_count, 1, "News constructor should have been called once")
            self.mock_db_session.add_all.assert_called_once() # Now store_news_articles uses add_all
            self.mock_db_session.commit.assert_called_once()

    @patch('backend.services.data_service.datetime')
    @patch('backend.services.data_service.fetch_latest_news')
    @patch('backend.database.get_db')
    @patch('backend.services.data_service.News') # Patch News where it's used
    def test_scheduled_news_update_does_not_run_at_wrong_time(self, MockNews, mock_get_db, mock_fetch_news, mock_datetime):
        MockNews.side_effect = self._mock_news_constructor

        sgt = pytz.timezone('Asia/Singapore')
        mock_datetime.now.return_value = sgt.localize(datetime(2025, 4, 21, 7, 0, 0))
        mock_get_db.return_value = self.mock_db_session
        self.mock_db_session.query.return_value.all.return_value = []
        self.news_constructor_call_count = 0

        with self.app.app_context():
            scheduled_news_update(self.app)
            mock_fetch_news.assert_not_called()
            self.assertEqual(self.news_constructor_call_count, 0, "News constructor should not have been called")
            self.mock_db_session.add_all.assert_not_called() # Assert add_all() not called
            self.mock_db_session.commit.assert_not_called()

    @patch('backend.services.data_service.datetime')
    @patch('backend.services.data_service.fetch_latest_news')
    @patch('backend.database.get_db')
    @patch('backend.services.data_service.News') # Patch News where it's used
    def test_scheduled_news_update_does_not_run_on_weekend(self, MockNews, mock_get_db, mock_fetch_news, mock_datetime):
        MockNews.side_effect = self._mock_news_constructor

        sgt = pytz.timezone('Asia/Singapore')
        mock_datetime.now.return_value = sgt.localize(datetime(2025, 4, 27, 6, 0, 0))
        mock_get_db.return_value = self.mock_db_session
        self.mock_db_session.query.return_value.all.return_value = []
        self.news_constructor_call_count = 0

        with self.app.app_context():
            scheduled_news_update(self.app)
            mock_fetch_news.assert_not_called()
            self.assertEqual(self.news_constructor_call_count, 0, "News constructor should not have been called")
            self.mock_db_session.add_all.assert_not_called() # Assert add_all() not called
            self.mock_db_session.commit.assert_not_called()

    if __name__ == '__main__':
        unittest.main()