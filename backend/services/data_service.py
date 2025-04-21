# backend/services/data_service.py
import yfinance as yf
from sqlalchemy.orm import Session
from backend import database  # Ensure this import is used
from backend.models import Company, FinancialData, News
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import logging
import pandas as pd
import os
import requests
import pytz
from backend.services.llm_service import analyze_news_sentiment

logging.basicConfig(level=logging.INFO)

def fetch_financial_data(ticker: str, period: str = "5y") -> Optional[List[Dict[str, Any]]]:
    """Fetches historical OHLCV data from yfinance."""
    try:
        data = yf.download(ticker, period=period)
        if data.empty:
            logging.warning(f"No OHLCV data received from yfinance for {ticker} ({period})")
            return None
        financial_data_list = []
        for index, row in data.iterrows():
            try:
                financial_data_list.append({
                    "date": index.to_pydatetime().date(),
                    "open": row['Open'].item(),
                    "high": row['High'].item(),
                    "low": row['Low'].item(),
                    "close": row['Close'].item(),
                    "volume": row['Volume'].item()
                })
            except (TypeError, ValueError) as e:
                logging.error(f"Error converting OHLCV data for {ticker} on {index}: {e}")
                continue
        return financial_data_list
    except Exception as e:
        logging.error(f"Error fetching OHLCV data for {ticker} ({period}): {e}")
        return None


def fetch_historical_fundamentals(ticker: str, years: int = 5) -> Optional[Dict[date, Dict[str, Any]]]:
    """Fetches historical fundamental data (annual) from yfinance."""
    try:
        tk = yf.Ticker(ticker)
        financials = tk.financials  # Annual income statement
        balance_sheet = tk.balance_sheet  # Annual balance sheet
        cashflow = tk.cashflow  # Annual cash flow statement

        print(f"\nDEBUG - Inside fetch_historical_fundamentals for {ticker}:")
        print(f"DEBUG - Type of financials: {type(financials)}")
        print(f"DEBUG - Type of balance_sheet: {type(balance_sheet)}")
        print(f"DEBUG - Type of cashflow: {type(cashflow)}")
        print(f"DEBUG - Financials columns: {financials.columns if financials is not None else None}")
        print(f"DEBUG - Balance Sheet columns: {balance_sheet.columns if balance_sheet is not None else None}")
        print(f"DEBUG - Cash Flow columns: {cashflow.columns if cashflow is not None else None}")

        if financials is None or balance_sheet is None or cashflow is None or financials.empty or balance_sheet.empty or cashflow.empty:
            logging.warning(f"Could not retrieve all historical fundamental statements for {ticker} or they are empty")
            return None

        fundamental_data = {}
        num_years = min(years, len(financials.columns))
        reporting_date = None  # Initialize reporting_date here

        for col in financials.columns[:num_years]:
            try:
                reporting_date = col.to_pydatetime().date()
                print(f"DEBUG - Processing fundamental data for date: {reporting_date}, type: {type(col)}")
                fundamental_data[reporting_date] = {}

                fundamental_data[reporting_date]['eps'] = financials.loc['BasicEPS', col].item() if 'BasicEPS' in financials.index and col in financials.columns and pd.notna(financials.loc['BasicEPS', col]) else None
                fundamental_data[reporting_date]['revenue'] = financials.loc['TotalRevenue', col].item() if 'TotalRevenue' in financials.index and col in financials.columns and pd.notna(financials.loc['TotalRevenue', col]) else None

                total_debt = balance_sheet.loc['TotalDebt', col].item() if 'TotalDebt' in balance_sheet.index and col in balance_sheet.columns and pd.notna(balance_sheet.loc['TotalDebt', col]) else None
                stockholders_equity = balance_sheet.loc['StockholdersEquity', col].item() if 'StockholdersEquity' in balance_sheet.index and col in balance_sheet.columns and pd.notna(balance_sheet.loc['StockholdersEquity', col]) else None
                fundamental_data[reporting_date]['total_debt'] = total_debt
                fundamental_data[reporting_date]['stockholders_equity'] = stockholders_equity
                if stockholders_equity != 0 and total_debt is not None and stockholders_equity is not None:
                    fundamental_data[reporting_date]['debt_to_equity'] = total_debt / stockholders_equity
                else:
                    fundamental_data[reporting_date]['debt_to_equity'] = None

                fundamental_data[reporting_date]['cash_flow'] = cashflow.loc['OperatingCashFlow', col].item() if 'OperatingCashFlow' in cashflow.index and col in cashflow.columns and pd.notna(cashflow.loc['OperatingCashFlow', col]) else None
                fundamental_data[reporting_date]['roi'] = financials.loc['ROI', col].item() if 'ROI' in financials.index and col in financials.columns and pd.notna(financials.loc['ROI', col]) else None

                print(f"DEBUG - Fundamental data for {reporting_date}: {fundamental_data[reporting_date]}")

            except KeyError as e:
                logging.warning(f"Missing key in fundamental data for {ticker} on {reporting_date}: {e}")
            except AttributeError as e:
                logging.error(f"Error processing fundamental data for {ticker} on {reporting_date}: {e}, type of col: {type(col)}")
            except Exception as e:
                logging.error(f"Unexpected error processing fundamental data for {ticker} on {reporting_date}: {e}")

        return fundamental_data
    except Exception as e:
        logging.error(f"Error fetching historical fundamental data for {ticker}: {e}")
        return None


