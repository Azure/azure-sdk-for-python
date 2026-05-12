# Implementation Plan: Durable Task Lifecycle Automation & Public API Simplification

**Branch**: `003-invocation-lifecycle-api` | **Date**: 2026-05-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-invocation-lifecycle-api/spec.md`

## Summary

Add three capabilities to the durable task subsystem in `azure-ai-agentserver-core`:

1. **Lifecycle automation** — The existing `.run(task_id, input)` and `.start(task_id, input)` methods on `DurableTask` become lifecycle-aware. They atomically handle start-or-resume-or-recover with deterministic behavior based on the current task state. No new methods needed — the platform always does the right thing: create if no task exists, start if pending, resume if suspended, throw if in-progress or completed.
2. **Re-entry context** — `TaskContext.entry_mode` returns `"fresh"`, `"resumed"`, or `"recovered"` so the durable function knows why it was entered. `ctx.input` always holds the current execution's data. Entry mode is informational — ignoring it is safe.
3. **Public API simplification** — New public types (`TaskConflictError`, `EntryMode`), `.get(task_id)` on `DurableTask` for querying persisted task info, `TaskInfo` exported publicly, and clean exports so developers never import from private modules.

All changes are in the core package. The invocations/responses packages are untouched — they remain pure protocol handlers. Samples demonstrate one composition pattern (sticky reentrant sessions) but the primitives enable any pattern.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: starlette (existing), httpx (existing), asyncio (stdlib)
**Storage**: Local JSON files (`$HOME/.durable-tasks/`) by default; HTTP-backed provider gated behind `FOUNDRY_TASK_API_ENABLED=1`
**Testing**: pytest with pytest-asyncio (`asyncio_mode = "auto"`)
**Target Platform**: Linux containers (Azure AI Foundry Hosted Agents) + local dev on any platform
**Project Type**: Library (Python package — `azure-ai-agentserver-core`)
**Constraints**: No new dependencies. No dataclasses. Plain classes with `__slots__`. All code in `azure.ai.agentserver.core.durable`. Protocol packages untouched.
**Scale/Scope**: Extends 12 existing modules in `durable/` subpackage; 198 existing tests must continue to pass

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modular Package Architecture | ✅ PASS | All changes in `core` package. Protocol packages untouched — they stay as HTTP plumbing only. No new cross-package dependencies. |
| II. Strong Type Safety | ✅ PASS | `EntryMode = Literal["fresh", "resumed", "recovered"]`. `TaskConflictError` extends `RuntimeError`. No `Any` in new APIs. |
| III. Azure SDK Guidelines | ✅ PASS | Naming, versioning, Black formatting all followed. Additions to existing `durable` subpackage. |
| IV. Async-First Design | ✅ PASS | `.run()`, `.start()`, `.get()` are `async`. Lifecycle checks use provider's async API. |
| V. Fail-Fast Config, Graceful Runtime | ✅ PASS | `.run()`/`.start()` raise `TaskConflictError` immediately on conflict (fail-fast). Stale recovery is graceful with checkpoint reconciliation. |
| VI. Observability & Correlation | ✅ PASS | Entry mode logged on function entry. Lifecycle transitions logged (start/resume/recover). |
| VII. Minimal Surface, Maximum Composability | ✅ PASS | Three new public types. Two new methods on existing `DurableTask`. No new abstractions in protocol packages. Developers compose freely. |

## Project Structure

### Documentation (this feature)

```text
specs/003-invocation-lifecycle-api/
├── spec.md              # Feature specification (done)
├── plan.md              # This file
├── research.md          # Phase 0 output (already incorporated into spec — industry patterns)
├── data-model.md        # Phase 1 output — new type definitions
├── contracts/           # Phase 1 output — public API contract
│   └── public-api.md
├── quickstart.md        # Phase 1 output — usage examples
└── tasks.md             # Phase 2 output (speckit tasks)
```

### Source Code (modifications to existing files)

```text
azure-ai-agentserver-core/
├── azure/ai/agentserver/core/
│   └── durable/
│       ├── __init__.py                # MODIFY — export TaskConflictError, EntryMode, TaskInfo
│       ├── _context.py                # MODIFY — add entry_mode to TaskContext
│       ├── _decorator.py              # MODIFY — make .run()/.start() lifecycle-aware, add .get()
│       ├── _manager.py                # MODIFY — wire entry_mode through execution paths
│       └── _exceptions.py             # MODIFY — add TaskConflictError
│
└── tests/
    └── durable/
        ├── test_entry_mode.py         # NEW — entry_mode unit tests
        ├── test_lifecycle.py          # NEW — lifecycle automation tests (.run()/.start())
        ├── test_get.py                # NEW — .get() tests
        └── test_sample_e2e.py         # MODIFY — rewrite samples to use new API + e2e tests

