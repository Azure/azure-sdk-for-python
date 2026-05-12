# Tasks: Durable Tasks for Long-Running Agents

**Input**: Design documents from `specs/001-durable-tasks/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Included — the spec defines crash recovery and lifecycle scenarios that require integration tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Exact file paths included in all descriptions

## Path Conventions

- **Source**: `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`
- **Tests**: `azure-ai-agentserver-core/tests/`
- **Package root**: `azure-ai-agentserver-core/`

---

## Phase 1: Setup

**Purpose**: Create the `durable/` subpackage skeleton and add the `httpx` dependency.

- [ ] T001 Create `durable/` package directory and `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/__init__.py` with public API docstring and empty `__all__`
- [ ] T002 Add `httpx>=0.27.0` and `azure-identity>=1.16.0` to `dependencies` (httpx) and `optional-dependencies` (azure-identity, under `[hosted]` extra) in `azure-ai-agentserver-core/pyproject.toml`
- [ ] T003 [P] Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_exceptions.py` — define `TaskFailed`, `TaskSuspended`, `TaskCancelled`, `TaskNotFound` per data-model.md §1.7

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Internal models, provider protocol, and storage implementations that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_models.py` — define `TaskStatus` literal, `LeaseInfo`, `TaskInfo`, `TaskCreateRequest`, `TaskPatchRequest` dataclasses per data-model.md §2.4-2.5
- [ ] T005 [P] Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_provider.py` — define `DurableTaskProvider` `Protocol` with `create`, `get`, `update`, `delete`, `list` async methods per data-model.md §2.3
- [ ] T006 Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_client.py` — implement `HostedDurableTaskProvider` using `httpx.AsyncClient` to call `/storage/tasks` endpoints; Bearer auth via lazy `DefaultAzureCredential`; all 5 CRUD methods per data-model.md §2.2 and research.md R-1/R-2
- [ ] T007 Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_local_provider.py` — implement `LocalFileDurableTaskProvider` with JSON files under `$HOME/.durable-tasks/{agent_name}/{session_id}/`, file-level locking, lease expiry simulation per research.md R-4
- [ ] T008 [P] Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_lease.py` — implement `derive_lease_owner(session_id)`, `generate_instance_id()`, and `lease_renewal_loop(provider, task_id, interval, cancel_event)` async function per research.md R-3
- [ ] T009 Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_metadata.py` — implement `TaskMetadata` class with `set`, `get`, `increment`, `append`, `to_dict`, `flush` methods; debounced persistence via provider per data-model.md §1.4
- [ ] T010 Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_context.py` — implement `TaskContext[Input]` generic class with identity fields, `input`, `metadata`, `cancel`/`shutdown` events, `run_attempt`, `lease_generation`, and `suspend()` method per data-model.md §1.2
- [ ] T011 [P] Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_run.py` — implement `TaskRun[Output]` generic class with `task_id`, `status`, `metadata`, `result()`, `cancel()`, `delete()`, `refresh()` per data-model.md §1.3; include `Suspended[Output]` sentinel class per data-model.md §1.5

**Checkpoint**: All internal primitives and storage providers are ready. User story implementation can begin.

---

## Phase 3: User Story 1 — Crash-Safe Durable Task Execution (Priority: P1) 🎯 MVP

**Goal**: A developer decorates an async function with `@durable_task`, invokes it with `.run()` or `.start()`, and the framework manages the full lifecycle — create, lease, renew, run, complete/fail, delete.

**Independent Test**: Decorate a function, call `.run(task_id=..., input=...)`, verify result is returned. Kill process mid-execution, restart, verify task is recovered and re-run.

### Tests for User Story 1

- [ ] T012 [P] [US1] Create `azure-ai-agentserver-core/tests/test_durable_decorator.py` — test `@durable_task` validates async functions, rejects sync, extracts input/output types, supports with/without arguments, returns `DurableTask[I, O]`
- [ ] T013 [P] [US1] Create `azure-ai-agentserver-core/tests/test_durable_lifecycle.py` — test full lifecycle: `.run()` creates task → acquires lease → runs function → returns result → deletes task (ephemeral); test `.start()` returns `TaskRun` handle; test exception → `TaskFailed`; test `ephemeral=False` keeps task as completed
- [ ] T014 [P] [US1] Create `azure-ai-agentserver-core/tests/test_durable_recovery.py` — test startup recovery: create stale in-progress task with same owner/different instance, verify manager reclaims lease (increments generation), dispatches to resume callback

