# AgentScope

AgentScope is a production-ready, developer-centric multi-agent framework designed to work with increasingly capable LLMs. It provides essential abstractions for building agentic applications with built-in support for tool calling, memory management, multi-agent orchestration, MCP protocol integration, RAG, and model finetuning. The framework leverages models' reasoning and tool-use abilities rather than constraining them with strict prompts and opinionated orchestrations.

The framework supports multiple LLM providers including DashScope (Qwen), OpenAI, Anthropic, Gemini, and Ollama. It features real-time voice agents, human-in-the-loop steering with interruption handling, structured output generation, and comprehensive observability through OpenTelemetry integration. AgentScope also includes AgentScope Studio for visualization and deployment capabilities for local, serverless, or Kubernetes environments.

## Installation

Install AgentScope from PyPI for quick setup.

```bash
pip install agentscope
# or with uv:
uv pip install agentscope
```

## ReActAgent - Creating Conversational AI Agents

The ReActAgent is the primary agent implementation in AgentScope, supporting reasoning-acting loops, parallel tool calling, memory management, and structured output generation.

```python
import asyncio
import os
from agentscope.agent import ReActAgent, UserAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit, execute_shell_command, execute_python_code, view_text_file


async def main():
    # Create and configure toolkit with built-in tools
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_shell_command)
    toolkit.register_tool_function(execute_python_code)
    toolkit.register_tool_function(view_text_file)

    # Initialize ReAct agent with model, formatter, memory and toolkit
    agent = ReActAgent(
        name="Friday",
        sys_prompt="You are a helpful assistant named Friday.",
        model=DashScopeChatModel(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            model_name="qwen-max",
            enable_thinking=False,
            stream=True,
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
        max_iters=10,  # Maximum reasoning-acting iterations
        parallel_tool_calls=False,  # Execute tools sequentially or in parallel
    )

    user = UserAgent("User")

    # Conversation loop
    msg = None
    while True:
        msg = await user(msg)
        if msg.get_text_content() == "exit":
            break
        msg = await agent(msg)

asyncio.run(main())
```

## Toolkit - Tool Registration and Management

The Toolkit class manages tool functions with support for grouping, activation/deactivation, and MCP client integration.

```python
import asyncio
from agentscope.tool import Toolkit, ToolResponse, execute_python_code
from agentscope.message import TextBlock


# Define a custom tool function
def calculate_sum(numbers: list[int]) -> ToolResponse:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: A list of integers to sum

    Returns:
        ToolResponse containing the sum result
    """
    total = sum(numbers)
    return ToolResponse(
        content=[TextBlock(type="text", text=f"The sum is: {total}")],
    )


async def main():
    toolkit = Toolkit()

    # Register a built-in tool function
    toolkit.register_tool_function(execute_python_code)

    # Register a custom tool function
    toolkit.register_tool_function(calculate_sum)

    # Create a tool group for organization
    toolkit.create_tool_group(
        group_name="math_tools",
        description="Tools for mathematical calculations",
        active=True,  # Active groups are included in JSON schemas
        notes="Use these tools for numerical computations",
    )

    # Register tool to a specific group
    toolkit.register_tool_function(
        calculate_sum,
        group_name="math_tools",
        func_name="sum_numbers",  # Custom name override
        namesake_strategy="override",  # Handle name conflicts: raise/override/skip/rename
    )

    # Get JSON schemas for active tool functions
    schemas = toolkit.get_json_schemas()
    print(f"Registered tools: {[s['function']['name'] for s in schemas]}")

    # Activate/deactivate tool groups dynamically
    toolkit.update_tool_groups(["math_tools"], active=False)

asyncio.run(main())
```

## MCP Integration - Model Context Protocol Tools

AgentScope provides flexible MCP (Model Context Protocol) integration with support for stateful and stateless clients, and both SSE and StreamableHTTP transports.

