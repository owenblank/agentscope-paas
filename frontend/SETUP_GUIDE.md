# AgentScope PaaS 前端快速启动指南

## 📋 前置要求

- Node.js 16+
- npm 8+ 或 yarn/pnpm
- 现代浏览器 (Chrome, Firefox, Edge, Safari)

## 🚀 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件（可选，使用默认配置即可）
```

### 3. 启动开发服务器

```bash
npm run dev
```

服务器将启动在 http://localhost:3000

### 4. 访问应用

打开浏览器访问 http://localhost:3000

## 🛠️ 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 修复代码问题
npm run lint:fix
```

## 📝 开发说明

### API配置
前端默认代理API请求到 `http://localhost:8000`，如果后端在不同端口，请修改：

1. 编辑 `vite.config.ts` 中的 `proxy.target`
2. 或创建 `.env` 文件设置 `VITE_API_URL`

### 浏览器支持
- Chrome (推荐)
- Firefox
- Safari
- Edge

## 🐛 常见问题

### 端口被占用
如果3000端口被占用，Vite会自动尝试其他端口，或手动指定：
```bash
npm run dev -- --port 3001
```

### 依赖安装失败
尝试清除缓存重新安装：
```bash
rm -rf node_modules package-lock.json
npm install
```

### 热更新不工作
检查防火墙设置，确保Vite的WebSocket连接没有被阻止。

## 📦 构建部署

### 开发环境构建
```bash
npm run build
```

### Docker部署
```bash
# 构建镜像
docker build -t agentscope-paas-frontend .

# 运行容器
docker run -p 3000:80 agentscope-paas-frontend
```

## 🔧 开发工具推荐

- **IDE**: VSCode + ESLint + Prettier
- **浏览器**: Chrome DevTools
- **API测试**: Postman 或 curl
