import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection - construct from individual variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "ticket_system")
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Set schema on SQLModel metadata (all tables will use this schema)
SQLModel.metadata.schema = DB_SCHEMA

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Useful for debugging SQL queries
    future=True,  # Ensures SQLAlchemy 2.0 compatibility
    pool_size=10,  # Keeps 10 connections ready
    max_overflow=20,  # Allows up to 20 extra connections during spikes
    isolation_level="READ COMMITTED",
)


def create_db_tables():
    """Create necessary tables in Postgres"""
    # Note: Ensure the database 'flight_db' exists before running this.
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session for business operations"""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize the database schema"""
    create_db_tables()


if __name__ == "__main__":
    init_db()
