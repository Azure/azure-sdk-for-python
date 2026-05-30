# Durable Tasks Developer Guide

> The end-user-developer guide for the `@task` primitive shipped by
> `azure-ai-agentserver-core`.
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

@task(name="flaky", retry=RetryPolicy(max_attempts=5))
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

### Suspend, resume, and multi-turn workflows (`Suspended`)

A handler that runs to completion is **one-shot**. A handler that
*suspends* enters a different mode: it persists its state, returns
control to the caller, and waits for the next input to bring it back
to life. This is the engine behind every multi-turn agent workflow —
chat sessions, approval flows, human-in-the-loop pipelines,
long-running orchestrations that wake up on external events.

```python
@task(name="approval_flow")
async def approval_flow(ctx: TaskContext[dict]) -> dict:
    if ctx.entry_mode == "fresh":
        proposal = await draft_proposal(ctx.input)
        ctx.metadata["proposal"] = proposal
        await ctx.metadata.flush()
        return await ctx.suspend(output={"awaiting": "approval", "proposal": proposal})

    # entry_mode == "resumed": ctx.input is the approver's verdict.
    if ctx.input["approved"]:
        return {"status": "shipped", "proposal": ctx.metadata["proposal"]}
    return {"status": "rejected", "proposal": ctx.metadata["proposal"]}
```

What's happening under the hood:

1. **`await ctx.suspend(output=...)`** moves the task to the `suspended`
   state, persists the metadata snapshot and the optional `output`
   envelope, and exits the handler. The caller's `.run()` / `.start()`
   resolves immediately with a `Suspended` envelope carrying that
   `output` — there is no in-flight execution waiting in memory.
2. **The next `.run(task_id=..., input=...)` or
   `.start(task_id=..., input=...)`** transitions the task from
   `suspended` back to `in_progress`. The framework re-invokes your
   handler on a fresh `TaskContext`, with `ctx.entry_mode="resumed"`,
   `ctx.input` populated from the new caller-supplied input, and
   `ctx.metadata` re-hydrated from the persisted snapshot.
3. **State lives in `ctx.metadata`** (see the metadata-namespace
   section above), not in handler-local variables, because those are
   gone the moment the handler returns. Whatever you want to see on
   the next turn must be flushed before you `return await ctx.suspend(...)`.

Multi-turn workflows are just this same suspend/resume cycle applied
repeatedly to the same `task_id` — see Pattern C in §6 for the
end-to-end chat-loop example.

### Steering: replacing in-flight input on a new turn (`steerable`)

`@task(steerable=True)` upgrades a task from "one input at a time" to
"the caller can preempt the in-flight input with a new one". This is
the model that lets a chat user say *"actually, ignore that and
search for X instead"* mid-stream and get a coherent answer to the
new question rather than the stale one.

#### What `.start()` does on an in-flight steerable task

Non-steerable (`steerable=False`, default):

- `.start(task_id=existing_in_progress, input=...)` → `TaskConflictError`.
  One input at a time, no exceptions.

Steerable (`steerable=True`):

