# AgentScope-PaaS 企业级智能体平台

## 🚀 项目简介

AgentScope-PaaS 是一个**企业级智能体PaaS平台**，基于官方 AgentScope Python 库构建，提供完整的智能体管理、Web界面和API服务。

**核心特性：**
- 🌐 **Web管理界面**：现代化的React前端，支持智能体配置、监控和管理
- 🔌 **REST API服务**：完整的API服务器，支持智能体创建、调用和管理
- 📝 **配置文件驱动**：YAML配置文件，无需编写代码即可创建智能体
- 🤖 **支持所有智能体类型**：ReActAgent、DialogAgent、FunctionCallAgent、ToolAgent
- 👥 **多智能体协作**：支持所有 AgentScope 协作模式
- 🔐 **用户认证系统**：完整的用户注册、登录和权限管理
- 📊 **监控和日志**：实时监控智能体状态，完整的操作日志
- 🎯 **生产级质量**：完整的错误处理、数据验证和安全防护
- 📦 **Skill-Creator 规范对齐**：完全兼容 Claude Code skill-creator 技能规范

---

## 📋 快速开始

### 方式一：Web界面（推荐）

#### 1. 环境准备
确保你的环境满足以下要求：
- Python >= 3.8
- Node.js >= 16
- pip 包管理工具

#### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/owenblank/agentscope-paas.git
cd agentscope-paas

# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

#### 3. 启动服务

**启动API服务器：**
```bash
# 方式1：直接运行
cd api_server
python main.py

# 方式2：使用启动脚本
bash start_api_server.sh
```

**启动前端界面：**
```bash
cd frontend
npm run dev
```

#### 4. 访问界面

- **前端界面**：http://localhost:5173
- **API文档**：http://localhost:8000/docs
- **注册账号**：首次使用请注册新账号

### 方式二：命令行接口

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 使用配置文件
在 `examples/` 目录下选择配置模板：
```bash
# 单智能体配置
cp examples/customer_service_agent.yaml my_agent.yaml

# 多智能体团队配置
cp examples/software_dev_team.yaml my_team.yaml
```

#### 3. 运行智能体
```bash
# 交互模式
python main.py --config my_agent.yaml

# 单次对话
python main.py --config my_agent.yaml --input "你好"
```

---

## 📁 项目结构

```
agentscope-paas/
├── agentscope_paas/           # 框架核心包
│   ├── __init__.py            # 包初始化
│   ├── auth/                  # 认证模块
│   │   ├── middleware.py      # JWT认证中间件
│   │   └── security.py        # 安全工具函数
│   ├── config/                # 配置模块
│   │   ├── loader.py          # YAML配置加载、校验、解析
│   │   └── validator.py       # 配置字段校验
│   ├── factory/               # 智能体工厂
│   │   ├── agent_factory.py   # 单智能体自动创建
│   │   └── team_factory.py    # 多智能体团队创建
│   ├── core/                  # 核心引擎
│   │   ├── engine.py          # 智能体运行引擎
│   │   └── async_chat_processor.py  # 异步对话处理器
│   ├── storage/               # 存储模块
│   │   ├── models.py          # 数据模型
│   │   ├── memory.py          # 内存存储
│   │   └── base.py            # 基础存储接口
│   └── utils/                 # 工具类
│       ├── logger.py          # 日志工具
│       └── exceptions.py      # 自定义异常
├── api_server/                # API服务器
│   ├── main.py                # FastAPI主应用
│   ├── routers/               # API路由
│   │   ├── auth.py            # 认证相关API
│   │   ├── agents.py          # 智能体管理API
│   │   ├── chat.py            # 对话API
│   │   └── monitoring.py      # 监控API
│   ├── data/                  # 数据存储目录
│   └── logs/                  # 日志目录
├── frontend/                  # React前端应用
│   ├── src/                   # 源代码
│   │   ├── components/        # React组件
│   │   ├── pages/             # 页面组件
│   │   ├── services/          # API服务
│   │   └── utils/             # 工具函数
│   ├── public/                # 静态资源
│   ├── package.json           # npm配置
│   └── vite.config.ts         # Vite配置
├── examples/                  # 配置示例
│   ├── customer_service_agent.yaml      # 客服智能体示例
│   ├── simple_chatbot.yaml              # 简单聊天机器人
│   └── software_dev_team.yaml           # 软件开发团队
├── tests/                     # 测试文件
│   ├── test_auth_api.py       # 认证API测试
│   ├── test_storage.py        # 存储测试
│   └── test_security.py       # 安全测试
├── docs/                      # 文档目录
│   ├── system_architecture.md # 系统架构
│   ├── api_design.md          # API设计文档
│   └── database_design.md     # 数据库设计
├── requirements.txt           # Python依赖
├── requirements-dev.txt       # 开发依赖
├── setup.py                   # 安装脚本
└── README.md                  # 项目说明（本文件）
```

