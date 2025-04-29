#backend/__init__.py
import os

import pytz
print(f"APP_ENV: {os.environ.get('APP_ENV')}")
from flask import Flask
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy here
from backend.tasks import daily_financial_data_update, daily_news_update, update_all_financial_data
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from atexit import register

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy() # Initialize SQLAlchemy instance

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./instance/app.db' # Or your database URI
    # ... other configurations ...
    db.init_app(app) # Initialize db with the app

    from backend.api import api_bp # Import blueprint after app and db are created
    app.register_blueprint(api_bp)

    # Initialize and start the scheduler
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Singapore'))

    from backend.tasks import daily_financial_data_update, daily_news_update, update_all_financial_data # Import the new function

    scheduler.add_job(
        id='update_financial_data_daily',
        func=daily_financial_data_update,
        args=(app,),
        trigger='cron',
        hour=6,
        minute=0,
        day_of_week='mon-fri'
    )
    scheduler.add_job(
        id='update_news_daily',
        func=daily_news_update,
        args=(app,),
        trigger='cron',
        hour=6,
        minute=0,
        day_of_week='mon-fri'
    )
    scheduler.start()
    logger.info("APScheduler started.")
    register(lambda: scheduler.shutdown())
    with app.app_context():
        update_all_financial_data(app)
    logger.info("Initial data update completed.")
    return app

def update_data_on_startup(app):
    """
    Updates financial data on application startup.
    """
    with app.app_context():
        from backend.tasks import update_all_financial_data # Import here
        update_all_financial_data(app)  # Call the function

if __name__ == '__main__':
    app = create_app()
    update_data_on_startup(app)  # Call the function
    app.run(debug=True)
