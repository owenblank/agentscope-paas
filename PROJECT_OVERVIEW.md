# AgentScope PaaS 项目总览

## 🎯 项目简介

AgentScope PaaS 是一个零代码智能体开发平台，让用户通过可视化界面配置和部署AI智能体，无需编写任何代码。

### 核心特性
- 🎨 **可视化配置**: 通过Web界面配置智能体，支持拖拽式操作
- 🤖 **多智能体类型**: 支持对话、推理、工具调用等多种智能体类型
- 👥 **团队协作**: 支持多智能体团队协作模式
- 🔄 **实时对话**: 支持流式对话和WebSocket实时通信
- 📊 **监控分析**: 完整的使用统计和性能监控
- 🚀 **一键部署**: 配置完成后自动部署智能体实例

---

## 📁 项目结构

```
agentscope-paas/
├── docs/                           # 📚 项目文档
│   ├── frontend_design_proposal.md # 前端设计方案
│   ├── api_design.md               # API接口设计
│   ├── database_design.md          # 数据库设计
│   └── system_architecture.md      # 系统架构设计
│
├── templates/                      # 📄 配置模板
│   ├── single_agent_paas_template.yaml      # 单智能体模板
│   ├── multi_agent_paas_template.yaml       # 多智能体模板
│   └── single_agent_frontend_optimized.yaml # 前端优化模板
│
├── examples/                       # 🎯 配置示例
│   ├── README.md                   # 示例说明
│   ├── quick_start_guide.md        # 快速开始指南
│   ├── simple_chatbot.yaml         # 简单聊天机器人
│   ├── customer_service_agent.yaml # 智能客服助手
│   └── software_dev_team.yaml      # 软件开发团队
│
└── README.md                       # 📖 项目说明
```

---

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/your-org/agentscope-paas.git
cd agentscope-paas

# 安装依赖
pip install -r requirements.txt
npm install
```

### 2. 配置数据库
```bash
# 启动PostgreSQL
docker-compose up -d db redis

# 运行数据库迁移
python manage.py migrate
```

### 3. 启动服务
```bash
# 启动后端服务
python main.py

# 启动前端服务
npm run dev
```

### 4. 访问应用
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:3000/admin

---

## 📚 核心功能

### 1. 智能体管理
- ✅ 创建智能体 (通过模板或自定义配置)
- ✅ 编辑智能体配置
- ✅ 启动/停止智能体
- ✅ 删除智能体
- ✅ 查看智能体统计

### 2. 对话管理
- ✅ 创建对话会话
- ✅ 发送/接收消息
- ✅ 流式对话 (SSE)
- ✅ 对话历史记录
- ✅ 对话质量评估

### 3. 团队协作
- ✅ 创建智能体团队
- ✅ 配置协作模式
- ✅ 管理团队成员
- ✅ 团队对话监控

### 4. 配置验证
- ✅ 实时配置验证
- ✅ 成本估算
- ✅ 模型连接测试
- ✅ 配置质量评分

---

## 🎨 前端设计

### 页面结构
```
├── 首页 (Dashboard)
│   ├── 数据概览
│   ├── 快速操作
│   └── 最近使用
│
├── 智能体管理
│   ├── 智能体列表
│   ├── 创建智能体 (向导式)
│   └── 智能体详情
│
├── 团队管理
│   ├── 团队列表
│   ├── 创建团队
│   └── 团队监控
│
└── 监控中心
    ├── 使用统计
    ├── 性能监控
    └── 成本分析
```

### 核心组件
- **配置向导**: 分步式智能体创建流程
- **YAML编辑器**: 带语法高亮的配置编辑器
- **实时预览**: 配置效果实时预览
- **成本计算器**: 使用成本实时估算
- **质量评分**: 配置质量智能评估

---

## 🔌 API接口

### RESTful API
- `POST /api/v1/agents` - 创建智能体
- `GET /api/v1/agents` - 获取智能体列表
- `GET /api/v1/agents/{id}` - 获取智能体详情
- `PUT /api/v1/agents/{id}` - 更新智能体
- `DELETE /api/v1/agents/{id}` - 删除智能体
- `POST /api/v1/agents/{id}/start` - 启动智能体
- `POST /api/v1/agents/{id}/stop` - 停止智能体

### WebSocket API
- `/ws/conversations/{id}` - 实时对话连接

详细API文档: [API设计文档](./docs/api_design.md)

---

## 🗄️ 数据库设计

### 核心数据表
- `users` - 用户表
- `agents` - 智能体表
- `teams` - 团队表
- `conversations` - 对话会话表
- `messages` - 消息表
- `templates` - 模板表
- `usage_logs` - 使用记录表

详细数据库设计: [数据库设计文档](./docs/database_design.md)

---

## 🛠️ 技术栈

### 前端
- React 18 + TypeScript
- Ant Design 5 (UI组件库)
- TailwindCSS (样式)
- Zustand (状态管理)
- React Query (数据获取)
- Socket.io (实时通信)

### 后端
- Python 3.10+
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- PostgreSQL (数据库)
- Redis (缓存)
- Celery (任务队列)

### 智能体框架
- AgentScope (智能体框架)
- OpenAI API / Anthropic API / 通义千问

---

## 📖 使用指南

### 新手入门
1. 阅读 [快速开始指南](./examples/quick_start_guide.md)
2. 运行 [简单聊天机器人示例](./examples/simple_chatbot.yaml)
3. 学习 [智能客服助手示例](./examples/customer_service_agent.yaml)

### 进阶使用
1. 研究 [软件开发团队示例](./examples/software_dev_team.yaml)
2. 自定义智能体配置
3. 创建多智能体团队

### 最佳实践
- 参考配置模板和示例
- 使用配置验证功能
- 注意成本控制
- 启用监控日志

---

## 🔄 开发路线图

### Phase 1: MVP (当前)
- ✅ 基础配置模板
- ✅ 单智能体支持
- ✅ Web界面设计
- ✅ API接口设计

### Phase 2: 核心功能
- 🔨 前端界面实现
- 🔨 后端API实现
- 🔨 智能体运行时集成
- 🔨 数据库和缓存

### Phase 3: 高级功能
- 📋 多智能体团队
- 📋 实时对话
- 📋 监控告警
- 📋 成本优化

### Phase 4: 企业功能
- 📋 权限管理
- 📋 多租户支持
- 📋 私有化部署
- 📋 SLA保障

---

## 🤝 贡献指南

### 如何贡献
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 开发规范
- 遵循 PEP 8 代码规范
- 编写单元测试
- 更新相关文档
- 提交前自我审查

---

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/your-org/agentscope-paas)
- 文档: [项目文档](./docs/)
- 问题反馈: [Issues](https://github.com/your-org/agentscope-paas/issues)
- 邮件: support@agentscope-paas.com

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢以下开源项目：
- [AgentScope](https://github.com/modelscope/agentscope) - 智能体框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Ant Design](https://ant.design/) - 企业UI组件库
- [PostgreSQL](https://www.postgresql.org/) - 开源数据库

---

**让我们一起构建零代码AI智能体开发平台！** 🚀
