# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from flask import g
from datetime import date  # Import date from datetime

SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:mySQL2025%21@localhost/fypquantanalysisplatform'
TEST_DATABASE_URL = "sqlite:///:memory:"

Base = declarative_base()  # Define Base *before* importing models

# Import your models here
from backend.models import User, Alert, Feedback, PromptVersion, Report, Company, FinancialData, News

def get_engine():
    if os.environ.get('TESTING'):
        return create_engine(TEST_DATABASE_URL)
    else:
        return create_engine(SQLALCHEMY_DATABASE_URL)

engine = get_engine()  # Create the engine
Base.metadata.create_all(bind=engine)  # Create the tables

def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    if 'db' not in g:
        g.db = get_session_local()()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):  # Keep the init_db function, but only for teardown
    app.teardown_appcontext(close_db)

# --- CRUD Operations ---
# Import models here, inside the file, to avoid circular imports.
from sqlalchemy.orm import Session
from backend.models.alert_model import Alert
from backend.models.data_model import Company, FinancialData, News
from backend.models.feedback_model import Feedback
from backend.models.prompt_model import PromptVersion
from backend.models.report_model import Report
from backend.models.user_model import User
from sqlalchemy import func, text
from typing import Optional, List, Dict, Any

# Helper function to handle common session operations
def _commit_and_refresh(db: Session, instance: Any) -> None:
    """Commits the session and refreshes the instance."""
    db.commit()
    db.refresh(instance)

# --- Company CRUD Operations ---
def get_all_companies(db: Session):
    return db.query(Company).all()

def get_company(db: Session, company_id: int) -> Optional[Company]:
    """Retrieves a company by its ID."""
    return db.query(Company).filter(Company.company_id == company_id).first()

def get_company_by_ticker(db: Session, ticker: str) -> Optional[Company]:
    """Retrieves a company by its ticker symbol."""
    return db.query(Company).filter(Company.ticker_symbol == ticker).first()

def create_company(db: Session, company_data: Dict[str, Any]) -> Company:
    """Creates a new company record."""
    db_company = Company(**company_data)
    db.add(db_company)
    _commit_and_refresh(db, db_company)
    return db_company

def update_company(db: Session, company_id: int, company_data: Dict[str, Any]) -> Optional[Company]:
    """Updates an existing company record."""
    db_company = get_company(db, company_id)
    if db_company:
        for key, value in company_data.items():
            setattr(db_company, key, value)
        _commit_and_refresh(db, db_company)
        return db_company
    return None  # Return None if company not found

def delete_company(db: Session, company_id: int) -> bool:
    """Deletes a company record."""
    db_company = get_company(db, company_id)
    if db_company:
        db.delete(db_company)
        db.commit()
        return True
    return False

# --- Financial Data CRUD Operations ---
def get_financial_data(db: Session, financial_data_id: int) -> Optional[FinancialData]:
    """Gets financial data by its ID."""
    return db.query(FinancialData).filter(FinancialData.data_id == financial_data_id).first() # Changed data_id

def create_financial_data(db: Session, financial_data: Dict[str, Any]) -> FinancialData:
    """Creates a new financial data record."""
    db_financial_data = FinancialData(**financial_data)
    db.add(db_financial_data)
    _commit_and_refresh(db, db_financial_data)
    return db_financial_data

def create_financial_data_list(db: Session, financial_data_list: List[Dict[str, Any]]) -> int:
    """Creates multiple financial data records, handling duplicates."""
    added_count = 0
    for data in financial_data_list:
        existing_record = check_existing_financial_data(db, data['company_id'], data['date'])
        if not existing_record:
            db_financial_data = FinancialData(**data)
            db.add(db_financial_data)
            added_count += 1
    db.commit()
    return added_count

from sqlalchemy.orm import Session
from backend.models.data_model import FinancialData

def update_financial_data(db: Session, company_id: int, date: date, updated_fields: dict):
    try:
        record_to_update = db.query(FinancialData).filter(
            FinancialData.company_id == company_id,
            FinancialData.date == date
        ).first()
        if record_to_update:
            for key, value in updated_fields.items():
                if hasattr(record_to_update, key):
                    setattr(record_to_update, key, value)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise

