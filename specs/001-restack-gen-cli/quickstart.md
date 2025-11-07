# Quickstart Guide: Restack Gen CLI

**Phase**: 1 - Design & Contracts  
**Date**: November 6, 2025  
**Context**: Quick start guide for developers using the Restack Gen CLI

## Installation

### Prerequisites

- Python 3.11 or higher
- Git (for project initialization)
- Internet connection (for dependencies and LLM features)

### Install via pip

```bash
pip install restack-gen
```

### Verify Installation

```bash
restack --version
# Output: Restack Gen CLI v1.0.0
```

## Quick Start

### 1. Create Your First Project

```bash
# Create a new Restack project
restack new my-ai-service

# Navigate to the project
cd my-ai-service

# Install dependencies
pip install -r requirements.txt
```

**What you get:**
```
my-ai-service/
├── restack.toml          # Project configuration
├── agents/               # AI agents directory
├── workflows/            # Temporal workflows
├── functions/            # Reusable functions
├── tests/               # Test suite
└── requirements.txt     # Python dependencies
```

### 2. Generate Your First Agent

```bash
# Generate an AI agent
restack g agent ChatBot --workflows ChatWorkflow

# This creates:
# - agents/chat_bot.py
# - tests/agents/test_chat_bot.py
```

### 3. Generate Supporting Components

```bash
# Create a workflow for the agent
restack g workflow ChatWorkflow --functions ProcessMessage,GenerateResponse

# Create the functions
restack g function ProcessMessage
restack g function GenerateResponse
```

### 4. Add LLM Integration

```bash
# Generate LLM integration with Gemini
restack g llm SmartResponder --provider gemini --with-prompts

# Set up your API key
export GEMINI_API_KEY="your-api-key-here"
```

### 5. Run Health Check

```bash
# Verify everything is set up correctly
restack doctor

# Should show all green checkmarks ✅
```

### 6. Start Development Server

```bash
# Start the development server
restack run:server --reload

# Visit: http://localhost:8000/health
```

## Common Usage Patterns

### Project Structure Best Practices

**Recommended organization:**
```
my-project/
├── agents/
│   ├── user_agent.py        # User interaction agent
│   ├── data_agent.py        # Data processing agent
│   └── notification_agent.py # Notification agent
├── workflows/
│   ├── user_onboarding.py   # Multi-step user flows
│   ├── data_pipeline.py     # Data processing pipelines
│   └── notification_flow.py # Notification workflows
├── functions/
│   ├── validators.py        # Input validation functions
│   ├── transformers.py      # Data transformation functions
│   └── integrations.py      # External API integrations
└── tests/
    ├── agents/
    ├── workflows/
    └── functions/
```

### Component Naming Conventions

- **Agents**: PascalCase nouns (`UserAgent`, `DataProcessor`, `ChatBot`)
- **Workflows**: PascalCase with "Workflow" suffix (`UserOnboardingWorkflow`)
- **Functions**: PascalCase verbs (`ValidateInput`, `TransformData`, `SendEmail`)
- **Pipelines**: PascalCase with "Pipeline" suffix (`DataProcessingPipeline`)

### Generator Commands Reference

#### Basic Component Generation
```bash
# Simple agent
restack g agent UserAgent

# Workflow with specific functions
restack g workflow DataPipeline --functions ValidateData,ProcessData,SaveData

# Pure function (no side effects)
restack g function CalculateScore --pure

# Pipeline with operator support
restack g pipeline MLTraining --operators sequence,loop --with-operators
```

#### Advanced Options
```bash
# Generate with custom timeout
restack g agent SlowAgent --timeout 60000

# Use specific template
restack g workflow CustomWorkflow --template advanced

# Force overwrite existing files
restack g function ExistingFunction --force

# Dry run to see what would be generated
restack g agent TestAgent --dry-run
```

### LLM Integration Examples

#### Gemini Integration
```bash
# Basic Gemini integration
restack g llm DocumentAnalyzer --provider gemini --model gemini-1.5-pro

# With custom prompts
restack g llm ContentGenerator --provider gemini --with-prompts --max-tokens 2048
```

#### Multi-Provider Setup
```bash
# Generate with provider flexibility
restack g llm FlexibleAI --provider gemini

# Later switch providers by updating restack.toml:
[defaults.llm]
default_provider = "openai"  # Switch to OpenAI
```

## Configuration

### Project Configuration (`restack.toml`)

