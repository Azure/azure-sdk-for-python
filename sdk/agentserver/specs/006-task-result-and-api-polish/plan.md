# Implementation Plan: TaskResult Wrapper & API Polish

**Branch**: `006-task-result-and-api-polish` | **Date**: 2026-05-12 | **Spec**: `specs/006-task-result-and-api-polish/spec.md`  
**Input**: Feature specification from `/specs/006-task-result-and-api-polish/spec.md`

## Summary

Two independently deliverable improvements to the durable task API surface:

1. **`TaskResult[Output]` wrapper (P1)** — Change `result()` and `run()` to return `TaskResult[Output]` instead of raw `Output`. This makes suspension a return value (with `.is_suspended`, `.output`, `.suspension_reason`) instead of raising `TaskSuspended`. Failures/cancel/terminate remain exceptions.

2. **Callable factories for `tags` and `description` (P3)** — Extend the existing `title` callable pattern (`Callable[[Input, str], T]`) to `tags` and a new `description` option on the decorator.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: `azure-ai-agentserver-core` (durable module)  
**Storage**: N/A (uses existing task store)  
**Testing**: pytest with pytest-asyncio, existing 227+ tests  
**Target Platform**: Linux containers (ASGI hosts)  
**Project Type**: Library  
**Constraints**: Python 3.10 compatibility, no new dependencies

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| II. Strong Type Safety | ✅ PASS | `TaskResult` is generic, fully typed with `__slots__` |
| III. Azure SDK Compliance | ✅ PASS | Follows existing patterns for return types and decorators |
| IV. Async-First | ✅ PASS | No async changes — `TaskResult` is a synchronous wrapper |
| VII. Minimal Surface | ✅ PASS | 1 new class (`TaskResult`), 1 new decorator option (`description`), callable extension for `tags` |
| Sample E2E Tests | ✅ Required | Update existing tests + new tests for `TaskResult` |

No constitution violations.

## Project Structure

### Source Changes

```text
azure-ai-agentserver-core/azure/ai/agentserver/core/durable/
├── __init__.py          # Add TaskResult to __all__
├── _result.py           # NEW — TaskResult[Output] class
├── _run.py              # Change result() return type to TaskResult[Output]
├── _manager.py          # Create TaskResult instead of set_result/set_exception for suspend
├── _decorator.py        # Change run() return type, add description option, callable tags
└── _exceptions.py       # TaskSuspended retained but no longer raised by result()/run()
```

### Test Changes

```text
azure-ai-agentserver-core/tests/durable/
├── test_task_result.py           # NEW — TaskResult wrapper tests
├── test_callable_factories.py    # NEW — callable tags/description tests  
└── test_*.py                     # EXISTING — update to unpack TaskResult from result()/run()
```

### Documentation Changes

```text
azure-ai-agentserver-core/docs/
└── durable-task-developer-guide.md  # Update result patterns, add callable factory docs
```

## Architecture

### TaskResult Design

`TaskResult[Output]` is a simple generic container. It replaces two current paths:

**Before:**
```python
# Success → raw Output
result = await task.run(...)   # returns Output directly

# Suspension → exception
try:
    result = await task.run(...)
except TaskSuspended as e:
    snapshot = e.output
    reason = e.reason
```

**After:**
```python
result = await task.run(...)   # returns TaskResult[Output]
if result.is_completed:
    output = result.output     # typed Output
elif result.is_suspended:
    snapshot = result.output   # Output | None
    reason = result.suspension_reason
```

The key change is in `_manager.py` `_execute_task_loop`:
- **Success path**: `result_future.set_result(TaskResult(output=result, status="completed", task_id=task_id))`
- **Suspend path**: `result_future.set_result(TaskResult(output=result.output, status="suspended", task_id=task_id, suspension_reason=result.reason))`
- **Failure/cancel/terminate**: Unchanged — still `result_future.set_exception(...)`

This means the future type changes from `asyncio.Future[Output]` to `asyncio.Future[TaskResult[Output]]`.

### Callable Factory Resolution

The existing `_resolve_title` pattern in `DurableTask`:

```python
def _resolve_title(self, input_val: Input, task_id: str) -> str:
    if callable(self._opts.title):
        return self._opts.title(input_val, task_id)
    if isinstance(self._opts.title, str):
        return self._opts.title
    return f"{self.name}:{task_id[:8]}"
```

This same pattern extends to `_resolve_tags` and `_resolve_description`. The resolution happens at task creation time (inside `_lifecycle_start`), not at execution time.

## Dependencies & Execution Order

### Phase Dependencies

1. **Phase 1 (TaskResult class)**: No dependencies — pure new type
2. **Phase 2 (Wire TaskResult)**: Depends on Phase 1 — changes manager, run, decorator
3. **Phase 3 (Update existing tests)**: Depends on Phase 2 — all tests need TaskResult unpacking
4. **Phase 4 (Callable factories)**: Independent of Phase 1-3 — can be done in parallel
5. **Phase 5 (New tests)**: Depends on Phase 2 and Phase 4
6. **Phase 6 (Docs + polish)**: Depends on all

### Parallelism

- Phase 4 (callable factories) can run in parallel with Phases 1-3 (TaskResult)
- All new tests in Phase 5 can be written in parallel

## Complexity Tracking

No constitution violations requiring justification.
