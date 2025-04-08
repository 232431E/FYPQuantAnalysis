import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()  # Load environment variables from .env file

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

#Database connection URL
DATABASE_URL = f"mysql+mysqlclient://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD Operations
class CRUDBase:
    def __init__(self, model):
        self.model = model
    
    def get(self, db, id):
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db, skip=0, limit=100):
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db, obj_in):
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def update(self, db, db_obj, obj_in):
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db, id):
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

# You can add helper functions here for basic database operations (CRUD)
# as outlined in the previous detailed response for Task 1.5.