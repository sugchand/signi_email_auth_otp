from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import DB_URL, MAX_CONN
from .core import logger


def get_engine():
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


def get_session_factory(engine=None):
    """Get the SQLAlchemy session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


SessionLocal = get_session_factory(engine=get_engine())


@contextmanager
def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()  # commit by default
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
