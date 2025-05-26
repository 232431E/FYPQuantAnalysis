# backend/routes/llm_routes.py
# all IN USE (for news report gen)
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
    print(f"[DEBUG - Backend - Route] Entering get_company_news_sentiment for company_id: {company_id}")

    try:
        company = db.get(Company, company_id)
        if not company:
            print(f"[DEBUG - Backend - Route] Company with ID {company_id} not found in database.")
            return jsonify({"error": "Company not found"}), 404

        # Retrieve news articles for the company
        news_articles = db.query(News).filter(News.company_id == company_id).order_by(News.published_date.desc()).limit(10).all() # Adjust limit as needed
        if not news_articles:
            return jsonify({"sentiment_analysis": {
                "brief_overall_sentiment": "Neutral",
                "market_outlook": "Insufficient information.",
                "detailed_explanation": "No news available to analyze political or geopolitical factors."
            }}), 200
        company_name = company.company_name
        ticker = company.ticker_symbol
        industry = company.industry
        # Construct the prompt for Gemini
        news_articles_formatted = "\n".join([
            f"Title: {article.title}\nLink: {article.link}\nSummary: {article.summary}"
            for article in news_articles
        ])
        custom_prompt = f"""
        Analyze the overall sentiment of the following recent news articles for {company_name} (ticker: {ticker}, industry: {industry}).
        **IMPORTANT FORMATTING INSTRUCTIONS:**
        Instead of Markdown formatting (like **bold**), please use standard HTML tags directly for emphasis (e.g., <strong>text</strong>, <em>text</em>, <u>text</u>). Do NOT use Markdown syntax (like asterisks).

        Additionally, based on your knowledge and the provided news, identify:
        - Key products/services/subsidiaries of {company_name}.
        - Any significant financial predictions or important financial news that directly impacts the market outlook.
        - Important upcoming or recent past financial key events/meetings (e.g., earnings calls, investor days, product launches, regulatory deadlines) with their dates and a brief explanation of their potential or actual impact.

        Consider potential environmental factors, company structure (human factors), financial reports, political, and geopolitical factors that might influence the company or its market.

        **Recent News Articles for Analysis:**
        {news_articles_formatted}

        Provide a comprehensive analysis in JSON format with the following specific keys and content:

        1.  <strong>"overall_news_summary"</strong>: A concise summary of the key news trends and events, using HTML for emphasis.
        2.  <strong>"brief_overall_sentiment"</strong>: A brief sentiment (e.g., Positive, Negative, Mixed, Neutral) accompanied by a confidence score out of 100 (e.g., "Mixed (Score: 60/100)"). Briefly explain the score.
        3.  <strong>"reasons_for_sentiment"</strong>: A detailed explanation of <em>why</em> the overall sentiment is as it is, explicitly mentioning the positive, negative, and neutral factors (including financial reports, political/geopolitical factors, environmental, and company structure/human factors) from the news that contribute to this sentiment. Use HTML for emphasis.
        4.  <strong>"market_outlook"</strong>: Describe the potential near-term market outlook for this company based on the news, identifying key drivers. Use HTML for emphasis.
        5.  <strong>"detailed_explanation"</strong>: Elaborate on the "Market Outlook," providing specific financial predictions, important financial news, and other relevant details that explain <em>why</em> the market outlook is as stated. Use HTML for emphasis.
        6.  <strong>"key_offerings"</strong>: A list of {company_name}'s best-selling or most significant products, services, and/or subsidiaries.
        7.  <strong>"financial_dates"</strong>: An array of objects, each representing a key financial event. Each object should have:
            * <strong>"date"</strong>: The date of the event (e.g., "2025-05-15" or "Q3 2024").
            * <strong>"event"</strong>: A brief description of the event (e.g., "Q4 Earnings Call", "Investor Day", "Regulatory Decision on Merger").
            * <strong>"impact"</strong>: A short explanation of its potential or actual impact on market outlook and sentiment.
        
        Ensure all required fields are present in the JSON output.
        """
        print("[DEBUG - Backend] Constructed LLM Prompt:\n", custom_prompt)
        sentiment_result = analyze_news_sentiment_gemini(
            news_articles=[{'title': n.title, 'description': n.summary, 'link': n.link} for n in news_articles],
            prompt=custom_prompt, llm_model='gemini-2.0-flash-lite')
        print("[DEBUG - Backend] Received sentiment_result from service:\n", sentiment_result)
        return jsonify({"report": sentiment_result}), 200
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
    print(f"[DEBUG - Backend - Route] Entering get_llm_report for company_id: {company_id}")

    try:
        logger.debug(f"Fetching company with ID: {company_id}")
        company = get_company(db, company_id)
        logger.debug(f"Fetched company: {company}")     
        if not company:
            logger.warning(f"Company with ID {company_id} not found.")
            return jsonify({'error': "Company not found"}), 404 # Temporary change
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
        sentiment_analysis = analyze_news_sentiment_gemini(news_for_llm, llm_model='gemini-2.0-flash-lite')
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