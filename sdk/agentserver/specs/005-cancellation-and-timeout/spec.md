# Feature Specification: Cancellation & Timeout

**Feature Branch**: `005-cancellation-and-timeout`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: Container spec §9 (Cancellation — Two Independent Channels) and §4.2 (Invoke-and-wait `wait_timeout`). Backlog items 3, 4, 5.

## Background & Motivation

The durable task API currently has:

- `ctx.cancel` — an `asyncio.Event` that can be set cooperatively, but **nothing in the framework fires it automatically**
- `ctx.shutdown` — an `asyncio.Event` for container shutdown, but **nothing wires it to SIGTERM**
- `timeout` parameter on `@durable_task` — the field exists on `DurableTaskOptions` but **there is zero enforcement logic**
- `handle.cancel()` — sets the event, but no escalation to hard cancellation
- No `handle.terminate()`, no `TaskTerminated`, no `TaskWaitTimeout`

The result: developers must implement all timeout and cancellation logic themselves, defeating the purpose of a convenience API.

### What Needs to Change

| Feature | Current State | Target State |
|---------|--------------|--------------|
| `timeout=` on decorator | Field exists, no enforcement | Auto-fires `ctx.cancel` after timeout, escalates to hard cancel |
| `wait_timeout=` on `.run()` | Not implemented | Bounds caller wait; task keeps running; raises `TaskWaitTimeout` |
| `handle.terminate()` | Not implemented | Forced non-recoverable exit; raises `TaskTerminated` |
| Hard cancellation escalation | Not implemented | After grace period, `asyncio.Task.cancel()` fires |
| `TaskWaitTimeout` exception | Does not exist | New exception type |
| `TaskTerminated` exception | Does not exist | New exception type |

### Container Spec Alignment

- **§9.1**: `ctx.cancel` is set by `handle.cancel()`, decorator `timeout=` firing, or `handle.terminate()`
- **§9.1**: Hard cancellation grace period (default 5s) — if developer doesn't observe cancel event, framework escalates to `asyncio.Task.cancel()`
- **§9.2**: `ctx.shutdown` — wired to SIGTERM (out of scope for this spec; already a container-level concern)
- **§4.2**: `wait_timeout=` on `.run()` and `.result()` — bounds caller wait without affecting task execution

---

## User Scenarios & Testing

### User Story 1 — Execution Timeout (Priority: P1)

A developer configures `timeout=timedelta(seconds=30)` on a durable task. If the task function exceeds 30 seconds, `ctx.cancel` is automatically set. If the function doesn't exit within a grace period, it is hard-cancelled.

**Why this priority**: Timeout is the most commonly needed cancellation mechanism. Without it, every developer writes their own `asyncio.wait_for` wrapper.

**Independent Test**: A task with `timeout=timedelta(seconds=1)` that sleeps for 10 seconds. Verify `ctx.cancel` is set after 1 second and the task is terminated after 1s + grace period.

**Acceptance Scenarios**:

1. **Given** `@durable_task(timeout=timedelta(seconds=1))`, **When** the task function sleeps for 10 seconds, **Then** `ctx.cancel.is_set()` becomes True after ~1 second.
2. **Given** a task that observes `ctx.cancel` and returns a partial result, **When** timeout fires, **Then** the task completes normally with the partial result (not a failure).
3. **Given** a task that ignores `ctx.cancel`, **When** timeout + grace period elapses, **Then** the framework hard-cancels via `asyncio.Task.cancel()` and raises `TaskCancelled`.
4. **Given** `timeout=` is not set, **When** the task runs, **Then** no timeout is enforced (current behavior preserved).

---

### User Story 2 — Caller Wait Timeout (Priority: P1)

A developer calls `.run(task_id="t1", input="x", wait_timeout=timedelta(seconds=5))`. If the task doesn't complete within 5 seconds, `.run()` raises `TaskWaitTimeout`. The task keeps running in the background — it is NOT cancelled.

**Why this priority**: In HTTP request handlers, callers need to bound response time without killing long-running work.

**Independent Test**: A task that sleeps 10 seconds. Call `.run()` with `wait_timeout=timedelta(seconds=1)`. Verify `TaskWaitTimeout` is raised and the task is still `in_progress`.

**Acceptance Scenarios**:

1. **Given** `.run(wait_timeout=timedelta(seconds=1))` on a 10-second task, **When** 1 second elapses, **Then** `TaskWaitTimeout` is raised with the `task_id`.
2. **Given** `TaskWaitTimeout` was raised, **When** I call `.get(task_id)`, **Then** the task is still `in_progress` (not cancelled or failed).
3. **Given** `.run()` without `wait_timeout`, **When** the task takes 60 seconds, **Then** `.run()` blocks for 60 seconds (current behavior preserved).
4. **Given** `task_run.result(wait_timeout=timedelta(seconds=1))`, **When** 1 second elapses, **Then** `TaskWaitTimeout` is raised.

