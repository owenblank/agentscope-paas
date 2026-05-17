"""
In-memory storage implementation for development and testing
"""
from typing import Dict, Optional, List
from datetime import datetime
from agentscope_paas.storage.base import IStorage
from agentscope_paas.storage.models import User, ApiKey


class MemoryStorage(IStorage):
    """
    In-memory storage implementation using dictionaries
    Not persistent - data is lost on restart
    """

    def __init__(self):
        """Initialize in-memory storage"""
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}
        self._api_keys: Dict[str, ApiKey] = {}
        self._api_key_hash_index: Dict[str, ApiKey] = {}

    async def save_user(self, user: User) -> bool:
        """Save user to memory"""
        # Check if user ID already exists
        if user.user_id in self._users:
            return False

        self._users[user.user_id] = user
        self._users_by_email[user.email] = user
        return True

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self._users_by_email.get(email)

    async def update_user(self, user_id: str, updates: dict) -> bool:
        """Update user in memory"""
        user = self._users.get(user_id)
        if not user:
            return False

        # Remove old email from index if email is being updated
        if 'email' in updates and user.email != updates['email']:
            old_email = user.email
            if old_email in self._users_by_email and self._users_by_email[old_email].user_id == user_id:
                del self._users_by_email[old_email]

        # Update user object
        user_data = user.model_dump()
        user_data.update(updates)
        user_data['updated_at'] = datetime.now()

        updated_user = User(**user_data)

        # Update all indices
        self._users[user_id] = updated_user
        self._users_by_email[updated_user.email] = updated_user

        return True

    async def save_api_key(self, api_key: ApiKey) -> bool:
        """Save API key to memory"""
        if api_key.key_id in self._api_keys:
            return False

        self._api_keys[api_key.key_id] = api_key
        self._api_key_hash_index[api_key.key_hash] = api_key
        return True

    async def get_api_key(self, key_id: str) -> Optional[ApiKey]:
        """Get API key by ID"""
        return self._api_keys.get(key_id)

    async def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate API key and return user"""
        import hashlib

        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Look up the key
        stored_key = self._api_key_hash_index.get(key_hash)
        if not stored_key or not stored_key.is_active:
            return None

        # Check expiration
        if stored_key.expires_at and stored_key.expires_at < datetime.now():
            return None

        # Return associated user
        return await self.get_user(stored_key.user_id)

    async def get_user_api_keys(self, user_id: str) -> List[ApiKey]:
        """Get all API keys for user"""
        return [
            key for key in self._api_keys.values()
            if key.user_id == user_id
        ]

    async def delete_api_key(self, key_id: str) -> bool:
        """Delete API key from memory"""
        api_key = self._api_keys.get(key_id)
        if not api_key:
            return False

        # Remove from both indices
        del self._api_keys[key_id]
        del self._api_key_hash_index[api_key.key_hash]

        return True

    async def update_api_key_last_used(self, key_id: str) -> bool:
        """Update last used timestamp"""
        api_key = self._api_keys.get(key_id)
        if not api_key:
            return False

        api_key.last_used = datetime.now()
        return True
