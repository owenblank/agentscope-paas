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
