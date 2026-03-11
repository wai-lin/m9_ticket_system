"""Database connection and setup"""
from sqlmodel import create_engine, Session, SQLModel
from src.env import DATABASE_URL, DB_SCHEMA
from src.models import *  # noqa: F401, F403


# Set schema on SQLModel metadata (all tables will use this schema)
SQLModel.metadata.schema = DB_SCHEMA

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20,
)


def create_db_tables():
    """Create necessary tables in Postgres"""
    SQLModel.metadata.create_all(engine)


def init_db():
    """Initialize the database schema"""
    create_db_tables()


if __name__ == "__main__":
    init_db()

