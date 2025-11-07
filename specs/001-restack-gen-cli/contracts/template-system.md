# Template System Contracts

**Phase**: 1 - Design & Contracts  
**Date**: November 6, 2025  
**Context**: Code generation template specifications and interfaces

## Template Engine Interface

### Base Template Class

```python
class BaseTemplate:
    """Base class for all code generation templates."""
    
    def __init__(self, template_path: Path, variables: Dict[str, Any]):
        self.template_path = template_path
        self.variables = variables
        self.jinja_env = self._create_jinja_environment()
    
    def render(self) -> str:
        """Render template with provided variables."""
        template = self.jinja_env.get_template(str(self.template_path))
        return template.render(**self.variables)
    
    def validate_variables(self) -> List[ValidationError]:
        """Validate required variables are provided."""
        pass
    
    def get_output_path(self, project_root: Path) -> Path:
        """Determine where generated file should be written."""
        pass
```

### Template Variable Schema

Each template must define its required variables:

```python
class TemplateSchema:
    """Schema definition for template variables."""
    
    required_vars: List[str]
    optional_vars: Dict[str, Any]  # name -> default value
    validation_rules: Dict[str, Callable]
    
    def validate(self, variables: Dict[str, Any]) -> List[ValidationError]:
        """Validate provided variables against schema."""
        pass
```

## Template Categories

### Project Template

Creates the initial project structure.

**Template Path**: `templates/project/`

**Required Variables**:
```python
{
    "project_name": str,          # kebab-case project name
    "project_description": str,   # human-readable description
    "python_version": str,        # e.g., "3.11"
    "restack_version": str,       # e.g., "1.2.3"
    "author_name": str,           # optional, from git config
    "author_email": str,          # optional, from git config
    "license": str,               # default: "MIT"
}
```

**Generated Files**:
```
project_name/
├── restack.toml              # Project configuration
├── pyproject.toml            # Python packaging config
├── requirements.txt          # Dependencies
├── README.md                 # Project documentation
├── .gitignore               # Git ignore rules
├── agents/                   # Agent components directory
│   └── __init__.py
├── workflows/                # Workflow components directory
│   └── __init__.py
├── functions/                # Function components directory
│   └── __init__.py
├── tests/                    # Test suite
│   ├── conftest.py
│   ├── agents/
│   ├── workflows/
│   └── functions/
└── .restack/                 # CLI metadata
    ├── migrations.json
    └── templates/
```

### Agent Template

Generates a Restack agent implementation.

**Template Path**: `templates/agents/agent.py.j2`

**Required Variables**:
```python
{
    "agent_name": str,            # PascalCase class name
    "agent_description": str,     # Human-readable description
    "workflows": List[str],       # Associated workflow names
    "input_schema": Dict,         # Pydantic model definition
    "output_schema": Dict,        # Pydantic model definition
    "retry_config": RetryConfig,  # Retry configuration
    "timeout_ms": int,           # Agent timeout
}
```

**Generated Files**:
- `agents/{snake_case_name}.py` - Agent implementation
- `tests/agents/test_{snake_case_name}.py` - Test suite

**Template Structure**:
```python
# agents/{{agent_name|snake_case}}.py
from typing import Any, Dict
from pydantic import BaseModel
from restack import Agent

class {{input_schema.name}}(BaseModel):
    {% for field_name, field_type in input_schema.fields.items() -%}
    {{field_name}}: {{field_type}}
    {% endfor %}

class {{output_schema.name}}(BaseModel):
    {% for field_name, field_type in output_schema.fields.items() -%}
    {{field_name}}: {{field_type}}
    {% endfor %}

class {{agent_name}}(Agent):
    """{{agent_description}}"""
    
    def __init__(self):
        super().__init__(
            name="{{agent_name|snake_case}}",
            workflows=[{{workflows|map('string')|join(', ')}}],
            timeout_ms={{timeout_ms}}
        )
    
    async def handle(self, input_data: {{input_schema.name}}) -> {{output_schema.name}}:
        """Main agent logic implementation."""
        # TODO: Implement agent logic
        pass
```

### Workflow Template

Generates a Temporal workflow implementation.

**Template Path**: `templates/workflows/workflow.py.j2`

**Required Variables**:
```python
{
    "workflow_name": str,         # PascalCase class name
    "workflow_description": str,  # Human-readable description
    "functions": List[str],       # Function names used
    "input_schema": Dict,         # Input parameters schema
    "output_schema": Dict,        # Return type schema
    "retry_config": RetryConfig,  # Retry configuration
    "timeout_ms": int,           # Workflow timeout
    "is_pipeline": bool,         # Whether it's a complex pipeline
}
```

