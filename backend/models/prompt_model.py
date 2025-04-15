# backend/models/prompt_model.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base  # Import Base


class Prompt(Base):
    __tablename__ = 'prompts'
    prompt_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  # Foreign Key to users table
    prompt_text = Column(Text, nullable=False)
    response_text = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    #  Import User within the class
    from .user_model import User
    user = relationship("User", back_populates="prompts")


def prompt_model_init():
    """Initialize the relationship for the Prompt model."""
    from .user_model import User  # Import User here to avoid circularity
    Prompt.user = relationship("User", back_populates="prompts")

