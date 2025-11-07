# Restack Gen CLI

A convention-over-configuration CLI tool for scaffolding [Restack.io](https://restack.io) projects with agents, workflows, functions, pipelines, and LLM integrations.

## Features

- 🚀 **Quick Project Scaffolding**: Generate complete Restack projects with sensible defaults in under 2 minutes
- 🎯 **Rails-Style Generators**: Create agents, workflows, and functions with `restack g` commands
- 🔄 **Smart Defaults**: Pre-configured exponential backoff retry strategies, timeouts, and structured logging
- 🤖 **LLM Integration**: Built-in support for Gemini (with extensible provider architecture)
- 🛠️ **FastMCP Tool Servers**: Generate MCP-compliant tool servers for LLM integration
- 🔍 **Health Checks**: Validate project structure and configuration with `restack doctor`
- 📦 **Component-Type Structure**: Organized project layout (agents/, workflows/, functions/)

## Installation

### From PyPI (when published)

```bash
pip install restack-gen
```

### From Source

```bash
git clone https://github.com/thinking-company/restack-gen.git
cd restack-gen
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/thinking-company/restack-gen.git
cd restack-gen
pip install -e ".[dev]"
```

## Quick Start

### Create a New Project

```bash
restack new my-agent-project
cd my-agent-project
```

This generates:
- Project structure (agents/, workflows/, functions/, tests/)
- Configuration file (restack.toml)
- Python packaging files (pyproject.toml, requirements.txt)
- Git repository (optional)

### Generate Components

```bash
# Generate an agent
restack g agent DataProcessor --description "Processes incoming data"

# Generate a workflow
restack g workflow DataPipeline --with-tests

# Generate a function
restack g function ValidateData --timeout 30
```

### Validate Your Project

```bash
# Run health checks
restack doctor

# Check specific aspects
restack doctor --check dependencies
restack doctor --check syntax --verbose
```

### Generate LLM Integration

```bash
# Create Gemini integration with prompts
restack g llm ResearchAssistant --provider gemini --with-prompts

# Create FastMCP tool server
restack g llm ToolServer --with-mcp
```

## Commands

### `restack new <project-name>`

Create a new Restack project with complete scaffolding.

**Options:**
- `--python-version <version>` - Python version (default: 3.11)
- `--template <name>` - Project template (default: standard)
- `--description <text>` - Project description
- `--no-git` - Skip Git initialization
- `--quiet` - Minimal output
- `--verbose` - Detailed output

### `restack g <type> <name>`

Generate a component (agent, workflow, function, pipeline, llm).

**Component Types:**
- `agent` - Restack agent with Pydantic models
- `workflow` - Temporal workflow
- `function` - Activity function
- `pipeline` - Complex pipeline with operator grammar
- `llm` - LLM integration

**Options:**
- `--description <text>` - Component description
- `--timeout <seconds>` - Timeout configuration
- `--with-tests` - Generate test files
- `--dry-run` - Preview without creating files
- `--force` - Overwrite existing files

### `restack doctor`

Validate project structure and configuration.

**Options:**
- `--check <type>` - Specific check (config, dependencies, syntax, structure)
- `--fix` - Auto-fix issues
- `--verbose` - Detailed diagnostic output

### `restack run:server`

Start development server with auto-reload.

**Options:**
- `--port <port>` - Server port (default: 8000)
- `--host <host>` - Server host (default: localhost)
- `--workers <count>` - Worker processes
- `--reload` - Enable auto-reload
- `--env <environment>` - Environment (dev, prod)

## Project Structure

Generated projects follow a component-type structure:

```text
my-project/
├── agents/              # Agent implementations
│   ├── __init__.py
│   └── data_processor_agent.py
├── workflows/           # Workflow definitions
│   ├── __init__.py
│   └── data_pipeline_workflow.py
├── functions/           # Activity functions
│   ├── __init__.py
│   └── validate_data_function.py
├── tests/               # Test files
│   ├── test_agents.py
│   ├── test_workflows.py
│   └── test_functions.py
├── restack.toml         # Configuration
├── pyproject.toml       # Python project metadata
└── requirements.txt     # Dependencies
```

## Configuration

Projects are configured via `restack.toml`:

```toml
[project]
name = "my-project"
version = "0.1.0"
python_version = "3.11"

[retry]
max_attempts = 3
initial_interval = 1.0
backoff_coefficient = 2.0
max_interval = 10.0
jitter = true

[timeout]
schedule_to_close = 600
start_to_close = 300

[logging]
level = "INFO"
format = "json"
```

## Development

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/ -m unit

# Integration tests
pytest tests/integration/ -m integration

# With coverage
pytest --cov=restack_gen --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy restack_gen

# Formatting
black restack_gen tests
```

## Requirements

- Python 3.11 or higher
- pip or uv for package management

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Support

- Documentation: [GitHub README](https://github.com/thinking-company/restack-gen#readme)
- Issues: [GitHub Issues](https://github.com/thinking-company/restack-gen/issues)
- Restack.io: [Official Documentation](https://restack.io/docs)
