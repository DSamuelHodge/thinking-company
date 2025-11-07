"""Pytest configuration and fixtures for restack-gen tests."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files.

    Yields:
        Path: Temporary directory path

    The directory and all its contents are automatically cleaned up after the test.
    """
    temp_path = Path(tempfile.mkdtemp(prefix="restack_test_"))
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_project_dir(temp_dir: Path) -> Path:
    """Create a sample Restack project structure for testing.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to sample project directory with basic structure
    """
    project_dir = temp_dir / "test_project"
    project_dir.mkdir(parents=True)

    # Create standard directories
    (project_dir / "agents").mkdir()
    (project_dir / "workflows").mkdir()
    (project_dir / "functions").mkdir()
    (project_dir / "tests").mkdir()

    # Create sample restack.toml
    config_content = """[project]
name = "test_project"
version = "0.1.0"
python_version = "3.11"

[retry]
max_attempts = 3
initial_interval = 1.0
backoff_coefficient = 2.0

[timeout]
schedule_to_close = 600
start_to_close = 300

[logging]
level = "INFO"
format = "json"
"""
    (project_dir / "restack.toml").write_text(config_content)

    return project_dir


@pytest.fixture
def mock_templates_dir(temp_dir: Path) -> Path:
    """Create a directory with mock template files for testing.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to mock templates directory
    """
    templates_dir = temp_dir / "templates"
    templates_dir.mkdir()

    # Create agent template
    agent_template = templates_dir / "agents"
    agent_template.mkdir()
    (agent_template / "agent.py.j2").write_text(
        """\"\"\"{{ name }} agent.\"\"\"

from restack_ai import Agent

class {{ name }}Agent(Agent):
    \"\"\"{{ description }}\"\"\"
    
    def __init__(self):
        super().__init__(name="{{ name | snake_case }}")
"""
    )

    # Create workflow template
    workflow_template = templates_dir / "workflows"
    workflow_template.mkdir()
    (workflow_template / "workflow.py.j2").write_text(
        """\"\"\"{{ name }} workflow.\"\"\"

from restack_ai import Workflow

class {{ name }}Workflow(Workflow):
    \"\"\"{{ description }}\"\"\"
    
    async def run(self):
        pass
"""
    )

    return templates_dir


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner.

    Returns:
        CliRunner: Click testing runner instance
    """
    from click.testing import CliRunner

    return CliRunner()


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    """Reset environment variables for each test.

    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    # Clear any environment variables that might affect tests
    env_vars_to_clear = [
        "RESTACK_CONFIG",
        "RESTACK_ENV",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
    ]
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)
