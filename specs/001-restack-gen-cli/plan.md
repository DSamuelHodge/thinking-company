# Implementation Plan: Restack Gen CLI

**Branch**: `001-restack-gen-cli` | **Date**: November 6, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-restack-gen-cli/spec.md`

**Note**: This file is generated and maintained by the `/speckit.plan` workflow.

## Summary

A convention-over-configuration CLI that scaffolds Restack agents, workflows, functions, tool servers, and LLM integrations. The CLI generates Python projects with component-type structure (agents/, workflows/, functions/ directories) and includes sensible defaults for exponential backoff retry strategies, timeout configurations, and structured logging. Technical approach uses Rails-style generators, Pydantic typing, and integration patterns for FastMCP and multi-provider LLMs (Gemini primary).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Click (CLI), Jinja2 (templating), Pydantic (validation), restack-ai (agents/workflows), fastmcp (MCP protocol), google-generativeai (Gemini)  
**Storage**: File system (templates, generated code, migration tracking)  
**Testing**: pytest (unit + integration with temp projects)  
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)  
**Project Type**: Single CLI project with template-based code generation  
**Performance Goals**: <10 seconds for component generation; <2 minutes for full project scaffolding  
**Constraints**: Must generate valid, runnable Python code; maintain backward compatibility with existing Restack projects; adhere to constitution gates  
**Scale/Scope**: Support 100+ concurrent CLI operations; projects with 1000+ components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on `.specify/memory/constitution.md`:

- ✅ Library-First Architecture: CLI and generators are modular libraries with clear boundaries
- ✅ CLI Interface Standard: Text I/O via Click; supports verbose/JSON modes; proper exit codes
- ✅ Test-First Development: pytest tests accompany all generators and commands (unit + integration)
- ✅ Integration Testing: Contracts and CLI flows covered by integration tests (new, generate, doctor)
- ✅ Observability & Debuggability: Structured JSON logging and verbose flags throughout
- ✅ Simplicity & YAGNI: Scope limited to scaffolding; infrastructure patterns documented, not over-built
- ✅ Versioning & Breaking Changes: Semver applied; migration guides for config schema changes

**Status**: ✅ PASS - No constitutional violations identified

## Project Structure

### Documentation (this feature)

```text
specs/001-restack-gen-cli/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 contracts
│   ├── llm-provider-interface.md
│   ├── fastmcp-integration.md
│   └── pipeline-operator-grammar.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
restack_gen/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   └── commands/
│       ├── __init__.py
│       ├── new.py
│       ├── generate.py
│       └── doctor.py
├── generators/
│   ├── __init__.py
│   ├── base.py
│   ├── project.py
│   ├── agent.py
│   ├── workflow.py
│   ├── function.py
│   └── pipeline.py (planned)
├── templates/
│   ├── project/
│   ├── agents/
│   ├── workflows/
│   ├── functions/
│   ├── pipelines/ (planned)
│   └── llm/
├── models/
│   ├── __init__.py
│   ├── config.py
│   └── project.py
├── migrations/
│   └── __init__.py
└── utils/
    ├── __init__.py
    ├── file_ops.py
    ├── validation.py
    └── logging.py

tests/
├── conftest.py
├── unit/
└── integration/
```

**Structure Decision**: Single CLI project with modular generator system for maintainability and clear separation of concerns between CLI interface, generation logic, templates, and utilities.

## Infrastructure Scope Clarification

The CLI generates scaffolding and integration points. The following are runtime dependencies/patterns (documented in research.md) and are NOT generated as code modules:
- FastMCP Server Manager (lifecycle management)
- FastMCP Client Wrapper (caching/observability)
- Multi-Provider LLM Router (fallback + circuit breakers)
- Declarative Pipeline Operators (CLI implements parser; templates generate workflows)

See `contracts/fastmcp-integration.md` for details.

## Complexity Tracking

> No violations identified; section not required.

## Scope Adjustments (2025-11-06)

- Pipeline Operator Scope (US3): Initial release limited to sequence (`→`), parallel (`⇄`), and optional (`→?`) operators. Loop and conditional branches are deferred to "Future Enhancements" and are documented in `contracts/pipeline-operator-grammar.md` under limitations. Tasks updated in `tasks.md` accordingly; acceptance in `spec.md` aligned
- LLM "Routing" Clarification (FR-005): Generation provides a provider registry and selection mechanism with prompt versioning. Dynamic runtime routing beyond the registry is treated as a documented pattern (see contracts) and not a generation target
- Temporal Runtime Validation (FR-015): Acceptance clarified in `spec.md`. `restack doctor` verifies `restack-ai` minimum version and decorators' usage; integration tests validate decorator usage via stubs/mocks without requiring a live Temporal cluster
- SC-008 Baseline & Measurement: Added a measurement plan to `spec.md` (baseline T0 via usability study) and an interim proxy gate: create + generate + test + doctor must complete in ≤ 20 minutes on a clean machine following `quickstart.md`
