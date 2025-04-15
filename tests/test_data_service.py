# backend/tests/test_data_service.py
import pytest
from sqlalchemy.orm import Session
from backend.services import data_service
from backend.models import Company, FinancialData
from datetime import date
from unittest.mock import patch
import yfinance as yf
import pandas as pd

@pytest.fixture
def mock_yfinance_download():
    """Mocks yfinance.download to return sample data."""
    def _mock_download(ticker, period):
        # Create a sample DataFrame
        data = {
            'Open': [100.0, 101.0, 102.0],
            'High': [102.0, 103.0, 104.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [101.0, 102.0, 103.0],
            'Volume': [10000, 11000, 12000],
        }
        index = pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        return pd.DataFrame(data, index=index)
    with patch('yfinance.download', side_effect=_mock_download) as mock:
        yield mock

@pytest.fixture
def mock_yfinance_ticker():
    """Mocks yfinance.Ticker to return sample company info."""
    class MockTicker:
        def __init__(self, ticker):
            self.info = {
                "symbol": ticker,
                "longName": f"{ticker} Company",
                "exchange": "NYSE",
                "industry": "Technology",
            }
    with patch('yfinance.Ticker', side_effect=MockTicker) as mock:
        yield mock
class TestDataService:
    def test_fetch_financial_data(self, mock_yfinance_download):
        """Tests the fetch_financial_data function."""
        ticker = "AAPL"
        data = data_service.fetch_financial_data(ticker)
        assert data is not None
        assert len(data) == 3
        assert all(isinstance(d['date'], date) for d in data)
        assert all(isinstance(d['open'], float) for d in data)

    def test_store_financial_data_new_company(self, db: Session, mock_yfinance_download, mock_yfinance_ticker):
        """Tests store_financial_data with a new company."""
        ticker = "AAPL"
        result = data_service.store_financial_data(db, ticker)
        assert result is True
        company = db.query(Company).filter(Company.ticker_symbol == ticker).first()
        assert company is not None
        assert company.company_name == "AAPL Company"
        financial_data_count = db.query(FinancialData).filter(FinancialData.company_id == company.company_id).count()
        assert financial_data_count == 3

    def test_store_financial_data_existing_company(self, db: Session, mock_yfinance_download, mock_yfinance_ticker):
        """Tests store_financial_data with an existing company."""
        # Create a company first
        company_data = {
            "ticker_symbol": "AAPL",
            "company_name": "Apple Inc",
            "exchange": "NASDAQ",
            "industry": "Electronics",
        }
        company = data_service.database.create_company(db, company_data)
        db.commit()

        ticker = "AAPL"
        result = data_service.store_financial_data(db, ticker)
        assert result is True
        financial_data_count = db.query(FinancialData).filter(FinancialData.company_id == company.company_id).count()
        assert financial_data_count == 3

    def test_store_financial_data_no_yf_data(self, db: Session):
        """Tests store_financial_data when yfinance returns no data."""
        with patch('yfinance.download', return_value=pd.DataFrame()):  # Mock empty DataFrame
            ticker = "AAPL"
            result = data_service.store_financial_data(db, ticker)
            assert result is False

    def test_store_financial_data_yf_error(self, db: Session):
        """Tests store_financial_data when yfinance raises an exception."""
        with patch('yfinance.download', side_effect=Exception("YF error")):
            ticker = "AAPL"
            result = data_service.store_financial_data(db, ticker)
            assert result is False