import pytest
import pytest_asyncio
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


@pytest_asyncio.fixture
async def storage():
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
    await storage.save_user(user)

    # Create admin user
    admin = User(
        user_id="admin_001",
        username="admin",
        email="admin@example.com",
        password_hash="salt$hash",
        role="admin"
    )
    await storage.save_user(admin)

    # Create API key for user
    plain_key, key_hash = generate_api_key("testuser")
    api_key = ApiKey(
        key_id="key_001",
        user_id="user_001",
        api_key=plain_key,
        key_hash=key_hash,
        name="Test Key"
    )
    await storage.save_api_key(api_key)

    return storage, plain_key


@pytest_asyncio.fixture
async def test_app(storage):
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


@pytest.mark.asyncio
async def test_admin_endpoint_with_admin_user(storage):
    """Test admin endpoint with admin user"""
    storage_instance, _ = storage

    # Create admin API key
    admin_key, key_hash = generate_api_key("admin")
    api_key = ApiKey(
        key_id="key_admin",
        user_id="admin_001",
        api_key=admin_key,
        key_hash=key_hash,
        name="Admin Key"
    )
    await storage_instance.save_api_key(api_key)

    set_storage(storage_instance)

    app = FastAPI()

    @app.get("/admin")
    async def admin_endpoint(current_user: User = Depends(require_role("admin"))):
        return {"user": current_user.username}

    client = TestClient(app)
    response = client.get("/admin", headers={"X-API-Key": admin_key})

    assert response.status_code == 200
    assert response.json()["user"] == "admin"


@pytest.mark.asyncio
async def test_admin_endpoint_with_regular_user(test_app):
    """Test admin endpoint with regular user (should fail)"""
    app, api_key = test_app
    client = TestClient(app)

    # Add admin endpoint to test app
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


@pytest.mark.asyncio
async def test_user_account_disabled_rejected():
    """Test that disabled user accounts are rejected"""
    # Create a new storage with a disabled user
    storage = MemoryStorage()

    # Create disabled user
    disabled_user = User(
        user_id="disabled_001",
        username="disabled",
        email="disabled@example.com",
        password_hash="salt$hash",
        role="user",
        is_active=False
    )
    await storage.save_user(disabled_user)

    # Create API key for disabled user
    disabled_key, key_hash = generate_api_key("disabled")
    disabled_api_key = ApiKey(
        key_id="key_disabled",
        user_id="disabled_001",
        api_key=disabled_key,
        key_hash=key_hash,
        name="Disabled User Key"
    )
    await storage.save_api_key(disabled_api_key)

    set_storage(storage)

    app = FastAPI()

    @app.get("/protected")
    async def protected_endpoint(current_user: User = Depends(api_key_auth)):
        return {"user": current_user.username}

    client = TestClient(app)
    response = client.get("/protected", headers={"X-API-Key": disabled_key})

    assert response.status_code == 403
    assert "用户账户已被禁用" in response.json()["detail"]


@pytest.mark.asyncio
async def test_multiple_role_requirement():
    """Test requiring multiple roles"""
    storage = MemoryStorage()

    # Create user with role
    user = User(
        user_id="user_002",
        username="testuser2",
        email="test2@example.com",
        password_hash="salt$hash",
        role="editor"
    )
    await storage.save_user(user)

    # Create API key
    plain_key, key_hash = generate_api_key("testuser2")
    api_key = ApiKey(
        key_id="key_002",
        user_id="user_002",
        api_key=plain_key,
        key_hash=key_hash,
        name="Editor Key"
    )
    await storage.save_api_key(api_key)

    set_storage(storage)

    app = FastAPI()

    @app.get("/editor_only")
    async def editor_endpoint(current_user: User = Depends(require_role("editor"))):
        return {"user": current_user.username}

    @app.get("/readwrite")
    async def readwrite_endpoint(current_user: User = Depends(require_role("read", "write", "admin"))):
        return {"user": current_user.username}

    client = TestClient(app)

    # Test editor endpoint
    response = client.get("/editor_only", headers={"X-API-Key": plain_key})
    assert response.status_code == 200

    # Test that non-admin, non-editor user is rejected from admin routes
    response = client.get("/readwrite", headers={"X-API-Key": plain_key})
    assert response.status_code == 403
    assert "需要以下角色之一" in response.json()["detail"]


@pytest.mark.asyncio
async def test_api_key_last_updated_timestamp():
    """Test that API key last_used timestamp is updated on successful auth"""
    storage = MemoryStorage()

    # Create user
    user = User(
        user_id="user_003",
        username="testuser3",
        email="test3@example.com",
        password_hash="salt$hash",
        role="user"
    )
    await storage.save_user(user)

    # Create API key with specific creation time
    plain_key, key_hash = generate_api_key("testuser3")
    api_key = ApiKey(
        key_id="key_003",
        user_id="user_003",
        api_key=plain_key,
        key_hash=key_hash,
        name="Test Key",
        last_used=None  # Start with no last_used
    )
    await storage.save_api_key(api_key)

    set_storage(storage)

    app = FastAPI()

    @app.get("/protected")
    async def protected_endpoint(current_user: User = Depends(api_key_auth)):
        return {"user": current_user.username}

    client = TestClient(app)

    # Before request
    key_before = await storage.get_api_key("key_003")
    assert key_before is not None
    assert key_before.last_used is None

    # Make request
    response = client.get("/protected", headers={"X-API-Key": plain_key})
    assert response.status_code == 200

    # After request
    key_after = await storage.get_api_key("key_003")
    assert key_after is not None
    assert key_after.last_used is not None