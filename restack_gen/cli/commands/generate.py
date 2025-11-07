"""Generate command for creating components."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from restack_gen.generators.agent import AgentGenerator
from restack_gen.generators.base import _snake_case
from restack_gen.generators.function import FunctionGenerator
from restack_gen.generators.llm import LLMGenerator
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


def _format_error_with_suggestion(error: Exception, component_type: str, name: str) -> None:
    """Format error message with actionable suggestions."""
    error_msg = str(error)

    # Common error patterns and suggestions
    if "already exists" in error_msg.lower():
        click.secho(
            f"❌ Error: {component_type.capitalize()} '{name}' already exists", fg="red", err=True
        )
        click.echo("", err=True)
        click.echo("💡 Try one of these options:", err=True)
        click.echo(
            f"   • Use --force to overwrite: restack g {component_type} {name} --force", err=True
        )
        click.echo(f"   • Choose a different name: restack g {component_type} {name}V2", err=True)
        click.echo(
            f"   • Preview with --dry-run: restack g {component_type} {name} --dry-run", err=True
        )
    elif "invalid" in error_msg.lower() and "name" in error_msg.lower():
        click.secho(f"❌ Error: Invalid {component_type} name '{name}'", fg="red", err=True)
        click.echo("", err=True)
        click.echo("💡 Component names must be PascalCase:", err=True)
        click.echo("   • Good: MyAgent, DataProcessor, UserWorkflow", err=True)
        click.echo("   • Bad: my-agent, data_processor, userworkflow", err=True)
        # Try to suggest a valid name
        suggested = "".join(word.capitalize() for word in name.replace("-", "_").split("_"))
        if suggested != name:
            click.echo(f"   • Try: restack g {component_type} {suggested}", err=True)
    elif "permission" in error_msg.lower():
        click.secho(f"❌ Error: Permission denied writing {component_type}", fg="red", err=True)
        click.echo("", err=True)
        click.echo("💡 Possible solutions:", err=True)
        click.echo("   • Check file/directory permissions", err=True)
        click.echo("   • Close any files that may be open in an editor", err=True)
        click.echo("   • Run with appropriate permissions", err=True)
    elif "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
        click.secho("❌ Error: Required directory or file not found", fg="red", err=True)
        click.echo(f"   {error}", err=True)
        click.echo("", err=True)
        click.echo("💡 This may indicate project structure issues:", err=True)
        click.echo("   • Run: restack doctor --check structure", err=True)
        click.echo("   • Fix automatically: restack doctor --fix", err=True)
    else:
        # Generic error with context
        click.secho(f"❌ Error: {error}", fg="red", err=True)
        click.echo("", err=True)
        click.echo("💡 For more information:", err=True)
        click.echo(f"   • Check logs with: restack --verbose g {component_type} {name}", err=True)
        click.echo("   • Validate project: restack doctor", err=True)
        click.echo("   • See help: restack g {component_type} --help", err=True)


@click.group(name="generate", invoke_without_command=False)
@click.pass_context
def generate(ctx: click.Context) -> None:
    """Generate components (agents, workflows, functions, llm)."""
    # Verify we're in a Restack project
    project_root = _find_project_root()
    if not project_root:
        click.secho("❌ Error: Not in a Restack project directory", fg="red", err=True)
        click.echo("", err=True)
        click.echo("💡 To fix this:", err=True)
        click.echo("   • Create a new project: restack new my-project", err=True)
        click.echo("   • Or navigate to an existing project directory", err=True)
        click.echo("   • Look for a directory containing restack.toml", err=True)
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

        click.secho(f"✨ Generated agent: {name}", fg="green")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        _format_error_with_suggestion(error, "agent", name)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate agent")
        _format_error_with_suggestion(error, "agent", name)
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

        click.secho(f"✨ Generated workflow: {name}", fg="green")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        _format_error_with_suggestion(error, "workflow", name)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate workflow")
        _format_error_with_suggestion(error, "workflow", name)
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

        click.secho(f"✨ Generated function: {name}", fg="green")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        _format_error_with_suggestion(error, "function", name)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate function")
        _format_error_with_suggestion(error, "function", name)
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

        click.secho(f"✨ Generated pipeline: {name}", fg="green")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        _format_error_with_suggestion(error, "pipeline", name)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate pipeline")
        _format_error_with_suggestion(error, "pipeline", name)
        sys.exit(1)


@generate.command(name="llm")
@click.argument("name")
@click.option(
    "--provider",
    type=click.Choice(["gemini", "openai", "anthropic"], case_sensitive=False),
    default="gemini",
    show_default=True,
    help="LLM provider",
)
@click.option("--model", help="LLM model name", default="gemini-1.5-pro", show_default=True)
@click.option("--with-prompts", is_flag=True, help="Include prompt versioning scaffold")
@click.option("--max-tokens", type=int, default=1024, show_default=True, help="Default max tokens")
@click.option(
    "--temperature", type=float, default=0.2, show_default=True, help="Default temperature (0-1)"
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--dry-run", is_flag=True, help="Preview generation without writing files")
@click.pass_context
def generate_llm(
    ctx: click.Context,
    name: str,
    provider: str,
    model: str,
    with_prompts: bool,
    max_tokens: int,
    temperature: float,
    force: bool,
    dry_run: bool,
) -> None:
    """Generate an LLM integration and FastMCP tool server."""
    project_root: Path = ctx.obj["project_root"]

    try:
        generator = LLMGenerator()

        snake = _snake_case(name)
        if dry_run:
            click.echo(f"Would generate LLM: {name}")
            click.echo(f"  LLM: {project_root}/llm/{snake}.py")
            click.echo(f"  Provider: {project_root}/llm/providers/{provider}.py")
            click.echo(f"  Tool server: {project_root}/tools/{snake}_tools.py")
            if with_prompts:
                click.echo(f"  Prompts: {project_root}/prompts/{snake}/v1.txt")
            return

        generated = generator.generate(
            name=name,
            output_dir=project_root,
            provider=provider.lower(),
            model=model,
            with_prompts=with_prompts,
            max_tokens=max_tokens,
            temperature=temperature,
            force=force,
        )

        click.secho(f"✨ Generated LLM: {name}", fg="green")
        for file_type, path in generated.items():
            click.echo(f"  📄 {file_type}: {path.relative_to(project_root)}")

    except (ValueError, FileExistsError) as error:
        _format_error_with_suggestion(error, "llm", name)
        sys.exit(1)
    except Exception as error:
        logger.exception("Failed to generate LLM")
        _format_error_with_suggestion(error, "llm", name)
        sys.exit(1)
