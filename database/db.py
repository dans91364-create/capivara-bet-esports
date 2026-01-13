"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config.settings import DATABASE_URL
from database.models import Base
from utils.logger import log


# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables."""
    log.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    log.info("Database initialized successfully")


def drop_db():
    """Drop all tables - use with caution!"""
    log.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    log.warning("All tables dropped")


@contextmanager
def get_db() -> Session:
    """Get database session context manager.
    
    Usage:
        with get_db() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        log.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a new database session.
    
    Returns:
        SQLAlchemy Session
    """
    return SessionLocal()
