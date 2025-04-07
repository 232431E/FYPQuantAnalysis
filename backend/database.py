from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.data_model import Base

# Replace with your actual database URL from your .env file
DATABASE_URL = "mysql+mysqlclient://your_user:your_password@your_host/your_database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example CRUD operations (you'll likely expand these)
def create_company(db: SessionLocal, ticker: str, name: str):
    db_company = Company(ticker=ticker, name=name)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company_by_ticker(db: SessionLocal, ticker: str):
    return db.query(Company).filter(Company.ticker == ticker).first()

# Implement similar functions for FinancialData (create, get, etc.)