**Generated Files**:
- `workflows/{snake_case_name}.py` - Workflow implementation
- `tests/workflows/test_{snake_case_name}.py` - Test suite

### Function Template

Generates a Temporal activity function.

**Template Path**: `templates/functions/function.py.j2`

**Required Variables**:
```python
{
    "function_name": str,         # PascalCase function name
    "function_description": str,  # Human-readable description
    "input_schema": Dict,         # Parameters schema
    "output_schema": Dict,        # Return type schema
    "retry_config": RetryConfig,  # Retry configuration
    "timeout_ms": int,           # Function timeout
    "is_pure": bool,             # Has side effects or not
}
```

### Pipeline Template

Generates a complex workflow with operator grammar.

**Template Path**: `templates/pipelines/pipeline.py.j2`

**Required Variables**:
```python
{
    "pipeline_name": str,         # PascalCase class name
    "pipeline_description": str,  # Human-readable description
    "operators": List[Dict],      # Operator definitions
    "composition_graph": Dict,    # Pipeline flow definition
    "error_handling": str,        # Error strategy
    "input_schema": Dict,         # Input parameters
    "output_schema": Dict,        # Output schema
}
```

**Operator Types**:
```python
# Sequence Operator
{
    "type": "sequence",
    "steps": List[str],           # Function/workflow names
    "name": str                   # Operator instance name
}

# Loop Operator
{
    "type": "loop",
    "condition": str,             # Loop condition expression
    "body": str,                  # Function/workflow to execute
    "max_iterations": int,        # Safety limit
    "name": str
}

# Conditional Operator
{
    "type": "conditional",
    "condition": str,             # Boolean expression
    "true_branch": str,           # Function/workflow if true
    "false_branch": str,          # Function/workflow if false
    "name": str
}
```

### LLM Integration Template

Generates LLM-powered component with prompt versioning.

**Template Path**: `templates/llm/llm_integration.py.j2`

**Required Variables**:
```python
{
    "integration_name": str,      # PascalCase class name
    "integration_description": str, # Human-readable description
    "provider": str,              # LLM provider (gemini, openai, anthropic)
    "model_name": str,           # Specific model
    "prompt_templates": List[Dict], # Versioned prompts
    "max_tokens": int,           # Response length limit
    "temperature": float,        # Randomness (0.0-1.0)
    "input_schema": Dict,        # Input parameters
    "output_schema": Dict,       # Structured output
}
```

**Prompt Template Structure**:
```python
{
    "name": str,                 # Prompt identifier
    "version": str,              # Version number
    "system_prompt": str,        # System instructions
    "user_template": str,        # User message template
    "variables": List[str],      # Required variables
    "output_format": str,        # Expected response format
}
```

## Template Filters and Functions

### Custom Jinja2 Filters

```python
# String manipulation
{{ "UserAgent" | snake_case }}          # -> "user_agent"
{{ "user_agent" | pascal_case }}        # -> "UserAgent"
{{ "user-agent" | camel_case }}         # -> "userAgent"
{{ "UserAgent" | kebab_case }}          # -> "user-agent"

# Code generation
{{ schema | pydantic_model }}           # Generate Pydantic model
{{ fields | dataclass_fields }}        # Generate dataclass fields
{{ imports | sort_imports }}           # Sort and organize imports

# Documentation
{{ text | docstring(width=72) }}       # Format as Python docstring
{{ params | param_docs }}              # Generate parameter docs
```

### Custom Functions

```python
# Type conversion
{{ python_type("string") }}            # -> "str"
{{ python_type("integer") }}           # -> "int"
{{ json_to_pydantic(schema) }}         # Convert JSON schema

# Validation
{{ validate_name(name, "class") }}     # Validate naming conventions
{{ validate_imports(imports) }}        # Check import validity

# File operations
{{ relative_path(from_path, to_path) }} # Calculate relative paths
{{ ensure_directory(path) }}           # Ensure directory exists
```

## Template Inheritance

### Base Templates

Common functionality shared across component templates.

**Base Python File Template** (`templates/base/python_file.py.j2`):
```python
#!/usr/bin/env python3
"""
{{ file_description }}

Generated by Restack Gen CLI on {{ generation_date }}.
Do not modify this file directly - regenerate using the CLI.
"""

{% block imports -%}
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
{% endblock %}

{% block models -%}
# Pydantic models will be inserted here
{% endblock %}

{% block implementation -%}
# Component implementation will be inserted here
{% endblock %}

{% block main -%}
if __name__ == "__main__":
    # Main execution block for testing
    pass
{% endblock %}
```

