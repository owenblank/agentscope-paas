"""
Data models for authentication system
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model"""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="User email")
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
