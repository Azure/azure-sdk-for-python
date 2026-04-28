---

description: "Task list for feature implementation"
---

# Tasks: Transparent Fabric Mirror Query Mapping

**Input**: Design documents from `specs/001-fabric-mirror-mapper/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), plus `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Included (required by constitution: golden translation, result mapping, redaction; integration tests are opt-in).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Driver Strategy Update (2026-01-30)**: Tasks updated to reflect `mssql-python` as primary SQL driver (pure Python, no system dependencies on Windows) with `pyodbc` as legacy support. See [research/python-sql-driver-options.md](research/python-sql-driver-options.md).

**Key Task Additions**:
- T013a: Create mssql-python driver adapter (primary)
- T045-T051: Driver migration tasks (implementation, testing, validation, benchmarking)
- T043a-T043b: Driver integration and comparison tests
- Updated T032, T036, T044: Reflect dual-driver support

**Status Summary**:
- ✅ **Phases 1-2 Complete**: Setup and Foundational infrastructure (currently uses pyodbc)
- ✅ **Phase 3 (~95% Complete)**: US1 core functionality implemented (missing T029)
- ⏳ **Phase 4-5 Pending**: US2 credential pass-through, US3 SDK integration docs
- 🔄 **Phase 6 Refactoring**: Refactor existing pyodbc implementation to use mssql-python as primary driver (T045-T051) - **Complete before first release**
- 📊 **Total Tasks**: 51 (was 44), 29 complete, 22 remaining (including refactoring tasks)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python package, tooling, and repository structure.

- [X] T001 Create Python package skeleton in pyproject.toml and src/azure_cosmos_fabric_mapper/__init__.py
- [X] T002 [P] Add base documentation files README.md and CHANGELOG.md
- [X] T003 [P] Create test scaffolding tests/unit/__init__.py and tests/integration/__init__.py
- [X] T004 [P] Add pytest configuration in pyproject.toml (tool.pytest.ini_options)
- [X] T005 [P] Add packaging metadata and optional dependency groups for mssql-python (primary) and pyodbc (legacy) in pyproject.toml
- [X] T006 [P] Add parser dependency lark to pyproject.toml
- [X] T007 Add CI workflow to run unit tests in .github/workflows/python-ci.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core primitives required by all user stories.

**Checkpoint**: Foundation ready → user story implementation can begin.

- [X] T008 Create error taxonomy in src/azure_cosmos_fabric_mapper/errors.py
- [X] T009 [P] Implement redaction utilities and safe diagnostics helpers in src/azure_cosmos_fabric_mapper/diagnostics.py
- [X] T010 [P] Define MirrorServingConfiguration and validation in src/azure_cosmos_fabric_mapper/config.py
- [X] T011 [P] Define CredentialSource abstractions in src/azure_cosmos_fabric_mapper/credentials.py
- [X] T012 [P] Define DB-API 2.0 compliant driver protocol and result set types in src/azure_cosmos_fabric_mapper/driver/base.py
- [X] T013 [P] Create legacy pyodbc adapter stub with graceful import handling in src/azure_cosmos_fabric_mapper/driver/pyodbc_driver.py- [ ] T013a [P] Create primary mssql-python driver adapter with graceful import handling in src/azure_cosmos_fabric_mapper/driver/mssql_driver.py- [X] T014 Create translation package skeleton in src/azure_cosmos_fabric_mapper/translate/__init__.py and src/azure_cosmos_fabric_mapper/translate/ast.py
- [X] T015 Create result mapping skeleton in src/azure_cosmos_fabric_mapper/results/__init__.py and src/azure_cosmos_fabric_mapper/results/mapper.py
- [X] T016 Create SDK hook skeleton in src/azure_cosmos_fabric_mapper/sdk_hook/__init__.py and src/azure_cosmos_fabric_mapper/sdk_hook/contract.py

---

## Phase 3: User Story 1 - Run Existing Cosmos Queries Against a Fabric Mirror (Priority: P1) 🎯 MVP

**Goal**: Translate a supported Cosmos SQL subset into driver-ready SQL, execute it via a driver client, and map results back to Cosmos-like items.

**Independent Test**: Run a set of at least 10 representative Cosmos-style queries through the mapper (using a stub driver) and validate deterministic translation + correct mapped results.

### Tests (required)

