# Feature Specification: TaskResult Wrapper & API Polish

**Feature Branch**: `006-task-result-and-api-polish`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: Backlog items 6 (TaskResult), 9 (callable factories). Container spec §2.1.

## Background & Motivation

Three independently deliverable improvements remain from the container spec gap analysis:

1. **`TaskResult[Output]` wrapper** — Today `result()` returns raw `Output` on success and raises `TaskSuspended` on suspension. For multi-turn agents (LangGraph, workflows), suspension is the *normal* path — every turn ends in a suspend. Raising an exception for the normal path is awkward. `TaskResult` makes suspension a return value alongside completion, with typed output and suspension reason.

2. **Callable factories for decorator options** — `title` already supports `Callable[[Input, str], str]` for dynamic titles. The same pattern should extend to `tags` and `description`, enabling runtime metadata that depends on the input value (e.g., tag by tenant, priority, model).

### What Needs to Change

| Feature | Current State | Target State |
|---------|--------------|--------------|
| `result()` return type | Raw `Output` or raises `TaskSuspended` | `TaskResult[Output]` with `.output`, `.status`, `.is_suspended`, `.suspension_reason` |
| `run()` return type | Raw `Output` or raises `TaskSuspended` | `TaskResult[Output]` |
| `TaskSuspended` exception | Raised by `result()` and `run()` | Kept as a type but no longer raised by `result()`/`run()` — retained for backward-compat import |
| `tags` callable factory | Static `dict[str, str]` only | `dict[str, str] \| Callable[[Input, str], dict[str, str]]` |
| `description` option | Does not exist | `str \| Callable[[Input, str], str] \| None` on decorator |

---

## User Scenarios & Testing

### User Story 1 — TaskResult for Multi-Turn Agents (Priority: P1)

A developer builds a conversational agent where each invocation suspends after processing a turn. Today, the caller must catch `TaskSuspended` as an exception — even though suspension is the expected outcome 90% of the time. With `TaskResult`, the caller pattern becomes:

```python
result = await process_turn.run(task_id="inv-abc", input=turn_input)
if result.is_suspended:
    return {"status": "waiting", "snapshot": result.output, "reason": result.suspension_reason}
return {"status": "done", "output": result.output}
```

**Why this priority**: This is the primary design motivation. Suspension-as-exception is the most awkward API surface in the current design, and multi-turn agents are the primary use case for the AgentServer SDK.

**Independent Test**: A task that suspends with `ctx.suspend(output=snapshot, reason="waiting for user")`. Verify `result.is_suspended == True`, `result.output == snapshot`, `result.suspension_reason == "waiting for user"`.

**Acceptance Scenarios**:

1. **Given** a task that returns normally, **When** `await task.run(...)` completes, **Then** `result.is_completed == True`, `result.output` is the typed return value, `result.suspension_reason is None`.
2. **Given** a task that calls `return await ctx.suspend(output=snapshot, reason="need input")`, **When** `await task.run(...)` completes, **Then** `result.is_suspended == True`, `result.output == snapshot`, `result.suspension_reason == "need input"`.
3. **Given** a task that suspends without output or reason, **When** `await task.run(...)` completes, **Then** `result.is_suspended == True`, `result.output is None`, `result.suspension_reason is None`.
4. **Given** a task that raises an exception, **When** `await task.run(...)` completes, **Then** `TaskFailed` is still raised (NOT wrapped in `TaskResult`).
5. **Given** a cancelled/terminated task, **When** `await task.run(...)` completes, **Then** `TaskCancelled`/`TaskTerminated` is still raised.

---

### User Story 2 — TaskResult with Streaming (Priority: P1)

A developer uses streaming and then awaits the final result. The `TaskResult` wrapper must work correctly when a task both streams chunks and eventually completes or suspends.

**Why this priority**: Streaming + result is a common pattern. The wrapper must not break existing streaming behavior.

**Independent Test**: A task that streams 3 chunks then returns. Consume stream via `async for chunk in task_run`, then `await task_run.result()`. Verify `result.is_completed == True` and all chunks were received.

**Acceptance Scenarios**:

1. **Given** a streaming task that completes, **When** the caller iterates the stream then calls `result()`, **Then** streaming works unchanged AND `result()` returns `TaskResult` with `is_completed == True`.
2. **Given** a streaming task that suspends, **When** the caller iterates the stream then calls `result()`, **Then** `result()` returns `TaskResult` with `is_suspended == True`.

---

### User Story 3 — Callable Factories for Tags (Priority: P3)

A developer wants tags computed from the input at runtime, e.g., tagging by tenant:

```python
@durable_task(
    tags=lambda input, task_id: {"tenant": input.tenant_id, "priority": input.priority},
)
async def process_request(ctx: TaskContext[RequestInput]) -> Response: ...
```

**Why this priority**: Useful for observability and filtering, but developers can set tags per-call today via `.run(tags=...)`. The callable factory is a convenience.

**Independent Test**: Decorate a task with a tags callable. Run the task. Verify the tags on the task record match the callable's output.

**Acceptance Scenarios**:

