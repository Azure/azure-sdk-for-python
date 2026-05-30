# Durable Tasks Developer Guide

> The consolidated end-user-developer guide for the `@task` primitive
> shipped by `azure-ai-agentserver-core`. This replaces the previous
> `durable-task-overview.md` and `durable-task-developer-guide.md` —
> both are now thin pointers to this document.
>
> Audience: developers building agents that run on the agentserver
> hosting platform (or any host that backs the durable-task primitive)
> and want their work to survive container crashes, OOM kills, and
> redeployments without hand-rolling lifecycle plumbing.

---

## 1. Why

Agent workloads run for minutes to hours — multi-step reasoning, tool
loops, batch processing, multi-turn conversations with human-in-the-loop
pauses. The sandbox hosting that work can crash, be OOM-killed,
redeployed, or idle-deactivated at any time — and most failure modes
are unannounced.

```
┌─────────────────────────────────────────────────────────┐
│  Agent starts a 45-minute research task...              │
│                                                         │
│  ██████████████░░░░░░░░░░░░░░░░  35% complete           │
│                     ▲                                   │
│                     │  💥 Crash / OOM / redeploy        │
│                                                         │
│  Without @task: progress lost. User must restart.       │
│  With    @task: handler is re-invoked, metadata intact. │
└─────────────────────────────────────────────────────────┘
```

Most agent frameworks already provide durability for state *between*
turns (LangGraph checkpointers, Semantic Kernel, Temporal, etc.). What
**none** of them solve is the **entrypoint**:

- Who calls the framework when the sandbox starts back up after a crash?
- Who knows there *was* a crash?
- Who tells the platform a unit of work is still in flight so the
  sandbox doesn't get killed?

That is the gap `@task` closes. It wraps a durable boundary around
your agent function — a unit of work the platform can see, restart,
and resume — so whatever framework is underneath has somewhere
to plug in.

### Two camps, one decorator

| Camp | Examples | What `@task` adds |
|------|----------|-------------------|
| **Externally stateful** — framework owns durability | Temporal, Durable Functions, Orleans | Platform visibility: lifecycle tracking, liveness signal, status reporting on top of the framework's own durability |
| **Locally stateful** — container holds state | LangGraph (SQLite checkpointer), Claude SDK tool loops, hand-written agents | A crash-safe entry point: framework-managed liveness, plus run / resume / progress / suspend primitives the developer would otherwise hand-roll |

`@task` is **not** a replacement for Temporal or Durable Functions —
it is the thin durable wrapper around the platform↔code boundary. It
does not make your function deterministic or replayable. It turns
`run(input) → output` into a unit of work that survives a container
crash, a deployment, or an idle-deactivation — with hooks for
progress, suspension, cancellation, and steering that compose with
whatever framework you use underneath.

---

## 2. Mental Model

The primitive enforces exactly one invariant: **for a given `task_id`,
at most one handler runs at a time.** Everything else falls out of that.

### Four states

```
         ┌──── pending ────┐
   .start/.run             │
        └──────────────────┤
                           ▼
                     in_progress  ◄── re-acquired ──┐
                       │   │                         │
                       │   │  process crashes        │ (a new lifetime
                       │   │  (handler torn down     │  picks the task
                       │   ▼   mid-execution)        │  back up)
                       │   └─────────────────────────┘
                       │
                       │   handler returns or
                       │   raises an exception
                       ▼
                  ┌────┴────┐
                  │         │
              completed   suspended
                            │
                            └── .start/.run → re-entered → in_progress
```

| State | Meaning |
|-------|---------|
| `pending` | Created, not yet picked up by a handler. |
| `in_progress` | A handler is currently executing this task. |
| `suspended` | Handler called `ctx.suspend(...)` and returned. Awaiting `.run()` / `.start()` with new input. |
| `completed` | Terminal. The handler is finished and will not run again. The *outcome* (success, failure, cancellation, termination) is communicated to the caller through `.run()` / `.result()` — either as the return value, or as one of `TaskFailed` / `TaskCancelled` / `TaskTerminated` (see §4). Outcome is not encoded in the status field. |

The framework computes the **entry mode** every time it invokes your
handler, by looking at the task's current state in the store:

