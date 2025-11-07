# Data Model: Restack Gen CLI

**Phase**: 1 - Design & Contracts  
**Date**: November 6, 2025  
**Context**: Data structures, entities, and relationships for the CLI system

## Core Entities

### Project

Represents a Restack project with its configuration and structure.

**Attributes**:
- `name: str` - Project name (alphanumeric, hyphens allowed)
- `version: str` - Semantic version (e.g., "1.0.0")
- `description: Optional[str]` - Human-readable project description
- `python_version: str` - Minimum Python version requirement (e.g., "3.11")
- `restack_version: str` - Restack SDK version dependency
- `structure_type: Literal["component"]` - Project organization pattern
- `created_at: datetime` - Project creation timestamp
- `config_version: str` - Configuration schema version for migrations

**Relationships**:
- Contains multiple Components (agents, workflows, functions)
- Has one ProjectConfiguration
- Contains zero or more Migrations

**Validation Rules**:
- Name must be valid Python package name
- Version must follow semantic versioning
- Python version must be 3.11 or higher
- Structure type currently only supports "component"

**State Transitions**:
- Created → Configured → Active
- Active → Migrating → Active (during configuration updates)

### Component

Base class for all generated components (Agent, Workflow, Function, Pipeline).

**Attributes**:
- `name: str` - Component name (PascalCase for classes)
- `type: Literal["agent", "workflow", "function", "pipeline", "llm"]` - Component type
- `file_path: Path` - Generated file location
- `test_path: Path` - Generated test file location
- `dependencies: List[str]` - Required Python packages
- `created_at: datetime` - Generation timestamp
- `template_version: str` - Template version used for generation

**Relationships**:
- Belongs to one Project
- May depend on other Components

**Validation Rules**:
- Name must be valid Python identifier
- File paths must be within project boundaries
- Dependencies must be valid package names
- Template version must exist

### Agent

Specialized component representing a Restack agent.

**Attributes** (inherits from Component):
- `workflows: List[str]` - Associated workflow names
- `input_schema: Dict` - Pydantic model definition for inputs
- `output_schema: Dict` - Pydantic model definition for outputs
- `retry_config: RetryConfig` - Retry strategy configuration
- `timeout_ms: int` - Agent timeout in milliseconds

**Validation Rules**:
- Must have at least one workflow
- Input/output schemas must be valid Pydantic definitions
- Timeout must be positive integer
- Workflow names must reference existing workflows

### Workflow

Represents a Temporal workflow definition.

**Attributes** (inherits from Component):
- `functions: List[str]` - Function names used in workflow
- `input_schema: Dict` - Workflow input parameters
- `output_schema: Dict` - Workflow return type
- `retry_config: RetryConfig` - Retry strategy for activities
- `timeout_ms: int` - Workflow timeout
- `is_pipeline: bool` - Whether this workflow is a complex pipeline

**Validation Rules**:
- Function names must reference existing functions
- Schemas must be valid Pydantic definitions
- Timeout must be positive integer
- Pipeline workflows have additional operator grammar validation

### Function

Represents a Temporal activity function.

**Attributes** (inherits from Component):
- `input_schema: Dict` - Function parameters schema
- `output_schema: Dict` - Function return type schema
- `retry_config: RetryConfig` - Activity retry configuration
- `timeout_ms: int` - Function timeout
- `is_pure: bool` - Whether function has side effects

**Validation Rules**:
- Schemas must be valid Pydantic definitions
- Pure functions should not have external dependencies
- Timeout must be positive for non-pure functions

### Pipeline

Specialized workflow with operator grammar support.

**Attributes** (inherits from Workflow):
- `operators: List[PipelineOperator]` - Sequence, loop, conditional operators
- `composition_graph: Dict` - DAG representation of pipeline flow
- `error_handling: ErrorHandlingStrategy` - How to handle operator failures

**Validation Rules**:
- Operator graph must be acyclic
- All operators must reference existing functions/workflows
- Error handling strategy must be valid

### LLMIntegration

Represents an LLM-powered component.

**Attributes** (inherits from Component):
- `provider: Literal["gemini", "openai", "anthropic"]` - LLM provider
- `model_name: str` - Specific model (e.g., "gemini-1.5-pro")
- `prompt_templates: List[PromptTemplate]` - Versioned prompt templates
- `max_tokens: int` - Maximum response length
- `temperature: float` - Randomness setting (0.0-1.0)

**Validation Rules**:
- Provider must be supported
- Model name must be valid for provider
- Temperature must be between 0.0 and 1.0
- Max tokens must be positive integer

## Configuration Entities

### ProjectConfiguration

Project-wide settings and defaults.

