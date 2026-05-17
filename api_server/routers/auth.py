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


router = APIRouter(tags=["认证"])


@router.post("/api/v1/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
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


@router.post("/api/v1/auth/login")
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


@router.get("/api/v1/auth/me")
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


@router.get("/api/v1/auth/api-keys")
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


@router.post("/api/v1/auth/api-keys", status_code=status.HTTP_201_CREATED)
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


@router.delete("/api/v1/auth/api-keys/{key_id}")
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