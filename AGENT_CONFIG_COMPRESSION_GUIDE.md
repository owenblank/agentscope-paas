# AgentScope PaaS 智能体配置中的上下文压缩集成指南

## 📋 概述

上下文压缩配置是 AgentScope PaaS 智能体配置的**标准组成部分**，与其他配置项（如 `model_config`、`prompt_config`、`memory_config`）并列，作为智能体配置的顶级配置项。本指南说明如何在智能体配置中正确集成和使用上下文压缩功能。

## 🎯 配置集成方式

### 1. 配置文件结构

上下文压缩配置作为智能体配置的**顶级配置项**，与其他标准配置项并列：

```yaml
# ============================================
# 标准智能体配置结构
# ============================================
agent_metadata: {...}          # 智能体元信息（必填）
model_config: {...}            # 模型配置（必填）
prompt_config: {...}           # 提示词配置（必填）
context_compression_config: {...}  # 上下文压缩配置（可选）
memory_config: {...}           # 记忆配置（可选）
tool_config: {...}             # 工具配置（可选）
knowledge_config: {...}        # 知识库配置（可选）
skills_config: {...}           # 技能配置（可选）
behavior_config: {...}         # 行为配置（可选）
monitoring_config: {...}       # 监控配置（可选）
```

### 2. 配置方式对比

#### 方式一：通过前端界面创建智能体
在智能体创建流程的**第7步**中设置上下文压缩参数：
1. 进入智能体创建页面
2. 填写基础信息（第1-6步）
3. 在第7步配置上下文压缩参数
4. 完成创建

#### 方式二：通过 YAML 配置文件
在智能体配置文件中添加 `context_compression_config` 部分（推荐）

## 📝 配置示例

### 示例 1：基础配置（适合简单对话机器人）

```yaml
agent_metadata:
  agent_id: "simple_bot_001"
  agent_name: "简单对话机器人"
  agent_type: "DialogAgent"
  description: "带有基础上下文压缩功能的对话机器人"
  version: "1.0.0"

model_config:
  model_name: "qwen-turbo"
  api_key: "sk-your-api-key"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  temperature: 0.8

prompt_config:
  system_prompt: "你是一个友好的聊天助手"
  user_prompt_template: "用户说：{user_input}"

# 上下文压缩配置（基础版本）
context_compression_config:
  enabled: true                           # 启用上下文压缩
  active_strategy: "hybrid"               # 使用混合策略

  strategies:
    hybrid:
      enabled: true
      semantic_weight: 0.6               # 语义权重60%
      token_weight: 0.4                  # Token权重40%
      min_context_length: 1000           # 最小上下文长度
      adaptive_threshold: 0.8            # 自适应阈值

  trigger_conditions:
    max_context_length: 3000             # 最大上下文长度
    token_threshold: 2000                # Token阈值
    trigger_on_each_turn: false          # 不在每轮都触发

  quality_controls:
    min_coherence_score: 0.8             # 最小连贯性分数
    max_information_loss: 0.2            # 最大信息丢失率
    enable_validation: true              # 启用验证
    compression_targets:
      min_compression_ratio: 0.3         # 最小压缩比
      max_compression_ratio: 0.6         # 最大压缩比

# 其他标准配置...
memory_config:
  short_term:
    enabled: true
    max_history_rounds: 10
```

### 示例 2：客服智能体配置（高级配置）

