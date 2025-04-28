# backend/models/prompt_model.py
from backend.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class PromptVersion(Base):
    __tablename__ = 'prompt_versions'

    prompt_version_id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    version = Column(Integer, nullable=False)
    operative = Column(Boolean, default=True)
    original_prompt = Column(Text, nullable=False)
    prompt_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    # You might want to add a ForeignKey relationship to the users table if you have a User model
    user = relationship("User", back_populates="prompt_versions")
   
def prompt_model_init():
    pass