"""Configuration models for Restack Gen CLI.

This module defines Pydantic models for various configuration aspects
of generated Restack projects, including retry strategies, timeouts, and logging.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RetryConfig(BaseModel):
    """Configuration for retry behavior with exponential backoff.

    Implements exponential backoff with jitter as recommended by Temporal best practices.
    Default values provide: 1s, 2s, 4s, 8s intervals with jitter.
    """

    max_attempts: int = Field(
        default=3, ge=1, le=10, description="Maximum number of retry attempts"
    )
    initial_interval: float = Field(
        default=1.0, gt=0, description="Initial retry interval in seconds"
    )
    backoff_coefficient: float = Field(
        default=2.0,
        ge=1.0,
        description="Multiplier for exponential backoff (2.0 = double each time)",
    )
    max_interval: float = Field(default=10.0, gt=0, description="Maximum retry interval in seconds")
    jitter: bool = Field(
        default=True, description="Add randomization to retry intervals to prevent thundering herd"
    )

    @field_validator("max_interval")
    @classmethod
    def validate_max_interval(cls, v: float, info) -> float:
        """Ensure max_interval is greater than initial_interval."""
        if "initial_interval" in info.data and v < info.data["initial_interval"]:
            raise ValueError("max_interval must be greater than or equal to initial_interval")
        return v


class TimeoutConfig(BaseModel):
    """Timeout configuration for workflows and activities.

    Based on Temporal timeout semantics:
    - schedule_to_close: Total time for workflow/activity including retries
    - start_to_close: Time for a single execution attempt
    """

    schedule_to_close: int = Field(
        default=600, ge=1, description="Total timeout in seconds including all retries"
    )
    start_to_close: int = Field(
        default=300, ge=1, description="Timeout in seconds for a single execution attempt"
    )
    schedule_to_start: int | None = Field(
        default=None, ge=1, description="Optional timeout for time in queue before starting"
    )

    @field_validator("start_to_close")
    @classmethod
    def validate_start_to_close(cls, v: int, info) -> int:
        """Ensure start_to_close is less than schedule_to_close."""
        if "schedule_to_close" in info.data and v > info.data["schedule_to_close"]:
            raise ValueError("start_to_close must be less than or equal to schedule_to_close")
        return v


class LoggingConfig(BaseModel):
    """Configuration for structured logging.

    Supports both JSON and text formats with configurable log levels.
    JSON format recommended for production observability.
    """

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Minimum log level to output"
    )
    format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format (json for structured logging, text for human-readable)",
    )
    include_timestamp: bool = Field(default=True, description="Include timestamp in log entries")
    include_caller: bool = Field(
        default=False, description="Include file and line number of log call"
    )
    output_file: str | None = Field(
        default=None, description="Optional file path for log output (stdout if not specified)"
    )


class ProjectConfig(BaseModel):
    """Top-level configuration for a Restack project.

    This model represents the complete configuration stored in restack.toml.
    """

    name: str = Field(description="Project name (kebab-case recommended)")
    version: str = Field(default="0.1.0", description="Project version (semantic versioning)")
    python_version: str = Field(default="3.11", description="Minimum Python version required")
    description: str | None = Field(default=None, description="Project description")

    retry: RetryConfig = Field(
        default_factory=RetryConfig, description="Default retry configuration for all components"
    )
    timeout: TimeoutConfig = Field(
        default_factory=TimeoutConfig,
        description="Default timeout configuration for workflows and activities",
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig, description="Logging configuration"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate project name follows kebab-case convention."""
        if not v:
            raise ValueError("Project name cannot be empty")
        if " " in v or "_" in v:
            raise ValueError(
                "Project name should use kebab-case (dashes, not spaces or underscores)"
            )
        if not v.replace("-", "").replace(".", "").isalnum():
            raise ValueError("Project name can only contain letters, numbers, dashes, and dots")
        return v

    @field_validator("python_version")
    @classmethod
    def validate_python_version(cls, v: str) -> str:
        """Validate Python version is within supported range (3.10–3.13)."""
        try:
            major, minor = map(int, v.split(".")[:2])
            if major != 3 or minor < 10 or minor > 13:
                raise ValueError("Python version must be between 3.10 and 3.13")
        except (ValueError, AttributeError):
            raise ValueError("Invalid Python version format (expected: 3.x)") from None
        return v
