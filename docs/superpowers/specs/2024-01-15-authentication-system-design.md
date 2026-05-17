# AgentScope PaaS 认证系统设计文档

**项目**: AgentScope PaaS 平台
**日期**: 2024-01-15
**版本**: 1.0
**状态**: 设计阶段

## 目录

1. [系统架构](#第一章系统架构)
2. [数据模型与存储接口](#第二章数据模型与存储接口)
3. [API端点与中间件](#第三章api端点与中间件)
4. [前端集成](#第四章前端集成设计)
5. [实现计划](#第五章实现计划)
6. [测试策略](#第六章测试策略)
7. [部署指南](#第七章部署指南)
8. [后续扩展](#第八章后续扩展计划)

---

## 第一章：系统架构

### 1.1 分层架构

```
┌─────────────────────────────────────────┐
│         Frontend (React + TS)           │
│  ┌─────────────┐    ┌────────────────┐ │
│  │ Auth Pages  │    │  API Client    │ │
│  │ Login/Reg   │    │  (with Auth)   │ │
│  └─────────────┘    └────────────────┘ │
└───────────────┬─────────────────────────┘
                │ HTTP + X-API-Key
┌───────────────▼─────────────────────────┐
│        Backend (FastAPI)                 │
│  ┌──────────────────────────────────┐   │
│  │  API Layer (routers/auth.py)     │   │
│  │  - /auth/register                │   │
│  │  - /auth/login                   │   │
│  │  - /auth/me                      │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Auth Middleware                  │   │
│  │  - api_key_auth()                │   │
│  │  - optional_auth()               │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Service Layer                    │   │
│  │  - AuthService                   │   │
│  │  - UserService                   │   │
│  └──────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│      Storage Layer (Abstract)           │
│  ┌──────────────────────────────────┐   │
│  │  IStorage (Interface)            │   │
│  │  - save_user()                   │   │
│  │  - get_user()                    │   │
│  │  - validate_api_key()            │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  MemoryStorage (Implementation)  │   │
│  │  - In-memory dict storage        │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 1.2 核心组件说明

**API层**
- `/api/v1/auth/register` - 用户注册
- `/api/v1/auth/login` - 用户登录
- `/api/v1/auth/me` - 获取当前用户信息
- `/api/v1/auth/api-keys` - API密钥管理

**认证中间件**
- `api_key_auth()` - 强制API密钥验证
- `optional_auth()` - 可选认证（允许匿名访问）

**存储抽象层**
- 接口定义（IStorage）：定义所有数据操作
- 内存实现（MemoryStorage）：当前默认实现
- 未来可扩展：SQLiteStorage、PostgreSQLStorage

**前端集成**
- 新增 `authService.ts` - 认证API调用
- 新增 `authStore.ts` - 认证状态管理（Zustand）
- 新增登录/注册页面
- 更新现有API客户端自动添加认证头

---

## 第二章：数据模型与存储接口

### 2.1 核心数据模型

```python
# 用户模型
class User(BaseModel):
    user_id: str                    # 唯一标识
    username: str                    # 用户名
    email: str                       # 邮箱
    password_hash: str               # 密码哈希
    role: str = "user"              # 角色: user, admin
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

# API密钥模型
class ApiKey(BaseModel):
    key_id: str                      # 密钥ID
    user_id: str                     # 所属用户
    api_key: str                     # API密钥（明文，用于显示）
    key_hash: str                    # 密钥哈希（用于验证）
    name: str                        # 密钥名称（如："开发环境密钥"）
    scopes: List[str] = ["read"]    # 权限范围
    last_used: Optional[datetime]   # 最后使用时间
    expires_at: Optional[datetime]  # 过期时间
    created_at: datetime
    is_active: bool = True

# 会话模型（为未来JWT准备）
class Session(BaseModel):
    session_id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    created_at: datetime
```

### 2.2 存储抽象层接口

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class IStorage(ABC):
    """存储抽象接口"""

    @abstractmethod
    async def save_user(self, user: User) -> bool:
        """保存用户"""
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        pass

    @abstractmethod
    async def update_user(self, user_id: str, updates: dict) -> bool:
        """更新用户信息"""
        pass

    @abstractmethod
    async def save_api_key(self, api_key: ApiKey) -> bool:
        """保存API密钥"""
        pass

    @abstractmethod
    async def get_api_key(self, key_id: str) -> Optional[ApiKey]:
        """获取API密钥"""
        pass

    @abstractmethod
    async def validate_api_key(self, api_key: str) -> Optional[User]:
        """验证API密钥并返回用户"""
        pass

    @abstractmethod
    async def get_user_api_keys(self, user_id: str) -> List[ApiKey]:
        """获取用户的所有API密钥"""
        pass

    @abstractmethod
    async def delete_api_key(self, key_id: str) -> bool:
        """删除API密钥"""
        pass

    @abstractmethod
    async def update_api_key_last_used(self, key_id: str) -> bool:
        """更新API密钥最后使用时间"""
        pass
```

### 2.3 前端类型定义

```typescript
// types/user.ts
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
}
```

---

## 第三章：API端点与中间件

### 3.1 认证API端点

#### 3.1.1 用户注册
**端点**: `POST /api/v1/auth/register`

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "user_001",
      "username": "testuser",
      "email": "test@example.com",
      "role": "user",
      "created_at": "2024-01-15T10:30:00Z"
    },
    "api_key": "as_live_testuser_abc123xyz...",
    "message": "注册成功，请妥善保管您的API密钥"
  }
}
```

#### 3.1.2 用户登录
**端点**: `POST /api/v1/auth/login`

**请求体**:
```json
{
  "email": "test@example.com",
  "password": "securepassword123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user": { ... },
    "api_key": "as_live_testuser_abc123xyz...",
    "message": "登录成功"
  }
}
```

#### 3.1.3 获取当前用户信息
**端点**: `GET /api/v1/auth/me`

**请求头**: `X-API-Key: as_live_testuser_abc123xyz...`

**响应**:
```json
{
  "success": true,
  "data": {
    "user": { ... }
  }
}
```

### 3.2 认证中间件

#### 3.2.1 API密钥验证中间件
```python
async def api_key_auth(api_key: str = Security(api_key_header)) -> User:
    """
    强制API密钥验证

    用法:
    @app.get("/api/v1/protected")
    async def protected_endpoint(current_user: User = Depends(api_key_auth)):
        return {"message": f"Hello, {current_user.username}"}
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API密钥缺失，请在请求头中提供X-API-Key"
        )

    user = await storage.validate_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )

    await storage.update_api_key_last_used(api_key)
    return user
```

### 3.3 安全特性

#### 3.3.1 密码哈希
```python
import hashlib
import secrets

def hash_password(password: str) -> str:
    """安全的密码哈希"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 迭代次数
    ).hex()
    return f"{salt}${password_hash}"

def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    try:
        salt, hash_value = password_hash.split('$')
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return computed_hash == hash_value
    except:
        return False
```

#### 3.3.2 API密钥生成
```python
def generate_api_key(username: str) -> tuple[str, str]:
    """
    生成API密钥
    返回: (明文密钥, 哈希密钥)

    格式: as_live_{username}_{随机字符}
    """
    random_part = secrets.token_urlsafe(32)
    api_key = f"as_live_{username}_{random_part}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key, key_hash
```

---

## 第四章：前端集成设计

### 4.1 前端项目结构

```
frontend/src/
├── services/
│   ├── auth.service.ts          # 认证API服务
│   ├── api.ts                   # 更新：添加认证拦截器
│   └── ...
├── store/
│   ├── auth.store.ts            # 认证状态管理
│   ├── app.store.ts             # 更新：集成认证状态
│   └── ...
├── pages/
│   ├── Auth/
│   │   ├── Login.tsx            # 登录页面
│   │   ├── Register.tsx         # 注册页面
│   │   └── index.ts
│   └── ...
├── components/
│   ├── Auth/
│   │   ├── ProtectedRoute.tsx   # 路由保护组件
│   │   └── ApiKeyManager.tsx    # API密钥管理组件
│   └── ...
├── types/
│   ├── auth.ts                  # 认证相关类型
│   └── ...
└── utils/
    └── storage.ts               # 本地存储工具
```

### 4.2 认证服务

```typescript
// services/auth.service.ts
export const authService = {
  async register(data: RegisterRequest) {
    const response = await api.post<ApiResponse<AuthResponse>>(
      '/auth/register',
      data
    )
    return response.data.data
  },

  async login(data: LoginRequest) {
    const response = await api.post<ApiResponse<AuthResponse>>(
      '/auth/login',
      data
    )
    return response.data.data
  },

  async getCurrentUser() {
    const response = await api.get<ApiResponse<{ user: User }>>(
      '/auth/me'
    )
    return response.data.data.user
  },

  logout() {
    localStorage.removeItem('api_key')
    localStorage.removeItem('user')
  },
}
```

### 4.3 认证状态管理

```typescript
// store/auth.store.ts
interface AuthState {
  user: User | null
  apiKey: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  getCurrentUser: () => Promise<void>
}
```

### 4.4 API客户端更新

```typescript
// services/api.ts
api.interceptors.request.use(
  (config) => {
    const { apiKey } = useAuthStore.getState()
    if (apiKey) {
      config.headers['X-API-Key'] = apiKey
    }
    return config
  }
)
```

---

## 第五章：实现计划

### 5.1 实现阶段划分

#### 阶段1：基础架构搭建（第1-2天）
- 创建项目目录结构
- 实现存储抽象接口
- 实现内存存储
- 创建数据模型

#### 阶段2：后端API实现（第3-4天）
- 实现用户注册端点
- 实现用户登录端点
- 实现获取用户信息端点
- 实现API密钥管理端点
- 集成认证中间件

#### 阶段3：前端服务层（第5天）
- 创建认证服务
- 创建认证状态管理
- 更新API客户端
- 添加认证相关类型

#### 阶段4：前端页面实现（第6-7天）
- 创建登录页面
- 创建注册页面
- 创建路由保护组件
- 更新主布局

#### 阶段5：集成与测试（第8天）
- 集成前后端
- 端到端测试
- 修复bug和优化
- 文档完善

### 5.2 依赖关系图

```
存储抽象层 → 内存存储 → 数据模型
                ↓
            安全工具 → 认证中间件
                ↓
            认证路由 → 主应用集成
                ↓
          前端服务 → 状态管理 → 页面组件
```

---

## 第六章：测试策略

### 6.1 后端测试

#### 单元测试
- 存储层CRUD操作测试
- 安全工具测试（密码哈希、API密钥生成）
- 中间件认证逻辑测试

#### API集成测试
- 用户注册流程测试
- 用户登录流程测试
- 受保护端点访问控制测试
- 错误处理测试

#### 安全测试
- 密码哈希验证测试
- API密钥生成格式测试
- SQL注入防护测试
- 认证绕过测试

### 6.2 前端测试

#### 组件测试
- ProtectedRoute组件测试
- Login页面表单验证测试
- Register页面表单验证测试

#### 服务测试
- authService API调用测试
- authStore状态管理测试
- API拦截器测试

#### E2E测试
- 完整注册流程测试
- 完整登录流程测试
- 路由保护功能测试
- API密钥显示测试

---

## 第七章：部署指南

### 7.1 环境配置

#### 开发环境
```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_ENABLE_DEBUG=true
```

#### 生产环境
```bash
VITE_API_URL=https://api.yourdomain.com/api/v1
DATABASE_URL=postgresql://user:pass@localhost/agentscope
SECRET_KEY=your-secret-key-here
```

### 7.2 Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/agentscope
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=agentscope
      - POSTGRES_USER=agent
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 第八章：后续扩展计划

### 8.1 短期扩展（1-2个月）

#### 存储层升级
- 实现SQLite存储
- 数据迁移工具
- 数据备份策略

#### 功能增强
- 邮箱验证
- 密码重置
- 用户资料编辑
- API密钥权限细化

#### 安全增强
- 速率限制
- IP白名单
- 审计日志
- 双因素认证（2FA）

### 8.2 中期扩展（3-6个月）

#### JWT支持
- 从API密钥平滑迁移到JWT
- Token刷新机制
- 令牌过期策略

#### OAuth集成
- Google OAuth
- GitHub OAuth
- 企业单点登录（SSO）

#### 团队管理
- 团队创建和邀请
- 基于团队的权限控制
- 团队API密钥管理

### 8.3 长期扩展（6个月+）

#### 企业级功能
- 多租户支持
- 细粒度权限控制（RBAC）
- 审计和合规报告
- 高级威胁防护

#### 性能优化
- Redis缓存层
- 数据库读写分离
- CDN加速
- 负载均衡

---

## 附录

### A. 文件清单

**后端文件**
- `agentscope_paas/storage/base.py` - 存储抽象接口
- `agentscope_paas/storage/memory.py` - 内存存储实现
- `agentscope_paas/storage/models.py` - 数据模型
- `agentscope_paas/auth/security.py` - 安全工具
- `agentscope_paas/auth/middleware.py` - 认证中间件
- `api_server/routers/auth.py` - 认证路由
- `api_server/main.py` - 主应用（更新）

**前端文件**
- `frontend/src/services/auth.service.ts` - 认证服务
- `frontend/src/store/auth.store.ts` - 认证状态管理
- `frontend/src/types/auth.ts` - 认证类型定义
- `frontend/src/pages/Auth/Login.tsx` - 登录页面
- `frontend/src/pages/Auth/Register.tsx` - 注册页面
- `frontend/src/components/Auth/ProtectedRoute.tsx` - 路由保护
- `frontend/src/services/api.ts` - API客户端（更新）

### B. 时间估算

- **阶段1**: 2天
- **阶段2**: 2天
- **阶段3**: 1天
- **阶段4**: 2天
- **阶段5**: 1天

**总计**: 8个工作日

### C. 风险评估

| 风险 | 影响 | 概率 | 缓解策略 |
|------|------|------|----------|
| 存储抽象层设计不当 | 高 | 中 | 充分的接口设计和测试 |
| 前后端集成问题 | 中 | 低 | 详细的API文档和测试 |
| 安全漏洞 | 高 | 低 | 代码审查和安全测试 |
| 性能问题 | 中 | 低 | 性能测试和优化 |

---

**文档版本**: 1.0
**最后更新**: 2024-01-15
**作者**: Claude AI Assistant
**状态**: 待审查