| Current state | Entry mode | What it means for your code |
|---------------|------------|------------------------------|
| No task / `pending` | `"fresh"` | First invocation. No prior state. |
| `suspended` | `"resumed"` | Caller provided new input; resume from there. |
| `in_progress` (previous lifetime torn down) | `"recovered"` | Previous lifetime crashed; you are the new lifetime. |
| `in_progress` (steerable, mid-flight) | `"resumed"` (with `ctx.was_steered=True`) | Another input arrived; drain it. |

You read `ctx.entry_mode` (an `EntryMode` literal) once at the top of
your handler and branch on it.

### What you persist, what the framework persists

- **Framework persists**: task metadata you write to `ctx.metadata`,
  the current input, lifecycle counters (`ctx.retry_attempt`,
  `ctx.recovery_count`, `ctx.steering_generation`), suspended-state
  snapshots, and a small amount of book-keeping the primitive uses to
  decide entry mode.
- **You persist**: anything else you need to recover from across
  crashes — through whatever your underlying framework already
  provides (LangGraph SqliteSaver, your own DB, etc.). The primitive
  does not impose a checkpoint schema. `ctx.metadata` is a
  small-watermark store, not a bulk-data store.

---

## 3. Hello World

A complete durable task in fewer than 15 lines:

```python
from azure.ai.agentserver.core.durable import task, TaskContext

@task(name="greet")
async def greet(ctx: TaskContext[str]) -> str:
    return f"Hello, {ctx.input}!"

# Run it — lifecycle-aware: creates if new, recovers if a prior
# lifetime crashed, raises TaskConflictError if another non-steerable
# lifetime is already active (or the task has already completed).
result = await greet.run(task_id="greet-alice", input="Alice")
print(result.output)  # "Hello, Alice!"
```

The decorator transforms your function into a `Task` (importable as
`Task`) with `.run()`, `.start()`, and a small handle returned by
`.start()` (`TaskRun`). Your function takes exactly one parameter — a
`TaskContext`.

If the container crashes mid-execution, the framework automatically
re-invokes your function on restart **before any HTTP handlers go
live** — your function is re-invoked with `ctx.entry_mode ==
"recovered"` and the same input. No caller action is needed.

If a caller calls `.run()` with a `task_id` whose previous run has
already completed, or with a `task_id` that is currently in progress
on another lifetime (and the task is not steerable), the framework
raises `TaskConflictError` — it does not create a duplicate or
overwrite the prior result.

---

## 4. Concepts

This section names the things you will encounter at runtime and links
each to the API symbol that exposes it. The exhaustive method-by-method
table lives in **§5 Reference** below.

### Entry mode (`EntryMode`)

`ctx.entry_mode` is the load-bearing signal. Branch on it at the top of
your handler:

```python
if ctx.entry_mode == "fresh":
    ...
elif ctx.entry_mode == "recovered":
    # We came back after a crash — check your watermark.
    ...
elif ctx.entry_mode == "resumed":
    # ctx.input is the new input that triggered the resume.
    ...
```

### Retry semantics (`ctx.retry_attempt`, `RetryPolicy`)

`ctx.retry_attempt` is the **cross-lifetime** failure-retry counter.

- Increments **only** when the handler raises a retryable failure.
- **Crash recovery does NOT consume the budget.** A lifetime that dies
  before the handler raises does not advance `retry_attempt`.
- Resets to 0 on successful completion and on steering drain.
- Persisted in the task's payload, re-hydrated on every entry, so a
  handler in lifetime *N* sees the same counter the previous lifetime
  saw.

The budget itself lives on `RetryPolicy.max_attempts`. When
`retry_attempt >= max_attempts`, the framework gives up — it stops
re-invoking your handler and the awaiting `.run()` / `.result()`
call raises `TaskFailed` with the last captured error.

```python
from azure.ai.agentserver.core.durable import task, RetryPolicy, TaskContext

@task(name="flaky", retry_policy=RetryPolicy(max_attempts=5))
async def flaky(ctx: TaskContext[str]) -> str:
    ...
```

### Metadata as a callable namespace facade

`ctx.metadata` (`TaskMetadata`) is the small persistent-state surface
your handler owns. It is a **callable namespace facade**:

- `ctx.metadata["key"] = value` — read/write the **default** namespace.
- `ctx.metadata("session")["upstream_id"] = sid` — read/write a
  **named** sibling namespace.

