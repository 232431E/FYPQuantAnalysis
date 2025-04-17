from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from backend.services import user_service

user_routes_bp = Blueprint('user', __name__, url_prefix='/user')

@user_routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db: Session = get_db()
        user = db.query(User).filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role  # Store user role in session
            return redirect(url_for('index'))  # Redirect to dashboard
        else:
            return render_template('user/login.html', error='Invalid username or password')

    return render_template('user/login.html')  # Render login form for GET request

@user_routes_bp.route('/logout')
def logout():
    """Handles user logout."""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))  # Redirect to login page

@user_routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  # Default role

        db: Session = get_db()
        # Check if username or email already exists
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return render_template('user/register.html', error='Username or email already exists')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        session['user_id'] = new_user.user_id
        session['username'] = new_user.username
        session['role'] = new_user.role
        return redirect(url_for('index'))
    return render_template('user/register.html')

# The dashboard route was initially in app.py but it's more user-centric, so it's moved here.
@user_routes_bp.route('/dashboard')
def dashboard():
    """Renders the dashboard template. Accessible to all users."""
    # Add logic here to fetch data needed for the dashboard
    # For example, get some company data to display
    db = get_db()
    try:
        from backend.models import Company  # Import Company model here to avoid circular imports
        companies = db.query(Company).all()  # Get a few companies for display
    except Exception as e:
        print(f"Error querying companies: {e}")
        companies = []
    finally:
        db.close()
    return render_template('user/dashboard.html', companies=companies)  # Pass data to template

@user_routes_bp.route('/dashboard/news/<int:user_id>', methods=['GET'])
def get_dashboard_news(user_id: int):
    db: Session = get_db()
    try:
        news = user_service.get_user_dashboard_news(db, user_id)
        return jsonify(news)
    finally:
        db.close()

# The index route redirects to the dashboard, so it can also be considered user-related.
@user_routes_bp.route('/')
def index():
    """Renders the main dashboard page."""
    return redirect('/dashboard')  # redirect to dashboard

# The login_required decorator is user authentication related.
def login_required(f):
    """Decorator to require authentication before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('user.login'))  # Redirect to login page (use blueprint name)
        return f(*args, **kwargs)
    return decorated_function