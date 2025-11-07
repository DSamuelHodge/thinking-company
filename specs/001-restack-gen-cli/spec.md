# Feature Specification: Restack Gen CLI

**Feature Branch**: `001-restack-gen-cli`  
**Created**: November 6, 2025  
**Status**: Draft  
**Input**: User description: "Restack Gen is a convention-over-configuration CLI that scaffolds Restack agents, workflows, functions, tool servers, and LLM integrations. It produces runnable, testable, and observable code with sensible defaults for retries, timeouts, and structured logging."

## Clarifications

### Session 2025-11-06

- Q: Target Programming Language → A: Python (matches Pydantic requirement, strong Temporal support)
- Q: Project Structure Convention → A: Component-type (separate top-level dirs: agents/, workflows/, functions/)
- Q: Default Retry Strategy → A: Exponential backoff with jitter (1s, 2s, 4s, 8s + randomization)
- Q: LLM Provider Support → A: Multi-provider (Gemini primary, extensible to others)
- Q: Configuration Migration Approach → A: Version-based (numbered migration files, up/down methods)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create New Restack Project (Priority: P1)

A developer wants to quickly bootstrap a new Restack project with all necessary scaffolding and sensible defaults.

**Why this priority**: Core foundation feature - without project creation, no other CLI functionality is possible. This delivers immediate value by eliminating manual setup complexity.

**Independent Test**: Can be fully tested by running `restack new my-project` and verifying a complete, runnable project structure is created with proper configuration files, entry points, and documentation.

**Acceptance Scenarios**:

1. **Given** a developer has the Restack Gen CLI installed, **When** they run `restack new my-project`, **Then** a new directory is created with complete project scaffolding including configuration files, folder structure, and basic documentation
2. **Given** a new project is created, **When** the developer examines the project structure, **Then** they find sensible defaults for retries, timeouts, and structured logging already configured
3. **Given** a freshly created project, **When** the developer runs the default commands, **Then** the project builds and runs without additional configuration

---

### User Story 2 - Generate Individual Components (Priority: P2)

A developer working in an existing Restack project wants to generate specific components (agents, workflows, functions) using Rails-style generators.

**Why this priority**: Essential productivity feature that provides the core scaffolding value. Builds on the foundation project but delivers significant time savings.

**Independent Test**: Can be tested independently by creating generators that work in any valid Restack project structure, each producing working, testable code components.

**Acceptance Scenarios**:

1. **Given** an existing Restack project, **When** developer runs `restack g agent UserAgent`, **Then** a complete agent implementation is generated with proper structure, tests, and integration points
2. **Given** an existing project, **When** developer runs `restack g workflow ProcessData`, **Then** a workflow implementation is generated with type-safe interfaces and example operations
3. **Given** an existing project, **When** developer runs `restack g function CalculateScore`, **Then** a function implementation is generated with proper input/output validation and error handling

---

### User Story 3 - Generate Complex Pipelines (Priority: P3)

A developer wants to create sophisticated data processing pipelines using operator grammar for composition (sequence, parallel, optional operations) for the initial release scope.

**Why this priority**: Advanced feature for complex use cases. Provides significant value but is not essential for basic CLI functionality.

**Independent Test**: Can be tested by generating pipeline definitions that correctly implement operator grammar and produce executable workflow compositions.

**Acceptance Scenarios**:

1. **Given** an existing project, **When** developer runs `restack g pipeline DataProcessor --with-operators`, **Then** a pipeline is generated with operator grammar support for sequence (`→`), parallel (`⇄`), and optional (`→?`) composition
2. **Given** a generated pipeline, **When** developer uses operators to compose workflow steps, **Then** the resulting pipeline executes steps in the correct order with proper error handling, including concurrent execution semantics for parallel groups
3. **Given** a complex pipeline with optional logic, **When** preconditions are not met, **Then** optional steps are skipped and the pipeline completes without executing those branches

---

### User Story 4 - LLM Integration and Tool Server Setup (Priority: P3)

A developer wants to integrate LLM capabilities with prompt versioning and FastMCP tool servers for AI-powered workflows.

**Why this priority**: Specialized feature for AI use cases. Important for the ecosystem but not core to basic scaffolding functionality.

**Independent Test**: Can be tested by generating LLM integration code that successfully connects to language models and manages prompt versions.

**Acceptance Scenarios**:

1. **Given** an existing project, **When** developer runs `restack g llm ChatAgent --with-prompts`, **Then** LLM integration code is generated with prompt versioning support and proper configuration
2. **Given** LLM integration is set up, **When** developer creates versioned prompts, **Then** the system can switch between prompt versions and track performance
3. **Given** FastMCP tool integration, **When** the system processes requests, **Then** tools are correctly routed and responses are properly formatted

---

### User Story 5 - Health Checks and Diagnostics (Priority: P2)

A developer wants to validate their Restack project configuration and diagnose common issues using built-in health checks.

**Why this priority**: Critical for developer experience and debugging. Prevents common configuration errors and reduces support burden.

