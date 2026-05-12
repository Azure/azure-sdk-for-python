# Feature Specification: Durable Task Lifecycle Automation & Public API Simplification

**Feature Branch**: `003-invocation-lifecycle-api`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Lifecycle management (start/resume/already-running) must be automated by the platform, re-entrant functions need entry mode context, and the public API surface needs radical simplification — no more reaching into manager._provider. Core package stays protocol-agnostic."

## Background & Motivation

The current samples expose three fundamental design problems:

1. **Verbose lifecycle management**: Developers must manually check task state (`suspended` → resume, `in_progress` → reject, `completed` → delete and restart). This is boilerplate that every developer writes identically. Temporal solves this with `id_conflict_policy=USE_EXISTING` (atomic start-or-attach). Inngest solves it with fully automatic memoization. LangGraph Cloud uses `multitask_strategy`. Our platform should handle this automatically.

2. **Poor public API ergonomics**: Samples import `_manager`, call `get_task_manager()`, reach into `manager._provider.get(task_id)`, and manually construct `TaskPatchRequest`. The public API should be a single call like `await my_task.run(task_id=..., input=...)` that handles all lifecycle internally.

3. **No re-entry context**: The durable function is called from scratch on resume (re-entrant). But the developer has no way to know *why* the function was entered — is this a fresh start, a resume from suspend, or a recovery from crash? Different entry modes may require different initialization or cleanup logic.

### Design Principle: Protocol Agnosticism

**The core package and durable task layer MUST remain protocol-agnostic.** The core layer works with `task_id` and `session_id` — it has no knowledge of protocol-specific identifiers like invocation IDs, response IDs, or conversation IDs.

How protocol-specific identifiers map to durable tasks is **entirely the developer's composition concern**:
- A developer using invocations might use `session_id` as the task key for sticky sessions, or create a fresh task per invocation — their choice
- A developer using the responses package would compose tasks completely differently
- The core provides primitives; developers compose them in their handler code
- Protocol packages (invocations, responses) handle HTTP plumbing only — they don't impose any task composition strategy

### Design Principle: Primitives, Not Higher-Order Abstractions

**The invocations and responses packages are protocol handlers, NOT orchestration layers.** They handle HTTP routing, header injection, and protocol compliance. They do NOT build higher-order abstractions on top of core durable tasks.

How a developer composes durable tasks with protocol endpoints is **entirely the developer's concern**:
- **One task per invocation**: Stateless — each POST creates a fresh task, runs it, returns the result. Good for independent operations.
- **One task per session (sticky/reentrant)**: Multi-turn — a single durable task spans many invocations, suspending between turns. Good for conversational agents, LangGraph graphs.
- **Multiple background tasks per invocation**: Fan-out — one invocation kicks off several tasks in parallel. Good for research agents, multi-tool orchestration.
- **Mixed patterns**: Some invocations create tasks, others query or cancel them. The developer decides.

Our samples demonstrate the sticky reentrant session pattern because it's the most complex and showcases durability best — but it is explicitly **one of many patterns** we enable. The core package provides primitives (`@durable_task`, `.run()`, `.start()`, `.get()`, `ctx.suspend()`, `ctx.entry_mode`). Protocol packages provide HTTP plumbing. Developers compose them freely.

### Industry Patterns (Research Summary)

| Framework | Start-or-resume | Developer lifecycle code? |
|---|---|---|
| **Temporal** | `id_conflict_policy=USE_EXISTING` + atomic Update-With-Start | No — declare policy |
| **Inngest** | Event-driven + `idempotency` key | No — fully automatic |
| **LangGraph Cloud** | `threads.create(if_exists="do_nothing")` + new Run | Minimal — 2 calls |
| **Azure Durable Functions** | Manual `get_status()` → branch | Yes — explicit |
| **Our SDK (current)** | Manual `provider.get()` → if/else → patch → resume | Yes — very verbose |

We should target the Temporal/LangGraph Cloud level: **developer declares intent, platform executes lifecycle**.

### Container Spec Alignment

