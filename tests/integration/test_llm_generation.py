"""Integration tests for LLM generation command."""

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

    # Minimal project config
    (project_dir / "restack.toml").write_text("[project]\nname = 'test-project'\n")
    (project_dir / "pyproject.toml").write_text(
        "[project]\nname = 'test-project'\nversion = '0.1.0'\n"
    )

    # Basic dirs
    (project_dir / "agents").mkdir()
    (project_dir / "workflows").mkdir()
    (project_dir / "functions").mkdir()
    (project_dir / "tests").mkdir()

    return project_dir


def test_generate_llm_creates_files(test_project: Path, monkeypatch) -> None:
    monkeypatch.chdir(test_project)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["generate", "llm", "TestLLM", "--provider", "gemini", "--with-prompts"]
    )

    assert result.exit_code == 0, result.output
    assert "Generated LLM: TestLLM" in result.output

    llm_file = test_project / "llm" / "test_llm.py"
    provider_file = test_project / "llm" / "providers" / "gemini.py"
    server_file = test_project / "tools" / "test_llm_tools.py"
    prompt_file = test_project / "prompts" / "test_llm" / "v1.txt"

    assert llm_file.exists()
    assert provider_file.exists()
    assert server_file.exists()
    assert prompt_file.exists()

    # Syntax check
    for py_path in (llm_file, provider_file, server_file):
        content = py_path.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Generated file has syntax error: {py_path}: {e}")


def test_restack_toml_updated_with_fastmcp(test_project: Path, monkeypatch) -> None:
    monkeypatch.chdir(test_project)
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "llm", "TestLLM"])  # defaults

    assert result.exit_code == 0

    toml_content = (test_project / "restack.toml").read_text()
    assert "[fastmcp]" in toml_content
    assert "[[fastmcp.servers]]" in toml_content
    assert "tools/test_llm_tools.py" in toml_content


def test_multi_provider_support_and_prompts(test_project: Path, monkeypatch) -> None:
    """Generate using a different provider and ensure files scaffold correctly."""
    monkeypatch.chdir(test_project)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "generate",
            "llm",
            "AltLLM",
            "--provider",
            "openai",
            "--model",
            "gpt-4",
            "--with-prompts",
        ],
    )

    assert result.exit_code == 0

    llm_file = test_project / "llm" / "alt_llm.py"
    provider_file = test_project / "llm" / "providers" / "openai.py"
    prompt_file = test_project / "prompts" / "alt_llm" / "v1.txt"

    assert llm_file.exists()
    assert provider_file.exists()
    assert prompt_file.exists()

    # Syntax check
    content = llm_file.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Generated LLM file has syntax error: {e}")
