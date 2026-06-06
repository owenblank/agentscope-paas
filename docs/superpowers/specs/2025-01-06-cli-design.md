# AgentScope PaaS CLI命令设计文档

**日期**: 2025-01-06
**项目**: AgentScope PaaS
**设计者**: Claude Code
**状态**: 待批准

---

## 设计目标

创建灵活强大的CLI命令系统，支持通过`agentscope-paas --configs <path>`的方式批量创建和启动智能体，支持交互式调试和后台服务多种运行模式。

---

## 命令结构设计

### 主命令格式
```bash
agentscope-paas <subcommand> [arguments] [options]
```

### 子命令结构

#### 1. run - 运行单个配置
```bash
agentscope-paas run <config-file> [options]
```
**功能**: 运行单个YAML配置文件，创建并启动智能体
**参数**:
- `<config-file>`: YAML配置文件路径（必需）
- `--mode` / `-m`: 运行模式
  - `interactive` (默认): 交互式对话模式
  - `daemon`: 后台守护进程模式
- `--workers` / `-w`: 并发工作线程数（默认: 1）

#### 2. batch - 批量运行配置目录
```bash
agentscope-paas batch <config-dir> [options]
```
**功能**: 扫描配置目录，批量创建和启动多个智能体
**参数**:
- `<config-dir>`: 配置文件目录路径（必需）
- `--mode`: 运行模式（interactive/daemon）
- `--pattern`: 文件匹配模式（默认: `*.yaml`）
- `--parallel`: 并行启动数量（默认: 3）

#### 3. serve - 后台服务模式
```bash
agentscope-paas serve <config-dir> [options]
```
**功能**: 启动后台服务，持续运行多个智能体
**参数**:
- `<config-dir>`: 配置文件目录路径
- `--port` / `-p`: API服务端口（默认: 8888）
- `--workers`: 工作进程数（默认: CPU核心数）
- `--reload`: 配置文件变化时自动重载

#### 4. validate - 验证配置文件
```bash
agentscope-paas validate <config-path> [options]
```
**功能**: 验证配置文件语法和语义，不启动智能体
**参数**:
- `<config-path>`: 配置文件或目录路径
- `--strict`: 严格模式，任何错误立即返回失败

#### 5. info - 系统信息
```bash
agentscope-paas info
```
**功能**: 显示系统信息、AgentScope版本、可用配置等

### 通用选项
- `--configs` / `-c`: 配置文件或目录路径
- `--log-level`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `--verbose` / `-v`: 详细输出模式
- `--quiet` / `-q`: 静默模式，只输出错误
- `--strict`: 严格模式，遇到错误立即停止
- `--help` / `-h`: 显示帮助信息
- `--version` / `-V`: 显示版本信息

---

## 核心组件架构

### 1. CLI主模块 (`agentscope_paas/cli.py`)

**职责**:
- 命令行参数解析和验证
- 子命令路由分发
- 全局错误处理和日志配置
- 进程信号处理（Ctrl+C优雅退出）

**核心类**:
```python
class CLIMain:
    """CLI主控制器"""
    def __init__(self):
        self.parser = self._create_parser()
        self.logger = None

    def _create_parser(self) -> ArgumentParser:
        """创建argparse解析器"""
        parser = ArgumentParser(...)
        subparsers = parser.add_subparsers(dest='command')

        # 添加子命令
        self._add_run_command(subparsers)
        self._add_batch_command(subparsers)
        # ... 其他子命令

        return parser

    def main(self):
        """CLI主入口"""
        args = self.parser.parse_args()
        self._setup_logging(args)

        # 路由到子命令
        if args.command == 'run':
            return self._run_single(args)
        elif args.command == 'batch':
            return self._batch_run(args)
        # ... 其他命令处理
```

### 2. 配置处理器 (`cli/config_processor.py`)

**职责**:
- 扫描配置目录，识别配置文件
- 批量配置验证和分类
- 生成智能体启动计划

**核心类**:
```python
class ConfigProcessor:
    """配置处理器"""

    def scan_directory(self, directory: str, pattern: str = "*.yaml") -> List[str]:
        """扫描目录，返回配置文件列表"""
        # 1. 检查目录存在性
        # 2. 使用glob模式匹配文件
        # 3. 过滤掉无效文件
        # 返回有效配置文件路径列表
        pass

    def validate_configs(self, config_paths: List[str], strict: bool = False) -> Dict:
        """批量验证配置文件"""
        results = {
            'valid': [],
            'invalid': [],
            'errors': {}
        }

        # 对每个配置文件进行验证
        for config_path in config_paths:
            try:
                # 使用ConfigLoader验证
                # 分类配置类型（单智能体/多智能体）
                pass
            except Exception as e:
                results['invalid'].append(config_path)
                results['errors'][config_path] = str(e)
                if strict:
                    raise

        return results

    def classify_config(self, config: Dict) -> str:
        """分类配置类型"""
        # 判断是单智能体配置还是多智能体团队配置
        # 返回 "single" 或 "team"
        pass
```