From `invocation-protocol-spec.md`:
- Platform injects `x-agent-invocation-id` on POST /invocations
- Container MUST echo it back in the response
- GET /invocations/{invocation_id} uses the invocation ID, not a task ID
- Each long-running invocation is wrapped in a task (durable-task-integration-spec)
- The invocation ID is the external contract; the task ID is internal
- **This mapping is the invocations package's responsibility, not the core durable task layer**

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Platform-managed task lifecycle (Priority: P1)

A developer building a multi-turn agent writes a single durable task function. When the developer calls `await my_task.run(task_id=..., input=...)`, the platform automatically determines whether to start a new task, resume a suspended one, or recover a stale one — the developer never writes lifecycle branching code. This works identically regardless of the protocol layer above (invocations, responses, custom).

**Why this priority**: This is the highest-impact change. Every sample currently contains 30+ lines of manual lifecycle management (check status, branch, patch payload, call handle_resume, handle stale tasks). This is identical boilerplate that the platform should own. Without this, every developer copies and adapts the same fragile if/else logic.

**Independent Test**: A developer registers a durable task that suspends after each turn. The developer calls `await my_task.run(task_id=..., input=...)` three times. The first call starts a new task; the second and third calls automatically resume the suspended task with new input. The developer writes zero lifecycle code.

**Acceptance Scenarios**:

1. **Given** a durable task function that calls `ctx.suspend(output=...)`, **When** the developer calls `await task.run(task_id="session:s1", input=data)` for the first time, **Then** the platform creates a new task, executes the function, and the function suspends — the developer gets the suspended output.

2. **Given** a suspended durable task with task_id "session:s1", **When** the developer calls `await task.run(task_id="session:s1", input=new_data)` again, **Then** the platform automatically detects the suspended task, updates the input payload, resumes the task — without the developer checking status or calling `handle_resume`.

3. **Given** a durable task that is currently `in_progress` for task_id "session:s1", **When** the developer calls `await task.run(task_id="session:s1", input=data)`, **Then** the platform raises `TaskConflictError` indicating the task is still running — not a generic error.

4. **Given** a durable task that is `in_progress` but stale (updated_at older than the configured stale timeout), **When** the developer calls `await task.run(task_id="session:s1", input=data)`, **Then** the platform automatically reconciles the stale task and recovers it, with `ctx.entry_mode == "recovered"`.

5. **Given** a completed durable task for task_id "session:s1", **When** the developer calls `await task.run(task_id="session:s1", input=data)`, **Then** the platform raises `TaskConflictError` — a completed task cannot be restarted. The developer must use a new task_id if they want a fresh task.

---

### User Story 2 — Re-entry mode context for durable functions (Priority: P1)

Since durable functions are re-entrant (called from scratch on resume/recovery), the developer needs to know *why* the function was entered. A fresh start may require initializing state; a resume may need to read the latest input; a recovery may need cleanup of partial work. The `TaskContext` MUST expose an `entry_mode` property so the function can branch when needed.

There are **two distinct resume paths** — both result in `entry_mode="resumed"`:
1. **Developer-initiated resume**: The developer calls `await task.run(task_id=..., input=...)` and the platform detects a suspended task → automatically resumes it with new input.
2. **Platform-initiated resume**: An external caller hits the `/tasks/{task_id}/resume` endpoint (e.g., orchestrator, webhook, another service) → the platform's resume callback re-enters the function.

Both paths re-enter the function from scratch. Both set `ctx.entry_mode = "resumed"`. The resume data is available via `ctx.input` — just like any other execution, the function receives its input through the standard `ctx.input` property.

**Why this priority**: Equally critical to lifecycle automation. Without entry mode, the developer cannot safely handle initialization vs continuation logic inside the function. Every re-entrant function needs this — it's the complement to automated lifecycle management. The platform handles "when to call the function" (Story 1); this tells the function "why was I called".

