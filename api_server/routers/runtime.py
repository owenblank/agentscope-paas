"""
Runtime Router Module

Provides API endpoints for AgentScope Runtime integration including
agent deployment, Runtime conversations, health monitoring, and lifecycle management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
import asyncio
import logging
import json

from agentscope_paas.config.loader import ConfigLoader
from agentscope_paas.core.runtime_manager import get_runtime_manager
from agentscope_paas.utils.runtime_validator import check_runtime_availability
from agentscope_paas.utils.logger import get_logger
from agentscope_paas.auth.middleware import get_storage
from api_server.utils.streaming import (
    create_streaming_response,
    create_sse_error_response,
    format_sse_message
)

# Create router
router = APIRouter(prefix="/api/v1", tags=["runtime"])

# Logger
logger = get_logger(__name__)

# ============================================
# Request/Response Models
# ============================================

class RuntimeDeployRequest(BaseModel):
    """Runtime deployment request"""
    host: str = Field(default="localhost", description="Service host address")
    port: int = Field(default=8080, description="Service port", ge=1, le=65535)
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent requests", ge=1)
    auto_start: bool = Field(default=True, description="Auto-start the service")
    idle_timeout_minutes: int = Field(default=30, description="Idle timeout before cleanup", ge=0)
    runtime_config: Optional[Dict[str, Any]] = Field(default=None, description="Additional Runtime configuration")

class RuntimeChatRequest(BaseModel):
    """Runtime chat request"""
    message: str = Field(..., description="User message", min_length=1)
    stream: bool = Field(default=False, description="Enable streaming response")
    user_id: str = Field(default="default_user", description="User ID for session management")
    session_id: str = Field(default="default_session", description="Session ID for conversation tracking")

class RuntimeHealthResponse(BaseModel):
    """Runtime health check response"""
    agent_id: str
    status: str
    deployment_status: str
    last_check: str
    deployment_url: Optional[str]
    uptime_minutes: Optional[float]
    idle_minutes: Optional[float]
    runtime_available: bool

class RuntimeStatusResponse(BaseModel):
    """Runtime agent status response"""
    agent_id: str
    deployment_status: str
    deployment_url: Optional[str]
    deployment_port: Optional[int]
    health_status: str
    last_health_check: Optional[str]
    auto_start: bool
    idle_timeout_minutes: int
    runtime_available: bool
    last_activity: Optional[str]

class RuntimeDeployResponse(BaseModel):
    """Runtime deployment response"""
    success: bool
    agent_id: str
    deployment_url: Optional[str]
    deployment_status: str
    message: str
    runtime_available: bool

class RuntimeChatResponse(BaseModel):
    """Runtime chat response"""
    success: bool
    agent_id: str
    response: Optional[str]
    stream_url: Optional[str]
    error: Optional[str]
    timestamp: str

class RuntimeStopResponse(BaseModel):
    """Runtime stop response"""
    success: bool
    agent_id: str
    previous_status: str
    message: str

class RuntimeRestartResponse(BaseModel):
    """Runtime restart response"""
    success: bool
    agent_id: str
    deployment_url: Optional[str]
    message: str

# ============================================
# Helper Functions
# ============================================

def get_agent_config_path(agent_id: str, storage) -> str:
    """
    Get configuration file path for agent

    Args:
        agent_id: Agent ID
        storage: Storage instance

    Returns:
        Configuration file path
    """
    try:
        agent_data = storage.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )

        config_path = agent_data.get("config_path")
        if not config_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent {agent_id} has no configuration path"
            )

        return config_path

    except Exception as e:
        logger.error(f"Error getting agent config path: {str(e)}")
        raise

def check_runtime_availability_endpoint():
    """Check if Runtime is available"""
    if not check_runtime_availability():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AgentScope Runtime is not available. Install with: pip install agentscope-runtime",
            headers={"X-Runtime-Available": "false"}
        )

# ============================================
# API Endpoints
# ============================================

@router.post(
    "/agents/{agent_id}/deploy",
    response_model=RuntimeDeployResponse,
    summary="Deploy agent as Runtime service",
    description="Deploy an existing agent as an AgentScope Runtime HTTP service"
)
async def deploy_agent(
    agent_id: str,
    deploy_request: RuntimeDeployRequest,
    storage=Depends(get_storage)
):
    """
    Deploy agent as Runtime service

    This endpoint deploys an existing agent configuration as an AgentScope Runtime
    HTTP service with the specified deployment parameters.
    """
    try:
        logger.info(f"Deploying agent {agent_id} as Runtime service")

        # Check Runtime availability
        if not check_runtime_availability():
            return RuntimeDeployResponse(
                success=False,
                agent_id=agent_id,
                deployment_url=None,
                deployment_status="runtime_unavailable",
                message="AgentScope Runtime is not available. Install with: pip install agentscope-runtime",
                runtime_available=False
            )

        # Get agent configuration path
        config_path = get_agent_config_path(agent_id, storage)

        # Load configuration
        config_loader = ConfigLoader(config_path)
        success, config, errors = config_loader.load()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuration loading failed: {errors}"
            )

        # Get Runtime manager
        runtime_manager = get_runtime_manager(config_loader)

        # Deploy agent
        deploy_success = runtime_manager.create_and_deploy_agent(
            host=deploy_request.host,
            port=deploy_request.port,
            max_concurrent_requests=deploy_request.max_concurrent_requests,
            auto_start=deploy_request.auto_start,
            idle_timeout_minutes=deploy_request.idle_timeout_minutes
        )

        if deploy_success:
            return RuntimeDeployResponse(
                success=True,
                agent_id=agent_id,
                deployment_url=runtime_manager.deployment_url,
                deployment_status=runtime_manager.deployment_status,
                message=f"Agent deployed successfully at {runtime_manager.deployment_url}",
                runtime_available=True
            )
        else:
            return RuntimeDeployResponse(
                success=False,
                agent_id=agent_id,
                deployment_url=None,
                deployment_status="deployment_failed",
                message="Agent deployment failed. Check logs for details.",
                runtime_available=True
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deployment error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment failed: {str(e)}"
        )


@router.post(
    "/agents/{agent_id}/chat/runtime",
    summary="Chat with deployed Runtime agent",
    description="Send a message to a deployed Runtime agent and get response"
)
async def chat_with_runtime_agent(
    agent_id: str,
    chat_request: RuntimeChatRequest,
    storage=Depends(get_storage)
):
    """
    Chat with deployed Runtime agent

    Supports both regular and streaming responses based on the stream parameter.
    """
    try:
        logger.info(f"Runtime chat request for agent {agent_id}")

        # Check Runtime availability
        if not check_runtime_availability():
            if chat_request.stream:
                return StreamingResponse(
                    iter([f"data: {json.dumps({'error': 'Runtime not available'})}\n\n"]),
                    media_type="text/event-stream"
                )
            else:
                return RuntimeChatResponse(
                    success=False,
                    agent_id=agent_id,
                    response=None,
                    stream_url=None,
                    error="AgentScope Runtime is not available",
                    timestamp=datetime.now().isoformat()
                )

        # Get agent configuration path
        config_path = get_agent_config_path(agent_id, storage)

        # Load configuration
        config_loader = ConfigLoader(config_path)
        success, config, errors = config_loader.load()

        if not success:
            error_msg = f"Configuration loading failed: {errors}"
            if chat_request.stream:
                return StreamingResponse(
                    iter([f"data: {json.dumps({'error': error_msg})}\n\n"]),
                    media_type="text/event-stream"
                )
            else:
                return RuntimeChatResponse(
                    success=False,
                    agent_id=agent_id,
                    response=None,
                    stream_url=None,
                    error=error_msg,
                    timestamp=datetime.now().isoformat()
                )

        # Get Runtime manager
        runtime_manager = get_runtime_manager(config_loader)

        # Check if agent is deployed
        if runtime_manager.deployment_status != "deployed":
            error_msg = "Agent is not deployed. Use /deploy endpoint first."
            if chat_request.stream:
                return StreamingResponse(
                    iter([f"data: {json.dumps({'error': error_msg})}\n\n"]),
                    media_type="text/event-stream"
                )
            else:
                return RuntimeChatResponse(
                    success=False,
                    agent_id=agent_id,
                    response=None,
                    stream_url=None,
                    error=error_msg,
                    timestamp=datetime.now().isoformat()
                )

        # Handle streaming response
        if chat_request.stream:
            try:
                # Use enhanced streaming utilities
                return StreamingResponse(
                    create_streaming_response(
                        agent_id=agent_id,
                        message=chat_request.message,
                        runtime_manager=runtime_manager,
                        user_id=chat_request.user_id,
                        session_id=chat_request.session_id,
                        timeout_seconds=120
                    ),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Agent-ID": agent_id,
                        "X-Accel-Buffering": "no"  # Disable nginx buffering
                    }
                )
            except Exception as e:
                logger.error(f"Streaming setup error: {str(e)}")
                error_sse = create_sse_error_response(str(e), agent_id, "STREAM_SETUP_ERROR")
                return StreamingResponse(
                    iter([error_sse]),
                    media_type="text/event-stream"
                )

        # Handle regular response
        else:
            response = await runtime_manager.chat_with_runtime(
                chat_request.message,
                stream=False
            )

            if response:
                return RuntimeChatResponse(
                    success=True,
                    agent_id=agent_id,
                    response=str(response),
                    stream_url=None,
                    error=None,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return RuntimeChatResponse(
                    success=False,
                    agent_id=agent_id,
                    response=None,
                    stream_url=None,
                    error="Failed to get response from Runtime agent",
                    timestamp=datetime.now().isoformat()
                )

    except Exception as e:
        logger.error(f"Runtime chat error: {str(e)}")
        error_msg = f"Chat failed: {str(e)}"

        if chat_request.stream:
            return StreamingResponse(
                iter([f"data: {json.dumps({'error': error_msg})}\n\n"]),
                media_type="text/event-stream"
            )
        else:
            return RuntimeChatResponse(
                success=False,
                agent_id=agent_id,
                response=None,
                stream_url=None,
                error=error_msg,
                timestamp=datetime.now().isoformat()
            )


@router.get(
    "/agents/{agent_id}/health",
    response_model=RuntimeHealthResponse,
    summary="Get Runtime agent health status",
    description="Check the health and status of a deployed Runtime agent"
)
async def get_agent_health(
    agent_id: str,
    storage=Depends(get_storage)
):
    """
    Get Runtime agent health status

    Returns detailed health information including deployment status,
    uptime, idle time, and health check results.
    """
    try:
        logger.info(f"Health check for agent {agent_id}")

        # Check Runtime availability
        runtime_available = check_runtime_availability()

        # Try to get Runtime manager even if Runtime is not available
        try:
            config_path = get_agent_config_path(agent_id, storage)
            config_loader = ConfigLoader(config_path)
            success, config, errors = config_loader.load()

            if success:
                runtime_manager = get_runtime_manager(config_loader)
                health_info = runtime_manager.check_health()

                return RuntimeHealthResponse(
                    agent_id=agent_id,
                    status=health_info.get("status", "unknown"),
                    deployment_status=health_info.get("deployment_status", "unknown"),
                    last_check=health_info.get("last_check", datetime.now().isoformat()),
                    deployment_url=health_info.get("deployment_url"),
                    uptime_minutes=health_info.get("uptime_minutes"),
                    idle_minutes=health_info.get("idle_minutes"),
                    runtime_available=runtime_available
                )
            else:
                return RuntimeHealthResponse(
                    agent_id=agent_id,
                    status="config_error",
                    deployment_status="unknown",
                    last_check=datetime.now().isoformat(),
                    deployment_url=None,
                    uptime_minutes=None,
                    idle_minutes=None,
                    runtime_available=runtime_available
                )

        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return RuntimeHealthResponse(
                agent_id=agent_id,
                status="health_check_error",
                deployment_status="unknown",
                last_check=datetime.now().isoformat(),
                deployment_url=None,
                uptime_minutes=None,
                idle_minutes=None,
                runtime_available=runtime_available
            )

    except Exception as e:
        logger.error(f"Health endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.delete(
    "/agents/{agent_id}/stop",
    response_model=RuntimeStopResponse,
    summary="Stop Runtime agent",
    description="Stop and cleanup a deployed Runtime agent"
)
async def stop_runtime_agent(
    agent_id: str,
    cleanup: bool = True,
    storage=Depends(get_storage)
):
    """
    Stop Runtime agent

    Stops the deployed Runtime agent and optionally cleans up resources.
    """
    try:
        logger.info(f"Stopping agent {agent_id}")

        # Check Runtime availability
        if not check_runtime_availability():
            return RuntimeStopResponse(
                success=False,
                agent_id=agent_id,
                previous_status="runtime_unavailable",
                message="AgentScope Runtime is not available"
            )

        # Get agent configuration
        config_path = get_agent_config_path(agent_id, storage)
        config_loader = ConfigLoader(config_path)
        success, config, errors = config_loader.load()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuration loading failed: {errors}"
            )

        # Get Runtime manager
        runtime_manager = get_runtime_manager(config_loader)

        # Get previous status
        previous_status = runtime_manager.deployment_status

        # Stop the agent
        stop_success = runtime_manager.stop_agent(cleanup=cleanup)

        if stop_success:
            return RuntimeStopResponse(
                success=True,
                agent_id=agent_id,
                previous_status=previous_status,
                message=f"Agent stopped successfully. Previous status: {previous_status}"
            )
        else:
            return RuntimeStopResponse(
                success=False,
                agent_id=agent_id,
                previous_status=previous_status,
                message="Failed to stop agent"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stop agent error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop agent: {str(e)}"
        )


@router.get(
    "/agents/{agent_id}/runtime-status",
    response_model=RuntimeStatusResponse,
    summary="Get Runtime agent status",
    description="Get detailed status information for a Runtime agent"
)
async def get_runtime_agent_status(
    agent_id: str,
    storage=Depends(get_storage)
):
    """
    Get Runtime agent detailed status

    Returns comprehensive status information including deployment details,
    health status, configuration, and activity information.
    """
    try:
        logger.info(f"Status request for agent {agent_id}")

        # Check Runtime availability
        runtime_available = check_runtime_availability()

        try:
            # Get agent configuration
            config_path = get_agent_config_path(agent_id, storage)
            config_loader = ConfigLoader(config_path)
            success, config, errors = config_loader.load()

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Configuration loading failed: {errors}"
                )

            # Get Runtime manager
            runtime_manager = get_runtime_manager(config_loader)

            # Get deployment info
            deployment_info = runtime_manager.get_deployment_info()

            return RuntimeStatusResponse(
                agent_id=agent_id,
                deployment_status=deployment_info["deployment_status"],
                deployment_url=deployment_info["deployment_url"],
                deployment_port=deployment_info["deployment_port"],
                health_status=deployment_info["health_status"],
                last_health_check=deployment_info["last_health_check"],
                auto_start=deployment_info["auto_start"],
                idle_timeout_minutes=deployment_info["idle_timeout_minutes"],
                runtime_available=deployment_info["runtime_available"],
                last_activity=deployment_info["last_activity"]
            )

        except Exception as e:
            logger.error(f"Status retrieval error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get status: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status request failed: {str(e)}"
        )


@router.post(
    "/agents/{agent_id}/restart",
    response_model=RuntimeRestartResponse,
    summary="Restart Runtime agent",
    description="Restart a deployed Runtime agent with the same configuration"
)
async def restart_runtime_agent(
    agent_id: str,
    storage=Depends(get_storage)
):
    """
    Restart Runtime agent

    Restarts the agent with the same deployment configuration.
    """
    try:
        logger.info(f"Restarting agent {agent_id}")

        # Check Runtime availability
        if not check_runtime_availability():
            return RuntimeRestartResponse(
                success=False,
                agent_id=agent_id,
                deployment_url=None,
                message="AgentScope Runtime is not available"
            )

        # Get agent configuration
        config_path = get_agent_config_path(agent_id, storage)
        config_loader = ConfigLoader(config_path)
        success, config, errors = config_loader.load()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuration loading failed: {errors}"
            )

        # Get Runtime manager
        runtime_manager = get_runtime_manager(config_loader)

        # Restart the agent
        restart_success = runtime_manager.restart_agent()

        if restart_success:
            return RuntimeRestartResponse(
                success=True,
                agent_id=agent_id,
                deployment_url=runtime_manager.deployment_url,
                message=f"Agent restarted successfully at {runtime_manager.deployment_url}"
            )
        else:
            return RuntimeRestartResponse(
                success=False,
                agent_id=agent_id,
                deployment_url=None,
                message="Failed to restart agent"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restart agent error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart agent: {str(e)}"
        )


@router.get(
    "/runtime/status",
    summary="Get Runtime system status",
    description="Get overall AgentScope Runtime system status and availability"
)
async def get_runtime_system_status():
    """
    Get Runtime system status

    Returns information about Runtime availability, version, and system capabilities.
    """
    try:
        from agentscope_paas.utils.runtime_validator import RuntimeValidator

        validator = RuntimeValidator()
        status_info = validator.get_runtime_status()

        return {
            "runtime_available": status_info["available"],
            "runtime_version": status_info["version"],
            "python_version": status_info["python_version"],
            "platform": status_info["platform"],
            "platform_details": status_info["platform_details"],
            "features": status_info["features"],
            "installation_commands": status_info["installation_commands"] if not status_info["available"] else None
        }

    except Exception as e:
        logger.error(f"Runtime system status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Runtime status: {str(e)}"
        )