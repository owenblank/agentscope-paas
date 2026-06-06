"""
Streaming Utilities Module

Provides Server-Sent Events (SSE) streaming support for Runtime agent responses
with proper error handling, timeout management, and connection management.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from fastapi import HTTPException
from agentscope_paas.utils.logger import get_logger


class StreamingResponseManager:
    """
    Manager for Server-Sent Events streaming responses

    Handles SSE streaming with proper formatting, error handling,
    timeout management, and connection cleanup.
    """

    def __init__(
        self,
        agent_id: str,
        timeout_seconds: int = 120,
        keepalive_interval: int = 30
    ):
        """
        Initialize streaming response manager

        Args:
            agent_id: Agent identifier for the stream
            timeout_seconds: Stream timeout in seconds
            keepalive_interval: Keepalive interval in seconds
        """
        self.agent_id = agent_id
        self.timeout_seconds = timeout_seconds
        self.keepalive_interval = keepalive_interval
        self.logger = get_logger(__name__)
        self.start_time = datetime.now()
        self.last_activity = datetime.now()

    async def stream_agent_response(
        self,
        response_generator: AsyncGenerator,
        on_chunk: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream agent response with proper SSE formatting

        Args:
            response_generator: Async generator yielding response chunks
            on_chunk: Optional callback for each chunk
            on_complete: Optional callback on completion
            on_error: Optional callback on error

        Yields:
            SSE formatted response strings
        """
        try:
            self.logger.info(f"Starting stream for agent {self.agent_id}")

            # Send initial connection event
            yield self._format_sse_event({
                "type": "connected",
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "timeout": self.timeout_seconds
            })

            # Track timeout
            timeout_task = asyncio.create_task(self._timeout_monitor())

            try:
                async for chunk in response_generator:
                    # Check timeout
                    if self._is_timeout():
                        yield self._format_sse_event({
                            "type": "timeout",
                            "agent_id": self.agent_id,
                            "message": "Stream timeout exceeded"
                        })
                        break

                    # Update activity
                    self.last_activity = datetime.now()

                    # Process chunk
                    if chunk:
                        chunk_data = {
                            "type": "chunk",
                            "agent_id": self.agent_id,
                            "content": str(chunk),
                            "timestamp": datetime.now().isoformat()
                        }

                        yield self._format_sse_event(chunk_data)

                        # Call chunk callback if provided
                        if on_chunk:
                            await on_chunk(chunk)

                # Send completion event
                yield self._format_sse_event({
                    "type": "complete",
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": (datetime.now() - self.start_time).total_seconds()
                })

                # Call complete callback if provided
                if on_complete:
                    await on_complete()

            except asyncio.CancelledError:
                # Stream was cancelled by client
                yield self._format_sse_event({
                    "type": "cancelled",
                    "agent_id": self.agent_id,
                    "message": "Stream cancelled by client"
                })
            except Exception as e:
                self.logger.error(f"Stream error for agent {self.agent_id}: {str(e)}")
                error_data = {
                    "type": "error",
                    "agent_id": self.agent_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                yield self._format_sse_event(error_data)

                # Call error callback if provided
                if on_error:
                    await on_error(e)

            finally:
                timeout_task.cancel()

        except Exception as e:
            self.logger.error(f"Stream manager error: {str(e)}")
            yield self._format_sse_event({
                "type": "fatal_error",
                "agent_id": self.agent_id,
                "error": str(e)
            })

    def _format_sse_event(self, data: Dict[str, Any]) -> str:
        """
        Format data as Server-Sent Event

        Args:
            data: Event data dictionary

        Returns:
            SSE formatted string
        """
        return f"data: {json.dumps(data)}\n\n"

    async def _timeout_monitor(self) -> None:
        """Monitor stream timeout and send keepalive events"""
        while not self._is_timeout():
            await asyncio.sleep(self.keepalive_interval)

            # Send keepalive to prevent connection timeout
            if self._is_idle_too_long():
                self.logger.warning(f"Stream idle timeout for agent {self.agent_id}")
                break

        self.logger.info(f"Timeout monitor ending for agent {self.agent_id}")

    def _is_timeout(self) -> bool:
        """Check if stream has exceeded timeout"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.timeout_seconds

    def _is_idle_too_long(self) -> bool:
        """Check if stream has been idle too long"""
        idle_time = (datetime.now() - self.last_activity).total_seconds()
        return idle_time > (self.keepalive_interval * 2)


class StreamingChatProcessor:
    """
    Processor for streaming chat interactions with Runtime agents
    """

    def __init__(self):
        """Initialize streaming chat processor"""
        self.logger = get_logger(__name__)
        self.active_streams: Dict[str, StreamingResponseManager] = {}

    async def process_streaming_chat(
        self,
        agent_id: str,
        message: str,
        runtime_manager,
        user_id: str = "default_user",
        session_id: str = "default_session",
        timeout_seconds: int = 120
    ) -> AsyncGenerator[str, None]:
        """
        Process streaming chat with Runtime agent

        Args:
            agent_id: Agent identifier
            message: User message
            runtime_manager: Runtime manager instance
            user_id: User ID
            session_id: Session ID
            timeout_seconds: Stream timeout

        Yields:
            SSE formatted response strings
        """
        try:
            # Create streaming manager
            stream_manager = StreamingResponseManager(
                agent_id=agent_id,
                timeout_seconds=timeout_seconds
            )

            # Track active stream
            self.active_streams[agent_id] = stream_manager

            # Send processing started event
            yield stream_manager._format_sse_event({
                "type": "processing_started",
                "agent_id": agent_id,
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

            # Get Runtime chat response
            response_generator = runtime_manager.chat_with_runtime(
                user_input=message,
                stream=True
            )

            # Stream the response
            async for chunk in response_generator:
                yield stream_manager._format_sse_event({
                    "type": "response_chunk",
                    "agent_id": agent_id,
                    "content": str(chunk) if chunk else "",
                    "timestamp": datetime.now().isoformat()
                })

            # Send completion event
            yield stream_manager._format_sse_event({
                "type": "processing_complete",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            self.logger.error(f"Streaming chat error: {str(e)}")
            yield self._format_sse_event({
                "type": "error",
                "agent_id": agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

        finally:
            # Cleanup stream tracking
            if agent_id in self.active_streams:
                del self.active_streams[agent_id]

    def get_active_streams(self) -> list:
        """Get list of active stream agent IDs"""
        return list(self.active_streams.keys())

    def cancel_stream(self, agent_id: str) -> bool:
        """
        Cancel active stream for agent

        Args:
            agent_id: Agent identifier

        Returns:
            True if stream was cancelled, False otherwise
        """
        if agent_id in self.active_streams:
            # Cleanup is handled by finally block
            del self.active_streams[agent_id]
            return True
        return False


# Global streaming processor instance
streaming_processor = StreamingChatProcessor()


async def create_streaming_response(
    agent_id: str,
    message: str,
    runtime_manager,
    user_id: str = "default_user",
    session_id: str = "default_session",
    timeout_seconds: int = 120
) -> AsyncGenerator[str, None]:
    """
    Create streaming response for Runtime agent chat

    Convenience function that uses the global streaming processor

    Args:
        agent_id: Agent identifier
        message: User message
        runtime_manager: Runtime manager instance
        user_id: User ID
        session_id: Session ID
        timeout_seconds: Stream timeout

    Yields:
        SSE formatted response strings
    """
    async for chunk in streaming_processor.process_streaming_chat(
        agent_id=agent_id,
        message=message,
        runtime_manager=runtime_manager,
        user_id=user_id,
        session_id=session_id,
        timeout_seconds=timeout_seconds
    ):
        yield chunk


def get_streaming_processor() -> StreamingChatProcessor:
    """
    Get the global streaming processor instance

    Returns:
        StreamingChatProcessor instance
    """
    return streaming_processor


def format_sse_message(
    message_type: str,
    data: Dict[str, Any],
    agent_id: Optional[str] = None
) -> str:
    """
    Format a message as Server-Sent Event

    Args:
        message_type: Type of SSE message
        data: Message data
        agent_id: Optional agent identifier

    Returns:
        SSE formatted string
    """
    sse_data = {
        "type": message_type,
        "timestamp": datetime.now().isoformat(),
        **data
    }

    if agent_id:
        sse_data["agent_id"] = agent_id

    return f"data: {json.dumps(sse_data)}\n\n"


def create_sse_error_response(
    error_message: str,
    agent_id: str,
    error_code: str = "STREAM_ERROR"
) -> str:
    """
    Create SSE error response

    Args:
        error_message: Error message
        agent_id: Agent identifier
        error_code: Error code

    Returns:
        SSE formatted error string
    """
    return format_sse_message(
        message_type="error",
        data={
            "error": error_message,
            "error_code": error_code
        },
        agent_id=agent_id
    )


def create_sse_keepalive(agent_id: str) -> str:
    """
    Create SSE keepalive message

    Args:
        agent_id: Agent identifier

    Returns:
        SSE formatted keepalive string
    """
    return format_sse_message(
        message_type="keepalive",
        data={},
        agent_id=agent_id
    )