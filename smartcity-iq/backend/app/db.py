"""Engine and scoped session shared by the Flask app, CLI scripts and pipelines."""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(autoflush=False, expire_on_commit=False))
_engine = None


def init_db(database_url: str, **engine_kwargs):
    global _engine
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    if _engine is not None:
        _engine.dispose()
    _engine = create_engine(database_url, pool_pre_ping=True, **engine_kwargs)
    Session.remove()
    Session.configure(bind=_engine)
    return _engine


def get_engine():
    if _engine is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    return _engine
