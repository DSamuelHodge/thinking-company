"""`restack new` command implementation."""

from __future__ import annotations

from pathlib import Path

import click

from ...generators.project import ProjectGenerationError, ProjectGenerator
from ...utils.logging import get_logger

LOGGER = get_logger("cli.new")


@click.command("new")
@click.argument("project_name", type=str)
@click.option(
    "--python-version",
    type=str,
    default="3.11",
    show_default=True,
    help="Python version requirement",
)
@click.option(
    "--template", type=str, default="standard", show_default=True, help="Project template"
)
@click.option("--description", type=str, default=None, help="Project description")
@click.option("--no-git", is_flag=True, help="Do not initialize a git repository")
@click.pass_obj
def new_command(
    ctx,
    project_name: str,
    python_version: str,
    template: str,
    description: str | None,
    no_git: bool,
) -> None:
    """Create a new Restack project with complete scaffolding."""
    output_dir = ctx.project_path

    try:
        generator = ProjectGenerator(
            project_name=project_name,
            output_dir=output_dir,
            python_version=python_version,
            description=description,
            template=template,
            git_init=not no_git,
        )
        result = generator.generate()
    except ProjectGenerationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc

    project_dir = result.project_path
    rel = project_dir.name if project_dir.parent == Path.cwd() else str(project_dir)

    click.echo(
        "\n".join(
            [
                f"✅ Created project '{project_name}'",
                "📁 Project structure initialized",
                f"🐍 Python {python_version} environment configured",
                "📋 Configuration files generated",
                "🧪 Test structure created",
                "",
                "Next steps:",
                f"  cd {rel}",
                "  pip install -r requirements.txt",
                "  restack doctor",
            ]
        )
    )
