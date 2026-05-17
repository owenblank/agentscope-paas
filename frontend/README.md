# AgentScope PaaS Frontend

AgentScope PaaS 的前端应用，基于 React + TypeScript + Ant Design 构建。

## 🚀 技术栈

- **框架**: React 18 + TypeScript
- **UI库**: Ant Design 5.0
- **状态管理**: Zustand
- **表单**: React Hook Form + Zod
- **数据获取**: TanStack Query (React Query)
- **HTTP客户端**: Axios
- **路由**: React Router v6
- **构建工具**: Vite
- **样式**: TailwindCSS + Ant Design

## 📦 安装依赖

```bash
npm install
```

## 🔧 配置环境变量

复制 `.env.example` 为 `.env` 并配置相关变量：

```bash
cp .env.example .env
```

## 🚀 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

## 🏗️ 项目结构

```
src/
├── components/          # 可复用组件
│   ├── Layout/         # 布局组件
│   └── Agent/          # 智能体相关组件
├── pages/              # 页面组件
│   ├── Dashboard/      # 仪表板
│   ├── Agent/          # 智能体管理
│   ├── Team/           # 团队管理
│   ├── Conversation/   # 对话界面
│   ├── Monitoring/     # 监控中心
│   └── Settings/       # 设置
├── services/           # API服务
├── store/              # 状态管理
├── types/              # TypeScript类型定义
├── utils/              # 工具函数
├── hooks/              # 自定义Hooks
├── styles/             # 样式文件
└── main.tsx           # 应用入口
```

## 🎯 核心功能

### 1. 智能体管理
- ✅ 智能体列表展示
- ✅ 智能体创建向导
- ✅ 智能体详情查看
- ✅ 智能体启动/停止
- ✅ 智能体删除

### 2. 配置向导
- ✅ 模板选择
- ✅ 基础信息配置
- ✅ 模型配置
- ✅ 提示词配置
- ✅ 高级配置
- ✅ 配置预览

### 3. 团队协作
- 📋 团队管理（开发中）
- 📋 协作配置（开发中）
- 📋 成员管理（开发中）

### 4. 对话功能
- 📋 实时对话（开发中）
- 📋 流式响应（开发中）
- 📋 对话历史（开发中）

## 🔌 API集成

前端通过RESTful API与后端通信，主要接口包括：

- `GET /api/v1/agents` - 获取智能体列表
- `POST /api/v1/agents` - 创建智能体
- `PUT /api/v1/agents/:id` - 更新智能体
- `DELETE /api/v1/agents/:id` - 删除智能体
- `POST /api/v1/agents/:id/start` - 启动智能体
- `POST /api/v1/agents/:id/stop` - 停止智能体

## 📝 开发规范

### 组件开发
- 使用函数组件和Hooks
- 遵循单一职责原则
- 组件文件使用PascalCase命名

### 代码风格
- 遵循ESLint规则
- 使用TypeScript类型注解
- 组件Props使用interface定义

### 状态管理
- 全局状态使用Zustand
- 本地状态使用useState
- 服务器状态使用React Query

## 🧪 测试

```bash
# 运行测试
npm test

# 测试覆盖率
npm run test:coverage
```

## 🏗️ 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

## 🚀 部署

### 开发环境
前端通过Vite开发服务器代理API请求，无需额外配置。

### 生产环境
1. 构建前端项目
2. 将 `dist/` 目录内容部署到静态文件服务器
3. 配置Nginx反向代理API请求

## 📖 相关文档

- [Ant Design 文档](https://ant.design/)
- [React 文档](https://react.dev/)
- [TanStack Query 文档](https://tanstack.com/query/latest)
- [Zustand 文档](https://zustand-demo.pmnd.rs/)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License