azure-ai-agentserver-invocations/
└── samples/
    └── durable_multiturn/
        └── durable_multiturn.py       # MODIFY — rewrite to use lifecycle-aware API (≤10 line handler)
    └── durable_langgraph/
        └── durable_langgraph.py       # MODIFY — rewrite to use lifecycle-aware API (≤10 line handler)
```

**Structure Decision**: No new modules — `TaskConflictError` goes in existing `_exceptions.py`. Lifecycle logic is added to existing `.run()`/`.start()` in `_decorator.py`. No new subpackages. Protocol packages (invocations, responses) are NOT modified — they remain protocol handlers.

## Implementation Phases

### Phase 0 — Research

Analyze lifecycle automation patterns from Temporal, Inngest, LangGraph Cloud, and Azure Durable Functions.

**Already done** — research incorporated into spec (see "Industry Patterns" section and research agents from prior session).

### Phase 1 — Data Model & Contracts

Define the exact class interfaces, method signatures, and data flow for all new types and methods.

**Deliverables:**
- `data-model.md` — `TaskConflictError`, `EntryMode` definitions; `TaskContext` changes
- `contracts/public-api.md` — Updated public API surface showing new methods and types
- `quickstart.md` — Usage examples showing the before/after API simplification

**Key Design Decisions:**

1. **`EntryMode`**: `Literal["fresh", "resumed", "recovered"]` — a type alias, not a class. Added to `_context.py`.

2. **`TaskContext` changes**:
   - Add `entry_mode: EntryMode` slot — set by manager before calling the function
   - `ctx.input` always holds the current execution's input (fresh data on start, resume data on resume) — no separate `resume_input` needed since the function is re-entrant and starts from scratch each time
   - `entry_mode` is a read-only property after construction

3. **`TaskConflictError`**: New exception in `_exceptions.py`:
   - Extends `RuntimeError`
   - `task_id: str`, `current_status: str`
   - Clear message: `"Task '{task_id}' is already {current_status}"`

4. **Lifecycle-aware `.run()` and `.start()`**: The existing methods gain lifecycle awareness:
   - Check current task state before acting
   - No task / pending → create and start (`entry_mode="fresh"`)
   - Suspended → patch input, resume (`entry_mode="resumed"`)
   - In-progress (not stale) → raise `TaskConflictError`
   - In-progress (stale) → recover (`entry_mode="recovered"`)
   - Completed → raise `TaskConflictError`
   - Return types unchanged: `.run()` → `Output`, `.start()` → `TaskRun[Output]`
   - `stale_timeout` parameter added (default 300.0 seconds)

5. **`DurableTask.get()` signature**:
   ```python
   async def get(self, task_id: str) -> TaskInfo | None:
   ```
   - Returns full persisted `TaskInfo` for any task state, or `None` if no task exists

### Phase 2 — Entry Mode (US2 — foundational, needed by Phase 3)

Add `entry_mode` to `TaskContext` and wire it through the manager.

**Why first**: Entry mode is the foundational primitive that lifecycle-aware `.run()`/`.start()` builds on. The manager needs to set it correctly for each lifecycle path (fresh/resumed/recovered). Building this first means the lifecycle automation has the signaling mechanism it needs.

**Files:**
1. `_context.py` — Add `entry_mode: str` to `__slots__` and `__init__` (`ctx.input` already carries the current execution's data — no separate `resume_input` needed)
2. `_manager.py` — Set `entry_mode="fresh"` in `create_and_run`/`create_and_start`; set `entry_mode="resumed"` in `handle_resume` (covers BOTH resume paths — developer-initiated via `.run()`/`.start()` and platform-initiated via `/tasks/{task_id}/resume` endpoint); set `entry_mode="recovered"` in stale task recovery path
3. `durable/__init__.py` — Export `EntryMode` type alias
4. `tests/durable/test_entry_mode.py` — Unit tests:
   - Fresh start → `ctx.entry_mode == "fresh"`, `ctx.input` has initial data
   - Developer-initiated resume (via `.run(task_id=..., input=new_data)`) → `ctx.entry_mode == "resumed"`, `ctx.input` has the new input provided on the call
   - Platform-initiated resume (via `handle_resume()` / `/tasks/resume`) → `ctx.entry_mode == "resumed"`, `ctx.input` has the task's persisted input (no new input on external resume)
   - Recovery → `ctx.entry_mode == "recovered"`
   - Ignoring entry_mode works fine (informational)

### Phase 3 — Lifecycle Automation (US1 — core feature)

Make `.run()` and `.start()` lifecycle-aware with automatic start-or-resume-or-recover logic.

**Why second**: Depends on Phase 2 for entry mode signaling. This is the highest-impact change — eliminates all manual lifecycle boilerplate.

**Files:**
1. `_exceptions.py` — Add `TaskConflictError(RuntimeError)` with `task_id`, `current_status`
2. `_decorator.py` — Modify `.run()` and `.start()` to add lifecycle logic:
   - Get manager via `get_task_manager()`
   - Query existing task via `manager._provider.get(task_id)` (internal — this is framework code, not user code)
   - Branch on status:
     - No existing / pending → fresh start (entry_mode="fresh")
     - Suspended → resume via `handle_resume()` with new input (entry_mode="resumed")
     - In_progress + not stale → raise `TaskConflictError`
     - In_progress + stale → recover (entry_mode="recovered")
     - Completed → raise `TaskConflictError` (no restarting completed tasks)
   - `.run()` returns `Output` (same as today)
   - `.start()` returns `TaskRun[Output]` (same as today)
3. `_decorator.py` — Add `.get(task_id)` method to `DurableTask`
4. `durable/__init__.py` — Export `TaskConflictError`, `TaskInfo`
5. `tests/durable/test_lifecycle.py` — Unit tests:
   - Fresh start → entry_mode="fresh"
   - Resume suspended → entry_mode="resumed"
   - In_progress → TaskConflictError
   - Stale → entry_mode="recovered"
   - Completed → TaskConflictError (no restart)
   - Pending → start it (entry_mode="fresh")
6. `tests/durable/test_get.py` — Unit tests:
   - Existing task → returns TaskInfo
   - No task → returns None
   - Returns full persisted info for any state

### Phase 4 — Public API Surface (US3 — polish)

Ensure all needed types are publicly exported and samples can be written without private imports.

**Why third**: Depends on Phase 2-3 for the types to exist. This is the polish step — clean exports, verify no private imports needed.

**Files:**
1. `durable/__init__.py` — Verify all new types exported: `TaskConflictError`, `EntryMode`, `TaskInfo`, and existing types still present
2. `core/__init__.py` — Re-export new types from top-level `azure.ai.agentserver.core`
3. Audit: Verify that a developer can write a complete multi-turn handler using ONLY:
   ```python
   from azure.ai.agentserver.core.durable import durable_task, TaskContext
   ```
   No imports from `_manager`, `_models`, `_local_provider`, `_exceptions`, etc.

### Phase 5 — Samples & E2E Tests (US4, US5)

Rewrite both invocations samples to use the lifecycle-aware `.run()`/`.start()` API. Update e2e tests. Verify all composition patterns work.

**Why last**: Depends on all core changes being complete and tested. Samples are the proof that the API works.

**Files:**
1. `azure-ai-agentserver-invocations/samples/durable_multiturn/durable_multiturn.py` — Rewrite:
   - Handler body ≤10 lines
   - Uses `await session_task.run(task_id=..., input=...)` for lifecycle
   - Uses `ctx.entry_mode` for fresh vs resumed branching in the task function
   - FileCheckpointStore with atomic writes (already exists, just composing differently)
   - Zero imports from private modules
   - Comment noting this is ONE composition pattern — not the only one
2. `azure-ai-agentserver-invocations/samples/durable_langgraph/durable_langgraph.py` — Rewrite:
   - Handler body ≤10 lines
   - Uses `await langgraph_task.run(task_id=..., input=...)` for lifecycle
   - SqliteSaver for graph checkpoints (already exists)
   - Zero imports from private modules
   - Comment noting this is ONE composition pattern
3. `azure-ai-agentserver-core/tests/durable/test_sample_e2e.py` — Update e2e tests:
   - Rewrite `TestMultiturnSampleE2E` to use new API
   - Rewrite `TestLangGraphSampleE2E` to use new API
   - Add test for crash recovery (stale task → recovered entry_mode)
   - Verify per-turn output is separate (developer composition, not framework)
   - All tests use inline logic (not sample imports), per constitution
4. Verify all 198 existing tests still pass
5. Run Black on all modified files

**Success Verification:**
- SC-001: LangGraph handler ≤10 lines ✓
- SC-002: Multiturn handler ≤10 lines ✓
- SC-003: Zero private module imports in samples ✓
- SC-004: Both samples survive crash + resume (e2e test) ✓
- SC-005: Core types have zero protocol-specific fields ✓
- SC-006: entry_mode correct in all paths (unit tests) ✓
- SC-007: mypy strict + pyright pass ✓

## Complexity Tracking

No constitution violations. All principles pass.
