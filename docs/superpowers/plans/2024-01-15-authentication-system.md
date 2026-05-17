# Authentication System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-step. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete authentication system for AgentScope PaaS with API key-based authentication, user registration/login, and frontend integration.

**Architecture:** Layered architecture with storage abstraction layer, authentication middleware, FastAPI backend routes, and React frontend with Zustand state management.

**Tech Stack:** FastAPI, Python 3.11+, React, TypeScript, Zustand, Pydantic, hashlib, secrets

---

## File Structure Overview

```
agentscope_paas/
├── storage/
│   ├── __init__.py           # Package initialization
│   ├── base.py               # IStorage abstract interface
│   ├── memory.py             # MemoryStorage implementation
│   └── models.py             # User, ApiKey, Session models
├── auth/
│   ├── __init__.py           # Package initialization
│   ├── security.py           # Password hashing, API key generation
│   └── middleware.py         # Authentication middleware
└── utils/
    └── exceptions.py         # Custom exceptions (modify)

api_server/
├── routers/
│   ├── __init__.py           # Router package initialization
│   └── auth.py               # Authentication routes
└── main.py                   # Main application (modify)

tests/
├── test_storage.py           # Storage layer tests
├── test_security.py          # Security utilities tests
└── test_auth_api.py          # Authentication API tests

frontend/src/
├── services/
│   ├── auth.service.ts       # Authentication API service
│   └── api.ts                # API client with auth interceptor (modify)
├── store/
│   └── auth.store.ts         # Authentication state management
├── types/
│   └── auth.ts               # Authentication type definitions
├── pages/
│   └── Auth/
│       ├── Login.tsx         # Login page
│       ├── Register.tsx      # Register page
│       └── index.ts          # Export file
├── components/
│   └── Auth/
│       ├── ProtectedRoute.tsx # Route protection component
│       └── index.ts          # Export file
└── App.tsx                   # Main app component (modify)
```

---

## Task 1: Create Storage Models

**Files:**
- Create: `agentscope_paas/storage/__init__.py`
- Create: `agentscope_paas/storage/models.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Create storage package initialization**

```python
# agentscope_paas/storage/__init__.py
"""
Storage package for AgentScope PaaS
Provides abstract storage interface and implementations
"""

from agentscope_paas.storage.base import IStorage
from agentscope_paas.storage.models import User, ApiKey, Session

__all__ = ['IStorage', 'User', 'ApiKey', 'Session']
```

- [ ] **Step 2: Create storage models**

```python
# agentscope_paas/storage/models.py
"""
Data models for authentication system
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    """User model"""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email")
    password_hash: str = Field(..., description="Hashed password")
    role: str = Field(default="user", description="User role: user or admin")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Account active status")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_1234567890",
                "username": "johndoe",
                "email": "john@example.com",
                "password_hash": "salt$hash",
                "role": "user",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "is_active": True
            }
        }


class ApiKey(BaseModel):
    """API Key model"""
    key_id: str = Field(..., description="Unique key identifier")
    user_id: str = Field(..., description="Owner user ID")
    api_key: str = Field(..., description="Plain API key for display")
    key_hash: str = Field(..., description="Hashed API key for validation")
    name: str = Field(..., description="Key name (e.g., 'Development Key')")
    scopes: List[str] = Field(default=["read"], description="Permission scopes")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    is_active: bool = Field(default=True, description="Key active status")

    class Config:
        json_schema_extra = {
            "example": {
                "key_id": "key_1234567890",
                "user_id": "user_1234567890",
                "api_key": "as_live_johndoe_abc123...",
                "key_hash": "hash_value",
                "name": "Development Key",
                "scopes": ["read", "write"],
                "last_used": "2024-01-15T12:00:00Z",
                "expires_at": None,
                "created_at": "2024-01-15T10:30:00Z",
                "is_active": True
            }
        }


class Session(BaseModel):
    """Session model for future JWT support"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="Owner user ID")
    token_hash: str = Field(..., description="Hashed session token")
    expires_at: datetime = Field(..., description="Session expiration")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_1234567890",
                "user_id": "user_1234567890",
                "token_hash": "token_hash_value",
                "expires_at": "2024-01-16T10:30:00Z",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
```

- [ ] **Step 3: Write failing tests for models**

```python
# tests/test_storage.py
import pytest
from datetime import datetime
from agentscope_paas.storage.models import User, ApiKey, Session


def test_user_creation_valid():
    """Test creating a valid user"""
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash"
    )
    assert user.user_id == "user_001"
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "user"
    assert user.is_active is True


def test_user_creation_invalid_email():
    """Test user creation fails with invalid email"""
    with pytest.raises(Exception):
        User(
            user_id="user_001",
            username="testuser",
            email="invalid-email",
            password_hash="salt$hash"
        )


def test_user_creation_invalid_username():
    """Test user creation fails with username too short"""
    with pytest.raises(Exception):
        User(
            user_id="user_001",
            username="ab",
            email="test@example.com",
            password_hash="salt$hash"
        )


def test_api_key_creation_valid():
    """Test creating a valid API key"""
    api_key = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key="as_live_testuser_abc123",
        key_hash="hash_value",
        name="Test Key"
    )
    assert api_key.key_id == "key_001"
    assert api_key.user_id == "user_001"
    assert api_key.scopes == ["read"]
    assert api_key.is_active is True


def test_session_creation_valid():
    """Test creating a valid session"""
    expires_at = datetime(2024, 1, 16, 10, 30, 0)
    session = Session(
        session_id="sess_001",
        user_id="user_001",
        token_hash="token_hash",
        expires_at=expires_at
    )
    assert session.session_id == "sess_001"
    assert session.expires_at == expires_at
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /d/workspace/agentscope-paas
pytest tests/test_storage.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add agentscope_paas/storage/
git commit -m "feat: add storage models with validation"
```

---

## Task 2: Create Storage Abstract Interface

**Files:**
- Create: `agentscope_paas/storage/base.py`
- Test: `tests/test_storage.py` (extend)

- [ ] **Step 1: Create abstract storage interface**

```python
# agentscope_paas/storage/base.py
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
```

- [ ] **Step 2: Add test for interface implementation**

```python
# tests/test_storage.py (add to existing file)

def test_storage_interface_is_abstract():
    """Test that IStorage cannot be instantiated directly"""
    from agentscope_paas.storage.base import IStorage

    with pytest.raises(TypeError):
        IStorage()
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_storage.py::test_storage_interface_is_abstract -v
```

Expected: PASS (IStorage is abstract and cannot be instantiated)

- [ ] **Step 4: Commit**

```bash
git add agentscope_paas/storage/base.py tests/test_storage.py
git commit -m "feat: add abstract storage interface"
```

---

## Task 3: Implement Memory Storage

**Files:**
- Create: `agentscope_paas/storage/memory.py`
- Test: `tests/test_storage.py` (extend)

- [ ] **Step 1: Implement memory storage**

```python
# agentscope_paas/storage/memory.py
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
```

- [ ] **Step 2: Add comprehensive tests for memory storage**

```python
# tests/test_storage.py (add to existing file)