```python
import asyncio
import os
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.mcp import HttpStatelessClient, HttpStatefulClient
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit


async def main():
    toolkit = Toolkit()

    # Stateful MCP client (maintains connection) - requires connect/close
    stateful_client = HttpStatefulClient(
        name="math_mcp",
        transport="sse",  # Server-Sent Events transport
        url="http://127.0.0.1:8001/sse",
    )
    await stateful_client.connect()

    # Stateless MCP client (connection per request)
    stateless_client = HttpStatelessClient(
        name="utility_mcp",
        transport="streamable_http",  # StreamableHTTP transport
        url="http://127.0.0.1:8002/mcp",
    )

    # Register all tools from MCP clients
    await toolkit.register_mcp_client(
        stateful_client,
        group_name="basic",
        enable_funcs=["add", "subtract"],  # Only register specific functions
        disable_funcs=None,  # Or exclude specific functions
        namesake_strategy="rename",  # Auto-rename on conflicts
    )
    await toolkit.register_mcp_client(stateless_client)

    # Get individual MCP tool as callable function for direct use
    add_func = await stateful_client.get_callable_function(
        func_name="add",
        wrap_tool_result=True,  # Wrap result in ToolResponse
    )

    # Call MCP tool directly
    result = await add_func(a=5, b=10)
    print(f"Direct call result: {result}")

    # Use with ReActAgent
    agent = ReActAgent(
        name="Calculator",
        sys_prompt="You are a calculator assistant.",
        model=DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ["DASHSCOPE_API_KEY"],
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
    )

    response = await agent(Msg("user", "What is 2345 * 3456 + 4567?", "user"))
    print(response.get_text_content())

    # Clean up stateful client
    await stateful_client.close()

asyncio.run(main())
```

## Structured Output - Type-Safe Responses

Generate structured, validated output from agents using Pydantic models.

```python
import asyncio
import json
import os
from typing import Literal
from pydantic import BaseModel, Field
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit


class PersonInfo(BaseModel):
    """Structured model for person information."""
    name: str = Field(description="The name of the person")
    age: int = Field(description="The age of the person", ge=0, le=120)
    intro: str = Field(description="A one-sentence introduction")
    honors: list[str] = Field(description="List of honors received")


class FruitChoice(BaseModel):
    """Structured model for fruit selection."""
    choice: Literal["apple", "banana", "orange"] = Field(
        description="Your choice of fruit"
    )


async def main():
    agent = ReActAgent(
        name="Friday",
        sys_prompt="You are a helpful assistant named Friday.",
        model=DashScopeChatModel(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            model_name="qwen-max",
            stream=True,
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=Toolkit(),
        memory=InMemoryMemory(),
    )

    # Request structured output with PersonInfo model
    response = await agent(
        Msg("user", "Please introduce Einstein", "user"),
        structured_model=PersonInfo,  # Pass Pydantic model for validation
    )

    # Structured data is in response.metadata
    print("Structured Output:")
    print(json.dumps(response.metadata, indent=4))
    # Output: {"name": "Albert Einstein", "age": 76, "intro": "...", "honors": [...]}

    # Request with constrained choices
    response = await agent(
        Msg("user", "Choose one of your favorite fruit", "user"),
        structured_model=FruitChoice,
    )
    print(f"Choice: {response.metadata['choice']}")  # One of: apple, banana, orange

asyncio.run(main())
```

## MsgHub and Pipelines - Multi-Agent Orchestration

MsgHub provides message broadcasting and subscription management for multi-agent conversations.