def store_financial_data(db: Session, ticker: str) -> bool:
    """Stores historical OHLCV and annual fundamental data for a given ticker (up to 5 years)."""
    company = database.get_company_by_ticker(db, ticker)
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
                company = database.create_company(db, company_data)
            except Exception as e:
                logging.error(f"Error creating company {ticker} in database: {e}")
                db.rollback()
                return False
        else:
            logging.error(f"Could not retrieve company info for {ticker}")
            return False

    if company:
        ohlcv_data_list = fetch_financial_data(ticker, period="5y")
        fundamental_data_map = fetch_historical_fundamentals(ticker, years=5)

        print(f"\nDEBUG - Inside store_financial_data for {ticker}:")
        print(f"DEBUG - Type of ohlcv_data_list: {type(ohlcv_data_list)}")
        print(f"DEBUG - Type of fundamental_data_map: {type(fundamental_data_map)}")
        print(f"DEBUG - Content of fundamental_data_map (first entry): {list(fundamental_data_map.items())[0] if fundamental_data_map else None}")

        if ohlcv_data_list:
            added_count = 0
            for ohlcv_data in ohlcv_data_list:
                financial_data = {
                    "company_id": company.company_id,
                    "date": ohlcv_data['date'],
                    "open": ohlcv_data['open'],
                    "high": ohlcv_data['high'],
                    "low": ohlcv_data['low'],
                    "close": ohlcv_data['close'],
                    "volume": ohlcv_data['volume'],
                    "eps": None,
                    "pe_ratio": None,  # Need price data for calculation
                    "revenue": None,
                    "debt_to_equity": None,
                    "cash_flow": None,
                    "roi": None,  # Needs more complex calculation
                }

                # Try to find matching fundamental data based on the year
                if fundamental_data_map:
                    year = ohlcv_data['date'].year
                    for fund_date, fund_values in fundamental_data_map.items():
                        if fund_date.year == year:
                            financial_data["eps"] = fund_values.get("eps")
                            financial_data["revenue"] = fund_values.get("revenue")
                            financial_data["debt_to_equity"] = fund_values.get("debt_to_equity")
                            financial_data["cash_flow"] = fund_values.get("cash_flow")
                            # P/E ratio requires price at the time of reporting
                            # This is a simplification - a more accurate approach would
                            # involve more complex alignment or using quarterly data.
                            if financial_data["eps"] is not None and financial_data["eps"] != 0 and ohlcv_data["close"] is not None:
                                financial_data["pe_ratio"] = ohlcv_data["close"] / financial_data["eps"]
                            break  # Assuming one annual report per year

                print(f"DEBUG - Storing financial data for date: {financial_data['date']}, Fundamentals: {financial_data}")
                existing_data = database.check_existing_financial_data(db, company.company_id, financial_data['date'])
                if not existing_data:
                    try:
                        database.create_financial_data(db, financial_data)
                        added_count += 1
                    except Exception as e:
                        logging.error(f"Error creating financial data for {ticker} and date {financial_data['date']}: {e}")
                        db.rollback()
                        return False
            print(f"Added {added_count} new financial records for {ticker} (up to 5 years with annual fundamentals)")
            return True
        else:
            logging.warning(f"No OHLCV data fetched for {ticker} for the last 5 years")
            return False
    return False

def scheduled_financial_data_update(app):
    """Fetches and stores the latest financial data for all companies."""
    with app.app_context():
        db = database.get_db()
        companies = db.query(Company).all()
        for company in companies:
            latest_data = database.get_latest_financial_data(company.ticker_symbol)
            if latest_data:
                store_financial_data(db, company.company_id, latest_data)
        logging.info("Daily financial data update completed.")
        db.close()
        
def fetch_latest_news(ticker: str, industry: str, exchange: str) -> List[Dict[str, Any]]:
    """Fetches the latest news related to the company using a news API."""
    news_api_key = os.environ.get('NEWS_API_KEY')
    news_endpoint = 'https://newsapi.org/v2/everything'  # Example NewsAPI endpoint
    articles: List[Dict[str, Any]] = []

    if not news_api_key:
        logging.warning("NEWS_API_KEY environment variable not set. Using placeholder news.")
        return [{"title": f"Placeholder News for {ticker}", "description": "This is a placeholder news article.", "url": "#", "publishedAt": date.today().isoformat()}] * 3

    try:
        query = f"{ticker} AND ({industry} OR {exchange})"
        params = {
            'q': query,
            'apiKey': news_api_key,
            'sortBy': 'publishedAt',
            'pageSize': 10  # Get the latest 10 articles
        }
        response = requests.get(news_endpoint, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if data.get('status') == 'ok' and data.get('articles'):
            articles = data['articles']
            logging.info(f"Successfully fetched {len(articles)} news articles for {ticker}")
        else:
            logging.warning(f"Could not fetch news for {ticker}. Response: {data}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news for {ticker}: {e}")
    return articles

def get_similar_companies(industry: Optional[str]) -> List[str]:
    """Retrieves a list of similar companies based on the industry."""
    if not industry:
        return ["No industry specified"]

    # This is a very basic placeholder. In a real application,
    # you would query a database or use an external API to find
    # companies in the same or related industries.

    similar_companies_data = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "Healthcare": ["JNJ", "PFE", "MRK"],
        "Finance": ["JPM", "BAC", "WFC"],
        # Add more industries and their common tickers
    }

    return similar_companies_data.get(industry, ["No similar companies found for this industry"])

