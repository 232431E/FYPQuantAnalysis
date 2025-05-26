# backend/services/user_service.py
from sqlalchemy.orm import Session
from backend import database
from backend.models import Company, News  # Import the models

# NOT YET IN USE
def get_user_dashboard_news(db: Session, user_id: int):
    """
    Fetches news for companies that a user might be interested in.
    In a real application, this would be based on user preferences or tracked companies.
    For this example, we'll use a hardcoded list of tickers.
    """
    interested_tickers = ["AAPL", "GOOGL", "MSFT"]  # Example

    news_list = []
    for ticker in interested_tickers:
        company = db.query(Company).filter(Company.ticker_symbol == ticker).first()
        if company:
            news = db.query(News).filter(News.company_id == company.company_id).order_by(News.published_date.desc()).limit(5).all()
            news_list.extend([{"company": company.company_name, "ticker": ticker, "title": item.title, "url": item.url, "published_date": item.published_date.isoformat() if item.published_date else None} for item in news])
    return news_list