```yaml
agent_metadata:
  agent_id: "customer_service_001"
  agent_name: "智能客服助手"
  agent_type: "DialogAgent"
  description: "带有智能上下文压缩的客服系统"
  version: "1.0.0"

model_config:
  model_name: "gpt-4o"
  api_key: "sk-your-api-key"
  base_url: "https://api.openai.com/v1"
  temperature: 0.7

prompt_config:
  system_prompt: "你是一个专业的客户服务代表"
  user_prompt_template: "用户咨询：{user_input}"

# 高级上下文压缩配置
context_compression_config:
  enabled: true
  active_strategy: "hybrid"

  strategies:
    hybrid:
      enabled: true
      semantic_weight: 0.7               # 客服场景更重视语义
      token_weight: 0.3
      min_context_length: 1500
      adaptive_threshold: 0.8

    semantic:
      enabled: true
      similarity_threshold: 0.8          # 更高的相似度阈值
      preserve_entities: true            # 保留实体信息
      preserve_keywords:                 # 保留关键业务词汇
        - "重要客户"
        - "紧急问题"
        - "VIP客户"
        - "订单号"
        - "投诉"
        - "退换货"
      min_summary_length: 150
      max_summary_length: 600

    token_based:
      enabled: true                      # 同时启用基于Token的压缩
      max_tokens: 2500
      preserve_structure: true
      priority_sections:                 # 保留重要章节
        - "system"
        - "user"
        - "order_info"
        - "product_details"
      compression_ratio: 0.4

  trigger_conditions:
    max_context_length: 4000             # 客服场景允许更长上下文
    token_threshold: 3000
    time_interval_minutes: 30            # 每30分钟检查一次
    trigger_on_each_turn: false

  priority_config:                       # 优先级配置（客服场景重要）
    enabled: true
    preservation_threshold: 0.85         # 高保留阈值
    priority_rules:
      - rule_id: "preserve_customer_info"
        rule_name: "保留客户信息"
        priority: 10                     # 最高优先级
        conditions:
          content_type: ["customer_info", "order_details"]
          user_tagged: true
        action: "preserve"

      - rule_id: "preserve_complaints"
        rule_name: "保留投诉记录"
        priority: 9
        conditions:
          content_type: ["complaint", "feedback"]
          contains_keywords: ["投诉", "不满意", "问题"]
        action: "preserve"

      - rule_id: "compress_old_conversations"
        rule_name: "压缩旧对话"
        priority: 5
        conditions:
          age_range_hours: [12, 72]      # 12-72小时的对话
        action: "compress"

      - rule_id: "remove_very_old"
        rule_name: "删除极旧对话"
        priority: 1
        conditions:
          age_range_hours: [720, 8760]   # 30天以上的对话
        action: "remove"

  quality_controls:
    min_coherence_score: 0.85            # 客服场景要求更高连贯性
    max_information_loss: 0.15           # 更少的信息丢失
    enable_validation: true
    compression_targets:
      min_compression_ratio: 0.4
      max_compression_ratio: 0.7

# 其他配置...
memory_config:
  short_term:
    enabled: true
    max_history_rounds: 15
```

### 示例 3：开发/调试配置（禁用压缩）

```yaml
# 开发环境配置示例
context_compression_config:
  enabled: false                          # 开发环境禁用压缩
  active_strategy: "hybrid"
  strategies:
    hybrid:
      enabled: false
    semantic:
      enabled: false
    token_based:
      enabled: false
  trigger_conditions:
    max_context_length: 5000              # 设置更高的阈值
    token_threshold: 4000
    trigger_on_each_turn: false
  quality_controls:
    min_coherence_score: 0.7              # 较低的质量要求
    max_information_loss: 0.3
    enable_validation: false              # 开发时禁用验证
```

## 🔧 配置参数详解

### 核心参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `enabled` | boolean | 是 | `true` | 是否启用上下文压缩 |
| `active_strategy` | string | 是 | `"hybrid"` | 活跃策略：`semantic`/`token_based`/`hybrid` |
| `strategies` | object | 是 | - | 策略配置对象 |
| `trigger_conditions` | object | 是 | - | 触发条件配置 |
| `quality_controls` | object | 是 | - | 质量控制配置 |

### 策略配置参数

#### Hybrid 混合策略（推荐）
```yaml
strategies:
  hybrid:
    enabled: true
    semantic_weight: 0.6          # 语义压缩权重 (0-1)
    token_weight: 0.4             # Token压缩权重 (0-1)
    min_context_length: 1000      # 启动压缩的最小上下文长度
    adaptive_threshold: 0.8       # 自适应调整阈值
```

#### Semantic 语义策略
```yaml
strategies:
  semantic:
    enabled: true
    similarity_threshold: 0.75    # 相似度阈值 (0-1)
    preserve_entities: true       # 是否保留命名实体
    preserve_keywords: []         # 要保留的关键词列表
    min_summary_length: 100       # 摘要最小长度
    max_summary_length: 500       # 摘要最大长度
```

#### Token-based Token策略
```yaml
strategies:
  token_based:
    enabled: true
    max_tokens: 2000             # 最大保留Token数
    preserve_structure: true     # 是否保留消息结构
    priority_sections: []        # 优先保留的章节
    compression_ratio: 0.5       # 压缩比例 (0-1)
```

### 触发条件参数

```yaml
trigger_conditions:
  max_context_length: 3000           # 触发压缩的最大上下文长度
  token_threshold: 2000              # 触发压缩的Token阈值
  time_interval_minutes: 30          # 压缩时间间隔（可选）
  trigger_on_each_turn: false        # 是否在每轮对话后都触发
```

### 质量控制参数

```yaml
quality_controls:
  min_coherence_score: 0.8           # 最小连贯性分数 (0-1)
  max_information_loss: 0.2          # 最大信息丢失率 (0-1)
  enable_validation: true            # 是否启用验证
  compression_targets:
    min_compression_ratio: 0.3       # 目标最小压缩比 (0-1)
    max_compression_ratio: 0.6       # 目标最大压缩比 (0-1)
```

