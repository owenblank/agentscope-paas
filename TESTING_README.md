# AgentScope PaaS - 端到端集成测试文档

## 📋 概述

本测试套件为 AgentScope PaaS 平台提供全面的端到端集成测试，涵盖前后端完整功能验证。

## 🚀 快速开始

### 前置条件

1. **启动后端服务**
```bash
# 方式1：直接运行
python api_server/main.py

# 方式2：使用启动脚本
python start_api_server.py
```

2. **启动前端服务**
```bash
cd frontend
npm run dev
```

3. **安装测试依赖**
```bash
pip install -r e2e/requirements.txt
playwright install chromium
```

### 运行测试

#### 方式一：快速测试（推荐新手）
```bash
# 快速验证系统基本功能
python quick_test.py
```

#### 方式二：完整集成测试
```bash
# Windows
run_integration_tests.bat

# Linux/Mac
chmod +x run_integration_tests.sh
./run_integration_tests.sh
```

#### 方式三：使用pytest（推荐开发者）
```bash
# 基本测试
pytest e2e/test_pytest_e2e.py -v

# 带HTML报告
pytest e2e/test_pytest_e2e.py --html=test_results/html/report.html

# 并行运行
pytest e2e/test_pytest_e2e.py -n auto

# 只运行特定测试类
pytest e2e/test_pytest_e2e.py::TestHealthCheck -v
```

#### 方式四：直接运行Python脚本
```bash
# 无头模式
python e2e/comprehensive_integration_test.py --headless

# 有头模式（可以看到浏览器操作）
python e2e/comprehensive_integration_test.py
```

## 📊 测试覆盖范围

### 1. 系统健康检查
- ✅ API服务可用性
- ✅ 前端服务可用性
- ✅ 系统健康状态
- ✅ API文档可访问性

### 2. 用户认证流程
- ✅ 用户注册
- ✅ 用户登录
- ✅ Token获取
- ✅ 认证请求验证

### 3. 智能体管理
- ✅ 创建智能体
- ✅ 获取智能体列表
- ✅ 获取智能体详情
- ✅ 启动智能体
- ✅ 停止智能体
- ✅ 删除智能体

### 4. 对话功能
- ✅ 创建对话会话
- ✅ 发送消息
- ✅ 获取对话历史
- ✅ 消息流式响应

### 5. 配置验证
- ✅ 有效配置验证
- ✅ 无效配置检测
- ✅ 质量评分
- ✅ 错误提示

### 6. 前端页面
- ✅ 首页加载
- ✅ 登录页面
- ✅ 注册页面
- ✅ 仪表板
- ✅ 智能体管理页面
- ✅ 对话页面
- ✅ 监控页面

### 7. API端点测试
- ✅ 模板管理API
- ✅ 工具管理API
- ✅ 压缩策略API
- ✅ MCP配置API
- ✅ 内置工具API

### 8. 性能测试
- ✅ API响应时间
- ✅ 并发请求处理
- ✅ 页面加载性能

## 📁 测试文件结构

```
agentscope-paas/
├── e2e/                              # 端到端测试目录
│   ├── comprehensive_integration_test.py  # 完整集成测试
│   ├── test_pytest_e2e.py             # Pytest版本测试
│   ├── requirements.txt               # 测试依赖
│   └── ...其他测试文件
├── test_results/                      # 测试结果目录
│   ├── screenshots/                   # 截图保存
│   ├── logs/                          # 日志文件
│   └── html/                          # HTML报告
├── pytest.ini                         # Pytest配置
├── quick_test.py                      # 快速测试脚本
├── run_integration_tests.bat          # Windows运行脚本
└── run_integration_tests.sh           # Linux/Mac运行脚本
```

## 🔧 测试配置

### 环境变量
```bash
# API服务器地址
export API_BASE_URL="http://localhost:8000"

# 前端服务器地址
export FRONTEND_BASE_URL="http://localhost:3000"

# 测试超时设置
export TEST_TIMEOUT=10
```

### 修改测试配置
编辑测试文件中的 `Config` 或 `TestConfig` 类：