```python
import asyncio
import os
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.pipeline import MsgHub, sequential_pipeline, fanout_pipeline


def create_agent(name: str, role: str) -> ReActAgent:
    """Create an agent with a specific role."""
    return ReActAgent(
        name=name,
        sys_prompt=f"You are {name}, a {role}.",
        model=DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ["DASHSCOPE_API_KEY"],
            stream=True,
        ),
        # Use MultiAgentFormatter for multi-entity conversations
        formatter=DashScopeMultiAgentFormatter(),
    )


async def main():
    # Create participant agents
    alice = create_agent("Alice", "friendly teacher")
    bob = create_agent("Bob", "curious student")
    charlie = create_agent("Charlie", "thoughtful doctor")

    # MsgHub manages message broadcasting among participants
    async with MsgHub(
        participants=[alice, bob, charlie],
        # Announcement is broadcast to all participants on entry
        announcement=Msg(
            "system",
            "Please introduce yourselves briefly.",
            "system",
        ),
        enable_auto_broadcast=True,  # Auto-broadcast replies to all
    ) as hub:
        # Sequential pipeline: agents respond one after another
        await sequential_pipeline([alice, bob, charlie])

        # Dynamic participant management
        hub.delete(bob)  # Remove Bob from conversation
        await hub.broadcast(Msg(
            "bob",
            "I have to leave now, goodbye!",
            "assistant",
        ))

        # Add new participant
        david = create_agent("David", "software engineer")
        hub.add(david)

        # Continue conversation with remaining participants
        await alice()
        await charlie()
        await david()

    # Fanout pipeline: agents respond concurrently
    async with MsgHub(
        participants=[alice, bob, charlie],
        announcement=Msg("system", "What do you think about AI?", "system"),
    ):
        # All agents respond in parallel
        responses = await fanout_pipeline([alice, bob, charlie])
        for resp in responses:
            print(f"{resp.name}: {resp.get_text_content()[:100]}...")

asyncio.run(main())
```

## RAG - Retrieval-Augmented Generation

Build knowledge bases with document readers, vector stores, and embedding models for enhanced agent responses.

```python
import asyncio
import os
from agentscope.embedding import DashScopeTextEmbedding
from agentscope.rag import (
    TextReader,
    PDFReader,
    QdrantStore,
    SimpleKnowledge,
)


async def main():
    # Create document readers with chunking configuration
    text_reader = TextReader(chunk_size=1024)
    pdf_reader = PDFReader(
        chunk_size=1024,
        split_by="sentence",  # Split by: sentence, paragraph, page
    )

    # Read text content
    documents = await text_reader(
        text="AgentScope is a multi-agent framework. "
        "It supports tool calling, memory management, and RAG."
    )

    # Read PDF files
    pdf_documents = await pdf_reader(pdf_path="./documents/manual.pdf")

    # Create knowledge base with vector store and embedding model
    knowledge = SimpleKnowledge(
        embedding_store=QdrantStore(
            location=":memory:",  # In-memory storage, or path for persistence
            collection_name="docs_collection",
            dimensions=1024,  # Must match embedding model dimensions
        ),
        embedding_model=DashScopeTextEmbedding(
            api_key=os.environ["DASHSCOPE_API_KEY"],
            model_name="text-embedding-v4",
        ),
    )

    # Add documents to knowledge base
    await knowledge.add_documents(documents + pdf_documents)

    # Retrieve relevant documents
    results = await knowledge.retrieve(
        query="What is AgentScope?",
        limit=3,  # Maximum documents to return
        score_threshold=0.7,  # Minimum similarity score
    )

    for doc in results:
        print(f"Score: {doc.score:.3f}")
        print(f"Content: {doc.metadata.content['text'][:200]}...")
        print("---")

asyncio.run(main())
```

## Memory Management - Working and Long-Term Memory

AgentScope provides flexible memory solutions including in-memory, Redis, SQLAlchemy, and long-term memory with mem0 integration.