### 优先级配置参数（可选）

```yaml
priority_config:
  enabled: true                       # 是否启用优先级规则
  preservation_threshold: 0.8        # 保留阈值 (0-1)
  priority_rules:                    # 优先级规则列表
    - rule_id: "rule_id"             # 规则唯一标识
      rule_name: "规则名称"          # 规则名称
      priority: 10                    # 优先级 (1-10, 10最高)
      conditions: {...}              # 触发条件
      action: "preserve"              # 执行动作: preserve/compress/remove
```

## 🎨 使用场景推荐

### 场景 1：简单对话机器人
```yaml
# 推荐配置：基础混合策略
active_strategy: "hybrid"
semantic_weight: 0.6
token_weight: 0.4
max_context_length: 3000
```

### 场景 2：客服系统
```yaml
# 推荐配置：语义优先 + 优先级规则
active_strategy: "hybrid"
semantic_weight: 0.7
token_weight: 0.3
priority_config:
  enabled: true
  preservation_threshold: 0.85
preserve_keywords:
  - "订单"
  - "投诉"
  - "VIP客户"
```

### 场景 3：技术文档助手
```yaml
# 推荐配置：结构保留 + 高质量要求
active_strategy: "token_based"
preserve_structure: true
priority_sections: ["code", "technical_spec"]
min_coherence_score: 0.9
max_information_loss: 0.1
```

### 场景 4：数据分析助手
```yaml
# 推荐配置：Token优先 + 大上下文
active_strategy: "token_based"
max_context_length: 5000
max_tokens: 3000
compression_ratio: 0.6
```

## 🚀 创建智能体时的参数传递

### 前端 API 调用格式

```typescript
// 创建智能体时的请求格式
const createAgentRequest = {
  config: {
    agent_metadata: {...},
    llm_config: {...},
    prompt_config: {...},
    context_compression_config: {    // 作为标准配置项传递
      enabled: true,
      active_strategy: "hybrid",
      strategies: {...},
      trigger_conditions: {...},
      quality_controls: {...}
    },
    memory_config: {...},
    tool_config: {...},
    // ...其他配置项
  }
}
```

### 配置文件保存位置

创建智能体后，配置会保存到：
```
data/agents/{agent_id}.yaml
```

配置文件中 `context_compression_config` 作为顶级配置项保存。

## 📚 配置验证和加载

### 配置验证
系统会自动验证上下文压缩配置：
- ✅ 参数类型和范围验证
- ✅ 策略一致性验证
- ✅ 质量控制参数验证
- ✅ 优先级规则验证

### 配置加载
```python
# 后端加载上下文压缩配置
from agentscope_paas.config.loader import ConfigLoader

loader = ConfigLoader("path/to/config.yaml")
compression_config = loader.get_context_compression_config()

# 配置包含完整的上下文压缩参数
print(compression_config['enabled'])           # True
print(compression_config['active_strategy'])   # 'hybrid'
```

## 🔍 故障排查

### 问题 1：压缩配置未生效
**检查清单：**
- [ ] `enabled: true` 已设置
- [ ] `active_strategy` 与策略配置匹配
- [ ] 触发条件阈值设置合理
- [ ] 配置文件格式正确

### 问题 2：压缩质量不理想
**调整建议：**
- 提高 `min_coherence_score` (0.8 → 0.9)
- 降低 `max_information_loss` (0.2 → 0.1)
- 调整策略权重比例

### 问题 3：重要信息丢失
**解决方案：**
- 启用 `priority_config`
- 添加关键词到 `preserve_keywords`
- 设置较高的 `preservation_threshold`

## 📖 相关文档

- **完整配置示例**：`data/agents/example_agent_with_new_features.yaml`
- **压缩策略详解**：`data/agents/compression_strategies_example.yaml`
- **前端配置界面**：前端智能体创建流程第7步
- **API 文档**：`api_server/main.py` 中的 `AgentConfig` 模型

## 🎯 最佳实践

### ✅ 推荐做法
1. **从混合策略开始**：`hybrid` 策略适合大多数场景
2. **设置合理阈值**：根据实际使用情况调整触发条件
3. **启用质量控制**：确保压缩后的内容质量
4. **监控压缩效果**：通过监控配置观察压缩性能

### ❌ 避免做法
1. **不要设置极端阈值**：避免 0 或 1 这样的极端值
2. **不要忽视业务特点**：不同场景需要不同的配置策略
3. **不要禁用验证**：生产环境应启用 `enable_validation`
4. **不要过度压缩**：保持合理的压缩比范围

---

**版本**: 1.0.0
**更新时间**: 2025-01-19
**维护**: AgentScope PaaS 团队