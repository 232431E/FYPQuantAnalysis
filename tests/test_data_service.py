# tests/test_data_service.py
import sys
import os
print(f"Current working directory: {os.getcwd()}")
# Get the directory containing the current script (test_data_service.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root)
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from decimal import Decimal

from backend.database import Base, get_db, create_company, get_company_by_ticker, check_existing_financial_data, create_financial_data
from backend.models import Company, FinancialData # Removed unused imports
from backend.services.data_service import fetch_financial_data, fetch_historical_fundamentals, store_financial_data

class TestDataService(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    @patch('yfinance.download')
    def test_fetch_financial_data_success(self, mock_download):
        mock_download.return_value = pd.DataFrame({
            'Open': [100.0, 101.5],
            'High': [102.0, 103.0],
            'Low': [99.0, 101.0],
            'Close': [101.5, 102.5],
            'Volume': [1000000, 1200000]
        }, index=[pd.Timestamp('2025-04-10'), pd.Timestamp('2025-04-11')])

        data = fetch_financial_data('AAPL')
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['date'], date(2025, 4, 10))
        self.assertEqual(data[0]['open'], 100.0)
        self.assertEqual(data[1]['close'], 102.5) # Add another assertion

    @patch('yfinance.download')
    def test_fetch_financial_data_empty(self, mock_download):
        mock_download.return_value = MagicMock(empty=True)
        data = fetch_financial_data('GOOG')
        self.assertIsNone(data)

    @patch('yfinance.Ticker')
    def test_fetch_historical_fundamentals_success(self, mock_ticker):
        dates = [pd.Timestamp('2024-12-31'), pd.Timestamp('2023-12-31')]
        mock_financials_df = pd.DataFrame({
            dates[0]: [10.0, 1000.0, 50.0, 100.0, 150.0, 0.1],
            dates[1]: [9.0, 900.0, 40.0, 90.0, 130.0, 0.09]
        }, index=['BasicEPS', 'TotalRevenue', 'TotalDebt', 'StockholdersEquity', 'OperatingCashFlow', 'ROI'])

        mock_balance_sheet_df = pd.DataFrame({
            dates[0]: [50.0, 100.0],
            dates[1]: [40.0, 90.0]
        }, index=['TotalDebt', 'StockholdersEquity'])

        mock_cashflow_df = pd.DataFrame({
            dates[0]: [150.0],
            dates[1]: [130.0]
        }, index=['OperatingCashFlow'])

        mock_ticker_instance = MagicMock()
        mock_ticker_instance.financials = mock_financials_df
        mock_ticker_instance.balance_sheet = mock_balance_sheet_df
        mock_ticker_instance.cashflow = mock_cashflow_df
        mock_ticker.return_value = mock_ticker_instance

        fundamentals = fetch_historical_fundamentals('MSFT', years=2)
        print(f"\nDEBUG - Inside test_fetch_historical_fundamentals_success:")
        print(f"DEBUG - Type of fundamentals: {type(fundamentals)}")
        print(f"DEBUG - Content of fundamentals: {fundamentals}")
        if fundamentals:
            for date_obj, data in fundamentals.items():
                print(f"DEBUG - Type of key (date): {type(date_obj)}")
        self.assertIsNotNone(fundamentals)
        self.assertEqual(len(fundamentals), 2)
        self.assertIn(date(2024, 12, 31), fundamentals)
        self.assertEqual(fundamentals[date(2024, 12, 31)]['eps'], 10.0)
        self.assertEqual(fundamentals[date(2024, 12, 31)]['debt_to_equity'], 0.5)
        self.assertEqual(fundamentals[date(2024, 12, 31)]['roi'], 0.1)

    @patch('yfinance.Ticker')
    @patch('yfinance.download')
    def test_store_financial_data_success(self, mock_download, mock_ticker):
        # Mock company info
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {'symbol': 'AMZN', 'longName': 'Amazon.com Inc', 'exchange': 'NASDAQ', 'industry': 'Retail'}
        mock_ticker.return_value = mock_ticker_instance

        # Mock OHLCV data - Simulate Pandas Series rows
        mock_download.return_value = MagicMock(empty=False, iterrows=MagicMock(return_value=[
            (pd.Timestamp('2024-12-30'), pd.Series({'Open': 150.0, 'High': 152.0, 'Low': 148.0, 'Close': 151.0, 'Volume': 5000000})),
            (pd.Timestamp('2025-01-02'), pd.Series({'Open': 151.0, 'High': 153.0, 'Low': 150.5, 'Close': 152.5, 'Volume': 6000000})),
        ]))

        # Mock historical fundamentals - INCLUDE DATA FOR 2025
        dates_amzn = [pd.Timestamp('2024-12-31'), pd.Timestamp('2025-12-31')]  # Add 2025
        mock_financials_df_amzn = pd.DataFrame({
            dates_amzn[0]: [12.0, 1200.0, 60.0, 120.0, 180.0, 0.12],
            dates_amzn[1]: [15.0, 1500.0, 70.0, 150.0, 200.0, 0.15]  # Mock 2025 data
        }, index=['BasicEPS', 'TotalRevenue', 'TotalDebt', 'StockholdersEquity', 'OperatingCashFlow', 'ROI'])

        mock_balance_sheet_df_amzn = pd.DataFrame({
            dates_amzn[0]: [60.0, 120.0],
            dates_amzn[1]: [70.0, 150.0]  # Mock 2025 data
        }, index=['TotalDebt', 'StockholdersEquity'])

        mock_cashflow_df_amzn = pd.DataFrame({
            dates_amzn[0]: [180.0],
            dates_amzn[1]: [200.0]  # Mock 2025 data
        }, index=['OperatingCashFlow'])

        mock_ticker_instance.financials = mock_financials_df_amzn
        mock_ticker_instance.balance_sheet = mock_balance_sheet_df_amzn
        mock_ticker_instance.cashflow = mock_cashflow_df_amzn
        mock_ticker.return_value = mock_ticker_instance

        success = store_financial_data(self.db, 'AMZN')
        print(f"\nDEBUG - Inside test_store_financial_data_success:")
        print(f"DEBUG - Value of success: {success}")
        self.assertTrue(success)

        company = get_company_by_ticker(self.db, 'AMZN')
        self.assertIsNotNone(company)

        financial_data_2024_12_30 = self.db.query(FinancialData).filter_by(company_id=company.company_id, date=date(2024, 12, 30)).first()
        self.assertIsNotNone(financial_data_2024_12_30)
        self.assertEqual(financial_data_2024_12_30.eps, 12.0)
        self.assertIsNone(financial_data_2024_12_30.roi)

        financial_data_2025_01_02 = self.db.query(FinancialData).filter_by(company_id=company.company_id, date=date(2025, 1, 2)).first()
        self.assertIsNotNone(financial_data_2025_01_02)
        self.assertEqual(financial_data_2025_01_02.eps, 15.0)  # Now asserting against mocked 2025 data
        self.assertEqual(financial_data_2025_01_02.revenue, 1500.0)
        self.assertAlmostEqual(float(financial_data_2025_01_02.debt_to_equity), float(Decimal('0.4666666666666667')), places=4) # Adjust places        self.assertEqual(financial_data_2025_01_02.cash_flow, 200.0)
        self.assertIsNone(financial_data_2025_01_02.roi)
        self.assertIsNotNone(financial_data_2025_01_02.pe_ratio)

if __name__ == '__main__':
    unittest.main()
