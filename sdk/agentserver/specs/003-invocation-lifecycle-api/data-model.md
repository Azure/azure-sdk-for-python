# Data Model: Durable Task Lifecycle Automation & Public API Simplification

**Phase 1 artifact** — Exact class definitions for the new types and modifications.

## 1. EntryMode (type alias — `_context.py`)

```python
from typing import Literal

EntryMode = Literal["fresh", "resumed", "recovered"]
"""Why the durable function was entered.

- ``"fresh"`` — First execution. Task was just created.
- ``"resumed"`` — Re-entered after suspension. On developer-initiated resume
  (via ``.run()``), ``ctx.input`` contains the new input. On platform-initiated
  resume (via ``/tasks/{task_id}/resume``), ``ctx.input`` contains the task's
  persisted input.
- ``"recovered"`` — Re-entered after stale task detection. The previous execution
  crashed or timed out. ``ctx.input`` contains the task's persisted input.
"""
```

Not a class — just a type alias. Zero runtime overhead. Used in `TaskContext`.

## 2. TaskContext Changes (`_context.py`)

```python
class TaskContext(Generic[Input]):
    __slots__ = (
        "task_id",
        "title",
        "session_id",
        "agent_name",
        "tags",
        "input",
        "metadata",
        "run_attempt",
        "lease_generation",
        "cancel",
        "shutdown",
        "_suspend_callback",
        "_stream_queue",
        "entry_mode",           # ← NEW
    )

    def __init__(
        self,
        *,
        task_id: str,
        title: str,
        session_id: str,
        agent_name: str,
        tags: dict[str, str],
        input: Input,
        metadata: TaskMetadata,
        run_attempt: int = 0,
        lease_generation: int = 0,
        cancel: asyncio.Event | None = None,
        shutdown: asyncio.Event | None = None,
        stream_queue: asyncio.Queue[Any] | None = None,
        entry_mode: EntryMode = "fresh",    # ← NEW
    ) -> None:
        # ... existing assignments ...
        self.entry_mode = entry_mode
```

### Changes from current:
- Add `"entry_mode"` to `__slots__`
- Add `entry_mode: EntryMode = "fresh"` parameter to `__init__`
- Default is `"fresh"` — backwards compatible with all existing callers
- `ctx.input` always holds the current execution's input (no separate `resume_input`)

## 3. TaskConflictError (new exception — `_exceptions.py`)

```python
class TaskConflictError(RuntimeError):
    """Raised when a task lifecycle conflict cannot be resolved.

    Raised by ``.run()`` or ``.start()`` when the task is already
    ``in_progress`` (non-stale) or ``completed``. The lifecycle is
    deterministic: create if none, start if pending, resume if suspended,
    throw if in-progress or completed.

    :param task_id: The conflicting task's ID.
    :type task_id: str
    :param current_status: The task's current status.
    :type current_status: str
    """

    __slots__ = ("task_id", "current_status")

    def __init__(
        self,
        task_id: str,
        current_status: str,
    ) -> None:
        self.task_id = task_id
        self.current_status = current_status
        super().__init__(
            f"Task '{task_id}' is already {current_status}"
        )
```

### Design notes:
- Extends `RuntimeError` (not `Exception` subclass that would be caught by broad handlers)
- Placed in `_exceptions.py` alongside existing `TaskFailed`, `TaskSuspended`, etc.

## 5. DurableTask Method Additions (`_decorator.py`)

## 4. DurableTask Method Changes (`_decorator.py`)

### `.run()` and `.start()` — now lifecycle-aware

The existing `.run()` and `.start()` methods gain lifecycle awareness. Before executing, they check the current task state and act accordingly. Signatures gain a `stale_timeout` parameter; return types are unchanged.

```python
async def run(
    self,
    *,
    task_id: str,
    input: Input,
    title: str | None = None,
    tags: dict[str, str] | None = None,
    stale_timeout: float = 300.0,
    retry: RetryPolicy | None = None,
    source: dict[str, Any] | None = None,
) -> Output:
    # Lifecycle check → then execute synchronously (wait for result)

async def start(
    self,
    *,
    task_id: str,
    input: Input,
    title: str | None = None,
    tags: dict[str, str] | None = None,
    stale_timeout: float = 300.0,
    retry: RetryPolicy | None = None,
    source: dict[str, Any] | None = None,
) -> TaskRun[Output]:
    # Lifecycle check → then execute in background (return handle)
```

**Lifecycle logic** (shared between `.run()` and `.start()`):

```
existing = provider.get(task_id)

if existing is None:
    # Fresh start — no task exists
    create_and_start(entry_mode="fresh", ...)

elif existing.status == "pending":
    # Start pending task
    start(task_id, entry_mode="fresh", ...)

elif existing.status == "suspended":
    # Resume: patch input, call handle_resume
    provider.patch(task_id, payload={"input": input})
    handle_resume(task_id, entry_mode="resumed")

elif existing.status == "in_progress":
    if is_stale(existing, stale_timeout):
        # Recover: reset and re-execute
        recover_stale(task_id, input, entry_mode="recovered")
    else:
        raise TaskConflictError(task_id, "in_progress")

elif existing.status == "completed":
    raise TaskConflictError(task_id, "completed")
```

### `.get()` — query persisted task info

```python
async def get(self, task_id: str) -> TaskInfo | None:
    """Return the full persisted task information.

    Works for any task state — running, suspended, completed, etc.
    Returns whatever is persisted. Returns None if no task exists.

    :param task_id: The task identifier.
    :type task_id: str
    :return: Task info or None if no task exists.
    :rtype: ~azure.ai.agentserver.core.durable.TaskInfo | None
    """
    manager = get_task_manager()
    try:
        return await manager._provider.get(task_id)
    except TaskNotFound:
        return None
```

### Design notes:
- `.get()` accesses `manager._provider` internally — but the developer doesn't need to
- `TaskInfo` is already defined in `_models.py` — needs to be added to public exports
- Lifecycle logic is shared between `.run()` and `.start()` — extracted into a helper method

## 5. Stale Task Detection

```python
def _is_stale(task: TaskInfo, timeout: float) -> bool:
    """Check if an in_progress task is stale (likely crashed)."""
    if not task.updated_at:
        return False
    updated = datetime.fromisoformat(task.updated_at)
    return (datetime.utcnow() - updated).total_seconds() > timeout
```

- Default timeout: 300 seconds (5 minutes)
- Configurable via `stale_timeout` parameter on `.run()` and `.start()`
- Only applies to `in_progress` tasks — suspended/completed are never stale
- Recovery involves checking application checkpoint state before resetting

## Summary of Changes

| File | Change | New Types |
|------|--------|-----------|
| `_context.py` | Add `entry_mode` slot + param | `EntryMode` type alias |
| `_exceptions.py` | Add `TaskConflictError` | `TaskConflictError` |
| `_decorator.py` | Make `.run()`/`.start()` lifecycle-aware, add `.get()` | — |
| `_manager.py` | Wire entry_mode through all paths | — |
| `__init__.py` | Export new types + `TaskInfo` | — |
