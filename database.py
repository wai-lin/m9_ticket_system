import os
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, Session, SQLModel

# Database URL from environment or default SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Create engine with appropriate pool settings
# For SQLite, use StaticPool and check_same_thread=False
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    **engine_kwargs,
)


def create_db_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize the database"""
    create_db_tables()