Each namespace is independent: a write to one does not dirty the
other; `flush()` on one persists only that namespace. The framework
also snapshots all touched namespaces at lifecycle boundaries (task
start, `ctx.suspend(...)` return, handler return or unhandled raise),
so writes you forget to explicitly flush are still durable across a
graceful boundary — but explicit `flush()` is the fence you use to
make at-most-once side-effect patterns work across a crash.

Names and keys starting with `_` are **reserved** for framework-internal
namespaces (the responses framework uses `_responses`, for example).
At the primitive layer this is a convention, not an enforced rule —
framework layers built on top of the primitive enforce it on the
handler-facing wrapper they expose.

### Suspend, resume, steering (`Suspended`)

`await ctx.suspend(output=...)` parks the task in `suspended` state
and exits the handler. A subsequent `.run()` / `.start()` resumes it
with `entry_mode="resumed"` and the new input. The `Suspended` type
models the suspended-state envelope the framework records.

For steerable conversations (multiple turns racing against each
other), the framework drains queued inputs into your handler with
`ctx.was_steered=True` and `ctx.pending_inputs` populated.

### Streaming (`StreamHandler`, `StreamHandlerFactory`, `QueueStreamHandler`)

Yield incremental output with `await ctx.stream(chunk)`. Consumers iterate
the task handle:

```python
run = await my_task.start(task_id=..., input=...)
async for chunk in run:
    print(chunk, end="")
```

`StreamHandler` is the interface the consumer side reads through;
`StreamHandlerFactory` is the per-task constructor injection point
(for example: tee every chunk to a file in addition to the in-memory
queue); `QueueStreamHandler` is the in-memory default.

### Results and runs (`TaskResult`, `TaskRun`, `TaskStatus`)

- `Task.run()` returns a `TaskResult[Output]` once the task reaches a
  terminal state — `result.status` is the `TaskStatus` literal,
  `result.output` is your handler's return value (or the last
  `ctx.suspend(output=...)` envelope).
- `Task.start()` returns a `TaskRun[Output]` handle you can poll,
  stream, or `await run.result()`-on.

### Input-acceptance preconditions (`LastInputIdPreconditionFailed`, `TaskPreconditionFailed`)

For sequential-input semantics (don't accept input *N* unless the
last-accepted input was *N-1*), `.start(... if_last_input_id=...)`
applies an HTTP-`If-Match`-style precondition. Mismatch raises
`LastInputIdPreconditionFailed` (a subclass of `TaskPreconditionFailed`).

### Steering-queue backpressure (`SteeringQueueFull`)

Steerable tasks have a bounded steering input queue; once full,
new `.start()` calls raise `SteeringQueueFull`.

### Unsuccessful outcomes (`TaskFailed`, `TaskCancelled`, `TaskTerminated`)

When a task ends without producing a normal return value, the
*stored* task status is still `completed` — the task is finished
either way — but `.run()` / `.result()` raises one of three typed
exceptions so the caller can branch on **why** it ended:

- `TaskFailed` — the handler raised an unhandled exception. Carries
  a structured `error` dict (`type`, `message`, optional `cause`).
- `TaskCancelled` — the task was cancelled via `handle.cancel()`.
- `TaskTerminated` — the task was forcefully terminated by the
  operator or platform via `handle.terminate()` (carries a `reason`).

In addition, `TaskNotFound` is raised by `handle.result()` (and by
`.start()` when resuming) if the referenced `task_id` has been
deleted out from under the caller, and `TaskConflictError` is raised
when `.run()` / `.start()` collides with an already-active
non-steerable task or with an already-completed task.

You do **not** need to catch any of these inside your handler —
they exist for the *caller's* error-handling code. Your handler
just `return`s, raises, or `await`s `ctx.suspend(...)`.

---

## 5. Reference

### `@task(name=..., ...)` (the decorator)

Wraps an `async def f(ctx: TaskContext[T]) -> R` function and returns
a `Task[T, R]`. The `name` argument is the routing key the framework
uses to discover the handler on recovery. Use a stable string —
changing it strands existing tasks.

### `Task` (the handle)

The decorated function exposes two keyword-only entry points:

```python
async def run(
    *, task_id: str, input: T,
    title: str | None = None,
    tags: dict[str, str] | None = None,
    stale_timeout: float = 300.0,
) -> TaskResult[R]

async def start(
    *, task_id: str, input: T,
    title: str | None = None,
    tags: dict[str, str] | None = None,
    stale_timeout: float = 300.0,
    input_id: str | None = None,
    if_last_input_id: str | None = None,
) -> TaskRun[R]
```