def store_news_articles(db_session, company_id, news_articles):
    news_items_to_add = []
    for article in news_articles:
        published_at_utc = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
        published_at_sgt = published_at_utc.astimezone(pytz.timezone('Asia/Singapore'))
        news = News(
            company_id=company_id,
            title=article['title'],
            url=article['url'],
            published_at=published_at_sgt,
            summary=article['description']
        )
        news_items_to_add.append(news)
    db_session.add_all(news_items_to_add)
    db_session.commit()  # <--- Commit only once after adding all articles

def scheduled_news_update(app):
    """Fetches and stores the latest news for all companies at 6 AM SGT on weekdays."""
    sgt = pytz.timezone('Asia/Singapore')
    now_sgt = datetime.now(sgt)
    if now_sgt.hour == 6 and now_sgt.weekday() < 5:  # Monday is 0 and Friday is 4
        with app.app_context():
            db = database.get_db()
            all_news_to_add = []
            companies = db.query(Company).all()
            print(f"DEBUG (inside scheduled_news_update): ID of db object: {id(db)}")
            print(f"DEBUG: Number of companies found: {len(companies)}")
            for company in companies:
                latest_news = fetch_latest_news(company.ticker_symbol)
                print(f"Updating news for {company.ticker_symbol} at {datetime.now(sgt)}")
                for article in latest_news:
                    published_at_utc = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                    published_at_sgt = published_at_utc.astimezone(pytz.timezone('Asia/Singapore'))
                    news = News(
                        company_id=company.company_id,
                        title=article['title'],
                        url=article['url'],
                        published_at=published_at_sgt,
                        summary=article['description']
                    )
                    all_news_to_add.append(news)

            if all_news_to_add:
                db.add_all(all_news_to_add)
                db.commit()

            db.close()
            logging.info("Daily news update completed.")
    else:
        logging.info(f"Skipping news update. Current time is {now_sgt.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

def get_stored_news(db: Session, company_id: int) -> List[News]:
    """Retrieves stored news articles for a given company."""
    return db.query(News).filter(News.company_id == company_id).order_by(News.published_date.desc()).all()



def predict_financial_trends(financial_data: Optional[List[Dict[str, Any]]]) -> Dict[str, Optional[str]]:
    """Analyzes historical financial data and predicts future trends (basic implementation)."""
    trends: Dict[str, Optional[str]] = {}
    if not financial_data or len(financial_data) < 2:
        return {"revenue_growth": "Insufficient data", "profit_margin": "Insufficient data"}

    # Basic trend analysis (simplistic and for illustrative purposes)
    # More sophisticated methods would involve time series analysis.

    # Revenue trend (using a placeholder 'revenue' key - adjust if your data has it)
    revenue_present = all(item.get('revenue') is not None for item in financial_data)
    if revenue_present:
        latest_revenue = financial_data[-1].get('revenue')
        previous_revenue = financial_data[-2].get('revenue')
        if latest_revenue is not None and previous_revenue is not None and previous_revenue != 0:
            growth_rate = (latest_revenue - previous_revenue) / previous_revenue
            if growth_rate > 0.05:
                trends["revenue_growth"] = "Positive"
            elif growth_rate < -0.05:
                trends["revenue_growth"] = "Negative"
            else:
                trends["revenue_growth"] = "Neutral"
        else:
            trends["revenue_growth"] = "Insufficient data for trend"
    else:
        trends["revenue_growth"] = "Revenue data not available"

    # Profit margin trend (using a placeholder - you'll need actual profit data)
    trends["profit_margin"] = "Analysis not implemented (requires profit data)"

    return trends

if __name__ == '__main__':
    # Example usage (for testing purposes)
    logging.basicConfig(level=logging.DEBUG)
    ticker = "AAPL"
    db_session = None # You would typically get a database session here

    # Fetch latest news (you'll need a NEWS_API_KEY set)
    news = fetch_latest_news(ticker, "Technology", "NASDAQ")
    logging.info(f"Latest news for AAPL: {news}")

    # Get similar companies
    similar = get_similar_companies("Technology")
    logging.info(f"Similar companies in Technology: {similar}")