"""LLM integration generator for Restack CLI."""

from __future__ import annotations

from pathlib import Path

from restack_gen.generators.base import BaseGenerator, _snake_case
from restack_gen.utils.file_ops import read_file, write_file
from restack_gen.utils.validation import validate_component_name


class LLMGenerator(BaseGenerator):
    """Generator for LLM integrations and FastMCP server scaffolding."""

    def generate(
        self,
        name: str,
        output_dir: Path,
        *,
        provider: str = "gemini",
        model: str = "gemini-1.5-pro",
        with_prompts: bool = False,
        max_tokens: int = 1024,
        temperature: float = 0.2,
        force: bool = False,
    ) -> dict[str, Path]:
        """Generate LLM integration files.

        Args:
            name: LLM component name (PascalCase)
            output_dir: Project root directory
            provider: LLM provider identifier
            model: Provider model name
            with_prompts: Whether to scaffold prompt versioning
            max_tokens: Default max tokens
            temperature: Default temperature
            force: Overwrite existing files

        Returns:
            Mapping of artifact type to generated file paths
        """
        # Validate name
        issues = validate_component_name(name)
        if issues:
            raise ValueError(
                f"Invalid LLM name '{name}': {', '.join(issue.message for issue in issues)}"
            )

        snake = _snake_case(name)
        context = {
            "llm_name": name,
            "provider": provider,
            "model_name": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        generated: dict[str, Path] = {}

        # Paths
        llm_dir = output_dir / "llm"
        providers_dir = llm_dir / "providers"
        prompts_root = output_dir / "prompts" / snake
        tools_dir = output_dir / "tools"

        # LLM integration file
        llm_file = llm_dir / f"{snake}.py"
        if llm_file.exists() and not force:
            raise FileExistsError(f"LLM file already exists: {llm_file}. Use --force to overwrite.")
        llm_content = self.render_template("llm/llm_integration.py.j2", context)
        self.write_output(llm_file, llm_content, force=force)
        generated["llm"] = llm_file

        # Provider base interface
        base_file = providers_dir / "base.py"
        if not base_file.exists() or force:
            base_content = self.render_template("llm/providers/base.py.j2", context)
            self.write_output(base_file, base_content, force=True)

        # Provider implementation
        provider_template = f"llm/providers/{provider}.py.j2"
        provider_file = providers_dir / f"{provider}.py"
        provider_content = self.render_template(provider_template, context)
        self.write_output(provider_file, provider_content, force=force)
        generated["provider"] = provider_file

        # FastMCP server
        server_file = tools_dir / f"{snake}_tools.py"
        server_content = self.render_template("llm/fastmcp_server.py.j2", context)
        self.write_output(server_file, server_content, force=force)
        generated["tool_server"] = server_file

        # Prompts (optional)
        if with_prompts:
            prompt_v1 = prompts_root / "v1.txt"
            prompt_content = self.render_template("llm/prompts/prompt_v1.txt.j2", context)
            self.write_output(prompt_v1, prompt_content, force=force)
            generated["prompt_v1"] = prompt_v1

        # Update restack.toml with FastMCP server config (idempotent append)
        self._update_restack_toml(output_dir, server_file)

        return generated

    def _update_restack_toml(self, project_root: Path, server_file: Path) -> None:
        """Append FastMCP server configuration to restack.toml if missing."""
        restack_toml = project_root / "restack.toml"
        if not restack_toml.exists():
            return
        content = read_file(restack_toml)
        server_rel = server_file.relative_to(project_root).as_posix()
        marker = f'path = "{server_rel}"'
        if marker in content:
            return
        append_block = (
            "\n\n[fastmcp]\n"
            "enabled = true\n"
            "auto_discover = true\n\n"
            "[[fastmcp.servers]]\n"
            f'name = "{server_file.stem}"\n'
            f'path = "{server_rel}"\n'
            'transport = "stdio"\n'
            "autostart = true\n"
        )
        write_file(restack_toml, content + append_block, overwrite=True)
