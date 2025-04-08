# backend/services/data_service.py
import requests
# import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.data_model import Company, FinancialData
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
FINANCIAL_API_KEY = os.getenv("FINANCIAL_API_KEY")

def fetch_company_info(ticker):
    """Fetch company information from API"""
    # Example using Alpha Vantage API
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={FINANCIAL_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "company_name": data.get("Name"),
            "ticker_symbol": ticker,
            "exchange": data.get("Exchange"),
            "industry": data.get("Industry")
        }
    return None

def fetch_financial_data(ticker, start_date=None, end_date=None):
    """Fetch financial data from API"""
    # Default to last 100 days if no dates provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=100)
    
    # Example using Alpha Vantage API
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={FINANCIAL_API_KEY}&outputsize=full"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        time_series = data.get("Time Series (Daily)", {})
        
        financial_data = []
        for date_str, values in time_series.items():
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Filter by date range
            if start_date.date() <= date <= end_date.date():
                financial_data.append({
                    "date": date,
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0))
                })
        
        # Calculate additional metrics
        for data_point in financial_data:
            # Simple ROI calculation (daily return)
            if data_point["open"] > 0:
                data_point["roi"] = (data_point["close"] - data_point["open"]) / data_point["open"] * 100
            else:
                data_point["roi"] = 0
                
            # Other metrics would typically come from different API calls or calculations
            data_point["eps"] = None
            data_point["pe_ratio"] = None
            data_point["revenue"] = None
            data_point["debt_to_equity"] = None
            data_point["cash_flow"] = None
        
        return financial_data
    
    return []

def validate_financial_data(data):
    """Validate financial data"""
    validated_data = []
    for item in data:
        # Check required fields
        if not all(k in item for k in ["date", "open", "high", "low", "close", "volume"]):
            continue
        
        # Validate data types
        try:
            item["open"] = float(item["open"])
            item["high"] = float(item["high"])
            item["low"] = float(item["low"])
            item["close"] = float(item["close"])
            item["volume"] = int(item["volume"])
            
            # Add to validated data
            validated_data.append(item)
        except (ValueError, TypeError):
            continue
    
    return validated_data

def store_company_data(ticker):
    """Store company and its financial data"""
    db = SessionLocal()
    try:
        # Fetch company info
        company_info = fetch_company_info(ticker)
        if not company_info:
            return {"success": False, "message": f"Could not fetch info for {ticker}"}
        
        # Check if company exists
        company = db.query(Company).filter(Company.ticker_symbol == ticker).first()
        if not company:
            # Create company
            company = Company(**company_info)
            db.add(company)
            db.commit()
            db.refresh(company)
        
        # Fetch financial data
        financial_data = fetch_financial_data(ticker)
        if not financial_data:
            return {"success": False, "message": f"Could not fetch financial data for {ticker}"}
        
        # Validate financial data
        validated_data = validate_financial_data(financial_data)
        
        # Store financial data
        for data_point in validated_data:
            # Check if data for this date already exists
            existing_data = db.query(FinancialData).filter(
                FinancialData.company_id == company.company_id,
                FinancialData.date == data_point["date"]
            ).first()
            
            if not existing_data:
                # Add company_id to data
                data_point["company_id"] = company.company_id
                
                # Create financial data entry
                financial_data_entry = FinancialData(**data_point)
                db.add(financial_data_entry)
        
        db.commit()
        return {"success": True, "message": f"Successfully stored data for {ticker}"}
    
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    
    finally:
        db.close()

def get_weekly_data(company_id):
    """Get weekly financial data for a company"""
    db = SessionLocal()
    try:
        # Get financial data from the weekly view
        result = db.execute(f"""
            SELECT * FROM weekly_financial_data 
            WHERE company_id = {company_id}
            ORDER BY week DESC
        """).fetchall()
        
        return [dict(row) for row in result]
    finally:
        db.close()

def get_monthly_data(company_id):
    """Get monthly financial data for a company"""
    db = SessionLocal()
    try:
        # Get financial data from the monthly view
        result = db.execute(f"""
            SELECT * FROM monthly_financial_data 
            WHERE company_id = {company_id}
            ORDER BY month DESC
        """).fetchall()
        
        return [dict(row) for row in result]
    finally:
        db.close()

def get_yearly_data(company_id):
    """Get yearly financial data for a company"""
    db = SessionLocal()
    try:
        # Get financial data from the yearly view
        result = db.execute(f"""
            SELECT * FROM yearly_financial_data 
            WHERE company_id = {company_id}
            ORDER BY year DESC
        """).fetchall()
        
        return [dict(row) for row in result]
    finally:
        db.close()