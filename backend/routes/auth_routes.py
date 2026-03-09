from flask import Blueprint, request, jsonify, session, flash, redirect, url_for
import datetime
from backend.database import get_session_local
from backend.models import User
from backend.services import user_service

auth_routes = Blueprint('auth', __name__, url_prefix='/auth')


@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['username', 'email', 'password', 'confirm_password']
    missing_fields = [field for field in required_fields if not data or field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    db = get_session_local()()
    try:
        existing_user_email = db.query(User).filter_by(email=data['email']).first()
        if existing_user_email:
            return jsonify({"message": "Email is already registered."}), 400

        existing_user_username = db.query(User).filter_by(username=data['username']).first()
        if existing_user_username:
            return jsonify({"message": "Username is already registered."}), 400
        
        if data['password'] != data['confirm_password']:
            return jsonify({"message": "Password and confirm password do not match."}), 400

        user = user_service.register_user(db, data['username'], data['email'], data['password'])
        print(f"New user registration attempt: {data['username']} - {data['email']}")
        if user:
            log_event = None
            try:
                from backend.utils.audit import log_event as _le
                log_event = _le
            except Exception:
                pass
            if log_event:
                log_event(db, user.user_id, 'registration', request.remote_addr, 'User registered successfully')
            flash('Account registered successfully. Please check your email to verify your account.', 'success')
            return jsonify({"message": "User registered successfully. Please check your email to verify your account."}), 201
        return jsonify({"message": "User registration failed"}), 400
    finally:
        db.close()


@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    db = get_session_local()()
    try:
        # Check if email has been verified
        if not user_service.is_email_verified(db, email):
            flash('Email not verified. Please check your email for the verification link.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if user is locked out
        user = db.query(User).filter_by(email=email).first()
        if user and user.lockout_until and user.lockout_until > datetime.datetime.utcnow():
            flash('Account is temporarily locked due to multiple failed login attempts. Please try again later.', 'danger')
            return redirect(url_for('auth.login'))

        user = user_service.authenticate_user(db, email, password)

        if user:
            session['username'] = user.username
            session['email'] = user.email
            session['user_id'] = user.user_id
            session['role'] = user.role.name if user.role else None
            # try to log event if available
            try:
                from backend.utils.audit import log_event
                log_event(db, user.user_id, 'login', request.remote_addr, 'User logged in successfully')
            except Exception:
                pass
            print(f"User {user.user_id} login event logged")
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
    finally:
        db.close()


@auth_routes.route('/verify-email/<token>', methods=['GET'])
def verify_email_route(token):
    db = get_session_local()()
    try:
        user = user_service.verify_email(db, token)
        if user:
            return redirect(url_for('auth.verification_success'))
        return jsonify({"message": "Invalid or expired verification token"}), 400
    finally:
        db.close()


@auth_routes.route('/email-test', methods=['POST'])
def email_test():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"message": "Email is required"}), 400
    db = get_session_local()()
    try:
        if user_service.email_sending_test(db, data['email']):
            return jsonify({"message": "Test email sent successfully"})
        return jsonify({"message": "Failed to send test email"}), 500
    finally:
        db.close()
