# Public API Contract: Durable Tasks

**Package**: `azure-ai-agentserver-core`  
**Module**: `azure.ai.agentserver.core.durable`  
**Re-export**: `azure.ai.agentserver.core` (top-level `__init__.py`)

---

## Public Exports

```python
from azure.ai.agentserver.core.durable import (
    # Decorator
    durable_task,

    # Types
    DurableTask,
    TaskContext,
    TaskRun,
    TaskMetadata,
    Suspended,
    TaskStatus,

    # Exceptions
    TaskFailed,
    TaskSuspended,
    TaskCancelled,
    TaskNotFound,
)
```

---

## 1. `@durable_task` Decorator

```python
def durable_task(
    fn: Callable[[TaskContext[Input]], Awaitable[Output]] | None = None,
    *,
    name: str | None = None,
    title: str | Callable[[Input, str], str] | None = None,
    tags: dict[str, str] | None = None,
    timeout: timedelta | None = None,
    lease_duration_seconds: int = 60,
    store_input: bool = True,
    ephemeral: bool = True,
) -> DurableTask[Input, Output] | Callable[..., DurableTask[Input, Output]]:
    """Turn an async function into a crash-resilient durable task.

    Can be used with or without arguments:

        @durable_task
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...

        @durable_task(name="custom-name", ephemeral=False)
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...
    """
```

---

## 2. `DurableTask[Input, Output]`

```python
class DurableTask(Generic[Input, Output]):
    """A decorated durable task function. Not callable directly."""

    name: str

    async def run(
        self,
        *,
        task_id: str,
        input: Input,
        session_id: str | None = None,
        title: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> Output:
        """Create a task, run the function, and return the result.

        Blocks until the function completes, suspends, or fails.

        :raises TaskFailed: If the function raises an unhandled exception.
        :raises TaskSuspended: If the function suspends.
        :raises TaskNotFound: If the task is deleted externally during execution.
        """

    async def start(
        self,
        *,
        task_id: str,
        input: Input,
        session_id: str | None = None,
        title: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> TaskRun[Output]:
        """Create a task, start the function, and return a handle immediately."""

    def options(
        self,
        *,
        title: str | Callable[[Input, str], str] | None = None,
        tags: dict[str, str] | None = None,
        timeout: timedelta | None = None,
        lease_duration_seconds: int | None = None,
        store_input: bool | None = None,
        ephemeral: bool | None = None,
    ) -> DurableTask[Input, Output]:
        """Return a new DurableTask with merged options. Original is unchanged."""
```

---

## 3. `TaskContext[Input]`

```python
class TaskContext(Generic[Input]):
    """The single parameter to a durable task function."""

    # Identity (read-only)
    task_id: str
    title: str
    session_id: str
    agent_name: str
    tags: dict[str, str]

    # Input (immutable, typed)
    input: Input

    # Mutable progress
    metadata: TaskMetadata

    # Observability counters (read-only)
    run_attempt: int
    lease_generation: int

    # Cancellation signals (read-only references)
    cancel: asyncio.Event
    shutdown: asyncio.Event

    async def suspend(
        self,
        *,
        reason: str | None = None,
        output: Output | None = None,
    ) -> Suspended[Output]:
        """Suspend the task. Must be used as: return await ctx.suspend(...)"""
```

---

## 4. `TaskRun[Output]`

```python
class TaskRun(Generic[Output]):
    """Handle to a running or completed durable task."""

    task_id: str
    status: TaskStatus

    @property
    def metadata(self) -> TaskMetadata: ...

    async def result(self) -> Output:
        """Await task completion and return the typed output.

        :raises TaskFailed: If the function raised an exception.
        :raises TaskSuspended: If the task was suspended.
        :raises TaskCancelled: If the task was cancelled.
        :raises TaskNotFound: If the task was deleted.
        """

    async def cancel(self) -> None:
        """Signal cancellation to the running task."""

    async def delete(self) -> None:
        """Delete the task record from the store."""

    async def refresh(self) -> None:
        """Re-fetch task state from the store."""
```

---

## 5. `TaskMetadata`

```python
class TaskMetadata:
    """Mutable progress dict persisted to the task record."""

    def set(self, key: str, value: Any) -> None: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def increment(self, key: str, delta: int = 1) -> None: ...
    def append(self, key: str, value: Any) -> None: ...
    def to_dict(self) -> dict[str, Any]: ...
    async def flush(self) -> None:
        """Force-flush pending metadata changes to the store."""
```

---

## 6. `Suspended[Output]`

```python
class Suspended(Generic[Output]):
    """Sentinel return value from ctx.suspend(). Framework interprets this on return."""

    reason: str | None
    output: Output | None
```

---

## 7. `TaskStatus`

```python
TaskStatus = Literal["pending", "in_progress", "suspended", "completed"]
```

---

## 8. Exception Types

```python
class TaskFailed(Exception):
    task_id: str
    error: dict[str, Any]

class TaskSuspended(Exception):
    task_id: str
    reason: str | None
    output: Any | None

class TaskCancelled(asyncio.CancelledError):
    task_id: str

class TaskNotFound(Exception):
    task_id: str
```

---

## 9. Resume Route (Auto-Registered)

```
POST /tasks/resume
Content-Type: application/json

{
    "task_id": "my-task-123"
}

→ 202 Accepted (empty body)
→ 404 Not Found (empty body)
→ 409 Conflict (empty body)
```

---

## 10. Host Integration

The durable task subsystem integrates with `AgentServerHost` via:

```python
# In host __init__ or startup:
app.tasks = DurableTaskManager(config=app.config)

# Auto-register resume route:
app.routes.append(Route("/tasks/resume", app.tasks._handle_resume_request, methods=["POST"]))

# Register shutdown callback:
app._shutdown_fn = app.tasks.shutdown
```

Protocol packages access tasks via `self.tasks` (inherited from `AgentServerHost`).
