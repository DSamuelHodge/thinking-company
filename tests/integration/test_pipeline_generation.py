"""Integration tests for pipeline generation command."""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from restack_gen.cli.main import cli


@pytest.fixture
def test_project(tmp_path: Path) -> Path:
    """Create a temporary test project."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create minimal project structure
    (project_dir / "restack.toml").write_text("[project]\nname = 'test-project'\n")
    (project_dir / "pyproject.toml").write_text(
        "[project]\nname = 'test-project'\nversion = '0.1.0'\n"
    )

    # Create component directories
    (project_dir / "agents").mkdir()
    (project_dir / "workflows").mkdir()
    (project_dir / "functions").mkdir()
    (project_dir / "tests").mkdir()

    return project_dir


class TestGeneratePipeline:
    """Tests for pipeline generation."""

    def test_generate_pipeline_creates_file(self, test_project: Path, monkeypatch) -> None:
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                "pipeline",
                "TestPipeline",
                "--operators",
                "A -> B || C",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "Generated pipeline: TestPipeline" in result.output

        pipeline_file = test_project / "workflows" / "test_pipeline.py"
        assert pipeline_file.exists()

        content = pipeline_file.read_text()
        assert "class TestPipeline" in content
        assert "asyncio.gather" in content  # parallel present
        assert "def step_a" in content
        assert "def step_b" in content
        assert "def step_c" in content

    def test_generated_pipeline_is_valid_python(self, test_project: Path, monkeypatch) -> None:
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        runner.invoke(
            cli,
            [
                "generate",
                "pipeline",
                "TestPipeline",
                "--operators",
                "A -> B",
            ],
        )

        pipeline_file = test_project / "workflows" / "test_pipeline.py"
        content = pipeline_file.read_text()
        ast.parse(content)  # raises on syntax error

    @pytest.mark.asyncio
    async def test_pipeline_executes_sequence_and_optional(
        self, test_project: Path, monkeypatch
    ) -> None:
        monkeypatch.chdir(test_project)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                "pipeline",
                "TestPipeline",
                "--operators",
                "A ->? B",
            ],
        )
        assert result.exit_code == 0, result.output

        pipeline_file = test_project / "workflows" / "test_pipeline.py"

        # Provide a minimal mock for restack_ai.workflow decorators & logger
        class _Logger:
            def info(self, *args, **kwargs):
                pass

            def error(self, *args, **kwargs):
                pass

        class _WorkflowNS:
            logger = _Logger()

            def defn(self, name: str | None = None):
                def deco(cls):
                    return cls

                return deco

            def run(self, fn):
                return fn

        mock_module = type(sys)("restack_ai")
        mock_module.workflow = _WorkflowNS()
        sys.modules["restack_ai"] = mock_module

        # Dynamic import from file
        spec = importlib.util.spec_from_file_location(
            "test_pipeline_module",
            str(pipeline_file),
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["test_pipeline_module"] = module
        spec.loader.exec_module(module)  # type: ignore[attr-defined]

        # Instantiate and run
        PipelineClass = module.TestPipeline
        PipelineInput = module.TestPipelineInput

        pipeline = PipelineClass()
        input_data = PipelineInput()
        output = await pipeline.run(input_data)

        assert output.steps_completed >= 1
        # Optional successor should run since stub returns non-None
        assert output.order == ["A", "B"]
