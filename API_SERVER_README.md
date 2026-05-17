# AgentScope PaaS Web API 服务器

基于 FastAPI 和 AgentScope 框架的企业级智能体 PaaS 平台 Web API 服务器。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 2. 启动API服务器

#### 方式一：使用启动脚本（推荐）

```bash
# Linux/Mac
chmod +x start_api_server.sh
./start_api_server.sh

# Windows (Git Bash)
bash start_api_server.sh
```

#### 方式二：直接运行Python模块

```bash
python -m api_server.main
```

#### 方式三：自定义配置

```bash
# 设置端口
export API_PORT=8080

# 设置主机
export API_HOST=127.0.0.1

# 启动服务器
python -m api_server.main
```

### 3. 访问API文档

启动后，访问以下地址查看交互式API文档：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 📋 API端点概览

### 健康检查
- `GET /api/v1/health` - 系统健康检查

### 模板管理
- `GET /api/v1/templates` - 获取模板列表
- `GET /api/v1/templates/{template_id}` - 获取模板详情
- `POST /api/v1/templates/{template_id}/create` - 从模板创建智能体

### 智能体管理
- `GET /api/v1/agents` - 获取智能体列表
- `GET /api/v1/agents/{agent_id}` - 获取智能体详情
- `POST /api/v1/agents` - 创建智能体
- `PUT /api/v1/agents/{agent_id}` - 更新智能体
- `DELETE /api/v1/agents/{agent_id}` - 删除智能体
- `POST /api/v1/agents/{agent_id}/start` - 启动智能体
- `POST /api/v1/agents/{agent_id}/stop` - 停止智能体

### 配置验证
- `POST /api/v1/config/validate` - 验证配置
- `POST /api/v1/config/estimate-cost` - 估算成本
- `POST /api/v1/config/test-connection` - 测试模型连接

### 对话管理
- `POST /api/v1/agents/{agent_id}/conversations` - 创建对话会话
- `GET /api/v1/conversations/{conversation_id}` - 获取对话详情
- `GET /api/v1/conversations/{conversation_id}/messages` - 获取对话消息
- `POST /api/v1/conversations/{conversation_id}/messages` - 发送消息

## 🔧 配置说明

### 智能体配置结构

```json
{
  "agent_metadata": {
    "agent_id": "string",
    "agent_name": "string",
    "agent_type": "DialogAgent",
    "description": "string",
    "version": "1.0.0",
    "tags": ["tag1", "tag2"]
  },
  "model_config": {
    "model_name": "gpt-4o",
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "prompt_config": {
    "system_prompt": "你是一个专业的AI助手...",
    "user_prompt_template": null
  },
  "memory_config": {},
  "tool_config": {},
  "knowledge_config": {},
  "skills_config": {},
  "behavior_config": {},
  "monitoring_config": {}
}
```

## 🧪 测试

### 运行测试脚本

```bash
python test_api_server.py
```

测试脚本将验证以下功能：
1. 健康检查
2. 模板列表获取
3. 智能体创建
4. 智能体列表获取
5. 智能体启动/停止
6. 对话会话创建
7. 消息发送和接收

### 手动测试示例

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 创建智能体
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "agent_metadata": {
        "agent_id": "test_agent",
        "agent_name": "测试智能体",
        "description": "用于测试"
      },
      "model_config": {
        "model_name": "gpt-4o",
        "api_key": "test-key"
      },
      "prompt_config": {
        "system_prompt": "你是一个有帮助的AI助手。"
      }
    }
  }'

# 启动智能体
curl -X POST http://localhost:8000/api/v1/agents/test_agent/start
```

## 🏗️ 架构说明

### 核心组件

1. **FastAPI服务器** (`api_server/main.py`)
   - RESTful API接口
   - 请求验证和响应处理
   - CORS中间件配置

2. **AgentScope集成** (`agentscope_paas/core/engine.py`)
   - 智能体运行引擎
   - 对话处理逻辑
   - 多智能体协作支持

3. **配置管理** (`agentscope_paas/config/loader.py`)
   - YAML配置加载
   - 配置验证
   - 模板管理

### 数据流

```
前端 -> FastAPI -> Engine -> AgentScope -> LLM
  <-       <-         <-         <-
```

## 📁 目录结构

```
agentscope-paas/
├── api_server/
│   └── main.py              # FastAPI服务器
├── agentscope_paas/
│   ├── core/
│   │   └── engine.py        # 运行引擎
│   ├── config/
│   │   └── loader.py        # 配置加载器
│   ├── factory/
│   │   ├── agent_factory.py # 智能体工厂
│   │   └── team_factory.py  # 团队工厂
│   └── utils/
│       ├── logger.py        # 日志工具
│       └── exceptions.py    # 异常定义
├── data/
│   └── agents/              # 智能体配置存储
├── logs/                    # 日志文件
├── requirements.txt         # Python依赖
├── start_api_server.sh      # 启动脚本
└── test_api_server.py       # 测试脚本
```

## 🔐 安全建议

### 生产环境部署

1. **API密钥管理**
   ```bash
   # 使用环境变量
   export OPENAI_API_KEY="your-api-key"
   ```

2. **CORS配置**
   ```python
   # 修改允许的源
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **认证和授权**
   - 添加JWT认证
   - 实现API密钥验证
   - 用户权限管理

4. **数据持久化**
   - 集成数据库（PostgreSQL/MongoDB）
   - 实现配置版本管理
   - 添加数据备份机制

## 🚀 性能优化

### 异步处理
- 使用异步I/O提高并发性能
- 实现消息队列处理长时间任务
- 添加缓存机制减少重复计算

### 监控和日志
- 集成APM工具（如New Relic、DataDog）
- 实现结构化日志记录
- 添加性能指标监控

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 更改端口
   export API_PORT=8080
   python -m api_server.main
   ```

2. **依赖缺失**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt --upgrade
   ```

3. **AgentScope初始化失败**
   ```bash
   # 检查AgentScope安装
   python -c "import agentscope; print(agentscope.__version__)"
   ```

## 📞 支持和贡献

- 问题反馈：[GitHub Issues](https://github.com/your-org/agentscope-paas/issues)
- 文档：[项目文档](https://docs.agentscope-paas.com)
- 社区：[Discord社区](https://discord.gg/agentscope)

## 📄 许可证

[MIT License](LICENSE)