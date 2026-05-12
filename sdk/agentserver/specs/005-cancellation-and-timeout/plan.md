# Implementation Plan: Cancellation & Timeout

**Branch**: `005-cancellation-and-timeout` | **Date**: 2026-05-12 | **Spec**: `specs/005-cancellation-and-timeout/spec.md`  
**Input**: Feature specification from `/specs/005-cancellation-and-timeout/spec.md`

## Summary

Add three missing cancellation/timeout features to the durable task subsystem: execution timeout enforcement via a background watchdog, caller-side wait timeout on `.run()` and `.result()`, and forced termination via `handle.terminate()`. Two new exception types (`TaskWaitTimeout`, `TaskTerminated`) are added to the public API.

## Technical Context

**Language/Version**: Python 3.10+ (no `asyncio.timeout` — use `asyncio.wait_for` and manual watchdog)  
**Primary Dependencies**: `azure-ai-agentserver-core` (durable module)  
**Storage**: N/A (uses existing task store)  
**Testing**: pytest with pytest-asyncio, existing e2e test infrastructure  
**Target Platform**: Linux containers (ASGI hosts)  
**Project Type**: Library  
**Performance Goals**: <1ms overhead when `timeout=None`  
**Constraints**: Python 3.10 compatibility, no new dependencies

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| II. Strong Type Safety | ✅ PASS | New exceptions use `__slots__`, all methods typed |
| III. Azure SDK Compliance | ✅ PASS | Follows existing exception and parameter patterns |
| IV. Async-First | ✅ PASS | Watchdog uses `asyncio.create_task`, `asyncio.wait_for` |
| VII. Minimal Surface | ✅ PASS | 2 new exceptions, 1 new method, 2 new parameters |
| Sample E2E Tests | ✅ Required | New tests for timeout, wait_timeout, terminate |

No constitution violations.

## Project Structure

### Source Changes

```text
azure-ai-agentserver-core/azure/ai/agentserver/core/durable/
├── __init__.py          # Add TaskWaitTimeout, TaskTerminated to __all__
├── _exceptions.py       # Add TaskWaitTimeout, TaskTerminated classes
├── _run.py              # Add terminate(), modify result() for wait_timeout
├── _manager.py          # Add timeout watchdog, terminate_event threading
└── _decorator.py        # Add wait_timeout param to .run(), cancel_grace_seconds
```

### Test Changes

```text
azure-ai-agentserver-core/tests/durable/
└── test_cancellation_timeout.py    # New test file for all 3 features
```

### Documentation Changes

```text
azure-ai-agentserver-core/docs/
└── durable-task-developer-guide.md  # Update with timeout + terminate sections
```

## Architecture

### Timeout Watchdog Design

The watchdog is a background `asyncio.Task` started alongside the execution task. It provides a two-phase cancellation:

```
Phase 1: Cooperative cancel
    sleep(timeout_seconds)
    cancel_event.set()  ← developer can observe ctx.cancel

Phase 2: Hard cancel (escalation)
    sleep(cancel_grace_seconds)  # default 5s
    execution_task.cancel()  ← asyncio.CancelledError at next await
```

The watchdog is cancelled when the task completes normally (success, suspend, or failure). If the developer observes `ctx.cancel` and exits cleanly during Phase 1, the hard cancel never fires.

### Terminate Event Threading

`terminate()` needs a communication channel from `TaskRun` (caller) to `_execute_task` (executor):

1. A shared `asyncio.Event` (`_terminate_event`) is created when the `TaskRun` is constructed
2. `terminate()` sets both `_cancel_event` and `_terminate_event`
3. In `_execute_task`, the `CancelledError` handler checks `terminate_event.is_set()`:
   - If set → `TaskTerminated` (failure path, no recovery)
   - If not → `TaskCancelled` (existing behavior)

### Wait Timeout Design

`wait_timeout` is purely caller-side — it wraps `asyncio.wait_for` around the result future:

```python
async def result(self, *, wait_timeout: timedelta | None = None) -> Output:
    if wait_timeout is not None:
        try:
            return await asyncio.wait_for(
                asyncio.shield(self._result_future),
                wait_timeout.total_seconds(),
            )
        except asyncio.TimeoutError:
            raise TaskWaitTimeout(self.task_id) from None
    return await self._result_future
```

Note: `asyncio.shield` is critical — without it, `wait_for` would cancel the future itself, which would cancel the task. We want the task to keep running.

## Dependencies & Execution Order

### Phase Dependencies

1. **Phase 1 (Exceptions)**: No dependencies — pure new types
2. **Phase 2 (Wait Timeout)**: Depends on Phase 1 (`TaskWaitTimeout`)
3. **Phase 3 (Terminate)**: Depends on Phase 1 (`TaskTerminated`)
4. **Phase 4 (Execution Timeout)**: Depends on Phase 3 (shares terminate/cancel event pattern)
5. **Phase 5 (Tests)**: Depends on all implementation phases
6. **Phase 6 (Docs + Polish)**: Depends on Phase 5

### Parallelism

- Phase 2 and Phase 3 can run in parallel (independent features, different files)
- All Phase 5 tests can be written in parallel (independent test methods)
