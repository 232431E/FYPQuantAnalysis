from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from backend.database import Base

class Alert(Base):
       __tablename__ = 'alerts'
       alert_id = Column(Integer, primary_key=True, autoincrement=True)
       company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
       alert_type = Column(String(50))
       message = Column(String(255))
       triggered_at = Column(DateTime, default=func.now())
       created_at = Column(DateTime, default=func.now())
       updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

       company = relationship("Company", back_populates="alerts")