# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

AgentScope-PaaS 是一个企业级智能体平台，提供配置驱动的智能体创建和管理功能。它将 AgentScope 框架转换为 PaaS（平台即服务）解决方案，具备 Web 界面、REST API 和多智能体协作支持。

**核心架构理念**：系统围绕配置驱动方法构建，YAML 文件定义智能体行为，工厂模式自动实例化 AgentScope 智能体，无需编写代码。

## 核心开发命令

### 后端开发
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest                          # 运行所有测试
pytest tests/                   # 仅运行单元测试
pytest e2e/                     # 运行端到端测试
pytest -k "test_auth"           # 运行特定测试模式
pytest -v --tb=short           # 详细输出和简短回溯

# 代码质量
black .                         # 格式化代码
isort .                         # 排序导入
flake8 .                        # 代码检查
mypy agentscope_paas/          # 类型检查

# 运行 API 服务器
cd api_server && python main.py            # 启动 API 服务器
uvicorn api_server.main:app --reload      # 开发时热重载
```

### 前端开发
```bash
cd frontend
npm install                     # 安装依赖
npm run dev                     # 启动开发服务器 (Vite)
npm run build                   # 生产环境构建
npm run lint                    # TypeScript 代码检查
npm run lint:fix                # 修复检查问题
```

### 全栈测试
```bash
# 运行完整测试套件
./run_tests.sh                  # Linux/Mac
./run_tests.bat                 # Windows