- [X] T017 [P] [US1] Add golden translation fixtures in tests/unit/fixtures/golden_queries.json
- [X] T018 [P] [US1] Implement golden translation tests in tests/unit/test_translation_golden.py
- [X] T019 [P] [US1] Implement parameterization tests (no literal interpolation) in tests/unit/test_parameterization.py
- [X] T020 [P] [US1] Implement result mapping contract tests in tests/unit/test_result_mapping.py

### Implementation

- [X] T021 [P] [US1] Implement Cosmos SQL subset grammar in src/azure_cosmos_fabric_mapper/translate/parser.py
- [X] T022 [P] [US1] Implement AST node types for supported subset in src/azure_cosmos_fabric_mapper/translate/ast.py
- [X] T023 [US1] Implement parser → AST construction in src/azure_cosmos_fabric_mapper/translate/parser.py (depends on T021, T022)
- [X] T024 [P] [US1] Implement parameter mapping Cosmos → driver params in src/azure_cosmos_fabric_mapper/translate/parameters.py
- [X] T025 [P] [US1] Implement AST → Fabric SQL emitter (parameterized) in src/azure_cosmos_fabric_mapper/translate/fabric_sql.py
- [X] T026 [US1] Implement top-level translate API in src/azure_cosmos_fabric_mapper/translate/__init__.py (depends on T023, T024, T025)
- [X] T027 [P] [US1] Implement driver execution wrapper using DriverClient protocol in src/azure_cosmos_fabric_mapper/driver/__init__.py
- [X] T028 [US1] Implement row/column → Cosmos-like document mapping in src/azure_cosmos_fabric_mapper/results/mapper.py
- [ ] T029 [US1] Implement end-to-end “translate→execute→map” helper in src/azure_cosmos_fabric_mapper/sdk_hook/contract.py

**Checkpoint**: User Story 1 works end-to-end with a stub driver.

---

## Phase 4: User Story 2 - Pass Through Credentials Securely (Priority: P2)

**Goal**: Allow users to configure credentials/connection settings once and safely pass them into the driver connection layer.

**Independent Test**: Configure mirror serving with a credential source and ensure (a) driver connect is invoked with the credential inputs and (b) no secrets appear in logs/errors.

### Tests (required)

- [ ] T030 [P] [US2] Add redaction tests ensuring secrets never appear in diagnostics/log strings in tests/unit/test_redaction.py
- [ ] T031 [P] [US2] Add credential validation tests for config parsing in tests/unit/test_config_credentials.py

### Implementation

- [ ] T032 [US2] Implement credential pass-through behavior in both driver adapters:
  - src/azure_cosmos_fabric_mapper/driver/mssql_driver.py (primary)
  - src/azure_cosmos_fabric_mapper/driver/pyodbc_driver.py (legacy)
- [ ] T033 [US2] Implement secure diagnostic payload construction in src/azure_cosmos_fabric_mapper/diagnostics.py
- [ ] T034 [US2] Enforce “no secrets in exceptions” policy in src/azure_cosmos_fabric_mapper/errors.py
- [ ] T035 [US2] Update SDK hook contract to accept MirrorServingConfiguration and CredentialSource in src/azure_cosmos_fabric_mapper/sdk_hook/contract.py

**Checkpoint**: Credentials are accepted and passed through safely; failures are informative but non-leaking.

---

## Phase 5: User Story 3 - Safe Optional Install and Clear Failure Modes (Priority: P3)

**Goal**: Ensure the Cosmos SDK can integrate with the mapper without a hard dependency, and provide clear instructions + error behavior when the mapper is absent.

**Independent Test**: Validate that the mapper package exposes a stable hook entry point and error types; validate documentation for minimal SDK patch is complete and unambiguous.

### Documentation deliverables (required)

- [X] T036 [US3] Expand installation and activation docs in README.md (include mssql-python as primary driver, migration guide from pyodbc, optional dependency story + safety guarantees)
- [ ] T037 [US3] Refine Cosmos SDK patch guidance with concrete code snippets in specs/001-fabric-mirror-mapper/contracts/sdk-integration.md
- [ ] T038 [US3] Add a “compatibility & limitations” section to README.md describing supported Cosmos SQL subset and failure behavior

### Mapper-side contract stabilization

