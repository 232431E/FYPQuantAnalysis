import sys
import os

# Get the absolute path to the directory containing app.py
app_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path to the project root (the directory containing the 'backend' folder)
project_root = os.path.dirname(app_dir)

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from backend.database import init_db, get_db
from backend.models import data_model_init, report_model_init, prompt_model_init
from sqlalchemy.orm import Session

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

@app.route('/')
def index():
    return redirect('/user/dashboard')

if __name__ == '__main__':
    app.run(debug=True)