import pytest
from agentscope_paas.storage.memory import MemoryStorage
from agentscope_paas.storage.models import User, ApiKey


@pytest.mark.asyncio
async def test_memory_storage_save_user():
    """Test saving user to memory storage"""
    storage = MemoryStorage()
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash"
    )

    result = await storage.save_user(user)
    assert result is True

    retrieved = await storage.get_user("user_001")
    assert retrieved.user_id == "user_001"
    assert retrieved.username == "testuser"


@pytest.mark.asyncio
async def test_memory_storage_duplicate_user():
    """Test saving duplicate user fails"""
    storage = MemoryStorage()
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash"
    )

    await storage.save_user(user)
    result = await storage.save_user(user)
    assert result is False


@pytest.mark.asyncio
async def test_memory_storage_get_user_by_email():
    """Test retrieving user by email"""
    storage = MemoryStorage()
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash"
    )

    await storage.save_user(user)
    retrieved = await storage.get_user_by_email("test@example.com")
    assert retrieved is not None
    assert retrieved.user_id == "user_001"


@pytest.mark.asyncio
async def test_memory_storage_update_user():
    """Test updating user"""
    storage = MemoryStorage()
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash"
    )

    await storage.save_user(user)
    result = await storage.update_user("user_001", {"username": "updateduser"})
    assert result is True

    updated = await storage.get_user("user_001")
    assert updated.username == "updateduser"


@pytest.mark.asyncio
async def test_memory_storage_save_api_key():
    """Test saving API key"""
    storage = MemoryStorage()
    api_key = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key="as_live_testuser_abc123",
        key_hash="hash_value",
        name="Test Key"
    )

    result = await storage.save_api_key(api_key)
    assert result is True

    retrieved = await storage.get_api_key("key_001")
    assert retrieved.key_id == "key_001"


@pytest.mark.asyncio
async def test_memory_storage_validate_api_key():
    """Test validating API key"""
    import hashlib

    storage = MemoryStorage()

    # Create API key
    plain_key = "as_live_testuser_abc123"
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()

    api_key = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key=plain_key,
        key_hash=key_hash,
        name="Test Key"
    )

    # Create user
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash"
    )

    await storage.save_user(user)
    await storage.save_api_key(api_key)

    # Validate correct key
    result = await storage.validate_api_key(plain_key)
    assert result is not None
    assert result.user_id == "user_001"

    # Validate incorrect key
    result = await storage.validate_api_key("wrong_key")
    assert result is None


@pytest.mark.asyncio
async def test_memory_storage_get_user_api_keys():
    """Test getting all user API keys"""
    storage = MemoryStorage()

    # Create user
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash"
    )
    await storage.save_user(user)

    # Create multiple API keys
    key1 = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key="key1",
        key_hash="hash1",
        name="Key 1"
    )
    key2 = ApiKey(
        key_id="key_002",
        user_id="user_002",  # Different user
        api_key="key2",
        key_hash="hash2",
        name="Key 2"
    )

    await storage.save_api_key(key1)
    await storage.save_api_key(key2)

    # Get keys for user_001
    keys = await storage.get_user_api_keys("user_001")
    assert len(keys) == 1
    assert keys[0].key_id == "key_001"


@pytest.mark.asyncio
async def test_memory_storage_delete_api_key():
    """Test deleting API key"""
    storage = MemoryStorage()

    api_key = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key="as_live_testuser_abc123",
        key_hash="hash_value",
        name="Test Key"
    )

    await storage.save_api_key(api_key)
    result = await storage.delete_api_key("key_001")
    assert result is True

    retrieved = await storage.get_api_key("key_001")
    assert retrieved is None


@pytest.mark.asyncio
async def test_memory_storage_update_api_key_last_used():
    """Test updating API key last used timestamp"""
    import time
    from datetime import datetime

    storage = MemoryStorage()

    api_key = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key="as_live_testuser_abc123",
        key_hash="hash_value",
        name="Test Key",
        last_used=None
    )

    await storage.save_api_key(api_key)
    time.sleep(0.1)  # Small delay

    result = await storage.update_api_key_last_used("key_001")
    assert result is True

    updated = await storage.get_api_key("key_001")
    assert updated.last_used is not None
    assert isinstance(updated.last_used, datetime)
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
pytest tests/test_storage.py -v
```

Expected: All tests PASS

- [ ] **Step 3: Update storage package exports**

```python
# agentscope_paas/storage/__init__.py (update)
"""
Storage package for AgentScope PaaS
Provides abstract storage interface and implementations
"""

from agentscope_paas.storage.base import IStorage
from agentscope_paas.storage.memory import MemoryStorage
from agentscope_paas.storage.models import User, ApiKey, Session

__all__ = ['IStorage', 'MemoryStorage', 'User', 'ApiKey', 'Session']
```

- [ ] **Step 4: Commit**

```bash
git add agentscope_paas/storage/ tests/test_storage.py
git commit -m "feat: implement memory storage with comprehensive tests"
```

---

## Task 4: Create Security Utilities

**Files:**
- Create: `agentscope_paas/auth/__init__.py`
- Create: `agentscope_paas/auth/security.py`
- Test: `tests/test_security.py`

- [ ] **Step 1: Create auth package initialization**

```python
# agentscope_paas/auth/__init__.py
"""
Authentication package for AgentScope PaaS
Provides security utilities and middleware
"""

from agentscope_paas.auth.security import hash_password, verify_password, generate_api_key

__all__ = ['hash_password', 'verify_password', 'generate_api_key']
```

- [ ] **Step 2: Create security utilities**

```python
# agentscope_paas/auth/security.py
"""
Security utilities for authentication system
Password hashing, API key generation, validation
"""
import hashlib
import secrets
import string


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256

    Args:
        password: Plain text password

    Returns:
        Hashed password in format "salt$hash"
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # PBKDF2 iterations
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash

    Args:
        password: Plain text password to verify
        password_hash: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        salt, hash_value = password_hash.split('$')
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return computed_hash == hash_value
    except (ValueError, AttributeError):
        return False


def generate_api_key(username: str) -> tuple[str, str]:
    """
    Generate a secure API key

    Args:
        username: Username for key identification

    Returns:
        Tuple of (plain_api_key, key_hash)
        Format: "as_live_{username}_{random_string}"
    """
    # Generate 32 random bytes using secrets for cryptographic security
    random_bytes = secrets.token_bytes(32)
    random_part = secrets.token_urlsafe(32)

    # Create API key with format
    api_key = f"as_live_{username}_{random_part}"

    # Create hash for storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    return api_key, key_hash


