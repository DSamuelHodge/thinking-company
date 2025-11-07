"""Validation helpers for project and component generation."""

from __future__ import annotations

import ast
import keyword
import re
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, ValidationError

PROJECT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
COMPONENT_NAME_PATTERN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
MODULE_NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")


class ValidationIssue(BaseModel):
    field: str
    message: str


def validate_project_name(name: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not PROJECT_NAME_PATTERN.match(name):
        issues.append(ValidationIssue(field="name", message="Project name must be kebab-case"))
    if "--" in name or name.startswith("-") or name.endswith("-"):
        issues.append(
            ValidationIssue(
                field="name", message="Project name cannot contain consecutive or edge hyphens"
            )
        )
    return issues


def validate_component_name(name: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not COMPONENT_NAME_PATTERN.match(name):
        issues.append(ValidationIssue(field="name", message="Component name must be PascalCase"))
    if keyword.iskeyword(name.lower()) or name.lower() in keyword.kwlist:
        issues.append(
            ValidationIssue(field="name", message="Component name cannot be Python keyword")
        )
    return issues


def validate_module_name(name: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not MODULE_NAME_PATTERN.match(name):
        issues.append(ValidationIssue(field="module", message="Module name must be snake_case"))
    if keyword.iskeyword(name):
        issues.append(
            ValidationIssue(field="module", message="Module name cannot be Python keyword")
        )
    return issues


def validate_path_within_project(path: Path, project_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        path.relative_to(project_root)
    except ValueError:
        issues.append(ValidationIssue(field="path", message="Path must be within project root"))
    return issues


def validate_pydantic_model(model: type[BaseModel]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        model.model_validate(model.model_construct())
    except ValidationError as error:
        issues.append(ValidationIssue(field=model.__name__, message=str(error)))
    return issues


# --- Doctor command helpers (T052 / T057) ---


def validate_project_structure(project_root: Path) -> list[ValidationIssue]:
    """Check required directories exist in the Restack project."""
    required = ["agents", "workflows", "functions", "tests"]
    issues: list[ValidationIssue] = []
    for name in required:
        if not (project_root / name).exists():
            issues.append(ValidationIssue(field="structure", message=f"Missing directory: {name}"))
    return issues


def validate_restack_toml(data: dict) -> list[ValidationIssue]:
    """Validate minimal schema for restack.toml loaded data.

    Required blocks and keys:
    [project]: name, version, python_version
    [structure]: agents_dir, workflows_dir, functions_dir
    """
    issues: list[ValidationIssue] = []
    project = data.get("project")
    if not isinstance(project, dict):
        issues.append(ValidationIssue(field="project", message="[project] table missing"))
    else:
        for key in ["name", "version", "python_version"]:
            if key not in project:
                issues.append(ValidationIssue(field="project", message=f"Missing key: {key}"))
        # Type checks (best-effort)
        if "python_version" in project and not isinstance(project.get("python_version"), str):
            issues.append(
                ValidationIssue(field="project", message="python_version must be a string")
            )

    structure = data.get("structure")
    if not isinstance(structure, dict):
        issues.append(ValidationIssue(field="structure", message="[structure] table missing"))
    else:
        for key in ["agents_dir", "workflows_dir", "functions_dir"]:
            if key not in structure:
                issues.append(ValidationIssue(field="structure", message=f"Missing key: {key}"))
        for k in ["agents_dir", "workflows_dir", "functions_dir"]:
            if k in structure and not isinstance(structure.get(k), str):
                issues.append(ValidationIssue(field="structure", message=f"{k} must be a string"))

    # Optional sections: validate if present
    retry = data.get("retry")
    if isinstance(retry, dict):
        # Expect positive numbers
        for k in ["max_attempts"]:
            if k in retry and not isinstance(retry[k], int):
                issues.append(ValidationIssue(field="retry", message=f"{k} must be int"))
        for k in ["initial_interval", "backoff_coefficient", "max_interval"]:
            if k in retry and not isinstance(retry[k], (int, float)):
                issues.append(ValidationIssue(field="retry", message=f"{k} must be number"))
        if isinstance(retry.get("max_attempts"), int) and retry["max_attempts"] < 1:
            issues.append(ValidationIssue(field="retry", message="max_attempts must be >= 1"))
        if (
            isinstance(retry.get("initial_interval"), (int, float))
            and retry["initial_interval"] <= 0
        ):
            issues.append(ValidationIssue(field="retry", message="initial_interval must be > 0"))
        if (
            isinstance(retry.get("backoff_coefficient"), (int, float))
            and retry["backoff_coefficient"] <= 0
        ):
            issues.append(ValidationIssue(field="retry", message="backoff_coefficient must be > 0"))
        if isinstance(retry.get("max_interval"), (int, float)) and retry["max_interval"] <= 0:
            issues.append(ValidationIssue(field="retry", message="max_interval must be > 0"))

    timeout = data.get("timeout")
    if isinstance(timeout, dict):
        for k in ["schedule_to_close", "start_to_close", "schedule_to_start"]:
            if k in timeout and not isinstance(timeout[k], int):
                issues.append(ValidationIssue(field="timeout", message=f"{k} must be int"))
            if isinstance(timeout.get(k), int) and timeout[k] < 0:
                issues.append(ValidationIssue(field="timeout", message=f"{k} must be >= 0"))

    logging = data.get("logging")
    if isinstance(logging, dict):
        level = logging.get("level")
        if level is not None and level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            issues.append(ValidationIssue(field="logging", message="level must be a valid level"))
        for k in ["include_timestamp", "include_caller"]:
            if k in logging and not isinstance(logging[k], bool):
                issues.append(ValidationIssue(field="logging", message=f"{k} must be boolean"))

    llm = data.get("llm")
    if isinstance(llm, dict):
        if "max_tokens" in llm and not isinstance(llm["max_tokens"], int):
            issues.append(ValidationIssue(field="llm", message="max_tokens must be int"))
        if isinstance(llm.get("max_tokens"), int) and llm["max_tokens"] <= 0:
            issues.append(ValidationIssue(field="llm", message="max_tokens must be > 0"))
        if "temperature" in llm and not isinstance(llm["temperature"], (int, float)):
            issues.append(ValidationIssue(field="llm", message="temperature must be number"))
        if isinstance(llm.get("temperature"), (int, float)):
            if not (0 <= float(llm["temperature"]) <= 1):
                issues.append(
                    ValidationIssue(field="llm", message="temperature must be between 0 and 1")
                )
    return issues


def validate_python_syntax(
    paths: Iterable[Path], project_root: Path | None = None
) -> list[ValidationIssue]:
    """Validate syntax for each Python file path.

    Returns ValidationIssue list with filename and error message for any syntax errors.
    """
    issues: list[ValidationIssue] = []
    for py in paths:
        try:
            ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError as exc:
            rel = py.relative_to(project_root) if project_root else py
            issues.append(
                ValidationIssue(
                    field="syntax",
                    message=f"{rel}: {exc.msg} (line {exc.lineno})",
                )
            )
    return issues
