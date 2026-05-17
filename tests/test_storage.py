"""
Tests for storage models and memory storage implementation
"""
import pytest
import time
from datetime import datetime
from agentscope_paas.storage.models import User, ApiKey, Session
from agentscope_paas.storage.memory import MemoryStorage


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


def test_storage_interface_is_abstract():
    """Test that IStorage cannot be instantiated directly"""
    from agentscope_paas.storage.base import IStorage

    with pytest.raises(TypeError):
        IStorage()


# MemoryStorage Tests
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
async def test_memory_storage_update_user_email():
    """Test updating user email maintains index consistency"""
    storage = MemoryStorage()
    user = User(
        user_id="user_001",
        username="testuser",
        email="old@example.com",
        password_hash="salt$hash"
    )

    await storage.save_user(user)

    # Update email
    result = await storage.update_user("user_001", {"email": "new@example.com"})
    assert result is True

    # Old email should not work
    old_lookup = await storage.get_user_by_email("old@example.com")
    assert old_lookup is None

    # New email should work
    new_lookup = await storage.get_user_by_email("new@example.com")
    assert new_lookup is not None
    assert new_lookup.email == "new@example.com"


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