### Implementation for User Story 1

- [ ] T015 [US1] Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_decorator.py` — implement `@durable_task` decorator: validate function signature, extract `Input`/`Output` generics via type inspection, return `DurableTask[Input, Output]` with `.run()`, `.start()`, `.options()` per contracts/public-api.md §1-2
- [ ] T016 [US1] Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_manager.py` — implement `DurableTaskManager`: provider selection based on `AgentConfig.is_hosted`, `create_and_run()` (create task with lease → spawn function as `asyncio.Task` → start renewal loop → await result → delete/complete → return), `create_and_start()` (same but return handle immediately), `startup()` (recover stale tasks), `shutdown()` (signal + force-expire) per data-model.md §2.1
- [ ] T017 [US1] Update `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/__init__.py` — export `durable_task`, `DurableTask`, `TaskContext`, `TaskRun`, `TaskMetadata`, `Suspended`, `TaskStatus`, and all exception types in `__all__`
- [ ] T018 [US1] Integrate `DurableTaskManager` into `AgentServerHost` in `azure-ai-agentserver-core/azure/ai/agentserver/core/_base.py` — add `self.tasks: DurableTaskManager` attribute, call `tasks.startup()` in lifespan, register `tasks.shutdown()` as shutdown callback
- [ ] T019 [US1] Update `azure-ai-agentserver-core/azure/ai/agentserver/core/__init__.py` — re-export durable task public types from the top-level package `__all__`

**Checkpoint**: `@durable_task` decorator works end-to-end with `.run()` and `.start()`. Crash recovery reclaims stale tasks on startup. MVP complete.

---

## Phase 4: User Story 2 — Suspend and Resume (Priority: P2)

**Goal**: A developer calls `return await ctx.suspend(reason=...)` inside a durable function to pause execution. An external trigger via `POST /tasks/resume` re-enters the function.

**Independent Test**: Start a task that suspends, verify task transitions to `suspended` with reason. Send `POST /tasks/resume`, verify function re-enters. Verify empty-body response with correct status codes.

### Tests for User Story 2

- [ ] T020 [P] [US2] Create `azure-ai-agentserver-core/tests/test_durable_suspend_resume.py` — test `ctx.suspend()` transitions to suspended, releases lease, persists output snapshot; test `POST /tasks/resume` re-fetches task, acquires new lease, dispatches function; test resume of non-existent task returns 404; test resume of in-progress task returns 409; test suspended tasks are NOT auto-resumed on restart
- [ ] T021 [P] [US2] Create `azure-ai-agentserver-core/tests/test_durable_resume_route.py` — test `POST /tasks/resume` HTTP endpoint with ASGI test client: 202 empty body on success, 404 on missing task, 409 on conflict; verify no response body content

### Implementation for User Story 2

- [ ] T022 [US2] Implement suspend flow in `_manager.py` — detect `Suspended` return sentinel from function, transition task to `suspended` status via provider PATCH (set `suspension_reason`, write output snapshot to `payload.output`, release lease), notify `TaskRun` handle
- [ ] T023 [US2] Create `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_resume_route.py` — implement Starlette `Route` handler for `POST /tasks/resume`: parse `task_id` from JSON body, validate task exists and is `suspended`, transition to `in_progress` with new lease, dispatch to registered resume callback, return `Response(status_code=202)` with empty body; return 404/409 as appropriate per spec FR-015
- [ ] T024 [US2] Register resume route in `_base.py` — auto-add `Route("/tasks/resume", ...)` to the host's route list during durable task initialization
- [ ] T025 [US2] Add `handle_resume(task_id)` to `DurableTaskManager` in `_manager.py` — re-fetch task from provider, validate status is `suspended`, acquire lease, look up resume callback by task's function name, dispatch

