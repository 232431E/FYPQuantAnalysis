from flask import Blueprint, jsonify, request, session
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.models import data_model, Company, FinancialData  # Import necessary models
from backend.services import data_service
from sqlalchemy import text
import logging
logging.basicConfig(level=logging.DEBUG)

data_routes_bp = Blueprint('data', __name__, url_prefix='/api/data')

@data_routes_bp.route('/ingest/<ticker>', methods=['POST'])
def ingest_data(ticker):
    """Handles the ingestion of financial data for a given ticker."""
    print(f"Received request to ingest data for ticker: {ticker}")
    db: Session = get_db()
    try:
        if data_service.store_financial_data(db, ticker):
            return jsonify({"message": f"Data ingested for {ticker}. Refresh the table.", "status": "success"}), 200
        else:
            return jsonify({"error": f"Failed to ingest data for {ticker}"}), 500
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@data_routes_bp.route('/dashboard/latest', methods=['GET'])
def get_all_financial_data():
    """Retrieves ALL financial data for all companies."""
    db: Session = get_db()
    try:
        query = text("""
            SELECT
                c.ticker_symbol,
                c.company_name,
                c.industry,
                fd.date,
                fd.open,
                fd.high,
                fd.low,
                fd.close,
                fd.volume
            FROM companies c
            JOIN financial_data fd ON c.company_id = fd.company_id
            ORDER BY fd.date DESC; -- Order by date, or any order you prefer
        """)
        all_data = db.execute(query).fetchall()
        results = []
        for row in all_data:
            results.append({
                "ticker_symbol": row.ticker_symbol,
                "company_name": row.company_name,
                "industry": row.industry,
                "date": row.date.isoformat(),
                "open": row.open,
                "high": row.high,
                "low": row.low,
                "close": row.close,
                "volume": row.volume
            })
        logging.debug(f"Successfully queried {len(results)} financial data entries")
        return jsonify(results), 200
    except Exception as e:
        print(f"Error fetching all financial data: {e}")
        return jsonify({"error": "Failed to fetch all financial data"}), 500
    finally:
        db.close()
        
@data_routes_bp.route('/companies/<int:company_id>/financials', methods=['GET'])
def get_company_financial_data(company_id):
    period = request.args.get('period', 'daily')
    db: Session = get_db()
    try:
        if period == 'daily':
            financial_data_query = db.query(data_model.FinancialData).filter(data_model.FinancialData.company_id == company_id).all()
            print(f"Daily financial data query in route: {[item.date for item in financial_data_query]}") # Log dates
            financial_data = [{"date": item.date.strftime('%Y-%m-%d'), "open": item.open, "close": item.close, "volume": item.volume}
                              for item in financial_data_query]
            return jsonify(financial_data)
        elif period == 'weekly':
            weekly_data = data_service.get_weekly_financial_data(db, company_id)
            print(f"Weekly financial data query in route: {[item.week for item in weekly_data]}") # Log weeks
            financial_data = [{"week": item.week, "avg_open": item.avg_open, "avg_close": item.avg_close, "total_volume": item.total_volume}
                              for item in weekly_data]
            return jsonify(financial_data)
        elif period == 'monthly':
            monthly_data = data_service.get_monthly_financial_data(db, company_id)
            print(f"Monthly financial data query in route: {[item.month for item in monthly_data]}") # Log months
            financial_data = [{"month": item.month, "avg_open": item.avg_open, "avg_close": item.avg_close, "total_volume": item.total_volume}
                              for item in monthly_data]
            return jsonify(financial_data)
        elif period == 'yearly':
            yearly_data = data_service.get_yearly_financial_data(db, company_id)
            print(f"Yearly financial data query in route: {[item.year for item in yearly_data]}") # Log years
            financial_data = [{"year": item.year, "avg_open": item.avg_open, "avg_close": item.avg_close, "total_volume": item.total_volume}
                              for item in yearly_data]
            return jsonify(financial_data)
        else:
            return jsonify({"error": "Invalid period"}), 400
    finally:
        db.close()

@data_routes_bp.route('/news', methods=['GET'])
def get_company_news():
    company_id = session.get('selected_company_id')
    print(f"Company ID in news route: {company_id}")
    if company_id:
        db: Session = get_db()
        try:
            news_query = db.query(data_model.News).filter(data_model.News.company_id == company_id).all()
            print(f"News query in route: {[item.title for item in news_query]}") # Log news titles
            news_list = [{"title": item.title, "url": item.url}
                         for item in news_query]
            return jsonify(news_list)
        finally:
            db.close()
    return jsonify([])