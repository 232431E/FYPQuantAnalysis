# backend/models/data_model.py
from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from backend.database import Base  # Import Base

class Company(Base):
    __tablename__ = 'companies'
    company_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)
    ticker_symbol = Column(String(20), unique=True, nullable=False)
    exchange = Column(String(50))
    industry = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    financial_data = relationship("FinancialData", back_populates="company")
    reports = relationship("Report", back_populates="company")
    alerts = relationship("Alert", back_populates="company")
    news_items = relationship("News", back_populates="company")


class FinancialData(Base):
    __tablename__ = 'financial_data'
    data_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    volume = Column(BigInteger)
    roi = Column(Numeric(10, 4))
    eps = Column(Numeric(10, 4))
    pe_ratio = Column(Numeric(10, 4))
    revenue = Column(Numeric(15, 2))
    debt_to_equity = Column(Numeric(10, 4))
    cash_flow = Column(Numeric(15, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="financial_data")


class News(Base):
    __tablename__ = 'news'
    news_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    title = Column(String(255))
    link = Column(String(500))
    published_date = Column(DateTime)
    summary = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="news_items")

def data_model_init():
    pass