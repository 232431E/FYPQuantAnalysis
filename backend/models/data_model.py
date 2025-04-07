from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    company_id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    # Add other company-related columns

    financial_data = relationship("FinancialData", back_populates="company")

class FinancialData(Base):
    __tablename__ = 'financial_data'

    financial_data_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    date = Column(String(10), nullable=False) # Or use Date type if preferred
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    # Add other financial data columns

    company = relationship("Company", back_populates="financial_data")

# Example of how to create an engine (replace with your actual database URL)
# engine = create_engine('mysql+mysqlclient://user:password@host/database_name')
# Base.metadata.create_all(engine)