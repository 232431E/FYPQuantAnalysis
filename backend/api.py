#backend/api.py
from flask import Blueprint, jsonify
from backend.database import get_all_companies, get_db, get_company_by_ticker
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
    Retrieves the latest financial data for all companies for the dashboard.
    """
    db = get_db()
    try:
        companies = get_all_companies(db)  # Get all companies
        if not companies:
            return jsonify([]), 200  # Return empty list if no companies

        all_financial_data = []
        for company in companies:
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

            if latest_data:
                all_financial_data.append(dict(latest_data))
        return jsonify(all_financial_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
@api_bp.route('/company/<ticker>', methods=['GET'])
def get_company_info(ticker):
    db = get_db()
    company = get_company_by_ticker(db, ticker)
    if not company:
        return jsonify({'error': 'Company not found'}), 404

    # Fetch historical financial data (e.g., for the last 5 years)
    financial_data = fetch_financial_data(ticker, period='5y')

    # Predict financial trends
    trend_predictions = predict_financial_trends(financial_data)

    # Fetch latest news (you might need to adjust parameters)
    news_articles = fetch_latest_news(ticker, company.industry, company.exchange)

    # Analyze news sentiment (using a placeholder LLM for now)
    llm_model = os.environ.get('LLM_MODEL', 'default-llm') # Configure your LLM model
    latest_news_analysis = analyze_news_sentiment(news_articles[:3], llm_model) # Analyze a few latest articles

    # Get top news (you might need to refine this based on LLM integration)
    top_news = [article['title'] for article in news_articles[:5]] # Example: Top 5 titles

    # Get similar companies
    similar_companies = get_similar_companies(company.industry)

    company_info = {
        'company': {
            'ticker': company.ticker_symbol,
            'name': company.company_name,
            'exchange': company.exchange,
            'industry': company.industry
        },
        'financial_data': financial_data,
        'trend_predictions': trend_predictions,
        'latest_news_analysis': latest_news_analysis,
        'top_news': top_news,
        'similar_companies': similar_companies
    }

    return jsonify(company_info)