### 3. 启动管理器 (`cli/launcher.py`)

**职责**:
- 智能体生命周期管理
- 交互式对话界面
- 后台服务守护进程
- 进程监控和重启

**核心类**:
```python
class Launcher:
    """智能体启动管理器"""

    def __init__(self, mode: str = "interactive"):
        self.mode = mode
        self.agents = {}  # agent_id -> agent_instance
        self.logger = get_logger(__name__)

    def launch_agent(self, config: Dict, agent_id: str) -> bool:
        """启动单个智能体"""
        try:
            # 使用AgentFactory创建智能体
            # 启动并监控智能体
            return True
        except Exception as e:
            self.logger.error(f"Failed to launch agent {agent_id}: {e}")
            return False

    def launch_interactive_session(self, agents: Dict):
        """启动交互式对话会话"""
        # 提供用户界面
        # 接收用户输入
        # 路由到相应智能体处理
        # 显示回复结果
        pass

    def start_daemon_service(self, config_dir: str, port: int):
        """启动后台守护服务"""
        # 创建FastAPI服务
        # 启动多个智能体
        # 提供HTTP API接口
        # 持续运行并监控
        pass
```

### 4. 错误处理器 (`cli/error_handler.py`)

**职责**:
- 配置验证错误的详细报告
- 容错机制的决策逻辑
- 错误日志记录
- 用户友好的错误消息

**核心类**:
```python
class ErrorHandler:
    """错误处理器"""

    def handle_config_error(self, config_path: str, error: Exception, strict: bool):
        """处理配置错误"""
        error_type = type(error).__name__

        # 记录详细日志
        self.logger.error(f"Config error in {config_path}: {error_type} - {error}")

        # 生成用户友好的错误消息
        if strict:
            print(f"❌ 严重错误: 配置文件 {config_path} 无法加载")
            print(f"   错误类型: {error_type}")
            print(f"   详细信息: {error}")
        else:
            print(f"⚠️  跳过配置: {config_path} ({error_type})")

    def handle_launch_error(self, agent_id: str, error: Exception, continue_on_error: bool):
        """处理启动错误"""
        if continue_on_error:
            print(f"⚠️ 智能体 {agent_id} 启动失败，继续其他智能体")
            print(f"   错误: {error}")
        else:
            print(f"❌ 智能体 {agent_id} 启动失败，停止所有操作")
            raise error
```

---

## 数据流设计

### 完整执行流程

```
1. 用户输入命令
   ↓
2. 参数验证和解析
   ↓
3. 配置文件扫描
   ├── 扫描目录 (对于batch/serve)
   ├── 识别YAML文件
   └── 加载配置内容
   ↓
4. 配置验证
   ├── 语法验证
   ├── 语义验证
   ├── 依赖检查
   └── 生成验证报告
   ↓
5. 配置分类
   ├── 单智能体配置
   └── 多智能体团队配置
   ↓
6. 智能体创建
   ├── 使用AgentFactory
   ├── 初始化Runtime环境
   └── 加载依赖组件
   ↓
7. 启动执行
   ├── 交互式模式: 提供对话界面
   ├── 后台模式: 启动守护进程
   └── 批量模式: 并发启动多个智能体
   ↓
8. 监控管理
   ├── 健康状态检查
   ├── 错误恢复
   └── 优雅关闭
```

### 容错数据流

**配置阶段容错**:
```
配置文件1 → 验证通过 → 加入启动队列
配置文件2 → 验证失败 → 记录错误 → 跳过
配置文件3 → 验证通过 → 加入启动队列
配置文件4 → 语法错误 → 记录错误 → 跳过

最终结果: 启动配置1和3，报告错误2和4
```

**启动阶段容错**:
```
智能体A → 创建成功 → 启动成功 → 运行中
智能体B → 创建失败 → 记录错误 → 跳过
智能体C → 创建成功 → 启动失败 → 重试3次 → 标记失败
智能体D → 创建成功 → 启动成功 → 运行中

最终结果: A和D运行中，B和C失败但系统继续
```

---

## 技术实现细节

### 依赖库
- **argparse**: 标准库，用于命令行参数解析
- **pathlib**: 路径操作
- **yaml**: 配置文件解析
- **logging**: 日志记录
- **asyncio**: 异步操作支持
- **signal**: 进程信号处理
- **subprocess**: 进程管理

