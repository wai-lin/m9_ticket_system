from sqlmodel import Session, text
from src.database import engine, DB_SCHEMA
from src.models.main import User


class UserRepository:
    """Data access layer for User operations"""

    @staticmethod
    def create(name: str, email: str, password: str) -> User:
        """Create a new user"""
        with Session(engine) as session:
            user = User(name=name, email=email, password=password)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @staticmethod
    def truncate() -> None:
        """Truncate user table and reset ID sequence"""
        with Session(engine) as session:
            session.exec(
                text(f'TRUNCATE TABLE {DB_SCHEMA}."user" RESTART IDENTITY CASCADE'))
            session.commit()

