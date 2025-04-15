# backend/models/feedback_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func   
from backend.database import Base

class Feedback(Base):
       __tablename__ = 'feedback'
       feedback_id = Column(Integer, primary_key=True, autoincrement=True)
       report_id = Column(Integer, ForeignKey('reports.report_id'), nullable=False)
       user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
       feedback_text = Column(Text, nullable=False)
       created_at = Column(DateTime, default=func.now())
       updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

       #  relationship with Report and User
       report = relationship("Report", back_populates="feedbacks")
       user = relationship("User", back_populates="feedbacks")