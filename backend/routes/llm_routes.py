# backend/routes/llm_routes.py
from flask import Blueprint, abort, jsonify
from backend.database import get_db, get_company
from sqlalchemy.orm import Session
from backend.models import News, Company
from backend.services.llm_service import analyze_news_sentiment_gemini
from sqlalchemy import select
import logging
from werkzeug.exceptions import NotFound 

logger = logging.getLogger(__name__)
llm_routes_bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@llm_routes_bp.errorhandler(NotFound)
def not_found(error):
    logger.debug(f"Handling NotFound error in Blueprint: {error}")
    response = jsonify({'error': error.description})
    response.status_code = 404
    return response

@llm_routes_bp.route('/sentiment/<int:company_id>', methods=['GET'])
def get_company_news_sentiment(company_id):
    """Retrieves news for a company and analyzes its sentiment using Gemini."""
    db: Session = get_db()
    try:
        company = db.get(Company, company_id)
        if not company:
            return jsonify({"error": "Company not found"}), 404

        # Retrieve news articles for the company
        news_articles = db.query(News).filter(News.company_id == company_id).order_by(News.published_date.desc()).limit(10).all() # Adjust limit as needed
        if not news_articles:
            return jsonify({"sentiment_analysis": {"brief": "No news available for analysis.", "sentiment": "Neutral"}}), 200

        # Construct the prompt for Gemini
        news_text = "\n".join([f"Title: {news.title}\nSummary: {news.summary}" for news in news_articles])
        prompt = f"""Analyze the overall sentiment of the following news articles for {company.company_name} (ticker: {company.ticker_symbol}, industry: {company.industry}):

        {news_text}

        Consider the information provided, as well as any potential geopolitical factors and your own general knowledge/research, to determine the overall sentiment towards the company. Provide:
        1. A brief overall sentiment (e.g., Positive, Negative, Mixed, Neutral).
        2. A more detailed explanation of the factors contributing to this sentiment, including any relevant geopolitical influences.
        """
        logger.debug(f"Prompt for LLM: {prompt}")
        # Analyze sentiment using Gemini
        sentiment_result = analyze_news_sentiment_gemini([{"title": news.title, "description": news.summary} for news in news_articles]) # Adapt the structure if needed

        return jsonify({"sentiment_analysis": sentiment_result}), 200
    except NotFound:
        raise  # Re-raise NotFound to be handled by Flask's default error handler
    except Exception as e:
        logger.error(f"An error occurred during sentiment analysis: {e}", exc_info=True)
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@llm_routes_bp.route('/report/<int:company_id>', methods=['GET'])
def get_llm_report(company_id):
    """
    Generates an LLM-powered report for a given company, including sentiment analysis of recent news.
    """
    db: Session = get_db()
    try:
        logger.debug(f"Fetching company with ID: {company_id}")
        company = get_company(db, company_id)
        logger.debug(f"Fetched company: {company}")     
        if not company:
            logger.warning(f"Company with ID {company_id} not found.")
            abort(NotFound(description="Company not found"))
        logger.debug(f"Company name from DB: {company.company_name}, Ticker: {company.ticker_symbol}")
        # Retrieve news articles for the company, ordered by published date
        logger.debug(f"Fetching news for company ID: {company_id}")
        news_articles = db.query(News).filter(News.company_id == company_id).order_by(
            News.published_date.desc()
        ).limit(10).all()
        logger.debug(f"Found {len(news_articles)} news articles.")

        if not news_articles:
            logger.debug(f"No news articles found for company ID {company_id}. Returning default report.")
            # Return a 200 with a default report for the no-news case
            report_data = {
                "overall_news_summary": "No news available.",
                "sentiment_analysis": {
                    "brief": "No news available for analysis.",
                    "sentiment": "Neutral",
                    "general_outlook": "No specific outlook due to lack of information.",
                    "investment_advice": "Insufficient information for investment advice."
                },
                "paragraph_section": "No significant news to report.",
                "company_name": company.company_name,  # Include company info
                "ticker_symbol": company.ticker_symbol
            }
            logger.debug(f"Report data before response: {report_data}")
            return jsonify({"report": report_data}), 200

        # Analyze sentiment of the news articles
        news_for_llm = [{"title": news.title, "description": news.summary} for news in news_articles]
        logger.debug("Calling analyze_news_sentiment_gemini")
        sentiment_analysis = analyze_news_sentiment_gemini(news_for_llm, llm_model='gemini-pro')
        logger.debug("Received sentiment analysis from LLM service.")

        # Construct the report
        report_data = {
            "overall_news_summary": sentiment_analysis.get("overall_summary", "Summary N/A"),
            "sentiment_analysis": sentiment_analysis,
            "paragraph_section": sentiment_analysis.get("full_report", "Full Report N/A"),
            "company_name": company.company_name,
            "ticker_symbol": company.ticker_symbol,
        }
        logger.debug("Report data constructed. Returning response.")
        return jsonify({"report": report_data}), 200
    except NotFound:  # Catch the NotFound exception
        raise  # Re-raise it so Flask's error handler can manage it
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        logger.debug("Closing database session.")
        db.close()