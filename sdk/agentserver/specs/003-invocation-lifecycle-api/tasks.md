# Tasks: Durable Task Lifecycle Automation & Public API Simplification

**Input**: Design documents from `/specs/003-invocation-lifecycle-api/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/public-api.md ✅, quickstart.md ✅

**Tests**: Included — spec explicitly requires unit tests (US1–US3 acceptance scenarios) and e2e tests (US4–US5).

**Organization**: Tasks grouped by implementation phase (which maps 1:1 to user stories). Phases 2–3 are foundational (P1), Phase 4 is polish (P1), Phase 5 is samples (P2).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths based on plan.md project structure

## Path Conventions

```
azure-ai-agentserver-core/
├── azure/ai/agentserver/core/durable/
│   ├── __init__.py
│   ├── _context.py
│   ├── _decorator.py
│   ├── _exceptions.py
│   ├── _manager.py
│   └── _models.py
└── tests/durable/
    ├── test_entry_mode.py          # NEW
    ├── test_lifecycle.py           # NEW
    ├── test_get.py                 # NEW
    └── test_sample_e2e.py          # MODIFY

azure-ai-agentserver-invocations/
└── samples/
    ├── durable_multiturn/durable_multiturn.py   # MODIFY
    └── durable_langgraph/durable_langgraph.py   # MODIFY