---

### User Story 3 — Forced Termination (Priority: P2)

A developer calls `await task_run.terminate()` to forcefully stop a task. Unlike `cancel()` (cooperative), `terminate()` fires `ctx.cancel` AND marks the task as terminated via the failure path — no recovery.

**Why this priority**: Termination is needed for admin scenarios (bad tasks, stuck tasks, resource cleanup) but is less common than timeout/wait.

**Independent Test**: Start a long-running task. Call `terminate()`. Verify `TaskTerminated` is raised and the task does NOT stay `in_progress` for recovery.

**Acceptance Scenarios**:

1. **Given** a running task, **When** `await task_run.terminate()` is called, **Then** `ctx.cancel` is set on the task context.
2. **Given** a terminated task, **When** the caller awaits `task_run.result()`, **Then** `TaskTerminated` is raised (not `TaskCancelled`).
3. **Given** a terminated task, **When** `.start()` is called with the same `task_id`, **Then** the task does NOT recover (unlike cancelled tasks). `TaskConflictError` is raised if non-ephemeral, or fresh start if ephemeral.
4. **Given** `handle.cancel()` is called instead of `terminate()`, **When** the task exits, **Then** the task stays `in_progress` for potential recovery (existing behavior).

---

### Edge Cases

- `timeout=` + `wait_timeout=` both set: `wait_timeout` fires first (caller gives up), `timeout` fires later (task gets cancelled). Both are independent.
- `terminate()` on an already-completed task: No-op or `TaskNotFound` if ephemeral.
- `wait_timeout=timedelta(0)`: Should raise `TaskWaitTimeout` immediately (fire-and-forget semantics — equivalent to `.start()`).
- `timeout=` on a suspended task: Timer resets on each resume (timeout measures active execution time, not wall clock from first start).
- Hard cancellation during `ctx.suspend()`: The suspend should complete cleanly (persist state) before the task is killed.

## Requirements

### Functional Requirements

- **FR-001**: `timeout=timedelta(...)` on `@durable_task` MUST set `ctx.cancel` when elapsed execution time exceeds the timeout.
- **FR-002**: After `ctx.cancel` is set by timeout, the framework MUST wait a grace period (default 5 seconds) before escalating to `asyncio.Task.cancel()`.
- **FR-003**: The hard cancellation grace period MUST be configurable per-task via `cancel_grace_seconds` on the decorator.
- **FR-004**: `.run()` and `task_run.result()` MUST accept `wait_timeout: timedelta | None = None`.
- **FR-005**: When `wait_timeout` elapses, `TaskWaitTimeout` MUST be raised. The task MUST continue running.
- **FR-006**: `TaskWaitTimeout` MUST include the `task_id` so the caller can follow up.
- **FR-007**: `TaskRun` MUST have a `terminate()` method that sets `ctx.cancel` and flags the outcome as terminated.
- **FR-008**: Terminated tasks MUST go through the failure path (§8.3 of container spec) — NOT stay `in_progress` for recovery.
- **FR-009**: `TaskTerminated` MUST be raised by `.run()` / `task_run.result()` when a task is terminated.
- **FR-010**: `TaskWaitTimeout` and `TaskTerminated` MUST be exported from `azure.ai.agentserver.core.durable.__init__` and added to `__all__`.
- **FR-011**: Timeout timer MUST reset on resume — it measures active execution time per entry, not total wall clock.
- **FR-012**: Per-call `timeout=` override on `.run()` and `.start()` MUST be supported (overrides decorator default).

### Non-Functional Requirements

- **NR-001**: Timeout enforcement MUST NOT add measurable overhead (<1ms) when `timeout=None`.
- **NR-002**: All new exceptions MUST follow the existing pattern in `_exceptions.py` (slots, `task_id` attribute, clear message).
- **NR-003**: Existing tests MUST continue to pass without modification.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A task with `timeout=timedelta(seconds=1)` is cancelled within 1s + grace period.
- **SC-002**: `.run(wait_timeout=timedelta(seconds=1))` raises `TaskWaitTimeout` within ~1 second.
- **SC-003**: `terminate()` prevents task recovery — subsequent `.start()` on non-ephemeral tasks raises `TaskConflictError`.
- **SC-004**: All existing 221+ tests pass without modification.
- **SC-005**: Developer guide updated with timeout and termination sections.

## Assumptions

- `ctx.shutdown` wiring to SIGTERM is out of scope — it's a container-level concern handled by the host framework.
- The `TaskOutcome` discriminated union (backlog item 6) is out of scope — that's a separate API design.
- `ctx.deadline()` helper (container spec §9.3) is a nice-to-have, not required for this spec.
