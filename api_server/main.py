"""
AgentScope PaaS Web API 服务器
提供 RESTful API 接口连接前端和后端智能体框架
"""

import sys
import os
from pathlib import Path

# 添加框架路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Literal
import uvicorn
import json
from datetime import datetime
import asyncio

# 暂时注释掉有问题的导入
# from agentscope_paas.config.loader import ConfigLoader
# from agentscope_paas.core.engine import Engine
# from agentscope_paas.utils.logger import get_logger
# from agentscope_paas.core.async_chat_processor import chat_processor
from agentscope_paas.auth.middleware import set_storage
from agentscope_paas.storage.memory import MemoryStorage
from api_server.routers import auth_router

# 创建 FastAPI 应用
app = FastAPI(
    title="AgentScope PaaS API",
    description="基于 AgentScope 的智能体 PaaS 平台 API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# 创建日志器（暂时禁用）
# logger = get_logger(__name__)
logger = None

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存存储（生产环境应使用数据库）
agents_store = {}
conversations_store = {}
templates_store = {}

# 认证存储初始化
auth_storage = MemoryStorage()
set_storage(auth_storage)

# ============================================
# 数据模型定义
# ============================================

class AgentMetadata(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str = "DialogAgent"
    description: str
    version: str = "1.0.0"
    tags: List[str] = []

class ModelConfig(BaseModel):
    model_name: str
    api_key: str
    base_url: Optional[str] = "https://api.openai.com/v1"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

class PromptConfig(BaseModel):
    system_prompt: str
    user_prompt_template: Optional[str] = None

class AgentConfig(BaseModel):
    agent_metadata: AgentMetadata
    llm_config: ModelConfig  # Renamed from model_config to avoid Pydantic conflict
    prompt_config: PromptConfig
    memory_config: Optional[Dict[str, Any]] = None
    tool_config: Optional[Dict[str, Any]] = None
    knowledge_config: Optional[Dict[str, Any]] = None
    skills_config: Optional[Dict[str, Any]] = None
    behavior_config: Optional[Dict[str, Any]] = None
    monitoring_config: Optional[Dict[str, Any]] = None
    # New configuration extensions
    mcp_config: Optional["MCPConfig"] = None
    built_in_tools_config: Optional["BuiltInToolsConfig"] = None
    context_compression_config: Optional["ContextCompressionConfig"] = None

class CreateAgentRequest(BaseModel):
    config: AgentConfig

class UpdateAgentRequest(BaseModel):
    config: Partial[AgentConfig]

class ValidationResult(BaseModel):
    valid: bool
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None
    quality_score: Optional[float] = None

class CostEstimateRequest(BaseModel):
    config: Dict[str, Any]
    usage_assumptions: Optional[Dict[str, Any]] = None

class ConnectionTestRequest(BaseModel):
    llm_config: ModelConfig  # Renamed from model_config

class CreateConversationRequest(BaseModel):
    agent_id: str
    user_id: Optional[str] = "user_001"
    metadata: Optional[Dict[str, Any]] = None

class SendMessageRequest(BaseModel):
    content: str
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None

# ============================================
# New Configuration Extension Models
# ============================================

class MCPConnectionConfig(BaseModel):
    connection_type: Literal['stdio', 'sse', 'http']
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 30
    env_vars: Optional[Dict[str, str]] = None

class MCPServerConfig(BaseModel):
    server_id: str
    server_name: str
    description: str
    connection: MCPConnectionConfig
    tools: List[str] = []
    resources: Optional[Dict[str, Any]] = None
    permissions: Optional[Dict[str, Any]] = None
    health_check: Optional[Dict[str, Any]] = None

class MCPConfig(BaseModel):
    enabled: bool = False
    servers: List[MCPServerConfig] = []
    global_settings: Optional[Dict[str, Any]] = None

class BuiltInToolParameter(BaseModel):
    name: str
    type: Literal['string', 'number', 'boolean', 'object', 'array']
    required: bool
    default: Optional[Any] = None
    description: str
    validation: Optional[Dict[str, Any]] = None

class BuiltInTool(BaseModel):
    tool_id: str
    tool_name: str
    category: Literal['data_analysis', 'text_processing', 'api_tools', 'file_operations', 'communication', 'web_tools']
    description: str
    version: str = "1.0.0"
    parameters: List[BuiltInToolParameter] = []
    execution_config: Optional[Dict[str, Any]] = None
    permissions: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None

class ToolCategory(BaseModel):
    category_id: str
    category_name: str
    description: str
    tools: List[str] = []
    icon: Optional[str] = None
    enabled_by_default: bool = True

class BuiltInToolsConfig(BaseModel):
    enabled: bool = False
    available_tools: List[BuiltInTool] = []
    categories: List[ToolCategory] = []
    global_restrictions: Optional[Dict[str, Any]] = None

class SemanticCompressionConfig(BaseModel):
    enabled: bool = True
    similarity_threshold: float = 0.75
    preserve_entities: bool = True
    preserve_keywords: List[str] = []
    min_summary_length: int = 100
    max_summary_length: int = 500

class TokenBasedCompressionConfig(BaseModel):
    enabled: bool = False
    max_tokens: int = 2000
    preserve_structure: bool = True
    priority_sections: List[str] = []
    compression_ratio: float = 0.5

class HybridCompressionConfig(BaseModel):
    enabled: bool = True
    semantic_weight: float = 0.6
    token_weight: float = 0.4
    min_context_length: int = 1000
    adaptive_threshold: float = 0.8

class PriorityRule(BaseModel):
    rule_id: str
    rule_name: str
    priority: int
    conditions: Dict[str, Any]
    action: Literal['preserve', 'compress', 'remove']

class ContextCompressionConfig(BaseModel):
    enabled: bool = False
    strategies: Dict[str, Any] = {}
    active_strategy: Literal['semantic', 'token_based', 'hybrid'] = 'hybrid'
    trigger_conditions: Dict[str, Any] = {}
    priority_config: Optional[Dict[str, Any]] = None
    quality_controls: Optional[Dict[str, Any]] = None

# ============================================
# 辅助函数
# ============================================

def load_templates():
    """加载模板数据"""
    global templates_store

    # 定义内置模板
    templates = [
        {
            "template_id": "customer_service_basic",
            "template_name": "智能客服基础版",
            "template_description": "适合初学者的客服智能体模板，支持基础对话和客户服务功能",
            "template_type": "single_agent",
            "category": "客户服务",
            "difficulty": "beginner",
            "tags": ["客服", "对话", "新手"],
            "thumbnail": "/templates/customer_service.png",
            "popularity_score": 4.8,
            "usage_count": 1234,
            "is_official": True,
            "is_featured": True,
            "created_at": "2024-01-10T00:00:00Z"
        },
        {
            "template_id": "data_analyst",
            "template_name": "数据分析助手",
            "template_description": "专注于数据分析和可视化的智能体，适合数据驱动的业务场景",
            "template_type": "single_agent",
            "category": "数据分析",
            "difficulty": "intermediate",
            "tags": ["数据分析", "可视化", "报表"],
            "thumbnail": "/templates/data_analyst.png",
            "popularity_score": 4.6,
            "usage_count": 856,
            "is_official": True,
            "is_featured": False,
            "created_at": "2024-01-12T00:00:00Z"
        },
        {
            "template_id": "dev_team_basic",
            "template_name": "基础开发团队",
            "template_description": "包含产品经理、开发工程师、测试工程师的协作团队模板",
            "template_type": "multi_agent",
            "category": "软件开发",
            "difficulty": "advanced",
            "tags": ["开发", "团队", "协作"],
            "thumbnail": "/templates/dev_team.png",
            "popularity_score": 4.9,
            "usage_count": 2341,
            "is_official": True,
            "is_featured": True,
            "created_at": "2024-01-08T00:00:00Z"
        }
    ]

    for template in templates:
        templates_store[template["template_id"]] = template

def save_agent_config(agent_id: str, config: AgentConfig):
    """保存智能体配置到文件"""
    config_dir = Path("./data/agents")
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / f"{agent_id}.json"

    # 将 Pydantic 模型转换为字典，并转换字段名
    config_dict = config.model_dump()

    # 将 llm_config 转换为 model_config (用于AgentScope兼容性)
    if "llm_config" in config_dict:
        config_dict["model_config"] = config_dict.pop("llm_config")

    # 保存为 JSON 文件（暂时用JSON代替YAML）
    import json
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=2)

    return str(config_file)

def load_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """从文件加载智能体配置"""
    config_file = Path(f"./data/agents/{agent_id}.json")
    if not config_file.exists():
        return None

    import json
    with open(config_file, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)

    return AgentConfig(**config_dict)

# 启动时加载模板
load_templates()

# ============================================
# 路由注册
# ============================================

# 包含认证路由
app.include_router(auth_router)

# ============================================
# 根路径处理
# ============================================

@app.get("/")
async def root():
    """根路径，重定向到API文档"""
    return RedirectResponse(url="/api/v1/docs")

@app.get("/docs")
async def docs_redirect():
    "/docs路径也重定向到API文档"
    return RedirectResponse(url="/api/v1/docs")

# ============================================
# 健康检查端点
# ============================================

@app.get("/api/v1/health")
async def health_check():
    """系统健康检查"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": "running",
            "services": {
                "api": "healthy",
                "agent_framework": "healthy"
            },
            "statistics": {
                "active_agents": len(agents_store),
                "active_conversations": len(conversations_store)
            }
        }
    }

# ============================================
# 模板管理端点
# ============================================

@app.get("/api/v1/templates")
async def get_templates(
    type: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None
):
    """获取模板列表"""
    templates = list(templates_store.values())

    # 过滤条件
    if type:
        templates = [t for t in templates if t["template_type"] == type]
    if category:
        templates = [t for t in templates if t["category"] == category]
    if difficulty:
        templates = [t for t in templates if t["difficulty"] == difficulty]

    return {
        "success": True,
        "data": {
            "templates": templates
        }
    }

@app.get("/api/v1/templates/{template_id}")
async def get_template(template_id: str):
    """获取模板详情"""
    if template_id not in templates_store:
        raise HTTPException(status_code=404, detail="模板不存在")

    template = templates_store[template_id].copy()

    # 添加示例配置
    if template_id == "customer_service_basic":
        template["example_config"] = {
            "agent_metadata": {
                "agent_id": "customer_service_001",
                "agent_name": "智能客服助手",
                "agent_type": "DialogAgent",
                "description": "24小时在线智能客服",
                "version": "1.0.0",
                "tags": ["客服", "中文"]
            },
            "llm_config": {
                "model_name": "gpt-4o",
                "api_key": "your-api-key",
                "base_url": "https://api.openai.com/v1"
            },
            "prompt_config": {
                "system_prompt": "你是一个专业的客户服务代表..."
            }
        }

    return {
        "success": True,
        "data": template
    }

@app.post("/api/v1/templates/{template_id}/create")
async def create_from_template(template_id: str, customizations: Dict[str, Any]):
    """从模板创建智能体"""
    if template_id not in templates_store:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 生成新的智能体 ID
    agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 创建基础配置（这里简化处理，实际应该从模板文件加载）
    base_config = {
        "agent_metadata": {
            "agent_id": agent_id,
            "agent_name": customizations.get("agent_metadata", {}).get("agent_name", "新智能体"),
            "agent_type": "DialogAgent",
            "description": customizations.get("agent_metadata", {}).get("description", "基于模板创建的智能体"),
            "version": "1.0.0",
            "tags": customizations.get("agent_metadata", {}).get("tags", [])
        },
        "llm_config": customizations.get("llm_config", {
            "model_name": "gpt-4o",
            "api_key": "your-api-key",
            "base_url": "https://api.openai.com/v1"
        }),
        "prompt_config": customizations.get("prompt_config", {
            "system_prompt": "你是一个有帮助的AI助手。"
        })
    }

    # 保存配置
    config = AgentConfig(**base_config)
    save_agent_config(agent_id, config)

    # 存储到内存
    agents_store[agent_id] = {
        "agent_id": agent_id,
        "config": config,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "template_id": template_id
    }

    return {
        "success": True,
        "data": {
            "agent_id": agent_id,
            "status": "created",
            "message": "智能体创建成功"
        }
    }

# ============================================
# 智能体管理端点
# ============================================

@app.get("/api/v1/agents")
async def get_agents(page: int = 1, limit: int = 20):
    """获取智能体列表"""
    agents = list(agents_store.values())

    # 分页
    start = (page - 1) * limit
    end = start + limit
    paginated_agents = agents[start:end]

    # 格式化响应
    formatted_agents = []
    for agent in paginated_agents:
        formatted_agents.append({
            "agent_id": agent["agent_id"],
            "agent_name": agent["config"].agent_metadata.agent_name,
            "agent_type": agent["config"].agent_metadata.agent_type,
            "description": agent["config"].agent_metadata.description,
            "status": agent["status"],
            "created_at": agent["created_at"],
            "tags": agent["config"].agent_metadata.tags
        })

    return {
        "success": True,
        "data": {
            "agents": formatted_agents,
            "pagination": {
                "total": len(agents),
                "page": page,
                "limit": limit,
                "pages": (len(agents) + limit - 1) // limit
            }
        }
    }

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取智能体详情"""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="智能体不存在")

    agent = agents_store[agent_id]

    return {
        "success": True,
        "data": {
            "agent_id": agent["agent_id"],
            "config": agent["config"].model_dump(),
            "status": agent["status"],
            "created_at": agent["created_at"]
        }
    }

