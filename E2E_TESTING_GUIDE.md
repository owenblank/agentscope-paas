# AgentScope PaaS 端到端测试使用指南

## 快速开始

### 方法1：一键运行（推荐）

**Windows用户：**
```bash
run_e2e_complete.bat
```

**Linux/Mac用户：**
```bash
python scripts/prepare_e2e_env.py
python scripts/start_services.py &
python e2e/simple_e2e_test.py
```

### 方法2：手动步骤

1. **环境准备**
```bash
python scripts/prepare_e2e_env.py
```

2. **启动服务**
```bash
# 后端
cd api_server
python main.py

# 前端（新终端）
cd frontend
npm run dev
```

3. **运行测试**
```bash
python e2e/simple_e2e_test.py
```

## 配置说明

测试配置文件：`e2e/test_config.json`

### 主要配置项

**测试环境：**
- `frontend_url`: 前端地址（默认 http://localhost:3005）
- `backend_url`: 后端地址（默认 http://localhost:8000）
- `timeout`: 超时时间（毫秒）

**测试用户：**
- `email`: 测试用户邮箱
- `password`: 测试用户密码
- `auto_create`: 是否自动创建用户

**测试设置：**
- `headless`: 是否无头模式（false=显示浏览器）
- `browser`: 浏览器类型（chromium/firefox/webkit）
- `slow_mo`: 操作延迟（毫秒，便于观察）

## 测试覆盖

### 功能测试
- ✅ 首页加载和渲染
- ✅ 用户登录流程
- ✅ 智能体创建页面
- ✅ 页面导航功能

### 输出内容
- **截图**: `e2e_screenshots/` 目录
- **报告**: `e2e_reports/` 目录
- **日志**: 控制台实时输出

## 故障排除

### 问题1：Playwright未安装
```bash
python -m pip install playwright
python -m playwright install chromium
```

### 问题2：端口被占用
```bash
# 检查端口
netstat -ano | findstr :8000
netstat -ano | findstr :3005

# 修改配置文件中的端口
```

### 问题3：依赖缺失
```bash
pip install -e ".[dev]"
```

### 问题4：前端依赖问题
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 测试结果解读

### 控制台输出
```
📋 测试摘要
==================================
总测试数: 4
通过: 3
失败: 0
部分通过: 1
通过率: 75.0%
==================================
```

### JSON报告
```json
{
  "summary": {
    "total": 4,
    "passed": 3,
    "failed": 0,
    "partial": 1,
    "pass_rate": "75.0%"
  },
  "tests": [
    {
      "name": "首页加载",
      "status": "PASS",
      "duration": "2.34s"
    }
  ]
}
```

## 扩展测试

### 添加新测试
在 `e2e/simple_e2e_test.py` 中添加新的测试方法：

```python
def test_new_feature(self):
    """测试新功能"""
    test_name = "新功能测试"
    print(f"\n🧪 测试: {test_name}")

    try:
        # 测试代码
        result = {
            'name': test_name,
            'status': 'PASS',
            'message': "测试通过"
        }
        return result
    except Exception as e:
        result = {
            'name': test_name,
            'status': 'FAIL',
            'error': str(e)
        }
        return result
```

### 修改测试数据
编辑 `e2e/test_config.json` 中的 `test_agent` 部分。

---

**最后更新**: 2025-01-06
**维护者**: AgentScope PaaS Team