### 文件结构
```
agentscope_paas/
├── cli.py                    # CLI主模块
├── cli/
│   ├── config_processor.py  # 配置处理
│   ├── launcher.py          # 启动管理
│   ├── error_handler.py     # 错误处理
│   ├── daemon_service.py     # 后台服务
│   └── interactive.py       # 交互式界面
```

### 现有组件集成
- **ConfigLoader**: 复用 `config/loader.py`
- **AgentFactory**: 复用 `factory/agent_factory.py`
- **TeamFactory**: 复用 `factory/team_factory.py`
- **Engine**: 复用 `core/engine.py`
- **Logger**: 复用 `utils/logger.py`

### 配置文件格式
支持标准YAML格式，兼容现有配置：
- `simple_chatbot.yaml`: 单智能体配置
- `customer_service_agent.yaml`: 单智能体配置
- `software_dev_team.yaml`: 多智能体团队配置

### 错误输出格式
**配置扫描输出**:
```
📂 扫描配置目录: D:/configs/
Found 5 config files:
  ✅ chatbot.yaml
  ✅ support_agent.yaml
  ❌ invalid_config.yaml (syntax error)
  ✅ team.yaml
  ⚠️ deprecated_agent.yaml (deprecated fields)

📋 验证摘要:
  ✅ Valid: 4 files
  ❌ Invalid: 1 file
  ⚠️  Warnings: 1 file

🚀 准备启动 4 个智能体...
```

**启动过程输出**:
```
🚀 启动智能体服务...
[1/4] Creating chatbot... ✅
[2/4] Creating support_agent... ✅
[3/4] Creating dev_team... ✅
[4/4] Creating deprecated_agent... ⚠️ (using compatibility mode)

📊 启动结果:
  ✅ 成功: 4 agents
  ⚠️ 警告: 1 agent
  ❌ 失败: 0 agents

💬 交互模式已启动，输入 'exit' 退出
chatbot> 你好
chatbot> ...
```

---

## 实施优先级

### Phase 1: 基础CLI框架 (必需)
1. 创建 `cli.py` 主模块
2. 实现argparse命令结构
3. 添加基础日志和错误处理
4. 实现run子命令（单个配置）

### Phase 2: 批量处理 (重要)
1. 实现batch子命令
2. 创建ConfigProcessor
3. 实现批量配置验证
4. 并发启动管理

### Phase 3: 运行模式 (重要)
1. 实现交互式对话界面
2. 实现后台守护模式
3. 添加进程监控功能
4. 信号处理和优雅关闭

### Phase 4: 高级功能 (可选)
1. 实现serve子命令
2. 添加validate子命令
3. 实现配置热重载
4. 性能监控和统计

---

## 成功标准

### 功能完整性
- ✅ 支持单个和批量配置运行
- ✅ 支持交互式和后台两种模式
- ✅ 容错机制完善，错误处理友好
- ✅ 命令帮助文档完整

### 代码质量
- ✅ 遵循项目编码规范
- ✅ 完整的错误处理和日志记录
- ✅ 模块化设计，职责清晰
- ✅ 复用现有组件，避免重复

### 用户体验
- ✅ 命令语法直观易记
- ✅ 错误提示清晰有用
- ✅ 进度反馈实时显示
- ✅ 文档说明详细完整

---

## 风险和缓解

### 潜在风险
1. **配置文件兼容性**: 配置格式变更可能影响现有配置
   - 缓解: 向后兼容策略，版本标记
2. **并发启动复杂度**: 多智能体并发启动可能产生资源竞争
   - 缓解: 限制并发数，启动速率限制
3. **进程管理复杂度**: 后台服务进程管理容易出错
   - 缓解: 使用成熟的进程管理库，完善监控
4. **依赖AgentScope**: 依赖外部框架的稳定性
   - 缓解: 优雅降级，错误隔离

### 应急方案
1. 配置加载失败时，提供详细诊断信息
2. 启动失败时，提供清理和恢复机制
3. 进程异常时，自动记录崩溃信息
4. 依赖缺失时，提供安装指导

---

## 后续改进

### 短期改进
1. 添加配置文件热重载功能
2. 实现智能体状态查询API
3. 添加性能监控和统计
4. 支持配置文件模板生成

### 长期规划
1. 支持远程配置加载
2. 实现分布式智能体编排
3. 添加智能体性能优化建议
4. 集成监控和告警系统

---

**设计状态**: ✅ 完成
**下一步**: 等待用户审查后创建实施计划

---

**设计原则遵循**:
- 配置驱动: 所有行为通过配置控制
- 容错优先: 遇到错误时提供最大灵活性
- 用户友好: 错误信息清晰，操作指引明确
- 模块化: 组件职责清晰，易于维护和扩展