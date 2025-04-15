import pytest
from backend.models.data_model import Company, FinancialData
from datetime import datetime

def test_create_company(app_test, db_session): # use app_test and db_session
    """Test creating a company record."""
    company = Company(company_name="Test Company", ticker_symbol="TEST", exchange="NASDAQ", industry="Technology")
    db_session.add(company)
    db_session.commit()
    assert company.company_name == "Test Company"

def test_add_financial_data(app_test, db_session): # use app_test and db_session
    """Test adding financial data for a company."""
    company = Company(company_name="Test Company", ticker_symbol="TEST", exchange="NASDAQ", industry="Technology")
    db_session.add(company)
    db_session.commit()

    financial_data = FinancialData(
        company_id=company.company_id,
        date=datetime.strptime("2023-10-01", "%Y-%m-%d").date(),
        open=100.0,
        high=105.0,
        low=99.0,
        close=102.0,
        volume=1000000
    )
    db_session.add(financial_data)
    db_session.commit()

    result = db_session.query(FinancialData).filter_by(company_id=company.company_id).first()
    assert result is not None
    assert result.close == 102.0