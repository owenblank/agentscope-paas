# AgentScope PaaS 数据库设计

## 📊 数据库架构

### 技术选型
- **主数据库**: PostgreSQL 14+ (关系型数据)
- **缓存层**: Redis 7+ (会话状态、实时数据)
- **文档存储**: MongoDB (可选，用于非结构化数据)
- **时序数据**: InfluxDB (可选，用于监控指标)

---

## 🗃️ 数据表设计

### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    avatar_url VARCHAR(500),
    role VARCHAR(50) DEFAULT 'user', -- 'admin', 'user', 'enterprise'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'suspended', 'deleted'
    subscription_tier VARCHAR(50) DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    api_quota_daily INTEGER DEFAULT 100,
    api_quota_monthly INTEGER DEFAULT 3000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    email_verified BOOLEAN DEFAULT false,
    phone VARCHAR(20),
    settings JSONB DEFAULT '{}' -- 用户偏好设置
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
```

### 2. API密钥表 (api_keys)
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(10) NOT NULL, -- 'sk-proj' for display
    name VARCHAR(100) NOT NULL,
    description TEXT,
    scopes TEXT[] DEFAULT ARRAY['read', 'write'],
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

### 3. 智能体表 (agents)
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id VARCHAR(100) UNIQUE NOT NULL, -- 业务ID
    agent_name VARCHAR(200) NOT NULL,
    agent_type VARCHAR(50) NOT NULL, -- 'DialogAgent', 'FunctionCallAgent', etc.
    description TEXT,
    version VARCHAR(50) DEFAULT '1.0.0',
    tags TEXT[] DEFAULT ARRAY[],
    config YAML NOT NULL, -- 完整的YAML配置
    status VARCHAR(50) DEFAULT 'created', -- 'created', 'running', 'stopped', 'error'

    -- 模型配置摘要
    model_name VARCHAR(100) NOT NULL,
    model_provider VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'qwen'

    -- 统计信息
    total_conversations INTEGER DEFAULT 0,
    total_tokens_used BIGINT DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0.0,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    stopped_at TIMESTAMP,

    -- 元数据
    config_file_path VARCHAR(500),
    last_backup_at TIMESTAMP
);

CREATE INDEX idx_agents_user_id ON agents(user_id);
CREATE INDEX idx_agents_agent_id ON agents(agent_id);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_model_provider ON agents(model_provider);
CREATE INDEX idx_agents_created_at ON agents(created_at);

-- 全文搜索索引
CREATE INDEX idx_agents_name_gin ON agents USING gin(to_tsvector('english', agent_name));
CREATE INDEX idx_agents_tags_gin ON agents USING gin(tags);
```

### 4. 团队表 (teams)
```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id VARCHAR(100) UNIQUE NOT NULL,
    team_name VARCHAR(200) NOT NULL,
    collaboration_mode VARCHAR(50) NOT NULL, -- 'SequentialChat', 'RoundRobinChat', etc.
    description TEXT,
    team_goal TEXT,
    version VARCHAR(50) DEFAULT '1.0.0',
    config YAML NOT NULL,
    status VARCHAR(50) DEFAULT 'created',

    -- 统计信息
    total_conversations INTEGER DEFAULT 0,
    total_agents INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP
);

CREATE INDEX idx_teams_user_id ON teams(user_id);
CREATE INDEX idx_teams_team_id ON teams(team_id);
CREATE INDEX idx_teams_collaboration_mode ON teams(collaboration_mode);
```

### 5. 团队成员关联表 (team_agents)
```sql
CREATE TABLE team_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    role_in_team VARCHAR(100), -- 'product_manager', 'architect', etc.
    speaking_order INTEGER,
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(team_id, agent_id)
);

CREATE INDEX idx_team_agents_team_id ON team_agents(team_id);
CREATE INDEX idx_team_agents_agent_id ON team_agents(agent_id);
```

### 6. 对话会话表 (conversations)
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL, -- 可选，团队对话
    user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- 可选，匿名用户为NULL
    conversation_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'failed', 'archived'

    -- 会话统计
    total_messages INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0.0,
    average_response_time DECIMAL(5, 2),

    -- 用户反馈
    user_satisfaction INTEGER, -- 1-5 stars
    user_feedback TEXT,

    -- 元数据
    metadata JSONB DEFAULT '{}',
    source VARCHAR(50), -- 'web', 'api', 'mobile'
    user_agent TEXT,
    ip_address INET,

    -- 时间戳
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_agent_id ON conversations(agent_id);
CREATE INDEX idx_conversations_conversation_id ON conversations(conversation_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_started_at ON conversations(started_at);
```

### 7. 消息表 (messages)
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_id VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text', -- 'text', 'image', 'audio', etc.

    -- Token使用
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,

    -- 性能指标
    response_time DECIMAL(5, 3), -- 响应时间（秒）
    model_version VARCHAR(100),

    -- 工具调用（如果有）
    tool_calls JSONB, -- 存储工具调用信息
    tool_call_results JSONB,

    -- 元数据
    metadata JSONB DEFAULT '{}',

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_message_id ON messages(message_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- 分区表（按月分区）
-- CREATE TABLE messages_2024_01 PARTITION OF messages
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 8. 模板表 (templates)
```sql
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    template_description TEXT,
    template_type VARCHAR(50) NOT NULL, -- 'single_agent', 'multi_agent'
    category VARCHAR(100),
    difficulty VARCHAR(50), -- 'beginner', 'intermediate', 'advanced'
    tags TEXT[] DEFAULT ARRAY[],

    -- 模板配置
    config YAML NOT NULL,
    screenshot_url VARCHAR(500),
    demo_url VARCHAR(500),

    -- 统计信息
    usage_count INTEGER DEFAULT 0,
    popularity_score DECIMAL(3, 2) DEFAULT 0.0,
    user_rating DECIMAL(3, 2),

    -- 创建者信息
    created_by UUID REFERENCES users(id),
    is_official BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_templates_template_id ON templates(template_id);
CREATE INDEX idx_templates_type ON templates(template_type);
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_popularity ON templates(popularity_score DESC);
```

### 9. 使用记录表 (usage_logs)
```sql
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,

    -- 使用统计
    tokens_used INTEGER DEFAULT 0,
    cost DECIMAL(10, 6) DEFAULT 0.0,
    model_provider VARCHAR(50),
    model_name VARCHAR(100),

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 分区优化
    date DATE DEFAULT CURRENT_DATE
);

CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_agent_id ON usage_logs(agent_id);
CREATE INDEX idx_usage_logs_date ON usage_logs(date);

-- 分区表（按月分区）
-- CREATE TABLE usage_logs_2024_01 PARTITION OF usage_logs
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 10. 监控指标表 (monitoring_metrics)
```sql
CREATE TABLE monitoring_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20, 6) NOT NULL,
    metric_unit VARCHAR(50), -- 'ms', 'tokens', 'count', etc.
    labels JSONB DEFAULT '{}', -- 额外的标签信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_monitoring_metrics_agent_id ON monitoring_metrics(agent_id);
CREATE INDEX idx_monitoring_metrics_metric_name ON monitoring_metrics(metric_name);
CREATE INDEX idx_monitoring_metrics_created_at ON monitoring_metrics(created_at);

-- 时序数据优化（考虑使用TimescaleDB扩展）
-- CREATE INDEX idx_monitoring_metrics_agent_time
-- ON monitoring_metrics(agent_id, created_at DESC);
```

### 11. 文件存储表 (file_storage)
```sql
CREATE TABLE file_storage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64), -- SHA256 hash

    -- 关联信息
    related_id UUID, -- 关联的资源ID
    related_type VARCHAR(50), -- 'agent_avatar', 'conversation_attachment', etc.

    -- 存储信息
    storage_provider VARCHAR(50) DEFAULT 'local', -- 'local', 's3', 'oss'
    storage_metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_file_storage_user_id ON file_storage(user_id);
CREATE INDEX idx_file_storage_related_id ON file_storage(related_id);
```

---

## 🔄 Redis 缓存设计

### 缓存键设计规范
```
# 用户会话
user:session:{user_id} -> Hash
  - user_data: JSON
  - permissions: Array
  - expires_at: Timestamp

# 智能体状态
agent:status:{agent_id} -> Hash
  - status: String
  - current_conversations: Integer
  - last_activity: Timestamp

# 对话上下文
conversation:context:{conversation_id} -> Hash
  - messages: Array
  - metadata: JSON
  - ttl: 3600 (1小时)

# 限流计数器
rate_limit:user:{user_id}:{endpoint} -> String (计数)
  - TTL: 60 (每分钟重置)

# 实时统计
stats:agent:daily:{agent_id}:{date} -> Hash
  - conversations: Integer
  - tokens: Integer
  - cost: Decimal
```

---

## 📈 数据库视图

### 智能体概览视图
```sql
CREATE VIEW agent_overview AS
SELECT
    a.id,
    a.agent_id,
    a.agent_name,
    a.agent_type,
    a.status,
    a.model_name,
    a.total_conversations,
    a.total_tokens_used,
    a.total_cost,
    u.username as owner_name,
    u.email as owner_email,
    COUNT(DISTINCT c.id) as active_conversations,
    AVG(c.average_response_time) as avg_response_time,
    a.created_at,
    a.updated_at
FROM agents a
LEFT JOIN users u ON a.user_id = u.id
LEFT JOIN conversations c ON a.id = c.agent_id AND c.status = 'active'
GROUP BY a.id, u.id;
```

### 用户使用统计视图
```sql
CREATE VIEW user_usage_stats AS
SELECT
    u.id as user_id,
    u.username,
    u.email,
    u.subscription_tier,
    COUNT(DISTINCT a.id) as total_agents,
    COUNT(DISTINCT c.id) as total_conversations,
    SUM(ul.tokens_used) as total_tokens,
    SUM(ul.cost) as total_cost,
    MAX(c.created_at) as last_activity
FROM users u
LEFT JOIN agents a ON u.id = a.user_id
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN usage_logs ul ON u.id = ul.user_id
GROUP BY u.id;
```

---

## 🔄 数据迁移策略

### 版本控制
```sql
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rollback_script TEXT
);

-- 示例迁移记录
INSERT INTO schema_migrations (version, description) VALUES
('001', 'Initial schema creation'),
('002', 'Add user preferences field'),
('003', 'Create monitoring metrics table');
```

---

## 💾 备份策略

### 定期备份
```bash
# 每日完整备份
pg_dump -U postgres agentscope_paas > backup_$(date +%Y%m%d).sql

# 增量备份（WAL归档）
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

### Redis 持久化
```conf
# RDB快照
save 900 1
save 300 10
save 60 10000

# AOF持久化
appendonly yes
appendfsync everysec
```

---

这个数据库设计提供了完整的数据存储方案，支持智能体的全生命周期管理和性能优化。您觉得还需要添加哪些表或功能吗？