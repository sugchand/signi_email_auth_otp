from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DB_URL, MAX_CONN

engine = create_engine(DB_URL, pool_size=MAX_CONN, max_overflow=MAX_CONN+5)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()  # commit by default
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
