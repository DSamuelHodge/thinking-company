"""Integration tests for migration commands."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from restack_gen.cli.main import cli


def test_migrate_make_generates_file(tmp_path: Path) -> None:
    """Test that migrate:make creates a migration file."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / "restack.toml").write_text("[project]\nname='test'\n")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "make", "AddUsers"],
    )

    assert result.exit_code == 0, result.output
    assert "Generated migration:" in result.output

    migrations_dir = project_dir / "migrations"
    assert migrations_dir.exists()

    # Should have exactly one migration file (excluding __init__.py)
    migration_files = [f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"]
    assert len(migration_files) == 1

    # Check content has class and methods
    content = migration_files[0].read_text()
    assert "class M" in content
    assert "def up(" in content
    assert "def down(" in content
    assert "AddUsers" in content


def test_migrate_up_applies_pending(tmp_path: Path) -> None:
    """Test that migrate:up applies pending migrations."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / "restack.toml").write_text("[project]\nname='test'\n")

    runner = CliRunner()

    # Create a migration
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "make", "TestMigration"],
    )
    assert result.exit_code == 0

    # Apply it
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "up"],
    )
    assert result.exit_code == 0, result.output
    assert "Applied 1 migration" in result.output

    # Verify history file
    history_file = project_dir / ".restack" / "migrations.json"
    assert history_file.exists()
    history = json.loads(history_file.read_text())
    assert len(history["applied"]) == 1
    assert "test_migration" in history["applied"][0]["id"]


def test_migrate_up_no_pending(tmp_path: Path) -> None:
    """Test that migrate:up handles no pending migrations."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / "restack.toml").write_text("[project]\nname='test'\n")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "up"],
    )

    assert result.exit_code == 0, result.output
    assert "No pending migrations" in result.output


def test_migrate_down_rollbacks_last(tmp_path: Path) -> None:
    """Test that migrate:down rolls back the last migration."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / "restack.toml").write_text("[project]\nname='test'\n")

    runner = CliRunner()

    # Create and apply a migration
    runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "make", "TestMigration"],
    )
    runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "up"],
    )

    # Rollback
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "down"],
    )

    assert result.exit_code == 0, result.output
    assert "Rolled back migration:" in result.output

    # Verify history is empty
    history_file = project_dir / ".restack" / "migrations.json"
    history = json.loads(history_file.read_text())
    assert len(history["applied"]) == 0


def test_migrate_down_no_migrations(tmp_path: Path) -> None:
    """Test that migrate:down handles no migrations to rollback."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / "restack.toml").write_text("[project]\nname='test'\n")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "down"],
    )

    assert result.exit_code == 0, result.output
    assert "No migrations to rollback" in result.output


def test_migrate_status_shows_migrations(tmp_path: Path) -> None:
    """Test that migrate:status shows applied and pending migrations."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / "restack.toml").write_text("[project]\nname='test'\n")

    runner = CliRunner()

    # Create two migrations
    runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "make", "Migration1"],
    )
    runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "make", "Migration2"],
    )

    # Apply first one
    runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "up"],
    )

    # Check status - should show one applied, one pending
    # (Actually both will be applied since up applies all pending)
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "status"],
    )

    assert result.exit_code == 0, result.output
    assert "Migration Status:" in result.output
    assert "migration_1" in result.output.lower() or "migration1" in result.output.lower()


def test_migrate_fails_outside_project(tmp_path: Path) -> None:
    """Test that migration commands fail outside a project."""
    runner = CliRunner()

    for cmd in ["make", "up", "down", "status"]:
        args = ["--project-path", str(tmp_path), "migrate", cmd]
        if cmd == "make":
            args.append("TestName")

        result = runner.invoke(cli, args)
        assert result.exit_code != 0
        assert "Not in a Restack project" in result.output


def test_migrate_workflow_end_to_end(tmp_path: Path) -> None:
    """Test complete migration workflow: create -> apply -> rollback."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / "restack.toml").write_text("[project]\nname='test'\n")

    runner = CliRunner()

    # 1. Create migration
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "make", "CreateSchema"],
    )
    assert result.exit_code == 0
    assert "Generated migration:" in result.output

    # 2. Check status (should be pending)
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "status"],
    )
    assert result.exit_code == 0
    assert "pending" in result.output

    # 3. Apply migration
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "up"],
    )
    assert result.exit_code == 0
    assert "Applied 1 migration" in result.output

    # 4. Check status (should be applied)
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "status"],
    )
    assert result.exit_code == 0
    assert "✅" in result.output

    # 5. Rollback
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "down"],
    )
    assert result.exit_code == 0
    assert "Rolled back migration:" in result.output

    # 6. Check status (should be pending again)
    result = runner.invoke(
        cli,
        ["--project-path", str(project_dir), "migrate", "status"],
    )
    assert result.exit_code == 0
    assert "pending" in result.output