**Independent Test**: A developer writes a durable task function that checks `ctx.entry_mode` and behaves differently on `"fresh"` (initialize state) vs `"resumed"` (load checkpoint and continue) vs `"recovered"` (log warning and reconcile). The test verifies each mode is set correctly across the three lifecycle paths.

**Acceptance Scenarios**:

1. **Given** a durable task function started for the first time via `.run()` or `.start()`, **When** the function reads `ctx.entry_mode`, **Then** it returns `"fresh"`.

2. **Given** a suspended durable task that is resumed via `.run(task_id=..., input=new_data)` (developer-initiated), **When** the function is re-entered, **Then** `ctx.entry_mode` returns `"resumed"` and `ctx.input` contains the new input data provided on the `.run()` call.

3. **Given** a suspended durable task that is resumed via the `/tasks/{task_id}/resume` endpoint (platform-initiated), **When** the platform's resume callback re-enters the function, **Then** `ctx.entry_mode` returns `"resumed"` and `ctx.input` contains whatever input is already persisted on the task (no new input is provided on the API call).

4. **Given** a stale `in_progress` task that is recovered by the platform, **When** the function is re-entered, **Then** `ctx.entry_mode` returns `"recovered"` — allowing the developer to run cleanup or reconciliation logic.

5. **Given** a developer who does NOT check `ctx.entry_mode`, **When** the function runs, **Then** everything works fine — entry mode is informational, not a required check. The function can ignore it entirely.

---

### User Story 3 — Simplified public API surface (Priority: P1)

The public API for interacting with durable tasks must be simple, intuitive, and protocol-agnostic. No reaching into private attributes (`manager._provider`), no manual construction of `TaskPatchRequest`, no importing internal modules (`_manager`, `_models`). The core durable API works for any protocol layer — invocations, responses, or custom.

**Why this priority**: API ergonomics directly impact developer adoption. The current pattern requires 5 imports from internal modules and ~40 lines of boilerplate per handler. The target is 1 import and ~5 lines.

**Independent Test**: A developer writes a complete multi-turn handler using only public imports from `azure.ai.agentserver.core.durable`. The handler body is under 10 lines.

**Acceptance Scenarios**:

1. **Given** a developer writing a handler, **When** they need to start or resume a durable task, **Then** they call `await my_task.run(task_id=..., input=data)` — no manual lifecycle checks.

2. **Given** a developer who needs to query task status, **When** they call `await my_task.get(task_id)`, **Then** it returns a `TaskInfo` object with the full persisted task state — no `manager._provider.get(...)`.

3. **Given** the public API, **When** a developer inspects it, **Then** all methods and types are importable from `azure.ai.agentserver.core.durable` — nothing from `_manager`, `_models`, `_local_provider`, etc.

4. **Given** the `DurableTask` object (returned by `@durable_task`), **When** a developer examines its methods, **Then** it has: `.run(task_id, input)` for lifecycle-managed synchronous execution, `.start(task_id, input)` for lifecycle-managed background execution, `.get(task_id)` for querying persisted task info.

---

### User Story 4 — Durable LangGraph sample with real crash resilience (Priority: P2)

A developer integrates LangGraph's `StateGraph` with `interrupt()`/`Command(resume=...)` into the durable invocations framework. The graph state is persisted via `SqliteSaver` (or `PostgresSaver` in production). The sample uses the simplified API from User Story 1-3, demonstrating that a real LangGraph agent with multi-turn human-in-the-loop can be built in ~50 lines of application code.

**Why this priority**: LangGraph is the most popular agent framework. A compelling sample proves the platform works with real-world tools. This story depends on Stories 1-3 for the clean API.

**Independent Test**: A developer runs the sample, sends 3 turns via curl, kills the process mid-turn, restarts, and the conversation continues from the last checkpoint without data loss. The graph state (LangGraph checkpoints) and invocation output both survive.

**Acceptance Scenarios**:

1. **Given** a LangGraph StateGraph compiled with `SqliteSaver`, **When** the developer wraps it in a `@durable_task` function and registers it with `InvocationAgentServerHost`, **Then** each POST /invocations runs one turn of the graph and suspends at `interrupt()`.

