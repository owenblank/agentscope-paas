# AgentScope PaaS API 接口设计

## 🌐 RESTful API 设计规范

### 基础信息
- **基础URL**: `http://localhost:8000/api/v1`
- **认证方式**: Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 📋 API 端点列表

### 1. 智能体管理

#### 1.1 创建智能体
```http
POST /api/v1/agents
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "config": {
    "agent_metadata": {
      "agent_id": "customer_service_001",
      "agent_name": "智能客服助手",
      "agent_type": "DialogAgent",
      "description": "提供24小时在线客户服务",
      "version": "1.0.0",
      "tags": ["客服", "中文"]
    },
    "model_config": {
      "model_name": "gpt-4o",
      "api_key": "sk-proj-xxxxx",
      "temperature": 0.7
    },
    "prompt_config": {
      "system_prompt": "你是一个专业的客户服务代表..."
    }
  }
}

响应示例：
{
  "success": true,
  "data": {
    "agent_id": "customer_service_001",
    "status": "created",
    "created_at": "2024-01-15T10:30:00Z",
    "config_file": "/data/agents/customer_service_001.yaml"
  },
  "message": "智能体创建成功"
}
```

#### 1.2 获取智能体列表
```http
GET /api/v1/agents?page=1&limit=20&status=running&tags=客服
Authorization: Bearer {access_token}

响应示例：
{
  "success": true,
  "data": {
    "agents": [
      {
        "agent_id": "customer_service_001",
        "agent_name": "智能客服助手",
        "agent_type": "DialogAgent",
        "status": "running",
        "created_at": "2024-01-15T10:30:00Z",
        "last_activity": "2024-01-15T14:25:00Z",
        "total_conversations": 1234,
        "tags": ["客服", "中文"]
      }
    ],
    "pagination": {
      "total": 45,
      "page": 1,
      "limit": 20,
      "pages": 3
    }
  }
}
```

#### 1.3 获取智能体详情
```http
GET /api/v1/agents/{agent_id}
Authorization: Bearer {access_token}

响应示例：
{
  "success": true,
  "data": {
    "agent_id": "customer_service_001",
    "config": { /* 完整配置 */ },
    "status": "running",
    "statistics": {
      "total_conversations": 1234,
      "total_tokens_used": 1234567,
      "average_response_time": 2.3,
      "success_rate": 98.5
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
}
```

#### 1.4 更新智能体
```http
PUT /api/v1/agents/{agent_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "config": {
    "prompt_config": {
      "system_prompt": "更新后的提示词..."
    }
  }
}

响应示例：
{
  "success": true,
  "data": {
    "agent_id": "customer_service_001",
    "status": "updated",
    "updated_at": "2024-01-15T15:30:00Z"
  },
  "message": "智能体更新成功"
}
```

#### 1.5 删除智能体
```http
DELETE /api/v1/agents/{agent_id}
Authorization: Bearer {access_token}

响应示例：
{
  "success": true,
  "message": "智能体删除成功"
}
```

#### 1.6 启动/停止智能体
```http
POST /api/v1/agents/{agent_id}/start
POST /api/v1/agents/{agent_id}/stop
Authorization: Bearer {access_token}

响应示例：
{
  "success": true,
  "data": {
    "agent_id": "customer_service_001",
    "status": "running",
    "started_at": "2024-01-15T16:00:00Z"
  }
}
```

---

### 2. 团队管理

#### 2.1 创建团队
```http
POST /api/v1/teams
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "config": {
    "team_metadata": {
      "team_id": "dev_team_001",
      "team_name": "软件开发团队",
      "collaboration_mode": "SequentialChat",
      "team_goal": "协同完成软件开发项目"
    },
    "agents": [
      {
        "agent_metadata": {
          "agent_id": "product_manager_001",
          "agent_name": "产品经理"
        }
      }
    ],
    "collaboration_config": {
      "speaking_order": ["product_manager_001"],
      "max_conversation_rounds": 30
    }
  }
}
```

#### 2.2 获取团队列表
```http
GET /api/v1/teams?page=1&limit=20&collaboration_mode=SequentialChat
Authorization: Bearer {access_token}
```

