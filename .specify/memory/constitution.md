# Thinking Company Development Constitution

## Core Principles

### I. Library-First Architecture
Every feature starts as a standalone library with clear boundaries. Libraries must be:
- Self-contained with minimal external dependencies
- Independently testable without requiring full system context
- Well-documented with clear purpose and usage examples
- Focused on solving one problem well (Single Responsibility Principle)

**Rationale**: Modular libraries enable reusability, easier testing, and independent versioning.

### II. CLI Interface Standard
Every library exposes core functionality through a command-line interface following text protocol:
- **Input**: stdin streams, command-line arguments, or file paths
- **Output**: stdout for results (JSON and human-readable formats supported)
- **Errors**: stderr for diagnostics and error messages
- **Exit codes**: 0 for success, non-zero for failures

**Rationale**: Text-based I/O ensures debuggability, composability, and automation-friendly interfaces.

### III. Test-First Development (NON-NEGOTIABLE)
Test-Driven Development (TDD) is mandatory for all code:
1. Write tests that define expected behavior
2. Obtain user/stakeholder approval of test scenarios
3. Verify tests fail (red phase)
4. Implement code to pass tests (green phase)
5. Refactor while maintaining passing tests

**No implementation without tests first.** Red-Green-Refactor cycle strictly enforced.

**Rationale**: TDD prevents over-engineering, ensures specifications are testable, and maintains high code quality.

### IV. Integration Testing Requirements
Integration tests are mandatory for:
- New library contracts and interfaces
- Changes to existing contracts (backward compatibility)
- Inter-service or inter-component communication
- Shared schemas and data models
- External API integrations

**Rationale**: Unit tests alone don't catch integration issues; contract tests ensure system coherence.

### V. Observability & Debuggability
All code must support debugging and monitoring:
- **Structured logging**: JSON-formatted logs with context (timestamps, request IDs, component names)
- **Text I/O protocol**: Enables piping, grepping, and standard Unix tools
- **Verbose modes**: Support `--verbose` or `--debug` flags for detailed output
- **Error messages**: Actionable messages with suggestions for resolution

**Rationale**: Production issues require observable systems; structured logs enable automated analysis.

### VI. Simplicity & YAGNI
Start with the simplest solution that works:
- Implement only what's needed now (YAGNI - You Aren't Gonna Need It)
- Avoid premature optimization and over-engineering
- Prefer explicit over clever code
- Refactor when complexity is proven necessary, not anticipated

**Rationale**: Simple code is easier to understand, test, and maintain. Complexity should be justified by real requirements.

### VII. Versioning & Breaking Changes
Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes to public APIs or contracts
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, documentation updates

Breaking changes require:
- Migration guides for users
- Deprecation warnings in previous version
- Changelog documentation

**Rationale**: Predictable versioning reduces integration friction and manages expectations.

## Development Workflow

### Code Review Requirements
All changes require:
- Pull request with clear description of changes
- Passing tests (unit and integration where applicable)
- Constitution compliance verification
- At least one approving review from team member

### Quality Gates
Before merging, verify:
- ✅ All tests pass (no skipped tests without justification)
- ✅ Code follows project style guidelines (linters pass)
- ✅ Documentation updated for public API changes
- ✅ No new complexity violations introduced
- ✅ Constitution principles upheld

### Complexity Justification
Introducing complexity requires:
- Documented rationale for why simpler approach won't work
- Evidence of actual need (not hypothetical future requirements)
- Plan for managing and testing the complexity
- Approval from technical lead or team consensus

## Technology Standards

### Language & Framework Choices
- **Python**: 3.11+ for all Python projects (typed code preferred)
- **Testing**: pytest with fixtures and parametrization
- **CLI**: Click framework for command-line interfaces
- **Configuration**: TOML for human-readable configs, Pydantic for validation
- **Logging**: Structured JSON logs via standard logging library

### Dependency Management
- Pin direct dependencies to specific versions
- Document why each dependency is needed
- Regular security audits of dependencies
- Minimize dependency count (avoid bloat)

## Governance

### Constitution Authority
This constitution supersedes all other development practices and guidelines. When conflicts arise:
1. Constitution principles take precedence
2. Discuss discrepancies openly with team
3. Document exceptions with clear rationale
4. Propose constitution amendments if principle needs evolution

### Amendment Process
To amend the constitution:
1. Propose change with rationale in team discussion
2. Demonstrate need with real examples
3. Achieve consensus or majority approval
4. Document amendment with effective date
5. Update version number and Last Amended date

### Compliance & Enforcement
- All PRs must verify constitution compliance in description
- Code reviews check for principle adherence
- Complexity violations require explicit approval
- Regular retrospectives assess constitution effectiveness

### Living Document
This constitution is a living document that evolves with team experience. Use `.github/copilot-instructions.md` for runtime development guidance and current project conventions.

**Version**: 1.0.0 | **Ratified**: November 6, 2025 | **Last Amended**: November 6, 2025