---

## 🖥️ 界面展示

### 用户认证界面

#### 登录页面
![Login Page](docs/screenshots/01_login_page.png)

#### 注册页面
![Register Page](docs/screenshots/02_register_page.png)

### 智能体管理界面

#### 智能体列表页
![Agent List](docs/screenshots/06_agent_list_detailed.png)

#### 创建智能体界面
![Create Agent Interface](docs/screenshots/07_create_agent_interface.png)

### 对话交互界面

#### 智能体聊天界面
![Chat Interface](docs/screenshots/08_chat_interface.png)

### 系统监控界面

#### 仪表板
![Dashboard](docs/screenshots/05_dashboard.png)

## 🎯 核心功能

### 1. Web管理界面
- **智能体管理**：通过Web界面创建、编辑、删除智能体
- **实时对话**：与智能体进行实时对话交互
- **监控仪表板**：查看智能体运行状态和性能指标
- **用户认证**：完整的用户注册、登录系统
- **响应式设计**：支持桌面和移动设备

### 2. REST API服务
- **智能体API**：创建、更新、删除、查询智能体
- **对话API**：发送消息、获取回复、管理对话历史
- **认证API**：用户注册、登录、token刷新
- **监控API**：获取系统状态、日志和性能指标
- **Swagger文档**：自动生成的API文档

### 3. 配置文件驱动
通过 YAML 配置文件定义智能体的所有属性：

```yaml
agent_metadata:
  agent_id: "customer_service_001"
  agent_name: "智能客服助手"
  agent_type: "ReActAgent"
  description: "24小时在线智能客服"

model_config:
  model_name: "gpt-4"
  api_key: "sk-xxx"
  base_url: "https://api.openai.com/v1"
```

### 4. 智能体类型支持
- **ReActAgent**：推理行动智能体，支持复杂推理和工具调用
- **DialogAgent**：对话智能体，适合基础对话场景
- **FunctionCallAgent**：函数调用智能体，支持外部API调用
- **ToolAgent**：工具智能体，专注于工具调用和任务执行

### 5. 多智能体协作模式
- **SequentialChat**：顺序对话，智能体按固定顺序轮流发言
- **RoundRobinChat**：轮询对话，智能体循环轮流发言
- **ManagerProxy**：管理者代理，由管理者智能体分配任务
- **FreeChat**：自由对话，智能体自由参与讨论

### 6. 企业级功能
- ✅ **用户认证**：JWT认证、密码加密、会话管理
- ✅ **数据存储**：用户数据、智能体配置、对话历史持久化
- ✅ **API安全**：CORS配置、请求验证、速率限制
- ✅ **日志系统**：操作日志、错误日志、访问日志
- ✅ **监控告警**：系统状态监控、异常告警
- ✅ **记忆模块**：短期记忆、长期记忆、向量记忆
- ✅ **技能系统**：前端上传技能配置（对齐skill-creator规范）

---

## 🔧 配置指南

### 单智能体配置要点

#### 必填字段
1. **agent_metadata**
   - agent_id: 智能体唯一标识（小写字母、数字、下划线）
   - agent_name: 智能体显示名称
   - agent_type: 智能体类型
   - description: 智能体功能描述
   - version: 版本号

2. **model_config**
   - model_name: 模型名称
   - api_key: API密钥
   - base_url: API基础地址

3. **prompt_config**
   - system_prompt: 系统提示词（角色定义和行为准则）

