# backend/services/data_service.py
from sqlalchemy import func
import yfinance as yf
from sqlalchemy.orm import Session
from backend import database
from backend.models import Company, FinancialData, News
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
import pandas as pd
import os
import requests
import pytz

logging.basicConfig(level=logging.INFO)

def fetch_financial_data(ticker: str, period: str = None, start: Optional[date] = None, end: Optional[date] = None) -> Optional[List[Dict[str, Any]]]:
    """Fetches historical OHLCV data from yfinance, allowing for period or specific date range."""
    try:
        if period and not start and not end:
            data = yf.download(ticker, period=period)
        elif start and end and not period:
            data = yf.download(ticker, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        else:
            logging.error(f"Invalid parameters for fetch_financial_data. Must provide either 'period' or both 'start' and 'end'.")
            return None

        if data.empty:
            logging.warning(f"No OHLCV data received from yfinance for {ticker} (period: {period}, start: {start}, end: {end})")
            return None
        financial_data_list = []
        for index, row in data.iterrows():
            try:
                if isinstance(index, pd.Timestamp):
                    data_date = index.to_pydatetime().date()
                else:
                    data_date = index

                financial_data_list.append({
                    "date": data_date,
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
        if "YFPricesMissingError" in str(e):
            logging.warning(f"No data found for {ticker}: {e}")
            return []
        else:
            logging.error(
                f"Error fetching OHLCV data for {ticker} (period: {period}, start: {start}, end: {end}): {e}")
            return None
    
def fetch_historical_fundamentals(ticker: str, years: int = 5) -> Optional[Dict[date, Dict[str, Any]]]:
    """Fetches historical fundamental data (annual) from yfinance."""
    try:
        tk = yf.Ticker(ticker)
        financials = tk.financials  # Annual income statement
        balance_sheet = tk.balance_sheet  # Annual balance sheet
        cashflow = tk.cashflow  # Annual cash flow statement

        if financials is None or balance_sheet is None or cashflow is None or financials.empty or balance_sheet.empty or cashflow.empty:
            logging.warning(
                f"Could not retrieve all historical fundamental statements for {ticker} or they are empty")
            return None

        fundamental_data = {}
        num_years = min(years, len(financials.columns))
        reporting_date = None  # Initialize reporting_date here

        for col in financials.columns[:num_years]:
            try:
                reporting_date = col.to_pydatetime().date()
                fundamental_data[reporting_date] = {}

                fundamental_data[reporting_date]['eps'] = financials.loc['BasicEPS', col].item() if 'BasicEPS' in financials.index and col in financials.columns and pd.notna(
                    financials.loc['BasicEPS', col]) else None
                fundamental_data[reporting_date]['revenue'] = financials.loc['TotalRevenue', col].item() if 'TotalRevenue' in financials.index and col in financials.columns and pd.notna(
                    financials.loc['TotalRevenue', col]) else None

                total_debt = balance_sheet.loc['TotalDebt', col].item() if 'TotalDebt' in balance_sheet.index and col in balance_sheet.columns and pd.notna(
                    balance_sheet.loc['TotalDebt', col]) else None
                stockholders_equity = balance_sheet.loc['StockholdersEquity', col].item() if 'StockholdersEquity' in balance_sheet.index and col in balance_sheet.columns and pd.notna(
                    balance_sheet.loc['StockholdersEquity', col]) else None
                fundamental_data[reporting_date]['total_debt'] = total_debt
                fundamental_data[reporting_date]['stockholders_equity'] = stockholders_equity
                if stockholders_equity != 0 and total_debt is not None and stockholders_equity is not None:
                    fundamental_data[reporting_date]['debt_to_equity'] = total_debt / stockholders_equity
                else:
                    fundamental_data[reporting_date]['debt_to_equity'] = None

                fundamental_data[reporting_date]['cash_flow'] = cashflow.loc['OperatingCashFlow', col].item() if 'OperatingCashFlow' in cashflow.index and col in cashflow.columns and pd.notna(
                    cashflow.loc['OperatingCashFlow', col]) else None
                fundamental_data[reporting_date]['roi'] = financials.loc['ROI', col].item() if 'ROI' in financials.index and col in financials.columns and pd.notna(
                    financials.loc['ROI', col]) else None

            except KeyError as e:
                logging.warning(
                    f"Missing key in fundamental data for {ticker} on {reporting_date}: {e}")
            except AttributeError as e:
                logging.error(
                    f"Error processing fundamental data for {ticker} on {reporting_date}: {e}, type of col: {type(col)}")
            except Exception as e:
                logging.error(
                    f"Unexpected error processing fundamental data for {ticker} on {reporting_date}: {e}")

        return fundamental_data
    except Exception as e:
        logging.error(f"Error fetching historical fundamental data for {ticker}: {e}")
        return None

def store_financial_data(db: Session, ticker: str, period: str = "5y") -> bool:
    """Stores historical OHLCV and annual fundamental data for a given ticker, linking them by date."""
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
        ohlcv_data_list = fetch_financial_data(ticker, period=period)  # Fetch OHLCV data with the specified period
        fundamental_data_map = fetch_historical_fundamentals(ticker, years=5)

        if company and ohlcv_data_list:
            added_count = 0
            for ohlcv_data in ohlcv_data_list:
                eps = None
                revenue = None
                debt_to_equity = None
                cash_flow = None
                pe_ratio = None

                # Try to find matching fundamental data based on the year
                if fundamental_data_map:
                    ohlcv_year = ohlcv_data['date'].year
                    relevant_fund_date = None
                    relevant_fund_values = None

                    for fund_date, fund_values in fundamental_data_map.items():
                        if fund_date.year <= ohlcv_year:
                            if relevant_fund_date is None or fund_date > relevant_fund_date:
                                relevant_fund_date = fund_date
                                relevant_fund_values = fund_values

                    if relevant_fund_values:
                        eps = relevant_fund_values.get("eps")
                        revenue = relevant_fund_values.get("revenue")
                        debt_to_equity = relevant_fund_values.get("debt_to_equity")
                        cash_flow = relevant_fund_values.get("cash_flow")
                        # P/E ratio calculation
                        if eps is not None and eps != 0 and ohlcv_data["close"] is not None:
                            pe_ratio = ohlcv_data["close"] / eps

                financial_data = {
                    "company_id": company.company_id,
                    "date": ohlcv_data['date'],
                    "open": ohlcv_data['open'],
                    "high": ohlcv_data['high'],
                    "low": ohlcv_data['low'],
                    "close": ohlcv_data['close'],
                    "volume": ohlcv_data['volume'],
                    "eps": eps,
                    "pe_ratio": pe_ratio,  # Include the calculated P/E ratio
                    "revenue": revenue,
                    "debt_to_equity": debt_to_equity,
                    "cash_flow": cash_flow,
                    "roi": None,  # Needs more complex calculation
                }

                existing_data = database.check_existing_financial_data(
                    db, company.company_id, financial_data['date'])
                if not existing_data:
                    try:
                        database.create_financial_data(db, financial_data)
                        added_count += 1
                    except Exception as e:
                        logging.error(
                            f"Error creating financial data for {ticker} and date {financial_data['date']}: {e}")
                        db.rollback()
                        return False
            print(
                f"Added {added_count} new financial records for {ticker} (up to 5 years with annual fundamentals)")
            return True
        else:
            logging.warning(
                f"No OHLCV data fetched for {ticker} for the last 5 years")
            return False
    return False

def needs_financial_data_update(db: Session, company_id: int, threshold_hours: int = 24) -> bool:
    """Checks if the financial data for a company needs updating."""
    most_recent_data = db.query(func.max(FinancialData.date)).filter(
        FinancialData.company_id == company_id).scalar()
    if not most_recent_data:
        return True  # No data exists, so needs update

    sgt = pytz.timezone('Asia/Singapore')
    now_sgt = datetime.now(sgt).date()
    data_date_sgt = most_recent_data
    logging.info(f'DEBUG:Most recent data:{most_recent_data}')
    logging.info(f'DEBUG: NOW_SGT:{now_sgt}')
    logging.info(f'DEBUG: DATA_DATE_SGT:{data_date_sgt}')
    # Check if the latest data is from a previous day in SGT
    return data_date_sgt < now_sgt

def fetch_company_news(ticker: str, company_name: str = "", count: int = 5) -> List[Dict[str, Any]]:
    """Fetches the latest news for a specific company using yfinance."""
    try:
        ticker_data = yf.Ticker(ticker)
        news = ticker_data.news
        if news:
            # Limit the number of news items
            latest_news = news[:count]
            formatted_news = []
            for item in latest_news:
                formatted_news.append({
                    "title": item.get('title'),
                    "description": item.get('summary'),
                    "url": item.get('link'),
                    "publishedAt": datetime.fromtimestamp(item.get('publishEpoch')).isoformat() if item.get(
                        'publishEpoch') else datetime.now().isoformat(),
                    "source": {"name": "Yahoo Finance"}
                })
            logging.info(
                f"Successfully fetched {len(formatted_news)} news articles for {ticker} from Yahoo Finance.")
            return formatted_news
        else:
            logging.info(f"No news found for {ticker} on Yahoo Finance.")
            return []
    except Exception as e:
        logging.error(f"Error fetching news for {ticker} from Yahoo Finance: {e}")
        return []

def fetch_industry_news(industry: str, count: int = 3) -> List[Dict[str, Any]]:
    """Fetches the latest news related to the industry."""
    news_api_key = os.environ.get('NEWS_API_KEY')
    news_endpoint = 'https://newsapi.org/v2/everything'

    if not news_api_key:
        logging.warning(
            "NEWS_API_KEY environment variable not set. Using placeholder industry news.")
        return [{"title": f"Placeholder Industry News for {industry}",
                 "description": f"This is a placeholder news article about the {industry} industry.",
                 "url": "#",
                 "publishedAt": datetime.now().isoformat(),
                 "source": {"name": "Placeholder News"}}] * count

    try:
        # Query for industry news
        query = f'"{industry}" AND (industry OR sector OR market)'
        params = {
            'q': query,
            'apiKey': news_api_key,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': count
        }

        response = requests.get(news_endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'ok' and data.get('articles'):
            articles = data['articles'][:count]  # Ensure we only get the count requested
            logging.info(
                f"Successfully fetched {len(articles)} industry news articles for {industry}")
            return articles
        else:
            logging.warning(
                f"Could not fetch industry news for {industry}. Response: {data}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching industry news for {industry}: {e}")
        return []

def fetch_latest_news(ticker: str, industry: str, exchange: str, company_name: str = "") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetches the latest news for a company and its industry.
    Now using yfinance for company news. Industry news is still a placeholder.
    """
    try:
        company_news = fetch_company_news(ticker, company_name, count=5)
    except Exception as e:
        logging.error(f"Error fetching company news (Yahoo Finance): {e}")
        company_news = []

    try:
        industry_news = fetch_industry_news(industry, count=3)
    except Exception as e:
        logging.error(f"Error fetching industry news (Placeholder): {e}")
        industry_news = []

    return company_news, industry_news

def store_news_articles(db: Session, company_id: int, news_articles: List[Dict[str, Any]], news_type: str = "company"):
    """
    Stores news articles in the database.
    """
    news_items_to_add = []

    # Check for duplicates before adding
    existing_urls = {news.link for news in db.query(
        News.link).filter(News.company_id == company_id).all()}

    for article in news_articles:
        # Skip if URL already exists in the database
        if article['url'] in existing_urls:
            continue

        try:
            # Handle different types of publishedAt values safely
            if isinstance(article['publishedAt'], str):
                published_at_utc = datetime.fromisoformat(
                    article['publishedAt'].replace('Z', '+00:00'))
                published_at_sgt = published_at_utc.astimezone(
                    pytz.timezone('Asia/Singapore'))
            else:
                # If it's a MagicMock or other object during testing, use current time
                published_at_sgt = datetime.now(
                    pytz.timezone('Asia/Singapore'))

            # Add a prefix to title to identify news type
            title_prefix = f"[{news_type.upper()}] " if news_type == "industry" else ""

            news = News(
                company_id=company_id,
                title=f"{title_prefix}{article['title']}",
                link=article['url'],
                published_date=published_at_sgt,
                summary=article['description'] or "No description available."
            )
            news_items_to_add.append(news)
        except Exception as e:
            logging.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")

    if news_items_to_add:
        try:
            db.add_all(news_items_to_add)
            db.commit()
        except Exception as db_error:
            logging.error(f"Database error when adding articles: {db_error}")
            db.rollback()
            raise  # Re-raise the exception so the test can catch it
    else:
        logging.info(f"No new {news_type} news articles to add")


def get_stored_news(db: Session, company_id: int, limit: int = 20) -> List[News]:
    """Retrieves stored news articles for a given company."""
    return db.query(News).filter(News.company_id == company_id).order_by(
        News.published_date.desc()).limit(limit).all()


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


if __name__ == '__main__':
    # Example usage (for testing purposes)
    logging.basicConfig(level=logging.DEBUG)
    ticker = "AAPL"
    company_name = "Apple Inc."

    # Test fetching company and industry news
    company_news, industry_news = fetch_latest_news(
        ticker, "Technology", "NASDAQ", company_name)
    logging.info(
        f"Latest company news for {ticker}: {len(company_news)} articles")
    logging.info(
        f"Latest industry news for Technology: {len(industry_news)} articles")

    # Get similar companies
    similar = get_similar_companies("Technology")
    logging.info(f"Similar companies in Technology: {similar}")
