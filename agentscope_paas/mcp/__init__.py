"""
MCP (Model Context Protocol) Package for AgentScope-PaaS

This package provides MCP server connection handling and tool integration.
"""

from .client import MCPClient, MCPConnectionError, mcp_client

__all__ = [
    'MCPClient',
    'MCPConnectionError',
    'mcp_client'
]