**Base Test Template** (`templates/base/test_file.py.j2`):
```python
#!/usr/bin/env python3
"""
Tests for {{ component_name }}.

Generated by Restack Gen CLI on {{ generation_date }}.
"""

import pytest
from unittest.mock import Mock, patch
{% block test_imports -%}
{% endblock %}

class Test{{ component_name }}:
    """Test suite for {{ component_name }}."""
    
    {% block test_setup -%}
    def setup_method(self):
        """Set up test fixtures before each test method."""
        pass
    {% endblock %}
    
    {% block test_methods -%}
    def test_initialization(self):
        """Test component initialization."""
        # TODO: Implement initialization test
        pass
    
    def test_basic_functionality(self):
        """Test basic component functionality."""
        # TODO: Implement functionality test
        pass
    {% endblock %}
```

### Component-Specific Extensions

Each component type extends the base templates:

```python
# templates/agents/agent.py.j2
{% extends "base/python_file.py.j2" %}

{% block imports %}
{{ super() }}
from restack import Agent
{% endblock %}

{% block implementation %}
class {{ agent_name }}(Agent):
    # Agent-specific implementation
{% endblock %}
```

## Template Validation

### Schema Validation

Templates must include schema definitions for validation:

```python
# template_schema.json
{
    "template_name": "agent",
    "version": "1.0.0",
    "required_variables": [
        "agent_name",
        "agent_description",
        "workflows"
    ],
    "optional_variables": {
        "timeout_ms": 30000,
        "retry_config": {
            "max_attempts": 3,
            "initial_interval_ms": 1000
        }
    },
    "validation_rules": {
        "agent_name": "^[A-Z][a-zA-Z0-9]*$",
        "timeout_ms": "positive_integer",
        "workflows": "non_empty_list"
    }
}
```

### Template Testing

Each template should include test cases:

```python
# tests/templates/test_agent_template.py
def test_agent_template_renders_correctly():
    """Test agent template renders with valid variables."""
    variables = {
        "agent_name": "TestAgent",
        "agent_description": "A test agent",
        "workflows": ["TestWorkflow"],
        "timeout_ms": 30000
    }
    
    template = AgentTemplate(variables)
    result = template.render()
    
    assert "class TestAgent(Agent):" in result
    assert "TestWorkflow" in result

def test_agent_template_validation():
    """Test template variable validation."""
    invalid_variables = {"agent_name": "invalid_name"}
    
    template = AgentTemplate(invalid_variables)
    errors = template.validate_variables()
    
    assert len(errors) > 0
    assert "agent_name must be PascalCase" in str(errors[0])
```

## Template Versioning

### Version Management

Templates are versioned for backward compatibility:

```
templates/
├── v1.0/
│   ├── agents/
│   ├── workflows/
│   └── functions/
├── v1.1/
│   ├── agents/           # Updated templates
│   ├── workflows/
│   └── functions/
└── current/              # Symlink to latest version
```

### Migration Support

Template migrations handle breaking changes:

```python
class TemplateMigration:
    """Migrate templates between versions."""
    
    def migrate_agent_v1_0_to_v1_1(self, variables: Dict) -> Dict:
        """Migrate agent template variables from v1.0 to v1.1."""
        # Handle breaking changes in template variables
        if "retry_attempts" in variables:
            variables["retry_config"] = {
                "max_attempts": variables.pop("retry_attempts")
            }
        return variables
```

## Error Handling

### Template Errors

Common template errors and their handling:

```python
class TemplateError(Exception):
    """Base exception for template-related errors."""
    pass

class TemplateNotFoundError(TemplateError):
    """Template file not found."""
    pass

class TemplateVariableError(TemplateError):
    """Invalid or missing template variables."""
    pass

class TemplateRenderError(TemplateError):
    """Error during template rendering."""
    pass
```

### Error Recovery

```python
def render_with_fallback(template_path: Path, variables: Dict) -> str:
    """Render template with fallback to default template."""
    try:
        return render_template(template_path, variables)
    except TemplateError as e:
        logger.warning(f"Template error: {e}, using fallback")
        return render_default_template(variables)
```

## Performance Considerations

### Template Caching

```python
class TemplateCache:
    """Cache compiled templates for performance."""
    
    def __init__(self):
        self._cache = {}
        self._jinja_env = self._create_environment()
    
    def get_template(self, template_path: Path) -> Template:
        """Get cached template or compile and cache."""
        cache_key = str(template_path)
        
        if cache_key not in self._cache:
            self._cache[cache_key] = self._jinja_env.get_template(cache_key)
        
        return self._cache[cache_key]
```

### Lazy Loading

Templates are loaded only when needed to reduce startup time.

### Batch Operations

Support for generating multiple components in a single operation for better performance.