#### 2.3 获取团队详情
```http
GET /api/v1/teams/{team_id}
Authorization: Bearer {access_token}
```

---

### 3. 对话管理

#### 3.1 创建对话会话
```http
POST /api/v1/agents/{agent_id}/conversations
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "user_id": "user_123",
  "metadata": {
    "source": "web",
    "user_agent": "Mozilla/5.0..."
  }
}

响应示例：
{
  "success": true,
  "data": {
    "conversation_id": "conv_abc123",
    "agent_id": "customer_service_001",
    "created_at": "2024-01-15T17:00:00Z",
    "status": "active"
  }
}
```

#### 3.2 发送消息
```http
POST /api/v1/conversations/{conversation_id}/messages
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "content": "你好，请问有什么可以帮助您的？",
  "message_type": "text",
  "metadata": {
    "timestamp": "2024-01-15T17:01:00Z"
  }
}

响应示例：
{
  "success": true,
  "data": {
    "message_id": "msg_xyz789",
    "conversation_id": "conv_abc123",
    "content": "您好！很高兴为您服务。有什么我可以帮助您的吗？",
    "role": "assistant",
    "created_at": "2024-01-15T17:01:05Z",
    "tokens_used": {
      "input": 15,
      "output": 25,
      "total": 40
    },
    "response_time": 1.23
  }
}
```

#### 3.3 获取对话历史
```http
GET /api/v1/conversations/{conversation_id}/messages?page=1&limit=50
Authorization: Bearer {access_token}
```

#### 3.4 流式对话 (SSE)
```http
GET /api/v1/conversations/{conversation_id}/stream
Authorization: Bearer {access_token}

响应：Server-Sent Events 流
data: {"token": "您"}
data: {"token": "好"}
data: {"token": "！"}
data: {"done": true, "tokens_used": 25}
```

---

### 4. 配置验证与估算

#### 4.1 验证配置
```http
POST /api/v1/config/validate
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "config": {
    "agent_metadata": {
      "agent_id": "test_agent",
      "agent_name": "测试智能体"
    },
    "model_config": {
      "model_name": "gpt-4o",
      "api_key": "invalid_key"
    }
  }
}

响应示例：
{
  "success": false,
  "data": {
    "valid": false,
    "errors": [
      {
        "field": "model_config.api_key",
        "message": "API密钥格式不正确",
        "severity": "error"
      },
      {
        "field": "prompt_config.system_prompt",
        "message": "系统提示词过短，建议至少100个字符",
        "severity": "warning"
      }
    ],
    "warnings": [
      {
        "field": "model_config.temperature",
        "message": "温度值较高，可能影响输出稳定性",
        "suggestion": "建议使用0.5-0.8之间的值"
      }
    ],
    "quality_score": 6.5
  }
}
```

#### 4.2 成本估算
```http
POST /api/v1/config/estimate-cost
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "config": {
    "model_config": {
      "model_name": "gpt-4o",
      "max_tokens": 2000
    }
  },
  "usage_assumptions": {
    "daily_conversations": 100,
    "avg_turns_per_conversation": 10
  }
}

响应示例：
{
  "success": true,
  "data": {
    "model_name": "gpt-4o",
    "pricing": {
      "input_price": 0.005,
      "output_price": 0.015,
      "currency": "USD"
    },
    "estimates": {
      "per_message": {
        "average_cost": 0.002,
        "min_cost": 0.001,
        "max_cost": 0.005
      },
      "daily": {
        "conversations": 100,
        "tokens": 600000,
        "cost": 2.0
      },
      "monthly": {
        "conversations": 3000,
        "tokens": 18000000,
        "cost": 60.0
      }
    },
    "optimization_tips": [
      {
        "tip": "使用 gpt-4o-mini 可节省70%成本",
        "potential_savings": 42.0
      },
      {
        "tip": "减少 max_tokens 到1000可节省25%成本",
        "potential_savings": 15.0
      }
    ]
  }
}
```

