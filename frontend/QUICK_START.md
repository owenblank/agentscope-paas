# 🚀 AgentScope PaaS 前端项目运行指南

## 📝 快速运行步骤

### Windows 用户：

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
# 方法1: 使用提供的脚本
start.bat

# 方法2: 直接使用npm命令
npm run dev
```

3. **访问应用**
打开浏览器访问: http://localhost:3000

### Linux/Mac 用户：

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
# 方法1: 使用提供的脚本
chmod +x start.sh
./start.sh

# 方法2: 直接使用npm命令
npm run dev
```

3. **访问应用**
打开浏览器访问: http://localhost:3000

## 🔧 常用命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 修复代码格式
npm run lint:fix
```

## 📋 环境要求

- Node.js: 16.0.0+
- npm: 8.0.0+
- 现代浏览器

## ⚙️ 配置说明

### 环境变量
项目根目录的 `.env` 文件包含以下配置：

```env
# API地址
VITE_API_URL=http://localhost:8000/api/v1

# WebSocket地址
VITE_WS_URL=ws://localhost:8000/ws

# 应用配置
VITE_APP_NAME=AgentScope PaaS
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_ENABLE_MONITORING=true
VITE_ENABLE_WEBSOCKET=true
```

### API代理配置
开发环境下，前端会自动代理API请求到后端服务器。
如果后端不在 `localhost:8000`，请修改 `vite.config.ts`：

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://your-backend-url:port',  // 修改这里
      changeOrigin: true,
    },
  },
}
```

## 🌐 访问地址

- **开发服务器**: http://localhost:3000
- **API文档**: http://localhost:3000/docs (如果后端启用)
- **管理后台**: http://localhost:3000/dashboard

## 🎯 功能页面

- `/dashboard` - 仪表板首页
- `/agents` - 智能体列表
- `/agents/create` - 创建智能体
- `/agents/:id` - 智能体详情
- `/teams` - 团队管理
- `/monitoring` - 监控中心
- `/settings` - 系统设置

## 🐛 故障排除

### 1. 端口被占用
如果3000端口被占用，Vite会自动尝试其他端口，或者手动指定：
```bash
npm run dev -- --port 3001
```

### 2. 依赖安装失败
清除缓存重新安装：
```bash
rm -rf node_modules package-lock.json
npm install
```

### 3. 热更新不工作
检查防火墙设置，确保WebSocket连接正常。

### 4. API请求失败
确认后端服务已启动，并检查环境变量配置。

## 📦 生产部署

### 构建生产版本
```bash
npm run build
```

### 使用Docker部署
```bash
# 构建镜像
docker build -t agentscope-paas-frontend .

# 运行容器
docker run -p 3000:80 agentscope-paas-frontend
```

### 静态文件部署
构建后的文件在 `dist/` 目录，可以部署到任何静态文件服务器：
- Nginx
- Apache
- Vercel
- Netlify
- AWS S3 + CloudFront

## 🔗 相关资源

- [React 文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
- [Ant Design 文档](https://ant.design/)
- [React Router 文档](https://reactrouter.com/)

## 💡 开发提示

1. **热重载**: 修改代码后会自动刷新浏览器
2. **TypeScript**: 享受类型安全和智能提示
3. **ESLint**: 代码规范检查，保持代码质量
4. **样式**: 使用TailwindCSS和Ant Design组件

---

**祝您使用愉快！** 🎉