```python
import asyncio
import os
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory, Mem0LongTermMemory
from agentscope.embedding import DashScopeTextEmbedding
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit
from agentscope.token import CharTokenCounter


async def main():
    model = DashScopeChatModel(
        model_name="qwen-max",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        stream=True,
    )

    # Long-term memory with mem0 for persistent storage
    long_term_memory = Mem0LongTermMemory(
        agent_name="Friday",
        user_name="user_123",
        model=model,
        embedding_model=DashScopeTextEmbedding(
            model_name="text-embedding-v3",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            dimensions=1024,
        ),
    )

    # Agent with memory compression for long conversations
    agent = ReActAgent(
        name="Friday",
        sys_prompt="You are a helpful assistant named Friday.",
        model=model,
        formatter=DashScopeChatFormatter(),
        toolkit=Toolkit(),
        memory=InMemoryMemory(),
        long_term_memory=long_term_memory,
        long_term_memory_mode="both",  # agent_control, static_control, or both
        # Enable auto memory compression for long conversations
        compression_config=ReActAgent.CompressionConfig(
            enable=True,
            agent_token_counter=CharTokenCounter(),
            trigger_threshold=8000,  # Compress when tokens exceed threshold
            keep_recent=3,  # Keep recent messages uncompressed
        ),
    )

    # Conversation that builds memory
    await agent(Msg("user", "My name is Alice and I love hiking.", "user"))
    await agent(Msg("user", "What's my name and hobby?", "user"))

    # Access working memory
    history = await agent.memory.get_memory()
    print(f"Messages in memory: {len(history)}")

    # Clear memory
    await agent.memory.clear()

asyncio.run(main())
```

## Model Providers - Multi-Provider Support

AgentScope supports multiple LLM providers with consistent interfaces.

```python
import os
from agentscope.model import (
    DashScopeChatModel,
    OpenAIChatModel,
    AnthropicChatModel,
    GeminiChatModel,
    OllamaChatModel,
)
from agentscope.formatter import (
    DashScopeChatFormatter,
    OpenAIChatFormatter,
    AnthropicChatFormatter,
    GeminiChatFormatter,
    OllamaChatFormatter,
)


# DashScope (Alibaba Qwen models)
dashscope_model = DashScopeChatModel(
    model_name="qwen-max",
    api_key=os.environ["DASHSCOPE_API_KEY"],
    stream=True,
    enable_thinking=False,  # Enable chain-of-thought for supported models
)
dashscope_formatter = DashScopeChatFormatter()

# OpenAI
openai_model = OpenAIChatModel(
    model_name="gpt-4o",
    api_key=os.environ["OPENAI_API_KEY"],
    stream=True,
)
openai_formatter = OpenAIChatFormatter()

# Anthropic Claude
anthropic_model = AnthropicChatModel(
    model_name="claude-3-5-sonnet-20241022",
    api_key=os.environ["ANTHROPIC_API_KEY"],
    stream=True,
)
anthropic_formatter = AnthropicChatFormatter()

# Google Gemini
gemini_model = GeminiChatModel(
    model_name="gemini-pro",
    api_key=os.environ["GOOGLE_API_KEY"],
    stream=True,
)
gemini_formatter = GeminiChatFormatter()

# Ollama (local models)
ollama_model = OllamaChatModel(
    model_name="llama3.1",
    api_url="http://localhost:11434",
    stream=True,
)
ollama_formatter = OllamaChatFormatter()

# Use with ReActAgent
from agentscope.agent import ReActAgent
agent = ReActAgent(
    name="Assistant",
    sys_prompt="You are a helpful assistant.",
    model=openai_model,  # Swap model provider easily
    formatter=openai_formatter,  # Use matching formatter
)
```

## Initialization and Tracing - Project Setup and Observability

Initialize AgentScope with logging, tracing, and studio integration.

```python
import agentscope
from agentscope.tracing import setup_tracing


# Full initialization with all features
agentscope.init(
    project="my_agent_project",  # Project name for organization
    name="chat_session_001",  # Run name for identification
    run_id="unique_run_id",  # Unique identifier for this run
    logging_path="./logs",  # Path to save log files
    logging_level="INFO",  # DEBUG, INFO, WARNING, ERROR
    studio_url="http://localhost:3000",  # AgentScope Studio URL
    tracing_url="http://localhost:4318/v1/traces",  # OpenTelemetry endpoint
)

# Or setup tracing separately for third-party platforms
# Compatible with Arize-Phoenix, Langfuse, and other OTLP platforms
setup_tracing(endpoint="http://localhost:4318/v1/traces")

# Access configuration
print(f"Version: {agentscope.__version__}")
print(f"Run ID: {agentscope._config.run_id}")
print(f"Project: {agentscope._config.project}")
```

## Agent Hooks - Pre/Post Processing

Register hooks for agent lifecycle events for logging, monitoring, or behavior modification.

