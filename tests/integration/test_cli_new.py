from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from restack_gen.cli.main import cli


def _invoke_new(runner: CliRunner, tmp: Path, *args: str):
    # Always pass project-path to avoid cwd side effects
    return runner.invoke(cli, ["--project-path", str(tmp), "new", *args])


def test_new_creates_project_structure(cli_runner: CliRunner, temp_dir: Path) -> None:
    project_name = "my-project"
    result = _invoke_new(cli_runner, temp_dir, project_name)

    assert result.exit_code == 0, result.output

    proj = temp_dir / project_name
    # Directories
    for d in ["agents", "workflows", "functions", "tests", ".github", ".github/workflows"]:
        assert (proj / d).exists() and (proj / d).is_dir(), f"Missing directory: {d}"

    # Files
    expected_files = [
        "restack.toml",
        "pyproject.toml",
        "README.md",
        "requirements.txt",
        ".gitignore",
        ".github/workflows/ci.yml",
        "tests/test_sample.py",
        "agents/__init__.py",
        "workflows/__init__.py",
        "functions/__init__.py",
        "tests/__init__.py",
    ]
    for rel in expected_files:
        assert (proj / rel).exists(), f"Missing file: {rel}"


@pytest.mark.parametrize(
    "bad_name",
    [
        "My Project",  # spaces and capitals
        "bad_name",  # underscore
        "-start",  # leading hyphen
        "end-",  # trailing hyphen
    ],
)
def test_new_invalid_name_fails(cli_runner: CliRunner, temp_dir: Path, bad_name: str) -> None:
    result = _invoke_new(cli_runner, temp_dir, bad_name)
    assert result.exit_code != 0
    assert "Error:" in result.output


def test_new_no_git_flag(cli_runner: CliRunner, temp_dir: Path) -> None:
    project_name = "no-git-proj"
    result = _invoke_new(cli_runner, temp_dir, "--no-git", project_name)
    assert result.exit_code == 0, result.output
    proj = temp_dir / project_name
    assert not (proj / ".git").exists(), "--no-git should not initialize a git repository"


def test_new_python_version_in_files(cli_runner: CliRunner, temp_dir: Path) -> None:
    project_name = "py311-proj"
    py_ver = "3.12"
    result = _invoke_new(cli_runner, temp_dir, "--python-version", py_ver, project_name)
    assert result.exit_code == 0, result.output
    proj = temp_dir / project_name
    restack_toml = (proj / "restack.toml").read_text(encoding="utf-8")
    pyproject = (proj / "pyproject.toml").read_text(encoding="utf-8")
    assert f'python_version = "{py_ver}"' in restack_toml
    # Allow an additional upper-bound restriction in the template (e.g., <3.14)
    assert f">={py_ver}" in pyproject
