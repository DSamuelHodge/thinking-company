"""Integration tests for the `restack run:server` command."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from restack_gen.cli.main import cli


def test_server_health_check(tmp_path: Path) -> None:
    runner = CliRunner()
    proj = tmp_path / "proj"
    proj.mkdir()

    # Use a high, likely-free ephemeral-ish port
    port = 8765
    result = runner.invoke(
        cli,
        ["--project-path", str(proj), "run:server", "--port", str(port), "--health-check"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    assert "Server healthy" in result.output
