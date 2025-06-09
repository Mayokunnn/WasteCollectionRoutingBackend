from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres.wfpqjovuietnphgthojn:mac2024@aws-0-eu-north-1.pooler.supabase.com:5432/postgres"

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (if they don't already exist)
Base.metadata.create_all(bind=engine)