`.run()` blocks until the task reaches a terminal state and returns a
`TaskResult`. `.start()` returns immediately with a `TaskRun` handle
you can stream from or `await handle.result()` on. The
`input_id` / `if_last_input_id` sequential-input preconditions live
only on `.start()` (see §4).

Retry policy and the stream handler are configured on the
`@task(...)` decorator (or via `Task.options(retry=...)` for a
derived `Task`), not per-call — see §4. They have to be registered
on the decorated function so they remain available after a crash,
when the framework re-enters the task with only the decorator's
options. Session identity is platform-derived from the
`FOUNDRY_AGENT_SESSION_ID` environment variable; there is no
per-call override.

### `TaskContext`

The single argument your handler receives. Properties:

| Property | Type | Description |
|----------|------|-------------|
| `input` | `T` | The typed input value. |
| `entry_mode` | `EntryMode` | `"fresh"` / `"recovered"` / `"resumed"`. |
| `task_id` | `str` | Task identity. |
| `metadata` | `TaskMetadata` | Callable namespace facade (see §4). |
| `cancel` | `asyncio.Event` | Set when cancellation is requested. |
| `shutdown` | `asyncio.Event` | Set when the container is shutting down. |
| `retry_attempt` | `int` | Cross-lifetime retry counter (see §4). |
| `recovery_count` | `int` | Increments each time the task is re-acquired by a new lifetime (after a crash). |
| `steering_generation` | `int` | Increments each time the task drains for steering. |
| `was_steered` | `bool` | `True` when this entry is part of a steering drain. |
| `pending_inputs` | `Sequence[Any]` | Snapshot of queued steering inputs at entry. |

Methods:

- `await ctx.suspend(output=...)` — park the task in `suspended`.
- `await ctx.stream(chunk)` — emit an incremental chunk to consumers.

### `TaskMetadata`

The persistent state surface returned by `ctx.metadata` and
`ctx.metadata(name)`. Dict-like (`__getitem__` / `__setitem__` /
`__contains__` / `__iter__` / `.get()` / `.to_dict()`) plus:

- `metadata.flush()` — force-persist any pending writes for this
  namespace. Returns when the write is durably committed.
- `metadata.increment(key)` — atomic numeric increment.
- `metadata.append(key, value)` — append to a list-valued key.

### `EntryMode`

A `Literal["fresh", "recovered", "resumed"]` you import for type
hints:

```python
from azure.ai.agentserver.core.durable import EntryMode
def on_entry(mode: EntryMode) -> None: ...
```

### `TaskResult` / `TaskRun` / `TaskStatus`

See §4. `TaskStatus` is a literal of the four lifecycle states:
`"pending" | "in_progress" | "suspended" | "completed"`.
Unsuccessful terminations (failure / cancel / terminate) are still
`"completed"` from the store's perspective — the *outcome* is
communicated to the caller through `.run()` / `.result()` (return
value, or one of the typed exceptions in §4).

### `Suspended`

The suspended-state envelope your handler returns via
`return await ctx.suspend(...)`. The framework also surfaces it on
the consumer side as `TaskResult.suspended` when a `.run()` call
returns from a suspension. Carries the optional `output` snapshot
the handler passed to `ctx.suspend(...)`.

### `RetryPolicy`

```python
RetryPolicy(
    *,
    initial_delay: timedelta = timedelta(seconds=1),
    backoff_coefficient: float = 2.0,
    max_delay: timedelta = timedelta(seconds=60),
    max_attempts: int = 3,
    retry_on: tuple[type[Exception], ...] | None = None,
    jitter: bool = True,
)
```

`max_attempts` is the total failure-retry budget across all
lifetimes for the task; crash recovery does NOT consume it.
`retry_on=None` retries every exception; pass a tuple to scope
retries to specific types.

### Streaming types (`StreamHandler`, `StreamHandlerFactory`, `QueueStreamHandler`)

See §4. Most users never touch these directly — they construct via
`stream_handler_factory=` on `@task`. The default
`QueueStreamHandler` is what you get when you do not override.

### Exceptions

These are the exceptions developers actually catch. All others surfaced
by the package are either internal-only or wrap one of these.

