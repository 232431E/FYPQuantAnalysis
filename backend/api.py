#backend/api.pi
from datetime import date, timedelta
from venv import logger
from flask import Flask, Blueprint, jsonify, request
from sqlalchemy import desc, text
from backend import database
from sqlalchemy.orm import Session
from backend.database import get_all_companies, get_db, get_company_by_ticker, get_session_local
from backend.models.data_model import FinancialData
from backend.routes.data_routes import ingest_data
from backend.services.data_service import (
    fetch_financial_data,
    fetch_historical_fundamentals,
    store_financial_data,
    fetch_latest_news,
    get_similar_companies,
    store_news_articles,
    get_stored_news,
    predict_financial_trends,
    get_similar_companies
)
from backend.services.llm_service import (
    analyze_news_sentiment_gemini,
    analyze_news_sentiment,
    analyze_news_sentiment_perplexity
)
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/data/dashboard/latest', methods=['GET'])
def get_latest_data():
    """
    Retrieves the latest financial data for all companies for the dashboard.html page.
    """
    db = get_db()
    print("[DEBUG] /data/dashboard/latest: Entered get_latest_data()") # Debug
    try:
        companies = get_all_companies(db)  # Get all companies
        print(f"[DEBUG] /data/dashboard/latest: Got companies: {companies}") # Debug
        if not companies:
            print("[DEBUG] /data/dashboard/latest: No companies found, returning empty list") # Debug
            return jsonify([]), 200  # Return empty list if no companies

        all_financial_data = []
        for company in companies:
            print(f"[DEBUG] /data/dashboard/latest: Processing company: {company.ticker_symbol}") # Debug
            # Fetch the latest financial data for each company
            latest_data = db.execute(
                """
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
                FROM company c
                JOIN financial_data fd ON c.company_id = fd.company_id
                WHERE c.company_id = ?
                ORDER BY fd.date DESC
                LIMIT 1
                """,
                (company.company_id,)
            ).fetchone()
            print(f"[DEBUG] /data/dashboard/latest: Latest data for {company.ticker_symbol}: {latest_data}")

            if latest_data:
                all_financial_data.append(dict(latest_data))
        print(f"[DEBUG] /data/dashboard/latest: All financial data: {all_financial_data}")
        return jsonify(all_financial_data), 200
    except Exception as e:
        print(f"[ERROR] /data/dashboard/latest: An error occurred: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
        print("[DEBUG] /data/dashboard/latest: Database connection closed")

@api_bp.route('/company/<ticker>', methods=['GET'])  # Corrected route definition
def get_company_data(ticker):
    """
    For company_details page """
    print(f"[DEBUG] /api/company/{ticker}: Entered get_company_data()")
    db_session_factory = database.get_session_local()
    db: Session = db_session_factory()    
    try:
        company = database.get_company_by_ticker(db, ticker)
        print(f"[DEBUG] /api/company/{ticker}: Got company: {company}") # Debug
        if company:
            #   Fetch financial data for the company
            financial_data = database.get_financial_data(db, ticker)
            print(f"[DEBUG] /api/company/{ticker}: Financial Data: {financial_data}")  # Debugging
            # Fetch trend predictions
            trend_predictions = {}  # Placeholder,  You need to implement the logic to fetch this.
            print(f"[DEBUG] /api/company/{ticker}: trend_predictions: {trend_predictions}")
            # Fetch latest news analysis
            latest_news_analysis = {} #  Placeholder,  You need to implement the logic to fetch this.
            print(f"[DEBUG] /api/company/{ticker}: latest_news_analysis: {latest_news_analysis}")
            # Fetch company news
            company_news = [] #  Placeholder,  You need to implement the logic to fetch this.
            print(f"[DEBUG] /api/company/{ticker}: company_news: {company_news}")
            # Fetch industry news
            industry_news = [] #  Placeholder,  You need to implement the logic to fetch this.
            print(f"[DEBUG] /api/company/{ticker}: industry_news: {industry_news}")
            # Fetch similar companies
            similar_companies = [] #  Placeholder,  You need to implement the logic to fetch this.
            print(f"[DEBUG] /api/company/{ticker}: similar_companies: {similar_companies}")
            response_data = {
                'company': {
                    'id': company.company_id,
                    'name': company.company_name,
                    'ticker': company.ticker_symbol,
                    'exchange': company.exchange,
                    'industry': company.industry
                },
                'financial_data': financial_data,
                'trend_predictions': trend_predictions,
                'latest_news_analysis': latest_news_analysis,
                'company_news': company_news,
                'industry_news': industry_news,
                'similar_companies': similar_companies
            }
            print(f"[DEBUG] /api/company/{ticker}: response_data: {response_data}")
            return jsonify(response_data)
        else:
            print(f"[DEBUG] /api/company/{ticker}: Company not found")
            return jsonify({'error': 'Company not found'}), 404
    finally:
        db.close()
        print(f"[DEBUG] /api/company/{ticker}: Database connection closed")

@api_bp.route('/company/<int:company_id>/stock_data')
def get_stock_data(company_id):
    """
    Retrieves stock data for a given company, optionally filtered by time frame. For company_details page
    """
    db = get_db()
    print(f"[DEBUG] /api/company/{company_id}/stock_data: Entered get_stock_data()")
    try:
        timeframe = request.args.get('timeframe', 'all')
        print(f"[DEBUG] /api/company/{company_id}/stock_data: timeframe: {timeframe}")

        if timeframe == '1w':
            view_name = 'weekly_financial_data'
            date_column = 'week'
        elif timeframe == '1m':
            view_name = 'monthly_financial_data'
            date_column = 'month'
        elif timeframe == '1y':
            view_name = 'yearly_financial_data'
            date_column = 'year'
        elif timeframe == 'all':
            # Fetch all available financial data
            query = """
                SELECT 
                    DATE_FORMAT(created_at, '%Y-%m-%d') AS date,
                    close,
                    volume
                FROM financial_data
                WHERE company_id = :company_id
                ORDER BY date ASC
            """
            stock_data = db.execute(query, {'company_id': company_id}).fetchall()
            stock_data = [dict(row) for row in stock_data]
            print(f"[DEBUG] /api/company/{company_id}/stock_data: stock_data (all): {stock_data}") # Debug
            return jsonify({'stock_data': stock_data}), 200
        else:
            print(f"[DEBUG] /api/company/{company_id}/stock_data: Invalid timeframe") # Debug
            return jsonify({'error': 'Invalid timeframe'}), 400

        # Use the appropriate view based on the timeframe
        query = f"""
            SELECT 
                {date_column} as date,
                avg_close AS close,
                total_volume AS volume
            FROM {view_name}
            WHERE company_id = :company_id
            ORDER BY {date_column} ASC
        """
        stock_data = db.execute(query, {'company_id': company_id}).fetchall()
        stock_data = [dict(row) for row in stock_data]
        print(f"[DEBUG] /api/company/{company_id}/stock_data: stock_data: {stock_data}")
        return jsonify({'stock_data': stock_data}), 200

    except Exception as e:
        print(f"[ERROR] /api/company/{company_id}/stock_data: An error occurred: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
        print(f"[DEBUG] /api/company/{company_id}/stock_data: Database connection closed")

@api_bp.route('/company/<int:company_id>/financial_data')
def get_financial_data(company_id):
    """
    Retrieves the latest financial data for a given company. For copmany_details page
    """
    db = get_db()
    print(f"[DEBUG] /api/company/{company_id}/financial_data: Entered get_financial_data()")
    try:
        latest_financial_data = db.query(FinancialData)\
            .filter(FinancialData.company_id == company_id)\
            .order_by(desc(FinancialData.date))\
            .first()
        
        if latest_financial_data:
            # Create a dictionary from the SQLAlchemy object to include all attributes
            financial_data_dict = {
                'date': latest_financial_data.date.isoformat(),
                'open': latest_financial_data.open,
                'high': latest_financial_data.high,
                'low': latest_financial_data.low,
                'close': latest_financial_data.close,
                'volume': latest_financial_data.volume,
                'roi': latest_financial_data.roi,
                'eps': latest_financial_data.eps,
                'pe_ratio': latest_financial_data.pe_ratio,
                'revenue': latest_financial_data.revenue,
                'debt_to_equity': latest_financial_data.debt_to_equity,
                'cash_flow': latest_financial_data.cash_flow,
                # Add any other attributes of the FinancialData model here
            }
            return jsonify({'financial_data': financial_data_dict}), 200
        else:
            print(f"[DEBUG] /api/company/{company_id}/financial_data: No financial data found in DB.")
            return jsonify({'financial_data': {}}), 200 # Return an empty dictionary

    except Exception as e:
        print(f"[ERROR] /api/company/{company_id}/financial_data: An error occurred: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
        print(f"[DEBUG]  /api/company/{company_id}/financial_data: Database connection closed")
