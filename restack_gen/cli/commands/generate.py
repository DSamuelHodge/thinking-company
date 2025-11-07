"""Generate command for creating components."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from restack_gen.generators.agent import AgentGenerator
from restack_gen.generators.base import _snake_case
from restack_gen.generators.function import FunctionGenerator
from restack_gen.generators.pipeline import PipelineGenerator
from restack_gen.generators.workflow import WorkflowGenerator
from restack_gen.utils.logging import get_logger

logger = get_logger(__name__)


def _find_project_root() -> Path | None:
    """
    Find the project root by looking for restack.toml.

    Returns:
        Path to project root or None if not found
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / "restack.toml").exists():
            return current
        current = current.parent
    return None


@click.group(name="generate", invoke_without_command=False)
@click.pass_context
def generate(ctx: click.Context) -> None:
    """Generate components (agents, workflows, functions)."""
    # Verify we're in a Restack project
    project_root = _find_project_root()
    if not project_root:
        click.echo("❌ Error: Not in a Restack project directory.", err=True)
        click.echo("   Run this command from a directory containing restack.toml", err=True)
        sys.exit(1)

    # Store project root in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = project_root


@generate.command(name="agent")
@click.argument("name")
@click.option(
    "--description",
    "-d",
    help="Description of the agent",
)
@click.option(
    "--no-tests",
    is_flag=True,
    help="Skip generating test files",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview generation without writing files",
)
@click.pass_context
def generate_agent(
    ctx: click.Context,
    name: str,
    description: str | None,
    no_tests: bool,
    force: bool,
    dry_run: bool,
) -> None:
    """Generate a new agent component."""
    project_root: Path = ctx.obj["project_root"]

    try:
        generator = AgentGenerator()

        if dry_run:
            click.echo(f"Would generate agent: {name}")
            click.echo(f"  Location: {project_root}/agents/{_snake_case(name)}.py")
            if not no_tests:
                click.echo(f"  Test: {project_root}/tests/test_{_snake_case(name)}.py")
            return

        generated = generator.generate(
            name=name,
            output_dir=project_root,
            description=description,
            with_tests=not no_tests,
            force=force,
        )

        click.echo(f"✨ Generated agent: {name}")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate agent")
        click.echo(f"❌ Unexpected error: {error}", err=True)
        sys.exit(1)


@generate.command(name="workflow")
@click.argument("name")
@click.option(
    "--description",
    "-d",
    help="Description of the workflow",
)
@click.option(
    "--with-functions",
    is_flag=True,
    help="Include function call examples",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    help="Timeout in seconds",
)
@click.option(
    "--no-tests",
    is_flag=True,
    help="Skip generating test files",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview generation without writing files",
)
@click.pass_context
def generate_workflow(
    ctx: click.Context,
    name: str,
    description: str | None,
    with_functions: bool,
    timeout: int | None,
    no_tests: bool,
    force: bool,
    dry_run: bool,
) -> None:
    """Generate a new workflow component."""
    project_root: Path = ctx.obj["project_root"]

    try:
        generator = WorkflowGenerator()

        if dry_run:
            click.echo(f"Would generate workflow: {name}")
            click.echo(f"  Location: {project_root}/workflows/{_snake_case(name)}.py")
            if not no_tests:
                click.echo(f"  Test: {project_root}/tests/test_{_snake_case(name)}.py")
            return

        generated = generator.generate(
            name=name,
            output_dir=project_root,
            description=description,
            with_functions=with_functions,
            timeout=timeout,
            with_tests=not no_tests,
            force=force,
        )

        click.echo(f"✨ Generated workflow: {name}")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate workflow")
        click.echo(f"❌ Unexpected error: {error}", err=True)
        sys.exit(1)


@generate.command(name="function")
@click.argument("name")
@click.option(
    "--description",
    "-d",
    help="Description of the function",
)
@click.option(
    "--pure",
    is_flag=True,
    help="Generate as pure function (not a class)",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    help="Timeout in seconds",
)
@click.option(
    "--no-tests",
    is_flag=True,
    help="Skip generating test files",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview generation without writing files",
)
@click.pass_context
def generate_function(
    ctx: click.Context,
    name: str,
    description: str | None,
    pure: bool,
    timeout: int | None,
    no_tests: bool,
    force: bool,
    dry_run: bool,
) -> None:
    """Generate a new function component."""
    project_root: Path = ctx.obj["project_root"]

    try:
        generator = FunctionGenerator()

        if dry_run:
            click.echo(f"Would generate function: {name}")
            click.echo(f"  Location: {project_root}/functions/{_snake_case(name)}.py")
            if not no_tests:
                click.echo(f"  Test: {project_root}/tests/test_{_snake_case(name)}.py")
            return

        generated = generator.generate(
            name=name,
            output_dir=project_root,
            description=description,
            pure=pure,
            timeout=timeout,
            with_tests=not no_tests,
            force=force,
        )

        click.echo(f"✨ Generated function: {name}")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(1)


@generate.command(name="pipeline")
@click.argument("name")
@click.option(
    "--description",
    "-d",
    help="Description of the pipeline",
)
@click.option(
    "--operators",
    help="Operator expression (supports ->, ->?, || and unicode equivalents)",
)
@click.option(
    "--error-strategy",
    type=click.Choice(["halt", "continue", "retry"], case_sensitive=False),
    default="halt",
    show_default=True,
    help="Error handling strategy",
)
@click.option(
    "--no-tests",
    is_flag=True,
    help="Skip generating test files",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview generation without writing files",
)
@click.pass_context
def generate_pipeline(
    ctx: click.Context,
    name: str,
    description: str | None,
    operators: str | None,
    error_strategy: str,
    no_tests: bool,
    force: bool,
    dry_run: bool,
) -> None:
    """Generate a new pipeline (workflow with operator grammar)."""
    project_root: Path = ctx.obj["project_root"]

    try:
        generator = PipelineGenerator()

        if dry_run:
            click.echo(f"Would generate pipeline: {name}")
            click.echo(f"  Location: {project_root}/workflows/{_snake_case(name)}.py")
            if operators:
                click.echo(f"  Operators: {operators}")
            if not no_tests:
                click.echo(f"  Test: {project_root}/tests/test_{_snake_case(name)}.py")
            return

        generated = generator.generate(
            name=name,
            output_dir=project_root,
            description=description,
            operators=operators,
            error_strategy=error_strategy,
            with_tests=not no_tests,
            force=force,
        )

        click.echo(f"✨ Generated pipeline: {name}")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate pipeline")
        click.echo(f"❌ Unexpected error: {error}", err=True)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate function")
        click.echo(f"❌ Unexpected error: {error}", err=True)
        sys.exit(1)
