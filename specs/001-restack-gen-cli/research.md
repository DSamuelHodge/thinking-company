# Research: Restack Gen CLI

**Phase**: 0 - Outline & Research  
**Date**: November 6, 2025  
**Context**: Technical decisions and best practices for convention-over-configuration CLI development

## Research Tasks Completed

### CLI Framework Selection

**Decision**: Click framework for Python CLI development

**Rationale**: 
- Industry standard for Python CLIs with excellent documentation
- Built-in support for command groups, options, and arguments
- Strong testing capabilities and error handling
- Integrates well with setuptools for distribution
- Used by major tools like Flask and others in Python ecosystem

**Alternatives Considered**:
- argparse: Too low-level, requires more boilerplate
- Typer: Good but newer, less battle-tested than Click
- Fire: Too magic, less control over interface design

### Template Engine Selection

**Decision**: Jinja2 for code generation templates

**Rationale**:
- De facto standard for Python templating
- Powerful control structures and filters
- Widely understood by Python developers
- Excellent performance and safety features
- Strong ecosystem support

**Alternatives Considered**:
- string.Template: Too limited for complex code generation
- Mako: More complex than needed, security concerns
- Custom templating: Reinventing the wheel

### Code Generation Patterns

**Decision**: Generator classes with template-based approach

**Rationale**:
- Rails-style generators provide familiar developer experience
- Template-based approach ensures consistent output
- Object-oriented design allows for easy extension and customization
- Separates generation logic from template content

**Alternatives Considered**:
- AST-based generation: Too complex for scaffolding use case
- Simple file copying: Insufficient for dynamic content
- Inline string generation: Unmaintainable for larger templates

### Configuration Management

**Decision**: TOML-based configuration with Pydantic validation

**Rationale**:
- TOML is human-readable and widely adopted in Python ecosystem
- Pydantic provides excellent validation and type safety
- Easy integration with Python typing system
- Good tooling support

**Alternatives Considered**:
- YAML: More complex parsing, indentation issues
- JSON: Less human-readable, no comments
- INI: Too limited for complex configuration

### LLM Integration Architecture

**Decision**: Abstract provider interface with Gemini as default implementation

**Rationale**:
- Allows for future provider additions without breaking changes
- Gemini provides excellent performance and capabilities
- Abstract interface enables testing with mock providers
- Plugin-style architecture for extensibility

**Alternatives Considered**:
- Single provider hardcoded: Inflexible
- All providers supported from start: Too much initial complexity
- No default provider: Poor developer experience

### FastMCP Integration Architecture

**Decision**: Model Context Protocol (MCP) for exposing tools, resources, and prompts to LLMs

**Rationale**:
- FastMCP provides standardized protocol for LLM interactions
- Separates stateless operations (tools, data) from stateful agent logic
- Enables modular architecture with independent scaling
- Pythonic interface with automatic schema generation from type hints
- Supports both synchronous and asynchronous operations
- Built-in support for tool transformation and customization

**Key Capabilities**:
1. **Tools**: Functions that execute code or interact with external systems
   - Auto-generates input schemas from type hints
   - Supports both sync and async functions
   - Enables tool transformation for domain-specific adaptations
   
2. **Resources**: Read-only data sources accessible via URIs
   - Lazy evaluation (only runs when requested)
   - Supports dynamic URIs with placeholders
   - Automatic serialization of JSON responses
   
3. **Prompts**: Parameterized message templates for LLM interactions
   - Ensures consistent instruction formatting
   - Supports multiple return types (strings, PromptMessage, lists)
   - Injectable Context for request metadata

**Integration Pattern with Restack**:
- Restack agents manage stateful workflows and orchestration
- FastMCP servers expose stateless functions and data
- Agents call MCP tools via `agent.step()` for retry-safe execution
- Resources loaded at runtime and stored in agent state
- Prompts retrieved for standardized LLM interactions

**Alternatives Considered**:
- Direct function calls: No standardization, harder to test and scale
- Custom protocol: Reinventing the wheel, maintenance burden
- REST APIs only: Less specialized for LLM interactions

### Migration System Design

**Decision**: Timestamp-based migration files with up/down methods

**Rationale**:
- Familiar pattern from database migrations
- Clear linear progression and rollback capabilities
- Timestamp-based naming prevents conflicts
- up/down methods provide explicit forward/backward compatibility

**Alternatives Considered**:
- Version numbers: Conflict potential in team environments
- Git-based tracking: Too complex for configuration changes
- Declarative approach: Harder to handle complex transformations

### Restack Agent Design Patterns

**Decision**: Component-based agent architecture following Restack conventions

**Core Components**:
1. `@agent.defn()`: Declares agent class
2. `__init__()`: Initializes persistent state
3. `@agent.event`: Async entry points triggered by signals
4. `agent.step()`: Calls pure functions with retry safety
5. `@agent.run`: Main lifecycle loop

