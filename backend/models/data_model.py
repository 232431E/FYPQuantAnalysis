from sqlalchemy import TEXT, Column, Integer, String, DECIMAL, BIGINT, TIMESTAMP, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)
    ticker_symbol = Column(String(20), unique=True, nullable=False)
    exchange = Column(String(50))
    industry = Column(String(255))
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    financial_data = relationship("FinancialData", back_populates="company")
    news = relationship("News", back_populates="company")
    reports = relationship("Report", back_populates="company")
    alerts = relationship("Alert", back_populates="company")

class FinancialData(Base):
    __tablename__ = 'financial_data'

    data_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(DECIMAL(10, 2))
    high = Column(DECIMAL(10, 2))
    low = Column(DECIMAL(10, 2))
    close = Column(DECIMAL(10, 2))
    volume = Column(BIGINT)
    roi = Column(DECIMAL(10, 4))
    eps = Column(DECIMAL(10, 4))
    pe_ratio = Column(DECIMAL(10, 4))
    revenue = Column(DECIMAL(15, 2))
    debt_to_equity = Column(DECIMAL(10, 4))
    cash_flow = Column(DECIMAL(15, 2))
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="financial_data")

class News(Base):
    __tablename__ = 'news'

    news_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(TEXT)
    url = Column(String(255))
    published_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="news")