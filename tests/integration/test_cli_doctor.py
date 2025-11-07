"""Integration tests for the `restack doctor` command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from restack_gen.cli.main import cli


@pytest.fixture
def minimal_project(tmp_path: Path) -> Path:
    """Create a minimal Restack project for doctor checks."""
    proj = tmp_path / "demo-project"
    proj.mkdir()
    (proj / "restack.toml").write_text(
        """[project]\nname = 'demo-project'\nversion = '0.1.0'\npython_version = '3.11'\n[structure]\nagents_dir='agents'\nworkflows_dir='workflows'\nfunctions_dir='functions'\n""",
        encoding="utf-8",
    )
    # Minimal requirements file to satisfy dependency check (include restack-ai)
    (proj / "requirements.txt").write_text(
        "click\njinja2\npydantic\nrestack-ai>=0.1.0\n", encoding="utf-8"
    )
    for d in ["agents", "workflows", "functions", "tests"]:
        (proj / d).mkdir()
    # Valid python file
    (proj / "agents" / "ok_agent.py").write_text("class OK:\n    pass\n", encoding="utf-8")
    return proj


def test_doctor_passes_on_valid_project(minimal_project: Path, monkeypatch) -> None:
    monkeypatch.chdir(minimal_project)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0, result.output
    assert "All checks passed" in result.output


def test_doctor_fails_outside_project(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code != 0
    assert "Not in a Restack project" in result.output


def test_doctor_detects_missing_structure(monkeypatch, tmp_path: Path) -> None:
    proj = tmp_path / "broken-project"
    proj.mkdir()
    (proj / "restack.toml").write_text(
        "[project]\nname='broken-project'\nversion='0.1.0'\npython_version='3.11'\n",
        encoding="utf-8",
    )
    (proj / "requirements.txt").write_text("restack-ai\n", encoding="utf-8")
    monkeypatch.chdir(proj)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--check", "structure"])
    assert result.exit_code != 0
    assert "Missing directory" in result.output


def test_doctor_fix_creates_missing_dirs(monkeypatch, tmp_path: Path) -> None:
    proj = tmp_path / "fix-project"
    proj.mkdir()
    (proj / "restack.toml").write_text(
        "[project]\nname='fix-project'\nversion='0.1.0'\npython_version='3.11'\n",
        encoding="utf-8",
    )
    (proj / "requirements.txt").write_text("restack-ai>=0.1.0\n", encoding="utf-8")
    # Run doctor with --fix to create missing directories
    monkeypatch.chdir(proj)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--check", "structure", "--fix"])
    assert result.exit_code == 0, result.output
    for d in ["agents", "workflows", "functions", "tests"]:
        assert (proj / d).exists(), f"Directory {d} was not created"


def test_doctor_dependency_version_below_min(monkeypatch, tmp_path: Path) -> None:
    proj = tmp_path / "ver-project"
    proj.mkdir()
    (proj / "restack.toml").write_text(
        "[project]\nname='ver-project'\nversion='0.1.0'\npython_version='3.11'\n",
        encoding="utf-8",
    )
    # Version intentionally below minimum (0.1.0) to trigger failure
    (proj / "requirements.txt").write_text("restack-ai==0.0.9\n", encoding="utf-8")
    for d in ["agents", "workflows", "functions", "tests"]:
        (proj / d).mkdir()
    monkeypatch.chdir(proj)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--check", "dependencies"])
    assert result.exit_code != 0, result.output
    assert "below minimum" in result.output


def test_doctor_detects_syntax_error(monkeypatch, minimal_project: Path) -> None:
    bad_file = minimal_project / "functions" / "bad.py"
    bad_file.write_text("def broken(:\n    pass\n", encoding="utf-8")
    monkeypatch.chdir(minimal_project)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--check", "syntax"])
    assert result.exit_code != 0
    assert "bad.py" in result.output


def test_doctor_json_output(minimal_project: Path, monkeypatch) -> None:
    monkeypatch.chdir(minimal_project)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--json"])
    assert result.exit_code == 0, result.output
    # Basic JSON structure expectations
    assert result.output.strip().startswith("{")
    assert '"checks"' in result.output
    assert '"summary"' in result.output


def test_doctor_verbose_human(minimal_project: Path, monkeypatch) -> None:
    monkeypatch.chdir(minimal_project)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--verbose"])
    assert result.exit_code == 0, result.output
    assert "Checked" in result.output  # python files count line
    assert "meets minimum version" in result.output


def test_doctor_verbose_json(minimal_project: Path, monkeypatch) -> None:
    monkeypatch.chdir(minimal_project)
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--json", "--verbose"])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert "meta" in parsed
    assert parsed["meta"]["min_restack_ai_version"] == "0.1.0"
    assert "project_root" in parsed["meta"]