**Attributes**:
- `retry_strategy: RetryConfig` - Default retry configuration
- `timeout_defaults: TimeoutConfig` - Default timeouts by component type
- `logging_config: LoggingConfig` - Structured logging settings
- `llm_config: LLMConfig` - Default LLM provider settings
- `testing_config: TestingConfig` - Test generation preferences

### RetryConfig

Retry strategy configuration using exponential backoff with jitter.

**Attributes**:
- `max_attempts: int` - Maximum retry attempts (default: 3)
- `initial_interval_ms: int` - Initial retry delay (default: 1000)
- `max_interval_ms: int` - Maximum retry delay (default: 8000)
- `backoff_multiplier: float` - Exponential backoff factor (default: 2.0)
- `jitter_enabled: bool` - Whether to add randomization (default: True)

**Validation Rules**:
- Max attempts must be 1-10
- Intervals must be positive integers
- Backoff multiplier must be >= 1.0

### TimeoutConfig

Default timeout configurations by component type.

**Attributes**:
- `agent_timeout_ms: int` - Default agent timeout
- `workflow_timeout_ms: int` - Default workflow timeout
- `function_timeout_ms: int` - Default function timeout
- `llm_timeout_ms: int` - Default LLM request timeout

### LoggingConfig

Structured logging configuration.

**Attributes**:
- `level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]` - Log level
- `format: str` - Log format string
- `structured: bool` - Whether to use JSON formatting
- `file_output: Optional[str]` - Log file path

### LLMConfig

LLM provider default settings.

**Attributes**:
- `default_provider: str` - Primary LLM provider (default: "gemini")
- `api_keys: Dict[str, str]` - Provider API key references
- `default_models: Dict[str, str]` - Default model per provider
- `rate_limits: Dict[str, RateLimit]` - Provider rate limiting

## Migration Entities

### Migration

Represents a configuration migration step.

**Attributes**:
- `id: str` - Timestamp-based migration ID (YYYYMMDDHHMMSS)
- `name: str` - Human-readable migration name
- `description: str` - What this migration changes
- `up_script: str` - Python code to apply migration
- `down_script: str` - Python code to reverse migration
- `created_at: datetime` - Migration creation time
- `applied_at: Optional[datetime]` - When migration was applied

**Validation Rules**:
- ID must be unique and timestamp-based
- Up/down scripts must be valid Python code
- Migration name must be descriptive

**State Transitions**:
- Created → Pending → Applied
- Applied → Pending (during rollback) → Created

### MigrationHistory

Tracks applied migrations for a project.

**Attributes**:
- `project_name: str` - Associated project name
- `applied_migrations: List[str]` - Migration IDs in application order
- `current_version: str` - Current configuration schema version
- `last_updated: datetime` - Last migration timestamp

## Template Entities

### Template

Represents a code generation template.

**Attributes**:
- `name: str` - Template identifier
- `type: str` - Component type this template generates
- `version: str` - Template version for compatibility
- `content: str` - Jinja2 template content
- `variables: List[TemplateVariable]` - Required template variables
- `dependencies: List[str]` - Required Python packages

### TemplateVariable

Variable definition for template rendering.

**Attributes**:
- `name: str` - Variable name
- `type: str` - Python type annotation
- `required: bool` - Whether variable is mandatory
- `default: Optional[Any]` - Default value if not required
- `description: str` - Human-readable description

## Validation Schemas

### ComponentName
- Pattern: `^[A-Z][a-zA-Z0-9]*$` (PascalCase)
- Length: 1-50 characters
- Reserved names: Python keywords, built-in functions

### ProjectName
- Pattern: `^[a-z][a-z0-9-]*$` (kebab-case)
- Length: 1-50 characters
- No consecutive hyphens
- No leading/trailing hyphens

### VersionString
- Pattern: Semantic versioning (major.minor.patch)
- Optional pre-release and build metadata
- Must be valid according to semver specification

## Data Flow

### Project Creation
1. Validate project name and configuration
2. Create project directory structure
3. Generate base configuration files
4. Initialize migration history
5. Create initial components (if specified)

### Component Generation
1. Validate component name and type
2. Load appropriate template
3. Gather template variables
4. Render template with project context
5. Write generated files
6. Update project configuration
7. Generate corresponding tests

### Configuration Migration
1. Detect configuration schema changes
2. Create migration script
3. Validate migration (dry run)
4. Apply migration to project
5. Update migration history
6. Verify project still functions

## Persistence

### File-based Storage
- Project metadata: `restack.toml` in project root
- Migration history: `.restack/migrations.json`
- Template cache: `.restack/templates/`
- Generated code: Standard Python package structure

### Schema Evolution
- Configuration schema versioning
- Backward-compatible changes when possible
- Migration scripts for breaking changes
- Validation of existing projects on CLI operations