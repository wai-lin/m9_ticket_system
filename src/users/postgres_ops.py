from sqlmodel import Session, text
from src.models.main import User
from src.database import engine, DB_SCHEMA


# --- Operation: Create a User ---
def create_user(name: str, email: str, password: str):
    """Create a new user in the database."""
    with Session(engine) as session:
        new_user = User(name=name, email=email, password=password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user


# --- Operation: Truncate User Table ---
def truncate_users():
    """Truncate user table and reset ID sequence to 1"""
    with Session(engine) as session:
        # Use raw SQL to truncate and reset sequence with schema prefix
        session.exec(
            text(f'TRUNCATE TABLE {DB_SCHEMA}."user" RESTART IDENTITY CASCADE'))
        session.commit()
        print("User table truncated and ID sequence reset to 1")