- [ ] T039 [US3] Define a stable hook function signature and re-export it in src/azure_cosmos_fabric_mapper/sdk_hook/__init__.py
- [ ] T040 [US3] Ensure all mapper public errors are exported in src/azure_cosmos_fabric_mapper/__init__.py

**Checkpoint**: SDK integration guidance is copy/paste-able; mapper exposes a stable import path.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements affecting multiple stories.

### Driver Migration (New - 2026-01-30)

**Purpose**: Refactor existing pyodbc implementation to use mssql-python as primary driver **before first release**.

**Context**: The current implementation uses pyodbc. Since we haven't released yet, we should refactor to use mssql-python as primary (better UX, no system driver on Windows) before v0.1.0 release.

- [ ] T045 [P] Implement MssqlDriverClient in src/azure_cosmos_fabric_mapper/driver/mssql_driver.py matching DB-API 2.0 interface (similar to existing PyOdbcDriverClient)
- [ ] T046 [P] Update driver selection logic to prefer mssql-python when available in src/azure_cosmos_fabric_mapper/driver/__init__.py
- [ ] T047 Add unit tests for mssql-python driver adapter in tests/unit/test_mssql_driver.py
- [ ] T048 Validate connection string compatibility between mssql-python and pyodbc drivers
- [ ] T049 Test Microsoft Entra ID authentication with mssql-python driver (ActiveDirectoryInteractive, MSI, ServicePrincipal)
- [ ] T050 Update CHANGELOG.md to reflect mssql-python as primary driver from initial release
- [ ] T051 Benchmark query performance: mssql-python vs pyodbc (validate no regression)

### Documentation & Quality

### Documentation & Quality

- [ ] T041 [P] Document unsupported query constructs and recommended alternatives in specs/001-fabric-mirror-mapper/contracts/python-api.md
- [ ] T042 Add a compatibility matrix stub to README.md (Cosmos SDK versions × mapper versions × feature subset + driver options)
- [ ] T043 Add opt-in integration test harness skeleton in tests/integration/test_driver_roundtrip.py (skipped by default)
- [ ] T043a [P] Add mssql-python driver integration tests in tests/integration/test_mssql_driver.py (validates against Fabric SQL endpoint)
- [ ] T043b [P] Add driver comparison tests to validate DB-API 2.0 compliance parity between mssql-python and pyodbc
- [ ] T044 Run quickstart validation steps and update specs/001-fabric-mirror-mapper/quickstart.md with concrete examples (using mssql-python)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion → BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependencies beyond Foundational
- **US2 (P2)**: Builds on US1 plumbing but remains independently testable with driver stubs
- **US3 (P3)**: Documentation + contract stabilization; independent of mirror endpoint availability

## Parallel Execution Examples

### US1 parallel work

- Grammar + AST can be built in parallel:
  - T021 (parser grammar) and T022 (AST types)
- Tests can be authored in parallel once fixtures exist:
  - T018, T019, T020 after T017

### US2 parallel work

- T030 (redaction tests) and T031 (credential config tests) can run in parallel.

### US3 parallel work

- T036 (README) and T037 (SDK integration doc) can run in parallel.

## Implementation Strategy

### Current Status (Pre-Release)

The implementation is **complete locally but not yet released**. Current code uses pyodbc as the driver.

### Refactoring Before Release

**Before first release (v0.1.0 or v1.0.0)**, complete driver refactoring:

1. ✅ **Already Complete**: Phases 1-3 core functionality (with pyodbc)
2. 🔄 **Refactor Now**: Implement mssql-python adapter (T045-T051)
3. ⏭️ **Complete**: Remaining user stories (US2, US3)
4. 🚀 **Release**: First version with mssql-python as primary, pyodbc as legacy option

**Why refactor now (pre-release)**:
- No breaking changes for users (nobody using it yet)
- Much better installation UX from day one (no system ODBC driver on Windows)
- Simpler documentation (recommend `[sql]` from the start)
- Official Microsoft driver with Fabric SQL support

### Task Order

1. Complete outstanding user stories (T029-T040) 
2. Refactor driver implementation (T045-T051) ← **Do this before release**
3. Final polish (T041-T044)
4. Release v1.0.0 with mssql-python as primary driver

**Result**: First release ships with `mssql-python` as the recommended driver, `pyodbc` as optional legacy support.
