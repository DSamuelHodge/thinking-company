"""Workflow generator for Restack CLI."""

from __future__ import annotations

from pathlib import Path

from restack_gen.generators.base import BaseGenerator, _snake_case
from restack_gen.utils.validation import validate_component_name


class WorkflowGenerator(BaseGenerator):
    """Generator for Restack workflow components."""

    def generate(
        self,
        name: str,
        output_dir: Path,
        *,
        description: str | None = None,
        with_functions: bool = False,
        timeout: int | None = None,
        with_tests: bool = True,
        force: bool = False,
    ) -> dict[str, Path]:
        """
        Generate a workflow component.

        Args:
            name: Workflow name (PascalCase)
            output_dir: Output directory for the workflow
            description: Optional description for the workflow
            with_functions: Whether to include function call examples
            timeout: Optional timeout in seconds
            with_tests: Whether to generate test files
            force: Whether to overwrite existing files

        Returns:
            Dictionary mapping file type to generated file paths

        Raises:
            ValueError: If name is invalid
            FileExistsError: If files exist and force is False
        """
        # Validate name
        issues = validate_component_name(name)
        if issues:
            raise ValueError(
                f"Invalid workflow name '{name}': {', '.join(issue.message for issue in issues)}"
            )

        # Prepare context
        context = {
            "name": name,
            "description": description,
            "with_functions": with_functions,
            "timeout": timeout,
            "package_name": self._get_package_name(output_dir),
        }

        # Generate workflow file
        workflow_dir = output_dir / "workflows"
        workflow_file = workflow_dir / f"{_snake_case(name)}.py"

        generated_files: dict[str, Path] = {}

        # Check if file exists
        if workflow_file.exists() and not force:
            raise FileExistsError(
                f"Workflow file already exists: {workflow_file}. Use --force to overwrite."
            )

        # Generate workflow
        workflow_content = self.render_template("workflows/workflow.py.j2", context)
        self.write_output(workflow_file, workflow_content, force=force)
        generated_files["workflow"] = workflow_file

        # Generate tests if requested
        if with_tests:
            test_dir = output_dir / "tests"
            test_file = test_dir / f"test_{_snake_case(name)}.py"

            if test_file.exists() and not force:
                raise FileExistsError(
                    f"Test file already exists: {test_file}. Use --force to overwrite."
                )

            test_content = self.render_template("workflows/test_workflow.py.j2", context)
            self.write_output(test_file, test_content, force=force)
            generated_files["test"] = test_file

        return generated_files

    def _get_package_name(self, output_dir: Path) -> str:
        """
        Determine the package name from the output directory.

        Args:
            output_dir: Output directory path

        Returns:
            Package name as string
        """
        # Try to find the project root with pyproject.toml
        current = output_dir.resolve()
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                # Use the directory name as package name
                return current.name.replace("-", "_")
            current = current.parent

        # Fallback to directory name
        return output_dir.name.replace("-", "_")
