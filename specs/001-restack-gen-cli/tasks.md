# Tasks: Restack Gen CLI

**Input**: Design documents from `/specs/001-restack-gen-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test generation will be covered in the implementation tasks as the CLI must generate tests for scaffolded components (per FR-011).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `restack_gen/`, `tests/` at repository root
- Paths follow the structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create restack-gen/ directory structure per plan.md with restack_gen/, tests/, and subdirectories
- [X] T002 Initialize Python project with pyproject.toml including Click, Jinja2, Pydantic, restack-ai SDK, google-generativeai dependencies
- [X] T003 [P] Configure pytest in tests/conftest.py with fixtures for temporary project generation
- [X] T004 [P] Setup .gitignore for Python project (\_\_pycache\_\_, .pytest_cache, .env, etc.)
- [X] T005 [P] Create README.md with project description and installation instructions
- [X] T006 [P] Setup requirements.txt and setup.py for pip installation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create base Pydantic models in restack_gen/models/config.py for RetryConfig, TimeoutConfig, LoggingConfig
- [X] T008 [P] Create Project model in restack_gen/models/project.py for project structure representation
- [X] T009 [P] Create Component base model in restack_gen/models/project.py for all generated components
- [X] T010 Implement file operations utilities in restack_gen/utils/file_ops.py (create, read, write, copy)
- [X] T011 [P] Implement validation utilities in restack_gen/utils/validation.py for name validation, syntax checking
- [X] T012 [P] Implement structured logging in restack_gen/utils/logging.py with JSON formatting
- [X] T013 Create base generator class in restack_gen/generators/base.py with template loading and rendering methods
- [X] T014 Setup Jinja2 environment with custom filters in restack_gen/generators/base.py (snake_case, pascal_case, kebab_case)
- [X] T015 Create CLI entry point in restack_gen/cli/main.py using Click framework
- [X] T016 [P] Setup Click command groups and global options in restack_gen/cli/main.py (--verbose, --quiet, --version)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create New Restack Project (Priority: P1) 🎯 MVP

**Goal**: Enable developers to quickly bootstrap a new Restack project with complete scaffolding and sensible defaults

**Independent Test**: Run `restack new test-project` and verify directory structure, configuration files, and runnable project are created

### Implementation for User Story 1

- [X] T017 [P] [US1] Create project template files in `restack_gen/templates/project/` (restack.toml, pyproject.toml, README.md)
- [X] T018 [P] [US1] Create directory structure templates (agents/, workflows/, functions/, tests/) ✅
- [X] T019 [P] [US1] Create requirements.txt template with restack-ai SDK and common dependencies
- [X] T020 [P] [US1] Create CI workflow template `.github/workflows/ci.yml.j2` (pytest + ruff)
- [X] T021 [P] [US1] Create .gitignore template for generated projects
- [X] T022 [US1] Implement ProjectGenerator class in `generators/project.py`
- [X] T023 [US1] Implement project name validation (kebab-case)
- [X] T024 [US1] Directory creation logic with error handling
- [X] T025 [US1] Configuration file generation (restack.toml defaults)
- [X] T026 [US1] `restack new` command implemented
- [X] T027 [US1] Command options (python-version, template, description, no-git); quiet/verbose provided globally
- [X] T028 [US1] Optional Git initialization implemented
- [X] T029 [US1] Success message with emojis
- [X] T030 [US1] Error handling (invalid names, existing dirs)
- [X] T031 [US1] Integration test (`tests/integration/test_cli_new.py`)
- [X] T032 [US1] Project scaffolding validated in tests

**Checkpoint**: At this point, User Story 1 should be fully functional - developers can create new Restack projects

---

## Phase 4: User Story 2 - Generate Individual Components (Priority: P2)

**Goal**: Enable Rails-style generators for agents, workflows, and functions within existing projects

**Independent Test**: In a generated project, run `restack g agent TestAgent`, `restack g workflow TestWorkflow`, and `restack g function TestFunction` to verify component generation

### Implementation for User Story 2

- [X] T033 [P] [US2] Agent template `templates/agents/agent.py.j2`
- [X] T034 [P] [US2] Workflow template `templates/workflows/workflow.py.j2`
- [X] T035 [P] [US2] Function template `templates/functions/function.py.j2`
- [X] T036 [P] [US2] Test templates for agents/workflows/functions
- [X] T037 [US2] AgentGenerator implemented
- [X] T038 [US2] WorkflowGenerator implemented
- [X] T039 [US2] FunctionGenerator implemented
- [X] T040 [US2] Component name validation (PascalCase) using validation utilities
- [X] T041 [US2] Pydantic Input/Output schemas in templates
- [X] T042 [US2] Test file generation logic
- [X] T043 [US2] `generate` command dispatcher group
- [X] T044 [US2] Subcommands agent/workflow/function
- [X] T045 [US2] Component-specific options implemented (description, --with-functions, --timeout, --pure, --no-tests, --force, --dry-run) NOTE: uses `--no-tests` instead of `--with-tests`; no separate --workflows/--functions flags for agents.
- [ ] T049 [US2] Update restack.toml after component generation to register new components (tracks generated agents/workflows/functions; enables doctor validation and autocomplete features)
- [X] T050 [US2] Integration tests (`tests/integration/test_cli_generate.py`)
- [X] T051 [US2] Syntax validation via AST in tests

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - create projects and generate components

---

## Phase 5: User Story 5 - Health Checks and Diagnostics (Priority: P2)

**Goal**: Provide `restack doctor` command for project validation and issue diagnosis

**Independent Test**: Run `restack doctor` in valid and invalid projects to verify diagnostic capabilities

### Implementation for User Story 5

- [X] T052 [P] [US5] Validation rules in `utils/validation.py` for config (extracted: structure, schema, syntax)
- [X] T053 [P] [US5] Syntax validation using `ast` in doctor command
- [X] T054 [P] [US5] Dependency checker (manifest presence + SDK checks; no import-time checks)
- [X] T055 [US5] Doctor command implemented (`cli/commands/doctor.py`) – functional (no class wrapper)
- [X] T056 [US5] Project structure validation
- [X] T057 [US5] restack.toml schema validation (types and ranges for optional sections; presence for required keys)
- [X] T058 [US5] Component syntax validation (agents/workflows/functions)
- [X] T059 [US5] Restack SDK compatibility check (warn if missing/unpinned; error if below minimum)
- [X] T060 [US5] Diagnostic reporting with icons ✅ ⚠️ ❌ and `--json` output
- [X] T061 [US5] `--fix` option for structure repair
- [X] T062 [US5] `--check` TYPE option implemented
- [X] T063 [US5] Dedicated `--verbose` option (doctor-local flag implemented in `cli/commands/doctor.py`) ✅
- [X] T064 [US5] Integration tests (`tests/integration/test_cli_doctor.py`)
- [X] T065 [US5] Reports configuration and structural issues (enhanced)

**Checkpoint**: All P2 user stories complete - projects can be created, components generated, and validated

---

## Phase 6: User Story 3 - Generate Complex Pipelines (Priority: P3)

**Goal**: Enable pipeline generation with operator grammar (sequence, parallel, optional) for v1

**Independent Test**: Run `restack g pipeline TestPipeline --with-operators` and verify operator grammar support for sequence (`→`), parallel (`⇄`), and optional (`→?`)

### Implementation for User Story 3
 
 - [X] T066 [P] [US3] Create Pipeline model in restack_gen/models/project.py with operator definitions
 - [X] T067 [P] [US3] Create PipelineOperator models for sequence, parallel, optional in restack_gen/models/project.py
 - [X] T068 [P] [US3] Create pipeline template in restack_gen/templates/pipelines/pipeline.py.j2 with operator implementations
 - [X] T069 [P] [US3] Create operator composition examples in templates (sequence, parallel, optional patterns) in restack_gen/templates/pipelines/examples/
 - [X] T070 [US3] Implement PipelineGenerator class in restack_gen/generators/pipeline.py extending WorkflowGenerator
 - [X] T071 [US3] Implement operator grammar parser for composition graph validation in restack_gen/generators/pipeline.py
 - [X] T072 [US3] Implement sequence operator generation in pipeline template in restack_gen/templates/pipelines/pipeline.py.j2
 - [X] T073 [US3] Implement parallel operator generation with asyncio.gather semantics in restack_gen/templates/pipelines/pipeline.py.j2
 - [X] T074 [US3] Implement optional operator generation with non-null predicate semantics in restack_gen/templates/pipelines/pipeline.py.j2
 - [X] T075 [US3] Add DAG validation to ensure pipeline is acyclic in restack_gen/generators/pipeline.py
 - [X] T076 [US3] Add --operators option to generate command for pipeline type in restack_gen/cli/commands/generate.py
 - [X] T077 [US3] Add --error-strategy option (halt, continue, retry) for pipeline error handling in restack_gen/cli/commands/generate.py
 - [X] T078 [US3] Implement integration test in tests/integration/test_pipeline_generation.py
 - [X] T079 [US3] Test generated pipelines execute operators in correct order (including parallel and optional semantics) in tests/integration/test_pipeline_generation.py

**Checkpoint**: Pipeline generation complete with operator grammar support

---
### Future Enhancements (Deferred)

The following items are explicitly deferred from the initial US3 scope and will be scheduled in a future phase:

- Loop operator support with max-iterations safety and guardrails
- Conditional branch operators (if/else) with type-safe merging
- Parser/validator and template extensions to support loop/conditional
- Comprehensive tests for loop/conditional semantics and error cases

---

## Phase 7: User Story 4 - LLM Integration and Tool Server Setup (Priority: P3)

**Goal**: Enable LLM integration generation with multi-provider support and prompt versioning

**Independent Test**: Run `restack g llm TestLLM --provider gemini --with-prompts` and verify LLM integration code

### Implementation for User Story 4

- [ ] T080 [P] [US4] Create LLMIntegration model in restack_gen/models/project.py with provider, model, prompts
- [ ] T081 [P] [US4] Create PromptTemplate model for versioned prompts in restack_gen/models/project.py
- [ ] T082 [P] [US4] Create LLM integration template in restack_gen/templates/llm/llm_integration.py.j2
- [ ] T083 [P] [US4] Create Gemini provider template with google-generativeai integration in restack_gen/templates/llm/providers/gemini.py.j2
- [ ] T084 [P] [US4] Create abstract provider interface for multi-provider extensibility in restack_gen/templates/llm/providers/base.py.j2
- [ ] T085 [P] [US4] Create prompt versioning structure templates in restack_gen/templates/llm/prompts/
- [ ] T086 [US4] Implement LLMGenerator class in restack_gen/generators/llm.py extending BaseGenerator
- [ ] T087 [US4] Implement provider-specific code generation (Gemini, OpenAI, Anthropic stubs) in restack_gen/generators/llm.py
- [ ] T088 [US4] Implement prompt template generation with versioning support in restack_gen/generators/llm.py
- [ ] T089 [US4] Add --provider option to generate command for LLM type in restack_gen/cli/commands/generate.py
- [ ] T090 [US4] Add --model option for specific model selection in restack_gen/cli/commands/generate.py
- [ ] T091 [US4] Add --with-prompts flag to include prompt versioning setup in restack_gen/cli/commands/generate.py
- [ ] T092 [US4] Add --max-tokens and --temperature options for LLM configuration in restack_gen/cli/commands/generate.py
- [ ] T093 [P] [US4] Create FastMCP tool server template in restack_gen/templates/llm/fastmcp_server.py.j2
- [ ] T094 [US4] Implement FastMCP tool registration and routing in generated code in restack_gen/templates/llm/fastmcp_server.py.j2
- [ ] T095 [US4] Add FastMCP server configuration to generated restack.toml in restack_gen/templates/project/restack.toml.j2
- [ ] T096 [US4] Implement integration test for FastMCP tool server in tests/integration/test_fastmcp.py
- [ ] T097 [US4] Add LLM provider API key validation in generated code in restack_gen/templates/llm/llm_integration.py.j2
- [ ] T098 [US4] Implement integration test in tests/integration/test_llm_generation.py
- [ ] T099 [US4] Test multi-provider support and prompt versioning structure in tests/integration/test_llm_generation.py

**Checkpoint**: All P3 user stories complete - full CLI functionality available

---

## Phase 8: Additional Commands

**Purpose**: Remaining CLI commands for complete feature set

- [ ] T100 [P] Create Migration model in restack_gen/models/migration.py with up/down methods
- [ ] T101 [P] Create MigrationManager in restack_gen/migrations/manager.py for migration execution
- [ ] T102 [P] Implement migration file generation with timestamp-based naming in restack_gen/migrations/manager.py
- [ ] T103 [P] Implement migration history tracking in .restack/migrations.json
- [ ] T104 Implement `restack run:server` command in restack_gen/cli/commands/server.py
- [ ] T105 Add server options: --port, --host, --workers, --reload, --env in restack_gen/cli/commands/server.py
- [ ] T106 Implement development server startup with auto-reload support in restack_gen/cli/commands/server.py
- [ ] T107 Implement health check endpoint for server validation in restack_gen/cli/commands/server.py
- [ ] T108 [P] Add integration test for server command in tests/integration/test_server.py

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T109 [P] Create comprehensive CLI documentation in README.md at repository root
- [ ] T110 [P] Add command examples and usage patterns to quickstart.md in specs/001-restack-gen-cli/quickstart.md
- [ ] T111 [P] Implement --json output format for all commands (for scripting) in restack_gen/cli/main.py
- [ ] T112 [P] Add shell completion support (bash, zsh, fish) using Click in restack_gen/cli/main.py
- [ ] T113 Implement error message improvements with actionable suggestions in restack_gen/cli/commands/generate.py
- [ ] T114 Add emoji and color formatting for CLI output using Click styling in restack_gen/cli/main.py
- [ ] T115 [P] Create template version checking for backward compatibility in restack_gen/generators/base.py
- [ ] T116 [P] Implement template caching for performance optimization in restack_gen/generators/base.py
- [ ] T117 Performance testing for <10 second component generation, <2 minute project creation in tests/performance/test_cli_performance.py
- [ ] T118 [P] Add comprehensive unit tests in tests/unit/ for all generators and utilities
- [ ] T119 Run quickstart.md validation and update with actual CLI usage in specs/001-restack-gen-cli/quickstart.md
- [X] T120 [P] Create CLI installation guide and troubleshooting documentation in docs/installation.md
- [X] T121 Security audit of file operations and template rendering in docs/security-audit.md
- [ ] T122 Add rate limiting for LLM API calls in generated code in restack_gen/templates/llm/llm_integration.py.j2
- [ ] T123 [P] [EC-001, EC-006] Test directory permission failures and existing file conflicts with --force/--skip options in tests/integration/test_edge_cases.py
- [ ] T124 [P] [EC-004] Test LLM service unavailability and API key validation failures with graceful degradation in tests/integration/test_edge_cases.py
- [ ] T125 [P] [EC-002] Test invalid generator component names (reserved keywords, special characters, lowercase) with validation messages in tests/integration/test_edge_cases.py
- [ ] T126 [P] [EC-005] Test migration version conflicts and rollback scenarios with conflict detection in tests/integration/test_edge_cases.py
- [ ] T127 [P] [EC-003] Test missing/corrupted template handling with recovery options in tests/integration/test_edge_cases.py
- [ ] T128 [EC-001] Implement rollback mechanism for failed project creation (clean up partial artifacts) in restack_gen/generators/project.py
- [ ] T129 [EC-002] Add name validation with Python keyword checking and suggestions in restack_gen/utils/validation.py
- [ ] T130 [EC-006] Implement conflict resolution prompts with --force/--rename/--skip options
- [ ] T131 [EC-004] Add graceful degradation for LLM unavailability with TODO comment generation in restack_gen/templates/llm/llm_integration.py.j2

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 (P1) → US2, US5 (P2) → US3, US4 (P3)
- **Additional Commands (Phase 8)**: Can proceed in parallel with user stories or after
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Requires US1 for project context but independently testable
- **User Story 5 (P2)**: Can start after Foundational - Requires US1 for project validation but independently testable
- **User Story 3 (P3)**: Can start after US2 (extends workflow generation) but independently testable
- **User Story 4 (P3)**: Can start after Foundational - Independently testable

### Within Each User Story

- Template files before generator implementation
- Generator classes before CLI commands
- Core implementation before integration
- Integration tests after implementation complete
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, multiple user stories can be worked on in parallel (if team capacity allows)
- Template creation within each story can be done in parallel
- Test creation can proceed in parallel with implementation

---

## Parallel Example: User Story 2

```bash
# Launch all templates for User Story 2 together:
Task: "Create agent template in restack_gen/templates/agents/agent.py.j2"
Task: "Create workflow template in restack_gen/templates/workflows/workflow.py.j2"
Task: "Create function template in restack_gen/templates/functions/function.py.j2"
Task: "Create test templates for agents, workflows, functions"

