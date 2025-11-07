# Contract: FastMCP Integration

**Feature**: 001-restack-gen-cli  
**Date**: November 6, 2025  
**Status**: Draft  
**Related**: FR-006 (FastMCP tool server integration), research.md (FastMCP Integration Architecture)

## Purpose

Defines how generated Restack projects integrate with FastMCP tool servers for exposing tools, resources, and prompts to LLM-powered agents.

## Scope Clarification

**Important**: The FastMCP infrastructure components (Server Manager, Client Wrapper, LLM Router, Pipeline Operators) described in research.md are **runtime utilities and patterns**, NOT code generation targets.

### What the CLI Generates

The CLI generates:
1. **FastMCP tool server scaffolding** - Basic MCP server setup
2. **Tool definitions** - Example tools with proper decorators
3. **Integration code** - How agents call MCP tools via `agent.step()`
4. **Configuration** - Server settings in `restack.toml`

### What are External Dependencies

The following are ecosystem patterns/libraries (NOT generated):
- FastMCP Server Manager - Runtime service lifecycle management
- FastMCP Client Wrapper - Runtime client with caching/observability
- Multi-Provider LLM Router - Runtime LLM routing with fallback
- Declarative Pipeline Operators - Expression parser for workflows

## Generated FastMCP Server Structure

When user runs: `restack g llm TestLLM --with-fastmcp`

Generated file: `tools/test_llm_tools.py`

```python
"""
Generated FastMCP tool server for TestLLM
"""
from fastmcp import FastMCP
from typing import Dict, List, Optional

# Create MCP server instance
mcp = FastMCP(
    name="TestLLMTools",
    instructions="""
    This server provides tools for TestLLM agent.
    Call available tools to execute operations.
    """
)

@mcp.tool
def example_tool(query: str, max_results: int = 10) -> List[Dict]:
    """
    Example tool implementation.
    
    Args:
        query: Search query string
        max_results: Maximum number of results
        
    Returns:
        List of result dictionaries
    """
    # TODO: Implement tool logic
    return [{"result": "example"}]

@mcp.resource("config://settings")
def get_settings() -> Dict:
    """Expose configuration as a resource"""
    return {
        "version": "1.0.0",
        "enabled": True
    }

@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Generate a prompt for asking about a topic"""
    return f"Can you explain {topic} in detail?"

if __name__ == "__main__":
    mcp.run()  # Start server
```

## Generated Agent Integration

Generated file: `agents/test_llm_agent.py`

```python
"""
Generated Restack agent with FastMCP integration
"""
from restack_ai import agent
from fastmcp import Client
from pydantic import BaseModel

class TestLLMInput(BaseModel):
    query: str

class TestLLMOutput(BaseModel):
    result: str

@agent.defn()
class TestLLMAgent:
    def __init__(self):
        self.results = []
    
    @agent.event
    async def process_query(self, event: TestLLMInput):
        """Process query using FastMCP tools"""
        # Call MCP tool via agent.step() for retry safety
        result = await agent.step(
            self._call_mcp_tool,
            tool_name="example_tool",
            args={"query": event.query}
        )
        self.results.append(result)
    
    async def _call_mcp_tool(self, tool_name: str, args: dict) -> dict:
        """
        Call FastMCP tool - wrapped for retry safety.
        This function is pure and idempotent.
        """
        async with Client("tools/test_llm_tools.py:mcp") as client:
            response = await client.call_tool(tool_name, args)
            return response
    
    @agent.run
    async def run(self):
        """Agent lifecycle control"""
        # Wait for events...
        pass
```

## Configuration Schema

Generated in `restack.toml`:

```toml
[fastmcp]
enabled = true
auto_discover = true  # Automatically discover tools/ directory

[[fastmcp.servers]]
name = "test_llm_tools"
path = "tools/test_llm_tools.py"
transport = "stdio"  # or "http"
autostart = true

[fastmcp.servers.env]
# Environment variables for this server
API_KEY = "${TOOLS_API_KEY}"
```

## FastMCP Tool Registration Requirements

All generated tools MUST:

1. **Use type hints** - For automatic schema generation
   ```python
   def my_tool(arg1: str, arg2: int = 5) -> dict:
   ```

2. **Avoid `*args` / `**kwargs`** - Complete parameter schemas required
   ```python
   # ❌ INVALID
   def bad_tool(*args, **kwargs):
       pass
   
   # ✅ VALID
   def good_tool(name: str, count: int) -> List[str]:
       pass
   ```

3. **Provide docstrings** - Used as tool descriptions
   ```python
   @mcp.tool
   def search(query: str) -> List[Dict]:
       """Search the knowledge base for relevant documents"""
       pass
   ```

4. **Be stateless and idempotent** - Tools should not maintain state
   ```python
   # ❌ AVOID
   results_cache = []  # Global state
   
   def search(query: str):
       results_cache.append(query)  # Stateful
   
   # ✅ PREFER
   def search(query: str) -> List[Dict]:
       results = fetch_from_db(query)  # Stateless
       return results
   ```

## Resource URI Conventions

Generated resources MUST follow URI patterns:

```python
@mcp.resource("config://app/settings")  # Configuration data
@mcp.resource("data://{dataset_id}")    # Dynamic data with params
@mcp.resource("file:///path/to/data")   # File-based resources
```

## Prompt Template Patterns

Generated prompts MUST:

```python
@mcp.prompt
def generate_analysis(topic: str, depth: str = "basic") -> str:
    """
    Generate an analysis prompt with configurable depth.
    
    Args:
        topic: Subject to analyze
        depth: Analysis depth (basic, intermediate, advanced)
    """
    return f"Provide a {depth} analysis of {topic}"
```

## Error Handling

Generated code MUST handle MCP errors:

```python
from restack_ai.errors import NonRetryableError

async def _call_mcp_tool(self, tool_name: str, args: dict):
    try:
        async with Client("server:mcp") as client:
            return await client.call_tool(tool_name, args)
    except ConnectionError as e:
        # Retryable - let agent.step() retry
        raise e
    except ValueError as e:
        # Non-retryable - bad input
        raise NonRetryableError(f"Invalid tool args: {e}")
```

## Testing Requirements

Generated test file: `tests/test_test_llm_tools.py`

```python
import pytest
from fastmcp import Client
from tools.test_llm_tools import mcp

@pytest.mark.asyncio
async def test_example_tool():
    """Test MCP tool execution"""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "example_tool",
            {"query": "test", "max_results": 5}
        )
        assert isinstance(result, list)
        assert len(result) <= 5
```

## Acceptance Criteria

- [ ] FastMCP server scaffolding generated with `@mcp.tool` decorators
- [ ] Agent integration code generated with `agent.step()` wrapper
- [ ] Configuration added to `restack.toml` for server settings
- [ ] Tools follow type hint requirements (no *args/**kwargs)
- [ ] Resources use valid URI patterns
- [ ] Prompts have clear parameter annotations
- [ ] Error handling wraps MCP calls properly
- [ ] Tests verify tool execution via Client
- [ ] Generated code passes syntax validation

## Non-Requirements (Future Enhancements)

- **Server Manager infrastructure** - Users implement per research.md patterns
- **Client wrapper with caching** - Users implement per research.md patterns  
- **LLM Router integration** - Separate from FastMCP tool servers
- **Tool transformation** - Users apply `Tool.from_tool()` manually
- **Health check endpoints** - Not generated by default

## Integration with Restack Patterns

Generated code follows Restack conventions:

1. **Stateful logic in agents** - Agent classes manage state
2. **Stateless logic in tools** - MCP tools are pure functions
3. **Retry via agent.step()** - MCP calls wrapped for retry safety
4. **Structured logging** - All tool calls logged with context
5. **Error propagation** - MCP errors converted to NonRetryableError when appropriate

## Notes

- FastMCP servers run as separate processes (stdio or HTTP transport)
- Agent code calls servers via fastmcp.Client
- Server lifecycle managed by user or external orchestrator
- Research.md infrastructure patterns are implementation examples, not generated code
