"""
Tool Registry System for AgentScope-PaaS

This module provides a comprehensive tool registry system for managing
built-in tools and MCP-provided tools with security, validation, and execution management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum


class ToolPermissionLevel(Enum):
    """Tool permission security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolCategory(Enum):
    """Tool categories"""
    DATA_ANALYSIS = "data_analysis"
    TEXT_PROCESSING = "text_processing"
    API_TOOLS = "api_tools"
    FILE_OPERATIONS = "file_operations"
    COMMUNICATION = "communication"
    WEB_TOOLS = "web_tools"


class ToolExecutionError(Exception):
    """Tool execution related errors"""
    pass


class ToolValidationException(Exception):
    """Tool validation errors"""
    pass


class ToolRegistry:
    """Central registry for managing built-in and MCP tools"""

    def __init__(self):
        """Initialize tool registry"""
        self.logger = self._get_logger()
        self.built_in_tools: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        self.tool_categories: Dict[str, Dict[str, Any]] = {}
        self.execution_stats: Dict[str, Dict[str, Any]] = {}
        self._initialize_built_in_tools()

    def _get_logger(self):
        """Get logger instance"""
        try:
            from agentscope_paas.utils.logger import get_logger
            return get_logger(__name__)
        except ImportError:
            logging.basicConfig(level=logging.INFO)
            return logging.getLogger(__name__)

    # Synchronous wrapper methods for FastAPI compatibility
    def execute_tool_sync(self, tool_id: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous wrapper for execute_tool"""
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
                        result[0] = new_loop.run_until_complete(self.execute_tool(tool_id, arguments, context))
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
                    return loop.run_until_complete(self.execute_tool(tool_id, arguments, context))
                finally:
                    loop.close()

        except Exception as e:
            self.logger.error(f"Error in execute_tool_sync: {str(e)}")
            raise

    def _initialize_built_in_tools(self):
        """Initialize built-in tool library"""
        built_in_tools = [
            {
                "tool_id": "csv_analyzer",
                "tool_name": "CSV Analyzer",
                "category": ToolCategory.DATA_ANALYSIS.value,
                "description": "Analyze CSV files and generate statistics",
                "version": "1.0.0",
                "parameters": [
                    {
                        "name": "file_path",
                        "type": "string",
                        "required": True,
                        "description": "Path to CSV file"
                    },
                    {
                        "name": "analysis_type",
                        "type": "string",
                        "required": False,
                        "default": "basic",
                        "description": "Type of analysis: basic, advanced, or statistical"
                    }
                ],
                "execution_config": {
                    "timeout": 30,
                    "retry_count": 2,
                    "memory_limit_mb": 512
                },
                "permissions": {
                    "enabled": True,
                    "max_calls_per_conversation": 10,
                    "security_level": ToolPermissionLevel.MEDIUM.value,
                    "require_user_confirmation": False
                }
            },
            {
                "tool_id": "text_summarizer",
                "tool_name": "Text Summarizer",
                "category": ToolCategory.TEXT_PROCESSING.value,
                "description": "Summarize long text content",
                "version": "1.0.0",
                "parameters": [
                    {
                        "name": "text",
                        "type": "string",
                        "required": True,
                        "description": "Text to summarize"
                    },
                    {
                        "name": "max_length",
                        "type": "number",
                        "required": False,
                        "default": 200,
                        "description": "Maximum summary length"
                    }
                ],
                "execution_config": {
                    "timeout": 15,
                    "retry_count": 1,
                    "memory_limit_mb": 256
                },
                "permissions": {
                    "enabled": True,
                    "max_calls_per_conversation": 20,
                    "security_level": ToolPermissionLevel.LOW.value,
                    "require_user_confirmation": False
                }
            },
            {
                "tool_id": "json_parser",
                "tool_name": "JSON Parser",
                "category": ToolCategory.DATA_ANALYSIS.value,
                "description": "Parse and validate JSON data",
                "version": "1.0.0",
                "parameters": [
                    {
                        "name": "json_string",
                        "type": "string",
                        "required": True,
                        "description": "JSON string to parse"
                    },
                    {
                        "name": "schema",
                        "type": "object",
                        "required": False,
                        "description": "JSON schema for validation"
                    }
                ],
                "execution_config": {
                    "timeout": 10,
                    "retry_count": 1,
                    "memory_limit_mb": 128
                },
                "permissions": {
                    "enabled": True,
                    "max_calls_per_conversation": 50,
                    "security_level": ToolPermissionLevel.LOW.value,
                    "require_user_confirmation": False
                }
            },
            {
                "tool_id": "web_scraper",
                "tool_name": "Web Scraper",
                "category": ToolCategory.WEB_TOOLS.value,
                "description": "Extract content from web pages",
                "version": "1.0.0",
                "parameters": [
                    {
                        "name": "url",
                        "type": "string",
                        "required": True,
                        "description": "URL to scrape"
                    },
                    {
                        "name": "extract_text",
                        "type": "boolean",
                        "required": False,
                        "default": True,
                        "description": "Extract text content"
                    }
                ],
                "execution_config": {
                    "timeout": 30,
                    "retry_count": 2,
                    "memory_limit_mb": 512
                },
                "permissions": {
                    "enabled": True,
                    "max_calls_per_conversation": 5,
                    "security_level": ToolPermissionLevel.HIGH.value,
                    "require_user_confirmation": True
                }
            },
            {
                "tool_id": "file_reader",
                "tool_name": "File Reader",
                "category": ToolCategory.FILE_OPERATIONS.value,
                "description": "Read file contents safely",
                "version": "1.0.0",
                "parameters": [
                    {
                        "name": "file_path",
                        "type": "string",
                        "required": True,
                        "description": "Path to file"
                    },
                    {
                        "name": "max_size_mb",
                        "type": "number",
                        "required": False,
                        "default": 10,
                        "description": "Maximum file size in MB"
                    }
                ],
                "execution_config": {
                    "timeout": 20,
                    "retry_count": 1,
                    "memory_limit_mb": 1024
                },
                "permissions": {
                    "enabled": True,
                    "max_calls_per_conversation": 15,
                    "security_level": ToolPermissionLevel.MEDIUM.value,
                    "require_user_confirmation": False
                }
            }
        ]

        # Register built-in tools
        for tool in built_in_tools:
            self.register_built_in_tool(tool)

        # Initialize categories
        self._initialize_categories()

    def _initialize_categories(self):
        """Initialize tool categories"""
        categories = [
            {
                "category_id": ToolCategory.DATA_ANALYSIS.value,
                "category_name": "Data Analysis",
                "description": "Tools for analyzing and processing data",
                "tools": ["csv_analyzer", "json_parser"],
                "icon": "📊",
                "enabled_by_default": True
            },
            {
                "category_id": ToolCategory.TEXT_PROCESSING.value,
                "category_name": "Text Processing",
                "description": "Tools for processing and manipulating text",
                "tools": ["text_summarizer"],
                "icon": "📝",
                "enabled_by_default": True
            },
            {
                "category_id": ToolCategory.WEB_TOOLS.value,
                "category_name": "Web Tools",
                "description": "Tools for web operations and scraping",
                "tools": ["web_scraper"],
                "icon": "🌐",
                "enabled_by_default": True
            },
            {
                "category_id": ToolCategory.FILE_OPERATIONS.value,
                "category_name": "File Operations",
                "description": "Tools for file system operations",
                "tools": ["file_reader"],
                "icon": "📁",
                "enabled_by_default": True
            }
        ]

        for category in categories:
            self.tool_categories[category["category_id"]] = category

    def register_built_in_tool(self, tool_config: Dict[str, Any]) -> bool:
        """
        Register a built-in tool

        Args:
            tool_config: Tool configuration dictionary

        Returns:
            True if registration successful, False otherwise
        """
        try:
            tool_id = tool_config.get("tool_id")
            if not tool_id:
                raise ToolValidationException("tool_config must have tool_id")

            # Validate tool configuration
            self._validate_tool_config(tool_config)

            # Register tool
            self.built_in_tools[tool_id] = {
                **tool_config,
                "registered_at": datetime.now().isoformat(),
                "type": "built_in"
            }

            # Initialize execution stats
            self.execution_stats[tool_id] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "average_execution_time": 0.0,
                "last_executed": None
            }

            self.logger.info(f"Registered built-in tool: {tool_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_config.get('tool_id', 'unknown')}: {str(e)}")
            return False

    def register_mcp_tool(self, tool_config: Dict[str, Any], server_id: str) -> bool:
        """
        Register an MCP-provided tool

        Args:
            tool_config: Tool configuration from MCP server
            server_id: MCP server ID

        Returns:
            True if registration successful, False otherwise
        """
        try:
            tool_id = tool_config.get("name") or tool_config.get("tool_id")
            if not tool_id:
                raise ToolValidationException("MCP tool config must have name or tool_id")

            # Convert MCP tool format to internal format
            internal_tool_config = {
                "tool_id": f"mcp_{server_id}_{tool_id}",
                "tool_name": tool_config.get("name", tool_id),
                "category": ToolCategory.API_TOOLS.value,
                "description": tool_config.get("description", ""),
                "version": "1.0.0",
                "parameters": self._convert_mcp_parameters(tool_config.get("inputSchema", {})),
                "execution_config": {
                    "timeout": 30,
                    "retry_count": 1,
                    "memory_limit_mb": 256
                },
                "permissions": {
                    "enabled": True,
                    "max_calls_per_conversation": 50,
                    "security_level": ToolPermissionLevel.MEDIUM.value,
                    "require_user_confirmation": False
                },
                "mcp_info": {
                    "server_id": server_id,
                    "original_name": tool_id,
                    "mcp_tool": tool_config
                },
                "type": "mcp"
            }

            self.mcp_tools[internal_tool_config["tool_id"]] = {
                **internal_tool_config,
                "registered_at": datetime.now().isoformat()
            }

            # Initialize execution stats
            self.execution_stats[internal_tool_config["tool_id"]] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "average_execution_time": 0.0,
                "last_executed": None
            }

            self.logger.info(f"Registered MCP tool: {internal_tool_config['tool_id']} from server: {server_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register MCP tool: {str(e)}")
            return False

    def _convert_mcp_parameters(self, input_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert MCP parameter schema to internal format"""
        parameters = []
        properties = input_schema.get("properties", {})
        required_fields = input_schema.get("required", [])

        for param_name, param_info in properties.items():
            parameter = {
                "name": param_name,
                "type": param_info.get("type", "string"),
                "required": param_name in required_fields,
                "description": param_info.get("description", ""),
                "default": param_info.get("default")
            }
            parameters.append(parameter)

        return parameters

    def _validate_tool_config(self, tool_config: Dict[str, Any]) -> bool:
        """
        Validate tool configuration

        Args:
            tool_config: Tool configuration to validate

        Returns:
            True if valid, raises exception otherwise
        """
        required_fields = ["tool_id", "tool_name", "category", "description", "version", "parameters", "execution_config", "permissions"]
        for field in required_fields:
            if field not in tool_config:
                raise ToolValidationException(f"Missing required field: {field}")

        # Validate parameters
        for param in tool_config.get("parameters", []):
            if "name" not in param or "type" not in param:
                raise ToolValidationException("Parameter must have name and type")

        # Validate execution config
        exec_config = tool_config.get("execution_config", {})
        if "timeout" not in exec_config:
            raise ToolValidationException("execution_config must have timeout")

        return True

    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tool configuration by ID

        Args:
            tool_id: Tool ID to retrieve

        Returns:
            Tool configuration or None if not found
        """
        # Check built-in tools first
        if tool_id in self.built_in_tools:
            return self.built_in_tools[tool_id]

        # Check MCP tools
        if tool_id in self.mcp_tools:
            return self.mcp_tools[tool_id]

        return None

    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all tools in a specific category

        Args:
            category: Tool category

        Returns:
            List of tool configurations
        """
        tools = []
        all_tools = {**self.built_in_tools, **self.mcp_tools}

        for tool_id, tool_config in all_tools.items():
            if tool_config.get("category") == category:
                tools.append(tool_config)

        return tools

    def get_all_tools(self, include_disabled: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered tools

        Args:
            include_disabled: Whether to include disabled tools

        Returns:
            Dictionary of all tools
        """
        all_tools = {**self.built_in_tools, **self.mcp_tools}

        if not include_disabled:
            all_tools = {
                tool_id: tool_config
                for tool_id, tool_config in all_tools.items()
                if tool_config.get("permissions", {}).get("enabled", True)
            }

        return all_tools

    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tool categories

        Returns:
            Dictionary of categories
        """
        return self.tool_categories.copy()

    async def execute_tool(self, tool_id: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a tool

        Args:
            tool_id: Tool ID to execute
            arguments: Tool arguments
            context: Execution context (optional)

        Returns:
            Tool execution result
        """
        tool_config = self.get_tool(tool_id)
        if not tool_config:
            raise ToolExecutionError(f"Tool not found: {tool_id}")

        # Check permissions
        if not tool_config.get("permissions", {}).get("enabled", True):
            raise ToolExecutionError(f"Tool is disabled: {tool_id}")

        # Validate arguments
        self._validate_tool_arguments(tool_config, arguments)

        # Check execution limits
        if not self._check_execution_limits(tool_id, tool_config):
            raise ToolExecutionError(f"Execution limits exceeded for tool: {tool_id}")

        # Execute tool
        start_time = datetime.now()
        try:
            if tool_config.get("type") == "built_in":
                result = await self._execute_built_in_tool(tool_config, arguments, context)
            elif tool_config.get("type") == "mcp":
                result = await self._execute_mcp_tool(tool_config, arguments, context)
            else:
                raise ToolExecutionError(f"Unknown tool type: {tool_config.get('type')}")

            # Update execution stats
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(tool_id, True, execution_time)

            return {
                "success": True,
                "result": result,
                "tool_id": tool_id,
                "execution_time": execution_time
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(tool_id, False, execution_time)
            raise ToolExecutionError(f"Tool execution failed: {str(e)}")

    def _validate_tool_arguments(self, tool_config: Dict[str, Any], arguments: Dict[str, Any]):
        """Validate tool arguments against parameter schema"""
        parameters = tool_config.get("parameters", [])

        for param in parameters:
            param_name = param.get("name")
            if param.get("required") and param_name not in arguments:
                raise ToolValidationException(f"Missing required parameter: {param_name}")

            # Add validation for parameter types, ranges, etc.
            if param_name in arguments:
                expected_type = param.get("type")
                if expected_type == "string" and not isinstance(arguments[param_name], str):
                    raise ToolValidationException(f"Parameter {param_name} must be string")

    def _check_execution_limits(self, tool_id: str, tool_config: Dict[str, Any]) -> bool:
        """Check if tool execution limits are within bounds"""
        permissions = tool_config.get("permissions", {})
        max_calls = permissions.get("max_calls_per_conversation")
        stats = self.execution_stats.get(tool_id, {})

        if max_calls and stats.get("total_calls", 0) >= max_calls:
            return False

        return True

    def _update_execution_stats(self, tool_id: str, success: bool, execution_time: float):
        """Update tool execution statistics"""
        if tool_id not in self.execution_stats:
            return

        stats = self.execution_stats[tool_id]
        stats["total_calls"] += 1

        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1

        # Update average execution time
        total_time = stats.get("average_execution_time", 0) * (stats["total_calls"] - 1) + execution_time
        stats["average_execution_time"] = total_time / stats["total_calls"]
        stats["last_executed"] = datetime.now().isoformat()

    async def _execute_built_in_tool(self, tool_config: Dict[str, Any], arguments: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Execute built-in tool"""
        tool_id = tool_config.get("tool_id")

        # Built-in tool implementations
        if tool_id == "csv_analyzer":
            return await self._csv_analyzer(arguments, context)
        elif tool_id == "text_summarizer":
            return await self._text_summarizer(arguments, context)
        elif tool_id == "json_parser":
            return await self._json_parser(arguments, context)
        elif tool_id == "web_scraper":
            return await self._web_scraper(arguments, context)
        elif tool_id == "file_reader":
            return await self._file_reader(arguments, context)
        else:
            raise ToolExecutionError(f"Built-in tool not implemented: {tool_id}")

    async def _execute_mcp_tool(self, tool_config: Dict[str, Any], arguments: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Execute MCP tool"""
        try:
            from agentscope_paas.mcp.client import mcp_client

            mcp_info = tool_config.get("mcp_info", {})
            server_id = mcp_info.get("server_id")
            original_name = mcp_info.get("original_name")

            # Find active connection to the MCP server
            connections = mcp_client.get_all_connections()
            connection_id = None

            for conn_id, conn_info in connections.items():
                if conn_info.get("server_config", {}).get("server_id") == server_id:
                    connection_id = conn_id
                    break

            if not connection_id:
                raise ToolExecutionError(f"No active connection to MCP server: {server_id}")

            # Call the tool
            result = await mcp_client.call_tool(connection_id, original_name, arguments)
            return result

        except Exception as e:
            raise ToolExecutionError(f"MCP tool execution failed: {str(e)}")

    # Built-in tool implementations
    async def _csv_analyzer(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """CSV analyzer implementation"""
        import pandas as pd
        import os

        file_path = arguments.get("file_path")
        analysis_type = arguments.get("analysis_type", "basic")

        if not os.path.exists(file_path):
            raise ToolExecutionError(f"File not found: {file_path}")

        try:
            df = pd.read_csv(file_path)

            if analysis_type == "basic":
                result = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data_types": df.dtypes.astype(str).to_dict(),
                    "missing_values": df.isnull().sum().to_dict(),
                    "preview": df.head(5).to_dict()
                }
            elif analysis_type == "advanced":
                result = {
                    "basic": {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": list(df.columns)
                    },
                    "statistics": df.describe().to_dict(),
                    "correlations": df.corr().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 1 else {}
                }
            else:  # statistical
                result = {
                    "statistics": df.describe().to_dict(),
                    "skewness": df.skew().to_dict(),
                    "kurtosis": df.kurtosis().to_dict()
                }

            return result

        except Exception as e:
            raise ToolExecutionError(f"CSV analysis failed: {str(e)}")

    async def _text_summarizer(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        """Text summarizer implementation"""
        text = arguments.get("text", "")
        max_length = arguments.get("max_length", 200)

        # Simple extractive summarization
        sentences = text.split('.')
        if len(sentences) <= 2:
            return text

        # Take first few sentences up to max_length
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence.strip() + ". "
            else:
                break

        return summary.strip()

    async def _json_parser(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """JSON parser implementation"""
        import json
        from jsonschema import validate, ValidationError

        json_string = arguments.get("json_string", "")
        schema = arguments.get("schema")

        try:
            data = json.loads(json_string)

            if schema:
                try:
                    validate(instance=data, schema=schema)
                    return {"valid": True, "data": data}
                except ValidationError as e:
                    return {"valid": False, "error": str(e), "data": data}

            return {"valid": True, "data": data}

        except json.JSONDecodeError as e:
            raise ToolExecutionError(f"Invalid JSON: {str(e)}")

    async def _web_scraper(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Web scraper implementation"""
        from bs4 import BeautifulSoup
        import httpx

        url = arguments.get("url", "")
        extract_text = arguments.get("extract_text", True)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30)
                response.raise_for_status()

                if extract_text:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)

                    return {
                        "url": url,
                        "title": soup.title.string if soup.title else "",
                        "content": text[:10000],  # Limit to 10000 characters
                        "content_length": len(text)
                    }
                else:
                    return {
                        "url": url,
                        "html": response.text[:50000],  # Limit to 50000 characters
                        "status_code": response.status_code
                    }

        except Exception as e:
            raise ToolExecutionError(f"Web scraping failed: {str(e)}")

    async def _file_reader(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """File reader implementation"""
        import os

        file_path = arguments.get("file_path", "")
        max_size_mb = arguments.get("max_size_mb", 10)

        if not os.path.exists(file_path):
            raise ToolExecutionError(f"File not found: {file_path}")

        try:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024

            if file_size > max_size_bytes:
                raise ToolExecutionError(f"File too large: {file_size} bytes exceeds limit {max_size_bytes} bytes")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "file_path": file_path,
                "file_size": file_size,
                "content": content,
                "encoding": "utf-8"
            }

        except Exception as e:
            raise ToolExecutionError(f"File reading failed: {str(e)}")

    def get_execution_stats(self, tool_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics

        Args:
            tool_id: Specific tool ID or None for all tools

        Returns:
            Execution statistics
        """
        if tool_id:
            return self.execution_stats.get(tool_id, {})
        return self.execution_stats.copy()


# Singleton instance for convenient usage
tool_registry = ToolRegistry()