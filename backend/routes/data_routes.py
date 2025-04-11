# backend/routes/data_routes.py
from flask import Blueprint, jsonify, request, session
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.services import data_service

data_routes = Blueprint('data', __name__, url_prefix='/api')

@data_routes.route('/companies/<int:company_id>/financials', methods=['GET'])
def get_company_financial_data(company_id: int):
    period = request.args.get('period', 'daily')  # Default to daily
    db: Session = next(get_db())

    if period == 'daily':
        financial_data = data_service.get_daily_financial_data(db, company_id)
    elif period == 'weekly':
        financial_data = data_service.get_weekly_financial_data(db, company_id)
    elif period == 'monthly':
        financial_data = data_service.get_monthly_financial_data(db, company_id)
    elif period == 'yearly':
        financial_data = data_service.get_yearly_financial_data(db, company_id)
    else:
        return jsonify({'error': 'Invalid period specified'}), 400

    return jsonify(financial_data)

@data_routes.route('/news', methods=['GET'])
def get_latest_news():
    db: Session = next(get_db())
    # Assuming you want news for the currently selected company in the session
    company_id = session.get('selected_company_id')
    if company_id:
        news = data_service.get_latest_news_for_company(db, company_id, limit=10)
        return jsonify([{"title": n.title, "url": n.url} for n in news])
    else:
        return jsonify([]), 200 # Or handle the case where no company is selected