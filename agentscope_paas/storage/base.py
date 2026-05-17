"""
Abstract storage interface for authentication system
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from agentscope_paas.storage.models import User, ApiKey, Session


class IStorage(ABC):
    """
    Abstract storage interface for authentication data
    Implementations: MemoryStorage, SQLiteStorage, PostgreSQLStorage
    """

    @abstractmethod
    async def save_user(self, user: User) -> bool:
        """
        Save a new user to storage

        Args:
            user: User object to save

        Returns:
            True if saved successfully, False if user_id already exists
        """
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Retrieve user by ID

        Args:
            user_id: Unique user identifier

        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve user by email

        Args:
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_user(self, user_id: str, updates: dict) -> bool:
        """
        Update user information

        Args:
            user_id: User to update
            updates: Dictionary of fields to update

        Returns:
            True if updated successfully, False if user not found
        """
        pass

    @abstractmethod
    async def save_api_key(self, api_key: ApiKey) -> bool:
        """
        Save a new API key

        Args:
            api_key: ApiKey object to save

        Returns:
            True if saved successfully, False if key_id already exists
        """
        pass

    @abstractmethod
    async def get_api_key(self, key_id: str) -> Optional[ApiKey]:
        """
        Retrieve API key by ID

        Args:
            key_id: API key identifier

        Returns:
            ApiKey object if found, None otherwise
        """
        pass

    @abstractmethod
    async def validate_api_key(self, api_key: str) -> Optional[User]:
        """
        Validate API key and return associated user

        Args:
            api_key: Plain API key string to validate

        Returns:
            User object if key is valid and active, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_api_keys(self, user_id: str) -> List[ApiKey]:
        """
        Get all API keys for a user

        Args:
            user_id: User identifier

        Returns:
            List of ApiKey objects
        """
        pass

    @abstractmethod
    async def delete_api_key(self, key_id: str) -> bool:
        """
        Delete an API key

        Args:
            key_id: API key to delete

        Returns:
            True if deleted successfully, False if not found
        """
        pass

    @abstractmethod
    async def update_api_key_last_used(self, key_id: str) -> bool:
        """
        Update the last_used timestamp for an API key

        Args:
            key_id: API key to update

        Returns:
            True if updated successfully, False if not found
        """
        pass