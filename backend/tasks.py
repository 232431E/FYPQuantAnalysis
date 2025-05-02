from sqlalchemy import func
from backend.database import get_db, get_all_companies
from backend.models.data_model import FinancialData, News
from backend.services.data_service import (
    fetch_financial_data,
    store_financial_data,
    fetch_latest_news,
    store_news_articles,
    needs_financial_data_update,  # Unused, so I'll leave it.  Consider removing if truly unused.
)
import logging
from datetime import datetime, timedelta, date  # Import date
import pytz
from flask import Flask
from sqlalchemy.orm import Session
from typing import List, Optional, Union #Import typing

logger = logging.getLogger(__name__)


def update_all_financial_data(app: Flask):
    """Checks and updates financial data for all companies, filling gaps if needed."""
    logger.info("Starting scheduled financial data update check for all companies...")
    with app.app_context():
        db: Session = get_db()
        try:
            companies = get_all_companies(db)
            for company in companies:
                ticker: str = company.ticker_symbol
                company_id: int = company.company_id
                logger.info(f"Checking financial data for {ticker}...")
                most_recent_data: Optional[Union[datetime, date]] = (
                    db.query(func.max(FinancialData.date))
                    .filter(FinancialData.company_id == company_id)
                    .scalar()
                )

                sgt = pytz.timezone("Asia/Singapore")
                now_sgt: date = datetime.now(sgt).date()

                if not most_recent_data:
                    logger.info(
                        f"No financial data found for {ticker}. Fetching up to 5 years of data."
                    )
                    store_financial_data(db, ticker, period="5y")
                else:
                    data_date_sgt: date
                    if isinstance(most_recent_data, date):
                        data_date_sgt = most_recent_data
                    elif isinstance(most_recent_data, datetime):
                        data_date_sgt = most_recent_data.date()  # Extract the date part
                    else:
                        try:
                            data_date_sgt = datetime.strptime(
                                str(most_recent_data), "%Y-%m-%d"
                            ).date()  # Attempt to convert from string
                        except ValueError:
                            logger.error(
                                f"Unexpected date format for {ticker}: {most_recent_data}.  Fetching 5 years of data."
                            )
                            store_financial_data(db, ticker, period="5y")
                            continue  # Skip to the next company

                    days_difference = (now_sgt - data_date_sgt).days
                    if days_difference > 1:
                        logger.info(
                            f"Last financial data for {ticker} is {days_difference} days old. Attempting to fill the gap."
                        )
                        # Fetch data for the missing period. Be mindful of API limits.
                        start_date: date = data_date_sgt + timedelta(days=1)
                        end_date: date = now_sgt
                        historical_data: Optional[List[dict]] = fetch_financial_data(
                            ticker, start=start_date, end=end_date
                        )
                        if historical_data:
                            added_count: int = 0
                            for data_point in historical_data:
                                # Ensure data_point['date'] is a date object
                                point_date: date
                                if isinstance(data_point['date'], date):
                                    point_date = data_point['date']
                                elif isinstance(data_point['date'], datetime):
                                    point_date = data_point['date'].date()
                                else:
                                    try:
                                        point_date = datetime.strptime(
                                            data_point['date'], "%Y-%m-%d"
                                        ).date()
                                    except (TypeError, ValueError) as e:
                                        logger.error(
                                            f"Invalid date format '{data_point['date']}' in fetched data for {ticker}: {e}"
                                        )
                                        continue  # Skip invalid data point

                                existing_record = (
                                    db.query(FinancialData)
                                    .filter(
                                        FinancialData.company_id == company_id,
                                        FinancialData.date == point_date,
                                    )
                                    .first()
                                )
                                if not existing_record:
                                    financial_data = {
                                        "company_id": company_id,
                                        "date": point_date,
                                        "open": data_point["open"],
                                        "high": data_point["high"],
                                        "low": data_point["low"],
                                        "close": data_point["close"],
                                        "volume": data_point["volume"],
                                        # Add other fields if you are fetching them historically
                                    }
                                    db.add(FinancialData(**financial_data))
                                    added_count += 1
                            db.commit()
                            logger.info(
                                f"Added {added_count} missing historical data points for {ticker}."
                            )
                        else:
                            logger.warning(
                                f"Could not fetch missing historical data for {ticker} between {start_date} and {end_date}."
                        )
                    elif days_difference <= 1:
                        logger.info(
                            f"Financial data for {ticker} seems up to date (last updated {days_difference} days ago)."
                        )
        except Exception as e:
            logger.error(f"Error during financial data update: {e}")
            db.rollback()
        finally:
            db.close()
    logger.info("Scheduled financial data update check finished.")



def daily_news_update(app: Flask):
    """Fetches and stores news articles for all companies."""
    sgt = pytz.timezone("Asia/Singapore")
    now: datetime = datetime.now(sgt)
    if now.weekday() < 5 and now.hour == 6 and now.minute == 0:
        logger.info("Starting daily news update...")
        with app.app_context():
            db: Session = get_db()
            logger.debug(f"Database session established: {id(db)}")

            try:
                companies: List = get_all_companies(db)
                logger.info(f"Found {len(companies)} companies for news update")

                for company in companies:
                    ticker: str = company.ticker_symbol
                    logger.info(f"Processing news for {ticker}")
                    try:
                        # Fetch both company and industry news
                        company_news: List[dict]
                        industry_news: List[dict]
                        company_news, industry_news = fetch_latest_news(
                            ticker,
                            company.industry,
                            company.exchange,
                            company.company_name,
                        )

                        logger.info(
                            f"Retrieved {len(company_news)} company news and {len(industry_news)} industry news for {ticker}"
                        )

                        # Store company-specific news
                        if company_news:
                            store_news_articles(db, company.company_id, company_news, "company")

                        # Store industry news
                        if industry_news:
                            store_news_articles(db, company.company_id, industry_news, "industry")

                    except Exception as e:
                        logger.error(f"Error updating news for {ticker}: {e}")
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



def daily_financial_data_update(app: Flask):
    """Fetches and stores the latest financial data for all companies at 6AM SGT."""
    sgt = pytz.timezone('Asia/Singapore')
    now: datetime = datetime.now(sgt)
    if now.weekday() < 5 and now.hour == 6 and now.minute == 0:
        logger.info("Starting scheduled daily financial data update...")
        with app.app_context():
            db: Session = get_db()
            try:
                companies: List = get_all_companies(db)
                for company in companies:
                    ticker: str = company.ticker_symbol
                    logger.info(f"Fetching and storing latest financial data for {ticker} (scheduled)...")
                    success: bool = store_financial_data(db, ticker, period="1d") # Fetch only the last day
                    if success:
                        logger.info(f"Successfully updated latest financial data for {ticker} (scheduled)")
                    else:
                        logger.warning(f"Failed to update latest financial data for {ticker} (scheduled)")
            except Exception as e:
                logger.error(f"Error during daily financial data update: {e}")
                db.rollback()
            finally:
                db.close()
        logger.info("Scheduled daily financial data update finished.")
    else:
        logger.debug(f"Skipping scheduled financial data update. Current time is {now.strftime('%H:%M')} SGT.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # You would typically run the Flask app which would then schedule these tasks
    # This section is for manual testing of the task functions
    from backend import create_app

    app = create_app()
    with app.app_context():
        daily_financial_data_update(app)
        daily_news_update(app)

