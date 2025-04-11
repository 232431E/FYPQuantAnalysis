# backend/database.py
import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from flask import g

SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:mySQL2025%21@localhost/fypquantanalysisplatform'
TEST_DATABASE_URL = "sqlite:///:memory:"

Base = declarative_base()

def get_engine():
    if os.environ.get('TESTING'):
        return create_engine(TEST_DATABASE_URL)
    else:
        return create_engine(SQLALCHEMY_DATABASE_URL)

def get_session_local():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    if 'db' not in g:
        g.db = get_session_local()()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    app.teardown_appcontext(close_db)

def delete_news_by_date(db: Session, company_id: int, date_obj: date):
    pass

from sqlalchemy.orm import Session
from .models import data_model
from sqlalchemy import func

def get_company(db: Session, company_id: int):
    return db.query(data_model.Company).filter(data_model.Company.company_id == company_id).first()

def get_company_by_ticker(db: Session, ticker: str):
    return db.query(data_model.Company).filter(data_model.Company.ticker_symbol == ticker).first()

def create_company(db: Session, company: dict):
    print(f"Creating company with data: {company}") # Debug print
    db_company = data_model.Company(**company)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    print(f"Created company with ID: {db_company.company_id}") # Debug print
    return db_company

def create_financial_data(db: Session, financial_data: dict):
    db_financial_data = data_model.FinancialData(**financial_data)
    db.add(db_financial_data)
    db.commit()
    db.refresh(db_financial_data)
    return db_financial_data

def delete_financial_data_by_date(db: Session, company_id: int, date: str):
    deleted_count = db.query(data_model.FinancialData).filter(
        data_model.FinancialData.company_id == company_id,
        data_model.FinancialData.date == date
    ).delete()
    db.commit()
    return deleted_count

def create_news(db: Session, news_data: dict):
    print(f"Creating news with data: {news_data}") # Debug print
    db_news = data_model.News(**news_data)
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    print(f"Created news with ID: {db_news.news_id}") # Debug print
    return db_news

def delete_news_by_date(db: Session, company_id: int, date_obj: date):
    deleted_count = db.query(data_model.News).filter(
        data_model.News.company_id == company_id,
        func.date(data_model.News.published_at) == date_obj
    ).delete()
    db.commit()
    return deleted_count

def get_news_by_company(db: Session, company_id: int, limit: int = 10):
    return db.query(data_model.News).filter(data_model.News.company_id == company_id).order_by(data_model.News.published_at.desc()).limit(limit).all()

# Add more CRUD functions as needed for other models