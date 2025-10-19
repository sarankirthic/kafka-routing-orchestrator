from sqlalchemy.orm import scoped_session, sessionmaker
from flask import current_app
from ..extensions import db


class DatabaseSessionAdapter:
    """Provides request-scoped SQLAlchemy session helpers."""

    def __init__(self):
        self.SessionLocal = None

    def init_app(self, app=None):
        """Configure a scoped session for use outside Flask context if needed."""
        engine = db.engine
        self.SessionLocal = scoped_session(
            sessionmaker(bind=engine, autocommit=False, autoflush=False)
        )
        return self

    def get_session(self):
        if not self.SessionLocal:
            raise RuntimeError("DatabaseSessionAdapter not initialized.")
        return self.SessionLocal()

    @classmethod
    def from_current_app(cls):
        """Get scoped database session within Flask app context."""
        adapter = cls()
        adapter.init_app(current_app)
        return adapter
