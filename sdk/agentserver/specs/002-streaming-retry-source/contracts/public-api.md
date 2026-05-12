# Public API Contract: Streaming, Retry Policies, and Source Field

**Phase 1 artifact** — Additions to the public API surface.

## New Exports

### `azure.ai.agentserver.core.durable`

```python
# Added to __all__:
"RetryPolicy"
```

### `azure.ai.agentserver.core`

```python
# Added to __all__ (re-export):
"RetryPolicy"
```

## New Class: `RetryPolicy`

```python
from datetime import timedelta

class RetryPolicy:
    """Retry configuration for durable tasks."""

    # Read-only attributes (set in __init__)
    initial_delay: timedelta
    backoff_coefficient: float
    max_delay: timedelta
    max_attempts: int
    retry_on: tuple[type[Exception], ...] | None
    jitter: bool

    def __init__(
        self,
        *,
        initial_delay: timedelta = timedelta(seconds=1),
        backoff_coefficient: float = 2.0,
        max_delay: timedelta = timedelta(seconds=60),
        max_attempts: int = 3,
        retry_on: tuple[type[Exception], ...] | None = None,
        jitter: bool = True,
    ) -> None: ...

    def compute_delay(self, attempt: int) -> float: ...
    def should_retry(self, attempt: int, error: Exception) -> bool: ...

    @classmethod
    def exponential_backoff(cls, *, max_attempts: int = 3) -> RetryPolicy: ...
    @classmethod
    def fixed_delay(cls, *, delay: timedelta = timedelta(seconds=5), max_attempts: int = 3) -> RetryPolicy: ...
    @classmethod
    def linear_backoff(cls, *, initial_delay: timedelta = timedelta(seconds=1), max_attempts: int = 5) -> RetryPolicy: ...
    @classmethod
    def no_retry(cls) -> RetryPolicy: ...
```

## Modified Signatures

### `@durable_task` decorator

```python
# Before:
@durable_task(
    title="...",
    tags={...},
    session_id="...",
    timeout=timedelta(...),
)

# After — added retry and source:
@durable_task(
    title="...",
    tags={...},
    session_id="...",
    timeout=timedelta(...),
    retry=RetryPolicy.exponential_backoff(),     # NEW
    source={"origin": "decorator", "v": "1.0"},  # NEW
)
```

### `DurableTask.run()` and `.start()`

```python
# Before:
result = await my_task.run(task_id="t1", input=MyInput(...))
run = await my_task.start(task_id="t1", input=MyInput(...))

# After — added retry, source overrides:
result = await my_task.run(
    task_id="t1",
    input=MyInput(...),
    retry=RetryPolicy.fixed_delay(),            # NEW — overrides decorator
    source={"origin": "api", "req": "r1"},      # NEW — overrides decorator
)

run = await my_task.start(
    task_id="t1",
    input=MyInput(...),
    retry=RetryPolicy.exponential_backoff(),    # NEW
    source={"origin": "api", "req": "r2"},      # NEW
)
```

### `TaskContext.stream()`

```python
# NEW method on existing class:
class TaskContext(Generic[Input]):
    async def stream(self, item: Any) -> None:
        """Emit a streaming item. In-memory only, not persisted."""
        ...
```

### `TaskRun` async iteration

```python
# NEW protocol on existing class:
class TaskRun(Generic[Output]):
    def __aiter__(self) -> TaskRun[Output]: ...
    async def __anext__(self) -> Any: ...

# Usage:
run = await my_task.start(task_id="t1", input=inp)
async for chunk in run:
    print(chunk)  # streaming items
result = await run.result()  # final result
```

### `TaskInfo.source`

```python
# NEW attribute on existing class:
class TaskInfo:
    source: dict[str, Any] | None  # set at creation, immutable
```

## Backward Compatibility

All changes are **additive**:

- `RetryPolicy` is a new class — no existing code affected
- `retry` and `source` parameters default to `None` — existing decorator/call usage unchanged
- `TaskContext.stream()` is opt-in — tasks that don't call it work identically to before
- `TaskRun.__aiter__` is opt-in — existing `await run.result()` still works
- `TaskInfo.source` defaults to `None` — existing tasks without source are unaffected
- `TaskCreateRequest.source` defaults to `None` — existing create calls work unchanged
