from functools import wraps
from flask import session, jsonify


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)

    return decorated_function


def permission_required(required_role: str):
    """Simple permission decorator that checks the user's role stored in session.

    This is intentionally simple: it allows the required role or `admin`.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')
            if user_role is None:
                return jsonify({'error': 'Authentication required'}), 401
            if user_role != required_role and user_role != 'admin':
                return jsonify({'error': 'Forbidden'}), 403
            return f(*args, **kwargs)

        return decorated_function

    return decorator