| Exception | Raised by | When |
|-----------|-----------|------|
| `TaskFailed` | `.run()` / `.result()` | Handler raised an unhandled exception. `.error` carries the structured cause. |
| `TaskCancelled` | `.run()` / `.result()` | Task was cancelled via `handle.cancel()`. |
| `TaskTerminated` | `.run()` / `.result()` | Task was forcefully terminated (operator / platform). Carries `reason`. |
| `TaskNotFound` | `handle.result()` / `.start()` | Referenced `task_id` has been deleted between calls. |
| `TaskConflictError` | `.run()` / `.start()` | Collided with an already-active non-steerable task, or with a `task_id` whose previous run already completed. |
| `LastInputIdPreconditionFailed` | `.start(if_last_input_id=...)` | Sequential-input precondition not satisfied (subclass of `TaskPreconditionFailed`). |
| `TaskPreconditionFailed` | `.start(...)` | Base for input-acceptance precondition failures. |
| `SteeringQueueFull` | `.start(...)` on steerable task | Steerable task's input queue is full. |

---

## 6. Patterns

The following patterns are the small set of idioms most agent code
ends up using. Each is **complete** — copy, change the name, and
ship.

### Pattern A — At-most-once side effect across recovery

```python
@task(name="charge_card")
async def charge_card(ctx: TaskContext[dict]) -> dict:
    if ctx.metadata.get("charge_id") is None:
        # Pre-issue dedup token, fence it durably BEFORE the side effect.
        token = uuid.uuid4().hex
        ctx.metadata["charge_id"] = token
        await ctx.metadata.flush()
        await stripe.charge(amount=ctx.input["amount"], idempotency_key=token)
    return {"charged": ctx.metadata["charge_id"]}
```

If the lifetime dies between the `flush()` and the `stripe.charge`
call, the next lifetime sees `charge_id` already set and retries the
*charge* call (Stripe's idempotency_key dedups the duplicate).

### Pattern B — Resumable iteration with a watermark

```python
@task(name="bulk_index")
async def bulk_index(ctx: TaskContext[list[str]]) -> dict:
    items = ctx.input
    start = ctx.metadata.get("index", 0)
    for i in range(start, len(items)):
        await index_one(items[i])
        ctx.metadata["index"] = i + 1
    return {"indexed": len(items)}
```

On crash, the recovered lifetime picks up at the last persisted
watermark. The framework snapshots metadata at lifecycle boundaries
(see §4); for crash safety mid-loop, add
`await ctx.metadata.flush()` after each write.

### Pattern C — Multi-turn conversation via suspend/resume

```python
@task(name="chat_session")
async def chat_session(ctx: TaskContext[dict]) -> dict:
    msg = ctx.input["message"]
    history = ctx.metadata.get("history", [])
    history.append({"role": "user", "content": msg})
    reply = await llm(history)
    history.append({"role": "assistant", "content": reply})
    ctx.metadata["history"] = history
    return await ctx.suspend(output={"reply": reply})
```

Every `.run(task_id=session_id, input={"message": ...})` resumes the
same task with the new turn.

### Pattern D — Per-namespace metadata to keep concerns isolated

```python
@task(name="orchestrator")
async def orchestrator(ctx: TaskContext[dict]) -> dict:
    # Default namespace: caller-facing checkpoints.
    ctx.metadata["progress_pct"] = 0
    # Sibling namespace: tool-call dedup tokens.
    tools = ctx.metadata("tool_calls")
    for tool in plan:
        if tools.get(tool.id) is None:
            tools[tool.id] = await invoke_tool(tool)
            await tools.flush()
    ctx.metadata["progress_pct"] = 100
    return ctx.metadata("tool_calls").to_dict()
```

### Pattern E — Streaming partial results to a UI

```python
@task(name="research")
async def research(ctx: TaskContext[str]) -> str:
    sources = await search(ctx.input)
    for s in sources:
        await ctx.stream({"event": "source", "url": s.url})
    return await synthesize(sources)
```

Consumer:

```python
run = await research.start(task_id="r-1", input="LLM observability")
async for chunk in run:
    ui.push(chunk)
final = await run.result()
```

---

## 7. Operational / Testing

### Local development

Durable storage is **zero-configuration**. When you run the agent on
your laptop, durable task state lives in a file under the project's
working directory so you can `cat` it while debugging. When the same
agent runs in the hosted platform, state lives in the platform's
task-storage service. Your handler code does not change between the
two, and there is no provider class or environment variable for you
to set — the framework auto-selects.

### Testing a recovery path

You don't need a crashed process to exercise the `"recovered"` entry
mode. In a unit test, invoke the handler once with a `task_id`, let
it write a watermark, and tear the first invocation down before it
completes. Then invoke it again with the **same** `task_id` (and a
short `stale_timeout=` so the framework treats the first lifetime as
gone) — the second invocation will see `ctx.entry_mode == "recovered"`
and the persisted `ctx.metadata` / counters from the first run.

```python
@task(name="resumable")
async def resumable(ctx: TaskContext[int]) -> int:
    if ctx.entry_mode == "fresh":
        ctx.metadata["seen"] = ctx.input
        await ctx.metadata.flush()
        raise SystemExit("simulate a crash")  # tear lifetime 1 down
    assert ctx.entry_mode == "recovered"
    return ctx.metadata["seen"]

# Lifetime 1: writes watermark, then dies.
with pytest.raises(SystemExit):
    await resumable.run(task_id="t-1", input=42)
# Lifetime 2: short stale_timeout so the framework reclaims t-1.
result = await resumable.run(task_id="t-1", input=42, stale_timeout=0.1)
assert result.output == 42
```

### What the framework persists at lifecycle boundaries

| Boundary | What is persisted |
|----------|-------------------|
| `start` | Input, initial counters, namespace snapshot. |
| `suspend` | `Suspended` envelope, namespace snapshot, queued inputs (steerable). |
| Handler returns or raises | Terminal status (`completed`), final namespace snapshot, output (or structured error). |
| `flush()` (handler-initiated) | The addressed namespace only, atomically. |

There is no background auto-flush loop. Persistence is **explicit
flush** (handler-side) and lifecycle-boundary snapshots (framework-side).

### Operational counters

- `recovery_count` — how many times this task has been re-acquired by
  a new lifetime. Useful as a recovery-loop health signal.
- `steering_generation` — how many times this task has drained for
  steering. Useful for steering-heavy conversations.
- `retry_attempt` — how many handler-raised retryable failures have
  occurred. Bounded by `RetryPolicy.max_attempts`.

---

## 8. What This Is NOT

- **Not a deterministic-replay framework.** `@task` does not record
  every effect so you can replay them on recovery. The handler is
  re-invoked from the top with whatever state survived; the durable
  bits are `ctx.input`, `ctx.metadata`, and the counters. Determinism
  is your handler's responsibility (the at-most-once pattern in §6 is
  the standard workaround).