def generate_user_id() -> str:
    """
    Generate a unique user ID

    Returns:
        Unique user identifier
    """
    return f"user_{secrets.token_hex(8)}"


def generate_key_id() -> str:
    """
    Generate a unique API key ID

    Returns:
        Unique key identifier
    """
    return f"key_{secrets.token_hex(8)}"
```

- [ ] **Step 3: Write comprehensive tests for security utilities**

```python
# tests/test_security.py
import pytest
from agentscope_paas.auth.security import (
    hash_password,
    verify_password,
    generate_api_key,
    generate_user_id,
    generate_key_id
)


def test_hash_password_basic():
    """Test basic password hashing"""
    password = "MySecurePassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert '$' in hashed
    assert len(hashed) > 32


def test_hash_password_different_salts():
    """Test that same password produces different hashes"""
    password = "SamePassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2  # Different salts


def test_verify_password_correct():
    """Test verifying correct password"""
    password = "MySecurePassword123"
    hashed = hash_password(password)

    result = verify_password(password, hashed)
    assert result is True


def test_verify_password_incorrect():
    """Test verifying incorrect password"""
    password = "MySecurePassword123"
    wrong_password = "WrongPassword123"
    hashed = hash_password(password)

    result = verify_password(wrong_password, hashed)
    assert result is False


def test_verify_password_invalid_format():
    """Test verifying password with invalid hash format"""
    result = verify_password("password", "invalid_hash")
    assert result is False


def test_generate_api_key_format():
    """Test API key generation format"""
    api_key, key_hash = generate_api_key("testuser")

    assert api_key.startswith("as_live_testuser_")
    assert len(api_key) > 40
    assert len(key_hash) == 64  # SHA256 hex length
    assert key_hash != api_key


def test_generate_api_key_unique():
    """Test that API keys are unique"""
    key1, hash1 = generate_api_key("testuser")
    key2, hash2 = generate_api_key("testuser")

    assert key1 != key2
    assert hash1 != hash2


def test_generate_user_id():
    """Test user ID generation"""
    user_id = generate_user_id()

    assert user_id.startswith("user_")
    assert len(user_id) == 21  # "user_" + 16 hex chars


def test_generate_user_id_unique():
    """Test that user IDs are unique"""
    id1 = generate_user_id()
    id2 = generate_user_id()

    assert id1 != id2


def test_generate_key_id():
    """Test key ID generation"""
    key_id = generate_key_id()

    assert key_id.startswith("key_")
    assert len(key_id) == 20  # "key_" + 16 hex chars


def test_password_strength_common_passwords():
    """Test that common passwords can be hashed"""
    passwords = [
        "password123",
        "admin123",
        "letmein",
        "welcome2024"
    ]

    for password in passwords:
        hashed = hash_password(password)
        assert verify_password(password, hashed)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_security.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add agentscope_paas/auth/ tests/test_security.py
git commit -m "feat: add security utilities with comprehensive tests"
```

---

## Task 5: Create Authentication Middleware

**Files:**
- Create: `agentscope_paas/auth/middleware.py`
- Test: `tests/test_auth_middleware.py`

- [ ] **Step 1: Create authentication middleware**

```python
# agentscope_paas/auth/middleware.py
"""
Authentication middleware for FastAPI
"""
from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from agentscope_paas.storage.models import User
from agentscope_paas.storage.base import IStorage


# Global storage instance (will be set during app initialization)
_storage_instance: Optional[IStorage] = None


def set_storage(storage: IStorage):
    """Set the global storage instance"""
    global _storage_instance
    _storage_instance = storage


def get_storage() -> IStorage:
    """Get the global storage instance"""
    if _storage_instance is None:
        raise RuntimeError("Storage not initialized. Call set_storage() first.")
    return _storage_instance


# API Key header authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def api_key_auth(api_key: str = Security(api_key_header)) -> User:
    """
    Dependency for requiring API key authentication

    Usage:
        @app.get("/protected")
        async def protected_endpoint(current_user: User = Depends(api_key_auth)):
            return {"message": f"Hello, {current_user.username}"}

    Raises:
        HTTPException 401: If API key is missing or invalid
        HTTPException 403: If user account is disabled
    """
    storage = get_storage()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API密钥缺失，请在请求头中提供X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Validate API key and get user
    user = await storage.validate_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )

    # Update last used timestamp
    await storage.update_api_key_last_used(api_key)

    return user


async def optional_auth(api_key: str = Security(api_key_header)) -> Optional[User]:
    """
    Dependency for optional API key authentication
    Returns None if no API key provided or if key is invalid

    Usage:
        @app.get("/public")
        async def public_endpoint(current_user: Optional[User] = Depends(optional_auth)):
            if current_user:
                return {"message": f"Hello, {current_user.username}"}
            return {"message": "Hello, anonymous"}
    """
    storage = get_storage()

    if not api_key:
        return None

    user = await storage.validate_api_key(api_key)
    if user and user.is_active:
        await storage.update_api_key_last_used(api_key)
        return user

    return None


