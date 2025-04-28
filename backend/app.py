#backend/app.py
import sys
import os

import pytz

# Get the absolute path to the directory containing app.py
app_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path to the project root (the directory containing the 'backend' folder)
project_root = os.path.dirname(app_dir)

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from backend import database
from backend.database import init_db, get_db
from backend.models import data_model_init, report_model_init, prompt_model_init
from sqlalchemy.orm import Session
from backend.services.data_service import fetch_latest_news
from apscheduler.schedulers.background import BackgroundScheduler
from backend.tasks import daily_news_update

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join('..', 'frontend', 'templates'),
                static_folder=os.path.join('..', 'frontend', 'static'),
                static_url_path='/static')
    CORS(app)
    app.secret_key = os.environ.get('SECRET_KEY') or 'your_default_secret_key'

    # Initialize the database
    with app.app_context():
        init_db(app)
        data_model_init()
        report_model_init()
        prompt_model_init()

    # Import Blueprints
    from backend.routes.user_routes import user_routes_bp
    from backend.routes.data_routes import data_routes_bp
    from backend.routes.report_routes import report_routes_bp
    from backend.routes.llm_routes import llm_routes_bp
    from backend.routes.feedback_routes import feedback_routes_bp
    from backend.routes.backtesting_routes import backtesting_routes_bp
    from backend.routes.visualization_routes import visualisation_routes_bp
    from backend.routes.download_routes import download_routes_bp
    from backend.routes.alert_routes import alert_routes_bp

    # Register Blueprints
    app.register_blueprint(user_routes_bp)
    app.register_blueprint(data_routes_bp)
    app.register_blueprint(report_routes_bp)
    app.register_blueprint(llm_routes_bp)
    app.register_blueprint(feedback_routes_bp)
    app.register_blueprint(backtesting_routes_bp)
    app.register_blueprint(visualisation_routes_bp)
    app.register_blueprint(download_routes_bp)
    app.register_blueprint(alert_routes_bp)

    return app

app = create_app()

from backend.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Initialize the scheduler
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Singapore'))

# Schedule the news update job for 6:00 AM SGT on weekdays (Monday-Friday)
scheduler.add_job(func=daily_news_update, trigger='cron', hour=6, minute=0, day_of_week='mon-fri', args=(app,))

# Start the scheduler (this will run in the background)
scheduler.start()

# It's good practice to shut down the scheduler when the app exits
import atexit
def shutdown_scheduler():
    scheduler.shutdown()
atexit.register(shutdown_scheduler)

print("Scheduler started for daily news updates at 6:00 AM SGT on weekdays.")

@app.route('/')
def index():
    return redirect('/user/dashboard')

@app.route('/api/company/<ticker>/news', methods=['GET'])
def get_company_news(ticker):
    db: Session = database.SessionLocal()
    try:
        company = database.get_company_by_ticker(db, ticker)
        if company:
            news_articles = fetch_latest_news(ticker, company.industry, company.exchange)
            # You might want to limit the number of articles here
            top_company_news = news_articles[:5]

            # Fetch industry news (you might need a way to get a list of companies in the same industry
            # and then fetch news related to the industry in general or top companies in it)
            # This is a simplified approach - you might need a more sophisticated way to get relevant industry news
            industry_news = fetch_latest_news(company.industry, company.industry, company.exchange)[:3]

            return jsonify({
                'company_news': top_company_news,
                'industry_news': industry_news
            })
        else:
            return jsonify({'error': 'Company not found'}), 404
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)