def delete_financial_data(db: Session, financial_data_id: int) -> bool:
    """Deletes a financial data record by its ID."""
    db_financial_data = get_financial_data(db, financial_data_id)
    if db_financial_data:
        db.delete(db_financial_data)
        db.commit()
        return True
    return False

def delete_financial_data_by_date(db: Session, company_id: int, date_obj: date) -> int:
    """Deletes financial data records for a company on a specific date."""
    deleted_count = db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.date == date_obj
    ).delete()
    db.commit()
    return deleted_count

def get_latest_financial_data(db: Session, company_id: int) -> Optional[FinancialData]:
    """Retrieves the latest financial data for a company."""
    return db.query(FinancialData).filter(FinancialData.company_id == company_id).order_by(
        FinancialData.date.desc()).first()

def get_latest_financial_data_from_view(db: Session) -> List[FinancialData]:
    """Retrieves the latest financial data for all companies using a view."""
    #  Use the ORM to query from the view
    return db.query(FinancialData).from_statement(text("SELECT * FROM latest_company_financial_data")).all()

def check_existing_financial_data(db: Session, company_id: int, date: date) -> Optional[FinancialData]:
    """Checks if financial data exists for a company on a specific date."""
    return db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.date == date
    ).first()

# --- News CRUD Operations ---
def get_news(db: Session, news_id: int) -> Optional[News]:
    """Gets a news item by its ID"""
    return db.query(News).filter(News.news_id == news_id).first()

def create_news(db: Session, news_data: Dict[str, Any]) -> News:
    """Creates a new news record."""
    db_news = News(**news_data)
    db.add(db_news)
    _commit_and_refresh(db, db_news)
    return db_news

def update_news(db: Session, news_id: int, news_data: Dict[str, Any]) -> Optional[News]:
    """Updates an existing news record."""
    db_news = get_news(db, news_id)
    if db_news:
        for key, value in news_data.items():
            setattr(db_news, key, value)
        _commit_and_refresh(db, db_news)
        return db_news
    return None

def delete_news(db: Session, news_id: int) -> bool:
    """Deletes a news item by its ID."""
    db_news = get_news(db, news_id)
    if db_news:
        db.delete(db_news)
        db.commit()
        return True
    return False

def delete_news_by_date(db: Session, company_id: int, date_obj: date) -> int:
    """Deletes news articles for a company on a specific date."""
    deleted_count = db.query(News).filter(
        News.company_id == company_id,
        func.date(News.published_date) == date_obj # changed published_at to published_date
    ).delete()
    db.commit()
    return deleted_count

def get_news_by_company(db: Session, company_id: int, limit: int = 10) -> List[News]:
    """Retrieves news articles for a company, ordered by publication date."""
    return db.query(News).filter(News.company_id == company_id).order_by(
        News.published_date.desc() # changed published_at to published_date
    ).limit(limit).all()

# --- Alert CRUD Operations ---
def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    """Gets an alert by its ID."""
    return db.query(Alert).filter(Alert.alert_id == alert_id).first()

def create_alert(db: Session, alert_data: Dict[str, Any]) -> Alert:
    """Creates a new alert record."""
    db_alert = Alert(**alert_data)
    db.add(db_alert)
    _commit_and_refresh(db, db_alert)
    return db_alert

def update_alert(db: Session, alert_id: int, alert_data: Dict[str, Any]) -> Optional[Alert]:
    """Updates an existing alert record."""
    db_alert = get_alert(db, alert_id)
    if db_alert:
        for key, value in alert_data.items():
            setattr(db_alert, key, value)
        _commit_and_refresh(db, db_alert)
        return db_alert
    return None

def delete_alert(db: Session, alert_id: int) -> bool:
    """Deletes an alert record."""
    db_alert = get_alert(db, alert_id)
    if db_alert:
        db.delete(db_alert)
        db.commit()
        return True
    return False

# --- Report CRUD Operations ---
def get_report(db: Session, report_id: int) -> Optional[Report]:
    """Gets a report by its ID."""
    return db.query(Report).filter(Report.report_id == report_id).first()

def create_report(db: Session, report_data: Dict[str, Any]) -> Report:
    """Creates a new report record."""
    db_report = Report(**report_data)
    db.add(db_report)
    _commit_and_refresh(db, db_report)
    return db_report

