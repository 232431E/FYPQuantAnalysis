# backend/__init__.py
import os
print(f"APP_ENV: {os.environ.get('APP_ENV')}")
from flask import Flask
from backend.api import api_bp
from backend.database import init_db  # Assuming you have a function to initialize the database
from backend.tasks import daily_financial_data_update
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./instance/app.db' # Or your database URI
    # ... other configurations ...
    init_db(app)
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
    
# ... rest of your Redis initialization ...
"""# backend/__init__.py
import os
import redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

r = None  # Initialize to None

if os.environ.get('APP_ENV') != 'testing':
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        print("Connected to Redis")
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
    except redis.exceptions.TimeoutError as e:
        print(f"Timeout connecting to Redis: {e}")

# You might have other initializations here"""