#### 可选字段
- memory_config: 记忆模块配置
- knowledge_config: 知识库配置
- **skills_config**: 技能配置
- tool_config: 工具调用配置
- behavior_config: 行为控制配置
- monitoring_config: 监控配置

### 多智能体团队配置要点

#### 必填字段
1. **team_metadata**
   - team_id: 团队唯一标识
   - team_name: 团队名称
   - collaboration_mode: 协作模式
   - team_goal: 团队任务目标
   - termination_conditions: 终止条件

2. **agents**
   - 至少包含一个智能体的完整配置

3. **collaboration_config**
   - initial_speaker: 初始发言者

---

## 💡 技能系统（对齐skill-creator规范）

AgentScope-PaaS 完全对齐 **Claude Code skill-creator 规范**，支持三种技能上传方式：

### 支持的技能上传方式

#### 1. 单个 SKILL.md 文件（推荐）
```yaml
skills_config:
  upload_config:
    supported_upload_methods:
      - method: "single_file"
        max_size_mb: 3
        skill_md_requirements:
          require_frontmatter: true
          required_frontmatter_fields: ["name", "description"]
```

**SKILL.md 示例**：
```markdown
---
name: data-analyzer
description: Use this skill whenever the user asks for data analysis, statistics, or data visualization.
version: 1.0.0
---

# 数据分析技能

## 功能描述
此技能用于分析数据文件并生成统计报告和可视化图表。
```

#### 2. 文件夹上传（复杂技能）
```
skill-folder/
├── SKILL.md              # 必需
├── scripts/              # 可选：可执行脚本
├── references/           # 可选：参考文档
└── assets/               # 可选：资源文件
```

#### 3. ZIP 压缩包（技能打包）
- 支持完整的 skill-creator 目录结构
- 适合技能版本控制和分发
- 自动解压和验证

### 技能配置限制

- **文件大小**：单个文件 ≤ 3MB
- **文件数量**：文件夹 ≤ 20 个，ZIP ≤ 50 个
- **格式要求**：必须符合 skill-creator 规范
- **安全验证**：恶意代码扫描、结构验证

**详细文档**：请参阅 [docs/SKILL_CONFIG_GUIDE.md](docs/SKILL_CONFIG_GUIDE.md)

---

## 💡 使用示例

### 示例1：创建智能客服

```yaml
# customer_service.yaml
agent_metadata:
  agent_id: "customer_service_001"
  agent_name: "智能客服助手"
  agent_type: "ReActAgent"
  description: "24小时在线智能客服，提供产品咨询、订单查询服务"
  version: "1.0.0"

model_config:
  model_name: "gpt-4o"
  api_key: "your-api-key"
  base_url: "https://api.openai.com/v1"
  temperature: 0.7
  max_tokens: 1500

prompt_config:
  system_prompt: |
    你是一个专业的客户服务代表，为用户提供优质的售前售后服务。

    你的职责：
    1. 产品咨询：详细介绍产品功能、规格、价格等信息
    2. 订单查询：帮助用户查询订单状态、物流信息
    3. 售后支持：处理退换货、投诉、技术问题等

    服务原则：
    - 始终保持专业、友好、耐心的态度
    - 快速响应用户需求，不推诿责任
    - 保护用户隐私，不泄露任何个人信息
```

运行：
```bash
python main.py --config customer_service.yaml
```

### 示例2：创建开发团队

```yaml
# dev_team.yaml
team_metadata:
  team_id: "dev_team_001"
  team_name: "软件开发协作团队"
  collaboration_mode: "SequentialChat"
  team_goal: "协同完成用户需求分析、方案设计和代码实现"
  termination_conditions:
    max_rounds: 30
    success_criteria:
      - "产出完整的技术方案文档"
      - "代码实现完成并通过测试"

agents:
  # 产品经理
  - agent_metadata:
      agent_id: "pm_001"
      agent_name: "项目经理"
      agent_type: "DialogAgent"
      description: "负责协调团队工作，分配任务，跟踪进度"
    # ... 其他配置

  # 架构师
  - agent_metadata:
      agent_id: "architect_001"
      agent_name: "架构师"
      agent_type: "ReActAgent"
      description: "负责系统架构设计和技术方案评审"
    # ... 其他配置

collaboration_config:
  speaking_order:
    - "pm_001"
    - "architect_001"
  initial_speaker: "pm_001"
```

