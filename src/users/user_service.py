from sqlmodel import Session, text
from src.database import engine
from src.models import User
from src.env import DB_SCHEMA


class UserService:
    """User operations (data access layer)"""

    @staticmethod
    def create_user(name: str, email: str, password: str = "default_password") -> User:
        """Create a new user"""
        with Session(engine) as session:
            user = User(name=name, email=email, password=password)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @staticmethod
    def truncate_users() -> None:
        """Truncate user table and reset ID sequence"""
        with Session(engine) as session:
            session.exec(
                text(f'TRUNCATE TABLE {DB_SCHEMA}."user" RESTART IDENTITY CASCADE'))
            session.commit()

