"""Pydantic models representing Restack projects and components."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from .config import LoggingConfig, RetryConfig, TimeoutConfig


class ComponentType(str, Enum):
    """Supported component types."""

    AGENT = "agent"
    WORKFLOW = "workflow"
    FUNCTION = "function"
    PIPELINE = "pipeline"
    LLM = "llm"


class Project(BaseModel):
    """Representation of a Restack project directory."""

    name: str = Field(description="Project name (kebab-case)")
    version: str = Field(default="0.1.0", description="Semantic version")
    description: str | None = Field(default=None, description="Project description")
    python_version: str = Field(default="3.11", description="Minimum Python version")
    restack_version: str = Field(default="latest", description="Restack SDK version")
    structure_type: str = Field(default="component", description="Project organization pattern")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    config_version: str = Field(default="1.0.0", description="Configuration schema version")
    components: list[Component] = Field(default_factory=list, description="Generated components")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v:
            raise ValueError("Project name cannot be empty")
        if not v.replace("-", "").isalnum():
            raise ValueError("Project name must contain letters, numbers, or hyphens")
        if "--" in v or v.startswith("-") or v.endswith("-"):
            raise ValueError(
                "Project name cannot start/end with hyphen or contain consecutive hyphens"
            )
        return v

    @field_validator("structure_type")
    @classmethod
    def validate_structure_type(cls, v: str) -> str:
        if v != "component":
            raise ValueError("Only component structure type is currently supported")
        return v


class Component(BaseModel):
    """Base metadata captured for generated components."""

    name: str = Field(description="Component class name (PascalCase)")
    type: ComponentType = Field(description="Component type")
    file_path: Path = Field(description="Path to generated component file")
    test_path: Path | None = Field(default=None, description="Path to generated test file")
    dependencies: list[str] = Field(default_factory=list, description="Python package dependencies")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Generation timestamp"
    )
    template_version: str = Field(default="1.0.0", description="Template version used")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v:
            raise ValueError("Component name cannot be empty")
        if not v[0].isalpha() or not v.replace("_", "").isalnum():
            raise ValueError("Component name must be PascalCase and alphanumeric")
        if not v[0].isupper():
            raise ValueError("Component name must start with uppercase letter")
        return v

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: Path) -> Path:
        if not v.suffix == ".py":
            raise ValueError("Component file path must be a Python file")
        return v


class RetryTimeoutMixin(BaseModel):
    """Mixin for components supporting retry and timeout configuration."""

    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    timeout_config: TimeoutConfig = Field(default_factory=TimeoutConfig)


class Agent(Component, RetryTimeoutMixin):
    workflows: list[str] = Field(default_factory=list, description="Associated workflows")
    input_schema: dict = Field(default_factory=dict, description="Input schema definition")
    output_schema: dict = Field(default_factory=dict, description="Output schema definition")


class Workflow(Component, RetryTimeoutMixin):
    functions: list[str] = Field(default_factory=list, description="Functions used in workflow")
    input_schema: dict = Field(default_factory=dict, description="Workflow input schema")
    output_schema: dict = Field(default_factory=dict, description="Workflow output schema")
    is_pipeline: bool = Field(default=False, description="Whether workflow represents a pipeline")


class Function(Component, RetryTimeoutMixin):
    input_schema: dict = Field(default_factory=dict)
    output_schema: dict = Field(default_factory=dict)
    is_pure: bool = Field(default=False, description="Whether function has side effects")


class PipelineOperator(BaseModel):
    operator_type: str = Field(description="Operator type (sequence, loop, conditional)")
    name: str = Field(description="Operator name")
    parameters: dict = Field(default_factory=dict, description="Operator-specific parameters")


class Pipeline(Workflow):
    operators: list[PipelineOperator] = Field(default_factory=list)
    composition_graph: dict[str, list[str]] = Field(default_factory=dict)
    error_handling: str = Field(default="halt", description="Error handling strategy")


class PromptTemplate(BaseModel):
    version: str = Field(description="Prompt template version")
    description: str | None = Field(default=None)
    content: str = Field(description="Prompt content")


class LLMIntegration(Component):
    provider: str = Field(default="gemini")
    model_name: str = Field(default="gemini-1.5-pro")
    prompt_templates: list[PromptTemplate] = Field(default_factory=list)
    max_tokens: int = Field(default=1024, ge=1)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    tool_server: str | None = Field(default=None, description="Associated FastMCP tool server path")
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