```python
import asyncio
from agentscope.agent import ReActAgent, AgentBase
from agentscope.message import Msg


# Define hook functions
async def log_pre_reply(agent: AgentBase, kwargs: dict) -> dict | None:
    """Pre-reply hook: log incoming message."""
    msg = kwargs.get("msg")
    if msg:
        print(f"[PRE-REPLY] {agent.name} received: {msg.get_text_content()[:50]}...")
    return None  # Return modified kwargs or None to keep original


async def log_post_reply(agent: AgentBase, kwargs: dict, output: Msg) -> Msg | None:
    """Post-reply hook: log outgoing message."""
    print(f"[POST-REPLY] {agent.name} responded: {output.get_text_content()[:50]}...")
    return None  # Return modified message or None to keep original


async def main():
    agent = ReActAgent(
        name="Friday",
        sys_prompt="You are a helpful assistant.",
        # ... model and formatter config
    )

    # Register class-level hooks (affects all instances)
    ReActAgent.register_class_hook(
        hook_type="pre_reply",
        hook_name="logging_pre",
        hook=log_pre_reply,
    )
    ReActAgent.register_class_hook(
        hook_type="post_reply",
        hook_name="logging_post",
        hook=log_post_reply,
    )

    # Register instance-level hooks (affects only this instance)
    agent.register_instance_hook(
        hook_type="pre_print",
        hook_name="custom_print_hook",
        hook=lambda self, kwargs: print(f"Printing message from {self.name}"),
    )

    # Remove hooks
    ReActAgent.remove_class_hook("pre_reply", "logging_pre")
    agent.remove_instance_hook("pre_print", "custom_print_hook")

    # Clear all hooks
    ReActAgent.clear_class_hooks()  # Clear all class hooks
    agent.clear_instance_hooks("post_reply")  # Clear specific type

asyncio.run(main())
```

## Messages and Content Blocks - Message Structure

AgentScope uses a unified message format with support for multimodal content.

```python
from agentscope.message import (
    Msg,
    TextBlock,
    ImageBlock,
    AudioBlock,
    ToolUseBlock,
    ToolResultBlock,
    ThinkingBlock,
    Base64Source,
    URLSource,
)


# Simple text message
text_msg = Msg(
    name="user",
    content="Hello, how are you?",
    role="user",  # user, assistant, system
)

# Message with multiple content blocks
multimodal_msg = Msg(
    name="user",
    content=[
        TextBlock(type="text", text="What's in this image?"),
        ImageBlock(
            type="image",
            source=URLSource(type="url", url="https://example.com/image.jpg"),
        ),
    ],
    role="user",
)

# Access message content
print(text_msg.get_text_content())  # Get text content only
print(text_msg.get_content_blocks("text"))  # Get specific block types
print(text_msg.has_content_blocks("image"))  # Check for content types

# Tool use and result blocks (used internally by agents)
tool_call = ToolUseBlock(
    type="tool_use",
    id="call_123",
    name="calculate",
    input={"a": 5, "b": 10},
)

tool_result = ToolResultBlock(
    type="tool_result",
    id="call_123",
    name="calculate",
    output="15",
)

# Message with metadata for structured output
response_msg = Msg(
    name="assistant",
    content="The calculation result is 15.",
    role="assistant",
    metadata={"result": 15, "operation": "addition"},  # Structured data
)
print(response_msg.metadata)  # Access structured output
```

AgentScope provides a comprehensive framework for building production-ready agentic applications. Its modular architecture allows developers to combine agents, tools, memory systems, and model providers flexibly while maintaining clean abstractions. The framework excels at multi-agent orchestration through MsgHub and pipelines, making it straightforward to implement complex conversational workflows.

Key integration patterns include: using ReActAgent with custom tools for task automation, combining RAG knowledge bases with agents for domain-specific applications, implementing long-term memory for personalized interactions, and leveraging MCP for standardized tool integration. The framework's support for structured output ensures type-safe responses, while tracing and hooks enable observability and customization throughout the agent lifecycle.