```python
class Config:
    """测试配置"""
    API_BASE_URL = "http://localhost:8000"
    FRONTEND_BASE_URL = "http://localhost:3000"
    TIMEOUT = 10
    HEADLESS = True  # 浏览器无头模式
```

## 📈 测试报告

### 报告类型

1. **控制台输出**
   - 实时显示测试进度
   - 彩色状态指示
   - 详细的错误信息

2. **JSON报告**
   - 机器可读格式
   - 完整的测试数据
   - 用于CI/CD集成

3. **HTML报告**
   - 交互式界面
   - 图表统计
   - 详细测试日志

4. **文本报告**
   - 简洁格式
   - 易于阅读
   - 适合归档

### 查看报告

```bash
# 查看最新的JSON报告
cat test_results/e2e_report_*.json | tail -1

# 查看最新的文本报告
cat test_results/e2e_report_*.txt

# 在浏览器中查看HTML报告
# Windows
start test_results/html/report.html

# Linux/Mac
open test_results/html/report.html
```

## 🐛 调试测试

### 启用详细日志
```bash
# 详细输出模式
pytest e2e/test_pytest_e2e.py -vv -s

# 显示print输出
python e2e/comprehensive_integration_test.py --verbose
```

### 调试特定测试
```bash
# 只运行一个测试
pytest e2e/test_pytest_e2e.py::TestHealthCheck::test_api_health_check -v

# 运行特定测试类
pytest e2e/test_pytest_e2e.py::TestAuthentication -v

# 运行标记的测试
pytest e2e/test_pytest_e2e.py -m "not slow" -v
```

### 使用浏览器调试
```bash
# 有头模式运行（可以看到浏览器）
python e2e/comprehensive_integration_test.py

# 慢速模式（每个操作延迟1秒）
pytest e2e/test_pytest_e2e.py --headed --slowmo=1000
```

## 🔄 持续集成

### GitHub Actions 配置
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r e2e/requirements.txt
          playwright install chromium
      - name: Start services
        run: |
          python api_server/main.py &
          cd frontend && npm run dev &
          sleep 10
      - name: Run tests
        run: python e2e/comprehensive_integration_test.py --headless
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test_results/
```

## 🎯 测试最佳实践

### 1. 测试隔离
- 每个测试应该独立运行
- 使用唯一的数据避免冲突
- 清理测试数据

### 2. 等待策略
- 使用显式等待而非隐式等待
- 等待页面加载完成
- 等待网络请求完成

### 3. 错误处理
- 记录详细的错误信息
- 保存失败时的截图
- 提供有用的失败原因

### 4. 性能考虑
- 设置合理的超时时间
- 避免不必要的等待
- 并行运行独立测试

## 📝 常见问题

### Q: 测试失败怎么办？
A:
1. 检查服务是否正常运行
2. 查看测试日志和截图
3. 尝试单独运行失败的测试
4. 检查网络连接和配置

### Q: 如何添加新测试？
A:
1. 在对应的测试类中添加测试方法
2. 使用 `test_` 前缀命名方法
3. 添加适当的断言和错误处理
4. 更新文档

### Q: 测试太慢怎么办？
A:
1. 使用并行测试执行
2. 减少等待时间
3. 跳过慢速测试：`pytest -m "not slow"`
4. 使用快速测试脚本：`quick_test.py`

### Q: 如何连接到远程服务器测试？
A: 修改配置文件中的URL：
```python
API_BASE_URL = "http://your-server.com"
FRONTEND_BASE_URL = "http://your-frontend.com"
```

## 🔗 相关资源

- [项目主文档](README.md)
- [API文档](http://localhost:8000/api/v1/docs)
- [AgentScope官方文档](https://github.com/modelscope/agentscope)
- [Playwright文档](https://playwright.dev/)
- [Pytest文档](https://docs.pytest.org/)

## 📞 支持与反馈

如有问题或建议，请：
- 提交 Issue
- 查看测试日志
- 联系开发团队

---

**最后更新**: 2025-01-18
**版本**: 1.0.0
**维护状态**: ✅ 活跃维护