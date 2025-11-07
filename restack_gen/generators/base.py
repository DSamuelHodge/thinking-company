"""Base generator classes and template utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from jinja2 import (
    BytecodeCache,
    Environment,
    FileSystemBytecodeCache,
    FileSystemLoader,
    StrictUndefined,
)

from ..utils.file_ops import write_file
from ..utils.logging import get_logger

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_VERSION = "1.0.0"  # Increment when templates change incompatibly

# Template caching configuration
_CACHE_ENABLED = os.getenv("RESTACK_CACHE_TEMPLATES", "1") == "1"
_CACHE_DIR = Path.home() / ".cache" / "restack-gen" / "templates"


def _snake_case(value: str) -> str:
    import re

    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.replace("-", "_").lower()


def _pascal_case(value: str) -> str:
    return "".join(word.capitalize() for word in value.replace("-", "_").split("_"))


def _kebab_case(value: str) -> str:
    return _snake_case(value).replace("_", "-")


def _get_bytecode_cache() -> BytecodeCache | None:
    """Get configured bytecode cache for templates."""
    if not _CACHE_ENABLED:
        return None
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return FileSystemBytecodeCache(str(_CACHE_DIR))
    except Exception:  # pragma: no cover - defensive
        # Silently fall back to no caching if cache directory can't be created
        return None


class BaseGenerator:
    """Base class for all code generators with template caching support."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self.logger = get_logger(self.__class__.__name__)
        template_path = templates_dir or TEMPLATE_DIR

        bytecode_cache = _get_bytecode_cache()

        self.env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=False,
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            bytecode_cache=bytecode_cache,
        )
        self.env.filters.update(
            snake_case=_snake_case,
            pascal_case=_pascal_case,
            kebab_case=_kebab_case,
        )
        self.template_version = TEMPLATE_VERSION

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with version metadata included in context."""
        # Include template version for forward compatibility checks
        context_with_meta = {
            **context,
            "_template_version": self.template_version,
        }
        template = self.env.get_template(template_name)
        return template.render(**context_with_meta)

    def write_output(
        self, path: Path, content: str, *, overwrite: bool = False, force: bool = False
    ) -> None:
        """
        Write content to a file.

        Args:
            path: Path to write to
            content: Content to write
            overwrite: Whether to overwrite existing files (legacy parameter)
            force: Whether to overwrite existing files (new parameter, takes precedence)
        """
        write_file(path, content, overwrite=force or overwrite)
