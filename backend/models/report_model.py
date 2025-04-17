# backend/models/report_model.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from backend.database import Base  # Import Base


class Report(Base):
    __tablename__ = 'reports'
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  # Add user_id
    report_date = Column(DateTime)
    content = Column(String(1000))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="reports")
    user = relationship("User", back_populates="reports")
    feedbacks = relationship("Feedback", back_populates="report")


def report_model_init():
    pass