from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import DB_URL, MAX_CONN
from .core import logger
from .models import Base

_SessionLocal = None


def _get_engine():
    """Get the SQLAlchemy engine."""
    logger.info(
        f"Creating database engine with URL: {DB_URL} and max connections: {MAX_CONN}"
    )
    return create_engine(
        DB_URL,
        echo=True,
        pool_size=MAX_CONN,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=1800,
    )


def _get_session_factory(engine=None):
    """Get the SQLAlchemy session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _initialize_db():
    """Initialize the database connection."""
    engine = _get_engine()
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database connection: {e}")
        raise


@contextmanager
def get_db() -> Generator[Session, None, None]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = _get_session_factory(_get_engine())
        _initialize_db()

    session = _SessionLocal()
    try:
        yield session
        session.commit()  # commit by default
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
