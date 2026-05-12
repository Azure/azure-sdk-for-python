# Durable Task Developer Guide

> Developer guidance for building crash-resilient agents with `@durable_task` — the single decorator for turning async functions into units of work that survive container crashes, OOM kills, and redeployments.

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Lifecycle Automation](#lifecycle-automation)
  - [State Diagram](#state-diagram)
  - [Entry Mode Decision Table](#entry-mode-decision-table)
  - [.run() vs .start() vs .get()](#run-vs-start-vs-get)
- [TaskContext](#taskcontext)
  - [Properties Reference](#properties-reference)
  - [Branching on Entry Mode](#branching-on-entry-mode)
- [Suspend & Resume](#suspend--resume)
  - [Multi-Turn Conversations](#multi-turn-conversations)
- [Streaming](#streaming)
- [Persistence](#persistence)
  - [Responsibility Matrix](#responsibility-matrix)
  - [The Durable Boundary Rule](#the-durable-boundary-rule)
- [The Invocation Store Pattern](#the-invocation-store-pattern)
- [RetryPolicy](#retrypolicy)
- [Decorator Options](#decorator-options)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Common Mistakes](#common-mistakes)

---

## Overview

Azure AI Hosted Agent containers can be killed at any time — OOM kills, node
preemptions, rolling deployments, or unexpected crashes. Without durability,
any in-flight work is lost and the agent starts from scratch.

`@durable_task` solves this. Decorate your async function, and the framework
guarantees it runs to completion — even if the container restarts mid-execution.
On recovery, your function is re-invoked with the same input and
last-saved metadata, so it can pick up where it left off.

**Your contract:**

- Write a normal `async` function that takes a `TaskContext`
- Use `ctx.metadata` to record lightweight progress (e.g. current phase, step count)
- Check `ctx.entry_mode` if you need to distinguish fresh runs from recoveries
- Return a result, or `await ctx.suspend()` for multi-turn patterns

**What you get:**

- Automatic crash recovery — your function re-runs without any caller intervention
- Input and metadata persistence across restarts
- Retry with configurable backoff on failures
- Cooperative cancellation and timeout
- Streaming incremental output to observers
- Suspend/resume for multi-turn conversational agents

### What durable tasks are NOT

- **Not a checkpoint/replay engine.** This is not Temporal or Durable Functions.
  Your function is re-executed from the top on recovery, not replayed from a
  deterministic log. If your function calls an LLM twice, it will call it again
  on recovery.
- **Not a result store.** Task output and metadata exist only while the task is
  alive. Once the task is deleted, they are gone. If you need results to outlive
  the task, persist them in your own store (database, blob storage, etc.).
- **Not a stream log.** Streamed chunks are relayed to live observers in real
  time but are not recorded. If a consumer connects after streaming ends,
  the chunks are gone.
- **Not application-level persistence.** The framework manages *task lifecycle*
  state (status, input, metadata, lease). Your application data — conversation
  history, invocation results, user-facing state — is your responsibility.
  See [Persistence](#persistence).
- **Not unbounded storage.** `ctx.metadata` is for small progress signals
  (current phase, retry count, step index), not for accumulating large data.
  The task payload has a 1 MB cap. Write large or growing data to your own store.

---

## Getting Started

A minimal durable task in 15 lines:

```python
from azure.ai.agentserver.core.durable import durable_task, TaskContext

@durable_task
async def greet(ctx: TaskContext[str]) -> str:
    """A simple durable task that greets the user."""
    name = ctx.input
    return f"Hello, {name}!"

# Run it — lifecycle-aware: creates if new, recovers if stale
result = await greet.run(task_id="greet-alice", input="Alice")
print(result.output)  # "Hello, Alice!"
```

That's it. The decorator transforms your function into a `DurableTask` with `.run()`,
`.start()`, and `.get()` methods. The function itself takes a single `TaskContext`
parameter.

If the process crashes mid-execution and you call `.run()` again with the same
`task_id`, the framework detects the stale task, recovers it, and re-enters your
function with `ctx.entry_mode = "recovered"`.

---

## Lifecycle Automation

Every call to `.run()` or `.start()` follows the same state machine. You never
manually check task state or call resume — the framework does it for you.

### State Diagram

```
                        .run() / .start()
                              │
                              ▼
                    ┌───── task exists? ─────┐
                    │                        │
                   No                       Yes
                    │                        │
                    ▼                        ▼
              ┌──────────┐         ┌──── status? ────┐
              │  Create  │         │                  │
              │  & Start │         │                  │
              └──────────┘    ┌────┴────┐    ┌───────┴────────┐
                    │         │         │    │                │
                    ▼      pending  suspended  in_progress  completed
                 fresh        │         │       │              │
                              ▼         ▼       ▼              ▼
                           fresh    resumed   stale?    TaskConflictError
                                                │
                                           ┌────┴────┐
                                          Yes        No
                                           │          │
                                           ▼          ▼
                                       recovered  TaskConflictError
```

### Entry Mode Decision Table

| Current State | Action | `ctx.entry_mode` |
|---|---|---|
| No task exists | Create and start | `"fresh"` |
| `pending` | Start | `"fresh"` |
| `suspended` | Resume with new input | `"resumed"` |
| `in_progress` (stale) | Recover | `"recovered"` |
| `in_progress` (not stale) | **Raises `TaskConflictError`** | — |
| `completed` (ephemeral) | Task was auto-deleted → create fresh | `"fresh"` |
| `completed` (non-ephemeral) | **Raises `TaskConflictError`** | — |

A task is considered **stale** when its last update is older than `stale_timeout`
(default: 300 seconds). This means the previous execution likely crashed.

### .run() vs .start() vs .get()

| Method | Blocks? | Returns | Use When |
|--------|---------|---------|----------|
| `.run()` | Yes — awaits completion | `TaskResult[Output]` | You want the result inline |
| `.start()` | No — returns immediately | `TaskRun[Output]` | You want a handle for polling/streaming |
| `.get()` | No — reads from store | `TaskInfo \| None` | You want to query task state without executing |

`.run()` and `.start()` follow the same lifecycle rules. The only difference is
whether you wait for the result or get a handle back.

```python
# .start() returns immediately with a handle
task_run = await greet.start(task_id="greet-bob", input="Bob")

# Use the handle to await the result later
result = await task_run.result()

# Or stream incremental output (if the task uses ctx.stream())
async for chunk in task_run:
    print(chunk)
```

`.get()` does not execute the task. It reads whatever is persisted:

```python
info = await greet.get("greet-bob")
if info is not None:
    print(info.status)   # "completed", "suspended", "in_progress", etc.
    print(info.payload)  # Contains input, metadata, output buckets
```

---

## TaskContext

Every durable task function receives exactly one parameter: a `TaskContext[Input]`
where `Input` is your typed input type.

### Properties Reference

| Property | Type | Description |
|----------|------|-------------|
| `ctx.input` | `Input` | The typed input value passed to `.run()` / `.start()` |
| `ctx.entry_mode` | `EntryMode` | Why the function was entered: `"fresh"`, `"resumed"`, or `"recovered"` |
| `ctx.task_id` | `str` | The task's unique identifier |
| `ctx.session_id` | `str` | Session scope identifier |
| `ctx.metadata` | `TaskMetadata` | Mutable progress metadata (persisted automatically) |
| `ctx.cancel` | `asyncio.Event` | Set when cancellation is requested |
| `ctx.shutdown` | `asyncio.Event` | Set when the container is shutting down |
| `ctx.run_attempt` | `int` | Framework retry attempt counter (0-indexed) |
| `ctx.title` | `str` | Human-readable task title |
| `ctx.tags` | `dict[str, str]` | Merged decorator + call-site tags |

### Branching on Entry Mode

Use `ctx.entry_mode` to handle different execution scenarios:

```python
from azure.ai.agentserver.core.durable import durable_task, TaskContext, EntryMode

@durable_task(name="process_order")
async def process_order(ctx: TaskContext[dict]) -> dict:
    order = ctx.input

    if ctx.entry_mode == "fresh":
        # First time — validate and begin processing
        ctx.metadata["step"] = "validating"

    elif ctx.entry_mode == "recovered":
        # Crashed mid-execution — check what was already done
        step = ctx.metadata.get("step", "validating")
        if step == "charged":
            # Payment already taken — skip to fulfillment
            return await fulfill(order)

    elif ctx.entry_mode == "resumed":
        # Resumed after suspension — ctx.input has new data
        pass

    # ... do work ...
    ctx.metadata["step"] = "charged"
    return {"status": "completed", "order_id": order["id"]}
```

**`TaskMetadata`** is automatically persisted to the task store. Use it to track
progress so that recovered tasks can skip completed steps:

```python
# Dict-style access (recommended)
ctx.metadata["progress"] = 50               # set a value
ctx.metadata["phase"] = "summarizing"        # set another
progress = ctx.metadata["progress"]          # read (raises KeyError if missing)
if "phase" in ctx.metadata:                  # containment check
    print(f"Phase: {ctx.metadata['phase']}")
for key in ctx.metadata:                     # iterate keys
    print(f"{key}: {ctx.metadata[key]}")

# Convenience methods for special operations
ctx.metadata.increment("items_processed")    # atomic increment
ctx.metadata.append("logs", "step 3 done")  # append to list
progress = ctx.metadata.get("progress")      # read with default (no KeyError)
snapshot = ctx.metadata.to_dict()            # full snapshot copy
```

All mutations (including `[]` assignment and `del`) are automatically tracked
and flushed to the task store on a 5-second debounce interval.

---

## Suspend & Resume

Use `ctx.suspend()` to pause execution and release the task lease. The task
transitions to `suspended` status. A subsequent `.run()` or `.start()` call
resumes it with `entry_mode="resumed"` and new input.

> **Critical**: Always use `return await ctx.suspend(...)`. Forgetting `return`
> or `await` silently breaks the suspension mechanism.

```python
@durable_task(name="approval_flow")
async def approval_flow(ctx: TaskContext[dict]) -> dict:
    request = ctx.input

    if ctx.entry_mode == "fresh":
        # Submit for approval, then suspend
        return await ctx.suspend(output={"status": "awaiting_approval", "request": request})

    elif ctx.entry_mode == "resumed":
        # Manager responded — ctx.input has the approval decision
        decision = ctx.input
        if decision.get("approved"):
            return {"status": "approved", "approved_by": decision["manager"]}
        return {"status": "rejected", "reason": decision.get("reason")}
```

The `output` parameter on `ctx.suspend()` is optional. It provides a snapshot
that observers can read while the task is suspended (via `.get()` or the
`TaskResult`'s `.output` attribute).

### Multi-Turn Conversations

The suspend/resume pattern is ideal for multi-turn agents where each turn is
one user ↔ agent interaction:

```python
@durable_task(name="chat_session")
async def chat_session(ctx: TaskContext[dict]) -> dict:
    message = ctx.input["message"]

    if ctx.entry_mode == "fresh":
        history = []
    elif ctx.entry_mode == "resumed":
        history = ctx.metadata.get("history", [])

    # Generate response (your LLM call, graph execution, etc.)
    reply = await generate_reply(message, history)

    # Track conversation history in metadata
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    ctx.metadata["history"] = history

    # Suspend — waiting for the next user message
    return await ctx.suspend(output={"reply": reply})
```

Each call to `.start(task_id=session_id, input={"message": "..."})` resumes the
same task with the new message. The framework handles the resume automatically.

---

## Streaming

Use `ctx.stream()` to emit incremental output and `async for` on the `TaskRun`
handle to consume it:

```python
@durable_task(name="generate_report")
async def generate_report(ctx: TaskContext[str]) -> str:
    topic = ctx.input
    chunks = []
    async for token in call_llm_streaming(topic):
        await ctx.stream(token)  # Emit to observers
        chunks.append(token)
    return "".join(chunks)

# Consumer side
task_run = await generate_report.start(task_id="report-1", input="Q3 Results")
async for chunk in task_run:
    print(chunk, end="")

# After streaming completes, get the full result
final = await task_run.result()
```

> **Important**: Streaming items are held in an in-memory `asyncio.Queue`. They are
> **not persisted** and are **lost on crash**. If the process restarts mid-stream,
> the recovered task starts from scratch. For durable incremental output, write
> to your own store inside the task function.

---

## Persistence

Understanding what is and isn't persisted is the most important concept in this
guide.

### Responsibility Matrix

| Data | Who Persists | Where |
|------|-------------|-------|
| Task status — `TaskStatus`: `"pending"`, `"in_progress"`, `"suspended"`, `"completed"` | **Framework** | Task store |
| Task input (the value passed to `.run()`/`.start()`) | **Framework** | Task store payload |
| Task metadata (`ctx.metadata`) | **Framework** | Task store payload |
| Task output (return value) | **Framework** | Task store payload |
| Task error (on failure) | **Framework** | Task store |
| Invocation results (what your API returns to callers) | **You** | Your store |
| Conversation history / checkpoints | **You** | Your store |
| Streaming items | **Nobody** | In-memory only |

The task store powers lifecycle and recovery. **It is NOT your application
database.** You read from it via `.get()` to inspect task state, but you should
not depend on it as the persistence layer for your API responses.

### The Durable Boundary Rule

> **Everything that must survive a crash must happen inside the durable task function.**

The durable task function is the crash-recovery boundary. If the process dies,
the framework re-enters your function on the next `.run()` / `.start()` call.
Any work done *outside* the function (e.g., in an HTTP handler, in an
`asyncio.create_task` callback) is lost.

---

## The Invocation Store Pattern

When building an HTTP API that fronts durable tasks (the 202 + poll pattern),
you need to persist invocation results so that clients can retrieve them. The
correct pattern: write results **inside** the durable task function.

```python
# Your persistence layer (file store, Redis, database — your choice)
invocation_store = FileStore("./invocations")

@durable_task(name="agent_session")
async def agent_session(ctx: TaskContext[dict]) -> dict:
    invocation_id = ctx.input["invocation_id"]
    message = ctx.input["message"]

    # Mark invocation as running (inside the durable boundary)
    invocation_store.save(invocation_id, {"status": "running"})

    # Do work
    reply = await generate_reply(message)
    result = {"status": "completed", "reply": reply}

    # Persist result (inside the durable boundary)
    invocation_store.save(invocation_id, result)

    # Suspend — waiting for next turn
    return await ctx.suspend(output=result)
```

The HTTP layer is minimal:

```python
# POST /invoke — start or resume the task
async def invoke(request):
    invocation_id = generate_id()
    try:
        await agent_session.start(
            task_id=session_id,
            input={"invocation_id": invocation_id, "message": message},
        )
    except TaskConflictError:
        return JSONResponse({"error": "Task already running"}, status_code=409)
    return JSONResponse({"invocation_id": invocation_id}, status_code=202)

# GET /invocations/{id} — read from YOUR store, not the task store
async def get_invocation(request):
    result = invocation_store.load(invocation_id)
    if result is None:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return JSONResponse(result)
```

Why this works: if the process crashes after `invocation_store.save(..., "running")`
but before the result write, the framework recovers the task, re-enters the function
with `entry_mode="recovered"`, and the result eventually gets written. The client
polls `GET /invocations/{id}` until it sees `"completed"`.

---

## RetryPolicy

Configure automatic retries on failure. Three presets cover most use cases:

```python
from datetime import timedelta
from azure.ai.agentserver.core.durable import durable_task, RetryPolicy, TaskContext

# Exponential backoff (default: 1s → 2s → 4s, 3 attempts)
@durable_task(name="call_api", retry=RetryPolicy.exponential_backoff())
async def call_api(ctx: TaskContext[str]) -> dict: ...

# Fixed delay (5s between each retry, 3 attempts)
@durable_task(name="poll_status", retry=RetryPolicy.fixed_delay(delay=timedelta(seconds=5)))
async def poll_status(ctx: TaskContext[str]) -> dict: ...

# Linear backoff (1s → 2s → 3s → 4s → 5s, 5 attempts)
@durable_task(name="batch_job", retry=RetryPolicy.linear_backoff(max_attempts=5))
async def batch_job(ctx: TaskContext[str]) -> dict: ...

# No retry — fail immediately
@durable_task(name="one_shot", retry=RetryPolicy.no_retry())
async def one_shot(ctx: TaskContext[str]) -> dict: ...
```

Customize any preset:

```python
RetryPolicy.exponential_backoff(
    max_attempts=5,
    initial_delay=timedelta(seconds=2),
    max_delay=timedelta(seconds=120),
    jitter=True,  # ±25% randomization (default)
)
```

Retry can also be set per-call, overriding the decorator:

```python
result = await call_api.run(
    task_id="api-1",
    input="https://example.com",
    retry=RetryPolicy.fixed_delay(max_attempts=10),
)
```

---

## Decorator Options

The `@durable_task` decorator accepts these options (defined in `DurableTaskOptions`):

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | `str` | Function name | Task type name. Used for routing and identification. |
| `retry` | `RetryPolicy \| None` | `None` | Retry policy on failure. See [RetryPolicy](#retrypolicy). |
| `ephemeral` | `bool` | `True` | Auto-delete task record on completion. |
| `source` | `dict[str, Any] \| None` | `None` | Immutable provenance metadata (e.g., model version). |
| `tags` | `dict[str, str] \| Callable[[Any, str], dict[str, str]] \| None` | `{}` | Default tags (static or callable factory receiving `(input, task_id)`). |
| `title` | `str \| Callable[[Any, str], str] \| None` | `None` | Human-readable title or title factory. |
| `description` | `str \| Callable[[Any, str], str \| None] \| None` | `None` | Task description (static or callable factory receiving `(input, task_id)`). |
| `store_input` | `bool` | `True` | Whether to persist input on the task record. |
| `timeout` | `timedelta \| None` | `None` | Execution timeout. When elapsed, `ctx.cancel` is set (cooperative), then hard cancellation after `cancel_grace_seconds`. |
| `cancel_grace_seconds` | `float` | `5.0` | Seconds between cooperative cancel and hard cancellation on timeout. |

```python
@durable_task(
    name="analyze_document",
    ephemeral=False,        # Keep task record after completion
    source={"model": "gpt-4o", "version": "2024-08"},
    tags={"team": "platform"},
    title="Document Analysis",
)
async def analyze_document(ctx: TaskContext[dict]) -> dict: ...
```

**`ephemeral`** controls what happens when a completed task's `.start()` / `.run()`
is called again:
- `ephemeral=True` (default): The completed task was auto-deleted, so a fresh task
  is created.
- `ephemeral=False`: The completed task still exists, so `TaskConflictError` is raised.

Use the `.options()` method for per-call overrides without modifying the decorator:

```python
# Override source for this specific call
result = await analyze_document.options(
    source={"model": "gpt-4o-mini"},
).run(task_id="doc-1", input={"url": "..."})
```

### Callable Factories (`tags`, `title`, `description`)

When `tags`, `title`, or `description` is a callable, it receives `(input, task_id)` and
is invoked at **task creation time** — before the task function runs.

```python
@durable_task(
    tags=lambda input, task_id: {"user": input["user_id"], "run": task_id[:8]},
    description=lambda input, task_id: f"Processing {input['filename']}",
)
async def process_file(ctx: TaskContext[dict]) -> str: ...
```

**Error behaviour:**

- If a factory **raises an exception**, it propagates directly to the `.run()` / `.start()`
  caller. The task is never created.
- If a factory **returns the wrong type** (e.g., `tags` callable returns a list instead of
  a dict), a `TypeError` is raised immediately at task creation time.
- Mixing a callable `tags` on the decorator with a static dict via `.options(tags={...})`
  raises `TypeError` — use one style consistently.

---

## Error Handling

| Exception | Raised By | When |
|-----------|-----------|------|
| `TaskConflictError` | `.run()`, `.start()` | Task is `in_progress` (non-stale) or `completed` (non-ephemeral) |
| `TaskFailed` | `.run()`, `task_run.result()` | Unhandled exception in the task function |
| `TaskCancelled` | `.run()`, `task_run.result()` | Task was cancelled via `task_run.cancel()` |
| `TaskTerminated` | `.run()`, `task_run.result()` | Task was forcefully terminated (timeout or `task_run.terminate()`) |
| `TaskNotFound` | `task_run.refresh()`, `task_run.delete()` | Task record does not exist in the store |

> **Note**: Suspension is no longer an exception. When a task suspends, `.run()` and
> `task_run.result()` return a `TaskResult` with `is_suspended == True`. Check
> `result.is_suspended` or `result.is_completed` to distinguish outcomes.

Handle them in your application code:

```python
from azure.ai.agentserver.core.durable import (
    TaskConflictError,
    TaskFailed,
    TaskTerminated,
)

result = await my_task.run(task_id="t1", input="hello")

if result.is_suspended:
    # Task paused — result.output has the snapshot
    print(f"Suspended: {result.output}")
elif result.is_completed:
    print(f"Done: {result.output}")
```

Exceptions are raised for true error conditions:

```python
try:
    result = await my_task.run(task_id="t1", input="hello")
except TaskConflictError:
    # Task already running or completed
    info = await my_task.get("t1")
    print(f"Task is {info.status}")
except TaskFailed as exc:
    # Task function raised an exception
    print(f"Failed: {exc.error}")
except TaskTerminated:
    # Task was forcefully terminated (timeout or explicit terminate)
    print("Task was terminated")
```

`TaskSuspended` is retained for backward compatibility but is no longer raised
by `.run()` or `task_run.result()`. Suspension is now a return value — check
`result.is_suspended` on the returned `TaskResult`.

---

## Cancellation, Timeout, and Termination

Durable tasks support three levels of stopping execution:

### Cooperative Cancellation

Set `ctx.cancel` to signal the task function to exit gracefully. The task
must check this event and respond:

```python
run = await my_task.start(task_id="t1", input=data)
await run.cancel()  # Sets ctx.cancel — task should check and exit
```

Inside the task function:

```python
@durable_task
async def my_task(ctx: TaskContext[Input]) -> Output:
    for item in items:
        if ctx.cancel.is_set():
            return partial_result  # Exit cleanly
        await process(item)
    return full_result
```

Cooperative cancel raises `TaskCancelled` on `result()`.

### Execution Timeout

Set a `timeout` to automatically cancel tasks that run too long. The timeout
uses a two-phase watchdog:

1. **Cooperative phase**: After `timeout` elapses, `ctx.cancel` is set.
2. **Hard phase**: After `cancel_grace_seconds` more, the asyncio task is
   force-cancelled and `TaskTerminated` is raised.

```python
from datetime import timedelta

@durable_task(
    timeout=timedelta(minutes=5),
    cancel_grace_seconds=10.0,  # 10s grace before hard cancel
)
async def analyze(ctx: TaskContext[dict]) -> dict:
    while not ctx.cancel.is_set():
        chunk = await process_next()
        if chunk is None:
            break
    return {"status": "done"}
```

### Forced Termination

`terminate()` immediately kills the task via the failure path. Unlike
cooperative cancel, terminated tasks are stored as failed and are **not**
eligible for recovery:

```python
run = await my_task.start(task_id="t1", input=data)
await run.terminate(reason="User requested abort")

try:
    await run.result()
except TaskTerminated:
    print("Task was terminated")
```

### Cancel vs Terminate Summary

| Method | `ctx.cancel` set? | Hard cancel? | Exception | Recoverable? |
|--------|-------------------|--------------|-----------|--------------|
| `run.cancel()` | ✅ | ❌ | `TaskCancelled` | Yes (stays in_progress) |
| `run.terminate()` | ✅ | ✅ | `TaskTerminated` | No (goes to failed) |
| Timeout expired | ✅ then ✅ | After grace | `TaskTerminated` | No (goes to failed) |

---

## Best Practices

1. **Keep tasks idempotent for recovery.** When `entry_mode="recovered"`, the
   function re-runs from the top. Use `ctx.metadata` to track completed steps
   and skip them on re-entry.

2. **Branch on `entry_mode`.** Always handle at least `"fresh"` and `"recovered"`.
   For suspend/resume tasks, handle `"resumed"` as well.

3. **Persist results inside the durable boundary.** Any write that must survive
   a crash belongs inside the task function, not in the HTTP handler or a
   background `asyncio.create_task`.

4. **Use `ephemeral=True` for one-shot tasks.** If the task doesn't need to be
   queried after completion, let the framework auto-delete it. This keeps the
   task store clean.

5. **Keep task functions focused.** A task should do one logical unit of work.
   Compose multiple tasks rather than building monolithic functions.

6. **Check cancellation cooperatively.** Poll `ctx.cancel.is_set()` in long loops
   and exit cleanly when set.

7. **Use `ctx.metadata` for progress, not for large data.** Metadata is flushed
   periodically to the task store. Keep values small and JSON-serializable.

---

## Common Mistakes

### ❌ Missing `return await` on suspend

```python
# ❌ BAD — suspend() returns a sentinel, but it's discarded
async def my_task(ctx: TaskContext[str]) -> str:
    await ctx.suspend(output="paused")
    return "done"  # This runs immediately — task never actually suspends

# ✅ GOOD — return the sentinel so the framework sees it
async def my_task(ctx: TaskContext[str]) -> str:
    return await ctx.suspend(output="paused")
```

### ❌ Persisting results outside the durable boundary

```python
# ❌ BAD — if the process crashes, the result is never written
async def invoke(request):
    task_run = await my_task.start(task_id="t1", input="hello")
    asyncio.create_task(save_result_when_done(task_run))  # LOST ON CRASH
    return JSONResponse({"id": "inv-1"}, status_code=202)

# ✅ GOOD — write results inside the task function itself
@durable_task(name="my_task")
async def my_task(ctx: TaskContext[dict]) -> dict:
    invocation_id = ctx.input["invocation_id"]
    result = await do_work()
    invocation_store.save(invocation_id, result)  # DURABLE
    return result
```

### ❌ Leaking task_id to API callers

```python
# ❌ BAD — task_id is an internal lifecycle identifier
return JSONResponse({"task_id": task_id}, status_code=202)

# ✅ GOOD — expose your own identifier (invocation_id, session_id, etc.)
return JSONResponse({"invocation_id": invocation_id}, status_code=202)
```

### ❌ Assuming streaming survives crashes

```python
# ❌ BAD — streaming items are in-memory only
@durable_task(name="stream_report")
async def stream_report(ctx: TaskContext[str]) -> str:
    for chunk in generate_chunks():
        await ctx.stream(chunk)  # Lost if process crashes here
    return "done"

# ✅ GOOD — also persist to your store if durability matters
@durable_task(name="stream_report")
async def stream_report(ctx: TaskContext[str]) -> str:
    for chunk in generate_chunks():
        await ctx.stream(chunk)
        append_to_store(ctx.task_id, chunk)  # Durable fallback
    return "done"
```
