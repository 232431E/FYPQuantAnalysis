# backend/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.models import Base  # Import Base
from backend.app import create_app  # Import your Flask app factory
from backend.config import TEST_DATABASE_URL  # Import the test database URL

@pytest.fixture(scope="session")
def app():
    """Flask application fixture for testing."""
    app = create_app()  # Create the Flask app
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture(scope="session")
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)  # Create tables in the test database
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(engine):
    """Create a new database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
