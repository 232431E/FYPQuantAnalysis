from flask import Blueprint, jsonify
from backend.database import get_db, get_company_by_ticker
from backend.services.data_service import (
    fetch_financial_data,
    fetch_historical_fundamentals,
    store_financial_data,
    fetch_latest_news,
    get_similar_companies,
    store_news_articles,
    get_stored_news,
    predict_financial_trends,
    analyze_news_sentiment,
    get_similar_companies
)
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

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