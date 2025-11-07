"""Unit tests for validation utilities."""

import pytest
from pydantic import ValidationError

from restack_gen.utils.validation import (
    ValidationIssue,
    validate_component_name,
    validate_module_name,
    validate_project_name,
)


class TestValidateProjectName:
    """Tests for project name validation (kebab-case)."""

    def test_valid_simple_name(self):
        """Valid lowercase single word."""
        issues = validate_project_name("myproject")
        assert issues == []

    def test_valid_kebab_case(self):
        """Valid kebab-case name."""
        issues = validate_project_name("my-project")
        assert issues == []

    def test_valid_multi_segment_kebab(self):
        """Valid multi-segment kebab-case."""
        issues = validate_project_name("my-awesome-project")
        assert issues == []

    def test_valid_with_numbers(self):
        """Valid with numbers."""
        issues = validate_project_name("project-2024")
        assert issues == []

    def test_invalid_uppercase(self):
        """Uppercase letters not allowed."""
        issues = validate_project_name("MyProject")
        assert len(issues) > 0
        assert any("kebab-case" in issue.message for issue in issues)

    def test_invalid_underscore(self):
        """Underscores not allowed."""
        issues = validate_project_name("my_project")
        assert len(issues) > 0

    def test_invalid_spaces(self):
        """Spaces not allowed."""
        issues = validate_project_name("my project")
        assert len(issues) > 0

    def test_invalid_leading_hyphen(self):
        """Leading hyphen not allowed."""
        issues = validate_project_name("-myproject")
        assert len(issues) > 0

    def test_invalid_trailing_hyphen(self):
        """Trailing hyphen not allowed."""
        issues = validate_project_name("myproject-")
        assert len(issues) > 0

    def test_invalid_consecutive_hyphens(self):
        """Consecutive hyphens not allowed."""
        issues = validate_project_name("my--project")
        assert len(issues) > 0

    def test_invalid_starts_with_number(self):
        """Starting with number not allowed."""
        issues = validate_project_name("2-project")
        assert len(issues) > 0

    def test_invalid_special_chars(self):
        """Special characters not allowed."""
        issues = validate_project_name("my@project")
        assert len(issues) > 0

    def test_empty_string(self):
        """Empty string is invalid."""
        issues = validate_project_name("")
        assert len(issues) > 0


class TestValidateComponentName:
    """Tests for component name validation (PascalCase)."""

    def test_valid_simple_name(self):
        """Valid single PascalCase word."""
        issues = validate_component_name("MyComponent")
        assert issues == []

    def test_valid_multi_word(self):
        """Valid multi-word PascalCase."""
        issues = validate_component_name("MyAwesomeComponent")
        assert issues == []

    def test_valid_with_numbers(self):
        """Valid with numbers."""
        issues = validate_component_name("Component2024")
        assert issues == []

    def test_valid_with_acronym(self):
        """Valid with acronym."""
        issues = validate_component_name("HTTPSAgent")
        assert issues == []

    def test_invalid_lowercase_start(self):
        """Lowercase start not allowed."""
        issues = validate_component_name("myComponent")
        assert len(issues) > 0
        assert any("PascalCase" in issue.message for issue in issues)

    def test_invalid_snake_case(self):
        """Snake_case not allowed."""
        issues = validate_component_name("My_Component")
        assert len(issues) > 0

    def test_invalid_kebab_case(self):
        """kebab-case not allowed."""
        issues = validate_component_name("My-Component")
        assert len(issues) > 0

    def test_invalid_spaces(self):
        """Spaces not allowed."""
        issues = validate_component_name("My Component")
        assert len(issues) > 0

    def test_invalid_starts_with_number(self):
        """Starting with number not allowed."""
        issues = validate_component_name("2Component")
        assert len(issues) > 0

    def test_invalid_python_keyword(self):
        """Python keywords not allowed."""
        issues = validate_component_name("Class")
        assert len(issues) > 0
        assert any("keyword" in issue.message.lower() for issue in issues)

    def test_invalid_builtin_name(self):
        """Python builtins checked (Dict should pass pattern but might fail keyword check)."""
        issues = validate_component_name("Dict")
        # Dict is not a keyword, but this documents current behavior
        # If implementation adds builtin checks, update this test
        assert issues == []  # Dict passes as valid PascalCase

    def test_empty_string(self):
        """Empty string is invalid."""
        issues = validate_component_name("")
        assert len(issues) > 0


class TestValidateModuleName:
    """Tests for module name validation (snake_case)."""

    def test_valid_simple_name(self):
        """Valid lowercase single word."""
        issues = validate_module_name("mymodule")
        assert issues == []

    def test_valid_snake_case(self):
        """Valid snake_case name."""
        issues = validate_module_name("my_module")
        assert issues == []

    def test_valid_multi_segment(self):
        """Valid multi-segment snake_case."""
        issues = validate_module_name("my_awesome_module")
        assert issues == []

    def test_valid_with_numbers(self):
        """Valid with numbers."""
        issues = validate_module_name("module_2024")
        assert issues == []

    def test_valid_leading_underscore(self):
        """Leading underscore allowed for private modules."""
        issues = validate_module_name("_mymodule")
        assert issues == []  # Pattern allows leading underscore

    def test_invalid_uppercase(self):
        """Uppercase letters not allowed."""
        issues = validate_module_name("MyModule")
        assert len(issues) > 0
        assert any("snake_case" in issue.message for issue in issues)

    def test_invalid_kebab_case(self):
        """kebab-case not allowed."""
        issues = validate_module_name("my-module")
        assert len(issues) > 0

    def test_invalid_spaces(self):
        """Spaces not allowed."""
        issues = validate_module_name("my module")
        assert len(issues) > 0

    def test_invalid_trailing_underscore(self):
        """Trailing underscore (single char) is valid by pattern."""
        issues = validate_module_name("mymodule_")
        # Pattern allows [a-z_][a-z0-9_]* so trailing _ is valid
        assert issues == []

    def test_invalid_consecutive_underscores(self):
        """Consecutive underscores allowed by pattern."""
        issues = validate_module_name("my__module")
        # Pattern allows any number of underscores
        assert issues == []

    def test_invalid_starts_with_number(self):
        """Starting with number not allowed."""
        issues = validate_module_name("2_module")
        assert len(issues) > 0

    def test_invalid_python_keyword(self):
        """Python keywords not allowed."""
        issues = validate_module_name("class")
        assert len(issues) > 0
        assert any("keyword" in issue.message.lower() for issue in issues)

    def test_invalid_special_chars(self):
        """Special characters not allowed."""
        issues = validate_module_name("my@module")
        assert len(issues) > 0

    def test_empty_string(self):
        """Empty string is invalid."""
        issues = validate_module_name("")
        assert len(issues) > 0


class TestValidationIssueModel:
    """Tests for ValidationIssue Pydantic model."""

    def test_create_issue(self):
        """Create validation issue."""
        issue = ValidationIssue(
            field="project_name",
            message="Invalid name",
        )
        assert issue.field == "project_name"
        assert issue.message == "Invalid name"

    def test_issue_field_and_message_required(self):
        """Both field and message are required."""
        # Assert specific ValidationError instead of broad Exception (B017)
        with pytest.raises(ValidationError):
            ValidationIssue(field="name")  # type: ignore