```

---

## Phase 1: Baseline (Shared Infrastructure)

**Purpose**: Verify existing tests pass before any changes. Establish baseline.

- [ ] T001 [US1,US2,US3] Run full test suite (`pytest azure-ai-agentserver-core/tests/durable/`) and confirm all 198 existing tests pass. Record baseline.

**Checkpoint**: Baseline green. All subsequent changes must keep it green.

---

## Phase 2: Entry Mode — US2 (Priority: P1, Foundational) 🎯

**Goal**: `TaskContext.entry_mode` returns `"fresh"`, `"resumed"`, or `"recovered"` so the durable function knows why it was entered.

**Independent Test**: A durable task function reads `ctx.entry_mode` and gets the correct value for each lifecycle path — fresh start, developer-initiated resume, platform-initiated resume, and crash recovery.

### Tests for US2

> **Write these tests FIRST — ensure they FAIL before implementation.**

- [ ] T002 [P] [US2] Unit test: fresh start → `ctx.entry_mode == "fresh"` in `tests/durable/test_entry_mode.py`
- [ ] T003 [P] [US2] Unit test: developer-initiated resume (`.run()` on suspended task) → `ctx.entry_mode == "resumed"`, `ctx.input` has new data, in `tests/durable/test_entry_mode.py`
- [ ] T004 [P] [US2] Unit test: platform-initiated resume (via `handle_resume()`) → `ctx.entry_mode == "resumed"`, `ctx.input` has persisted input, in `tests/durable/test_entry_mode.py`
- [ ] T005 [P] [US2] Unit test: stale task recovery → `ctx.entry_mode == "recovered"` in `tests/durable/test_entry_mode.py`
- [ ] T006 [P] [US2] Unit test: ignoring `entry_mode` works fine (function doesn't check it, still runs correctly) in `tests/durable/test_entry_mode.py`

### Implementation for US2

- [ ] T007 [US2] Add `EntryMode` type alias (`Literal["fresh", "resumed", "recovered"]`) to `azure/ai/agentserver/core/durable/_context.py`
- [ ] T008 [US2] Add `"entry_mode"` to `TaskContext.__slots__` and `__init__` (default `"fresh"`) in `azure/ai/agentserver/core/durable/_context.py` (depends on T007)
- [ ] T009 [US2] Wire `entry_mode="fresh"` through `create_and_run` / `create_and_start` paths in `azure/ai/agentserver/core/durable/_manager.py` (depends on T008)
- [ ] T010 [US2] Wire `entry_mode="resumed"` through `handle_resume()` in `azure/ai/agentserver/core/durable/_manager.py` — covers BOTH developer-initiated and platform-initiated resume paths (depends on T008)
- [ ] T011 [US2] Wire `entry_mode="recovered"` through stale task recovery path in `azure/ai/agentserver/core/durable/_manager.py` (depends on T008)
- [ ] T012 [US2] Run all tests: new entry_mode tests pass (T002–T006), existing 198 tests still pass, Black formatting passes

**Checkpoint**: `ctx.entry_mode` works in all paths. US2 is independently testable and complete. Foundation ready for US1.

---

## Phase 3: Lifecycle Automation — US1 (Priority: P1, Core Feature)

**Goal**: `.run()` and `.start()` become lifecycle-aware — they atomically start, resume, or recover based on task state. `.get(task_id)` returns full persisted `TaskInfo`. No manual lifecycle code needed.

**Independent Test**: Call `.run(task_id=..., input=...)` three times on a task that suspends each turn. First call starts fresh, second/third automatically resume. Developer writes zero lifecycle code.

**Depends on**: Phase 2 (entry mode signaling)

### Tests for US1

> **Write these tests FIRST — ensure they FAIL before implementation.**

- [ ] T013 [P] [US1] Unit test: `.run()` on non-existent task → creates and starts, `entry_mode="fresh"` in `tests/durable/test_lifecycle.py`
- [ ] T014 [P] [US1] Unit test: `.run()` on `pending` task → starts it, `entry_mode="fresh"` in `tests/durable/test_lifecycle.py`
- [ ] T015 [P] [US1] Unit test: `.run()` on `suspended` task → patches input and resumes, `entry_mode="resumed"` in `tests/durable/test_lifecycle.py`
- [ ] T016 [P] [US1] Unit test: `.run()` on `in_progress` (not stale) task → raises `TaskConflictError(task_id, "in_progress")` in `tests/durable/test_lifecycle.py`
- [ ] T017 [P] [US1] Unit test: `.run()` on stale `in_progress` task → recovers, `entry_mode="recovered"` in `tests/durable/test_lifecycle.py`
- [ ] T018 [P] [US1] Unit test: `.run()` on `completed` task → raises `TaskConflictError(task_id, "completed")` in `tests/durable/test_lifecycle.py`
- [ ] T019 [P] [US1] Unit test: `.start()` follows same lifecycle rules as `.run()` (at least fresh + resume + conflict cases) in `tests/durable/test_lifecycle.py`
- [ ] T020 [P] [US1] Unit test: `stale_timeout` parameter controls stale detection threshold in `tests/durable/test_lifecycle.py`
- [ ] T021 [P] [US1] Unit test: `.get(task_id)` returns `TaskInfo` for existing task in `tests/durable/test_get.py`
- [ ] T022 [P] [US1] Unit test: `.get(task_id)` returns `None` for non-existent task in `tests/durable/test_get.py`
- [ ] T023 [P] [US1] Unit test: `.get(task_id)` returns correct info for any state (suspended, in_progress, completed) in `tests/durable/test_get.py`

### Implementation for US1

- [ ] T024 [US1] Add `TaskConflictError(RuntimeError)` with `task_id`, `current_status`, `__slots__` to `azure/ai/agentserver/core/durable/_exceptions.py`
- [ ] T025 [US1] Add `_is_stale(task, timeout)` helper to `azure/ai/agentserver/core/durable/_decorator.py` (depends on T024)
- [ ] T026 [US1] Add shared `_resolve_lifecycle()` helper that implements the lifecycle state machine (check status → branch → return action) in `azure/ai/agentserver/core/durable/_decorator.py` (depends on T024, T025)
- [ ] T027 [US1] Modify `.run()` in `DurableTask` to call `_resolve_lifecycle()` before execution — add `stale_timeout` param, keep return type `Output` unchanged in `azure/ai/agentserver/core/durable/_decorator.py` (depends on T026)
- [ ] T028 [US1] Modify `.start()` in `DurableTask` to call `_resolve_lifecycle()` before execution — add `stale_timeout` param, keep return type `TaskRun[Output]` unchanged in `azure/ai/agentserver/core/durable/_decorator.py` (depends on T026)
- [ ] T029 [US1] Add `.get(task_id) -> TaskInfo | None` method to `DurableTask` in `azure/ai/agentserver/core/durable/_decorator.py`
- [ ] T030 [US1] Run all tests: new lifecycle tests pass (T013–T023), entry_mode tests still pass (T002–T006), existing 198 tests still pass, Black passes

**Checkpoint**: Lifecycle automation and `.get()` work. US1 + US2 are complete. Core functionality done.

---

## Phase 4: Public API Surface — US3 (Priority: P1, Polish)

**Goal**: All new types publicly exported. Developer can write a complete handler using only `from azure.ai.agentserver.core.durable import ...` — no private module imports.

**Independent Test**: Write a handler that uses `durable_task`, `TaskContext`, `TaskConflictError`, `EntryMode`, `TaskInfo` — all imported from public surface. Zero private module imports.

**Depends on**: Phases 2–3 (types must exist)

### Implementation for US3

- [ ] T031 [P] [US3] Add imports and exports for `EntryMode`, `TaskConflictError`, `TaskInfo` to `azure/ai/agentserver/core/durable/__init__.py` — update `__all__`, update module docstring's `Public API` block
- [ ] T032 [P] [US3] Re-export `EntryMode`, `TaskConflictError`, `TaskInfo` from `azure/ai/agentserver/core/__init__.py`
- [ ] T033 [US3] Audit: verify a developer can write a complete multi-turn handler using ONLY `from azure.ai.agentserver.core.durable import durable_task, TaskContext` (plus new types as needed). No imports from `_manager`, `_models`, `_local_provider`, `_exceptions`. Document findings.
- [ ] T034 [US3] Run all tests + Black. Confirm no regressions.

**Checkpoint**: Public API surface is clean and complete. US1–US3 (all P1 stories) done.

---

## Phase 5: Samples & E2E Tests — US4, US5 (Priority: P2)

**Goal**: Rewrite both durable samples to use lifecycle-aware `.run()` API. Handler ≤10 lines, zero private imports. E2E tests prove crash resilience.

**Independent Test**: Run each sample, send 3 turns via curl, kill process mid-turn, restart — conversation resumes.

**Depends on**: Phases 2–4 (all core changes complete)

### Implementation for US4 (LangGraph Sample)

- [ ] T035 [US4] Rewrite `azure-ai-agentserver-invocations/samples/durable_langgraph/durable_langgraph.py`:
  - Handler ≤10 lines
  - Uses `await langgraph_task.run(task_id=..., input=...)` for lifecycle
  - Uses `ctx.entry_mode` for fresh vs resumed branching
  - `SqliteSaver` for graph checkpoints
  - Zero private module imports
  - Comment: "This is ONE composition pattern — not the only one"

### Implementation for US5 (Multiturn Sample)

- [ ] T036 [P] [US5] Rewrite `azure-ai-agentserver-invocations/samples/durable_multiturn/durable_multiturn.py`:
  - Handler ≤10 lines
  - Uses `await session_task.run(task_id=..., input=...)` for lifecycle
  - Uses `ctx.entry_mode` for fresh vs resumed branching
  - FileCheckpointStore with atomic writes
  - Zero private module imports
  - Comment: "This is ONE composition pattern — not the only one"

### E2E Tests for US4 + US5

- [ ] T037 [US4,US5] Update `azure-ai-agentserver-core/tests/durable/test_sample_e2e.py`:
  - Rewrite `TestMultiturnSampleE2E` to use new API (inline logic, not sample imports)
  - Rewrite `TestLangGraphSampleE2E` to use new API (inline logic, not sample imports)
  - Add test: crash recovery — stale task → `entry_mode="recovered"`
  - Add test: per-turn output is separate (developer composition)
  - All tests use inline logic per constitution (no sample file imports)

### Final Validation

- [ ] T038 [US1–US5] Run full test suite: all new tests pass, all 198 existing tests pass
- [ ] T039 [US1–US5] Run Black on all modified files
- [ ] T040 [US1–US5] Verify success criteria:
  - SC-001: LangGraph handler ≤10 lines ✓
  - SC-002: Multiturn handler ≤10 lines ✓
  - SC-003: Zero private module imports in samples ✓
  - SC-004: Both samples survive crash + resume (e2e test) ✓
  - SC-005: Core types have zero protocol-specific fields ✓
  - SC-006: `entry_mode` correct in all paths (unit tests) ✓
  - SC-007: mypy strict + pyright pass ✓

**Checkpoint**: All user stories complete. All success criteria met. Feature ready for review.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Baseline)
  └─► Phase 2 (Entry Mode — US2)
        └─► Phase 3 (Lifecycle — US1)
              └─► Phase 4 (Public API — US3)
                    └─► Phase 5 (Samples — US4, US5)
```

### Within Each Phase

1. **Tests FIRST** — write tests, confirm they FAIL
2. **Implementation** — make tests pass
3. **Validation** — existing tests still green, Black passes
4. **Checkpoint** — verify phase is independently complete

### Parallel Opportunities

- All tests within a phase marked [P] can be written in parallel (they target different scenarios in the same file)
- T031 and T032 can run in parallel (different `__init__.py` files)
- T035 and T036 can run in parallel (different sample files)
- Phases themselves are sequential (each builds on the previous)

---

## Notes

- [P] tasks = different files or independent scenarios, no dependencies
- [Story] label maps task to specific user story for traceability
- Entry mode (Phase 2) MUST be done before lifecycle (Phase 3) — lifecycle needs entry_mode signaling
- Protocol packages (invocations, responses) are NOT modified in any task — they remain HTTP handlers
- `TaskInfo` already exists in `_models.py` — we only need to re-export it, not create it
- `_resolve_lifecycle()` is the key new helper — extracts lifecycle state machine into one shared function used by both `.run()` and `.start()`
- Constitution: no `from __future__ import annotations` in files that interact with LangGraph's `get_type_hints()`