1. **Given** `@durable_task(tags=lambda input, task_id: {"tenant": input.tenant_id})`, **When** `task.run(task_id="t1", input=RequestInput(tenant_id="acme"))` is called, **Then** the task record has `tags={"tenant": "acme"}`.
2. **Given** a tags callable AND per-call `tags={"extra": "value"}`, **When** run, **Then** per-call tags are merged on top of callable tags.
3. **Given** `@durable_task(tags={"static": "v"})` (static dict, no callable), **When** run, **Then** existing behavior is preserved.

---

### User Story 4 — Callable Factory for Description (Priority: P3)

A developer wants a description generated from input context:

```python
@durable_task(
    description=lambda input, task_id: f"Processing {input.document_name} for {input.user}",
)
async def process_document(ctx: TaskContext[DocInput]) -> DocOutput: ...
```

**Why this priority**: Nice-to-have for observability. Lower priority than tags since description is less commonly queried.

**Independent Test**: Decorate a task with a description callable. Verify the task metadata includes the computed description.

**Acceptance Scenarios**:

1. **Given** `@durable_task(description="static desc")`, **When** run, **Then** task metadata has `description="static desc"`.
2. **Given** `@durable_task(description=lambda input, task_id: f"Processing {input.name}")`, **When** run with `DocInput(name="report.pdf")`, **Then** task metadata has `description="Processing report.pdf"`.
3. **Given** no `description` set, **When** run, **Then** no description in metadata (backward compat).

---

### Edge Cases

- `TaskResult.output` on a completed task that returns `None`: `result.output is None` AND `result.is_completed == True`. Callers distinguish from suspended-without-output via `result.status`.
- `TaskResult` with generic typing: `TaskResult[str].output` should be `str | None` — the `None` covers the suspended-without-output case. Mypy must accept this.
- Callable tags factory that raises: Should propagate the exception at task creation time — fail fast, not at execution time.
- Backward compatibility: Code that catches `TaskSuspended` from `result()` will silently stop catching (the exception is no longer raised). This is a **breaking change** that must be documented.

## Requirements

### Functional Requirements

#### TaskResult Wrapper (P1)

- **FR-001**: `TaskResult[Output]` MUST be a generic class with `output: Output | None`, `status: Literal["completed", "suspended"]`, `suspension_reason: str | None`.
- **FR-002**: `TaskResult` MUST have `is_suspended` and `is_completed` convenience properties.
- **FR-003**: `TaskRun.result()` MUST return `TaskResult[Output]` instead of raw `Output`.
- **FR-004**: `DurableTask.run()` MUST return `TaskResult[Output]` instead of raw `Output`.
- **FR-005**: `TaskFailed`, `TaskCancelled`, `TaskTerminated` MUST still be raised as exceptions from `result()` and `run()`.
- **FR-006**: `TaskSuspended` exception MUST be retained in `_exceptions.py` and `__all__` for backward compatibility, but MUST NOT be raised by `result()` or `run()`.
- **FR-007**: `TaskResult` MUST carry the `task_id` for caller convenience.
- **FR-008**: `TaskResult` MUST be exported from `azure.ai.agentserver.core.durable.__init__` and added to `__all__`.
- **FR-009**: `TaskResult.__repr__` MUST show status, truncated output, and suspension_reason.

#### Callable Factories (P3)

- **FR-010**: `tags` on `@durable_task` MUST accept `dict[str, str] | Callable[[Input, str], dict[str, str]]`.
- **FR-011**: `description` MUST be a new option on `@durable_task` accepting `str | Callable[[Input, str], str] | None`.
- **FR-012**: Callable factories receive `(input_value, task_id)` — same signature as the existing `title` callable.
- **FR-013**: Per-call `tags=` in `.run()` MUST merge on top of callable-resolved tags (same as today with static tags).
- **FR-014**: Callable factories MUST be invoked at task creation time, not at execution time.

### Key Entities

- **`TaskResult[Output]`**: New generic wrapper returned by `result()` and `run()`. Carries output, status, task_id, and suspension_reason.


## Success Criteria

### Measurable Outcomes

- **SC-001**: A multi-turn agent sample that uses `result.is_suspended` instead of `try/except TaskSuspended` — cleaner caller pattern.
- **SC-002**: All existing tests updated to unpack `TaskResult` — no regressions (current count: 227+).
- **SC-003**: `TaskResult` passes mypy/pyright with correct generic typing — `result.output` is `Output | None`.
- **SC-004**: Callable tags factory produces correct tags on the task record.
- **SC-006**: Developer guide updated with `TaskResult`, function-style, and callable factory sections.

## Assumptions

- `description` is stored in task metadata, not as a top-level field on `TaskInfo`. The metadata system already supports arbitrary key-value pairs.
- Backward compatibility: changing `result()` return type from `Output` to `TaskResult[Output]` is a **breaking change**. This is acceptable because the package is still in preview (`0.x` / `b` version).
- The `TaskSuspended` exception class is kept for any code that imported it, but a deprecation warning is NOT added in this spec (can be added later).
