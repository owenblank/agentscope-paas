"""
MCP Client Module for AgentScope-PaaS

This module provides Model Context Protocol (MCP) server connection handling,
supporting stdio, SSE, and HTTP connection types for external tool and resource access.
"""

import asyncio
import json
import subprocess
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
import httpx
from sseclient import SSEClient

from agentscope_paas.utils.logger import get_logger


class MCPConnectionError(Exception):
    """MCP connection related errors"""
    pass


class MCPClient:
    """MCP Server Client for managing connections to MCP servers"""

    def __init__(self):
        """Initialize MCP client"""
        self.logger = get_logger(__name__)
        self.active_connections: Dict[str, Any] = {}
        self.connection_history: List[Dict[str, Any]] = []

    # Synchronous wrapper methods for FastAPI compatibility
    def test_connection_sync(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for test_connection"""
        try:
            # Check if there's already a running event loop (FastAPI case)
            try:
                loop = asyncio.get_running_loop()
                # If we have a running loop, we need to create a new thread
                import threading

                result = [None]
                exception = [None]

                def run_in_new_loop():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result[0] = new_loop.run_until_complete(self.test_connection(server_config))
                        new_loop.close()
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=run_in_new_loop)
                thread.start()
                thread.join()

                if exception[0]:
                    raise exception[0]

                return result[0]

            except RuntimeError:
                # No running loop, safe to use standard approach
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.test_connection(server_config))
                finally:
                    loop.close()

        except Exception as e:
            self.logger.error(f"Error in test_connection_sync: {str(e)}")
            raise

    def connect_to_server_sync(self, server_config: Dict[str, Any]) -> str:
        """Synchronous wrapper for connect_to_server"""
        try:
            # Check if there's already a running event loop (FastAPI case)
            try:
                loop = asyncio.get_running_loop()
                # If we have a running loop, we need to create a new thread
                import threading

                result = [None]
                exception = [None]

                def run_in_new_loop():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result[0] = new_loop.run_until_complete(self.connect_to_server(server_config))
                        new_loop.close()
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=run_in_new_loop)
                thread.start()
                thread.join()

                if exception[0]:
                    raise exception[0]

                return result[0]

            except RuntimeError:
                # No running loop, safe to use standard approach
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.connect_to_server(server_config))
                finally:
                    loop.close()

        except Exception as e:
            self.logger.error(f"Error in connect_to_server_sync: {str(e)}")
            raise

    def call_tool_sync(self, connection_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for call_tool"""
        try:
            # Check if there's already a running event loop (FastAPI case)
            try:
                loop = asyncio.get_running_loop()
                # If we have a running loop, we need to create a new thread
                import threading

                result = [None]
                exception = [None]

                def run_in_new_loop():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result[0] = new_loop.run_until_complete(self.call_tool(connection_id, tool_name, arguments))
                        new_loop.close()
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=run_in_new_loop)
                thread.start()
                thread.join()

                if exception[0]:
                    raise exception[0]

                return result[0]

            except RuntimeError:
                # No running loop, safe to use standard approach
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.call_tool(connection_id, tool_name, arguments))
                finally:
                    loop.close()

        except Exception as e:
            self.logger.error(f"Error in call_tool_sync: {str(e)}")
            raise

    async def test_connection(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test connection to an MCP server

        Args:
            server_config: MCP server configuration

        Returns:
            Connection test result with status and details
        """
        start_time = datetime.now()
        connection_result = {
            "server_id": server_config.get("server_id", "unknown"),
            "server_name": server_config.get("server_name", "Unknown"),
            "connection_type": server_config.get("connection", {}).get("connection_type", "unknown"),
            "status": "unknown",
            "latency_ms": 0,
            "error": None,
            "available_tools": [],
            "timestamp": datetime.now().isoformat()
        }

        try:
            connection_type = server_config.get("connection", {}).get("connection_type")

            if connection_type == "stdio":
                result = await self._test_stdio_connection(server_config)
            elif connection_type == "sse":
                result = await self._test_sse_connection(server_config)
            elif connection_type == "http":
                result = await self._test_http_connection(server_config)
            else:
                raise MCPConnectionError(f"Unsupported connection type: {connection_type}")

            connection_result.update(result)
            connection_result["status"] = "success"

        except Exception as e:
            connection_result["status"] = "failed"
            connection_result["error"] = str(e)
            self.logger.error(f"MCP connection test failed: {str(e)}")

        # Calculate latency
        end_time = datetime.now()
        connection_result["latency_ms"] = int((end_time - start_time).total_seconds() * 1000)

        # Store in history
        self.connection_history.append(connection_result)
        if len(self.connection_history) > 100:  # Keep last 100 results
            self.connection_history.pop(0)

        return connection_result

    async def _test_stdio_connection(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test stdio-based MCP server connection"""
        connection = server_config.get("connection", {})
        command = connection.get("command")
        args = connection.get("args", [])
        timeout = connection.get("timeout", 30)

        if not command:
            raise MCPConnectionError("stdio connection requires 'command' field")

        try:
            # Start the process
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=connection.get("env_vars", {})
            )

            # Send initialization message
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "agentscope-paas",
                        "version": "1.0.0"
                    }
                }
            }

            # Write to process and wait for response
            process.stdin.write((json.dumps(init_message) + "\n").encode())
            await process.stdin.drain()

            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=timeout
                )
                response = json.loads(response_line.decode())

                # Get available tools
                tools_message = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }

                process.stdin.write((json.dumps(tools_message) + "\n").encode())
                await process.stdin.drain()

                tools_response = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=timeout
                )
                tools_data = json.loads(tools_response.decode())

                # Clean up process
                process.terminate()
                await process.wait()

                return {
                    "available_tools": tools_data.get("result", {}).get("tools", []),
                    "server_info": response.get("result", {}).get("serverInfo", {})
                }

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise MCPConnectionError(f"Connection timeout after {timeout}s")

        except FileNotFoundError:
            raise MCPConnectionError(f"Command not found: {command}")
        except Exception as e:
            raise MCPConnectionError(f"stdio connection failed: {str(e)}")

    async def _test_sse_connection(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test SSE-based MCP server connection"""
        connection = server_config.get("connection", {})
        url = connection.get("url")
        headers = connection.get("headers", {})
        timeout = connection.get("timeout", 30)

        if not url:
            raise MCPConnectionError("sse connection requires 'url' field")

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Send initialize request
                init_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "agentscope-paas",
                            "version": "1.0.0"
                        }
                    }
                }

                response = await client.post(
                    url,
                    json=init_payload,
                    headers=headers
                )
                response.raise_for_status()
                init_result = response.json()

                # Get available tools
                tools_payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }

                tools_response = await client.post(
                    url,
                    json=tools_payload,
                    headers=headers
                )
                tools_response.raise_for_status()
                tools_data = tools_response.json()

                return {
                    "available_tools": tools_data.get("result", {}).get("tools", []),
                    "server_info": init_result.get("result", {}).get("serverInfo", {})
                }

        except httpx.TimeoutException:
            raise MCPConnectionError(f"Connection timeout after {timeout}s")
        except httpx.HTTPError as e:
            raise MCPConnectionError(f"HTTP connection failed: {str(e)}")

    async def _test_http_connection(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test HTTP-based MCP server connection"""
        connection = server_config.get("connection", {})
        url = connection.get("url")
        headers = connection.get("headers", {})
        timeout = connection.get("timeout", 30)

        if not url:
            raise MCPConnectionError("http connection requires 'url' field")

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Send initialize request
                init_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "agentscope-paas",
                            "version": "1.0.0"
                        }
                    }
                }

                response = await client.post(
                    url,
                    json=init_payload,
                    headers=headers
                )
                response.raise_for_status()
                init_result = response.json()

                # Get available tools
                tools_payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }

                tools_response = await client.post(
                    url,
                    json=tools_payload,
                    headers=headers
                )
                tools_response.raise_for_status()
                tools_data = tools_response.json()

                return {
                    "available_tools": tools_data.get("result", {}).get("tools", []),
                    "server_info": init_result.get("result", {}).get("serverInfo", {})
                }

        except httpx.TimeoutException:
            raise MCPConnectionError(f"Connection timeout after {timeout}s")
        except httpx.HTTPError as e:
            raise MCPConnectionError(f"HTTP connection failed: {str(e)}")

    async def connect_to_server(self, server_config: Dict[str, Any]) -> str:
        """
        Establish persistent connection to MCP server

        Args:
            server_config: MCP server configuration

        Returns:
            Connection ID for managing the connection
        """
        server_id = server_config.get("server_id")
        if not server_id:
            raise MCPConnectionError("server_config must have server_id")

        # Test connection first
        test_result = await self.test_connection(server_config)
        if test_result["status"] != "success":
            raise MCPConnectionError(f"Connection test failed: {test_result.get('error')}")

        # Store connection
        connection_id = f"{server_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_connections[connection_id] = {
            "server_config": server_config,
            "connected_at": datetime.now().isoformat(),
            "status": "active",
            "test_result": test_result
        }

        self.logger.info(f"Connected to MCP server: {server_id} (connection_id: {connection_id})")
        return connection_id

    async def disconnect_from_server(self, connection_id: str) -> bool:
        """
        Disconnect from MCP server

        Args:
            connection_id: Connection ID to disconnect

        Returns:
            True if successful, False otherwise
        """
        if connection_id not in self.active_connections:
            self.logger.warning(f"Connection ID not found: {connection_id}")
            return False

        # Clean up connection resources
        connection_info = self.active_connections[connection_id]
        server_id = connection_info["server_config"].get("server_id")

        # Remove from active connections
        del self.active_connections[connection_id]

        self.logger.info(f"Disconnected from MCP server: {server_id} (connection_id: {connection_id})")
        return True

    async def call_tool(self, connection_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on connected MCP server

        Args:
            connection_id: Connection ID for the server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if connection_id not in self.active_connections:
            raise MCPConnectionError(f"Connection ID not found: {connection_id}")

        connection_info = self.active_connections[connection_id]
        server_config = connection_info["server_config"]
        connection_type = server_config.get("connection", {}).get("connection_type")

        try:
            if connection_type == "stdio":
                return await self._call_stdio_tool(server_config, tool_name, arguments)
            elif connection_type in ["sse", "http"]:
                return await self._call_http_tool(server_config, tool_name, arguments)
            else:
                raise MCPConnectionError(f"Unsupported connection type: {connection_type}")

        except Exception as e:
            self.logger.error(f"Tool call failed: {str(e)}")
            raise MCPConnectionError(f"Tool call failed: {str(e)}")

    async def _call_stdio_tool(self, server_config: Dict[str, Any], tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call tool via stdio connection"""
        # Implementation for stdio tool calls
        # This would involve process communication
        pass

    async def _call_http_tool(self, server_config: Dict[str, Any], tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call tool via HTTP/SSE connection"""
        connection = server_config.get("connection", {})
        url = connection.get("url")
        headers = connection.get("headers", {})

        tool_call_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=tool_call_payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def get_connection_status(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific connection

        Args:
            connection_id: Connection ID to check

        Returns:
            Connection status information or None
        """
        return self.active_connections.get(connection_id)

    def get_all_connections(self) -> Dict[str, Any]:
        """
        Get all active connections

        Returns:
            Dictionary of all active connections
        """
        return self.active_connections.copy()

    def get_connection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent connection test history

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of recent connection test results
        """
        return self.connection_history[-limit:]


# Singleton instance for convenient usage
mcp_client = MCPClient()