- **Not a workflow engine.** If you want fan-out / fan-in,
  child-workflow orchestration, signals, timers as first-class
  primitives, use Temporal / Durable Functions. `@task` is the thin
  durable boundary around a single agent function — use it inside
  those engines if you want, but it is not a replacement for them.
- **Not a bulk data store.** `ctx.metadata` is intentionally small.
  Persist conversation history, LLM outputs, and large checkpoints
  through your underlying framework (LangGraph SqliteSaver, your own
  DB, etc.). Use metadata only for small watermarks and dedup tokens.
- **Not a queue.** A `task_id` identifies one logical unit of work.
  If you want competing consumers off a shared queue, you want a
  different primitive.

---

## Rename map (for users migrating from earlier pre-release builds)

| Old name | New name | Notes |
|----------|----------|-------|
| `ctx.run_attempt` | `ctx.retry_attempt` | Now durable across crash/recovery. |
| `ctx.lease_generation` | `ctx.recovery_count` | Same semantics, clearer name. |
| `ctx.generation` | `ctx.steering_generation` | Same semantics, clearer name. |
| `ctx.previous_input` | (deleted) | Read the queued inputs from `ctx.pending_inputs` instead. |
| `ctx.title` / `ctx.description` / `ctx.tags` / `ctx.agent_name` | (deleted) | Not part of the primitive's contract anymore. |
| `@task(store_input=True)` | (deleted) | Storage is always implicit. |
| `@task(max_pending=...)` | (deleted) | Server-side back-pressure lives at a different layer. |
| `@task(lease_duration_seconds=...)` | (deleted) | The platform owns lease duration. |
| `payload["_framework"][...]` | `payload["_last_input_id"]`, `payload["_retry_attempt"]`, `payload["metadata:<name>"]` | Top-level `_*` slots; named-namespace metadata moved out of a single bucket. |
| `TaskSuspended` exception | (deleted) | Use `ctx.suspend(...)`'s return value; observers see the `Suspended` envelope. |
