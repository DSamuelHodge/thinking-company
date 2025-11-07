"""Unit tests for ProjectGenerator error paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from restack_gen.generators.project import (
    InvalidProjectNameError,
    ProjectGenerator,
    TargetDirectoryExistsError,
)


class TestProjectGeneratorErrors:
    """Tests for ProjectGenerator error conditions."""

    def test_invalid_name_with_spaces_raises(self, temp_dir: Path) -> None:
        """Test project name with spaces raises InvalidProjectNameError."""
        generator = ProjectGenerator(
            project_name="my project",
            output_dir=temp_dir,
            python_version="3.11",
        )
        with pytest.raises(InvalidProjectNameError) as exc_info:
            generator.generate()
        assert "kebab-case" in str(exc_info.value)

    def test_invalid_name_with_underscores_raises(self, temp_dir: Path) -> None:
        """Test project name with underscores raises InvalidProjectNameError."""
        generator = ProjectGenerator(
            project_name="my_project",
            output_dir=temp_dir,
            python_version="3.11",
        )
        with pytest.raises(InvalidProjectNameError):
            generator.generate()

    def test_invalid_name_leading_hyphen_raises(self, temp_dir: Path) -> None:
        """Test project name starting with hyphen raises error."""
        generator = ProjectGenerator(
            project_name="-project",
            output_dir=temp_dir,
            python_version="3.11",
        )
        with pytest.raises(InvalidProjectNameError):
            generator.generate()

    def test_invalid_name_trailing_hyphen_raises(self, temp_dir: Path) -> None:
        """Test project name ending with hyphen raises error."""
        generator = ProjectGenerator(
            project_name="project-",
            output_dir=temp_dir,
            python_version="3.11",
        )
        with pytest.raises(InvalidProjectNameError):
            generator.generate()

    def test_invalid_name_consecutive_hyphens_raises(self, temp_dir: Path) -> None:
        """Test project name with consecutive hyphens raises error."""
        generator = ProjectGenerator(
            project_name="my--project",
            output_dir=temp_dir,
            python_version="3.11",
        )
        with pytest.raises(InvalidProjectNameError):
            generator.generate()

    def test_existing_empty_directory_raises(self, temp_dir: Path) -> None:
        """Test existing empty directory raises TargetDirectoryExistsError."""
        existing = temp_dir / "existing-project"
        existing.mkdir()

        generator = ProjectGenerator(
            project_name="existing-project",
            output_dir=temp_dir,
            python_version="3.11",
        )
        with pytest.raises(TargetDirectoryExistsError) as exc_info:
            generator.generate()
        assert "already exists" in str(exc_info.value)

    def test_existing_nonempty_directory_raises(self, temp_dir: Path) -> None:
        """Test existing non-empty directory raises TargetDirectoryExistsError."""
        existing = temp_dir / "nonempty-project"
        existing.mkdir()
        (existing / "file.txt").touch()

        generator = ProjectGenerator(
            project_name="nonempty-project",
            output_dir=temp_dir,
            python_version="3.11",
        )
        with pytest.raises(TargetDirectoryExistsError) as exc_info:
            generator.generate()
        assert "not empty" in str(exc_info.value)

    def test_valid_name_succeeds(self, temp_dir: Path) -> None:
        """Test valid project name generates successfully."""
        generator = ProjectGenerator(
            project_name="valid-project",
            output_dir=temp_dir,
            python_version="3.11",
        )
        result = generator.generate()
        assert result.project_path == temp_dir / "valid-project"
        assert result.project_path.exists()

    def test_git_init_false_skips_git(self, temp_dir: Path) -> None:
        """Test git_init=False skips Git initialization."""
        generator = ProjectGenerator(
            project_name="no-git-project",
            output_dir=temp_dir,
            python_version="3.11",
            git_init=False,
        )
        result = generator.generate()
        assert result.git_initialized is False
        assert not (result.project_path / ".git").exists()
