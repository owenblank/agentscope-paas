# AgentScope PaaS 配置示例

本目录包含基于模板创建的实际配置示例，帮助您快速理解和使用AgentScope PaaS框架。

## 📁 示例文件

### 1. `simple_chatbot.yaml` - 简单聊天机器人
**难度**: ⭐ 新手入门
**适合**: 第一次使用AgentScope PaaS的用户

**特点**:
- 极简配置，只有60行
- 使用低成本模型（通义千问）
- 基础对话功能
- 无工具调用，无复杂逻辑

**快速开始**:
```bash
# 替换API Key后即可运行
model_config:
  api_key: "sk-your-api-key-here"
```

---

### 2. `customer_service_agent.yaml` - 智能客服助手
**难度**: ⭐⭐ 进阶
**适合**: 需要生产级智能体的开发者

**特点**:
- 完整的单智能体配置
- 集成3个工具（订单查询、产品信息、知识库）
- 包含记忆模块、安全过滤、行为控制
- 客服特定功能（转人工、工作时间、满意度跟踪）

**核心功能**:
```yaml
# 工具集成示例
tool_config:
  tools:
    - tool_id: "order_query"
      tool_name: "订单查询系统"
      tool_type: "api"

# 安全配置
safety_config:
  content_filter: true
  refused_topics:
    - "政治敏感话题"
    - "违法活动咨询"
```

---

### 3. `software_dev_team.yaml` - 软件开发团队
**难度**: ⭐⭐⭐ 高级
**适合**: 需要多智能体协作的复杂场景

**特点**:
- 3个智能体协作（产品经理、架构师、开发者）
- SequentialChat协作模式
- 完整的软件开发流程
- 包含代码生成、执行、审查工具

**团队结构**:
```yaml
agents:
  - 产品经理: 需求分析、任务分解、进度协调
  - 架构师: 系统设计、技术选型、代码审查
  - 开发者: 前后端开发、数据库设计、测试

speaking_order:
  - product_manager_001  # 提出需求
  - architect_001        # 设计架构
  - fullstack_developer_001  # 实现代码
```

**协作流程**:
1. 产品经理分析需求 → 输出PRD文档
2. 架构师设计技术方案 → 输出架构图
3. 开发者实现功能 → 输出代码
4. 循环迭代直到完成

---

## 🚀 使用指南

### 步骤1: 选择合适的示例
- **新手**: 从 `simple_chatbot.yaml` 开始
- **有经验**: 参考 `customer_service_agent.yaml`
- **高级用户**: 研究 `software_dev_team.yaml`

### 步骤2: 配置API密钥
```yaml
# OpenAI示例
model_config:
  model_name: "gpt-4o"
  api_key: "sk-proj-your-openai-key"

# 通义千问示例（推荐新手）
model_config:
  model_name: "qwen-turbo"
  api_key: "sk-your-qwen-key"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Claude示例
model_config:
  model_name: "claude-3-5-sonnet-20241022"
  api_key: "sk-ant-your-claude-key"
```

### 步骤3: 自定义配置
根据需求调整提示词、工具、行为控制等配置项。

### 步骤4: 运行智能体
```bash
# 使用AgentScope PaaS框架加载配置
python -m agentscope.paas run simple_chatbot.yaml
```

---

## 🔧 配置修改指南

### 修改提示词
```yaml
prompt_config:
  system_prompt: |
    你是一个{{你的角色}}
    你的职责是{{你的职责描述}}
```

### 添加新工具
```yaml
tool_config:
  tools:
    - tool_id: "your_tool_id"
      tool_name: "工具名称"
      tool_type: "api"
      description: "工具功能描述"
      tool_config:
        endpoint: "https://api.example.com/endpoint"
```

### 调整智能体行为
```yaml
behavior_config:
  max_conversation_rounds: 20  # 最大对话轮次
  auto_reply: true            # 自动回复
  output_format:
    type: "text"              # 输出格式
```

---

## 📊 示例对比

| 特性 | 简单聊天机器人 | 智能客服 | 开发团队 |
|------|--------------|---------|---------|
| 代码行数 | 60行 | 200行 | 450行 |
| 智能体数量 | 1个 | 1个 | 3个 |
| 工具数量 | 0个 | 3个 | 6个 |
| 配置复杂度 | 简单 | 中等 | 复杂 |
| 适用场景 | 学习对话 | 生产客服 | 项目协作 |
| 预估成本 | 低 | 中等 | 较高 |

---

## 💡 最佳实践

### 1. 从简单开始
建议先运行 `simple_chatbot.yaml`，熟悉配置格式和框架使用。

### 2. 逐步增加功能
在简单示例基础上，逐步添加工具、记忆模块等高级功能。

### 3. 控制成本
- 开发测试期使用低成本模型（如 `qwen-turbo`）
- 生产环境再使用高性能模型（如 `gpt-4`）
- 设置合理的 `max_tokens` 和 `max_conversation_rounds`

### 4. 安全考虑
```yaml
# 启用内容过滤
safety_config:
  content_filter: true

# 设置拒绝话题
refused_topics:
  - "敏感话题"
```

### 5. 监控和日志
```yaml
# 启用对话记录
monitoring_config:
  save_conversation_history: true
  enable_performance_tracking: true
```

---

## 🐛 常见问题

**Q: 为什么智能体没有响应？**
A: 检查API密钥是否正确，网络是否可达，查看日志文件。

**Q: 如何降低成本？**
A: 使用更便宜的模型，减少max_tokens，降低max_conversation_rounds。

**Q: 多智能体团队如何选择协作模式？**
A:
- 固定流程用 `SequentialChat`
- 自由讨论用 `FreeChat`
- 需要管理用 `ManagerProxy`

**Q: 工具配置失败怎么办？**
A: 检查工具的API端点、认证信息、参数配置是否正确。

---

## 📚 进阶学习

1. **工具集成**: 参考 `customer_service_agent.yaml` 学习如何集成外部API
2. **团队协作**: 研究 `software_dev_team.yaml` 了解多智能体协作模式
3. **提示词工程**: 优化 `system_prompt` 提升智能体表现
4. **性能优化**: 调整温度、token数等参数平衡成本和质量

---

## 🎯 下一步

1. ✅ 运行 `simple_chatbot.yaml` 体验基础功能
2. ✅ 修改提示词，创造你自己的对话机器人
3. ✅ 尝试 `customer_service_agent.yaml` 学习工具集成
4. ✅ 探索 `software_dev_team.yaml` 掌握团队协作

祝你使用AgentScope PaaS开发愉快！🎉
