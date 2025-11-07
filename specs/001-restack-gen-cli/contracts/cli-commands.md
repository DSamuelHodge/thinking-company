# CLI Command Contracts

**Phase**: 1 - Design & Contracts  
**Date**: November 6, 2025  
**Context**: Command-line interface definitions and specifications

## Command Structure

All commands follow the pattern: `restack <command> [subcommand] [options] [arguments]`

## Core Commands

### `restack new <project-name>`

Create a new Restack project with complete scaffolding.

**Syntax**:
```bash
restack new <project-name> [options]
```

**Arguments**:
- `<project-name>`: Project name (kebab-case, alphanumeric with hyphens)

**Options**:
- `--python-version VERSION`: Python version requirement (default: "3.11")
- `--template TEMPLATE`: Base template to use (default: "standard")
- `--description TEXT`: Project description
- `--no-git`: Skip Git repository initialization
- `--quiet, -q`: Suppress output except errors
- `--verbose, -v`: Enable detailed output

**Success Response**:
```
✅ Created project 'my-project'
📁 Project structure initialized
🐍 Python 3.11 environment configured
📋 Configuration files generated
🧪 Test structure created

Next steps:
  cd my-project
  pip install -r requirements.txt
  restack run:server
```

**Error Responses**:
- `Invalid project name`: Name doesn't follow naming conventions
- `Directory exists`: Target directory already exists
- `Permission denied`: Insufficient filesystem permissions
- `Python version unsupported`: Specified Python version not supported

**Exit Codes**:
- `0`: Success
- `1`: Invalid arguments
- `2`: Filesystem error
- `3`: Configuration error

### `restack generate <type> <name>` (alias: `restack g`)

Generate a specific component within an existing project.

**Syntax**:
```bash
restack g <type> <name> [options]
```

**Arguments**:
- `<type>`: Component type (`agent`, `workflow`, `function`, `pipeline`, `llm`)
- `<name>`: Component name (PascalCase)

**Options**:
- `--with-tests`: Generate comprehensive test suite (default: true)
- `--template TEMPLATE`: Use specific template variant
- `--force`: Overwrite existing files
- `--dry-run`: Show what would be generated without creating files
- `--output-dir PATH`: Override default output directory

**Component-specific Options**:

#### Agent Generation
```bash
restack g agent UserAgent [options]
```
- `--workflows LIST`: Comma-separated workflow names to associate
- `--timeout MILLISECONDS`: Agent timeout (default: 30000)

#### Workflow Generation
```bash
restack g workflow ProcessData [options]
```
- `--functions LIST`: Comma-separated function names to use
- `--timeout MILLISECONDS`: Workflow timeout (default: 60000)
- `--pipeline`: Generate as complex pipeline with operator support

#### Function Generation
```bash
restack g function CalculateScore [options]
```
- `--pure`: Mark as pure function (no side effects)
- `--timeout MILLISECONDS`: Function timeout (default: 10000)

#### Pipeline Generation
```bash
restack g pipeline DataProcessor [options]
```
- `--operators LIST`: Comma-separated operators (sequence, loop, conditional)
- `--error-strategy STRATEGY`: Error handling strategy (halt, continue, retry)

#### LLM Integration Generation
```bash
restack g llm ChatAgent [options]
```
- `--provider PROVIDER`: LLM provider (gemini, openai, anthropic)
- `--model MODEL`: Specific model name
- `--with-prompts`: Include prompt versioning setup
- `--max-tokens NUMBER`: Maximum response tokens

**Success Response**:
```
✅ Generated Agent 'UserAgent'
📄 Created: agents/user_agent.py
🧪 Created: tests/agents/test_user_agent.py
📝 Updated: restack.toml

Files created:
  agents/user_agent.py (156 lines)
  tests/agents/test_user_agent.py (89 lines)
```

**Error Responses**:
- `Not a Restack project`: Command run outside project directory
- `Component exists`: Component with that name already exists
- `Invalid type`: Unsupported component type
- `Invalid name`: Name doesn't follow conventions
- `Template not found`: Specified template doesn't exist

### `restack doctor`

Validate project configuration and diagnose issues.

**Syntax**:
```bash
restack doctor [options]
```

**Options**:
- `--fix`: Automatically fix issues where possible
- `--check TYPE`: Check specific aspect (config, dependencies, syntax, structure)
- `--verbose, -v`: Show detailed diagnostic information

**Success Response**:
```
🔍 Restack Project Health Check

✅ Project Configuration
  • restack.toml is valid
  • Python version compatible (3.11)
  • Dependencies satisfied

✅ Project Structure
  • All directories present
  • File permissions correct
  • Git repository initialized

✅ Generated Components
  • 3 agents, 5 workflows, 8 functions
  • All components syntactically valid
  • Test coverage: 85%

✅ Restack Integration
  • SDK version compatible
  • Temporal configuration valid
  • Connection test successful

🎉 Project is healthy!
```