# 端到端测试
cd e2e && python main_test_runner.py quick           # 快速测试
cd e2e && python main_test_runner.py e2e             # 完整 E2E 测试
cd e2e && python main_test_runner.py all             # 所有测试套件
```

## 架构概览

### 配置驱动的工厂模式
系统的核心哲学是"配置优于代码"。用户不需要编写 Python 代码创建智能体，而是在 YAML 文件中定义智能体行为，框架处理实例化。

**核心组件**：
1. **ConfigLoader** (`agentscope_paas/config/loader.py`)：加载和验证 YAML 配置
2. **ConfigValidator** (`agentscope_paas/config/validator.py`)：验证配置结构和值
3. **AgentFactory** (`agentscope_paas/factory/agent_factory.py`)：从配置创建 AgentScope 智能体
4. **TeamFactory** (`agentscope_paas/factory/team_factory.py`)：从配置创建多智能体团队
5. **Engine** (`agentscope_paas/core/engine.py`)：智能体和团队的统一执行引擎

### 数据流架构
```
YAML 配置 → ConfigLoader → ConfigValidator → 工厂模式 → AgentScope 对象 → API/Web 界面
```

**关键洞察**：配置系统必须保持与 AgentScope 原生 API 的向后兼容性，同时添加 PaaS 功能。添加新配置选项（如 `context_compression_config`）时，必须将其作为 `AgentConfig` 模型中的可选字段集成，并由工厂模式正确处理。

### 存储抽象层
认证系统使用抽象存储接口 (`agentscope_paas/storage/base.py`)，支持多种实现：
- **MemoryStorage**：开发/测试用的内存存储
- **SQLiteStorage**：持久化文件存储
- **PostgreSQLStorage**：生产数据库存储

**重要**：存储层通过依赖注入中间件 (`agentscope_paas/auth/middleware.py`) 注入。修改认证相关代码时，确保与所有存储实现兼容。

### API 服务器结构
FastAPI 服务器 (`api_server/main.py`) 使用模块化路由器组织：
- **auth_router**：用户注册、登录、令牌管理
- **agents_router**：智能体 CRUD 操作（尚未实现）
- **chat_router**：对话管理（尚未实现）
- **monitoring_router**：系统监控（尚未实现）

**注意**：当前 API 服务器有占位符实现。添加新端点时，遵循 `auth_router.py` 中的现有模式处理请求/响应模型和错误处理。

### 前端架构
React 前端使用现代技术栈，通过 Zustand 进行状态管理：
- **agentFormStore**：多步骤智能体创建表单，包含完整的 `AgentConfig` 状态
- **类型安全**：所有 API 响应使用 `@/types/agent.ts` 中的 TypeScript 接口
- **服务层**：API 调用集中在 `@/services/` 目录
- **组件架构**：Ant Design 组件与自定义包装器

**关键集成点**：添加新配置字段（如 `context_compression_config`）时，需要更新：
1. `frontend/src/types/agent.ts` - 添加 TypeScript 接口
2. `frontend/src/store/agentFormStore.ts` - 添加到初始表单数据
3. `frontend/src/components/Agent/` - 如需要，添加表单组件
4. `api_server/main.py` - 添加到 Pydantic 模型
5. `agentscope_paas/config/loader.py` - 如需要，添加 getter 方法

## 配置系统最佳实践

### 添加新配置选项
1. **从 TypeScript 接口开始** - 在 `frontend/src/types/agent.ts` 中定义
2. **添加到 AgentConfig 模型** - 在 `api_server/main.py` 中作为 Optional 字段
3. **更新表单存储** - 在 `frontend/src/store/agentFormStore.ts` 中更新初始数据
4. **添加 ConfigLoader 方法** - 如需要复杂验证/加载
5. **创建配置示例** - 在 `examples/` 目录中创建
6. **更新文档** - 更新 README.md 并创建指南

### 配置文件结构
```yaml
agent_metadata: {...}          # 必填：基础智能体信息
model_config: {...}            # 必填：大模型配置
prompt_config: {...}           # 必填：系统提示词
context_compression_config: {...}  # 可选：上下文管理
memory_config: {...}           # 可选：记忆设置
tool_config: {...}             # 可选：工具集成
knowledge_config: {...}        # 可选：知识库
skills_config: {...}           # 可选：技能上传
behavior_config: {...}         # 可选：行为控制
monitoring_config: {...}       # 可选：监控设置
```

**关键原则**：所有新配置都应该是可选的，向后兼容。没有新配置的现有智能体应该正常工作。

## 测试策略

### 测试组织
- **tests/**：单元测试
- **e2e/**：端到端集成测试
- **pytest.ini**：配置测试发现和标记

### 测试标记
```bash
pytest -m unit              # 仅单元测试
pytest -m integration       # 仅集成测试
pytest -m e2e              # 仅端到端测试
pytest -m "not slow"        # 排除慢速测试
```

### 测试模式
遵循 `tests/test_auth_api.py` 中的现有模式：
1. 使用 pytest 夹具进行设置/清理
2. 模拟外部依赖（API 调用、数据库）
3. 测试成功和失败情况
4. 包含边界情况和验证错误

## 关键依赖和约束

### AgentScope 版本约束
```python
agentscope~=1.0.19  # 固定到 1.0.x 系列以保持兼容性
```

**关键**：框架依赖 AgentScope 1.0.x API。升级到 2.0+ 需要对工厂模式和引擎逻辑进行重大重构。

### Python 版本支持
- **最低版本**：Python 3.8
- **目标版本**：Python 3.8-3.11
- **测试环境**：Python 3.10（主要开发环境）

### 前端约束
- **构建工具**：Vite（需要 Node.js 16+）
- **TypeScript**：启用严格模式
- **UI 框架**：Ant Design 5.x
- **状态管理**：Zustand（不使用 Redux）

## 重要文件位置

### 配置模板
- `examples/simple_chatbot.yaml` - 最小工作示例
- `examples/customer_service_agent.yaml` - 复杂真实场景示例
- `examples/agent_with_compression.yaml` - 上下文压缩集成示例

### 入口点
- `agentscope_paas/cli.py` - CLI 接口（尚未实现）
- `api_server/main.py` - FastAPI 服务器入口点
- `frontend/src/main.tsx` - React 应用入口点

### 关键集成点
- `agentscope_paas/config/loader.py:356` - `get_context_compression_config()` 方法
- `api_server/main.py:99` - `AgentConfig` 模型定义
- `frontend/src/types/agent.ts:470` - `ContextCompressionConfig` 接口
- `frontend/src/store/agentFormStore.ts:118` - 表单状态初始化

## 开发工作流

### 进行配置更改
1. **从示例开始** - 首先更新 `examples/`
2. **更新类型** - 修改 TypeScript 和 Pydantic 模型
3. **更新表单** - 如需要，添加表单组件
4. **本地测试** - 使用前端开发服务器和 API 服务器
5. **运行 E2E 测试** - 验证完整集成
6. **更新文档** - 记录新功能

### 调试配置问题
1. **检查 ConfigValidator** - 查看 `agentscope_paas/config/validator.py`
2. **验证 YAML 语法** - 使用在线 YAML 验证器
3. **检查智能体工厂日志** - 工厂模式记录详细创建信息
4. **测试最小配置** - 从 `simple_chatbot.yaml` 开始

### 处理 AgentScope 集成
调试 AgentScope 相关问题时：
1. **检查导入** - 框架为缺少 AgentScope 安装提供了回退
2. **验证模型兼容性** - AgentScope 模型需要特定格式化器
3. **手动测试配置** - 使用 AgentScope CLI 验证配置工作
4. **检查工厂日志** - AgentFactory 记录详细创建过程

## 常见模式

### 添加新智能体类型
1. 在 `api_server/main.py` 的 `AgentConfig` 模型中添加类型
2. 更新 `AgentFactory.create_model()` 处理新模型类型
3. 在 `ConfigValidator` 中添加配置验证
4. 在 `examples/` 中创建配置示例
5. 更新前端类型定义

### API 错误处理
遵循 `auth_router.py` 中的模式：
```python
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="具体错误信息"
)
```

### 前端状态更新
始终使用存储方法：
```typescript
updateFormData({ context_compression_config: newConfig })
```

这确保正确的状态管理和响应性。

## 部署考虑

### 生产配置
- 在 `api_server/main.py` 中设置 `DEBUG=False`
- 使用环境变量处理敏感数据
- 配置正确的 CORS 源
- 启用数据库存储而非内存存储
- 设置适当的日志和监控

### 数据库迁移
存储抽象允许通过配置轻松切换存储后端，当前未实现数据库迁移系统。

## 上下文压缩配置集成

### 集成架构
上下文压缩配置作为智能体配置的标准组成部分集成：
- **前端类型**：`frontend/src/types/agent.ts:470-498` 定义 `ContextCompressionConfig` 接口
- **后端模型**：`api_server/main.py:99` 在 `AgentConfig` 中包含 `context_compression_config`
- **状态管理**：`frontend/src/store/agentFormStore.ts:118-162` 包含完整表单状态
- **配置加载**：`agentscope_paas/config/loader.py:356` 提供 `get_context_compression_config()` 方法

### 参数传递链路
完整的前端到后端参数传递：
```
用户表单输入 → agentFormStore.updateFormData() → agentService.createAgent() →
POST /api/v1/agents → AgentConfig.context_compression_config →
save_agent_config() → data/agents/{agent_id}.json
```

### 验证测试
- **自动化验证**：运行 `python verify_compression_integration.py` 进行完整集成验证
- **真实场景测试**：运行 `python test_compression_real_simple.py` 进行功能测试
- **配置示例**：参考 `examples/agent_with_compression.yaml` 获取完整配置示例

### 配置指南
详细的配置和使用指南请参考：
- **集成指南**：`AGENT_CONFIG_COMPRESSION_GUIDE.md`
- **成功报告**：`COMPRESSION_INTEGRATION_SUCCESS_REPORT.md`
- **示例配置**：`examples/` 目录下的各种场景示例