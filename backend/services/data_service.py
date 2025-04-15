# backend/services/data_service.py
import yfinance as yf
from sqlalchemy.orm import Session
from backend import database  # Import the database module
from backend.models import Company, FinancialData  # Import the models
from datetime import date
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.ERROR)


def fetch_financial_data(ticker: str) -> Optional[List[Dict[str, Any]]]:
    """Fetches financial data from yfinance."""
    try:
        data = yf.download(ticker, period="1mo")
        if data.empty:
            logging.warning(f"No data received from yfinance for ticker {ticker}")
            return None
        financial_data_list = []
        for index, row in data.iterrows():
            try:  # Wrap each data point conversion
                financial_data_list.append({
                    "date": index.to_pydatetime().date(),  # Consistent date conversion
                    "open": row['Open'].item(),
                    "high": row['High'].item(),
                    "low": row['Low'].item(),
                    "close": row['Close'].item(),
                    "volume": row['Volume'].item()
                })
            except (TypeError, ValueError) as e:
                logging.error(f"Error converting data point for {ticker} on {index}: {e}")
                # Consider if you want to continue processing other rows or stop.
                # Here, I'll continue to the next row.
        return financial_data_list
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return None


def store_financial_data(db: Session, ticker: str) -> bool:
    """Stores financial data for a given ticker."""
    company = database.get_company_by_ticker(db, ticker)  # Use the get_company function
    if not company:
        company_info = yf.Ticker(ticker).info
        if company_info:
            company_data = {
                "ticker_symbol": company_info.get("symbol"),
                "company_name": company_info.get("longName"),
                "exchange": company_info.get("exchange"),
                "industry": company_info.get("industry")
            }
            try:
                company = database.create_company(db, company_data)  # Use create_company
            except Exception as e:
                logging.error(f"Error creating company {ticker} in database: {e}")
                db.rollback()
                return False
        else:
            logging.error(f"Could not retrieve company info for {ticker}")
            return False

    if company:
        financial_data_list = fetch_financial_data(ticker)
        if financial_data_list:
            added_count = 0
            for data in financial_data_list:
                data["company_id"] = company.company_id
                existing_data = database.check_existing_financial_data(db, company.company_id, data['date'])
                if not existing_data:
                    try:
                        database.create_financial_data(db, data)
                        added_count += 1
                    except Exception as e:
                        logging.error(f"Error creating financial data for {ticker} and date {data['date']}: {e}")
                        db.rollback()  # Rollback on any single data point error.
                        # Consider if you want to continue to the next data point.  I'll stop here.
                        return False
            print(f"Added {added_count} new financial records for {ticker}")
            return True
        else:
            logging.warning(f"No financial data fetched for {ticker}")
            return False
    return False