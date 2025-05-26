from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DB_USER = os.getenv("DB_USER", "unfbrbzgfgscg")
DB_PASSWORD = os.getenv("DB_PASSWORD", "meut1tbd0twk")
DB_HOST = os.getenv("DB_HOST", "gfram1000.siteground.biz")
DB_NAME = os.getenv("DB_NAME", "dblbufwzxkgog9")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create engine with connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 