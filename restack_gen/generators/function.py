"""Function generator for Restack CLI."""

from __future__ import annotations

from pathlib import Path

from restack_gen.generators.base import BaseGenerator, _snake_case
from restack_gen.utils.validation import validate_component_name


class FunctionGenerator(BaseGenerator):
    """Generator for Restack function components."""

    def generate(
        self,
        name: str,
        output_dir: Path,
        *,
        description: str | None = None,
        pure: bool = False,
        timeout: int | None = None,
        with_tests: bool = True,
        force: bool = False,
    ) -> dict[str, Path]:
        """
        Generate a function component.

        Args:
            name: Function name (PascalCase)
            output_dir: Output directory for the function
            description: Optional description for the function
            pure: Whether to generate a pure function (not a class)
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
                f"Invalid function name '{name}': {', '.join(issue.message for issue in issues)}"
            )

        # Prepare context
        context = {
            "name": name,
            "description": description,
            "pure": pure,
            "timeout": timeout,
            "package_name": self._get_package_name(output_dir),
        }

        # Generate function file
        function_dir = output_dir / "functions"
        function_file = function_dir / f"{_snake_case(name)}.py"

        generated_files: dict[str, Path] = {}

        # Check if file exists
        if function_file.exists() and not force:
            raise FileExistsError(
                f"Function file already exists: {function_file}. Use --force to overwrite."
            )

        # Generate function
        function_content = self.render_template("functions/function.py.j2", context)
        self.write_output(function_file, function_content, force=force)
        generated_files["function"] = function_file

        # Generate tests if requested
        if with_tests:
            test_dir = output_dir / "tests"
            test_file = test_dir / f"test_{_snake_case(name)}.py"

            if test_file.exists() and not force:
                raise FileExistsError(
                    f"Test file already exists: {test_file}. Use --force to overwrite."
                )

            test_content = self.render_template("functions/test_function.py.j2", context)
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