**Checkpoint**: Suspend/resume round-trip works. External triggers via HTTP re-enter the function. Empty-body responses confirmed.

---

## Phase 5: User Story 3 — Task Progress and Metadata (Priority: P3)

**Goal**: A developer writes `ctx.metadata.set("phase", "researching")` inside a running task and external observers can read the progress.

**Independent Test**: Set metadata inside a running task, read it via `handle.metadata.get(...)` from outside, verify values match.

### Tests for User Story 3

- [ ] T026 [P] [US3] Create `azure-ai-agentserver-core/tests/test_durable_metadata.py` — test `set`/`get`/`increment`/`append`/`to_dict` operations; test debounced flush to provider; test immediate flush on suspend/complete; test `flush()` explicit call; test type validation (increment requires numeric, append requires list)

### Implementation for User Story 3

- [ ] T027 [US3] Add debounced persistence to `_metadata.py` — implement background `asyncio.Task` that flushes dirty metadata to provider via `PATCH payload.metadata` at configurable interval (default 5s); cancel on task completion; immediate flush on `flush()` call
- [ ] T028 [US3] Wire metadata into `TaskRun.metadata` in `_run.py` — for in-process handles, expose the live `TaskMetadata` reference; for external handles, fetch from provider on `refresh()`
- [ ] T029 [US3] Ensure metadata is included in the payload PATCH during suspend and complete flows in `_manager.py` — flush pending metadata changes before the status transition PATCH

**Checkpoint**: Metadata is observable from outside the function. Debounced persistence minimizes API calls.

---

## Phase 6: User Story 4 — Local Development Parity (Priority: P4)

**Goal**: Full durable task lifecycle works locally without Azure credentials. Tasks stored as JSON files.

**Independent Test**: Run agent without `FOUNDRY_HOSTING_ENVIRONMENT`. Create/start/update/complete/delete tasks. Kill process, restart, verify stale task recovery from filesystem.

### Tests for User Story 4

- [ ] T030 [P] [US4] Create `azure-ai-agentserver-core/tests/test_durable_local_provider.py` — test all 5 CRUD operations on `LocalFileDurableTaskProvider`; test JSON file creation/read/update/delete under temp directory; test lease expiry simulation (expired `expires_at` treated as released); test file locking for concurrent access; test list with status filter; test force delete and cascade delete

### Implementation for User Story 4

- [ ] T031 [US4] Add startup recovery to `LocalFileDurableTaskProvider` in `_local_provider.py` — on `list()` with `status="in_progress"`, check each task's `lease.expires_at` and return expired-lease tasks so the manager can reclaim them
- [ ] T032 [US4] Add ETag simulation to `LocalFileDurableTaskProvider` in `_local_provider.py` — generate ETag from file modification time + content hash; validate `If-Match` on PATCH/DELETE; return 412 on mismatch
- [ ] T033 [US4] Add provider auto-selection to `DurableTaskManager.__init__` in `_manager.py` — if `config.is_hosted` use `HostedDurableTaskProvider`, else use `LocalFileDurableTaskProvider(base_dir=Path.home() / ".durable-tasks")`

**Checkpoint**: Local dev works identically to hosted. Crash recovery testable by killing/restarting the process.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Shutdown coordination, observability, and validation pass.