2. **Given** a running LangGraph session, **When** the process is killed after the graph reaches `interrupt()` but before `ctx.suspend()` is called, **Then** on restart the platform's stale task reconciliation detects the interrupt in the SQLite checkpoint and recovers the session.

3. **Given** a LangGraph sample, **When** the developer examines the code, **Then** there are zero references to `manager._provider`, `TaskPatchRequest`, `get_task_manager`, `handle_resume`, or any internal module.

4. **Given** the sample, **When** the developer reads the invoke handler, **Then** it is under 10 lines: parse input → `await langgraph_session.run(task_id=..., input=...)` → return result.

---

### User Story 5 — Durable multi-turn sample with atomic checkpoints (Priority: P2)

A developer builds a multi-turn conversation agent without LangGraph, using a simple file-based checkpoint store. The sample uses the simplified API and demonstrates atomic checkpoint writes, stale task recovery, and session reuse after completion.

**Why this priority**: Not all developers use LangGraph. This sample proves the platform works with hand-rolled state management too. Depends on Stories 1-3.

**Independent Test**: Same as Story 4 but without LangGraph — kill mid-turn, restart, conversation resumes. Checkpoint files are never corrupt (atomic write via temp+rename).

**Acceptance Scenarios**:

1. **Given** a multiturn sample using `FileCheckpointStore`, **When** the developer writes the invoke handler, **Then** it is under 10 lines — all lifecycle management is handled by `await session_task.run(task_id=..., input=...)`.

2. **Given** a process crash during `checkpoint_store.save()`, **When** the process restarts, **Then** the checkpoint file is either the old valid version or the new valid version — never a partial/corrupt file (atomic write).

3. **Given** a completed session with task_id "session:s1", **When** the client POSTs a new message, **Then** the platform raises `TaskConflictError` — a completed task cannot be restarted. Use a new task_id for a fresh session.

---

### Edge Cases

- What happens when two concurrent `.run()` calls arrive for the same task_id? → Platform serializes via task lease; second call gets `TaskConflictError` since first is already running.
- What happens when a developer uses `.run()` without registering the task function? → `RuntimeError` at call time with descriptive message.
- What happens when the stale task timeout is too aggressive (task is legitimately slow)? → The timeout is configurable; reconciliation checks checkpoint state before resetting, so completed turns are never lost.
- What happens when `ctx.entry_mode` is `"recovered"` but the developer doesn't check it? → Nothing — the function runs normally. Entry mode is informational, not required.
- What happens when the function is resumed but the checkpoint store is empty/corrupt? → `ctx.entry_mode` is `"recovered"` (not `"resumed"`), signaling the developer to handle initialization. The framework logs a warning.
- What happens when the developer's output store is unavailable? → The framework doesn't own output stores. Output persistence is the developer's responsibility — demonstrated in samples but not enforced.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Durable Task Layer (protocol-agnostic)

- **FR-001**: The existing `.run()` and `.start()` methods on `DurableTask` MUST be lifecycle-aware — they atomically handle start-or-resume-or-recover based on the current task state.
- **FR-002**: `.run()` MUST execute synchronously (wait for completion/suspension). `.start()` MUST execute in background (return immediately with a `TaskRun` handle).
- **FR-003**: Both methods MUST follow deterministic lifecycle rules: create and start if no task exists, start if pending, resume if suspended, throw `TaskConflictError` if in-progress (non-stale), recover if in-progress (stale), throw `TaskConflictError` if completed.
- **FR-004**: A public `.get(task_id)` method on `DurableTask` MUST return the full persisted `TaskInfo` for any task state (running, suspended, completed, etc.), or `None` if no task exists.
- **FR-005**: `TaskContext` MUST expose an `entry_mode` property returning `"fresh"`, `"resumed"`, or `"recovered"`.
- **FR-006**: On resume (both developer-initiated and platform-initiated), `ctx.input` contains the resume data — the function always gets its current execution's input via `ctx.input`, regardless of entry mode.
- **FR-007**: Entry mode MUST be purely informational — ignoring it MUST NOT break the function.
- **FR-008**: The platform MUST automatically detect stale `in_progress` tasks (configurable timeout) and reconcile with checkpoint state.
- **FR-009**: Stale task reconciliation MUST check application checkpoint state (graph state, file checkpoint) before deciding to reset — turns that completed before the crash MUST NOT be lost.
- **FR-010**: All lifecycle APIs MUST be importable from `azure.ai.agentserver.core.durable` — no private module imports required.

