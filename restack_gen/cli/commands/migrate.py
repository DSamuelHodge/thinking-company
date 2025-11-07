"""Migration commands for managing project schema and structure changes."""

from __future__ import annotations

import click

from ...migrations import MigrationManager
from ...utils.logging import get_logger

LOGGER = get_logger("migrate")


@click.group(name="migrate")
@click.pass_obj
def migrate_group(ctx) -> None:
    """Manage project migrations."""
    pass


@migrate_group.command(name="make")
@click.argument("name")
@click.pass_obj
def make(ctx, name: str) -> None:
    """Generate a new migration file with the given name.

    Example: restack migrate:make AddUserModel
    """
    project_dir = ctx.project_path

    if not (project_dir / "restack.toml").exists():
        click.secho("❌ Not in a Restack project directory", fg="red", err=True)
        raise SystemExit(1)

    try:
        manager = MigrationManager(project_dir)
        file_path = manager.generate(name)
        rel_path = file_path.relative_to(project_dir)
        click.secho(f"✅ Generated migration: {rel_path}", fg="green")
        click.echo("   Edit the file to implement up() and down() methods")
    except Exception as exc:
        LOGGER.error("Failed to generate migration", exc_info=exc)
        click.secho(f"❌ Error: {exc}", fg="red", err=True)
        raise SystemExit(1) from exc


@migrate_group.command(name="up")
@click.option("--verbose", is_flag=True, help="Show detailed migration information")
@click.pass_obj
def up(ctx, verbose: bool) -> None:
    """Apply all pending migrations.

    Example: restack migrate:up
    """
    project_dir = ctx.project_path

    if not (project_dir / "restack.toml").exists():
        click.secho("❌ Not in a Restack project directory", fg="red", err=True)
        raise SystemExit(1)

    try:
        manager = MigrationManager(project_dir)
        applied_ids = manager.apply_pending()

        if not applied_ids:
            click.echo("ℹ️  No pending migrations")
            return

        click.secho(f"✅ Applied {len(applied_ids)} migration(s):", fg="green")
        for mig_id in applied_ids:
            prefix = "   - " if verbose else "   "
            click.echo(f"{prefix}{mig_id}")
    except Exception as exc:
        LOGGER.error("Failed to apply migrations", exc_info=exc)
        click.secho(f"❌ Error: {exc}", fg="red", err=True)
        raise SystemExit(1) from exc


@migrate_group.command(name="down")
@click.option("--verbose", is_flag=True, help="Show detailed migration information")
@click.pass_obj
def down(ctx, verbose: bool) -> None:
    """Rollback the last applied migration.

    Example: restack migrate:down
    """
    project_dir = ctx.project_path

    if not (project_dir / "restack.toml").exists():
        click.secho("❌ Not in a Restack project directory", fg="red", err=True)
        raise SystemExit(1)

    try:
        manager = MigrationManager(project_dir)
        mig_id = manager.rollback_last()

        if not mig_id:
            click.echo("ℹ️  No migrations to rollback")
            return

        click.secho(f"✅ Rolled back migration: {mig_id}", fg="green")
    except Exception as exc:
        LOGGER.error("Failed to rollback migration", exc_info=exc)
        click.secho(f"❌ Error: {exc}", fg="red", err=True)
        raise SystemExit(1) from exc


@migrate_group.command(name="status")
@click.pass_obj
def status(ctx) -> None:
    """Show migration status (applied and pending).

    Example: restack migrate:status
    """
    project_dir = ctx.project_path

    if not (project_dir / "restack.toml").exists():
        click.secho("❌ Not in a Restack project directory", fg="red", err=True)
        raise SystemExit(1)

    try:
        manager = MigrationManager(project_dir)
        all_migrations = manager.discover()
        applied_ids = set(manager.applied_ids())

        if not all_migrations:
            click.echo("ℹ️  No migrations found")
            return

        click.echo("Migration Status:")
        click.echo()

        for mig_id, _path in all_migrations:
            if mig_id in applied_ids:
                click.secho(f"  ✅ {mig_id}", fg="green")
            else:
                click.secho(f"  ⏳ {mig_id} (pending)", fg="yellow")
    except Exception as exc:
        LOGGER.error("Failed to get migration status", exc_info=exc)
        click.secho(f"❌ Error: {exc}", fg="red", err=True)
        raise SystemExit(1) from exc
