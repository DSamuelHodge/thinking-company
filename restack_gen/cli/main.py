"""Main CLI entry point for restack-gen."""

from __future__ import annotations

from pathlib import Path

import click

from ..models.config import LoggingConfig
from ..utils.logging import configure_logging, get_logger
from .commands.doctor import doctor
from .commands.generate import generate
from .commands.new import new_command

LOGGER = get_logger("cli")


class CLIContext:
    """Shared CLI context object."""

    def __init__(self, project_path: Path) -> None:
        self.project_path = project_path


@click.group()
@click.version_option(package_name="restack-gen")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", is_flag=True, help="Suppress non-critical output")
@click.option(
    "--project-path",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Project root directory",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool, project_path: Path) -> None:
    """Restack Gen CLI for scaffolding Restack projects."""
    level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    config = LoggingConfig(level=level)
    configure_logging(config)
    LOGGER.debug("CLI initialized", extra={"project_path": str(project_path)})
    ctx.obj = CLIContext(project_path=project_path)


# Register subcommands
cli.add_command(new_command)
cli.add_command(generate)
cli.add_command(doctor)