- [ ] T034 Create `azure-ai-agentserver-core/tests/test_durable_shutdown.py` — test SIGTERM signals `ctx.shutdown` on all active tasks; test force-expire leases on shutdown; test graceful drain within timeout
- [ ] T035 Implement shutdown coordination in `_manager.py` — `shutdown()` method: signal `shutdown` event on all active `TaskContext` instances, wait up to graceful timeout, force-expire all leases via provider PATCH with `lease_duration_seconds=0`, cancel all lease renewal loops
- [ ] T036 [P] Add OpenTelemetry spans to `_client.py` — wrap each HTTP call with a span (`durable_task.create`, `durable_task.get`, etc.) including `task_id`, `status`, `lease_generation` attributes
- [ ] T037 [P] Add structured logging to `_manager.py` and `_lease.py` — log task creation, lease acquisition, renewal success/failure, recovery, suspension, completion, and shutdown events at appropriate levels (INFO/WARNING)
- [ ] T038 [P] Add input serialization support in `_decorator.py` — implement detection and serialization/deserialization for Pydantic models (`model_dump`/`model_validate`), dataclasses (`asdict`/constructor), and plain JSON types per research.md R-9
- [ ] T039 Run `azpysdk pylint .` from `azure-ai-agentserver-core/` and fix any warnings in new durable task files
- [ ] T040 Run `azpysdk mypy .` from `azure-ai-agentserver-core/` and fix any type errors in new durable task files
- [ ] T041 Run `azpysdk black .` from `azure-ai-agentserver-core/` and fix any formatting issues
- [ ] T042 Validate quickstart.md scenarios work end-to-end against the implementation — run each code snippet from `specs/001-durable-tasks/quickstart.md` as a smoke test

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (T001-T003) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — MVP delivery
- **US2 (Phase 4)**: Depends on Phase 2 — can start in parallel with US1 but integrates with `_manager.py`
- **US3 (Phase 5)**: Depends on Phase 2 — can start in parallel with US1/US2
- **US4 (Phase 6)**: Depends on Phase 2 (T007 specifically) — can start in parallel with US1
- **Polish (Phase 7)**: Depends on all user stories

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories. MVP-complete independently.
- **US2 (P2)**: Integrates with `_manager.py` from US1 (adds suspend/resume paths). Can be developed in parallel on a branch but merges after US1.
- **US3 (P3)**: Integrates with `_metadata.py` from Phase 2 and `_manager.py` from US1. Can be developed in parallel.
- **US4 (P4)**: Depends on `_local_provider.py` from Phase 2 (T007). Independent of US1-US3 logic but validates via the same manager.

### Within Each User Story

- Tests written first → verify they fail
- Internal primitives before orchestration
- Manager integration before host integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T003 can run in parallel with T001/T002
- **Phase 2**: T005 ∥ T008 ∥ T011 (different files, no dependencies)
- **Phase 3**: T012 ∥ T013 ∥ T014 (test files, no dependencies)
- **Phase 4**: T020 ∥ T021 (test files, no dependencies)
- **Phase 5**: T026 can start as soon as Phase 2 completes
- **Phase 6**: T030 can start as soon as T007 is done
- **Phase 7**: T034 ∥ T036 ∥ T037 ∥ T038 (different files)

---

## Parallel Example: Foundational Phase

```
# These can all be worked on simultaneously:
T005: _provider.py (protocol definition)
T008: _lease.py (lease utilities)
T011: _run.py + Suspended (handle + sentinel)

# These must wait for T004 (_models.py):
T006: _client.py (uses TaskInfo, TaskCreateRequest)
T007: _local_provider.py (uses TaskInfo, TaskCreateRequest)
T009: _metadata.py (standalone but logical dependency)
T010: _context.py (uses TaskMetadata from T009)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011)
3. Complete Phase 3: US1 — Crash-Safe Execution (T012-T019)
4. **STOP and VALIDATE**: Run tests, verify `.run()` and `.start()` work, test crash recovery
5. Ship MVP — developers can make any async function crash-resilient

### Incremental Delivery

1. Setup + Foundational → All primitives ready
2. US1 → Crash-safe execution (MVP!) ✅
3. US2 → Add suspend/resume for human-in-the-loop ✅
4. US3 → Add metadata observability ✅
5. US4 → Local dev parity ✅
6. Polish → Observability, validation, cleanup ✅

### Suggested Scope

- **MVP**: Phases 1-3 (Setup + Foundational + US1) = 19 tasks
- **Full feature**: All phases = 42 tasks

---

## Notes

- [P] tasks = different files, no dependencies — safe to parallelize
- [Story] label maps each task to a specific user story for traceability
- All file paths are relative to `azure-ai-agentserver-core/`
- Constitution mandates: async-first, strong typing, Black formatting, 120-char lines
- `depends_on_task_ids`, `ctx.stream(...)`, `RetryPolicy` are OUT OF SCOPE
- `POST /tasks/resume` returns empty body with status code only (202/404/409)
