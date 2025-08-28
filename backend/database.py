# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB", "db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "db")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Tạo engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các model
Base = declarative_base()

# Dependency helper dùng với FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