#### 4.3 测试模型连接
```http
POST /api/v1/config/test-connection
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "model_config": {
    "model_name": "gpt-4o",
    "api_key": "sk-proj-xxxxx",
    "base_url": "https://api.openai.com/v1"
  }
}

响应示例：
{
  "success": true,
  "data": {
    "connection_status": "success",
    "response_time": 0.523,
    "model_available": true,
    "test_message": "Connection successful!",
    "timestamp": "2024-01-15T18:00:00Z"
  }
}
```

---

### 5. 模板管理

#### 5.1 获取模板列表
```http
GET /api/v1/templates?type=single_agent&category=客服&difficulty=beginner
Authorization: Bearer {access_token}

响应示例：
{
  "success": true,
  "data": {
    "templates": [
      {
        "template_id": "customer_service_basic",
        "template_name": "智能客服基础版",
        "template_description": "适合初学者的客服智能体模板",
        "template_type": "single_agent",
        "category": "客户服务",
        "difficulty": "beginner",
        "tags": ["客服", "对话", "新手"],
        "thumbnail": "/templates/customer_service.png",
        "popularity": 4.8,
        "usage_count": 1234,
        "created_at": "2024-01-10T00:00:00Z"
      }
    ]
  }
}
```

#### 5.2 获取模板详情
```http
GET /api/v1/templates/{template_id}
Authorization: Bearer {access_token}
```

#### 5.3 从模板创建智能体
```http
POST /api/v1/templates/{template_id}/create
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "customizations": {
    "agent_metadata": {
      "agent_name": "我的智能客服"
    },
    "model_config": {
      "api_key": "sk-proj-xxxxx"
    }
  }
}
```

---

### 6. 监控与统计

#### 6.1 获取智能体统计
```http
GET /api/v1/agents/{agent_id}/statistics?period=7d
Authorization: Bearer {access_token}

响应示例：
{
  "success": true,
  "data": {
    "period": "7d",
    "overview": {
      "total_conversations": 1234,
      "total_messages": 5678,
      "total_tokens_used": 1234567,
      "average_response_time": 2.3,
      "success_rate": 98.5,
      "user_satisfaction": 4.6
    },
    "daily_stats": [
      {
        "date": "2024-01-15",
        "conversations": 145,
        "tokens": 123456,
        "cost": 2.34
      }
    ],
    "top_topics": [
      { "topic": "产品咨询", "count": 456 },
      { "topic": "订单查询", "count": 321 }
    ]
  }
}
```

#### 6.2 获取系统健康状态
```http
GET /api/v1/health
Authorization: Bearer {access_token}

响应示例：
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 1234567,
    "services": {
      "api": "healthy",
      "database": "healthy",
      "redis": "healthy"
    },
    "statistics": {
      "active_agents": 12,
      "active_conversations": 34,
      "requests_per_minute": 120
    }
  }
}
```

---

## 🔐 认证与授权

### 用户认证
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

响应示例：
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "username": "user@example.com",
      "role": "admin"
    }
  }
}
```

### Token刷新
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## ❌ 错误处理

### 标准错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "agent_id",
        "message": "智能体ID不能为空"
      }
    ],
    "timestamp": "2024-01-15T18:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### 常见错误码
| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

---

## 🔄 Webhook 事件

### 事件类型
```json
{
  "event": "conversation.completed",
  "timestamp": "2024-01-15T19:00:00Z",
  "data": {
    "conversation_id": "conv_abc123",
    "agent_id": "customer_service_001",
    "messages": 15,
    "duration": 300,
    "tokens_used": 1234
  }
}
```

### 支持的事件类型
- `conversation.created`: 对话创建
- `conversation.completed`: 对话完成
- `conversation.failed`: 对话失败
- `agent.started`: 智能体启动
- `agent.stopped`: 智能体停止
- `agent.error`: 智能体错误

---

## 📏 限流规则

```http
GET /api/v1/agents
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642260000
```

### 限流规则
- **免费用户**: 100 requests/minute
- **付费用户**: 1000 requests/minute
- **企业用户**: 自定义

---

这个API设计提供了完整的前后端交互规范，支持智能体的全生命周期管理和实时对话功能。您觉得还需要添加哪些功能吗？