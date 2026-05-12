# Research: Streaming, Retry Policies, and Source Field

**Phase 0 artifact** — Analysis of existing code and prior art.

## Prior Art: Retry Policies

### Temporal (Python SDK)
```python
RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=100),
    maximum_attempts=0,  # unlimited
    non_retryable_error_types=["ValueError"],
)
```
- Delay formula: `min(initial_interval * backoff_coefficient ^ attempt, maximum_interval)`
- `maximum_attempts=0` means unlimited retries
- `non_retryable_error_types` is a list of exception class names (strings)

### Azure Durable Functions (Python SDK)
```python
RetryOptions(
    first_retry_interval_in_milliseconds=5000,
    max_number_of_attempts=3,
)
# Plus optional: backoff_coefficient, max_retry_interval, retry_timeout
```
- Similar formula to Temporal
- Uses milliseconds (we use `timedelta`)

### Celery
```python
@app.task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,      # enables exponential backoff
    retry_backoff_max=600,   # seconds
    retry_jitter=True,       # adds randomness
    max_retries=3,
)
```
- `autoretry_for` is an opt-in tuple of exception types (not strings)
- Jitter is boolean on/off (uses `random.randint(0, countdown)`)

### Our Design Decision

Aligned with Temporal/DTF naming with Celery-style `retry_on` semantics:

| Parameter | Type | Default | Rationale |
|-----------|------|---------|-----------|
| `initial_delay` | `timedelta` | 1s | Temporal's `initial_interval` — more descriptive name |
| `backoff_coefficient` | `float` | 2.0 | Same as Temporal/DTF |
| `max_delay` | `timedelta` | 60s | Temporal's `maximum_interval` — caps exponential growth |
| `max_attempts` | `int` | 3 | DTF's `max_number_of_attempts` |
| `retry_on` | `tuple[type[Exception], ...] | None` | None (all) | Celery's `autoretry_for` — but None means "all exceptions" |
| `jitter` | `bool` | True | Celery's `retry_jitter` — ±25% randomization |

## Existing Code Touchpoints

### Files to modify

| File | Change | Complexity |
|------|--------|-----------|
| `_retry.py` | NEW — RetryPolicy class | Medium |
| `_context.py` | Add `stream()` method, `_stream_queue` slot | Low |
| `_run.py` | Add `__aiter__`/`__anext__`, `_stream_queue` slot | Medium |
| `_models.py` | Add `source` field to `TaskInfo`, `TaskCreateRequest` | Low |
| `_decorator.py` | Add `retry` + `source` params to `DurableTaskOptions` | Low |
| `_manager.py` | Retry loop, stream queue lifecycle, source passthrough | High |
| `_client.py` | Send `source` in create body | Low |
| `_local_provider.py` | Persist `source` in JSON | Low |
| `durable/__init__.py` | Export `RetryPolicy` | Trivial |
| `core/__init__.py` | Re-export `RetryPolicy` | Trivial |

### Existing patterns to follow

- All models use `__slots__`, `__init__`, `__repr__`, `__eq__` — NO dataclasses
- `TaskStatus = Literal[...]` — Literal types, not enums
- Provider methods: `create`, `get`, `update`, `delete`, `list`
- `_manager.py` is the orchestration hub (~25KB, ~600 lines)
- `TaskContext` already has `_cancel_event: asyncio.Event` slot — streaming queue follows same pattern
- `TaskRun` already wraps an `asyncio.Future` — streaming iteration is a natural extension
