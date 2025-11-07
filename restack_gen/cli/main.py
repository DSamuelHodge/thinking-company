"""Main CLI entry point for restack-gen."""

from __future__ import annotations

from pathlib import Path

import click

from ..models.config import LoggingConfig
from ..utils.logging import configure_logging, get_logger
from .commands.doctor import doctor
from .commands.generate import generate
from .commands.migrate import migrate_group
from .commands.new import new_command
from .commands.server import server as server_command

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
cli.add_command(migrate_group)
cli.add_command(server_command, name="run:server")


# Shell completion support
@cli.command(name="completion")
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False))
def completion_command(shell: str) -> None:
    """Generate shell completion script.

    Usage:
        bash:  restack completion bash > ~/.bash_completion.d/restack
        zsh:   restack completion zsh > ~/.zsh/completion/_restack
        fish:  restack completion fish > ~/.config/fish/completions/restack.fish
    """
    shell_lower = shell.lower()

    if shell_lower == "bash":
        script = """
# Bash completion for restack
_restack_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   _RESTACK_COMPLETE=complete $1 ) )
    return 0
}

complete -F _restack_completion -o default restack
"""
    elif shell_lower == "zsh":
        script = """
#compdef restack

_restack_completion() {
    eval $(env COMMANDLINE="${words[1,$CURRENT]}" _RESTACK_COMPLETE=complete-zsh restack)
}

compdef _restack_completion restack
"""
    elif shell_lower == "fish":
        script = """
# Fish completion for restack
function __restack_complete
    set -lx _RESTACK_COMPLETE complete-fish
    set -lx COMP_WORDS (commandline -opc) (commandline -ct)
    restack
end

complete -f -c restack -a "(__restack_complete)"
"""
    else:  # pragma: no cover - validated by Click
        click.secho(f"Shell '{shell}' not supported", fg="red", err=True)
        raise SystemExit(1)

    click.echo(script)
