from src.users.user_repository import UserRepository


class UserService:
    """Business logic for User operations"""

    def __init__(self):
        self.repository = UserRepository()

    def create_user(self, name: str, email: str, password: str):
        """Create a new user"""
        return self.repository.create(name, email, password)

    def truncate_users(self):
        """Truncate all users"""
        return self.repository.truncate()


# Singleton instance for convenience
_user_service = UserService()


def create_user(name: str, email: str, password: str):
    """Create a new user - convenience function"""
    return _user_service.create_user(name, email, password)


def truncate_users():
    """Truncate users - convenience function"""
    return _user_service.truncate_users()