运行：
```bash
python main.py --config dev_team.yaml --task "设计一个用户认证系统"
```

---

## 🛠️ 故障排查

### 常见问题

#### 1. 导入错误
```
ImportError: No module named 'agentscope'
```
**解决方法**：
```bash
pip install agentscope>=1.0.19
```

#### 2. 配置文件格式错误
```
YAML文件解析失败
```
**解决方法**：
- 检查YAML语法（缩进、冒号、引号）
- 使用在线YAML验证器验证格式
- 参考配置模板

#### 3. API调用失败
```
模型配置错误: API Key无效
```
**解决方法**：
- 检查API Key是否正确
- 确认base_url地址正确
- 检查网络连接

#### 4. 智能体无响应
```
智能体回复为空
```
**解决方法**：
- 检查system_prompt是否清晰完整
- 确认模型配置正确
- 增加temperature参数提高回复多样性

### 调试技巧

#### 启用调试日志
```bash
python main.py --config configs/my_agent.yaml --log-level DEBUG
```

#### 保存日志到文件
```bash
python main.py --config configs/my_agent.yaml --log-file logs/agent.log
```

#### 查看配置信息
```bash
python main.py --config configs/my_agent.yaml --info
```

---

## 🔮 高级用法

### 1. 自定义工具集成

在配置文件中添加工具调用：

```yaml
tool_config:
  tools:
    - tool_id: "web_search"
      tool_name: "网络搜索"
      tool_type: "api"
      description: "在互联网上搜索最新信息"
      tool_config:
        endpoint: "https://api.example.com/search"
        method: "POST"
```

### 2. 知识库配置

配置平台知识库：

```yaml
knowledge_config:
  platform_knowledge:
    enabled: true
    platform_url: "https://knowledge.example.com/api/v1"
    connection_config:
      authentication:
        type: "bearer_token"
        token: "your-token"
    retrieval_config:
      retrieval_mode: "semantic"
      similarity_threshold: 0.75
      top_k: 5
```

### 3. 技能配置（skill-creator规范）

配置技能上传：

```yaml
skills_config:
  load_mode: "upload"
  upload_config:
    supported_upload_methods:
      - method: "single_file"
        max_size_mb: 3
        supported_formats: [".md"]
        skill_md_requirements:
          require_frontmatter: true
          required_frontmatter_fields: ["name", "description"]
          require_markdown_body: true
          max_recommended_lines: 500

    validation_config:
      validate_frontmatter: true
      validate_markdown: true
      validate_schema: true

      frontmatter_validation:
        name_pattern: "^[a-z0-9-]+$"
        description_min_length: 50
        description_max_length: 500
        require_trigger_info: true
```

---

## 📚 参考文档

### 官方文档
- [AgentScope 官方文档](https://github.com/modelscope/agentscope)
- [技能配置详细指南](./docs/SKILL_CONFIG_GUIDE.md)
- [配置文件完整说明](./configs/single_agent_paas_template.yaml)
- [多智能体协作说明](./configs/multi_agent_paas_template.yaml)

### 相关链接
- AgentScope GitHub: https://github.com/modelscope/agentscope
- Python YAML 文档: https://pyyaml.org/wiki
- skill-creator 规范: https://github.com/anthropics/claude-code-skill-creator

---

## 🤝 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

## 📞 联系方式

- 项目主页：[AgentScope-PaaS](https://github.com/owenblank/agentscope-paas)
- 问题反馈：[Issues](https://github.com/owenblank/agentscope-paas/issues)
- 在线演示：访问 http://your-domain.com （请部署后替换）

---

## 📊 项目状态

当前版本：v1.0.0
最后更新：2025年1月
维护状态：✅ 活跃维护中

**技术栈：**
- 后端：Python 3.8+ / FastAPI / AgentScope
- 前端：React 18 / TypeScript / Vite / Ant Design
- 认证：JWT / bcrypt
- 数据存储：JSON文件 / SQLite（可扩展至PostgreSQL）
- API文档：Swagger/OpenAPI

---

**维护者**：AgentScope PaaS Team
**许可证**：MIT License