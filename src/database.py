import os
from sqlmodel import create_engine, Session, SQLModel

# PostgreSQL connection: postgres user with empty password
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres@localhost/ticket_system"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Useful for debugging SQL queries
    future=True,  # Ensures SQLAlchemy 2.0 compatibility
    pool_size=10,  # Keeps 10 connections ready
    max_overflow=20,  # Allows up to 20 extra connections during spikes
)


def create_db_tables():
    """Requirement 1 & 2: Create necessary tables in Postgres"""
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
