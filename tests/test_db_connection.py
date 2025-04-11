"""# tests/test_db_connection.py
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app, db

def test_database_connection():
    try:
        app = create_app(config_class='Config')
        with app.app_context():
            db.engine.connect()
            print("SQLAlchemy connection successful!")
    except Exception as e:
        print(f"SQLAlchemy connection failed: {e}")

if __name__ == '__main__':
    test_database_connection()"""