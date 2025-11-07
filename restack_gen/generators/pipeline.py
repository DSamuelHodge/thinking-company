"""Pipeline generator for Restack CLI.

Implements v1 operator grammar with sequence (-> / →), parallel (|| / ⇄), and
optional (->? / →?) semantics. Generates a workflow-compatible pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from restack_gen.generators.base import BaseGenerator, _snake_case
from restack_gen.generators.workflow import WorkflowGenerator
from restack_gen.utils.validation import validate_component_name


# AST node definitions for a tiny operator grammar
@dataclass
class StepNode:
    name: str


@dataclass
class SeqNode:
    left: Any
    right: Any


@dataclass
class OptNode:
    left: Any
    right: Any


@dataclass
class ParNode:
    left: Any
    right: Any


class PipelineGenerator(WorkflowGenerator):
    """Generator for Restack pipeline components (specialized workflow)."""

    # Public API mirrors other generators
    def generate(
        self,
        name: str,
        output_dir: Path,
        *,
        description: str | None = None,
        operators: str | None = None,
        error_strategy: str = "halt",
        with_tests: bool = True,
        force: bool = False,
    ) -> dict[str, Path]:
        """
        Generate a pipeline (workflow with operator composition).

        Args:
            name: Pipeline name (PascalCase)
            output_dir: Output directory (project root)
            description: Optional description
            operators: Operator expression (sequence/parallel/optional)
            error_strategy: Error strategy: halt|continue|retry
            with_tests: Generate test file (future)
            force: Overwrite existing files

        Returns:
            Dict of generated file paths
        """

        # Validate name
        issues = validate_component_name(name)
        if issues:
            raise ValueError(
                f"Invalid pipeline name '{name}': {', '.join(issue.message for issue in issues)}"
            )

        # Parse operators (optional)
        ast_root = None
        steps: list[str] = []
        exec_snippets = "# No operators provided; add logic here\n    steps_completed = 0\n"

        if operators and operators.strip():
            ast_root = self._parse_expression(operators)
            steps = sorted(self._collect_steps(ast_root))
            self._validate_steps_unique(steps)
            exec_snippets = self._compile_execution(ast_root)

        # Prepare context
        context: dict[str, Any] = {
            "name": name,
            "description": description,
            "timeout": None,
            "package_name": self._get_package_name(output_dir),
            "steps": steps,
            "exec_snippets": exec_snippets,
            "error_strategy": error_strategy,
        }

        # Output under workflows/ to stay Temporal-compatible
        workflow_dir = output_dir / "workflows"
        workflow_file = workflow_dir / f"{_snake_case(name)}.py"

        generated: dict[str, Path] = {}

        if workflow_file.exists() and not force:
            raise FileExistsError(
                f"Pipeline file already exists: {workflow_file}. Use --force to overwrite."
            )

        content = self.render_template("pipelines/pipeline.py.j2", context)
        self.write_output(workflow_file, content, force=force)
        generated["pipeline"] = workflow_file

        # Tests can be added later; keep symmetry with others if needed
        if with_tests:
            test_dir = output_dir / "tests"
            test_file = test_dir / f"test_{_snake_case(name)}.py"
            # Generate a minimal smoke test to ensure importability
            if not test_file.exists() or force:
                test_content = (
                    "\n".join(
                        [
                            f"# Auto-generated smoke test for {name} pipeline",
                            "import ast",
                            f"from pathlib import Path",
                            "",
                            "def test_pipeline_generated_is_valid_python(tmp_path):",
                            f"    content = Path('{workflow_file.as_posix()}').read_text()",
                            "    ast.parse(content)",
                        ]
                    )
                    + "\n"
                )
                self.write_output(test_file, test_content, force=force)
                generated["test"] = test_file

        return generated

    # === Parsing ===
    def _tokenize(self, expr: str) -> list[str]:
        # Normalize unicode to ascii equivalents
        normalized = (
            expr.replace("→?", "->?")
            .replace("→", "->")
            .replace("⇄", "||")
        )
        # Tokens: identifiers, parentheses, operators
        pattern = r"\s*(->\?|->|\|\||[A-Za-z_][A-Za-z0-9_]*|[()])\s*"
        tokens = re.findall(pattern, normalized)
        if not tokens:
            raise ValueError("Operator expression is empty or invalid")
        return tokens

    def _parse_expression(self, expr: str):
        tokens = self._tokenize(expr)
        self._tokens = tokens
        self._pos = 0
        node = self._parse_parallel()
        if self._pos != len(self._tokens):
            raise ValueError("Unexpected tokens at end of expression")
        return node

    def _peek(self) -> str | None:
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None

    def _eat(self, value: str | None = None) -> str:
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if value is not None and tok != value:
            raise ValueError(f"Expected '{value}', got '{tok}'")
        self._pos += 1
        return tok

    # parallel := sequence ( '||' sequence )*
    def _parse_parallel(self):
        node = self._parse_sequence()
        while self._peek() == "||":
            self._eat("||")
            rhs = self._parse_sequence()
            node = ParNode(node, rhs)
        return node

    # sequence := optional ( '->' optional )*
    def _parse_sequence(self):
        node = self._parse_optional()
        while self._peek() == "->":
            self._eat("->")
            rhs = self._parse_optional()
            node = SeqNode(node, rhs)
        return node

    # optional := primary ( '->?' primary )*
    def _parse_optional(self):
        node = self._parse_primary()
        while self._peek() == "->?":
            self._eat("->?")
            rhs = self._parse_primary()
            node = OptNode(node, rhs)
        return node

    def _parse_primary(self):
        tok = self._peek()
        if tok == "(":
            self._eat("(")
            node = self._parse_parallel()
            self._eat(")")
            return node
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", tok):
            self._eat()
            return StepNode(tok)
        raise ValueError(f"Invalid token '{tok}' in expression")

    # === Validation & compilation ===
    def _collect_steps(self, node: Any) -> set[str]:
        steps: set[str] = set()
        def _walk(n: Any) -> None:
            if isinstance(n, StepNode):
                steps.add(n.name)
            elif isinstance(n, (SeqNode, OptNode, ParNode)):
                _walk(n.left)
                _walk(n.right)
        _walk(node)
        return steps

    def _validate_steps_unique(self, steps: Iterable[str]) -> None:
        # Simple v1 rule: no duplicate step names to avoid accidental cycles/ambiguity
        seen: set[str] = set()
        for s in steps:
            if s in seen:
                raise ValueError(f"Duplicate step name detected: {s}")
            seen.add(s)

    def _compile_execution(self, node: Any) -> str:
        """Compile AST into Python code snippet for the run() method body.

        Returns a string with proper indentation (assumed to be 8 spaces in template).
        """

        counter = {"i": 0}

        def new_branch_name() -> str:
            counter["i"] += 1
            return f"_branch_{counter['i']}"

        def compile_node(n: Any, indent: int = 8) -> tuple[list[str], list[str]]:
            """
            Returns (lines, prelude) where:
            - lines: inline execution lines at current position
            - prelude: helper inner functions that must be defined above current lines
            """
            pad = " " * indent
            prelude: list[str] = []
            if isinstance(n, StepNode):
                return [f"{pad}await step_{_snake_case(n.name)}(ctx)"], prelude
            if isinstance(n, SeqNode):
                l_lines, l_prelude = compile_node(n.left, indent)
                r_lines, r_prelude = compile_node(n.right, indent)
                return l_lines + r_lines, l_prelude + r_prelude
            if isinstance(n, OptNode):
                # Evaluate left into a temp to check non-null
                l_lines, l_prelude = compile_node(n.left, indent)
                # Modify the last call to capture result
                # We'll call the step function directly and capture return
                # Ensure left-most is a step or a nested block that returns something.
                # To keep it simple, re-run left into a variable using a dedicated helper.
                helper_name = new_branch_name()
                h_lines, h_prelude = compile_node(n.left, indent + 4)
                prelude.append(
                    " " * indent
                    + f"async def {helper_name}():\n"
                    + "\n".join(h_prelude)
                    + ("\n" if h_prelude else "")
                    + "\n".join(line.replace("await ", "return await ", 1) if "await " in line else line for line in h_lines)
                    + "\n"
                )
                lines = [
                    f"{pad}left_result = await {helper_name}()",
                    f"{pad}if left_result is not None:",
                ]
                r_lines, r_prelude = compile_node(n.right, indent + 4)
                return lines + r_lines, prelude + l_prelude + h_prelude + r_prelude
            if isinstance(n, ParNode):
                left_helper = new_branch_name()
                right_helper = new_branch_name()
                l_lines, l_prelude = compile_node(n.left, indent + 4)
                r_lines, r_prelude = compile_node(n.right, indent + 4)
                prelude.append(
                    " " * indent
                    + f"async def {left_helper}():\n"
                    + "\n".join(l_prelude)
                    + ("\n" if l_prelude else "")
                    + "\n".join(l_lines)
                    + "\n"
                )
                prelude.append(
                    " " * indent
                    + f"async def {right_helper}():\n"
                    + "\n".join(r_prelude)
                    + ("\n" if r_prelude else "")
                    + "\n".join(r_lines)
                    + "\n"
                )
                lines = [
                    f"{pad}await asyncio.gather({left_helper}(), {right_helper}())",
                ]
                return lines, prelude
            raise ValueError("Unknown AST node type")

        lines, prelude = compile_node(node)
        # Assemble with a progress counter
        assembled = []
        if prelude:
            assembled.extend(prelude)
        assembled.extend(lines)
        assembled.append(" " * 8 + "steps_completed = len(ctx['order'])")
        return "\n".join(assembled) + "\n"
