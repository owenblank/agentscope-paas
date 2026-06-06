"""
对话管理路由

提供会话和对话消息的管理功能，包括会话记忆管理。
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime
from agentscope_paas.storage.models import User
from agentscope_paas.auth.middleware import api_key_auth
from agentscope_paas.memory.session_memory_service import session_memory_service

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

# 模拟的对话存储
conversations_store = {}


@router.get("/sessions/{session_id}/memory")
async def get_session_memory(
    session_id: str,
    user_id: str,
    current_user: User = Depends(api_key_auth)
):
    """获取会话记忆"""
    try:
        # 检查会话是否存在
        if session_id not in conversations_store:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 获取会话配置
        conversation = conversations_store[session_id]
        config = conversation.get("config", {})

        # 获取记忆
        memories = session_memory_service.get_memory(
            user_id=user_id,
            session_id=session_id,
            config=config
        )

        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "user_id": user_id,
                "memories": memories,
                "total_messages": len(memories)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"获取会话记忆失败: {str(e)}"
        }


@router.delete("/sessions/{session_id}/memory")
async def clear_session_memory(
    session_id: str,
    user_id: str,
    current_user: User = Depends(api_key_auth)
):
    """清除会话记忆"""
    try:
        # 检查会话是否存在
        if session_id not in conversations_store:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 获取会话配置
        conversation = conversations_store[session_id]
        config = conversation.get("config", {})

        # 清除记忆
        success = session_memory_service.clear_memory(
            user_id=user_id,
            session_id=session_id,
            config=config
        )

        if success:
            return {
                "success": True,
                "message": "会话记忆清除成功",
                "data": {
                    "session_id": session_id,
                    "user_id": user_id,
                    "cleared_at": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "清除会话记忆失败"
            }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"清除会话记忆失败: {str(e)}"
        }


@router.get("/sessions/{session_id}/memory/statistics")
async def get_memory_statistics(
    session_id: str,
    user_id: str,
    current_user: User = Depends(api_key_auth)
):
    """获取会话记忆统计信息"""
    try:
        # 检查会话是否存在
        if session_id not in conversations_store:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 获取会话配置
        conversation = conversations_store[session_id]
        config = conversation.get("config", {})

        # 获取统计信息
        stats = session_memory_service.get_statistics(
            user_id=user_id,
            session_id=session_id,
            config=config
        )

        return {
            "success": True,
            "data": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"获取统计信息失败: {str(e)}"
        }


@router.post("/sessions/{session_id}/memory/messages")
async def add_memory_message(
    session_id: str,
    request: Dict[str, Any],
    current_user: User = Depends(api_key_auth)
):
    """向会话记忆添加消息"""
    try:
        # 检查会话是否存在
        if session_id not in conversations_store:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 获取参数
        role = request.get("role")
        content = request.get("content")

        if not role or not content:
            raise HTTPException(status_code=400, detail="缺少role或content参数")

        # 获取会话配置
        conversation = conversations_store[session_id]
        config = conversation.get("config", {})

        # 添加消息
        success = session_memory_service.add_message(
            user_id=current_user.user_id,
            session_id=session_id,
            role=role,
            content=content,
            config=config
        )

        if success:
            return {
                "success": True,
                "message": "消息添加成功",
                "data": {
                    "session_id": session_id,
                    "role": role,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "消息添加失败"
            }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"添加消息失败: {str(e)}"
        }