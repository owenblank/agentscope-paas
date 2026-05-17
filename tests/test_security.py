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
