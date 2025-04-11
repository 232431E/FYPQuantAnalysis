# backend/services/data_service.py
import yfinance as yf
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import data_model
from backend import database
import time

def fetch_daily_news(db: Session, ticker_symbol: str, fetch_date: date):
    try:
        company = database.get_company_by_ticker(db, ticker_symbol)
        if not company:
            print(f"Company with ticker {ticker_symbol} not found in the database.")
            return

        deleted_count = database.delete_news_by_date(db, company.company_id, fetch_date)
        if deleted_count > 0:
            print(f"Deleted {deleted_count} news items for {ticker_symbol} on {fetch_date}.")

        ticker = yf.Ticker(ticker_symbol)
        news_data = ticker.news
        print(f"Raw news data from Yahoo Finance for {ticker_symbol} on {fetch_date}: {news_data}") # Debug print

        for item in news_data:
            print(f"Processing news item: {item}") # Debug print
            timestamp = item.get("publishedAt")
            published_at_datetime = datetime.fromtimestamp(timestamp) if timestamp else None
            news_record = {
                "company_id": company.company_id,
                "title": item.get("title"),
                "description": item.get("summary"),
                "url": item.get("link"),
                "published_at": published_at_datetime
            }
            print(f"News record to be saved: {news_record}") # Debug print
            database.create_news(db, news_record)
        print(f"Successfully retrieved and saved {len(news_data)} news items for {ticker_symbol} on {fetch_date}.")

    except Exception as e:
        print(f"Error fetching news for {ticker_symbol} on {fetch_date}: {e}")

def retry_previous_day_news(db: Session, ticker_symbol: str, failed_date: date):
    previous_date = failed_date - timedelta(days=1)
    print(f"Retrying news retrieval for {ticker_symbol} on {previous_date}...")
    fetch_daily_news(db, ticker_symbol, previous_date)

def delete_news_by_date(db: Session, company_id: int, date_obj: date):
    deleted_count = db.query(data_model.News).filter(
        data_model.News.company_id == company_id,
        func.date(data_model.News.published_at) == date_obj
    ).delete()
    db.commit()
    return deleted_count

# Example of how you might schedule this to run daily for tracked companies
def update_daily_news_for_all_companies(db: Session):
    companies = db.query(data_model.Company).all()
    today = date.today()
    for company in companies:
        fetch_daily_news(db, company.ticker_symbol, today)
        # Consider adding error handling and retries here

# backend/services/data_service.py
from sqlalchemy.orm import Session
from backend.models import data_model
from sqlalchemy import func, extract, text

def get_daily_financial_data(db: Session, company_id: int):
    return db.query(
        data_model.FinancialData.date,
        data_model.FinancialData.open,
        data_model.FinancialData.close,
        data_model.FinancialData.volume
    ).filter(data_model.FinancialData.company_id == company_id).order_by(data_model.FinancialData.date.desc()).all()

from sqlalchemy import func, text

def get_weekly_financial_data(db: Session, company_id: int):
    return db.query(
        func.concat(func.year(data_model.FinancialData.date), '-', func.week(data_model.FinancialData.date)).label('week'),
        func.avg(data_model.FinancialData.open).label('avg_open'),
        func.avg(data_model.FinancialData.close).label('avg_close'),
        func.sum(data_model.FinancialData.volume).label('total_volume')
    ).filter(data_model.FinancialData.company_id == company_id).group_by(
        'week'
    ).order_by(
        text('week DESC')  # Use sqlalchemy.sql.expression.text for aliased columns in ORDER BY
    ).all()

def get_monthly_financial_data(db: Session, company_id: int):
    return db.query(
        func.date_format(data_model.FinancialData.date, '%Y-%m').label('month'),
        func.avg(data_model.FinancialData.open).label('avg_open'),
        func.avg(data_model.FinancialData.close).label('avg_close'),
        func.sum(data_model.FinancialData.volume).label('total_volume')
    ).filter(data_model.FinancialData.company_id == company_id).group_by(
        func.date_format(data_model.FinancialData.date, '%Y-%m')
    ).order_by(
        func.date_format(data_model.FinancialData.date, '%Y-%m').desc()
    ).all()

def get_yearly_financial_data(db: Session, company_id: int):
    return db.query(
        func.year(data_model.FinancialData.date).label('year'),
        func.avg(data_model.FinancialData.open).label('avg_open'),
        func.avg(data_model.FinancialData.close).label('avg_close'),
        func.sum(data_model.FinancialData.volume).label('total_volume')
    ).filter(data_model.FinancialData.company_id == company_id).group_by(
        func.year(data_model.FinancialData.date)
    ).order_by(
        func.year(data_model.FinancialData.date).desc()
    ).all()

def get_latest_news_for_company(db: Session, company_id: int, limit: int = 10):
    return db.query(data_model.News).filter(data_model.News.company_id == company_id).order_by(data_model.News.published_at.desc()).limit(limit).all()