# Data Model: Streaming, Retry Policies, and Source Field

**Phase 1 artifact** — Exact class definitions for the three new features.

## 1. RetryPolicy (new class — `_retry.py`)

```python
class RetryPolicy:
    """Retry configuration for durable tasks.

    Delay formula: min(initial_delay * backoff_coefficient ^ attempt, max_delay)
    When jitter=True, ±25% randomization is applied to the computed delay.
    """

    __slots__ = (
        "initial_delay",
        "backoff_coefficient",
        "max_delay",
        "max_attempts",
        "retry_on",
        "jitter",
    )

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

    def compute_delay(self, attempt: int) -> float:
        """Return delay in seconds for the given attempt number (0-based)."""
        ...

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Return True if the task should be retried for this error and attempt."""
        ...

    # Convenience presets (class methods)
    @classmethod
    def exponential_backoff(cls, *, max_attempts: int = 3) -> RetryPolicy: ...

    @classmethod
    def fixed_delay(cls, *, delay: timedelta = timedelta(seconds=5), max_attempts: int = 3) -> RetryPolicy: ...

    @classmethod
    def linear_backoff(cls, *, initial_delay: timedelta = timedelta(seconds=1), max_attempts: int = 5) -> RetryPolicy: ...

    @classmethod
    def no_retry(cls) -> RetryPolicy: ...
```

### Validation rules (fail-fast in `__init__`)

- `initial_delay` must be > 0
- `backoff_coefficient` must be >= 1.0
- `max_delay` must be >= `initial_delay`
- `max_attempts` must be >= 1
- `retry_on` entries must be subclasses of `Exception`

### Preset definitions

| Preset | initial_delay | coefficient | max_delay | max_attempts | jitter |
|--------|--------------|-------------|-----------|-------------|--------|
| `exponential_backoff()` | 1s | 2.0 | 60s | 3 | True |
| `fixed_delay(delay=5s)` | 5s | 1.0 | 5s | 3 | False |
| `linear_backoff(initial_delay=1s)` | 1s | 1.0 | 60s | 5 | False |
| `no_retry()` | 0s | 1.0 | 0s | 1 | False |

Note: `linear_backoff` uses additive delay (attempt * initial_delay), not the exponential formula. This is a special case handled in `compute_delay`.

## 2. Source Field (additions to existing models)

### TaskCreateRequest — add `source` slot

```python
class TaskCreateRequest:
    __slots__ = (..., "source")

    def __init__(self, ..., source: dict[str, Any] | None = None) -> None:
        self.source = source
```

### TaskInfo — add `source` slot

```python
class TaskInfo:
    __slots__ = (..., "source")

    def __init__(self, ..., source: dict[str, Any] | None = None) -> None:
        self.source = source

    def to_dict(self) -> dict[str, Any]:
        d = {...}
        if self.source is not None:
            d["source"] = self.source
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskInfo:
        ...
        source=data.get("source"),
```

### Immutability

- Source is set only at task creation time
- `TaskPatchRequest` does NOT include `source` — it cannot be changed after creation
- This is enforced by the SDK, not the server

## 3. Streaming (modifications to existing classes)

### TaskContext — add `stream()` method

```python
class TaskContext(Generic[Input]):
    __slots__ = (..., "_stream_queue")

    def __init__(self, ..., stream_queue: asyncio.Queue[Any] | None = None) -> None:
        ...
        self._stream_queue = stream_queue

    async def stream(self, item: Any) -> None:
        """Emit a streaming item to observers.

        Items are delivered in-memory via asyncio.Queue.
        NOT persisted to the task store.

        :param item: Any JSON-serializable value.
        :raises RuntimeError: If streaming is not enabled for this task.
        """
        if self._stream_queue is None:
            raise RuntimeError("Streaming is not enabled for this task run")
        await self._stream_queue.put(item)
```

### TaskRun — add `__aiter__`/`__anext__`

```python
_STREAM_SENTINEL = object()  # signals end of stream

class TaskRun(Generic[Output]):
    __slots__ = (..., "_stream_queue")

    def __init__(self, ..., stream_queue: asyncio.Queue[Any] | None = None) -> None:
        ...
        self._stream_queue = stream_queue

    def __aiter__(self) -> TaskRun[Output]:
        return self

    async def __anext__(self) -> Any:
        if self._stream_queue is None:
            raise StopAsyncIteration
        item = await self._stream_queue.get()
        if item is _STREAM_SENTINEL:
            raise StopAsyncIteration
        return item
```

### Stream lifecycle in `_manager.py`

1. **Create**: `queue = asyncio.Queue()` — created per task execution
2. **Pass to producer**: `TaskContext(..., stream_queue=queue)`
3. **Pass to consumer**: `TaskRun(..., stream_queue=queue)`
4. **End signal**: Manager puts `_STREAM_SENTINEL` on completion, failure, or suspend
5. **Error handling**: On task failure, sentinel is put AFTER the exception is set on the future
   - The consumer will get all streamed items, then `StopAsyncIteration`, then `result()` raises

## Wire Format: Source Field in JSON

### Create request body (POST /tasks)
```json
{
  "task_id": "task_abc",
  "title": "Process document",
  "input": {"url": "https://..."},
  "source": {
    "origin": "api",
    "request_id": "req_123",
    "user": "alice"
  }
}
```

### Task record in local JSON file
```json
{
  "task_id": "task_abc",
  "status": "completed",
  "source": {"origin": "api", "request_id": "req_123"},
  "result": {"summary": "done"},
  ...
}
```
