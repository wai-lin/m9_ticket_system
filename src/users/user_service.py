from src.users.user_repository import UserRepository
from src.models import User


class UserService:
    """Business logic for user operations"""

    @staticmethod
    def create_user(name: str, email: str, password: str = "default_password") -> User:
        """Create a new user"""
        return UserRepository.create(name, email, password)

    @staticmethod
    def truncate_users() -> None:
        """Truncate all users"""
        UserRepository.truncate()
