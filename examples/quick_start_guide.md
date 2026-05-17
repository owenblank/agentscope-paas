# 🚀 AgentScope PaaS 5分钟快速开始

这是一个超简明的入门指南，帮助你在5分钟内运行第一个智能体！

## ⏱️ 时间分配

- 步骤1: 获取API密钥 - 2分钟
- 步骤2: 配置文件 - 1分钟
- 步骤3: 运行智能体 - 2分钟

---

## 步骤1️⃣: 获取API密钥（2分钟）

选择一个模型服务商并获取API密钥：

### 选项A: 通义千问（推荐新手）
1. 访问：https://dashscope.aliyun.com/
2. 注册/登录账号
3. 进入API-KEY管理
4. 创建新的API-KEY
5. 复制保存（格式：sk-xxx）

**优点**: 有免费额度，中文支持好，成本低

### 选项B: OpenAI
1. 访问：https://platform.openai.com/
2. 注册/登录账号
3. 进入API keys section
4. 创建新的secret key
5. 复制保存（格式：sk-proj-xxx）

**优点**: 模型能力强，生态完善

---

## 步骤2️⃣: 配置文件（1分钟）

### 复制示例文件
```bash
cd examples
cp simple_chatbot.yaml my_first_agent.yaml
```

### 修改API密钥
打开 `my_first_agent.yaml`，找到这部分：

```yaml
model_config:
  # 如果使用通义千问
  model_name: "qwen-turbo"
  api_key: "sk-替换为你的API密钥"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"

  # 如果使用OpenAI
  # model_name: "gpt-4o-mini"
  # api_key: "sk-proj-替换为你的API密钥"
  # base_url: "https://api.openai.com/v1"
```

**只需要修改这一个地方！**

---

## 步骤3️⃣: 运行智能体（2分钟）

### 安装AgentScope
```bash
pip install agentscope
```

### 启动智能体
```bash
python -m agentscope.paas run my_first_agent.yaml
```

### 开始对话
```
🤖 智能客服助手已启动！
用户: 你好
智能体: 你好！很高兴为你服务。有什么我可以帮助你的吗？

用户: 你能做什么？
智能体: 我可以和你聊天，回答问题，讨论各种话题。我可以帮你解答疑问、提供建议，或者只是陪你聊聊天。你想聊些什么呢？

用户: 介绍一下自己
智能体: 我是一个友好的AI助手，善于倾听和交流。我喜欢帮助他人，知识面比较广泛。无论是学习、工作还是生活上的问题，我都很乐意和你一起探讨。
```

---

## ✅ 恭喜！

你已经成功运行了第一个智能体！🎉

---

## 🎯 下一步

### 修改智能体性格
编辑配置文件中的 `system_prompt`:

```yaml
prompt_config:
  system_prompt: |
    你是一个专业的Python编程导师。

    你的职责：
    - 帮助学生学习Python编程
    - 解答编程问题
    - 提供代码示例和最佳实践

    教学风格：
    - 耐心细致，循序渐进
    - 用简单语言解释复杂概念
    - 鼓励学生动手实践
```

### 添加工具能力
参考 `customer_service_agent.yaml` 学习如何集成工具。

### 创建团队
研究 `software_dev_team.yaml` 了解多智能体协作。

---

## 🔥 常见问题快速解决

### 问题1: API密钥错误
```
错误信息: Authentication failed
解决: 检查API密钥是否正确复制，前后没有空格
```

### 问题2: 网络连接失败
```
错误信息: Connection timeout
解决: 检查网络连接，如果在中国，建议使用通义千问
```

### 问题3: 模型响应慢
```
现象: 等待时间超过10秒
解决: 更换为更快的模型（如 qwen-turbo, gpt-4o-mini）
```

### 问题4: 超出预算
```
现象: API费用过高
解决:
- 降低 max_tokens: 800
- 减少 max_conversation_rounds: 5
- 使用更便宜的模型
```

---

## 💰 成本参考

### 通义千问（推荐新手）
- qwen-turbo: ¥0.008/千tokens
- 估算：每天100次对话 ≈ ¥1-2

### OpenAI
- gpt-4o-mini: $0.15/百万输入tokens
- 估算：每天100次对话 ≈ $0.1-0.2

**建议**: 开发测试用通义千问，生产环境用OpenAI

---

## 📚 学习路径

```
第1天: 运行 simple_chatbot.yaml
      ↓
第2天: 修改提示词，自定义智能体性格
      ↓
第3天: 运行 customer_service_agent.yaml，学习工具集成
      ↓
第4天: 创建自己的客服智能体
      ↓
第5天: 运行 software_dev_team.yaml，了解团队协作
      ↓
第1周: 构建自己的多智能体应用
```

---

## 🎓 推荐资源

- [AgentScope官方文档](https://github.com/modelscope/agentscope)
- [提示词工程指南](https://www.promptingguide.ai/)
- [通义千问API文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI API文档](https://platform.openai.com/docs)

---

## 🌟 进阶技巧

### 技巧1: 温度参数控制创意
```yaml
# 温度=0.3: 稳定一致，适合客服、翻译
temperature: 0.3

# 温度=0.8: 平衡，适合聊天、问答
temperature: 0.8

# 温度=1.2: 创意丰富，适合创作、头脑风暴
temperature: 1.2
```

### 技巧2: 记忆容量管理
```yaml
memory_config:
  # 短记忆：适合简单对话，节省成本
  max_history_rounds: 5

  # 长记忆：适合复杂任务，提高质量
  max_history_rounds: 20
```

### 技巧3: 输出格式约束
```yaml
behavior_config:
  output_format:
    type: "json"  # 强制JSON输出
    # 或 "markdown" 用于结构化文本
```

---

**准备好开始了吗？选择一个示例，立即开始吧！** 🚀