def update_report(db: Session, report_id: int, report_data: Dict[str, Any]) -> Optional[Report]:
    """Updates an existing report record."""
    db_report = get_report(db, report_id)
    if db_report:
        for key, value in report_data.items():
            setattr(db_report, key, value)
        _commit_and_refresh(db, db_report)
        return db_report
    return None

def delete_report(db: Session, report_id: int) -> bool:
    """Deletes a report record."""
    db_report = get_report(db, report_id)
    if db_report:
        db.delete(db_report)
        db.commit()
        return True
    return False

# --- Feedback CRUD Operations ---
def get_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    """Gets a feedback by its ID."""
    return db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()

def create_feedback(db: Session, feedback_data: Dict[str, Any]) -> Feedback:
    """Creates a new feedback record."""
    db_feedback = Feedback(**feedback_data)
    db.add(db_feedback)
    _commit_and_refresh(db, db_feedback)
    return db_feedback

def update_feedback(db: Session, feedback_id: int, feedback_data: Dict[str, Any]) -> Optional[Feedback]:
    """Updates an existing feedback record."""
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback:
        for key, value in feedback_data.items():
            setattr(db_feedback, key, value)
        _commit_and_refresh(db, db_feedback)
        return db_feedback
    return None

def delete_feedback(db: Session, feedback_id: int) -> bool:
    """Deletes a feedback record."""
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback:
        db.delete(db_feedback)
        db.commit()
        return True
    return False

# --- Prompt CRUD Operations ---
def create_prompt_version(db: Session, user_id: int, original_prompt: str, prompt_text: str):
    latest_prompt = db.query(PromptVersion).order_by(PromptVersion.prompt_id.desc()).first()
    next_prompt_id = 1 if not latest_prompt else latest_prompt.prompt_id + 1
    db.query(PromptVersion).filter(PromptVersion.prompt_id == next_prompt_id, PromptVersion.operative == True).update({PromptVersion.operative: False})
    latest_version = db.query(PromptVersion).filter(PromptVersion.prompt_id == next_prompt_id).order_by(PromptVersion.version.desc()).first()
    next_version = 1 if not latest_version else latest_version.version + 1
    db_prompt_version = PromptVersion(
        prompt_id=next_prompt_id,
        user_id=user_id,
        version=next_version,
        original_prompt=original_prompt,
        prompt_text=prompt_text,
        operative=True
    )
    db.add(db_prompt_version)
    _commit_and_refresh(db, db_prompt_version)
    return db_prompt_version

def update_prompt_version(db: Session, prompt_version_id: int, user_id: int, prompt_text: str):
    db_prompt_version = db.query(PromptVersion).filter(PromptVersion.prompt_version_id == prompt_version_id).first()
    if db_prompt_version:
        db.query(PromptVersion).filter(PromptVersion.prompt_id == db_prompt_version.prompt_id, PromptVersion.operative == True).update({PromptVersion.operative: False})
        latest_version = db.query(PromptVersion).filter(PromptVersion.prompt_id == db_prompt_version.prompt_id).order_by(PromptVersion.version.desc()).first()
        next_version = latest_version.version + 1 if latest_version else 1
        new_prompt_version = PromptVersion(
            prompt_id=db_prompt_version.prompt_id,
            user_id=user_id,
            version=next_version,
            original_prompt=db_prompt_version.original_prompt,
            prompt_text=prompt_text,
            operative=True
        )
        db.add(new_prompt_version)
        _commit_and_refresh(db, new_prompt_version)
        return new_prompt_version
    return None

def get_prompt_version(db: Session, prompt_version_id: int):
    return db.query(PromptVersion).filter(PromptVersion.prompt_version_id == prompt_version_id).first()

def get_prompt_versions_by_prompt_id(db: Session, prompt_id: int, skip: int = 0, limit: int = 100):
    return db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).offset(skip).limit(limit).all()

def get_operative_prompts(db: Session):
    return db.query(PromptVersion).filter(PromptVersion.operative == True).all()

def delete_prompt_version(db: Session, prompt_version_id: int):
    db_prompt_version = db.query(PromptVersion).filter(PromptVersion.prompt_version_id == prompt_version_id).first()
    if db_prompt_version:
        db.delete(db_prompt_version)
        db.commit()
        return True
    return False