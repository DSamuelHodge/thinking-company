"""`restack doctor` command implementation for project diagnostics."""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import click

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback for older Pythons
    tomllib = None  # type: ignore[assignment]

from ...utils.logging import get_logger
from ...utils.validation import (
    validate_project_structure,
    validate_python_syntax,
    validate_restack_toml,
)

LOGGER = get_logger("cli.doctor")


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: list[str]
    warn: bool = False


def _find_project_root() -> Path | None:
    """Locate project root by searching for restack.toml upwards from CWD."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "restack.toml").exists():
            return current
        current = current.parent
    return None


def _load_toml(path: Path) -> dict:
    if tomllib is None:
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_config(project_root: Path) -> CheckResult:
    toml_path = project_root / "restack.toml"
    if not toml_path.exists():
        return CheckResult("Config", ok=False, details=["restack.toml is missing"])
    try:
        data = _load_toml(toml_path)
    except Exception as exc:  # pragma: no cover
        return CheckResult("Config", ok=False, details=[f"Failed to parse restack.toml: {exc}"])

    issues = validate_restack_toml(data)
    details = [issue.message for issue in issues]
    ok = len(details) == 0
    return CheckResult("Config", ok=ok, details=details)


def _check_structure(project_root: Path, fix: bool) -> CheckResult:
    issues = validate_project_structure(project_root)
    details: list[str] = []
    if issues and fix:
        # Attempt auto-fix
        for issue in issues:
            # message format: Missing directory: <name>
            if issue.message.startswith("Missing directory:"):
                name = issue.message.split(":", 1)[1].strip()
                try:
                    (project_root / name).mkdir(parents=True, exist_ok=True)
                    details.append(f"Created missing directory: {name}")
                except Exception as exc:  # pragma: no cover
                    details.append(f"Failed to create directory {name}: {exc}")
    else:
        details.extend(i.message for i in issues)
    # Re-validate after potential fix
    final_issues = validate_project_structure(project_root)
    ok = len(final_issues) == 0
    if ok and not details:
        details = []
    return CheckResult("Structure", ok=ok, details=details)


def _iter_python_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for sub in ["agents", "workflows", "functions"]:
        base = project_root / sub
        if base.exists():
            files.extend(base.rglob("*.py"))
    return files


def _check_syntax(project_root: Path) -> CheckResult:
    paths = _iter_python_files(project_root)
    issues = validate_python_syntax(paths, project_root=project_root)
    details = [i.message for i in issues]
    ok = len(details) == 0
    return CheckResult("Syntax", ok=ok, details=details)


MIN_RESTACK_AI_VERSION = "0.0.115"


def _parse_version(raw: str) -> tuple[int, int, int]:
    parts = raw.strip().split(".")
    nums: list[int] = []
    for p in parts[:3]:
        try:
            nums.append(int("".join(ch for ch in p if ch.isdigit())))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)  # type: ignore[return-value]


def _version_lt(a: str, b: str) -> bool:
    return _parse_version(a) < _parse_version(b)


def _check_dependencies(project_root: Path) -> CheckResult:
    details: list[str] = []
    # Lightweight: verify dependency manifests exist; avoid environment-coupled import checks
    if (
        not (project_root / "requirements.txt").exists()
        and not (project_root / "pyproject.toml").exists()
    ):
        details.append("No requirements.txt or pyproject.toml found")
        return CheckResult("Dependencies", ok=False, details=details)
    # SDK compatibility check (manifest-level): warn if restack-ai not declared
    try:
        req = project_root / "requirements.txt"
        declared = False
        declared_version: str | None = None
        if req.exists():
            content = req.read_text(encoding="utf-8")
            for line in content.splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if s.lower().startswith("restack-ai"):
                    declared = True
                    # Accept patterns: restack-ai>=x.y.z, restack-ai==x.y.z, restack-ai~=x.y, restack-ai[x]
                    for sep in [">=", "==", "~="]:
                        if sep in s:
                            declared_version = s.split(sep, 1)[1].split()[0]
                            # Strip extras like ; or [] or whitespace
                            declared_version = declared_version.split(";")[0].split("[")[0]
                            break
                    if declared_version is None and "==" in s:
                        declared_version = s.split("==", 1)[1].split()[0]
                    break
        # future: parse pyproject for dependencies if needed
        if not declared:
            details.append(
                "Restack SDK ('restack-ai') not declared in requirements.txt. Add 'restack-ai>="
                + MIN_RESTACK_AI_VERSION
                + "' to ensure compatibility."
            )
            return CheckResult("Dependencies", ok=True, details=details, warn=True)
        # Enforce minimum version if specified
        if declared_version and _version_lt(declared_version, MIN_RESTACK_AI_VERSION):
            details.append(
                f"Declared restack-ai version {declared_version} is below minimum {MIN_RESTACK_AI_VERSION}."
            )
            return CheckResult("Dependencies", ok=False, details=details)
        if declared_version is None:
            # Version unspecified; warn but pass
            details.append(
                "restack-ai version not pinned; specify >= "
                + MIN_RESTACK_AI_VERSION
                + " for stability."
            )
            return CheckResult("Dependencies", ok=True, details=details, warn=True)
        return CheckResult("Dependencies", ok=True, details=details)
    except Exception:  # pragma: no cover
        # Non-fatal; return ok
        return CheckResult("Dependencies", ok=True, details=details)


@click.command("doctor")
@click.option(
    "--check",
    "checks",
    type=click.Choice(
        ["all", "config", "structure", "syntax", "dependencies"], case_sensitive=False
    ),
    default="all",
    show_default=True,
    help="Run only a specific set of checks",
)
@click.option("--fix", is_flag=True, help="Attempt to auto-fix fixable issues")
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON")
@click.option(
    "--verbose",
    "doctor_verbose",
    is_flag=True,
    help="Show extended diagnostic details (doctor-local)",
)
def doctor(checks: str, fix: bool, json_output: bool, doctor_verbose: bool) -> None:
    """Run health checks and diagnostics for the current Restack project."""
    project_root = _find_project_root()
    if not project_root:
        click.echo("❌ Error: Not in a Restack project directory.", err=True)
        click.echo("   Run this command from a directory containing restack.toml", err=True)
        sys.exit(1)

    selected = [checks] if checks != "all" else ["config", "structure", "syntax", "dependencies"]

    results: list[CheckResult] = []
    if "config" in selected:
        results.append(_check_config(project_root))
    if "structure" in selected:
        results.append(_check_structure(project_root, fix=fix))
    if "syntax" in selected:
        results.append(_check_syntax(project_root))
    if "dependencies" in selected:
        results.append(_check_dependencies(project_root))

    # If JSON output requested, emit machine-readable structure
    if json_output:
        import json

        payload = {
            "checks": [
                {
                    "name": r.name,
                    "ok": r.ok,
                    "warn": r.warn,
                    "details": r.details,
                }
                for r in results
            ]
        }
        errors = sum(1 for r in results if not r.ok)
        warns = sum(1 for r in results if r.warn and r.ok)
        payload["summary"] = {"errors": errors, "warnings": warns}
        if doctor_verbose:
            payload["meta"] = {
                "project_root": str(project_root),
                "python_files_checked": sum(1 for r in results if r.name == "Syntax"),
                "min_restack_ai_version": MIN_RESTACK_AI_VERSION,
            }
        click.echo(json.dumps(payload, indent=2))
        if errors:
            sys.exit(1)
        sys.exit(0)

    # Output (human readable)
    errors = 0
    warns = 0
    for res in results:
        icon = "✅" if res.ok and not res.warn else ("⚠️" if res.warn else "❌")
        click.echo(f"{icon} {res.name}")
        for line in res.details:
            click.echo(textwrap.indent(f"- {line}", prefix="    "))
        if doctor_verbose and res.name == "Dependencies" and res.ok and not res.warn:
            click.echo(
                textwrap.indent(
                    f"- restack-ai meets minimum version {MIN_RESTACK_AI_VERSION}", prefix="    "
                )
            )
        if doctor_verbose and res.name == "Syntax" and res.ok:
            py_count = len(_iter_python_files(project_root))
            click.echo(textwrap.indent(f"- Checked {py_count} Python files", prefix="    "))
        if not res.ok:
            errors += 1
        elif res.warn:
            warns += 1

    if errors:
        click.echo(f"\n❌ Doctor found {errors} error(s).", err=True)
        sys.exit(1)
    if warns:
        click.echo(f"\n⚠️ Doctor completed with {warns} warning(s).")
    else:
        click.echo("\n✅ All checks passed.")