#### Protocol Packages (invocations, responses, etc.)

- **FR-012**: Protocol packages MUST NOT build higher-order durable task abstractions. They provide HTTP routing, header management, and protocol compliance ONLY.
- **FR-013**: How developers compose durable tasks with protocol endpoints (one-per-invocation, one-per-session, fan-out, mixed) is entirely the developer's concern — not enforced or constrained by the packages.
- **FR-014**: Protocol packages MUST NOT add protocol-specific fields to core types (`TaskContext`, etc.).
- **FR-015**: Per-invocation or per-turn output mapping (e.g., `invocation_id → output`) is developer composition logic, demonstrated in samples but NOT built into the package.

#### Samples & Quality

- **FR-016**: The file-based checkpoint store MUST use atomic writes (temp file + rename) to prevent corruption on crash.
- **FR-017**: LangGraph sample MUST use `SqliteSaver` (not `MemorySaver`) for graph checkpointing to ensure cross-restart durability.
- **FR-018**: Samples MUST NOT import from private modules (`_manager`, `_models`, `_local_provider`). If they need something, it should be part of the public API.

### Key Entities

- **DurableTask**: The registered function + its metadata. Protocol-agnostic. Provides lifecycle-aware `.run()`, `.start()`, and `.get()`.
- **TaskContext**: Execution context passed to the durable function. Now includes `entry_mode`. `ctx.input` always holds the current execution's input (fresh data on start, resume data on resume).
- **EntryMode**: `Literal["fresh", "resumed", "recovered"]` — tells the function why it was entered.
- **TaskConflictError**: Raised when `.run()` or `.start()` encounters a task in `in_progress` (non-stale) or `completed` state.
- **TaskInfo**: Full persisted task information returned by `.get()`.
- **Session**: A logical conversation/workflow. The developer maps sessions to task_ids as they see fit. This is one composition pattern — developers may also use one task per request, fan-out, or custom patterns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The LangGraph sample invoke handler is ≤10 lines of application code (excluding imports and function definition).
- **SC-002**: The multiturn sample invoke handler is ≤10 lines of application code.
- **SC-003**: Zero imports from private modules (`_manager`, `_models`, `_local_provider`) in any sample.
- **SC-004**: Both samples survive kill -9 mid-turn and resume correctly on restart (verified by e2e test).
- **SC-005**: The core `DurableTask` and `TaskContext` types contain zero protocol-specific fields (`invocation_id`, `response_id`, etc.) — verified by code inspection.
- **SC-006**: `ctx.entry_mode` correctly returns `"fresh"`, `"resumed"`, or `"recovered"` in each lifecycle path (verified by unit tests).
- **SC-007**: All public API types pass mypy strict and pyright.

## Assumptions

- The `InvocationAgentServerHost` already injects `x-agent-invocation-id` and `request.state.invocation_id` — this infrastructure is reused. It remains a protocol handler, not an orchestration layer.
- The durable task provider's file-based store is sufficient for local development. The hosted provider (Foundry) is not yet available; a feature flag env var enables it when ready.
- Per-turn output mapping, session management, and task composition patterns are developer concerns demonstrated in samples, not built into packages.
- LangGraph is an optional dependency — the core durable task API works without it. The sample has its own `requirements.txt`.
- The core package supports invocations, responses, and any future protocol — it MUST NOT assume any specific protocol's ID scheme or output model.
- Samples showcase the sticky reentrant session pattern but explicitly note this is one of many valid composition patterns.
