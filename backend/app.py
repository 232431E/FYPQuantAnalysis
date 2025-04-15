import sys
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from backend.database import get_db, init_db  # Import init_db
from backend.services.data_service import store_financial_data
from sqlalchemy.orm import Session
from flask_cors import CORS
from backend.config import DATABASE_URL
from sqlalchemy import text
from backend.models import Company, FinancialData, Report, data_model_init, report_model_init, prompt_model_init  # Import init functions
import yfinance as yf
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

# Get the directory containing the current script (app.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)


def create_app():  # Added a function
    app = Flask(__name__, template_folder=os.path.join('..', 'frontend', 'templates'),
                    static_folder=os.path.join('..', 'frontend', 'static'),
                    static_url_path='/static')
    CORS(app)
    app.secret_key = os.environ.get('SECRET_KEY') or 'your_default_secret_key'

    # Initialize the database
    with app.app_context():
        init_db(app)  # Initialize the database within the application context
        from backend.models import data_model_init, report_model_init, prompt_model_init  # Import init functions
        data_model_init()
        report_model_init()
        prompt_model_init()  # Call the prompt init function
    return app


app = create_app()  # initialize


# Define a route for the dashboard that doesn't require login
@app.route('/dashboard')
def dashboard():
    """Renders the dashboard template.  Accessible to all users."""
    #  Add logic here to fetch data needed for the dashboard
    #  For example, get some company data to display
    db = get_db()
    try:
        companies = db.query(Company).limit(10).all()  # Get a few companies for display
    except Exception as e:
        print(f"Error querying companies: {e}")
        companies = []
    db.close()
    return render_template('user/dashboard.html', companies=companies)  # Pass data to template



# def login_required(f):
#     """Decorator to require authentication before accessing a route."""
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # if session.get('user_id') is None:
#         #     return redirect(url_for('login'))  # Redirect to login page
#         return f(*args, **kwargs)
#     return decorated_function

def fetch_latest_data_from_yfinance(ticker):
    """Fetches the latest financial data for a ticker from yfinance."""
    try:
        data = yf.download(ticker, period="1d")
        if not data.empty:
            latest_row = data.iloc[-1]
            return {
                "date": latest_row.name.to_pydatetime().date(),
                "open": latest_row['Open'],
                "close": latest_row['Close'],
                "volume": latest_row['Volume']
            }
        return None
    except Exception as e:
        print(f"Error fetching latest data for {ticker} from yfinance: {e}")
        return None


# --- Routes ---

@app.route('/')
# @login_required  # Removed the login_required decorator from the index route
def index():
    """Renders the main dashboard page."""
    return redirect('/dashboard')  # redirect to dashboard


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """Handles user login."""
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db: Session = next(get_db())
#         user = db.query(User).filter_by(username=username).first()
#
#         if user and check_password_hash(user.password_hash, password):
#             session['user_id'] = user.user_id
#             session['username'] = user.username
#             session['role'] = user.role  # Store user role in session
#             return redirect(url_for('index'))  # Redirect to dashboard
#         else:
#             return render_template('user/login.html', error='Invalid username or password')
#
#     return render_template('user/login.html')  # Render login form for GET request

# @app.route('/logout')
# def logout():
#     """Handles user logout."""
#     session.pop('user_id', None)
#     session.pop('username', None)
#     session.pop('role', None)
#     return redirect(url_for('login'))  # Redirect to login page

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     """Handles user registration"""
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         role = 'user'  # Default role
#
#         db: Session = next(get_db())
#         # Check if username or email already exists
#         existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
#         if existing_user:
#             return render_template('user/register.html', error='Username or email already exists')
#
#         hashed_password = generate_password_hash(password)
#         new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#
#         session['user_id'] = new_user.user_id
#         session['username'] = new_user.username
#         session['role'] = new_user.role
#         return redirect(url_for('index'))
#     return render_template('user/register.html')

@app.route('/api/ingest/<ticker>', methods=['POST'])
# @login_required
def ingest_data(ticker):
    """Handles the ingestion of financial data for a given ticker."""
    print(f"Received request to ingest data for ticker: {ticker}")
    db = get_db()  # change here
    try:
        if store_financial_data(db, ticker):
            return jsonify({"message": f"Data ingested for {ticker}. Refresh the table.", "status": "success"}), 200
        else:
            return jsonify({"error": f"Failed to ingest data for {ticker}"}), 500
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@app.route('/api/dashboard/latest', methods=['GET'])
# @login_required
def get_all_financial_data():
    """Retrieves the latest financial data for all companies."""
    db = get_db()  # change here
    try:
        query = text("""
            SELECT
                c.ticker_symbol,
                c.company_name,
                c.industry,
                fd.date,
                fd.open,
                fd.high,
                fd.low,
                fd.close,
                fd.volume
            FROM companies c
            JOIN financial_data fd ON c.company_id = fd.company_id
            ORDER BY c.ticker_symbol, fd.date;
        """)
        all_data = db.execute(query).fetchall()
        results = []
        for row in all_data:
            results.append({
                "ticker_symbol": row.ticker_symbol,
                "company_name": row.company_name,
                "industry": row.industry,
                "date": row.date.isoformat(),
                "open": row.open,
                "high": row.high,
                "low": row.low,
                "close": row.close,
                "volume": row.volume
            })
        return jsonify(results), 200
    except Exception as e:
        print(f"Error fetching all financial data: {e}")
        return jsonify({"error": "Failed to fetch all financial data"}), 500
    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
