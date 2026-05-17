"""
Authentication middleware for FastAPI
"""
from typing import Optional
import hashlib
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from agentscope_paas.storage.models import User, ApiKey
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

    # Update last used timestamp - find the API key by hash
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    user_api_keys = await storage.get_user_api_keys(user.user_id)
    for user_api_key in user_api_keys:
        if user_api_key.key_hash == key_hash and user_api_key.is_active:
            await storage.update_api_key_last_used(user_api_key.key_id)
            break

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
        # Update last used timestamp - find the API key by hash
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        user_api_keys = await storage.get_user_api_keys(user.user_id)
        for user_api_key in user_api_keys:
            if user_api_key.key_hash == key_hash and user_api_key.is_active:
                await storage.update_api_key_last_used(user_api_key.key_id)
                break
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