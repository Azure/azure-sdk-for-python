# Research: Cancellation & Timeout

## Current Implementation Analysis

### `_manager.py::_execute_task` (line 596)

This is the execution engine. Key observations:

1. **No timeout wrapping**: `result = await fn(ctx)` runs with no `asyncio.wait_for` or `asyncio.timeout`.
2. **CancelledError handling exists** (line 653): Catches `asyncio.CancelledError`, sets `TaskCancelled` on the future. But nothing triggers the cancel — only external `asyncio.Task.cancel()` would do it.
3. **cancel_event is created** (line 350/518) but never set by the framework — only exposed to user code via `ctx.cancel`.
4. **Retry loop** (line 614): The timeout timer must integrate with the retry loop — timeout should apply to the entire execution (all attempts), not per-attempt.

### Where Timeout Enforcement Goes

The timeout should wrap the task execution in `_execute_task`. Two approaches:

**Option A: asyncio.timeout context manager (Python 3.11+)**
```python
async with asyncio.timeout(opts.timeout.total_seconds()):
    result = await fn(ctx)
```
Problem: Python 3.10 compatibility required. Also, this hard-cancels without grace period.

**Option B: Background timer task (preferred)**
```python
async def _timeout_watchdog(cancel_event, timeout_seconds, grace_seconds, task_ref):
    await asyncio.sleep(timeout_seconds)
    cancel_event.set()  # Cooperative cancel
    await asyncio.sleep(grace_seconds)
    task_ref.cancel()   # Hard cancel
```
This gives the developer a chance to observe `ctx.cancel` and exit cleanly before escalation.

### Where Wait Timeout Goes

`.run()` currently does:
```python
handle = await self._lifecycle_start(...)
return await handle.result()
```

With wait_timeout:
```python
handle = await self._lifecycle_start(...)
return await handle.result(wait_timeout=wait_timeout)
```

And `handle.result()` becomes:
```python
async def result(self, *, wait_timeout: timedelta | None = None) -> Output:
    if wait_timeout is not None:
        try:
            return await asyncio.wait_for(self._result_future, wait_timeout.total_seconds())
        except asyncio.TimeoutError:
            raise TaskWaitTimeout(self.task_id) from None
    return await self._result_future
```

### Where Terminate Goes

`TaskRun.terminate()` needs to:
1. Set `ctx.cancel` (like `cancel()`)
2. Set a `_terminated` flag on the run handle
3. The `_execute_task` CancelledError handler checks the flag to decide between `TaskCancelled` vs `TaskTerminated`
4. The task goes through `_handle_failure` (not `_handle_success`)

### New Files

No new files needed. Changes to:

| File | Changes |
|------|---------|
| `_exceptions.py` | Add `TaskWaitTimeout`, `TaskTerminated` |
| `_run.py` | Add `terminate()`, modify `result()` for `wait_timeout` |
| `_manager.py` | Add timeout watchdog in `_execute_task`, terminate flag handling |
| `_decorator.py` | Add `wait_timeout` param to `.run()`, pass `cancel_grace_seconds` |
| `__init__.py` | Export `TaskWaitTimeout`, `TaskTerminated` |

### New Exception Signatures

```python
class TaskWaitTimeout(Exception):
    """Raised when wait_timeout elapses before task completion."""
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Timed out waiting for task {task_id!r}")

class TaskTerminated(Exception):
    """Raised when a task is forcefully terminated via handle.terminate()."""
    def __init__(self, task_id: str, reason: str | None = None) -> None:
        self.task_id = task_id
        self.reason = reason
        suffix = f": {reason}" if reason else ""
        super().__init__(f"Task {task_id!r} was terminated{suffix}")
```

### Timeout Timer Lifecycle

```
.start() called
    │
    ▼
_execute_task begins
    │
    ├── Start timeout watchdog (if timeout is set)
    │       │
    │       ├── sleep(timeout_seconds)
    │       ├── cancel_event.set()  ← cooperative cancel
    │       ├── sleep(grace_seconds)
    │       └── asyncio_task.cancel()  ← hard cancel
    │
    ├── fn(ctx) runs
    │       │
    │       ├── Observes ctx.cancel? → exits cleanly (success or partial result)
    │       └── Doesn't observe? → gets hard-cancelled after grace period
    │
    ├── On success/suspend: cancel the watchdog
    └── On failure/cancel: cancel the watchdog
```

### Terminate vs Cancel Semantics

| | `cancel()` | `terminate()` |
|---|---|---|
| Sets `ctx.cancel` | ✅ | ✅ |
| Grace period | No escalation | Same escalation as timeout |
| Task stays `in_progress` | Yes (recoverable) | No (failure path) |
| Exception raised | `TaskCancelled` | `TaskTerminated` |
| Ephemeral cleanup | No delete | Delete (same as failure) |

### Thread Safety: terminate flag

The `_terminated` flag must be communicated from the `TaskRun` (caller side) to `_execute_task` (executor side). Options:

- **asyncio.Event** (preferred): `_terminate_event = asyncio.Event()`. The `terminate()` method sets it. The CancelledError handler in `_execute_task` checks it.
- Both `cancel_event` and `terminate_event` are set by `terminate()`. The executor differentiates by checking `terminate_event.is_set()`.

### Impact on retry loop

- **Timeout**: Applies across all retry attempts. If the total time (including retries) exceeds timeout, cancel fires.
- **Cancel/Terminate**: Immediately breaks the retry loop (line 661: `break`). No more retries.
- **Wait timeout**: Independent of execution timeout. The task keeps running even if the caller gives up.
