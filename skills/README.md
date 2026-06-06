# AgentScope PaaS Skills 技能配置目录

## 概述

此目录用于存放智能体技能配置文件，支持从目录批量加载技能。所有技能配置文件遵循统一的标准格式，兼容Anthropic的规范要求。

## 目录结构

```
skills/
├── README.md                    # 本文件
├── skill_template.yaml         # 技能配置模板
└── examples/                   # 示例技能文件
    ├── order_processing.yaml   # 订单处理技能示例
    ├── product_query.yaml      # 产品查询技能示例
    └── customer_service.yaml   # 客户服务技能示例
```

## 技能配置规范

### 文件命名规范

- 技能文件名即为技能ID，使用小写字母和下划线
- 文件扩展名必须为 `.yaml` 或 `.yml`
- 示例：`order_processing.yaml`, `text_analysis.yaml`

### 技能配置结构

每个技能配置文件必须包含以下核心部分：

#### 1. 技能基础信息 (skill_metadata)
```yaml
skill_metadata:
  skill_id: "技能唯一ID"
  skill_name: "技能名称"
  skill_type: "技能类型"
  version: "1.0.0"
  description: "技能功能描述"
  tags: ["标签1", "标签2"]
```

#### 2. 技能能力定义 (capabilities)
```yaml
capabilities:
  operations:
    - operation_id: "操作ID"
      operation_name: "操作名称"
      description: "操作描述"
      enabled: true
      parameters:
        input_schema: {...}    # JSON Schema格式
        output_schema: {...}   # JSON Schema格式
      execution_config:
        timeout: 30
        max_retries: 2
```

#### 3. 技能实现配置 (implementation)
```yaml
implementation:
  implementation_type: "function_call|api_call|code_execution"
  function_config:
    function_name: "函数名称"
    function_parameters: {...}
  api_config:
    endpoint: "API端点"
    method: "POST|GET|PUT|DELETE"
    authentication:
      type: "bearer_token|api_key"
```

## 技能类型分类

### 支持的技能类型

1. **text_analysis** - 文本分析类
   - 文本摘要、分类、关键词提取
   - 情感分析、实体识别
   - 语言翻译、文本生成

2. **data_processing** - 数据处理类
   - 数据清洗、转换
   - 数据聚合、统计
   - 格式转换

3. **api_tool** - API工具类
   - 外部API调用
   - Web服务集成
   - 第三方平台对接

4. **code_execution** - 代码执行类
   - 代码运行和调试
   - 脚本执行
   - 沙箱环境执行

5. **database_query** - 数据库查询类
   - SQL查询执行
   - 数据检索
   - 数据库操作

6. **knowledge_retrieval** - 知识检索类
   - 知识库搜索
   - 文档检索
   - 语义搜索

7. **communication** - 通信协作类
   - 消息发送
   - 通知推送
   - 邮件发送

8. **analysis** - 分析类
   - 数据分析
   - 趋势分析
   - 预测分析

9. **generation** - 生成类
   - 内容生成
   - 报告生成
   - 文档生成

## 使用方法

### 1. 创建新技能

1. 复制 `skill_template.yaml` 模板文件
2. 重命名为合适的技能文件名
3. 根据技能需求填写配置参数
4. 将文件放置在 `skills/` 目录下

### 2. 在智能体配置中启用技能

在智能体配置文件中配置技能加载：

```yaml
skills_config:
  load_mode: "directory"
  skills_directory: "./skills/"
  loading_config:
    recursive_loading: true
    supported_formats:
      - ".yaml"
      - ".yml"
    validate_schema: true
  filter_config:
    included_skills:
      - "order_processing"    # 只加载指定的技能
      - "product_query"
    excluded_skills: []       # 排除的技能
```

### 3. 技能文件加载规则

- 系统会自动扫描 `skills/` 目录下的所有 `.yaml` 和 `.yml` 文件
- 支持递归加载子目录中的技能文件
- 如果配置了 `included_skills`，则只加载指定的技能
- 如果配置了 `excluded_skills`，则排除指定的技能
- 技能文件名必须与配置中的技能ID匹配

## 配置验证

### 必填字段验证

系统会验证以下必填字段：
- `skill_metadata.skill_id`
- `skill_metadata.skill_name`
- `skill_metadata.skill_type`
- `skill_metadata.version`
- `skill_metadata.description`
- `capabilities.operations` (至少包含一个操作)
- `implementation.implementation_type`

### 可选字段验证

以下字段为可选，但建议填写以提供完整的功能：
- `performance_config` - 性能配置
- `security_config` - 安全配置
- `monitoring_config` - 监控配置
- `dependencies` - 依赖配置
- `error_handling` - 错误处理
- `testing_config` - 测试配置
- `documentation` - 使用文档

## 最佳实践

### 1. 技能设计原则

- **单一职责**：每个技能专注于一个特定功能领域
- **接口清晰**：明确定义输入输出参数
- **错误处理**：提供完善的错误处理和降级策略
- **性能优化**：合理设置超时时间和重试策略
- **安全考虑**：根据数据敏感度设置合适的安全级别

### 2. 参数设计规范

- 使用 JSON Schema 定义参数结构
- 为参数提供清晰的描述和示例
- 设置合理的参数验证规则
- 考虑参数的默认值和可选性

### 3. 错误处理建议

- 定义清晰的错误类型和错误码
- 提供有用的错误消息和建议
- 实现适当的重试机制
- 考虑降级策略以保证服务可用性

### 4. 性能优化建议

- 合理使用缓存减少重复计算
- 设置适当的超时时间
- 考虑并发操作的限制
- 监控技能执行性能

## 示例技能

### 订单处理技能 (order_processing.yaml)

提供订单创建、查询、修改、取消等功能，包含：
- 完整的输入输出参数定义
- API调用实现方式
- 安全配置和访问控制
- 性能监控和日志记录
- 测试用例和使用文档

### 其他示例技能

更多示例技能将陆续添加到 `examples/` 目录中，涵盖：
- 产品查询技能
- 客户服务技能
- 数据分析技能
- 文本处理技能

## 故障排查

### 常见问题

1. **技能文件未被加载**
   - 检查文件名是否与技能ID匹配
   - 确认文件扩展名为 `.yaml` 或 `.yml`
   - 检查文件路径是否正确

2. **参数验证失败**
   - 检查输入输出参数的JSON Schema格式
   - 确认必填字段都已填写
   - 验证参数类型和格式是否正确

3. **技能执行超时**
   - 调整 `execution_config.timeout` 参数
   - 检查网络连接和API响应时间
   - 考虑优化技能实现或使用异步方式

4. **权限错误**
   - 检查 `security_config.access_control` 配置
   - 确认用户角色是否在允许列表中
   - 验证API认证信息是否正确

## 版本控制

建议对技能配置文件进行版本控制：

1. 在 `skill_metadata.version` 中标明版本号
2. 使用语义化版本号（如：1.0.0, 1.1.0, 2.0.0）
3. 重大变更时更新主版本号
4. 功能新增时更新次版本号
5. bug修复时更新修订版本号

## 更新日志

### v1.0.0 (2023-06-15)
- 初始版本发布
- 提供技能配置模板
- 添加订单处理技能示例
- 完善文档和使用说明

## 技术支持

如有问题或建议，请联系：
- 邮箱：support@agentscope.example.com
- 文档：https://docs.agentscope.example.com
- 社区：https://community.agentscope.example.com