@app.post("/api/v1/agents")
async def create_agent(request: CreateAgentRequest):
    """创建智能体"""
    agent_id = request.config.agent_metadata.agent_id

    # 检查是否已存在
    if agent_id in agents_store:
        raise HTTPException(status_code=409, detail="智能体 ID 已存在")

    # 保存配置
    config_file = save_agent_config(agent_id, request.config)

    # 存储到内存
    agents_store[agent_id] = {
        "agent_id": agent_id,
        "config": request.config,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "config_file": config_file
    }

    return {
        "success": True,
        "data": {
            "agent_id": agent_id,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "config_file": config_file
        },
        "message": "智能体创建成功"
    }

@app.put("/api/v1/agents/{agent_id}")
async def update_agent(agent_id: str, request: Dict[str, Any]):
    """更新智能体"""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="智能体不存在")

    # 更新配置（简化处理）
    agent = agents_store[agent_id]

    # 保存更新的配置
    save_agent_config(agent_id, agent["config"])

    agent["updated_at"] = datetime.now().isoformat()
    agent["status"] = "updated"

    return {
        "success": True,
        "data": {
            "agent_id": agent_id,
            "status": "updated",
            "updated_at": datetime.now().isoformat()
        },
        "message": "智能体更新成功"
    }

@app.delete("/api/v1/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """删除智能体"""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="智能体不存在")

    # 删除配置文件
    config_file = Path(f"./data/agents/{agent_id}.json")
    if config_file.exists():
        config_file.unlink()

    # 从内存中删除
    del agents_store[agent_id]

    return {
        "success": True,
        "message": "智能体删除成功"
    }

@app.post("/api/v1/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """启动智能体"""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        agent = agents_store[agent_id]

        # 简化版启动：仅标记状态，不实际调用Engine
        agent["status"] = "running"
        agent["started_at"] = datetime.now().isoformat()

        return {
            "success": True,
            "data": {
                "agent_id": agent_id,
                "status": "running",
                "started_at": agent["started_at"],
                "message": "智能体启动成功（模拟模式）"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"智能体启动异常: {str(e)}"
        }

@app.post("/api/v1/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """停止智能体"""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        agent = agents_store[agent_id]

        # 简化版停止：仅标记状态
        agent["status"] = "stopped"
        agent["stopped_at"] = datetime.now().isoformat()

        return {
            "success": True,
            "data": {
                "agent_id": agent_id,
                "status": "stopped",
                "stopped_at": agent["stopped_at"]
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"停止智能体异常: {str(e)}"
        }

# ============================================
# 配置验证端点
# ============================================

@app.post("/api/v1/config/validate")
async def validate_config(request: Dict[str, Any]):
    """验证配置"""
    config = request.get("config", {})

    errors = []
    warnings = []

    # 基本验证
    if not config.get("agent_metadata", {}).get("agent_id"):
        errors.append({
            "field": "agent_metadata.agent_id",
            "message": "智能体 ID 不能为空",
            "severity": "error"
        })

    if not config.get("agent_metadata", {}).get("agent_name"):
        errors.append({
            "field": "agent_metadata.agent_name",
            "message": "智能体名称不能为空",
            "severity": "error"
        })

    if not config.get("llm_config", {}).get("model_name"):
        errors.append({
            "field": "llm_config.model_name",
            "message": "模型名称不能为空",
            "severity": "error"
        })

    if not config.get("llm_config", {}).get("api_key"):
        errors.append({
            "field": "llm_config.api_key",
            "message": "API 密钥不能为空",
            "severity": "error"
        })

    system_prompt = config.get("prompt_config", {}).get("system_prompt", "")
    if len(system_prompt) < 50:
        warnings.append({
            "field": "prompt_config.system_prompt",
            "message": "系统提示词过短，建议至少 100 个字符",
            "severity": "warning"
        })

    # 计算质量分数
    quality_score = 10.0
    quality_score -= len(errors) * 2.0
    quality_score -= len(warnings) * 0.5
    quality_score = max(0.0, min(10.0, quality_score))

    return {
        "success": len(errors) == 0,
        "data": {
            "valid": len(errors) == 0,
            "errors": errors if errors else None,
            "warnings": warnings if warnings else None,
            "quality_score": quality_score
        }
    }

@app.post("/api/v1/config/estimate-cost")
async def estimate_cost(request: CostEstimateRequest):
    """估算成本"""
    model_name = request.config.get("model_name", "gpt-4o")
    max_tokens = request.config.get("max_tokens", 2000)

    # 简化的定价模型（实际应该调用真实API）
    pricing = {
        "gpt-4o": {"input_price": 0.005, "output_price": 0.015},
        "gpt-4o-mini": {"input_price": 0.00015, "output_price": 0.0006},
        "gpt-3.5-turbo": {"input_price": 0.0005, "output_price": 0.0015}
    }

    model_pricing = pricing.get(model_name, pricing["gpt-4o"])

    assumptions = request.usage_assumptions or {
        "daily_conversations": 100,
        "avg_turns_per_conversation": 10
    }

    daily_conversations = assumptions.get("daily_conversations", 100)
    avg_turns = assumptions.get("avg_turns_per_conversation", 10)

    # 计算估算
    avg_input_tokens = max_tokens // 2
    avg_output_tokens = max_tokens // 2

    per_message_cost = (avg_input_tokens * model_pricing["input_price"] +
                       avg_output_tokens * model_pricing["output_price"]) / 1000

    daily_tokens = daily_conversations * avg_turns * (avg_input_tokens + avg_output_tokens)
    daily_cost = daily_conversations * avg_turns * per_message_cost

    monthly_cost = daily_cost * 30

    optimization_tips = []
    if model_name == "gpt-4o":
        optimization_tips.append({
            "tip": "使用 gpt-4o-mini 可节省 70% 成本",
            "potential_savings": monthly_cost * 0.7
        })

    return {
        "success": True,
        "data": {
            "model_name": model_name,
            "pricing": {
                "input_price": model_pricing["input_price"],
                "output_price": model_pricing["output_price"],
                "currency": "USD"
            },
            "estimates": {
                "per_message": {
                    "average_cost": per_message_cost,
                    "min_cost": per_message_cost * 0.5,
                    "max_cost": per_message_cost * 1.5
                },
                "daily": {
                    "conversations": daily_conversations,
                    "tokens": daily_tokens,
                    "cost": daily_cost
                },
                "monthly": {
                    "conversations": daily_conversations * 30,
                    "tokens": daily_tokens * 30,
                    "cost": monthly_cost
                }
            },
            "optimization_tips": optimization_tips
        }
    }

@app.post("/api/v1/config/test-connection")
async def test_connection(request: ConnectionTestRequest):
    """测试模型连接"""
    import time
    start_time = time.time()

    # 这里应该实际测试模型连接，现在简化处理
    try:
        # 模拟连接测试
        time.sleep(0.1)  # 模拟网络延迟

        # 简单验证 API key 格式
        api_key = request.llm_config.api_key
        if not api_key or len(api_key) < 10:
            return {
                "success": False,
                "data": {
                    "connection_status": "failed",
                    "response_time": 0.0,
                    "model_available": False,
                    "test_message": "API key 格式不正确",
                    "timestamp": datetime.now().isoformat()
                }
            }

        response_time = time.time() - start_time

        return {
            "success": True,
            "data": {
                "connection_status": "success",
                "response_time": response_time,
                "model_available": True,
                "test_message": "Connection successful!",
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "data": {
                "connection_status": "failed",
                "response_time": 0.0,
                "model_available": False,
                "test_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        }

# ============================================
# MCP Configuration Endpoints
# ============================================

@app.post("/api/v1/mcp/test-connection")
async def test_mcp_connection(request: Dict[str, Any]):
    """测试MCP服务器连接"""
    try:
        from agentscope_paas.mcp.client import mcp_client

        server_config = request.get("server_config", {})
        if not server_config:
            raise HTTPException(status_code=400, detail="缺少 server_config")

        # Use synchronous wrapper to avoid event loop conflicts
        result = mcp_client.test_connection_sync(server_config)

        return {
            "success": result["status"] == "success",
            "data": result
        }

    except Exception as e:
        return {
            "success": False,
            "data": {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        }

@app.get("/api/v1/mcp/servers")
async def list_mcp_servers():
    """获取可用的MCP服务器列表"""
    try:
        from agentscope_paas.mcp.client import mcp_client

        connections = mcp_client.get_all_connections()

        return {
            "success": True,
            "data": {
                "servers": list(connections.values()),
                "total": len(connections)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"获取MCP服务器列表失败: {str(e)}"
        }

@app.post("/api/v1/mcp/servers")
async def add_mcp_server(request: Dict[str, Any]):
    """添加新的MCP服务器配置"""
    try:
        from agentscope_paas.mcp.client import mcp_client

        server_config = request.get("server_config", {})
        if not server_config:
            raise HTTPException(status_code=400, detail="缺少 server_config")

        # Test connection first
        test_result = await mcp_client.test_connection(server_config)
        if test_result["status"] != "success":
            return {
                "success": False,
                "message": f"MCP服务器连接测试失败: {test_result.get('error')}"
            }

        # Establish connection
        connection_id = mcp_client.connect_to_server_sync(server_config)

        return {
            "success": True,
            "data": {
                "connection_id": connection_id,
                "server_id": server_config.get("server_id"),
                "test_result": test_result
            },
            "message": "MCP服务器添加成功"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"添加MCP服务器失败: {str(e)}"
        }

# ============================================
# Built-in Tools Endpoints
# ============================================

@app.get("/api/v1/tools/builtin/registry")
async def get_builtin_tools_registry():
    """获取内置工具注册表"""
    try:
        from agentscope_paas.tools.registry import tool_registry

        all_tools = tool_registry.get_all_tools()
        categories = tool_registry.get_categories()

        return {
            "success": True,
            "data": {
                "tools": all_tools,
                "categories": categories,
                "total_tools": len(all_tools)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"获取工具注册表失败: {str(e)}"
        }

@app.post("/api/v1/tools/builtin/configure")
async def configure_builtin_tool(request: Dict[str, Any]):
    """配置内置工具"""
    try:
        from agentscope_paas.tools.registry import tool_registry

        tool_config = request.get("tool_config", {})
        if not tool_config:
            raise HTTPException(status_code=400, detail="缺少 tool_config")

        # Register or update tool
        success = tool_registry.register_built_in_tool(tool_config)

        if success:
            return {
                "success": True,
                "data": {
                    "tool_id": tool_config.get("tool_id"),
                    "tool_name": tool_config.get("tool_name")
                },
                "message": "工具配置成功"
            }
        else:
            return {
                "success": False,
                "message": "工具配置失败"
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"配置工具失败: {str(e)}"
        }

@app.get("/api/v1/tools/categories")
async def get_tool_categories():
    """获取工具类别列表"""
    try:
        from agentscope_paas.tools.registry import tool_registry

        categories = tool_registry.get_categories()

        return {
            "success": True,
            "data": {
                "categories": list(categories.values()),
                "total": len(categories)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"获取工具类别失败: {str(e)}"
        }

@app.post("/api/v1/tools/{tool_id}/execute")
async def execute_tool(tool_id: str, request: Dict[str, Any]):
    """执行工具"""
    try:
        from agentscope_paas.tools.registry import tool_registry

        arguments = request.get("arguments", {})
        context = request.get("context", {})

        # Execute tool (use synchronous wrapper to avoid event loop conflicts)
        result = tool_registry.execute_tool_sync(tool_id, arguments, context)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"工具执行失败: {str(e)}"
        }

# ============================================
# Context Compression Endpoints
# ============================================

@app.post("/api/v1/compression/analyze")
async def analyze_context_compression(request: Dict[str, Any]):
    """分析上下文并提供压缩建议"""
    try:
        from agentscope_paas.compression.engine import compression_engine

        context = request.get("context", [])
        compression_config = request.get("compression_config", {})

        if not context:
            raise HTTPException(status_code=400, detail="缺少 context 参数")

        # Use synchronous wrapper to avoid event loop conflicts
        analysis = compression_engine.analyze_context_sync(context, compression_config)

        return {
            "success": True,
            "data": analysis
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"上下文分析失败: {str(e)}"
        }

@app.post("/api/v1/compression/preview")
async def preview_compression(request: Dict[str, Any]):
    """预览压缩结果"""
    try:
        from agentscope_paas.compression.engine import compression_engine

        context = request.get("context", [])
        compression_config = request.get("compression_config", {})

        if not context:
            raise HTTPException(status_code=400, detail="缺少 context 参数")

        # Use synchronous wrapper to avoid event loop conflicts
        result = compression_engine.compress_context_sync(context, compression_config)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"压缩预览失败: {str(e)}"
        }

@app.get("/api/v1/compression/strategies")
async def get_compression_strategies():
    """获取可用的压缩策略"""
    try:
        from agentscope_paas.compression.engine import CompressionStrategy

        strategies = [
            {
                "strategy_id": CompressionStrategy.SEMANTIC.value,
                "name": "Semantic Compression",
                "description": "基于语义相似度的智能压缩，保留重要信息的同时合并相似内容",
                "advantages": [
                    "保持语义完整性",
                    "智能合并相似消息",
                    "保留关键实体和关键词"
                ],
                "best_for": "需要保持对话语义和上下文连贯性的场景",
                "compression_ratio": "30-50%"
            },
            {
                "strategy_id": CompressionStrategy.TOKEN_BASED.value,
                "name": "Token-Based Compression",
                "description": "基于Token计数的压缩，确保上下文长度在指定限制内",
                "advantages": [
                    "精确控制上下文长度",
                    "保持消息结构",
                    "优先级排序"
                ],
                "best_for": "有严格Token限制的场景",
                "compression_ratio": "40-60%"
            },
            {
                "strategy_id": CompressionStrategy.HYBRID.value,
                "name": "Hybrid Compression",
                "description": "结合语义和Token优势的混合压缩策略",
                "advantages": [
                    "平衡压缩质量和长度控制",
                    "自适应调整",
                    "最佳综合效果"
                ],
                "best_for": "需要平衡压缩质量和长度控制的一般场景",
                "compression_ratio": "35-55%"
            }
        ]

        return {
            "success": True,
            "data": {
                "strategies": strategies,
                "default_strategy": CompressionStrategy.HYBRID.value
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"获取压缩策略失败: {str(e)}"
        }

# ============================================
# 对话管理端点
# ============================================

@app.post("/api/v1/agents/{agent_id}/conversations")
async def create_conversation(agent_id: str, request: CreateConversationRequest):
    """创建对话会话"""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="智能体不存在")

    conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    conversation = {
        "conversation_id": conversation_id,
        "agent_id": agent_id,
        "user_id": request.user_id,
        "metadata": request.metadata or {},
        "status": "active",
        "messages": [],
        "created_at": datetime.now().isoformat()
    }

    conversations_store[conversation_id] = conversation

    return {
        "success": True,
        "data": conversation
    }

@app.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取对话详情"""
    if conversation_id not in conversations_store:
        raise HTTPException(status_code=404, detail="对话不存在")

    return {
        "success": True,
        "data": conversations_store[conversation_id]
    }

@app.get("/api/v1/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, page: int = 1, limit: int = 50):
    """获取对话消息列表"""
    if conversation_id not in conversations_store:
        raise HTTPException(status_code=404, detail="对话不存在")

    conversation = conversations_store[conversation_id]
    messages = conversation.get("messages", [])

    # 分页
    start = (page - 1) * limit
    end = start + limit
    paginated_messages = messages[start:end]

    return {
        "success": True,
        "data": {
            "messages": paginated_messages
        }
    }

@app.post("/api/v1/conversations/{conversation_id}/messages")
async def send_message(conversation_id: str, request: SendMessageRequest):
    """发送消息"""
    if conversation_id not in conversations_store:
        raise HTTPException(status_code=404, detail="对话不存在")

    conversation = conversations_store[conversation_id]
    agent_id = conversation["agent_id"]

    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="智能体不存在")

    # 添加用户消息
    user_message = {
        "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        "content": request.content,
        "role": "user",
        "created_at": datetime.now().isoformat(),
        "metadata": request.metadata or {}
    }

    conversation["messages"].append(user_message)

    # 简化版消息处理：返回模拟回复
    import time
    start_time = time.time()

    ai_response = f"这是对消息的模拟回复：{request.content}"

    assistant_message = {
        "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        "conversation_id": conversation_id,
        "content": ai_response,
        "role": "assistant",
        "created_at": datetime.now().isoformat(),
        "tokens_used": {
            "input": len(request.content),
            "output": len(ai_response),
            "total": len(request.content) + len(ai_response)
        },
        "response_time": time.time() - start_time
    }

    conversation["messages"].append(assistant_message)

    return {
        "success": True,
        "data": assistant_message
    }

# ============================================
# 主函数
# ============================================

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """启动 API 服务器"""
    # 创建必要的目录
    Path("./data/agents").mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)

    print("Starting AgentScope PaaS API Server")
    print(f"Address: http://{host}:{port}")
    print(f"Docs: http://localhost:{port}/api/v1/docs")
    print(f"Debug mode: {reload}")

    uvicorn.run(
        "api_server.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()