```toml
[project]
name = "my-ai-service"
version = "1.0.0"
description = "My AI-powered service"
python_version = "3.11"

[defaults.retry]
max_attempts = 3
initial_interval_ms = 1000
max_interval_ms = 8000

[defaults.timeouts]
agent_timeout_ms = 30000
workflow_timeout_ms = 60000
function_timeout_ms = 10000

[defaults.llm]
default_provider = "gemini"
default_model = "gemini-1.5-pro"
```

### Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Restack settings
RESTACK_LOG_LEVEL=INFO
RESTACK_ENV=development
```

## Development Workflow

### 1. Test-Driven Development

```bash
# Generate component with tests
restack g agent UserProcessor --with-tests

# Run tests
pytest tests/agents/test_user_processor.py -v

# Run all tests
pytest -v
```

### 2. Iterative Development

```bash
# Check project health regularly
restack doctor

# Auto-fix common issues
restack doctor --fix

# Verbose diagnostics
restack doctor --verbose
```

### 3. Component Evolution

```bash
# Regenerate component with new options
restack g workflow UpdatedWorkflow --functions NewFunction --force

# Update all components to latest templates
restack doctor --check templates --fix
```

## Common Patterns

### Error Handling Pattern

Generated components include robust error handling:

```python
# Auto-generated in agent files
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(TemporaryError)
)
async def handle_request(self, input_data):
    try:
        result = await self.process(input_data)
        return result
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise
```

### LLM Integration Pattern

```python
# Auto-generated LLM integration
class SmartResponder(LLMIntegration):
    def __init__(self):
        super().__init__(
            provider="gemini",
            model="gemini-1.5-pro",
            max_tokens=1024
        )
    
    async def generate_response(self, prompt: str) -> str:
        response = await self.client.generate(
            prompt=prompt,
            temperature=0.7
        )
        return response.text
```

### Pipeline Composition Pattern

```python
# Auto-generated pipeline with operators
class DataPipeline(Pipeline):
    def __init__(self):
        super().__init__()
        self.add_sequence([
            ValidateData,
            TransformData,
            SaveData
        ])
        self.add_conditional(
            condition=lambda x: x.needs_processing,
            true_branch=ProcessData,
            false_branch=SkipProcessing
        )
```

## Troubleshooting

### Common Issues

#### "Not a Restack project" Error
```bash
# Ensure you're in the project directory
cd my-project
restack doctor
```

#### Missing Dependencies
```bash
# Update requirements
pip install -r requirements.txt --upgrade

# Check for compatibility issues
restack doctor --check dependencies
```

#### Template Issues
```bash
# Reset to latest templates
restack doctor --check templates --fix

# Use specific template version
restack g agent MyAgent --template v1.0
```

#### LLM Integration Issues
```bash
# Check API key configuration
echo $GEMINI_API_KEY

# Test connection
restack doctor --check llm
```

### Getting Help

```bash
# Command help
restack --help
restack new --help
restack g --help

# Project diagnostics
restack doctor --verbose

# Check configuration
restack doctor --check config
```

### Debug Mode

```bash
# Enable verbose logging
export RESTACK_LOG_LEVEL=DEBUG
restack g agent MyAgent --verbose

# Dry run to see generated content
restack g workflow TestWorkflow --dry-run
```

## Next Steps

### Advanced Features

1. **Custom Templates**: Create your own component templates
2. **Pipeline Orchestration**: Build complex data processing pipelines
3. **Multi-Agent Systems**: Coordinate multiple AI agents
4. **Production Deployment**: Deploy to Kubernetes with Temporal

### Learning Resources

- [Restack Framework Documentation](https://docs.restack.io)
- [Temporal Workflow Patterns](https://docs.temporal.io)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
- [Pydantic Models](https://pydantic-docs.helpmanual.io)

### Community

- GitHub Issues: Report bugs and request features
- Discord: Join the community for support
- Documentation: Contribute to docs and examples

## Quick Reference

### Essential Commands
```bash
restack new <project-name>              # Create project
restack g agent <name>                  # Generate agent
restack g workflow <name>               # Generate workflow
restack g function <name>               # Generate function
restack g llm <name>                   # Generate LLM integration
restack doctor                         # Health check
restack run:server                     # Start server
```

### Global Options
```bash
--help, -h                            # Show help
--version                             # Show version
--verbose, -v                         # Verbose output
--quiet, -q                          # Quiet mode
--force                              # Force overwrite
--dry-run                           # Preview without changes
```

### File Locations
```bash
restack.toml                         # Project config
agents/                             # AI agents
workflows/                          # Temporal workflows
functions/                          # Reusable functions
tests/                             # Test suite
.restack/                          # CLI metadata
```