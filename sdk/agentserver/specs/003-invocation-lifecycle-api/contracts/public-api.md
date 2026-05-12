# Public API Contract: Durable Task Lifecycle Automation & Public API Simplification

**Phase 1 artifact** — Changes to the public API surface.

## New Exports

### `azure.ai.agentserver.core.durable`

```python
# Added to __all__:
"EntryMode"
"TaskConflictError"
"TaskInfo"           # was internal-only, now public
```

### `azure.ai.agentserver.core`

```python
# Added to __all__ (re-export):
"EntryMode"
"TaskConflictError"
"TaskInfo"
```

## New Type: `EntryMode`

```python
from typing import Literal

EntryMode = Literal["fresh", "resumed", "recovered"]
```

A type alias, not a class. Describes why the durable function was entered.

## New Class: `TaskConflictError`

```python
class TaskConflictError(RuntimeError):
    """Raised when a task lifecycle conflict cannot be resolved."""

    task_id: str
    current_status: str
```

Raised by `.run()` or `.start()` when the task is already in-progress (non-stale) or completed.

## Modified Class: `TaskContext`

```python
class TaskContext(Generic[Input]):
    # Existing attributes unchanged...
    task_id: str
    title: str
    session_id: str
    agent_name: str
    tags: dict[str, str]
    input: Input
    metadata: TaskMetadata
    run_attempt: int
    lease_generation: int
    cancel: asyncio.Event
    shutdown: asyncio.Event

    # NEW
    entry_mode: EntryMode    # "fresh", "resumed", or "recovered"

    # Existing methods unchanged...
    async def suspend(self, *, reason: str | None = None, output: Any = None) -> Suspended: ...
    async def stream(self, item: Any) -> None: ...
```

## Modified Class: `DurableTask`

```python
class DurableTask(Generic[Input, Output]):
    # Existing attributes unchanged...
    name: str

    # MODIFIED — now lifecycle-aware (start/resume/recover automatically)
    async def run(self, *, task_id: str, input: Input, stale_timeout: float = 300.0, ...) -> Output: ...
    async def start(self, *, task_id: str, input: Input, stale_timeout: float = 300.0, ...) -> TaskRun[Output]: ...

    # Existing, unchanged
    def options(self, ...) -> DurableTask[Input, Output]: ...

    # NEW — query persisted task info
    async def get(self, task_id: str) -> TaskInfo | None: ...
```

## Newly Public Type: `TaskInfo`

```python
class TaskInfo:
    """Task metadata returned by the provider. Now part of public API."""

    id: str
    agent_name: str
    session_id: str
    status: str
    title: str | None
    source: dict[str, Any] | None
    created_at: str
    updated_at: str
    # ... other fields
```

Previously internal (`_models.py`). Now exported because `.get()` returns it.

## Complete Updated `__all__`

```python
__all__ = [
    # Existing (unchanged)
    "durable_task",
    "DurableTask",
    "DurableTaskOptions",
    "RetryPolicy",
    "TaskContext",
    "TaskMetadata",
    "TaskRun",
    "Suspended",
    "TaskStatus",
    "TaskFailed",
    "TaskSuspended",
    "TaskCancelled",
    "TaskNotFound",
    # New
    "EntryMode",
    "TaskConflictError",
    "TaskInfo",
]
```

## Backward Compatibility

All changes are **purely additive**:
- `TaskContext.__init__` gains `entry_mode` with default `"fresh"` — existing callers unaffected
- `.run()` and `.start()` gain lifecycle awareness + `stale_timeout` param — existing calls that create new tasks work exactly as before (no existing task = fresh start)
- `DurableTask` gains `.get()` — existing `.options()` unchanged
- New types are new exports — no removals or renames

## Developer Experience: Before vs After

### Before (current)
```python
from azure.ai.agentserver.core.durable._manager import get_task_manager
from azure.ai.agentserver.core.durable._models import TaskPatchRequest

manager = get_task_manager()
task_id = f"session:{session_id}"
existing = await manager._provider.get(task_id)

if existing and existing.status == "suspended":
    await manager._provider.patch(task_id, TaskPatchRequest(payload={"input": data}))
    await manager.handle_resume(task_id)
elif existing and existing.status == "in_progress":
    return {"error": "already running"}
else:
    run = await my_task.start(task_id=task_id, input=data)
```

### After (new API)
```python
from azure.ai.agentserver.core.durable import durable_task, TaskContext

output = await my_task.run(task_id=f"session:{session_id}", input=data)
# Platform handles start/resume/recover automatically
# ctx.entry_mode inside the function tells you why it was entered
```

**30+ lines → 1 line. 5 private imports → 0 private imports. No new types to learn.**
