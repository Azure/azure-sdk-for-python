# Quickstart: Streaming, Retry Policies, and Source Field

**Phase 1 artifact** — Usage examples for the three new features.

## 1. Streaming Output

```python
from azure.ai.agentserver.core.durable import durable_task, TaskContext

@durable_task(title="Stream chunks")
async def stream_demo(ctx: TaskContext[str]) -> str:
    for i in range(5):
        await ctx.stream({"chunk": i, "text": f"Processing step {i}"})
    return "all done"

# Consumer side:
run = await stream_demo.start(task_id="s1", input="go")
async for chunk in run:
    print(chunk)  # {"chunk": 0, "text": "Processing step 0"}, ...
result = await run.result()  # "all done"
```

## 2. Retry Policies

### Using presets
```python
from datetime import timedelta
from azure.ai.agentserver.core.durable import durable_task, TaskContext, RetryPolicy

# Exponential backoff: 1s → 2s → 4s (default)
@durable_task(title="Resilient call", retry=RetryPolicy.exponential_backoff())
async def api_call(ctx: TaskContext[str]) -> dict:
    return await call_external_api(ctx.input)

# Fixed delay: wait 5s between retries
@durable_task(title="Polling", retry=RetryPolicy.fixed_delay(delay=timedelta(seconds=5)))
async def poll_status(ctx: TaskContext[str]) -> str:
    return await check_status(ctx.input)
```

### Custom policy
```python
@durable_task(
    title="Custom retry",
    retry=RetryPolicy(
        initial_delay=timedelta(seconds=2),
        backoff_coefficient=3.0,
        max_delay=timedelta(seconds=120),
        max_attempts=5,
        retry_on=(ConnectionError, TimeoutError),
        jitter=True,
    ),
)
async def flaky_task(ctx: TaskContext[dict]) -> str:
    return await do_something_flaky(ctx.input)
```

### Override at call site
```python
# Decorator sets default, but caller can override:
result = await flaky_task.run(
    task_id="t1",
    input={"url": "https://..."},
    retry=RetryPolicy.no_retry(),  # override: no retries this time
)
```

## 3. Source Field (Provenance)

### Set at decorator level
```python
@durable_task(
    title="Ingest document",
    source={"origin": "pipeline", "version": "2.0"},
)
async def ingest(ctx: TaskContext[str]) -> dict:
    return await process_document(ctx.input)
```

### Set at call site (overrides decorator)
```python
result = await ingest.run(
    task_id="t1",
    input="doc.pdf",
    source={"origin": "api", "request_id": "req_abc", "user": "alice"},
)
```

### Read source from TaskInfo
```python
run = await ingest.start(task_id="t1", input="doc.pdf")
info = await run.info()
print(info.source)  # {"origin": "api", "request_id": "req_abc", "user": "alice"}
```

## 4. Combining Features

```python
@durable_task(
    title="Full-featured task",
    retry=RetryPolicy.exponential_backoff(max_attempts=5),
    source={"origin": "scheduler", "cron": "0 * * * *"},
)
async def hourly_job(ctx: TaskContext[dict]) -> dict:
    await ctx.stream({"phase": "starting", "attempt": ctx.run_attempt})

    result = await do_work(ctx.input)

    await ctx.stream({"phase": "complete", "rows": result["count"]})
    return result

# Consumer:
run = await hourly_job.start(task_id="hourly-1", input={"table": "users"})
async for update in run:
    print(f"Update: {update}")
final = await run.result()
```

## 5. Error Handling with Retry

```python
@durable_task(
    title="With retry logging",
    retry=RetryPolicy(
        initial_delay=timedelta(seconds=1),
        max_attempts=3,
        retry_on=(ConnectionError,),
    ),
)
async def resilient(ctx: TaskContext[str]) -> str:
    if ctx.run_attempt > 0:
        await ctx.stream({"retry_attempt": ctx.run_attempt})
    return await fetch_data(ctx.input)
```

When `fetch_data` raises `ConnectionError`:
1. Attempt 0 fails → retry after ~1s
2. Attempt 1 fails → retry after ~2s
3. Attempt 2 fails → `TaskFailed` raised (max_attempts=3 exhausted)

If `ValueError` is raised, it fails immediately (not in `retry_on`).
