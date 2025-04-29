# tests/test_data_service.py
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from decimal import Decimal
import pytz
from backend.database import Base, get_db, get_company_by_ticker
from backend.models import Company, FinancialData
from backend.services.data_service import fetch_financial_data, store_financial_data, needs_financial_data_update
import logging

logging.basicConfig(level=logging.DEBUG)  # Enable debug logging


class TestDataService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    def execute_sql(self, sql_statement):
        """Helper function to execute raw SQL."""
        with self.engine.connect() as connection:
            connection.execute(text(sql_statement))
            connection.commit()

    @patch("yfinance.download")
    def test_fetch_financial_data_success(self, mock_download):
        """Test successful fetching of financial data."""
        mock_download.return_value = pd.DataFrame(
            {
                "Open": [100.0, 101.5],
                "High": [102.0, 103.0],
                "Low": [99.0, 101.0],
                "Close": [101.5, 102.5],
                "Volume": [1000000, 1200000],
            },
            index=[pd.Timestamp("2025-04-10"), pd.Timestamp("2025-04-11")],
        )

        data = fetch_financial_data("AAPL")
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["date"], date(2025, 4, 10))
        self.assertEqual(data[0]["open"], 100.0)
        self.assertEqual(data[1]["close"], 102.5)
        logging.info("test_fetch_financial_data_success passed")

    @patch("yfinance.download")
    def test_fetch_financial_data_empty(self, mock_download):
        """Test handling of empty data from yfinance."""
        mock_download.return_value = MagicMock(empty=True)
        data = fetch_financial_data("GOOG")
        self.assertIsNone(data)
        logging.info("test_fetch_financial_data_empty passed")

    @patch("backend.services.data_service.yf.Ticker")
    @patch("backend.services.data_service.yf.download")
    def test_store_financial_data_new_company_success(self, mock_download, mock_ticker):
        """Test storing financial data for a new company."""
        # Mock company info
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            "symbol": "NVDA",
            "longName": "NVIDIA Corporation",
            "exchange": "NASDAQ",
            "industry": "Semiconductors",
        }
        mock_ticker.return_value = mock_ticker_instance

        # Mock OHLCV data
        mock_download.return_value = MagicMock(
            empty=False,
            iterrows=MagicMock(
                return_value=[
                    (
                        pd.Timestamp("2025-04-28"),
                        pd.Series(
                            {
                                "Open": 800.0,
                                "High": 810.0,
                                "Low": 795.0,
                                "Close": 805.0,
                                "Volume": 15000000,
                            }
                        ),
                    ),
                ]
            ),
        )

        # Mock historical fundamentals
        dates_nvda = [pd.Timestamp("2024-12-31")]
        mock_financials_df_nvda = pd.DataFrame(
            {
                dates_nvda[0]: [5.0, 500.0, 20.0, 80.0, 90.0, 0.15],
            },
            index=["BasicEPS", "TotalRevenue", "TotalDebt", "StockholdersEquity", "OperatingCashFlow", "ROI"],
        )
        mock_balance_sheet_df_nvda = pd.DataFrame(
            {
                dates_nvda[0]: [20.0, 80.0],
            },
            index=["TotalDebt", "StockholdersEquity"],
        )
        mock_cashflow_df_nvda = pd.DataFrame(
            {
                dates_nvda[0]: [90.0],
            },
            index=["OperatingCashFlow"],
        )
        mock_ticker_instance.financials = mock_financials_df_nvda
        mock_ticker_instance.balance_sheet = mock_balance_sheet_df_nvda
        mock_ticker_instance.cashflow = mock_cashflow_df_nvda

        success = store_financial_data(self.db, "NVDA")
        self.assertTrue(success)

        company = get_company_by_ticker(self.db, "NVDA")
        self.assertIsNotNone(company)
        self.assertEqual(company.company_name, "NVIDIA Corporation")

        financial_data = (
            self.db.query(FinancialData)
            .filter_by(company_id=company.company_id, date=date(2025, 4, 28))
            .first()
        )
        self.assertIsNotNone(financial_data)
        self.assertEqual(financial_data.close, 805.0)
        self.assertEqual(financial_data.eps, 5.0)
        logging.info("test_store_financial_data_new_company_success passed")

    @patch("backend.services.data_service.yf.Ticker")
    @patch("backend.services.data_service.yf.download")
    def test_store_financial_data_existing_company_success(self, mock_download, mock_ticker):
        """Test storing financial data for an existing company."""
        # Create an existing company
        existing_company = Company(
            ticker_symbol="AAPL", company_name="Apple Inc", exchange="NASDAQ", industry="Technology"
        )
        self.db.add(existing_company)
        self.db.commit()

        # Mock OHLCV data
        mock_download.return_value = MagicMock(
            empty=False,
            iterrows=MagicMock(
                return_value=[
                    (
                        pd.Timestamp("2025-04-29"),
                        pd.Series(
                            {
                                "Open": 170.0,
                                "High": 172.0,
                                "Low": 169.5,
                                "Close": 171.5,
                                "Volume": 10000000,
                            }
                        ),
                    ),
                ]
            ),
        )

        # Mock historical fundamentals
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.financials = pd.DataFrame({pd.Timestamp('2024-12-31'): [8.0]}, index=['BasicEPS'])
        mock_ticker_instance.balance_sheet = pd.DataFrame(
            {pd.Timestamp('2024-12-31'): [30.0, 100.0]}, index=['TotalDebt', 'StockholdersEquity'])
        mock_ticker_instance.cashflow = pd.DataFrame({pd.Timestamp('2024-12-31'): [120.0]}, index=['OperatingCashFlow'])
        mock_ticker.return_value = mock_ticker_instance

        success = store_financial_data(self.db, "AAPL")
        self.assertTrue(success)

        company = get_company_by_ticker(self.db, "AAPL")
        self.assertIsNotNone(company)

        financial_data = (
            self.db.query(FinancialData)
            .filter_by(company_id=company.company_id, date=date(2025, 4, 29))
            .first()
        )
        self.assertIsNotNone(financial_data)
        self.assertEqual(financial_data.close, 171.5)
        self.assertEqual(financial_data.eps, 8.0)
        logging.info("test_store_financial_data_existing_company_success passed")

    def test_needs_financial_data_update(self):
        """Test the needs_financial_data_update function."""
        # Create a company for testing
        company = Company(
            ticker_symbol="MSFT", company_name="Microsoft Corp", exchange="NASDAQ", industry="Technology"
        )
        self.db.add(company)
        self.db.commit()
        company_id = company.company_id
        self.db.refresh(company)

        # Test case 1: No existing data
        self.assertTrue(needs_financial_data_update(self.db, company_id))
        logging.info(f"Test Case 1 Result: True")
        self.db.query(FinancialData).filter(FinancialData.company_id == company_id).delete()
        self.db.commit()

        # Test case 2: Data exists, but is older than today
        old_data = FinancialData(
            company_id=company_id,
            date=date(2024, 1, 1),
            open=200.0,
            high=205.0,
            low=198.0,
            close=202.0,
            volume=25000000,
        )
        self.db.add(old_data)
        self.db.commit()
        self.assertTrue(needs_financial_data_update(self.db, company_id))
        logging.info(f"Test Case 2 Result: True")
        self.db.query(FinancialData).filter(FinancialData.company_id == company_id).delete()
        self.db.commit()

        # Test case 3: Data is from today (same day in SGT)
        sgt = pytz.timezone("Asia/Singapore")
        today_sgt = datetime.now(sgt).date()
        recent_data = FinancialData(
            company_id=company_id,
            date=today_sgt,
            open=210.0,
            high=212.0,
            low=209.0,
            close=211.5,
            volume=15000000,
        )
        self.db.add(recent_data)
        self.db.commit()
        self.assertFalse(needs_financial_data_update(self.db, company_id))
        logging.info(f"Test Case 3 Result: False")
        self.db.query(FinancialData).filter(FinancialData.company_id == company_id).delete()
        self.db.commit()

        # Test case 4: Data is from yesterday
        yesterday_sgt = today_sgt - timedelta(days=1)
        yesterday_data = FinancialData(company_id=company_id, date=yesterday_sgt, open=205.0, high=207.0, low=203.0,
                                            close=206.0, volume=12000000)
        self.db.add(yesterday_data)
        self.db.commit()
        self.assertTrue(needs_financial_data_update(self.db, company_id))
        logging.info(f"Test Case 4 Result: True")
        self.db.query(FinancialData).filter(FinancialData.company_id == company_id).delete()
        self.db.commit()
        
    @patch("backend.services.data_service.yf.Ticker")
    @patch("backend.services.data_service.yf.download")
    def test_store_financial_data_no_company_info(self, mock_download, mock_ticker):
        """Test when yfinance returns no company info."""
        # Mock yfinance.Ticker().info to return None
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = None
        mock_ticker.return_value = mock_ticker_instance

        success = store_financial_data(self.db, "BABA")
        self.assertFalse(success)
        self.assertIsNone(get_company_by_ticker(self.db, "BABA"))
        logging.info("test_store_financial_data_no_company_info passed")

    @patch("backend.services.data_service.yf.Ticker")
    @patch("backend.services.data_service.yf.download")
    def test_store_financial_data_empty_ohlcv(self, mock_download, mock_ticker):
        """Test when yfinance returns empty OHLCV data."""
        # Mock company info
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            "symbol": "TSLA",
            "longName": "Tesla, Inc.",
            "exchange": "NASDAQ",
            "industry": "Auto Manufacturers",
        }
        mock_ticker.return_value = mock_ticker_instance

        # Mock empty OHLCV data
        mock_download.return_value = MagicMock(empty=True)

        success = store_financial_data(self.db, "TSLA")
        self.assertFalse(success)
        company = get_company_by_ticker(self.db, "TSLA")
        self.assertIsNotNone(company)  # Company should still be created
        logging.info("test_store_financial_data_empty_ohlcv passed")

    @patch('yfinance.Ticker')
    @patch('yfinance.download')
    def test_store_financial_data_success(self, mock_download, mock_ticker):
        """Test successful storage of financial data with comprehensive mocking."""
        # Mock company info
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {'symbol': 'AMZN', 'longName': 'Amazon.com Inc', 'exchange': 'NASDAQ',
                                     'industry': 'Retail'}
        mock_ticker.return_value = mock_ticker_instance

        # Mock OHLCV data - Simulate Pandas Series rows
        mock_download.return_value = MagicMock(empty=False, iterrows=MagicMock(return_value=[
            (pd.Timestamp('2024-12-30'),
             pd.Series({'Open': 150.0, 'High': 152.0, 'Low': 148.0, 'Close': 151.0, 'Volume': 5000000})),
            (pd.Timestamp('2025-01-02'),
             pd.Series({'Open': 151.0, 'High': 153.0, 'Low': 150.5, 'Close': 152.5, 'Volume': 6000000})),
        ]))

        # Mock historical fundamentals - INCLUDE DATA FOR 2025
        dates_amzn = [pd.Timestamp('2024-12-31'), pd.Timestamp('2025-12-31')]  # Add 2025
        mock_financials_df_amzn = pd.DataFrame({
            dates_amzn[0]: [12.0, 1200.0, 60.0, 120.0, 180.0, None],  # Added None for ROI
            dates_amzn[1]: [15.0, 1500.0, 70.0, 150.0, 200.0, None]
        }, index=['BasicEPS', 'TotalRevenue', 'TotalDebt', 'StockholdersEquity', 'OperatingCashFlow', 'ROI'])

        mock_balance_sheet_df_amzn = pd.DataFrame({
            dates_amzn[0]: [60.0, 120.0],
            dates_amzn[1]: [70.0, 150.0]  # Mock 2025 data
        }, index=['TotalDebt', 'StockholdersEquity'])

        mock_cashflow_df_amzn = pd.DataFrame({
            dates_amzn[0]: [180.0],
            dates_amzn[1]: [200.0]  # Mock 2025 data
        }, index=['OperatingCashFlow'])

        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {'symbol': 'AMZN', 'longName': 'Amazon.com Inc', 'exchange': 'NASDAQ',
                                     'industry': 'Retail'}
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.financials = mock_financials_df_amzn
        mock_ticker_instance.balance_sheet = mock_balance_sheet_df_amzn
        mock_ticker_instance.cashflow = mock_cashflow_df_amzn

        success = store_financial_data(self.db, 'AMZN')
        self.assertTrue(success)

        company = get_company_by_ticker(self.db, 'AMZN')
        self.assertIsNotNone(company)

        financial_data_2024_12_30 = self.db.query(FinancialData).filter_by(
            company_id=company.company_id, date=date(2024, 12, 30)).first()
        self.assertIsNotNone(financial_data_2024_12_30)
        self.assertEqual(financial_data_2024_12_30.eps, 12.0)
        self.assertIsNone(financial_data_2024_12_30.roi)

        financial_data_2025_01_02 = self.db.query(FinancialData).filter_by(
            company_id=company.company_id, date=date(2025, 1, 2)).first()
        self.assertIsNotNone(financial_data_2025_01_02)
        self.assertEqual(financial_data_2025_01_02.eps, 15.0)  # Now asserting against mocked 2025 data
        self.assertEqual(financial_data_2025_01_02.revenue, 1500.0)
        self.assertAlmostEqual(float(financial_data_2025_01_02.debt_to_equity), float(Decimal('0.4666666666666667')),
                             places=4)
        self.assertEqual(financial_data_2025_01_02.cash_flow, 200.0)
        self.assertIsNone(financial_data_2025_01_02.roi)
        self.assertIsNotNone(financial_data_2025_01_02.pe_ratio)
        logging.info("test_store_financial_data_success passed")

    @patch("backend.services.data_service.yf.Ticker")
    @patch("backend.services.data_service.yf.download")
    def test_auto_update_financial_data(self, mock_download, mock_ticker):
        """Test the automatic update of financial data."""
        logging.info("Running test_auto_update_financial_data")
        # 1. Create a company
        company = Company(ticker_symbol='GOOG', company_name='Alphabet Inc.', exchange='NASDAQ', industry='Technology')
        self.db.add(company)
        self.db.commit()
        company_id = company.company_id

        # 2. Mock that the database has outdated data (e.g., from yesterday)
        sgt = pytz.timezone('Asia/Singapore')
        yesterday_sgt = datetime.now(sgt).date() - timedelta(days=1)
        old_data = FinancialData(company_id=company_id, date=yesterday_sgt, open=2700.0, high=2750.0, low=2680.0,
                                 close=2720.0, volume=3000000)
        self.db.add(old_data)
        self.db.commit()

        # 3. Mock yfinance to return updated data
        mock_download.return_value = pd.DataFrame({
            'Open': [2730.0],
            'High': [2780.0],
            'Low': [2710.0],
            'Close': [2760.0],
            'Volume': [3500000]
        }, index=[pd.Timestamp(datetime.now(sgt).date())])  # Today's date

        # Mock ticker
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {'symbol': 'GOOG', 'longName': 'Alphabet Inc.', 'exchange': 'NASDAQ',
                                     'industry': 'Technology'}
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.financials = pd.DataFrame({pd.Timestamp(datetime.now(sgt).date()): [100.0]},
                                                      index=['BasicEPS'])  # Add minimal
        mock_ticker_instance.balance_sheet = pd.DataFrame({pd.Timestamp(datetime.now(sgt).date()): [100.0, 100.0]},
                                                           index=['TotalDebt', 'StockholdersEquity'])
        mock_ticker_instance.cashflow = pd.DataFrame({pd.Timestamp(datetime.now(sgt).date()): [100.0]},
                                                     index=['OperatingCashFlow'])

        # 4. Call needs_financial_data_update - should return True
        should_update = needs_financial_data_update(self.db, company_id)
        self.assertTrue(should_update)
        logging.info(f"needs_financial_data_update returned: {should_update}")

        # 5. Call store_financial_data - should update the data
        success = store_financial_data(self.db, 'GOOG')
        self.assertTrue(success)
        logging.info(f"store_financial_data success: {success}")

        # 6. Check that the data in the database has been updated
        updated_data = self.db.query(FinancialData).filter_by(company_id=company_id,
                                                                 date=datetime.now(sgt).date()).first()
        self.assertIsNotNone(updated_data)
        self.assertEqual(updated_data.close, 2760.0)  # Check against the mocked updated data
        logging.info(f"Updated data close value: {updated_data.close}")

        logging.info("test_auto_update_financial_data passed")
