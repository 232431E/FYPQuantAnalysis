import os
print(f"APP_ENV: {os.environ.get('APP_ENV')}")
from flask import Flask
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy here
# from backend.database import init_db # Remove this import
from backend.tasks import daily_financial_data_update
from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.data_service import scheduled_news_update
import logging

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

    scheduler = BackgroundScheduler(timezone="Asia/Singapore")
    scheduler.add_job(daily_financial_data_update, trigger='cron', hour=6, minute=0, day_of_week='mon-fri')
    scheduler.start()
    logger.info("APScheduler started.")

    # Shut down the scheduler when the app exits
    from atexit import register
    register(lambda: scheduler.shutdown())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)