import logging

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.config.envs import DATABASE_URL

# Configure logging
logger = logging.getLogger(__name__)

# Use Supabase PostgreSQL database URL
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Create engine for PostgreSQL (no SQLite-specific args needed)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # PostgreSQL connection pool settings
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Set to True for SQL query logging in development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check function
def check_db_connection():
    """Check if database connection is healthy."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection is healthy")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
