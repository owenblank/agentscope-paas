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
