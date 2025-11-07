"""Integration tests for FastMCP server scaffold generation."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from click.testing import CliRunner

from restack_gen.cli.main import cli


@pytest.fixture
def test_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "fastmcp-project"
    project_dir.mkdir()

    (project_dir / "restack.toml").write_text("[project]\nname = 'fastmcp-project'\n")
    (project_dir / "pyproject.toml").write_text(
        "[project]\nname = 'fastmcp-project'\nversion = '0.1.0'\n"
    )

    (project_dir / "agents").mkdir()
    (project_dir / "workflows").mkdir()
    (project_dir / "functions").mkdir()
    (project_dir / "tests").mkdir()

    return project_dir


def test_fastmcp_server_scaffold(test_project: Path, monkeypatch) -> None:
    monkeypatch.chdir(test_project)
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "llm", "TestLLM"])

    assert result.exit_code == 0

    server_file = test_project / "tools" / "test_llm_tools.py"
    assert server_file.exists()

    # Check 'mcp' symbol and parse syntax
    content = server_file.read_text()
    assert "mcp = FastMCP" in content
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Generated FastMCP server has syntax error: {e}")
