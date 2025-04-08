# tests/test_data_service.py
import pytest
from backend.services.data_service import (
    fetch_company_info,
    fetch_financial_data,
    validate_financial_data,
    store_company_data
)

def test_fetch_company_info():
    # Test with a valid ticker
    info = fetch_company_info("AAPL")
    assert info is not None
    assert info["ticker_symbol"] == "AAPL"
    
    # Test with an invalid ticker
    info = fetch_company_info("INVALID")
    assert info is None

def test_fetch_financial_data():
    # Test with a valid ticker
    data = fetch_financial_data("AAPL")
    assert len(data) > 0
    assert "date" in data[0]
    assert "open" in data[0]
    
    # Test with an invalid ticker
    data = fetch_financial_data("INVALID")
    assert len(data) == 0

def test_validate_financial_data():
    # Valid data
    data = [
        {"date": "2023-01-01", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000000}
    ]
    validated = validate_financial_data(data)
    assert len(validated) == 1
    
    # Invalid data (missing fields)
    data = [
        {"date": "2023-01-01", "open": 100.0}  # Missing fields
    ]
    validated = validate_financial_data(data)
    assert len(validated) == 0
    
    # Invalid data (wrong types)
    data = [
        {"date": "2023-01-01", "open": "invalid", "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000000}
    ]
    validated = validate_financial_data(data)
    assert len(validated) == 0

def test_store_company_data():
    # This test requires a database connection
    # In a real test, you might want to use a test database or mock the database
    result = store_company_data("AAPL")
    assert result["success"] is True