**Key Rules**:
- **Statefulness**: Maintain progress in instance variables
- **Typed Events**: Use Pydantic or dataclass models
- **Idempotent Functions**: Functions in `agent.step()` must be pure and retry-safe
- **Communication**: Use `agent.signal()` to trigger events on other agents
- **Lifecycle Control**: `@agent.run` waits on conditions and controls termination
- **Error Handling**: Log events and wrap deterministic failures in NonRetryableError
- **Modularity**: Single responsibility per agent

**Integration with FastMCP**:
- Use MCP tools as steps within agents
- Load external context via MCP resources
- Leverage MCP prompts for structured LLM queries
- Keep agent state in Restack, stateless operations in FastMCP
- Wrap MCP client calls in `agent.step()` for retry logic

**Alternatives Considered**:
- Flat function-based approach: Loses state management benefits
- Framework-agnostic design: Doesn't leverage Restack capabilities
- Monolithic agents: Poor separation of concerns

### Project Structure Conventions

**Decision**: Component-type directory structure with standard Python packaging

**Rationale**:
- Clear separation of concerns between component types
- Familiar to developers working with microservices
- Easy to navigate and understand project layout
- Scales well as projects grow in complexity

**Alternatives Considered**:
- Domain-driven structure: Too complex for scaffolding tool
- Flat structure: Doesn't scale with project growth
- Feature-based: Less clear for component-oriented architecture

### Testing Strategy

**Decision**: Comprehensive test pyramid with temporary project generation

**Rationale**:
- Unit tests for individual generator components
- Integration tests using real file system operations
- End-to-end tests validating complete CLI workflows
- Temporary directories ensure test isolation

**Alternatives Considered**:
- Mock-based testing only: Insufficient for file generation validation
- Manual testing only: Not sustainable for CI/CD
- Snapshot testing only: Brittle and hard to maintain

## Technology Stack Summary

| Category | Choice | Version | Rationale |
|----------|--------|---------|-----------|
| Language | Python | 3.11+ | Pydantic requirement, Temporal ecosystem |
| CLI Framework | Click | 8.x | Industry standard, excellent testing |
| Templating | Jinja2 | 3.x | De facto standard, powerful features |
| Validation | Pydantic | 2.x | Type safety, data validation |
| Testing | pytest | 7.x | Comprehensive testing ecosystem |
| Configuration | TOML | - | Human-readable, Python ecosystem standard |
| LLM Primary | Gemini | Latest | Performance, capabilities, API stability |
| Tool Server | FastMCP | 2.x | MCP-compliant tool server framework |
| Restack SDK | restack-ai | Latest | Core framework integration |

## Durable Pipeline Infrastructure

### FastMCP Server Manager

**Decision**: Centralized service lifecycle management for multiple MCP servers

**Rationale**:
- Automates configuration loading from YAML
- Manages server lifecycles (start, stop, health checks)
- Supports environment variable expansion for secrets
- Provides server registry for runtime access
- Enables graceful shutdown procedures

**Key Features**:
- Per-server autostart configuration
- Periodic health monitoring
- Manual start/stop controls
- Transport configuration (HTTP, stdio)
- Integration with Restack workflows

### FastMCP Client for Agents

**Decision**: Wrapped client with caching, observability, and error handling

**Rationale**:
- Proper context management (async with)
- Tool registry lookup with informative errors
- Optional response caching with TTL
- Observability hooks for monitoring/tracing
- Reduces repetitive connection management code

**Integration Pattern**:
```python
async with FastMCPClient("server_name", cache_enabled=True) as client:
    result = await client.call_tool("tool_name", args)
```

### Multi-Provider LLM Router

**Decision**: Unified interface with automatic fallback and circuit-breaker behavior

**Rationale**:
- Protects against provider outages and rate limits
- Configuration-driven provider management
- Cost estimation without API calls (dry-run mode)
- Circuit breaker prevents thrashing
- Backend agnostic (supports proxies like Kong)

**Key Features**:
- Priority-based provider selection
- Automatic failover on timeout/5xx/rate limits
- Per-provider circuit breakers with cooldown
- Typed models (Pydantic) for requests/responses
- Cost estimation before execution

### Declarative Pipeline Operators

**Decision**: Expression language for describing agent/workflow composition

**Rationale**:
- Concise pipeline definitions
- Self-documenting workflows
- Reduces imperative boilerplate
- Easier to modify than nested Python code

**Operators**:
- `→` (Sequence): Execute components in order
- `⇄` (Parallel): Run components concurrently
- `→?` (Optional): Execute only if previous succeeds
- `()` (Grouping): Control precedence

**Example**: `Agent1 → (WorkflowReview ⇄ Agent2) → FunctionSummarize`

## Best Practices Identified

### Code Generation
- Use consistent naming conventions across all generators
- Include comprehensive docstrings in generated code
- Generate tests alongside code components
- Validate syntax before writing files
- Provide clear error messages for generation failures

### CLI Design
- Follow POSIX conventions for command-line interfaces
- Provide both verbose and quiet modes
- Include progress indicators for long operations
- Support both interactive and non-interactive modes
- Implement consistent help text and examples