**Independent Test**: Can be tested by running doctor commands on various project states and verifying correct diagnosis of configuration issues.

**Acceptance Scenarios**:

1. **Given** a Restack project with configuration issues, **When** developer runs `restack doctor`, **Then** the system identifies specific problems and provides actionable remediation steps
2. **Given** a properly configured project, **When** health checks are run, **Then** all systems report healthy status with performance metrics
3. **Given** syntax validation needs, **When** developer runs validation commands, **Then** the system checks generated code for common issues before deployment

### Edge Cases

#### EC-001: Project Creation Failures
**Scenario**: Directory permissions denied or target directory already exists

**Expected Behavior**:
- Check permissions before creating directories
- If target exists: Prompt user with `--force` option to overwrite
- If permissions denied: Display clear error with suggested fixes (chmod, sudo, different location)
- No partial project creation (rollback on failure)

**Acceptance**: CLI exits with code 1, displays actionable error message, and leaves no partial artifacts

---

#### EC-002: Invalid Generator Names
**Scenario**: User provides invalid component names (reserved keywords, special characters, lowercase)

**Expected Behavior**:
- Validate name against pattern: `^[A-Z][a-zA-Z0-9]*$` (PascalCase)
- Check against Python reserved keywords (class, def, import, etc.)
- Check against existing component names to prevent duplicates
- Provide suggestions for valid alternatives

**Acceptance**: CLI rejects invalid names with specific error message and suggested corrections

---

#### EC-003: Missing Templates
**Scenario**: Template file is missing or corrupted

**Expected Behavior**:
- Verify template exists before rendering
- If missing: Offer to reinstall CLI or download templates
- If corrupted: Display template path and checksum mismatch details
- Provide fallback to basic template if available

**Acceptance**: CLI does not crash; provides recovery options

---

#### EC-004: LLM Service Unavailable
**Scenario**: Gemini API is down or API key is invalid during LLM-dependent generation

**Expected Behavior**:
- Generation continues for non-LLM components (agents, workflows, functions)
- LLM-specific features (prompt generation) deferred with warning
- Generate TODO comments in code where LLM would enhance
- Provide retry command for LLM features when service recovers

**Acceptance**: CLI generates functional code with warnings; no crash on LLM unavailability

---

#### EC-005: Configuration Migration Conflicts
**Scenario**: Multiple migrations target same config field or migration history is corrupted

**Expected Behavior**:
- Detect conflicting migrations during validation phase
- Display conflict details (which migrations, which fields)
- Require manual resolution (edit migration or config)
- Provide `restack migrate status` to show migration state
- Support `restack migrate rollback` to undo last migration

**Acceptance**: No automatic destructive changes; user has full visibility and control

---

#### EC-006: Generated Code Conflicts
**Scenario**: Generated file would overwrite existing implementation

**Expected Behavior**:
- Check if file exists before generating
- If exists: Prompt user with options:
  - `--force`: Overwrite (with backup creation)
  - `--merge`: Attempt smart merge (future enhancement)
  - `--rename`: Generate with suffix (e.g., `AgentNew.py`)
  - `--skip`: Abort generation for this file
- Display diff preview if `--verbose` enabled

**Acceptance**: No silent overwrites; user explicitly chooses conflict resolution strategy

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide `restack new` command that creates complete Python project scaffolding with component-type structure (agents/, workflows/, functions/ directories) and sensible defaults including exponential backoff with jitter retry strategy, timeout configurations, and structured logging
- **FR-002**: System MUST provide Rails-style generators (`restack g agent`, `restack g workflow`, `restack g function`) that create runnable, testable Python code
- **FR-003**: System MUST generate type-safe Python code using Pydantic models for all data structures and interfaces
- **FR-004**: System MUST support operator grammar for pipeline composition including sequence (`→`), parallel (`⇄`), and optional (`→?`) operations (see contracts/pipeline-operator-grammar.md for formal grammar specification)
- **FR-005**: System MUST provide an LLM provider registry and selection with prompt versioning for AI-powered workflows with multi-provider support (Gemini as primary default, extensible to other providers per contracts/llm-provider-interface.md). "Routing" here refers to selecting among configured providers via the registry in generated scaffolding; dynamic runtime routers beyond the registry are documented patterns (see contracts/llm-provider-interface.md) and not generation targets
- **FR-006**: System MUST integrate with FastMCP tool servers for tool management and routing (see contracts/fastmcp-integration.md for integration patterns; note: Server Manager, LLM Router, and infrastructure utilities are runtime dependencies described in research.md, NOT code generation targets)
- **FR-007**: System MUST provide `restack doctor` command for health checks and configuration validation
- **FR-008**: System MUST validate syntax before code generation to prevent invalid output (includes AST parsing for Python code, Pydantic schema validation, Python keyword checking, and pipeline operator grammar validation)
- **FR-009**: System MUST support reversible configuration migrations for schema evolution using version-based approach with numbered migration files and up/down methods
- **FR-010**: System SHOULD provide `restack run:server` command for starting development servers (marked as future enhancement - Phase 8, not required for MVP)
- **FR-011**: System MUST generate comprehensive unit and integration tests for all generated components
- **FR-012**: System MUST create CI-friendly project layouts with proper build and deployment configurations
- **FR-013**: System MUST enforce convention-over-configuration through opinionated defaults while allowing customization
- **FR-014**: System MUST provide structured logging and observability features in all generated code
- **FR-015**: System MUST build upon Restack.io Kubernetes-native Agents Framework with Temporal infrastructure integration

