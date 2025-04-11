# backend/services/user_service.py
from sqlalchemy.orm import Session
from backend import database

def get_user_dashboard_news(db: Session, user_id: int):
    # In a real application, you'd fetch the companies the user is interested in
    # For now, let's assume a hardcoded list or a way to get it from the user object
    interested_tickers = ["AAPL", "GOOGL", "MSFT"]  # Example

    news_list = []
    for ticker in interested_tickers:
        company = database.get_company_by_ticker(db, ticker)
        if company:
            news = database.get_news_by_company(db, company.company_id, limit=5) # Get latest 5 news
            news_list.extend([{"company": company.company_name, "ticker": ticker, **item.__dict__} for item in news])
    return news_list

# Example route (backend/routes/user_routes.py)
from flask import Blueprint, jsonify
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.services import user_service

user_routes = Blueprint('user', __name__, url_prefix='/api/user')

@user_routes.route('/dashboard/news/<int:user_id>', methods=['GET'])
def get_dashboard_news(user_id: int):
    db: Session = next(get_db())
    news = user_service.get_user_dashboard_news(db, user_id)
    return jsonify(news)