### Error Handling
- Use structured logging for debugging
- Provide actionable error messages
- Include suggestions for common mistakes
- Implement graceful degradation where possible
- Support verbose error modes for troubleshooting

### Template Organization
- Organize templates by component type
- Use consistent variable naming across templates
- Include template comments for maintainability
- Separate templates for different use cases
- Version templates alongside code

### Restack + FastMCP Integration
- Keep stateful logic in Restack agents
- Keep stateless operations in FastMCP tools
- Call MCP tools via `agent.step()` for retry safety
- Load resources at runtime and store in agent state
- Use prompts for standardized LLM interactions
- Handle async operations properly in both frameworks
- Propagate errors and convert to NonRetryableError when needed
- Log tool calls and responses for traceability

### FastMCP Best Practices
- Use type hints for automatic schema generation
- Avoid `*args` and `**kwargs` in tool definitions
- Make tools idempotent and stateless
- Use async functions for I/O-bound operations
- Provide clear docstrings (auto-used as descriptions)
- Use unique URIs for resources
- Leverage tool transformation for domain adaptation
- Set appropriate timeouts for tool calls
- Use context manager pattern for client connections

## Architecture Integration Summary

### Layer Separation
1. **Restack Layer** (Stateful)
   - Agent state management
   - Workflow orchestration
   - Event handling and signaling
   - Lifecycle control
   - Progress tracking

2. **FastMCP Layer** (Stateless)
   - Tool execution
   - Resource access
   - Prompt templates
   - External API integration
   - Data retrieval

3. **Infrastructure Layer**
   - Server lifecycle management
   - LLM routing and fallback
   - Caching and observability
   - Circuit breakers
   - Health monitoring

### Communication Flow
```
User Request → Restack Agent → FastMCP Client → MCP Server → Tool/Resource
            ←                ←                ←            ← Result
```

### Key Integration Points
- Agents use `agent.step()` to call MCP tools
- Resources fetched at runtime via client
- Prompts retrieved for LLM standardization
- Server manager handles MCP server lifecycle
- LLM router provides resilient model access
- Client provides caching and observability

## Risk Mitigation

### Template Compatibility
- Implement template version checking
- Provide migration paths for template updates
- Test templates against multiple Python versions
- Document template customization guidelines

### Performance
- Lazy-load templates to reduce startup time
- Implement caching for repeated operations (FastMCP client cache)
- Optimize file I/O operations
- Profile generation performance regularly
- Use async operations for I/O-bound tasks
- Circuit breakers prevent cascading failures

### Maintainability
- Use consistent code style across all modules
- Implement comprehensive logging (structured for observability)
- Document all public APIs
- Provide examples for extension points
- Regular dependency updates and security audits
- Clear separation between stateful and stateless components

### Reliability
- Implement retry logic via `agent.step()`
- Use circuit breakers for external dependencies
- Automatic failover between LLM providers
- Health checks for MCP servers
- Graceful degradation when services unavailable
- Proper error propagation and NonRetryableError handling

## Development Checklists

### Restack Agent Development Checklist
- [ ] Define agent class with `@agent.defn()`
- [ ] Use `@agent.event` for each input with typed models (Pydantic/dataclass)
- [ ] Call pure functions via `agent.step()`
- [ ] Manage lifecycle and termination in `@agent.run`
- [ ] Communicate with other agents via `agent.signal()`
- [ ] Use workflows to compose agents
- [ ] Log events and wrap deterministic errors with NonRetryableError
- [ ] Maintain state in instance variables only (no global state)

### FastMCP Server Development Checklist
- [ ] Create FastMCP instance with meaningful name and instructions
- [ ] Define tools using `@mcp.tool`, avoid `*args`/`**kwargs`, use type hints
- [ ] Define resources via `@mcp.resource` with unique URIs
- [ ] Define prompts via `@mcp.prompt` with clear parameter annotations
- [ ] Customize names, descriptions, tags, and metadata where helpful
- [ ] Handle duplicates by setting `on_duplicate_tools/resources/prompts`
- [ ] Use `mcp.run()` or `fastmcp run` to start server
- [ ] Use `fastmcp.Client` within `async with` block
- [ ] Call `list_tools()`, `call_tool()`, `read_resource()`, `get_prompt()` appropriately
- [ ] Consider tool transformation with `Tool.from_tool()` for domain adaptation
- [ ] Use async functions for prompts/resources needing dynamic data
- [ ] Inject Context object when needing request metadata

### Integration Development Checklist
- [ ] Separate stateful logic (Restack) from stateless operations (FastMCP)
- [ ] Wrap MCP client calls in `agent.step()` for retry safety
- [ ] Set appropriate timeouts for tool calls
- [ ] Propagate errors and convert to NonRetryableError when needed
- [ ] Log tool calls and responses with structured logging
- [ ] Use server manager for MCP server lifecycle
- [ ] Configure LLM router for resilient model access
- [ ] Enable caching in FastMCP client where appropriate
- [ ] Implement observability hooks for monitoring
- [ ] Test with both successful and failure scenarios