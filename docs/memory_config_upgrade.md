# 🔄 记忆配置升级说明

## 📋 更新概述

已成功将智能体的记忆配置从单选模式升级为**多选模式**，现在可以同时配置：

- ✅ **短期记忆**（当前会话）
- ✅ **长期记忆**（持久化存储）
- ✅ **向量记忆**（语义检索）

## 🔧 主要更改

### 1. 配置文件结构变化

#### 旧格式（单选）：
```yaml
memory_config:
  memory_type: "short_term"  # 只能选择一种
  max_history_rounds: 10
  storage_config:
    storage_type: "file"
    storage_path: "./memory/agent_memory.json"
```

#### 新格式（多选）：
```yaml
memory_config:
  short_term:              # 短期记忆配置
    enabled: true
    max_history_rounds: 10

  long_term:               # 长期记忆配置
    enabled: true
    storage_type: "vector"  # 支持 file/database/redis/vector
    vector_db_path: "./data/memory"
    collection_name: "agent_memories"
    vector_config:
      embedding_model: "text-embedding-ada-002"
      similarity_threshold: 0.8
      top_k: 5

  vector:                  # 向量记忆配置
    enabled: false
    vector_db_path: "./data/vector_memory"
    collection_name: "vector_memories"
```

### 2. 前端界面改进

#### 新增功能：
- ✅ **独立开关**：每种记忆类型都有独立的启用开关
- ✅ **条件显示**：只有在启用时才显示相关配置选项
- ✅ **智能提示**：每种记忆类型都有详细说明
- ✅ **实时预览**：配置更改实时反映在表单中

#### 界面布局：
```
📋 记忆配置
├── ☑ 短期记忆（当前会话）
│   └── 最大对话轮次: [10]
├── ☑ 长期记忆（持久化存储）
│   ├── 存储类型: [向量数据库]
│   ├── 向量数据库路径: ./data/memory
│   ├── 集合名称: agent_memories
│   ├── 相似度阈值: [0.8]
│   └── 返回结果数: [5]
└── ☐ 向量记忆（语义检索）
    ├── 向量数据库路径
    └── 配置选项
```

### 3. 智能体记忆检索策略

启用多种记忆后，智能体会按以下顺序检索信息：

1. **短期记忆** → 当前会话上下文
2. **长期记忆** → 历史持久化数据
3. **向量记忆** → 语义相似的相关记忆

## 📁 更新的文件

### 配置模板文件：
- ✅ `single_agent_paas_template.yaml` - 单智能体模板
- ✅ `multi_agent_paas_template.yaml` - 多智能体模板
- ✅ `single_agent_frontend_optimized.yaml` - 前端优化模板

### 示例配置文件：
- ✅ `examples/simple_chatbot.yaml` - 简单聊天机器人
- ✅ `examples/customer_service_agent.yaml` - 智能客服助手

### 前端代码：
- ✅ `src/types/agent.ts` - 类型定义
- ✅ `src/components/Agent/AdvancedConfigForm.tsx` - 表单组件
- ✅ `src/store/agentFormStore.ts` - 状态管理

## 🎯 使用场景

### 场景1：仅短期记忆（适合简单对话）
```yaml
memory_config:
  short_term:
    enabled: true
    max_history_rounds: 10
  long_term:
    enabled: false
  vector:
    enabled: false
```

### 场景2：短期+长期记忆（适合客服助手）
```yaml
memory_config:
  short_term:
    enabled: true
    max_history_rounds: 15
  long_term:
    enabled: true
    storage_type: "vector"
    vector_db_path: "./data/customer_memory"
    vector_config:
      similarity_threshold: 0.8
      top_k: 5
  vector:
    enabled: false
```

### 场景3：全功能记忆（适合高级智能体）
```yaml
memory_config:
  short_term:
    enabled: true
    max_history_rounds: 20
  long_term:
    enabled: true
    storage_type: "vector"
    vector_config:
      similarity_threshold: 0.7
      top_k: 10
  vector:
    enabled: true
    vector_db_path: "./data/vector_memory"
    vector_config:
      similarity_threshold: 0.75
      top_k: 5
```

## 💡 配置建议

### 性能优化：
- 🔹 **开发测试**：仅启用短期记忆，减少资源消耗
- 🔹 **生产环境**：启用短期+长期记忆，平衡性能和功能
- 🔹 **高级场景**：全部启用，获得最强记忆能力

### 存储选择：
- 🗂️ **文件存储**：适合小规模应用，部署简单
- 🗄️ **数据库**：适合大规模应用，支持复杂查询
- 🔍 **向量数据库**：适合语义检索，提供智能记忆联想

### 参数调优：
- 📊 **记忆容量**：根据对话长度调整（建议5-20轮）
- 🎯 **相似度阈值**：控制检索精度（建议0.7-0.85）
- 📈 **返回结果数**：控制检索范围（建议3-10条）

## 🚀 迁移指南

如果您有使用旧格式的配置文件，需要：

1. **更新记忆配置结构**
2. **在创建智能体时重新配置记忆选项**
3. **或手动编辑现有配置文件**

### 自动迁移脚本（未来版本）
未来版本将提供自动迁移工具，可以自动将旧配置转换为新格式。

## 🎉 总结

此次升级为智能体记忆系统带来了更大的灵活性和更强大的功能，同时保持了向后兼容性。您可以根据实际需求选择合适的记忆配置组合！