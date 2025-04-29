# backend/tasks.py
from backend.database import get_db, get_all_companies
from backend.models.data_model import News
from backend.services.data_service import (
    fetch_financial_data, 
    store_financial_data, 
    fetch_latest_news, 
    store_news_articles,
    needs_financial_data_update
)
import logging
from datetime import datetime
import pytz
from flask import Flask

logger = logging.getLogger(__name__)

def update_all_financial_data(app: Flask):
    """Checks and updates financial data for all companies if needed."""
    logger.info("Starting on-demand financial data update check for all companies...")
    with app.app_context():
        db = get_db()
        try:
            companies = get_all_companies(db)
            for company in companies:
                ticker = company.ticker_symbol
                company_id = company.company_id
                logger.info(f"Checking if financial data needs update for {ticker}...")
                if needs_financial_data_update(db, company_id):
                    logger.info(f"Financial data for {ticker} is outdated or missing, attempting to update...")
                    success = store_financial_data(db, ticker)
                    if success:
                        logger.info(f"Successfully updated financial data for {ticker}")
                    else:
                        logger.warning(f"Failed to update financial data for {ticker}")
                else:
                    logger.info(f"Financial data for {ticker} is already up to date.")
        finally:
            db.close()
    logger.info("On-demand financial data update check finished.")

def daily_financial_data_update(app: Flask):
    sgt = pytz.timezone('Asia/Singapore')
    now = datetime.now(sgt)
    if now.weekday() < 5:  # Monday to Friday (0-4)
        if now.hour == 6 and now.minute == 0:
            logger.info("Starting scheduled daily financial data update...")
            with app.app_context():
                db = get_db()
                try:
                    companies = get_all_companies(db)
                    for company in companies:
                        logger.info(f"Fetching and storing financial data for {company.ticker_symbol} (scheduled)...")
                        success = store_financial_data(db, company.ticker_symbol)
                        if success:
                            logger.info(f"Successfully updated financial data for {company.ticker_symbol} (scheduled)")
                        else:
                            logger.warning(f"Failed to update financial data for {company.ticker_symbol} (scheduled)")
                finally:
                    db.close()
            logger.info("Scheduled daily financial data update finished.")
        else:
            logger.debug(f"Skipping scheduled financial data update. Current time is {now.strftime('%H:%M')} SGT.")
    else:
        logger.debug(f"Skipping scheduled financial data update. It's the weekend ({now.strftime('%A')}).")

# backend/tasks.py
def daily_news_update(app: Flask):
    sgt = pytz.timezone('Asia/Singapore')
    now = datetime.now(sgt)
    if now.weekday() < 5 and now.hour == 6 and now.minute == 0:
        logger.info("Starting daily news update...")
        with app.app_context():
            db = get_db()
            logger.debug(f"Database session established: {id(db)}")

            try:
                companies = get_all_companies(db)
                logger.info(f"Found {len(companies)} companies for news update")

                for company in companies:
                    logger.info(f"Processing news for {company.ticker_symbol}")
                    try:
                        # Fetch both company and industry news
                        company_news, industry_news = fetch_latest_news(
                            company.ticker_symbol,
                            company.industry,
                            company.exchange,
                            company.company_name
                        )

                        logger.info(f"Retrieved {len(company_news)} company news and {len(industry_news)} industry news for {company.ticker_symbol}")

                        # Store company-specific news
                        if company_news:
                            store_news_articles(db, company.company_id, company_news, "company")

                        # Store industry news
                        if industry_news:
                            store_news_articles(db, company.company_id, industry_news, "industry")

                    except Exception as e:
                        logger.error(f"Error updating news for {company.ticker_symbol}: {e}")
                        # Continue with next company rather than breaking the loop
                        continue

                db.commit()  # Commit all changes after processing all companies

            except Exception as overall_error:
                logger.error(f"An overall error occurred during news update: {overall_error}")
                db.rollback()

            finally:
                db.close()
                logger.debug("Database session closed")

        logger.info("Daily news update finished.")
    else:
        logger.debug(f"Skipping news update. Current time is {now.strftime('%H:%M')} SGT.")
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # You would typically run the Flask app which would then schedule these tasks
    # This section is for manual testing of the task functions
    from backend import create_app
    app = create_app()
    # with app.app_context():
    #     daily_financial_data_update(app)
    #     daily_news_update(app)