# Then implement generators in parallel:
Task: "Implement AgentGenerator class in restack_gen/generators/agent.py"
Task: "Implement WorkflowGenerator class in restack_gen/generators/workflow.py"
Task: "Implement FunctionGenerator class in restack_gen/generators/function.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test `restack new` command independently
5. Deploy/demo CLI with project creation only

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Release v0.1 (MVP - project creation!)
3. Add User Story 2 → Test independently → Release v0.2 (add component generators)
4. Add User Story 5 → Test independently → Release v0.3 (add diagnostics)
5. Add User Stories 3 & 4 → Test independently → Release v1.0 (full feature set)
6. Each story adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (project creation)
   - Developer B: User Story 2 (component generators)
   - Developer C: User Story 5 (diagnostics)
3. P3 stories (pipelines, LLM) can proceed after P2 completion
4. Stories integrate independently without blocking each other

---

## Total Task Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 10 tasks (BLOCKING)
- **Phase 3 (US1 - P1)**: 16 tasks
- **Phase 4 (US2 - P2)**: 19 tasks
- **Phase 5 (US5 - P2)**: 14 tasks
- **Phase 6 (US3 - P3)**: 14 tasks
- **Phase 7 (US4 - P3)**: 20 tasks
- **Phase 8 (Additional)**: 9 tasks
- **Phase 9 (Polish)**: 18 tasks

**Total Tasks**: 126 tasks

**Parallel Opportunities**: 48 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-3 (32 tasks) delivers working project creation CLI

**Independent Test Criteria**:
- US1: `restack new test-project` creates runnable project
- US2: `restack g agent/workflow/function` generates valid components
- US5: `restack doctor` validates and diagnoses projects
- US3: `restack g pipeline --with-operators` generates complex pipelines
- US4: `restack g llm --provider gemini` generates LLM integrations

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story (US1-US5) for traceability
- Each user story should be independently completable and testable
- All generated code must include tests (per FR-011)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Test-first development: ensure generated tests fail before implementing components