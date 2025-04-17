from backend.database import get_db, get_all_companies
from backend.services.data_service import fetch_financial_data, store_financial_data
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

def daily_financial_data_update():
    sgt = pytz.timezone('Asia/Singapore')
    now = datetime.now(sgt)
    if now.weekday() < 5:  # Monday to Friday (0-4)
        if now.hour == 6 and now.minute == 0:
            logger.info("Starting daily financial data update...")
            db = get_db()
            try:
                companies = get_all_companies(db)
                for company in companies:
                    logger.info(f"Fetching and storing data for {company.ticker_symbol}...")
                    success = store_financial_data(db, company.ticker_symbol)
                    if success:
                        logger.info(f"Successfully updated data for {company.ticker_symbol}")
                    else:
                        logger.warning(f"Failed to update data for {company.ticker_symbol}")
            finally:
                db.close()
            logger.info("Daily financial data update finished.")
        else:
            logger.debug(f"Skipping data update. Current time is {now.strftime('%H:%M')} SGT.")
    else:
        logger.debug(f"Skipping data update. It's the weekend ({now.strftime('%A')}).")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    daily_financial_data_update()