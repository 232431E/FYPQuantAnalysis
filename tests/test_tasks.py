import sys
import os

# Get the directory containing the current script (test_tasks.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root)
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

import unittest
from unittest.mock import patch, MagicMock
from backend.tasks import daily_financial_data_update
from datetime import datetime
import pytz

class TestDailyFinancialDataUpdate(unittest.TestCase):

    @patch('backend.tasks.get_db')
    @patch('backend.tasks.get_all_companies')
    @patch('backend.tasks.store_financial_data')
    @patch('backend.tasks.datetime')
    def test_daily_update_weekday_6am(self, mock_datetime, mock_store, mock_get_all, mock_get_db):
        mock_sgt_tz = pytz.timezone('Asia/Singapore')
        mock_now = mock_sgt_tz.localize(datetime(2025, 4, 22, 6, 0)) # Tuesday 6:00 AM
        mock_datetime.now.return_value = mock_now

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        companies = [MagicMock(ticker_symbol='AAPL'), MagicMock(ticker_symbol='GOOG')]
        mock_get_all.return_value = companies
        mock_store.return_value = True

        daily_financial_data_update()

        mock_get_all.assert_called_once_with(mock_db)
        self.assertEqual(mock_store.call_count, 2)
        mock_store.assert_any_call(mock_db, 'AAPL')
        mock_store.assert_any_call(mock_db, 'GOOG')
        mock_db.close.assert_called_once()

    @patch('backend.tasks.get_db')
    @patch('backend.tasks.datetime')
    def test_daily_update_weekend(self, mock_datetime, mock_get_db):
        mock_sgt_tz = pytz.timezone('Asia/Singapore')
        mock_now = mock_sgt_tz.localize(datetime(2025, 4, 26, 6, 0)) # Saturday 6:00 AM
        mock_datetime.now.return_value = mock_now

        daily_financial_data_update()

        mock_get_db.assert_not_called() # Should not try to fetch data

    # Add more test cases for different times and scenarios

if __name__ == '__main__':
    unittest.main()