- `.start(task_id=existing_in_progress, input=...)` →
  1. **The new input is queued** at the tail of an internal
     `pending_inputs` FIFO.
  2. **The cancel signal is raised** on the currently-executing
     generation (`ctx.cancel.is_set()` becomes True for the handler
     that's running right now).
  3. **A *new* `TaskRun` handle is returned** to the caller —
     specifically, the steering-ack handle. Its `.result()` resolves
     when the generation that *will eventually process this new input*
     finishes.
  4. **The original caller's `TaskRun` resolves with
     `TaskResult(status="superseded", output=None)`** — no exception
     is raised. The original caller cleanly observes "I got displaced
     by a later turn; I am done."
- If the steering queue is at its internal bound, `.start()` raises
  `SteeringQueueFull` instead of queuing.

#### What your handler is supposed to do when steered

A steerable handler **must** check `ctx.cancel.is_set()` at every
suspension-friendly boundary (between LLM tokens, between tool
calls, between iterations of a loop). On a True read, the polite,
correct shape is to suspend with the partial output you have so far:

```python
@task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    history = ctx.metadata.get("history", [])
    history.append({"role": "user", "content": ctx.input["message"]})

    reply_chunks: list[str] = []
    async for chunk in llm_stream(history):
        if ctx.cancel.is_set():
            # Steering arrived. Stash the partial turn and bow out.
            history.append({"role": "assistant", "content": "".join(reply_chunks), "partial": True})
            ctx.metadata["history"] = history
            await ctx.metadata.flush()
            return await ctx.suspend(output={"interrupted": True})
        reply_chunks.append(chunk)

    reply = "".join(reply_chunks)
    history.append({"role": "assistant", "content": reply})
    ctx.metadata["history"] = history
    return await ctx.suspend(output={"reply": reply})
```

The framework then drains the next queued input by re-invoking the
handler with `entry_mode="resumed"` and `ctx.was_steered=True`.

#### Steering observability: `was_steered`, `pending_inputs`, `steering_generation`

On a steering-driven re-entry, your `TaskContext` exposes three
read-only fields:

- **`ctx.was_steered: bool`** — True when this invocation is being
  driven by a steering input drain (as opposed to a plain
  `suspend()` → `.run()` resume). Branch on this to apply any
  steering-specific logic (for example: log a "user changed their
  mind" event for analytics).
- **`ctx.pending_inputs: list[Any]`** — an *advisory snapshot* of
  whatever else is queued behind the input you're processing right
  now. Use it for logging or to decide "I'm three turns behind, I
  should short-circuit even harder". Do NOT use it as the live queue
  — it does not update mid-handler.
- **`ctx.steering_generation: int`** — monotonic counter of how many
  steering drains the framework has performed for this `task_id`.
  Useful for dashboards and dedupe keys.

#### Rapid-fire short-circuit

If three steering inputs land while the first generation is still
draining (`[B, C, D]` queued), the framework's drain loop calls your
handler for B *with `ctx.cancel` already set* (because C and D are
still queued). The intended idiom is to immediately suspend without
doing the actual work for B, then again for C, and only execute D to
completion. This keeps the user-visible latency to the most recent
input close to "one handler run", not "N handler runs serialized".

#### Composing multi-turn + steering

A task can be both **steerable** AND **multi-turn**. The handler
suspends after each turn (multi-turn), and additionally accepts
preempting input mid-turn (steering). The two are orthogonal: the
suspend/resume cycle drives sequential turns; `ctx.cancel` +
`pending_inputs` drive within-turn preemption. Pattern F in §6 shows
the unified shape.


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
  terminal-for-this-caller state. `TaskResult` carries:
  - `result.output` — your handler's return value, or the snapshot
    passed to `ctx.suspend(output=...)`, or `None` if the caller was
    superseded by a later steering input.
  - `result.status: Literal["completed", "suspended", "superseded"]`
    — what *kind* of outcome this is, with the corresponding
    convenience properties `result.is_completed`,
    `result.is_suspended`, `result.is_superseded`. Note: this is a
    **different literal** from the four-state `TaskStatus`; it's
    specifically the caller-observable outcome.
  - `result.suspension_reason: str | None` — populated only on the
    `"suspended"` branch when the handler returned via
    `ctx.suspend(reason=...)`.
- `result.status == "superseded"` is the steering outcome: the
  original caller's `.run()` cleanly resolves with
  `TaskResult(status="superseded", output=None)` when a later
  `.start()` queued a new input and the framework drained past their
  generation. No exception is raised — it's the polite "you got
  displaced" signal.
- `Task.start()` returns a `TaskRun[Output]` handle you can poll,
  stream, or `await run.result()`-on. `TaskRun.cancel()` raises the
  cancel signal; `TaskRun.terminate(reason=...)` is the forceful
  exit (goes through the failure path; the typed exception is
  `TaskTerminated`).

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

| Keyword                  | Type                                      | Default | Description |
|--------------------------|-------------------------------------------|---------|-------------|
| `name`                   | `str`                                     | `fn.__qualname__` | Stable identity for recovery routing. Always set this explicitly for production tasks. |
| `title`                  | `str \| Callable[[T, str], str] \| None`  | `None`  | Human-readable title (template or callable). |
| `tags`                   | `dict[str, str] \| Callable[[T, str], dict[str, str]] \| None` | `None` | Default tags (static dict or callable factory). |
| `timeout`                | `timedelta \| None`                       | `None`  | Execution timeout. When elapsed, `ctx.cancel` is set cooperatively. |
| `ephemeral`              | `bool`                                    | `True`  | Delete the persisted record on terminal exit. |
| `retry`                  | `RetryPolicy \| None`                     | `None`  | Retry policy for handler-raised exceptions. Recovery-safe (applied on every entry, including post-crash). |
| `steerable`              | `bool`                                    | `False` | Allow `.start()` on an `in_progress` task to queue a steering input instead of raising. |
| `stream_handler_factory` | `Callable[[str], StreamHandler] \| None`  | `None`  | Custom stream-handler factory. Recovery-safe: fresh starts, resumes, and crash recovery all use this factory. |
| `stale_timeout`          | `float` (seconds)                         | `300.0` | Threshold for callsite-driven recovery (see §7). |

All decorator options are recovery-safe: the framework only knows
about the registered decorator after a crash, so anything that needs
to survive recovery must be configured here. Use `Task.options(...)`
to derive a variant with overrides without redefining the function.

### `Task` (the handle)

The decorated function exposes two keyword-only entry points:

```python
async def run(
    *, task_id: str, input: T,
    input_id: str | None = None,
    if_last_input_id: str | None = None,
) -> TaskResult[R]

async def start(
    *, task_id: str, input: T,
    input_id: str | None = None,
    if_last_input_id: str | None = None,
) -> TaskRun[R]
```

`.run()` blocks until the task reaches a terminal state and returns a
`TaskResult`. `.start()` returns immediately with a `TaskRun` handle
you can stream from or `await handle.result()` on. Both accept the
same `input_id` / `if_last_input_id` sequential-input preconditions
(see §4).

Everything else that characterises a task — `title`, `tags`, `retry`,
`stream_handler_factory`, `stale_timeout`, `steerable`, `ephemeral`,
`timeout` — is configured once on the `@task(...)` decorator (or via
`Task.options(...)` for a derived `Task`). There is no per-call
override. This is deliberate so the settings survive crash recovery:
after the container crashes and the framework re-enters the task, it
has only the registered decorator's view to work with — a per-call
override would silently disappear at the crash boundary. Session
identity is platform-derived from the `FOUNDRY_AGENT_SESSION_ID`
environment variable.

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

There are **two separate literals** in play here — pick the right
one for the question you're asking:

- **`TaskStatus = Literal["pending", "in_progress", "suspended",
  "completed"]`** — the *stored lifecycle state* on the task record.
  Four values only. Unsuccessful terminations (failure / cancel /
  terminate) are still `"completed"` from the store's perspective;
  the *cause* is surfaced through the typed exceptions in §4.
- **`TaskResult.status = Literal["completed", "suspended",
  "superseded"]`** — the *caller-observable outcome* of a single
  `.run()` / `.result()` call. Three values:
  - `"completed"` — handler returned normally; `result.output` is
    the return value.
  - `"suspended"` — handler called `ctx.suspend(output=...)`;
    `result.output` is the suspend envelope; `result.suspension_reason`
    is the optional reason passed in.
  - `"superseded"` — a steering input displaced this caller before
    their generation finished; `result.output` is `None`. See §4
    "Steering" for the full mechanic.

`TaskResult` also exposes `is_completed`, `is_suspended`, and
`is_superseded` boolean properties — preferred over string compares.

`TaskRun` is the handle returned by `Task.start()`. Useful members:

- `await run.result()` — block until terminal-for-this-caller; same
  `TaskResult` semantics as above.
- `async for chunk in run` — stream incremental output (see
  Streaming).
- `await run.cancel()` — signal cancellation; the handler's
  `ctx.cancel` event fires.
- `await run.terminate(reason=...)` — forceful exit; the caller's
  `.result()` raises `TaskTerminated`.
- `run.status`, `run.metadata`, `run.lease_expiry_count` — last-known
  values; call `await run.refresh()` to re-fetch from the store.

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
    if ctx.entry_mode == "fresh":
        history: list[dict] = []
    else:
        history = ctx.metadata.get("history", [])

    history.append({"role": "user", "content": ctx.input["message"]})

    reply = await llm(history)
    history.append({"role": "assistant", "content": reply})

    ctx.metadata["history"] = history
    ctx.metadata["turn_count"] = ctx.metadata.get("turn_count", 0) + 1
    await ctx.metadata.flush()

    return await ctx.suspend(output={"reply": reply, "turn": ctx.metadata["turn_count"]})
```

Caller (one session, many turns, same `task_id`):

```python
session = f"chat:{user_id}:{conversation_id}"

# Turn 1.
r1 = await chat_session.run(task_id=session, input={"message": "Hello!"})
print(r1.output["reply"])      # is_suspended is True; we'll come back.

# Turn 2 — same task_id resumes the persisted history.
r2 = await chat_session.run(task_id=session, input={"message": "What did I just say?"})
print(r2.output["reply"])      # The LLM sees turn 1 in history.
```

Why this works:

- **State survives in `ctx.metadata`**, not in handler locals. The
  handler exits between turns; only metadata is persisted.
- **The same `task_id` is the conversation's identity.** Pick a
  stable key (user + conversation id, in this example) so subsequent
  `.run()` calls land on the same task.
- **`entry_mode == "fresh"` branches initialization** from resumption.
  Turn 1 sees `"fresh"`; every subsequent turn sees `"resumed"`.
- **`await ctx.metadata.flush()` before `ctx.suspend()`** ensures the
  history is durably persisted before the caller is told the turn is
  done. The framework also persists at the suspend boundary, but an
  explicit pre-suspend flush is cheap insurance for partial-write
  scenarios.

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

### Pattern F — Steerable chat: preempting in-flight turns

```python
@task(name="steerable_chat", steerable=True)
async def steerable_chat(ctx: TaskContext[dict]) -> dict:
    history = ctx.metadata.get("history", []) if ctx.entry_mode != "fresh" else []
    history.append({"role": "user", "content": ctx.input["message"]})

    if ctx.was_steered and ctx.pending_inputs:
        # Multiple inputs already queued behind us — fast-suspend so
        # the framework can drain to the freshest input without doing
        # work for stale ones.
        ctx.metadata["history"] = history
        await ctx.metadata.flush()
        return await ctx.suspend(output={"superseded_early": True})

    reply_buf: list[str] = []
    async for chunk in llm_stream(history):
        if ctx.cancel.is_set():
            # A new turn arrived. Stash the partial and yield.
            history.append({
                "role": "assistant",
                "content": "".join(reply_buf),
                "partial": True,
            })
            ctx.metadata["history"] = history
            await ctx.metadata.flush()
            return await ctx.suspend(output={"interrupted": True})
        reply_buf.append(chunk)

    reply = "".join(reply_buf)
    history.append({"role": "assistant", "content": reply})
    ctx.metadata["history"] = history
    await ctx.metadata.flush()
    return await ctx.suspend(output={"reply": reply})
```

Caller side, showing the supersede semantics:

```python
session = f"chat:{user_id}:{conversation_id}"

# Turn 1 starts a slow generation.
run1 = await steerable_chat.start(task_id=session, input={"message": "Tell me a long story."})

# 50ms later, user changes their mind.
run2 = await steerable_chat.start(task_id=session, input={"message": "Actually, what's 2 + 2?"})

# Original caller's run cleanly resolves "superseded".
r1 = await run1.result()
assert r1.is_superseded         # output is None; no exception.

# Steering ack resolves with the new turn's actual reply.
r2 = await run2.result()
assert r2.is_suspended          # the steerable handler ends each turn via ctx.suspend(...)
print(r2.output["reply"])       # "4"
```

What this pattern covers that Pattern C doesn't:

- **`steerable=True`** turns `.start()`-on-`in_progress` from
  `TaskConflictError` into "queue + cancel".
- **`ctx.cancel.is_set()`** is the in-handler signal to wind down
  cleanly. Suspending with a partial output is the canonical shape.
- **`ctx.was_steered` + `ctx.pending_inputs`** let a handler
  short-circuit when it's already multiple turns behind.
- **`TaskResult.is_superseded`** is how the displaced caller learns
  their turn was preempted — no exception, just a polite terminal
  outcome.
- **Backpressure**: if a misbehaving client floods `.start()`, the
  bounded steering queue raises `SteeringQueueFull` to the caller —
  the handler never sees runaway memory growth.

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
completes. Then invoke it again with the **same** `task_id` — the
second invocation will see `ctx.entry_mode == "recovered"` and the
persisted `ctx.metadata` / counters from the first run.

Set a short `stale_timeout=` on the decorator so the framework
considers the first lifetime gone immediately. (For production tasks
the default 5-minute timeout is what you want — see "Stale-task
recovery and `stale_timeout`" below.)

```python
@task(name="resumable", stale_timeout=0.1)
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
# Lifetime 2: framework treats t-1 as stale → recovered entry mode.
result = await resumable.run(task_id="t-1", input=42)
assert result.output == 42
```

If a single test needs both the *stale* and *not-stale* outcomes on
the same handler, derive variants with `Task.options(stale_timeout=...)`
rather than redefining the function.

### Stale-task recovery and `stale_timeout`

`stale_timeout` (decorator option, default 300 seconds) controls
**how long the framework waits before treating an `in_progress`
record from a previous lifetime as abandoned and eligible for
re-acquisition by a new `.run()` / `.start()` call**.

It exists because a crash leaves an `in_progress` record behind with
no signalled outcome — and the new lifetime needs a deterministic
rule for "is anyone still working on this, or am I free to take it
over?". The framework checks `now - updated_at` against
`stale_timeout` at the start of every `.run()` / `.start()` that
encounters an `in_progress` record:

| Outcome | Behaviour |
|---------|-----------|
| `now - updated_at > stale_timeout` | The call enters with `entry_mode == "recovered"`. |
| `now - updated_at ≤ stale_timeout` | A `TaskConflictError` is raised — the framework assumes the prior lifetime is still active. |

This callsite-driven check is **independent of** the background
lease-reclaim loop that runs at host startup. The background loop
reclaims tasks whose lease owner is a *previous host instance*
(dead/restarted) and re-enters them automatically. `stale_timeout`
covers the narrower window where a callsite happens to encounter
an unreclaimed-yet record — for example a same-process test that
simulates a crash, or the briefly-racy window during host startup.

Pick a value that comfortably exceeds the longest legitimate gap
between the task's own `ctx.metadata.flush()` / lifecycle-boundary
writes. For a quick `query()` task that finishes in seconds the
default 300s is generous; for a multi-hour batch job that only
flushes between batches, raise it to several times the batch
interval. In tests, drop it to `0.0`–`0.1` to deterministically
take the recovered path.

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
