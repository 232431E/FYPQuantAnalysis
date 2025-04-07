from sqlalchemy import Column, Integer, String, TEXT, BOOLEAN, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prompt(Base):
    __tablename__ = 'prompts'

    prompt_id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_name = Column(String(255), nullable=False)
    prompt_text = Column(TEXT, nullable=False)
    version = Column(Integer, nullable=False)
    operative = Column(BOOLEAN, default=True)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
