# Tasks: Python TypeSpec Code Generation Tooling

**Input**: Design documents from `/specs/34167-python-typespec-codegen/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/makefile-interface.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Configure the TypeSpec Python emitter in the existing project

- [x] T001 Add `@azure-tools/typespec-python` emitter and options to type_spec/tspconfig.yaml
- [x] T002 Create the Makefile skeleton at Makefile with default variables (OUTPUT_DIR, TYPESPEC_DIR)

**Checkpoint**: tspconfig.yaml has Python emitter config; Makefile exists with variable declarations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: There are no foundational blocking tasks for this feature — each user story target is independent.

**⚠️ NOTE**: All three Makefile targets (US1, US2, US3) are independent of each other. The Setup phase (tspconfig.yaml + Makefile skeleton) must complete first, but then all user stories can proceed in parallel.

**Checkpoint**: Setup complete — user story implementation can begin

---

## Phase 3: User Story 1 — Generate Python Models from TypeSpec Definitions (Priority: P1) 🎯 MVP

**Goal**: `make generate-models` compiles TypeSpec definitions into Python model classes in `azure/ai/responses/server/_generated/`

**Independent Test**: Run `make generate-models` in a clean environment with `tsp-client` installed; verify Python model files are generated in the output directory without errors.

### Implementation for User Story 1

- [x] T003 [US1] Implement the `generate-models` target in Makefile — validate `tsp-client` is on PATH, run `tsp-client generate` from the TYPESPEC_DIR, and print an actionable error if tsp-client is missing
- [ ] T004 [US1] Verify idempotency — run `make generate-models` twice on unchanged input and confirm output is identical *(deferred: requires Node.js + tsp-client)*

**Checkpoint**: `make generate-models` produces Python model files in `azure/ai/responses/server/_generated/`

---

## Phase 4: User Story 2 — Clean and Regenerate Models (Priority: P2)

**Goal**: `make clean` removes all previously generated Python model files; `make clean generate-models` performs a full clean regeneration

**Independent Test**: Generate models, add a spurious file to `_generated/`, run `make clean`, verify all files (including spurious) are removed. Then `make generate-models` and verify a fresh set is produced.

### Implementation for User Story 2

- [x] T005 [P] [US2] Implement the `clean` target in Makefile — remove the OUTPUT_DIR directory and all contents; succeed silently if directory does not exist
- [ ] T006 [US2] Verify clean + regenerate workflow — run `make clean generate-models` and confirm output matches a first-time generation with zero stale artifacts *(deferred: requires Node.js + tsp-client)*

**Checkpoint**: `make clean` removes generated output; `make clean generate-models` produces a fresh identical set

---

## Phase 5: User Story 3 — Install Prerequisites for Code Generation (Priority: P2)

**Goal**: `make install-typespec-deps` installs `tsp-client` CLI globally and syncs TypeSpec source files into `TempTypeSpecFiles/`

**Independent Test**: On a machine with Node.js but no `tsp-client`, run `make install-typespec-deps`, then verify `tsp-client --version` succeeds and `type_spec/TempTypeSpecFiles/` is populated.

### Implementation for User Story 3

- [x] T007 [P] [US3] Implement the `install-typespec-deps` target in Makefile — validate Node.js/npm are available, install `@azure-tools/typespec-client-generator-cli` globally via npm, run `tsp-client sync` from TYPESPEC_DIR, and print an actionable error if Node.js is missing
- [ ] T008 [US3] Verify re-run safety — run `make install-typespec-deps` when prerequisites are already installed and confirm it completes without errors *(deferred: requires Node.js + npm)*

**Checkpoint**: `make install-typespec-deps` installs tooling and syncs TypeSpec sources

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T009 [P] Run `make generate-models` end-to-end and verify generated Python files pass ruff check and mypy type-checking without manual edits *(deferred: requires Node.js + tsp-client + make)*
- [ ] T010 [P] Verify the quickstart workflow from specs/34167-python-typespec-codegen/quickstart.md — confirm a developer can go from fresh clone to generated models following the documented steps *(deferred: requires Node.js + make)*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: N/A — no blocking prerequisites beyond Setup
- **User Stories (Phase 3-5)**: All depend on Setup (Phase 1) completion
  - US1 (generate-models), US2 (clean), US3 (install-deps) can proceed in parallel
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Setup (T001, T002). No dependencies on other stories.
- **User Story 2 (P2)**: Depends on Setup (T001, T002). Can run in parallel with US1 and US3.
- **User Story 3 (P2)**: Depends on Setup (T001, T002). Can run in parallel with US1 and US2.

### Within Each User Story

- Implementation before verification
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 (Setup) are sequential (T002 depends on T001 for tspconfig context)
- T003, T005, T007 (core implementation of each target) can run in parallel after Setup
- T009 and T010 (Polish) can run in parallel

---

## Parallel Example: User Story Targets

```text
# After Setup completes, launch all three target implementations in parallel:
Task T003: "Implement generate-models target in Makefile"
Task T005: "Implement clean target in Makefile"
Task T007: "Implement install-typespec-deps target in Makefile"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 3: User Story 1 — generate-models (T003, T004)
3. **STOP and VALIDATE**: Run `make generate-models` and verify output
4. Deploy/demo if ready — developer can now generate Python models

### Incremental Delivery

1. Setup → tspconfig.yaml + Makefile skeleton ready
2. Add US1 (generate-models) → Test independently → Core value delivered (MVP!)
3. Add US2 (clean) → Test independently → Clean regeneration enabled
4. Add US3 (install-typespec-deps) → Test independently → Onboarding streamlined
5. Polish → Linting/type-checking validation, quickstart verification

### Single Developer Strategy

Since all tasks modify a single file (Makefile) plus one config file:

1. Complete Setup (T001, T002)
2. Implement all targets sequentially (T003 → T005 → T007)
3. Run verifications (T004, T006, T008)
4. Polish (T009, T010)

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story corresponds to one Makefile target and is independently testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
