"""Integration tests for component generation commands."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from click.testing import CliRunner

from restack_gen.cli.main import cli


@pytest.fixture
def test_project(tmp_path: Path) -> Path:
    """Create a temporary test project."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create minimal project structure
    (project_dir / "restack.toml").write_text("[project]\nname = 'test-project'\n")
    (project_dir / "pyproject.toml").write_text(
        "[project]\nname = 'test-project'\nversion = '0.1.0'\n"
    )

    # Create component directories
    (project_dir / "agents").mkdir()
    (project_dir / "workflows").mkdir()
    (project_dir / "functions").mkdir()
    (project_dir / "tests").mkdir()

    return project_dir


class TestGenerateAgent:
    """Tests for agent generation."""

    def test_generate_agent_creates_file(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation creates the expected file."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "agent", "TestAgent"])

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Generated agent: TestAgent" in result.output

        agent_file = test_project / "agents" / "test_agent.py"
        assert agent_file.exists()

        # Verify content
        content = agent_file.read_text()
        assert "class TestAgent" in content
        assert "TestAgentInput" in content
        assert "TestAgentOutput" in content

    def test_generate_agent_creates_test_file(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation creates test file."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "agent", "TestAgent"])

        assert result.exit_code == 0

        test_file = test_project / "tests" / "test_test_agent.py"
        assert test_file.exists()

        # Verify content
        content = test_file.read_text()
        assert "class TestTestAgent" in content
        assert "async def test_run_with_valid_input" in content

    def test_generate_agent_without_tests(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation without test files."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "agent", "TestAgent", "--no-tests"])

        assert result.exit_code == 0

        agent_file = test_project / "agents" / "test_agent.py"
        test_file = test_project / "tests" / "test_test_agent.py"

        assert agent_file.exists()
        assert not test_file.exists()

    def test_generate_agent_with_description(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation with description."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                "agent",
                "TestAgent",
                "--description",
                "Custom agent description",
            ],
        )

        assert result.exit_code == 0

        agent_file = test_project / "agents" / "test_agent.py"
        content = agent_file.read_text()
        assert "Custom agent description" in content

    def test_generate_agent_fails_without_project(self, tmp_path: Path, monkeypatch) -> None:
        """Test agent generation fails outside a project."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "agent", "TestAgent"])

        assert result.exit_code == 1
        assert "Not in a Restack project" in result.output

    def test_generate_agent_fails_with_invalid_name(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation fails with invalid name."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "agent", "invalid-name"])

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_generate_agent_fails_if_exists(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation fails if file exists."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()

        # Create agent first time
        runner.invoke(cli, ["generate", "agent", "TestAgent"])

        # Try to create again
        result = runner.invoke(cli, ["generate", "agent", "TestAgent"])

        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_generate_agent_force_overwrites(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation with --force overwrites existing file."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()

        # Create agent first time
        runner.invoke(cli, ["generate", "agent", "TestAgent"])

        # Create again with --force
        result = runner.invoke(cli, ["generate", "agent", "TestAgent", "--force"])

        assert result.exit_code == 0
        assert "Generated agent: TestAgent" in result.output

    def test_generate_agent_dry_run(self, test_project: Path, monkeypatch) -> None:
        """Test agent generation dry run."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "agent", "TestAgent", "--dry-run"])

        assert result.exit_code == 0
        assert "Would generate agent: TestAgent" in result.output

        agent_file = test_project / "agents" / "test_agent.py"
        assert not agent_file.exists()

    def test_generated_agent_is_valid_python(self, test_project: Path, monkeypatch) -> None:
        """Test generated agent file is syntactically valid Python."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        runner.invoke(cli, ["generate", "agent", "TestAgent"])

        agent_file = test_project / "agents" / "test_agent.py"
        content = agent_file.read_text()

        # Parse as AST to verify syntax
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Generated agent has syntax error: {e}")


class TestGenerateWorkflow:
    """Tests for workflow generation."""

    def test_generate_workflow_creates_file(self, test_project: Path, monkeypatch) -> None:
        """Test workflow generation creates the expected file."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "workflow", "TestWorkflow"])

        assert result.exit_code == 0
        assert "Generated workflow: TestWorkflow" in result.output

        workflow_file = test_project / "workflows" / "test_workflow.py"
        assert workflow_file.exists()

        # Verify content
        content = workflow_file.read_text()
        assert "class TestWorkflow" in content
        assert "TestWorkflowInput" in content
        assert "TestWorkflowOutput" in content

    def test_generate_workflow_with_functions(self, test_project: Path, monkeypatch) -> None:
        """Test workflow generation with function examples."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", "workflow", "TestWorkflow", "--with-functions"],
        )

        assert result.exit_code == 0

        workflow_file = test_project / "workflows" / "test_workflow.py"
        content = workflow_file.read_text()
        assert "workflow.execute_activity" in content or "Example" in content

    def test_generate_workflow_with_timeout(self, test_project: Path, monkeypatch) -> None:
        """Test workflow generation with timeout."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", "workflow", "TestWorkflow", "--timeout", "60"],
        )

        assert result.exit_code == 0

        workflow_file = test_project / "workflows" / "test_workflow.py"
        content = workflow_file.read_text()
        assert "60" in content

    def test_generated_workflow_is_valid_python(self, test_project: Path, monkeypatch) -> None:
        """Test generated workflow file is syntactically valid Python."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        runner.invoke(cli, ["generate", "workflow", "TestWorkflow"])

        workflow_file = test_project / "workflows" / "test_workflow.py"
        content = workflow_file.read_text()

        # Parse as AST to verify syntax
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Generated workflow has syntax error: {e}")


class TestGenerateFunction:
    """Tests for function generation."""

    def test_generate_function_creates_file(self, test_project: Path, monkeypatch) -> None:
        """Test function generation creates the expected file."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "function", "TestFunction"])

        assert result.exit_code == 0
        assert "Generated function: TestFunction" in result.output

        function_file = test_project / "functions" / "test_function.py"
        assert function_file.exists()

        # Verify content
        content = function_file.read_text()
        assert "class TestFunction" in content
        assert "TestFunctionInput" in content
        assert "TestFunctionOutput" in content

    def test_generate_function_pure(self, test_project: Path, monkeypatch) -> None:
        """Test function generation as pure function."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "function", "TestFunction", "--pure"])

        assert result.exit_code == 0

        function_file = test_project / "functions" / "test_function.py"
        content = function_file.read_text()
        assert "async def test_function" in content
        # Pure functions should define the function directly, not wrap it in a class
        # But Input/Output classes will still exist
        assert "@function.defn" in content

    def test_generate_function_with_timeout(self, test_project: Path, monkeypatch) -> None:
        """Test function generation with timeout."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", "function", "TestFunction", "--timeout", "30"],
        )

        assert result.exit_code == 0

        function_file = test_project / "functions" / "test_function.py"
        content = function_file.read_text()
        assert "30" in content

    def test_generated_function_is_valid_python(self, test_project: Path, monkeypatch) -> None:
        """Test generated function file is syntactically valid Python."""
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        runner.invoke(cli, ["generate", "function", "TestFunction"])

        function_file = test_project / "functions" / "test_function.py"
        content = function_file.read_text()

        # Parse as AST to verify syntax
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Generated function has syntax error: {e}")