#### FR-015 Acceptance: Temporal Runtime Validation

- Generated workflows MUST use Temporal-compatible decorators (`@workflow.defn`, `@workflow.run`)
- Generated agents MUST use Temporal-compatible decorators (`@agent.defn`, `@agent.run`)
- `restack doctor` MUST verify `restack-ai` (Temporal integration) is installed and at or above the minimum supported version; otherwise warn or error accordingly
- Integration tests MUST simulate a minimal workflow run using stubs/mocks to validate import-time registration and decorator usage without requiring a live Temporal cluster

### Key Entities

- **Project**: Complete Restack Python application with component-type folder structure (agents/, workflows/, functions/), configuration files, dependencies, and build setup
- **Agent**: Autonomous component that executes workflows and manages state using Restack framework
- **Workflow**: Orchestrated sequence of operations with exponential backoff retry logic, timeout handling, and error recovery mechanisms
- **Function**: Reusable code unit with defined inputs, outputs, and validation rules
- **Pipeline**: Complex workflow composition using operator grammar for advanced data processing
- **Tool Server**: FastMCP-compatible service that provides tools and capabilities to workflows
- **LLM Integration**: Multi-provider language model connection (Gemini primary) with prompt versioning and routing capabilities
- **Configuration Migration**: Reversible schema change using version-based migration files with up/down methods that updates project structure and settings

## Architecture Clarifications *(informational)*

### Code Generation vs Runtime Dependencies

**What the CLI Generates**:
- Restack agent scaffolding with `@agent.defn()`, `@agent.event`, `agent.step()` patterns
- Workflow definitions with `@workflow.defn()` and retry configurations
- Function/activity implementations with timeout and retry settings
- FastMCP tool server scaffolding with `@mcp.tool` decorated functions
- Project configuration files (`restack.toml`, `pyproject.toml`, CI workflows)
- Comprehensive test suites for all generated components

**What are Runtime Dependencies** (from research.md):
- **Restack SDK** (`restack-ai`) - Core framework for agents and workflows
- **FastMCP** (`fastmcp`) - MCP protocol implementation for tools/resources/prompts
- **Gemini SDK** (`google-generativeai`) - LLM provider implementation
- **Infrastructure Patterns** - Server Manager, LLM Router, Client Wrappers are architectural patterns and example implementations described in research.md for users to adapt, not generated code modules

### Restack Agent Design Patterns

Generated agents follow these conventions (per research.md):
- **Statefulness**: Instance variables track agent state across events
- **Typed Events**: Pydantic models define event inputs with validation
- **Idempotent Functions**: Functions called via `agent.step()` are pure and retry-safe
- **Communication**: Agents signal each other via `agent.signal()`
- **Lifecycle Control**: `@agent.run` manages agent termination conditions
- **Error Handling**: Deterministic failures wrapped in `NonRetryableError`
- **FastMCP Integration**: MCP tool calls wrapped in `agent.step()` for retry safety

### Layer Separation

Generated code maintains clear separation:
1. **Restack Layer** (Stateful) - Agent state, workflow orchestration, event handling
2. **FastMCP Layer** (Stateless) - Tool execution, resource access, prompt templates
3. **Business Logic** - Domain-specific functions and data processing

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can create a new Restack project and have it running within 2 minutes using default configuration
- **SC-002**: Generated code passes all included tests without modification and runs successfully on first execution
- **SC-003**: Generator commands complete within 10 seconds for standard components (agents, workflows, functions)
- **SC-004**: 95% of generated projects build and deploy successfully without manual configuration changes
- **SC-005**: Health check commands identify and provide solutions for 90% of common configuration issues
- **SC-006**: Generated test suites achieve 80% code coverage for all scaffolded components
- **SC-007**: CLI commands provide helpful error messages and suggestions for 100% of invalid inputs
- **SC-008**: Generated code follows consistent patterns that reduce onboarding time for new team members by 50%

#### SC-008 Measurement Plan and Baseline

- Baseline definition: Measure time for a new engineer (familiar with Python but new to Restack) to add one workflow and one agent without the CLI, from blank project to passing tests (T0)
- Measurement method: Time-boxed usability study with at least 3 participants; record median T0 and environment details
- Target: Post-CLI flow (using quickstart + generators) achieves ≤ 50% of T0 for the same task
- Interim proxy gate (until T0 is captured): A new engineer can create a project and generate an agent, workflow, and function, run tests, and pass `restack doctor` end-to-end in ≤ 20 minutes on a clean machine following `quickstart.md`
 - See docs/metrics/onboarding.md for the schedule, data capture template, and reporting guidance