def require_role(*roles: str):
    """
    Dependency factory for requiring specific user roles

    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: str,
            current_user: User = Depends(require_role("admin"))
        ):
            # Only admin can access
            pass

    Args:
        *roles: Allowed roles

    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(api_key_auth)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(roles)}"
            )
        return current_user

    return role_checker
```

- [ ] **Step 2: Write tests for middleware**

```python
# tests/test_auth_middleware.py
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from agentscope_paas.auth.middleware import (
    api_key_auth,
    optional_auth,
    require_role,
    set_storage,
    get_storage
)
from agentscope_paas.storage.memory import MemoryStorage
from agentscope_paas.storage.models import User, ApiKey
from agentscope_paas.auth.security import generate_api_key
import hashlib


@pytest.fixture
def storage():
    """Create test storage with sample data"""
    storage = MemoryStorage()

    # Create test user
    user = User(
        user_id="user_001",
        username="testuser",
        email="test@example.com",
        password_hash="salt$hash",
        role="user"
    )
    storage.save_user(user)

    # Create admin user
    admin = User(
        user_id="admin_001",
        username="admin",
        email="admin@example.com",
        password_hash="salt$hash",
        role="admin"
    )
    storage.save_user(admin)

    # Create API key for user
    plain_key, key_hash = generate_api_key("testuser")
    api_key = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key=plain_key,
        key_hash=key_hash,
        name="Test Key"
    )
    storage.save_api_key(api_key)

    return storage, plain_key


@pytest.fixture
def test_app(storage):
    """Create test FastAPI app"""
    storage_instance, api_key = storage

    # Set storage for middleware
    set_storage(storage_instance)

    app = FastAPI()

    @app.get("/protected")
    async def protected_endpoint(current_user: User = Depends(api_key_auth)):
        return {"user": current_user.username}

    @app.get("/public")
    async def public_endpoint(current_user: User = Depends(optional_auth)):
        if current_user:
            return {"user": current_user.username, "authenticated": True}
        return {"authenticated": False}

    @app.get("/admin")
    async def admin_endpoint(current_user: User = Depends(require_role("admin"))):
        return {"user": current_user.username, "is_admin": True}

    return app, api_key


def test_protected_endpoint_with_valid_key(test_app):
    """Test protected endpoint with valid API key"""
    app, api_key = test_app
    client = TestClient(app)

    response = client.get("/protected", headers={"X-API-Key": api_key})

    assert response.status_code == 200
    assert response.json()["user"] == "testuser"


def test_protected_endpoint_without_key(test_app):
    """Test protected endpoint without API key"""
    app, api_key = test_app
    client = TestClient(app)

    response = client.get("/protected")

    assert response.status_code == 401
    assert "API密钥缺失" in response.json()["detail"]


def test_protected_endpoint_with_invalid_key(test_app):
    """Test protected endpoint with invalid API key"""
    app, api_key = test_app
    client = TestClient(app)

    response = client.get("/protected", headers={"X-API-Key": "invalid_key"})

    assert response.status_code == 401
    assert "无效的API密钥" in response.json()["detail"]


def test_public_endpoint_without_key(test_app):
    """Test public endpoint without authentication"""
    app, api_key = test_app
    client = TestClient(app)

    response = client.get("/public")

    assert response.status_code == 200
    assert response.json()["authenticated"] is False


def test_public_endpoint_with_key(test_app):
    """Test public endpoint with valid API key"""
    app, api_key = test_app
    client = TestClient(app)

    response = client.get("/public", headers={"X-API-Key": api_key})

    assert response.status_code == 200
    assert response.json()["authenticated"] is True
    assert response.json()["user"] == "testuser"


def test_admin_endpoint_with_admin_user(storage):
    """Test admin endpoint with admin user"""
    storage_instance, _ = storage
    set_storage(storage_instance)

    # Create admin API key
    admin_key, key_hash = generate_api_key("admin")
    api_key = ApiKey(
        key_id="key_admin",
        user_id="admin_001",
        api_key=admin_key,
        key_hash=key_hash,
        name="Admin Key"
    )
    storage_instance.save_api_key(api_key)

    app = FastAPI()

    @app.get("/admin")
    async def admin_endpoint(current_user: User = Depends(require_role("admin"))):
        return {"user": current_user.username}

    client = TestClient(app)
    response = client.get("/admin", headers={"X-API-Key": admin_key})

    assert response.status_code == 200
    assert response.json()["user"] == "admin"


def test_admin_endpoint_with_regular_user(test_app):
    """Test admin endpoint with regular user (should fail)"""
    app, api_key = test_app
    client = TestClient(app)

    # First add the admin endpoint
    @app.get("/admin_test")
    async def admin_endpoint(current_user: User = Depends(require_role("admin"))):
        return {"user": current_user.username}

    response = client.get("/admin_test", headers={"X-API-Key": api_key})

    assert response.status_code == 403
    assert "需要以下角色之一" in response.json()["detail"]


def test_get_storage_raises_when_not_initialized():
    """Test that get_storage raises error when not initialized"""
    # Reset storage
    import agentscope_paas.auth.middleware as middleware
    middleware._storage_instance = None

    with pytest.raises(RuntimeError, match="Storage not initialized"):
        get_storage()
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
pytest tests/test_auth_middleware.py -v
```

Expected: All tests PASS

- [ ] **Step 4: Update auth package exports**

```python
# agentscope_paas/auth/__init__.py (update)
"""
Authentication package for AgentScope PaaS
Provides security utilities and middleware
"""

from agentscope_paas.auth.security import (
    hash_password,
    verify_password,
    generate_api_key,
    generate_user_id,
    generate_key_id
)
from agentscope_paas.auth.middleware import (
    api_key_auth,
    optional_auth,
    require_role,
    set_storage,
    get_storage
)

__all__ = [
    'hash_password',
    'verify_password',
    'generate_api_key',
    'generate_user_id',
    'generate_key_id',
    'api_key_auth',
    'optional_auth',
    'require_role',
    'set_storage',
    'get_storage'
]
```

- [ ] **Step 5: Commit**

```bash
git add agentscope_paas/auth/ tests/test_auth_middleware.py
git commit -m "feat: add authentication middleware with role-based access"
```

---

## Task 6: Create Authentication API Routes

**Files:**
- Create: `api_server/routers/__init__.py`
- Create: `api_server/routers/auth.py`
- Modify: `api_server/main.py`
- Test: `tests/test_auth_api.py`

- [ ] **Step 1: Create routers package**

```python
# api_server/routers/__init__.py
"""
API routers package
"""

from api_server.routers.auth import router as auth_router

__all__ = ['auth_router']
```

- [ ] **Step 2: Create authentication request/response models**

```python
# api_server/routers/auth.py (part 1)
"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

from agentscope_paas.auth.middleware import get_storage
from agentscope_paas.auth.security import (
    hash_password,
    verify_password,
    generate_api_key,
    generate_user_id,
    generate_key_id
)
from agentscope_paas.storage.models import User, ApiKey
from agentscope_paas.storage.base import IStorage


# Request/Response Models
class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=100, description="密码")

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """User information response"""
    user_id: str
    username: str
    email: str
    role: str
    created_at: datetime
    is_active: bool


class AuthResponse(BaseModel):
    """Authentication response"""
    user: UserResponse
    api_key: str
    message: str


class CreateApiKeyRequest(BaseModel):
    """Create API key request"""
    name: str = Field(..., min_length=1, max_length=100, description="密钥名称")
    scopes: List[str] = Field(default=["read"], description="权限范围")


class ApiKeyResponse(BaseModel):
    """API key response"""
    key_id: str
    user_id: str
    name: str
    scopes: List[str]
    last_used: Optional[datetime]
    created_at: datetime
    is_active: bool


class CreateApiKeyResponse(BaseModel):
    """Create API key response"""
    api_key: ApiKeyResponse
    key: str  # Plain API key (only shown on creation)
```

- [ ] **Step 3: Create authentication routes**

```python
# api_server/routers/auth.py (part 2 - add to existing file)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    storage: IStorage = Depends(get_storage)
):
    """
    用户注册

    创建新用户账户并生成API密钥
    """
    # Check if email already exists
    existing_user = await storage.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # Check if username already exists
    existing_by_username = await storage.get_user(request.username)
    if existing_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # Create new user
    user_id = generate_user_id()
    password_hash = hash_password(request.password)

    user = User(
        user_id=user_id,
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        role="user"
    )

    # Save user
    if not await storage.save_user(user):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户创建失败"
        )

    # Generate API key
    api_key_plain, key_hash = generate_api_key(request.username)
    key_id = generate_key_id()

    api_key = ApiKey(
        key_id=key_id,
        user_id=user_id,
        api_key=api_key_plain,
        key_hash=key_hash,
        name="默认API密钥",
        scopes=["read", "write"]
    )

    await storage.save_api_key(api_key)

    # Return response
    return {
        "success": True,
        "data": {
            "user": UserResponse.model_validate(user.model_dump()),
            "api_key": api_key_plain,
            "message": "注册成功，请妥善保管您的API密钥"
        }
    }


@router.post("/login")
async def login(
    request: LoginRequest,
    storage: IStorage = Depends(get_storage)
):
    """
    用户登录

    验证用户凭据并返回API密钥
    """
    # Find user by email
    user = await storage.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # Get existing API keys or create new one
    api_keys = await storage.get_user_api_keys(user.user_id)
    if api_keys:
        api_key_obj = api_keys[0]  # Use first existing key
        api_key_plain = api_key_obj.api_key
    else:
        # Create new API key
        api_key_plain, key_hash = generate_api_key(user.username)
        key_id = generate_key_id()

        api_key_obj = ApiKey(
            key_id=key_id,
            user_id=user.user_id,
            api_key=api_key_plain,
            key_hash=key_hash,
            name="登录生成的API密钥",
            scopes=["read", "write"]
        )

        await storage.save_api_key(api_key_obj)

    return {
        "success": True,
        "data": {
            "user": UserResponse.model_validate(user.model_dump()),
            "api_key": api_key_plain,
            "message": "登录成功"
        }
    }


@router.get("/me")
async def get_current_user(
    storage: IStorage = Depends(get_storage),
    current_user: User = Depends(api_key_auth)
):
    """
    获取当前用户信息

    需要API密钥认证
    """
    return {
        "success": True,
        "data": {
            "user": UserResponse.model_validate(current_user.model_dump())
        }
    }


@router.get("/api-keys")
async def get_api_keys(
    storage: IStorage = Depends(get_storage),
    current_user: User = Depends(api_key_auth)
):
    """
    获取当前用户的所有API密钥

    需要API密钥认证
    """
    api_keys = await storage.get_user_api_keys(current_user.user_id)

    return {
        "success": True,
        "data": {
            "api_keys": [
                ApiKeyResponse.model_validate(key.model_dump())
                for key in api_keys
            ]
        }
    }


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateApiKeyRequest,
    storage: IStorage = Depends(get_storage),
    current_user: User = Depends(api_key_auth)
):
    """
    创建新的API密钥

    需要API密钥认证
    """
    # Generate new API key
    api_key_plain, key_hash = generate_api_key(current_user.username)
    key_id = generate_key_id()

    api_key = ApiKey(
        key_id=key_id,
        user_id=current_user.user_id,
        api_key=api_key_plain,
        key_hash=key_hash,
        name=request.name,
        scopes=request.scopes
    )

    await storage.save_api_key(api_key)

    return {
        "success": True,
        "data": {
            "api_key": ApiKeyResponse.model_validate(api_key.model_dump()),
            "key": api_key_plain,
            "message": "API密钥创建成功"
        }
    }


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    storage: IStorage = Depends(get_storage),
    current_user: User = Depends(api_key_auth)
):
    """
    删除指定的API密钥

    需要API密钥认证
    """
    # Get API key to verify ownership
    api_key = await storage.get_api_key(key_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API密钥不存在"
        )

    # Verify ownership
    if api_key.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此API密钥"
        )

    # Delete API key
    if not await storage.delete_api_key(key_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API密钥删除失败"
        )

    return {
        "success": True,
        "message": "API密钥删除成功"
    }
```

**Note**: Need to add import for `api_key_auth` at the top of the file.

- [ ] **Step 4: Update imports in auth routes**

```python
# api_server/routers/auth.py (update imports at top)
"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

from agentscope_paas.auth.middleware import get_storage, api_key_auth
from agentscope_paas.auth.security import (
    hash_password,
    verify_password,
    generate_api_key,
    generate_user_id,
    generate_key_id
)
from agentscope_paas.storage.models import User, ApiKey
from agentscope_paas.storage.base import IStorage
```

- [ ] **Step 5: Integrate auth routes into main app**

```python
# api_server/main.py (update existing file)

# Add these imports at the top
from agentscope_paas.auth.middleware import set_storage
from agentscope_paas.storage.memory import MemoryStorage
from api_server.routers import auth_router

# After creating the FastAPI app, add:
# Initialize authentication storage
storage = MemoryStorage()
set_storage(storage)

# Include authentication routes
app.include_router(auth_router)

# Protect existing agent endpoints with authentication
# Example update for agents endpoint:
@app.post("/api/v1/agents")
async def create_agent(
    request: CreateAgentRequest,
    current_user: User = Depends(api_key_auth)  # Add authentication
):
    # ... existing logic ...
    pass

# Similar updates for other protected endpoints
```

- [ ] **Step 6: Write comprehensive API tests**

```python
# tests/test_auth_api.py
import pytest
from fastapi.testclient import TestClient
from api_server.main import app
from agentscope_paas.auth.middleware import set_storage
from agentscope_paas.storage.memory import MemoryStorage


@pytest.fixture
def client():
    """Create test client with initialized storage"""
    storage = MemoryStorage()
    set_storage(storage)

    return TestClient(app)


def test_register_success(client):
    """Test successful user registration"""
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "api_key" in data["data"]
    assert data["data"]["user"]["username"] == "testuser"
    assert data["data"]["user"]["email"] == "test@example.com"
    assert data["data"]["user"]["role"] == "user"


def test_register_duplicate_email(client):
    """Test registration with duplicate email fails"""
    # First registration
    client.post("/api/v1/auth/register", json={
        "username": "user1",
        "email": "test@example.com",
        "password": "SecurePass123"
    })

    # Second registration with same email
    response = client.post("/api/v1/auth/register", json={
        "username": "user2",
        "email": "test@example.com",
        "password": "SecurePass456"
    })

    assert response.status_code == 400
    assert "邮箱已被注册" in response.json()["detail"]


def test_register_weak_password(client):
    """Test registration with weak password fails"""
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "weak"
    })

    assert response.status_code == 422  # Validation error


def test_login_success(client):
    """Test successful login"""
    # Register first
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    })

    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "api_key" in data["data"]
    assert data["data"]["user"]["email"] == "test@example.com"


def test_login_wrong_password(client):
    """Test login with wrong password fails"""
    # Register first
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    })

    # Login with wrong password
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword"
    })

    assert response.status_code == 401
    assert "邮箱或密码错误" in response.json()["detail"]


def test_get_current_user(client):
    """Test getting current user info"""
    # Register and get API key
    register_response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    api_key = register_response.json()["data"]["api_key"]

    # Get current user
    response = client.get("/api/v1/auth/me", headers={
        "X-API-Key": api_key
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["username"] == "testuser"


def test_get_current_user_without_auth(client):
    """Test getting current user without authentication fails"""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert "API密钥缺失" in response.json()["detail"]


def test_create_api_key(client):
    """Test creating new API key"""
    # Register and get API key
    register_response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    auth_key = register_response.json()["data"]["api_key"]

    # Create new API key
    response = client.post("/api/v1/auth/api-keys", headers={
        "X-API-Key": auth_key
    }, json={
        "name": "Test Key",
        "scopes": ["read", "write"]
    })

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "key" in data["data"]
    assert data["data"]["api_key"]["name"] == "Test Key"


def test_get_api_keys(client):
    """Test getting user's API keys"""
    # Register and get API key
    register_response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    auth_key = register_response.json()["data"]["api_key"]

    # Get API keys
    response = client.get("/api/v1/auth/api-keys", headers={
        "X-API-Key": auth_key
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["api_keys"]) >= 1


def test_delete_api_key(client):
    """Test deleting API key"""
    # Register and get API key
    register_response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    auth_key = register_response.json()["data"]["api_key"]

    # Create additional key
    create_response = client.post("/api/v1/auth/api-keys", headers={
        "X-API-Key": auth_key
    }, json={
        "name": "Key to Delete",
        "scopes": ["read"]
    })
    key_id = create_response.json()["data"]["api_key"]["key_id"]

    # Delete the key
    response = client.delete(f"/api/v1/auth/api-keys/{key_id}", headers={
        "X-API-Key": auth_key
    })

    assert response.status_code == 200
    assert response.json()["success"] is True
```

- [ ] **Step 7: Run API tests to verify functionality**

```bash
pytest tests/test_auth_api.py -v
```

Expected: All tests PASS

- [ ] **Step 8: Test the API endpoints manually**

```bash
# Start the server
python -m api_server.main

# In another terminal, test endpoints:
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"SecurePass123"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

- [ ] **Step 9: Commit**

```bash
git add api_server/ tests/test_auth_api.py
git commit -m "feat: add authentication API routes with comprehensive tests"
```

---

## Task 7: Create Frontend Authentication Types

**Files:**
- Create: `frontend/src/types/auth.ts`
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: Create authentication type definitions**

```typescript
// frontend/src/types/auth.ts
/**
 * Authentication related type definitions
 */

export interface User {
  user_id: string
  username: string
  email: string
  role: 'user' | 'admin'
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface ApiKey {
  key_id: string
  user_id: string
  api_key: string
  name: string
  scopes: string[]
  last_used?: string
  expires_at?: string
  created_at: string
  is_active: boolean
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  api_key: string
  message: string
}

export interface RegisterFormData {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export interface LoginFormData {
  email: string
  password: string
}

export interface CreateApiKeyRequest {
  name: string
  scopes: string[]
}

export interface CreateApiKeyResponse {
  api_key: ApiKey
  key: string
  message: string
}
```

- [ ] **Step 2: Update main types export file**

```typescript
// frontend/src/types/index.ts (update existing file)

// 统一导出所有类型
export * from './agent'
export * from './team'
export * from './conversation'
export * from './api'
export * from './auth'  // Add this line

// 通用工具类型
export interface PaginationParams {
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface FilterParams {
  status?: string
  tags?: string[]
  search?: string
  date_from?: string
  date_to?: string
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/
git commit -m "feat: add frontend authentication type definitions"
```

---

## Task 8: Create Frontend Authentication Service

**Files:**
- Create: `frontend/src/services/auth.service.ts`
- Modify: `frontend/src/services/index.ts`

- [ ] **Step 1: Create authentication service**

```typescript
// frontend/src/services/auth.service.ts
/**
 * Authentication API service
 */
import api from './api'
import type {
  User,
  ApiKey,
  RegisterRequest,
  LoginRequest,
  AuthResponse,
  CreateApiKeyRequest,
  CreateApiKeyResponse,
  ApiResponse,
} from '@/types'

export const authService = {
  /**
   * User registration
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<ApiResponse<AuthResponse>>(
      '/auth/register',
      data
    )
    return response.data.data
  },

  /**
   * User login
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<ApiResponse<AuthResponse>>(
      '/auth/login',
      data
    )
    return response.data.data
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<ApiResponse<{ user: User }>>(
      '/auth/me'
    )
    return response.data.data.user
  },

  /**
   * Get user's API keys
   */
  async getApiKeys(): Promise<ApiKey[]> {
    const response = await api.get<ApiResponse<{ api_keys: ApiKey[] }>>(
      '/auth/api-keys'
    )
    return response.data.data.api_keys
  },

  /**
   * Create new API key
   */
  async createApiKey(data: CreateApiKeyRequest): Promise<CreateApiKeyResponse> {
    const response = await api.post<ApiResponse<CreateApiKeyResponse>>(
      '/auth/api-keys',
      data
    )
    return response.data.data
  },

  /**
   * Delete API key
   */
  async deleteApiKey(keyId: string): Promise<void> {
    const response = await api.delete<ApiResponse<void>>(
      `/auth/api-keys/${keyId}`
    )
    return response.data
  },

  /**
   * Client-side logout (clears local storage)
   */
  logout(): void {
    localStorage.removeItem('auth-storage')
  },
}
```

- [ ] **Step 2: Update services index file**

```typescript
// frontend/src/services/index.ts (update existing file)
export { authService } from './auth.service'
export { agentService } from './agent.service'
export { teamService } from './team.service'
export { conversationService } from './conversation.service'
export { templateService } from './template.service'
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/services/
git commit -m "feat: add frontend authentication service"
```

---

## Task 9: Create Frontend Authentication State Management

**Files:**
- Create: `frontend/src/store/auth.store.ts`
- Modify: `frontend/src/store/index.ts`
- Modify: `frontend/src/store/app.store.ts`

- [ ] **Step 1: Install zustand persistence middleware if not available**

```bash
cd frontend
npm install zustand
```

- [ ] **Step 2: Create authentication store**

```typescript
// frontend/src/store/auth.store.ts
/**
 * Authentication state management
 */
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User, ApiKey } from '@/types'
import { authService } from '@/services'

interface AuthState {
  // State
  user: User | null
  apiKey: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  getCurrentUser: () => Promise<void>
  setApiKey: (apiKey: string) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      apiKey: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login action
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authService.login({ email, password })
          set({
            user: response.user,
            apiKey: response.api_key,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || '登录失败'
          set({
            error: errorMessage,
            isLoading: false,
          })
          throw error
        }
      },

      // Register action
      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authService.register({
            username,
            email,
            password,
          })
          set({
            user: response.user,
            apiKey: response.api_key,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || '注册失败'
          set({
            error: errorMessage,
            isLoading: false,
          })
          throw error
        }
      },

      // Logout action
      logout: () => {
        authService.logout()
        set({
          user: null,
          apiKey: null,
          isAuthenticated: false,
        })
      },

      // Get current user action
      getCurrentUser: async () => {
        set({ isLoading: true, error: null })
        try {
          const user = await authService.getCurrentUser()
          set({ user, isLoading: false })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || '获取用户信息失败'
          set({
            error: errorMessage,
            isLoading: false,
          })
          // If getting user fails, clear auth state
          get().logout()
        }
      },

      // Set API key action
      setApiKey: (apiKey: string) => {
        set({ apiKey })
      },

      // Clear error action
      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist user info and API key
      partialize: (state) => ({
        user: state.user,
        apiKey: state.apiKey,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
```

- [ ] **Step 3: Update store index file**

```typescript
// frontend/src/store/index.ts (update existing file)
export { useAuthStore } from './auth.store'
export { useAppStore } from './app.store'
```

- [ ] **Step 4: Update app store to integrate auth**

```typescript
// frontend/src/store/app.store.ts (update existing file)

// Add import for auth store
import { useAuthStore } from './store'

// In the app store, add:
export const useAppStore = create<AppState>((set, get) => ({
  // ... existing state ...

  // Add user info from auth store
  user: useAuthStore.getState().user,

  // ... existing actions ...
}))

// You can also add a selector to get auth info
export const useUser = () => useAuthStore((state) => state.user)
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated)
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/store/
git commit -m "feat: add authentication state management with zustand"
```

---

## Task 10: Update API Client with Authentication Interceptor

**Files:**
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: Update API client to add authentication interceptor**

```typescript
// frontend/src/services/api.ts (update existing file)
/**
 * API client with authentication
 */
import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/store'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add authentication header
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { apiKey } = useAuthStore.getState()
    if (apiKey && config.headers) {
      config.headers['X-API-Key'] = apiKey
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle authentication errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // Handle 401 Unauthorized - clear auth state and redirect to login
    if (error.response?.status === 401) {
      const authStore = useAuthStore.getState()
      authStore.logout()

      // Only redirect if we're in a browser environment
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add authentication interceptor to API client"
```

---

## Task 11: Create Protected Route Component

**Files:**
- Create: `frontend/src/components/Auth/ProtectedRoute.tsx`
- Create: `frontend/src/components/Auth/index.ts`

- [ ] **Step 1: Create protected route component**

```typescript
// frontend/src/components/Auth/ProtectedRoute.tsx
/**
 * Route protection component
 */
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { Spin } from 'antd'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireAuth?: boolean
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
}) => {
  const { isAuthenticated, isLoading } = useAuthStore()
  const location = useLocation()

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  // Redirect to login if authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Redirect to home if authentication is not required but user is authenticated
  if (!requireAuth && isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
```

- [ ] **Step 2: Create Auth components index file**

```typescript
// frontend/src/components/Auth/index.ts
export { ProtectedRoute } from './ProtectedRoute'
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/Auth/
git commit -m "feat: add protected route component for authentication"
```

---

## Task 12: Create Login Page

**Files:**
- Create: `frontend/src/pages/Auth/Login.tsx`
- Create: `frontend/src/pages/Auth/index.ts`

- [ ] **Step 1: Create login page component**

```typescript
// frontend/src/pages/Auth/Login.tsx
/**
 * User login page
 */
import { useState } from 'react'
import { Form, Input, Button, Card, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store'

const { Title, Text } = Typography

interface LoginFormData {
  email: string
  password: string
}

export const Login: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading } = useAuthStore()
  const [form] = Form.useForm()

  const from = (location.state as any)?.from?.pathname || '/'

  const onFinish = async (values: LoginFormData) => {
    try {
      await login(values.email, values.password)
      message.success('登录成功')
      navigate(from, { replace: true })
    } catch (error) {
      // Error is handled by the store
      message.error('登录失败，请检查邮箱和密码')
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>AgentScope PaaS</Title>
          <Text type="secondary">登录您的账户</Text>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="邮箱"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoading}
              block
            >
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Space>
              <Text>还没有账户？</Text>
              <a onClick={() => navigate('/register')}>立即注册</a>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}
```

- [ ] **Step 2: Create Auth pages index file**

```typescript
// frontend/src/pages/Auth/index.ts
export { Login } from './Login'
export { Register } from './Register'
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Auth/
git commit -m "feat: add login page with form validation"
```

---

## Task 13: Create Register Page

**Files:**
- Create: `frontend/src/pages/Auth/Register.tsx`
- Modify: `frontend/src/pages/Auth/index.ts`

- [ ] **Step 1: Create register page component**

```typescript
// frontend/src/pages/Auth/Register.tsx
/**
 * User registration page
 */
import { useState } from 'react'
import { Form, Input, Button, Card, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'

const { Title, Text } = Typography

interface RegisterFormData {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export const Register: React.FC = () => {
  const navigate = useNavigate()
  const { register, isLoading } = useAuthStore()
  const [form] = Form.useForm()

  const onFinish = async (values: RegisterFormData) => {
    try {
      await register(values.username, values.email, values.password)
      message.success('注册成功')
      navigate('/')
    } catch (error) {
      // Error is handled by the store
      message.error('注册失败，请稍后重试')
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>AgentScope PaaS</Title>
          <Text type="secondary">创建新账户</Text>
        </div>

        <Form
          form={form}
          name="register"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
              { max: 20, message: '用户名最多20个字符' },
              {
                pattern: /^[a-zA-Z0-9_]+$/,
                message: '用户名只能包含字母、数字和下划线',
              },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 8, message: '密码至少8个字符' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                message: '密码必须包含大小写字母和数字',
              },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoading}
              block
            >
              注册
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Space>
              <Text>已有账户？</Text>
              <a onClick={() => navigate('/login')}>立即登录</a>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}
```

- [ ] **Step 2: Update Auth pages index file**

```typescript
// frontend/src/pages/Auth/index.ts (update)
export { Login } from './Login'
export { Register } from './Register'
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Auth/
git commit -m "feat: add registration page with comprehensive validation"
```

---

## Task 14: Update Main App with Authentication Routes

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Update main app component to include authentication**

```typescript
// frontend/src/App.tsx (update existing file)
/**
 * Main application component with authentication
 */
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { Router, Routes, Route, Navigate } from 'react-router-dom'
import { BrowserRouter } from 'react-router-dom/browser'
import { ProtectedRoute } from './components/Auth'
import { MainLayout } from './components/Layout'
import { Login, Register } from './pages/Auth'
import Dashboard from './pages/Dashboard'
import { AgentList, AgentCreate } from './pages/Agent'
import { TeamList, TeamCreate } from './pages/Team'
import Conversation from './pages/Conversation'
import Monitoring from './pages/Monitoring'
import Settings from './pages/Settings'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route
            path="/login"
            element={
              <ProtectedRoute requireAuth={false}>
                <Login />
              </ProtectedRoute>
            }
          />
          <Route
            path="/register"
            element={
              <ProtectedRoute requireAuth={false}>
                <Register />
              </ProtectedRoute>
            }
          />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="agents" element={<AgentList />} />
            <Route path="agents/create" element={<AgentCreate />} />
            <Route path="agents/:agentId" element={<AgentList />} />
            <Route path="teams" element={<TeamList />} />
            <Route path="teams/create" element={<TeamCreate />} />
            <Route path="teams/:teamId" element={<TeamList />} />
            <Route path="conversation" element={<Conversation />} />
            <Route path="monitoring" element={<Monitoring />} />
            <Route path="settings" element={<Settings />} />
          </Route>

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: integrate authentication routes into main app"
```

---

## Task 15: Update Main Layout with User Info and Logout

**Files:**
- Modify: `frontend/src/components/Layout/MainLayout.tsx`

- [ ] **Step 1: Update main layout to show user info and logout button**

```typescript
// frontend/src/components/Layout/MainLayout.tsx (update existing file)
/**
 * Main layout component with user info
 */
import { Layout, Menu, Dropdown, Avatar } from 'antd'
import {
  HomeOutlined,
  RobotOutlined,
  TeamOutlined,
  MessageOutlined,
  MonitoringOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store'

const { Header, Sider, Content } = Layout

export const MainLayout: React.FC<{ children?: React.ReactNode }> = ({
  children,
}) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <HomeOutlined />,
      label: '仪表板',
      onClick: () => navigate('/dashboard'),
    },
    {
      key: '/agents',
      icon: <RobotOutlined />,
      label: '智能体管理',
      onClick: () => navigate('/agents'),
    },
    {
      key: '/teams',
      icon: <TeamOutlined />,
      label: '团队管理',
      onClick: () => navigate('/teams'),
    },
    {
      key: '/conversation',
      icon: <MessageOutlined />,
      label: '对话',
      onClick: () => navigate('/conversation'),
    },
    {
      key: '/monitoring',
      icon: <MonitoringOutlined />,
      label: '监控中心',
      onClick: () => navigate('/monitoring'),
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings'),
    },
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
      onClick: () => navigate('/settings'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        logout()
        navigate('/login')
      },
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={240}>
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: 18,
            fontWeight: 'bold',
          }}
        >
          AgentScope PaaS
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <div />
          <Dropdown
            menu={{ items: userMenuItems }}
            placement="bottomRight"
          >
            <div
              style={{
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <Avatar icon={<UserOutlined />} />
              <span>{user?.username || '用户'}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: '#fff',
              borderRadius: 4,
            }}
          >
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/Layout/MainLayout.tsx
git commit -m "feat: add user info and logout to main layout"
```

---

## Task 16: Test Complete Authentication Flow

**Files:**
- All created files
- Manual testing

- [ ] **Step 1: Start backend server**

```bash
cd /d/workspace/agentscope-paas
python -m api_server.main
```

- [ ] **Step 2: Start frontend development server**

```bash
cd frontend
npm run dev
```

- [ ] **Step 3: Test complete authentication flow**

1. **Navigate to http://localhost:3000**
   - Expected: Redirect to /login

2. **Test Registration**
   - Click "立即注册"
   - Fill in form:
     - Username: "testuser"
     - Email: "test@example.com"
     - Password: "SecurePass123"
     - Confirm Password: "SecurePass123"
   - Click "注册"
   - Expected: Success message, redirect to dashboard

3. **Test Protected Routes**
   - Try accessing /agents, /teams, /settings
   - Expected: All pages load successfully

4. **Test Logout**
   - Click user dropdown in header
   - Click "退出登录"
   - Expected: Redirect to /login

5. **Test Login**
   - Fill in form:
     - Email: "test@example.com"
     - Password: "SecurePass123"
   - Click "登录"
   - Expected: Success message, redirect to dashboard

6. **Test Invalid Login**
   - Try with wrong password
   - Expected: Error message

- [ ] **Step 4: Test API authentication**

```bash
# Test without authentication (should fail)
curl http://localhost:8000/api/v1/agents

# Test with authentication (should succeed)
API_KEY="as_live_testuser_..." # Use the key from registration
curl -H "X-API-Key: $API_KEY" http://localhost:8000/api/v1/agents
```

- [ ] **Step 5: Run all tests**

```bash
# Backend tests
pytest tests/ -v

# Frontend tests (if available)
cd frontend
npm run test
```

- [ ] **Step 6: Final commit**

```bash
git add .
git commit -m "feat: complete authentication system implementation"
```

---

## Completion Checklist

- [ ] All storage models and interfaces implemented
- [ ] Memory storage with comprehensive tests
- [ ] Security utilities (password hashing, API key generation)
- [ ] Authentication middleware with role-based access
- [ ] Authentication API routes (register, login, profile, API keys)
- [ ] Frontend authentication types
- [ ] Frontend authentication service
- [ ] Frontend authentication state management
- [ ] API client with authentication interceptor
- [ ] Protected route component
- [ ] Login and registration pages
- [ ] Updated main app with authentication routes
- [ ] User info display and logout in main layout
- [ ] Complete authentication flow tested
- [ ] All tests passing

---

## Implementation Notes

### Key Design Decisions

1. **API Key Authentication**: Simple and effective for development, easy to extend to JWT later
2. **Storage Abstraction**: Clean interface allows switching between storage implementations
3. **Zustand for State Management**: Lightweight and performant choice for React state
4. **Route Protection**: Centralized authentication checking for protected routes
5. **Form Validation**: Comprehensive validation on both client and server side

### Security Considerations

1. **Password Hashing**: PBKDF2 with 100,000 iterations and salt
2. **API Key Storage**: Hashed for validation, plain key only shown on creation
3. **HTTPS Recommended**: Use HTTPS in production for secure transmission
4. **Input Validation**: Comprehensive validation on all inputs
5. **Role-Based Access**: Foundation for future permission system

### Future Enhancements

1. **JWT Tokens**: Migrate from API keys to JWT for better scalability
2. **OAuth Integration**: Add Google, GitHub OAuth login
3. **Email Verification**: Send verification emails on registration
4. **Password Reset**: Implement forgot password functionality
5. **Two-Factor Authentication**: Add 2FA for enhanced security
6. **Session Management**: Add session timeout and refresh tokens

---

**Plan completed**: All tasks defined with complete implementation details, test cases, and commit messages.