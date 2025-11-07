"""Project scaffolding generator."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..utils.file_ops import ensure_directory
from ..utils.validation import ValidationIssue, validate_project_name
from .base import BaseGenerator


class ProjectGenerationError(Exception):
    """Base exception for project generation issues."""


class InvalidProjectNameError(ProjectGenerationError):
    """Raised when the provided project name fails validation."""


class TargetDirectoryExistsError(ProjectGenerationError):
    """Raised when the target project directory already exists."""


@dataclass
class ProjectGenerationResult:
    """Result metadata from project generation."""

    project_path: Path
    files_created: list[Path]
    directories_created: list[Path]
    git_initialized: bool


class ProjectGenerator(BaseGenerator):
    """Generate a new Restack project from templates."""

    def __init__(
        self,
        project_name: str,
        output_dir: Path,
        python_version: str,
        description: str | None = None,
        template: str = "standard",
        git_init: bool = True,
    ) -> None:
        super().__init__()
        self.project_name = project_name
        self.output_dir = output_dir
        self.python_version = python_version
        self.description = description or ""
        self.template = template
        self.git_init = git_init
        self.logger.info(
            "Initialized ProjectGenerator",
            extra={
                "project_name": project_name,
                "output_dir": str(output_dir),
                "python_version": python_version,
                "template": template,
                "git_init": git_init,
            },
        )

    # Public API ---------------------------------------------------------
    def generate(self) -> ProjectGenerationResult:
        """Generate project scaffolding on disk."""
        self._validate_name()
        project_path = self.output_dir / self.project_name
        self._ensure_target_available(project_path)

        directories_created = self._create_directory_structure(project_path)
        files_created = self._render_project_files(project_path)

        git_initialized = False
        if self.git_init:
            git_initialized = self._initialize_git(project_path)

        self.logger.info(
            "Generated project",
            extra={
                "project_path": str(project_path),
                "files_created": len(files_created),
                "directories_created": len(directories_created),
                "git_initialized": git_initialized,
            },
        )
        return ProjectGenerationResult(
            project_path=project_path,
            files_created=files_created,
            directories_created=directories_created,
            git_initialized=git_initialized,
        )

    # Internal helpers ---------------------------------------------------
    def _validate_name(self) -> None:
        issues: list[ValidationIssue] = validate_project_name(self.project_name)
        if issues:
            messages = ", ".join(issue.message for issue in issues)
            self.logger.error("Project name validation failed", extra={"messages": messages})
            raise InvalidProjectNameError(messages)

    def _ensure_target_available(self, project_path: Path) -> None:
        if project_path.exists():
            if any(project_path.iterdir()):
                raise TargetDirectoryExistsError(
                    f"Target directory {project_path} already exists and is not empty"
                )
            raise TargetDirectoryExistsError(f"Target directory {project_path} already exists")
        ensure_directory(project_path)

    def _create_directory_structure(self, project_path: Path) -> list[Path]:
        directories = [
            project_path / "agents",
            project_path / "workflows",
            project_path / "functions",
            project_path / "tests",
            project_path / "tests" / "agents",
            project_path / "tests" / "workflows",
            project_path / "tests" / "functions",
            project_path / ".github" / "workflows",
        ]
        created: list[Path] = []
        for directory in directories:
            ensure_directory(directory)
            created.append(directory)
        return created

    def _render_project_files(self, project_path: Path) -> list[Path]:
        context = self._build_context(project_path)
        template_map: dict[str, Path] = {
            "project/restack.toml.j2": project_path / "restack.toml",
            "project/pyproject.toml.j2": project_path / "pyproject.toml",
            "project/README.md.j2": project_path / "README.md",
            "project/requirements.txt.j2": project_path / "requirements.txt",
            "project/.gitignore.j2": project_path / ".gitignore",
            "project/.github/workflows/ci.yml.j2": project_path
            / ".github"
            / "workflows"
            / "ci.yml",
            "project/structure/agents/__init__.py.j2": project_path / "agents" / "__init__.py",
            "project/structure/workflows/__init__.py.j2": project_path
            / "workflows"
            / "__init__.py",
            "project/structure/functions/__init__.py.j2": project_path
            / "functions"
            / "__init__.py",
            "project/structure/tests/__init__.py.j2": project_path / "tests" / "__init__.py",
            "project/structure/tests/test_sample.py.j2": project_path / "tests" / "test_sample.py",
        }

        created: list[Path] = []
        for template_name, output_path in template_map.items():
            content = self.render_template(template_name, context)
            self.write_output(output_path, content, overwrite=True)
            created.append(output_path)
        return created

    def _build_context(self, project_path: Path) -> dict[str, str]:
        package_name = self.project_name.replace("-", "_")
        title = self.project_name.replace("-", " ").title()
        return {
            "project_name": self.project_name,
            "project_description": self.description,
            "python_version": self.python_version,
            "package_name": package_name,
            "project_title": title,
            "project_root": str(project_path),
        }

    def _initialize_git(self, project_path: Path) -> bool:
        try:
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            return True
        except FileNotFoundError:
            self.logger.warning("Git executable not found; skipping repository initialization")
            return False
        except subprocess.CalledProcessError as exc:
            self.logger.warning(
                "Git initialization failed",
                extra={
                    "returncode": exc.returncode,
                    "stderr": (exc.stderr.decode(errors="ignore") if exc.stderr else ""),
                },
            )
            return False
