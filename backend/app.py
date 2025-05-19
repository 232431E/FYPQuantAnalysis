# backend/app.py
import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
import pytz
from flask import Flask, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from backend import database
from backend.database import init_db
from backend.models import data_model_init, report_model_init, prompt_model_init
from sqlalchemy.orm import Session
from backend.services.data_service import fetch_latest_news
from apscheduler.schedulers.background import BackgroundScheduler
from atexit import register
from backend.tasks import daily_news_update, update_all_financial_data
import logging
from dotenv import load_dotenv
load_dotenv()  # for LLM API to be used later

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the scheduler (outside create_app for potential reuse)
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Singapore'))
db = SQLAlchemy()
scheduler_started = False
app = None 

def create_app(testing = None, start_scheduler=True):
    global app
    app = Flask(__name__,
                template_folder=os.path.join('..', 'frontend', 'templates'),
                static_folder=os.path.join('..', 'frontend', 'static'),
                static_url_path='/static')
    CORS(app)
    app.secret_key = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if testing is None:
        app.config['TESTING'] = os.environ.get('FLASK_ENV') == 'testing'
    else:
        app.config['TESTING'] = testing

    if app.config['TESTING']:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        logger.info("Application created in testing mode.")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:mySQL2025%21@localhost/fypquantanalysisplatform'
        logger.info(f"Application created with database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        logger.info("Application running in real time")

    db.init_app(app)
    
    with app.app_context():
        init_db(app)
        data_model_init()
        report_model_init()
        prompt_model_init()
        db.create_all()
        if not app.config['TESTING'] and start_scheduler:
            logger.info("Starting background tasks (scheduler and initial data update).")
            global scheduler_started
            if not scheduler_started:
                scheduler.add_job(func=daily_news_update, trigger='cron', hour=6, minute=0, day_of_week='mon-fri', args=(app,))
                scheduler.add_job(func=update_all_financial_data, trigger='cron', hour=14, minute=43, day_of_week='mon-fri', args=(app,))
                scheduler.start()
                print("Scheduler started for daily news and financial data updates on weekdays.")
                register(scheduler.shutdown)
                update_all_financial_data(app)
                logger.info("Initial data update completed.")
                scheduler_started = True
        elif app.config['TESTING']:
            logger.info("Background tasks (scheduler and initial data update) skipped in testing mode.")

    from backend.routes.user_routes import user_routes_bp
    from backend.routes.data_routes import data_routes_bp
    from backend.routes.report_routes import report_routes_bp
    from backend.routes.llm_routes import llm_routes_bp
    from backend.routes.feedback_routes import feedback_routes_bp
    from backend.routes.backtesting_routes import backtesting_routes_bp
    from backend.routes.graph_routes import graph_routes_bp
    from backend.routes.download_routes import download_routes_bp
    from backend.routes.alert_routes import alert_routes_bp

    app.register_blueprint(user_routes_bp)
    app.register_blueprint(data_routes_bp)
    app.register_blueprint(report_routes_bp)
    app.register_blueprint(llm_routes_bp)
    app.register_blueprint(feedback_routes_bp)
    app.register_blueprint(backtesting_routes_bp)
    app.register_blueprint(graph_routes_bp)
    app.register_blueprint(download_routes_bp)
    app.register_blueprint(alert_routes_bp)

    from backend.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return redirect('/user/dashboard')

    @app.route('/company_details.html')
    def company_details():
            return render_template('user/company_details.html')

    @app.route('/company/<ticker>')
    def company_detail_page(ticker):
        return render_template('company_details.html', ticker=ticker)

    @app.route('/api/company/<ticker>/news', methods=['GET'])
    def get_company_news(ticker):
        db: Session = database.SessionLocal()
        try:
            company = database.get_company_by_ticker(db, ticker)
            if company:
                news_articles = fetch_latest_news(ticker, company.industry, company.exchange)
                top_company_news = news_articles[:5]
                industry_news = fetch_latest_news(company.industry, company.industry, company.exchange)[:3]
                return jsonify({'company_news': top_company_news, 'industry_news': industry_news})
            else:
                return jsonify({'error': 'Company not found'}), 404
        finally:
            db.close()
            
    return app

if __name__ == '__main__':
    app = create_app(start_scheduler=True) # Create app for running directly
    if app:
        app.run(debug=True, use_reloader=False)