**Warning Response**:
```
⚠️  Issues Found

🔧 Fixable Issues:
  • Outdated dependencies (run: pip install -U -r requirements.txt)
  • Missing test files for WorkflowA (run: restack g workflow WorkflowA --tests-only)

⚠️  Manual Action Required:
  • agent/user_agent.py: Syntax error on line 23
  • restack.toml: Invalid timeout value (must be positive integer)

Run 'restack doctor --fix' to auto-fix available issues.
```

### `restack run:server`

Start development server for the Restack project.

**Syntax**:
```bash
restack run:server [options]
```

**Options**:
- `--port PORT`: Server port (default: 8000)
- `--host HOST`: Server host (default: localhost)
- `--workers NUMBER`: Worker processes (default: 1)
- `--reload`: Auto-reload on file changes (development mode)
- `--env FILE`: Environment file to load

**Success Response**:
```
🚀 Starting Restack development server...

📊 Project: my-project (v1.0.0)
🐍 Python: 3.11.5
📦 Restack SDK: 1.2.3
⏱️  Temporal: Connected

🌐 Server running at: http://localhost:8000
📝 Health check: http://localhost:8000/health

Press Ctrl+C to stop
```

## Global Options

All commands support these global options:

- `--help, -h`: Show command help
- `--version`: Show CLI version
- `--config FILE`: Use specific configuration file
- `--quiet, -q`: Suppress non-error output
- `--verbose, -v`: Enable detailed logging
- `--no-color`: Disable colored output

## Configuration File Contract

### `restack.toml`

Project configuration file following TOML format.

```toml
[project]
name = "my-project"
version = "1.0.0"
description = "My Restack project"
python_version = "3.11"
restack_version = "1.2.3"

[structure]
type = "component"
agents_dir = "agents"
workflows_dir = "workflows"
functions_dir = "functions"

[defaults]
[defaults.retry]
max_attempts = 3
initial_interval_ms = 1000
max_interval_ms = 8000
backoff_multiplier = 2.0
jitter_enabled = true

[defaults.timeouts]
agent_timeout_ms = 30000
workflow_timeout_ms = 60000
function_timeout_ms = 10000
llm_timeout_ms = 15000

[defaults.logging]
level = "INFO"
format = "json"
structured = true

[defaults.llm]
default_provider = "gemini"
default_model = "gemini-1.5-pro"

[testing]
framework = "pytest"
coverage_minimum = 80
generate_tests = true

[migrations]
version = "1.0"
auto_migrate = true
```

### Environment Variables

CLI respects these environment variables:

- `RESTACK_CONFIG`: Path to configuration file
- `RESTACK_LOG_LEVEL`: Override log level
- `RESTACK_NO_COLOR`: Disable colored output
- `GEMINI_API_KEY`: Gemini API key for LLM features
- `OPENAI_API_KEY`: OpenAI API key for LLM features
- `ANTHROPIC_API_KEY`: Anthropic API key for LLM features

## Exit Codes

Standard exit codes across all commands:

- `0`: Success
- `1`: General error (invalid arguments, command failed)
- `2`: Filesystem error (permissions, missing files)
- `3`: Configuration error (invalid config, missing dependencies)
- `4`: Network error (API calls, Temporal connection)
- `5`: Validation error (syntax errors, schema validation)

## Output Formats

### Standard Output

- Use colored output by default (disable with `--no-color`)
- Emoji symbols for visual clarity (✅ ❌ ⚠️ 🔍 etc.)
- Progress indicators for long operations
- Structured information in tables where appropriate

### JSON Output

Available for scripting with `--json` flag on supported commands:

```json
{
  "command": "new",
  "status": "success",
  "project": {
    "name": "my-project",
    "path": "/path/to/my-project",
    "files_created": 23,
    "components_generated": 0
  },
  "execution_time_ms": 1250
}
```

### Error Output

Errors written to stderr with consistent format:

```
Error: Invalid project name 'My Project'
  
  Project names must:
  • Use lowercase letters, numbers, and hyphens only
  • Start with a letter
  • Not end with a hyphen
  
  Examples: my-project, user-service, data-processor
  
  Try: restack new my-project
```

## Validation Rules

### Project Names
- Pattern: `^[a-z][a-z0-9-]*[a-z0-9]$`
- Length: 1-50 characters
- No consecutive hyphens
- Reserved names: `test`, `src`, `lib`, Python keywords

### Component Names
- Pattern: `^[A-Z][a-zA-Z0-9]*$` (PascalCase)
- Length: 1-50 characters
- No Python keywords or built-ins
- Must be valid Python identifiers

### File Paths
- Must be within project boundaries
- No hidden files (starting with `.`)
- Valid filesystem names for target platform
- No conflicts with existing generated files

## Backward Compatibility

### Version Support
- CLI maintains backward compatibility for 1 major version
- Configuration file format is versioned
- Migration system handles breaking changes
- Template compatibility matrix documented

### Deprecation Policy
- Features deprecated for minimum 6 months before removal
- Clear migration paths provided
- Warnings shown for deprecated usage
- Documentation updated with migration guides