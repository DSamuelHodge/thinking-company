"""Base generator classes and template utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..utils.file_ops import write_file
from ..utils.logging import get_logger

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _snake_case(value: str) -> str:
    import re

    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.replace("-", "_").lower()


def _pascal_case(value: str) -> str:
    return "".join(word.capitalize() for word in value.replace("-", "_").split("_"))


def _kebab_case(value: str) -> str:
    return _snake_case(value).replace("_", "-")


class BaseGenerator:
    """Base class for all code generators."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self.logger = get_logger(self.__class__.__name__)
        template_path = templates_dir or TEMPLATE_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=False,
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )
        self.env.filters.update(
            snake_case=_snake_case,
            pascal_case=_pascal_case,
            kebab_case=_kebab_case,
        )

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)

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
