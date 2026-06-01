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
| `completed` | Terminal. The handler is finished and will not run again. The *outcome* (success, failure, cancellation) is communicated to the caller through `.run()` / `.result()` — either as the return value, or as one of `TaskFailed` / `TaskCancelled` (see §4). Outcome is not encoded in the status field. |

The framework computes the **entry mode** every time it invokes your
handler, by looking at the task's current state in the store:

| Current state | Entry mode | What it means for your code |
|---------------|------------|------------------------------|
| No task / `pending` | `"fresh"` | First invocation. No prior state. |
| `suspended` | `"resumed"` | Caller provided new input; resume from there. |
| `in_progress` (previous lifetime torn down) | `"recovered"` | Previous lifetime crashed; you are the new lifetime. |
| `in_progress` (steerable, mid-flight) | `"resumed"` (with `ctx.is_steered_turn=True`) | Another input was queued; this is the next-turn re-entry. |

You read `ctx.entry_mode` (an `EntryMode` literal) once at the top of
your handler and branch on it.

### What you persist, what the framework persists

- **Framework persists**: task metadata you write to `ctx.metadata`,
  the current input, lifecycle counters (`ctx.retry_attempt`,
  `ctx.recovery_count`), suspended-state
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

### Steering: queueing a new input on a steerable task (`steerable`)

`@task(steerable=True)` upgrades a task from "one input at a time" to
"the caller can queue a new input while the handler is mid-flight".
This is the model that lets a chat user say *"actually, ignore that
and search for X instead"* mid-stream and get a coherent answer to
the new question.

#### What `.start()` does on an in-flight steerable task

Non-steerable (`steerable=False`, default):

- `.start(task_id=existing_in_progress, input=...)` → `TaskConflictError`.
  One input at a time, no exceptions.

Steerable (`steerable=True`):

- `.start(task_id=existing_in_progress, input=...)` →
  1. **The new input is queued** at the tail of an internal
     pending-inputs FIFO.
  2. **The cancel signal is raised** on the currently-executing turn
     (`ctx.cancel.is_set()` becomes True for the handler that's
     running right now). The framework also flips
     `ctx.pending_input_count` from `0` to `1` (or whatever the live
     backlog is); a handler can read this live mid-flight to make
     "should I bail?" decisions.
  3. **A new `TaskRun` handle is returned** to the caller. Its
     `.result()` resolves with **whatever the next turn emits** —
     it is treated as the steerer of that next turn.
- If the steering queue is at its internal bound, `.start()` raises
  `SteeringQueueFull` instead of queuing.

**Steering is plain multi-turn.** The mental model is "the second
`.start()` queues a new input, then the framework drives the next
turn of the handler the same way a normal `.run()` after
`ctx.suspend()` would." There is no separate "supersede" mechanism
on the public surface — the first turn's caller observes the
natural multi-turn outcome (whatever the handler returned or
suspended with), and the steerer's caller observes the next turn's
outcome.

#### What the first turn's caller sees

When the first turn ends, its `TaskResult` is whatever the handler
chose, with no special steering-specific shape:

| Handler ends turn 1 with... | First caller's `TaskResult` |
|---|---|
| `return await ctx.suspend(output=X)` | `TaskResult(status="suspended", output=X, suspension_reason=R)` — identical to plain multi-turn. The framework then re-enters for the queued steering input. |
| `return value` | `TaskResult(status="completed", output=value)`. The handler chose to finish; the task is terminal; the queued steerer's `.result()` resolves with `TaskConflictError(current_status="completed")` instead. |
| `raise SomeError` | `.result()` raises the appropriate typed exception. The task is terminal; the queued steerer's `.result()` resolves with `TaskConflictError(current_status="failed")` instead. |

The handler's emitted output via `ctx.suspend(output=X)` is delivered
unconditionally to the first caller — it is NEVER replaced by what a
later turn produces, regardless of whether a steering input was
queued during turn 1.

#### Cooperative cancellation: the handler is in charge

`ctx.cancel` is **advisory**. The framework signals it when a
steering input arrives (alongside `ctx.pending_input_count > 0`),
but it does not preempt your handler — your handler decides what to
do about it. There are three legitimate strategies, and the choice
belongs to the handler author:

- **A — Yield immediately.** Check `ctx.cancel.is_set()` (or
  `ctx.pending_input_count > 0`) at the next boundary and
  `return await ctx.suspend(output=...)` right away. Lowest
  user-visible latency to the new turn; throws away whatever
  partial work was in flight. Use this when the in-flight work is
  cheap to re-derive or strictly stale.

- **B — Wind down to a safe checkpoint, then suspend.** Finish the
  current tool call / token batch / loop iteration, persist a
  durable checkpoint via `ctx.metadata`, *then*
  `return await ctx.suspend(output=...)`. Costs one extra checkpoint
  of latency but keeps your invariants clean. Use this when the
  in-flight work has external side effects that need a clean cut
  point.

- **C — Ignore cancel and finish.** Don't read `ctx.cancel` at all;
  let the handler run to its normal `return value`. The task ends;
  the queued steerer's `.result()` raises `TaskConflictError`. Use
  this when the current input must complete atomically (e.g., a
  financial transaction, a multi-step tool sequence that cannot
  leave the world half-done).

#### Example: cooperative suspend (strategy A)

```python
@task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    history = ctx.metadata.get("history", [])
    history.append({"role": "user", "content": ctx.input["message"]})

    reply_chunks: list[str] = []
    async for chunk in llm_stream(history):
        if ctx.cancel.is_set():
            # Strategy A: bow out immediately.
            history.append({"role": "assistant", "content": "".join(reply_chunks), "partial": True})
            ctx.metadata["history"] = history
            return await ctx.suspend(output={"interrupted": True})
        reply_chunks.append(chunk)

    reply = "".join(reply_chunks)
    history.append({"role": "assistant", "content": reply})
    return await ctx.suspend(output={"reply": reply})
```

(Note: explicit `ctx.metadata.flush()` is no longer required at the
suspend boundary — the framework auto-flushes metadata at every
terminal-of-turn boundary, including steering drain shortcuts. See
§4 Metadata.)

The framework then drains the next queued input by re-invoking the
handler with `entry_mode="resumed"` and `ctx.is_steered_turn=True`.

#### Steering observability: `is_steered_turn`, `pending_input_count`

On a steering-driven re-entry, your `TaskContext` exposes two
read-only fields:

- **`ctx.is_steered_turn: bool`** — `True` if and only if THIS
  invocation of the handler was constructed by the steering-drain
  code path. Every other entry path (fresh, normal resume, recovery)
  yields `False`. Orthogonal to `entry_mode`:
  `(entry_mode="recovered", is_steered_turn=True)` is a legal
  combination when a previous process crashed mid-drain.
- **`ctx.pending_input_count: int`** — live count of queued steering
  inputs (reflects current backlog, including inputs queued
  mid-handler). Reads as `0` for non-steerable tasks. Use this to
  decide "I'm three turns behind, I should short-circuit even
  harder".

#### Rapid-fire short-circuit

If three steering inputs land while the first turn is still
draining (`[B, C, D]` queued), the framework drives each turn in
order — but if a turn observes `ctx.pending_input_count > 1` it can
choose to suspend immediately (strategy A) and let the framework
drive past stale work toward the freshest input. This keeps the
user-visible latency to the most recent input close to "one handler
run", not "N handler runs serialized".

#### Composing multi-turn + steering

A task can be both **steerable** AND **multi-turn**. Steering IS
plain multi-turn: every turn's `.suspend()` checkpoint is the
boundary at which the next queued steering input (if any) drives
the next turn. The two are not orthogonal modes — they are the
same mechanism. Pattern F in §6 shows the unified shape.

### Cancellation: independent cause booleans (`timeout_exceeded`, `cancel_requested`, `pending_input_count`)

`ctx.cancel` is a bare `asyncio.Event` — observe it with
`ctx.cancel.is_set()` or `await ctx.cancel.wait()`. The framework
sets it from multiple causes; a handler observing the bare event
does NOT know **why** it was set. Three independent cause booleans
on `TaskContext` answer that question:

- **`ctx.timeout_exceeded: bool`** — `True` once the per-turn
  timeout watchdog has fired for this turn (see Timeout subsection
  below).
- **`ctx.cancel_requested: bool`** — `True` once `TaskRun.cancel()`
  was invoked against this run from external caller code.
- **`ctx.pending_input_count: int`** — live count of queued steering
  inputs (reflects current backlog).

**Causes accumulate.** Multiple cause booleans can be `True`
simultaneously (e.g., a steering input arrived AND the timeout
fired AND an external `.cancel()` was issued). They are flipped
to `True` when their cause fires and are **NEVER reset**.

**Ordering invariant.** Each cause is set BEFORE the framework
sets `ctx.cancel`. A handler observing `ctx.cancel.is_set() == True`
is guaranteed to see at least one cause boolean already `True`.

```python
@task(name="cancellable", timeout=timedelta(seconds=60))
async def cancellable(ctx: TaskContext[str]) -> str:
    while not ctx.cancel.is_set():
        await do_a_unit_of_work(ctx.input)

    # Branch on cause:
    if ctx.timeout_exceeded:
        return "(timed out — partial result)"
    if ctx.cancel_requested:
        # Operator pulled the plug — raise so the caller sees TaskCancelled.
        raise asyncio.CancelledError()
    if ctx.pending_input_count > 0:
        # A steering input is queued — suspend so the next turn picks it up.
        return await ctx.suspend(output="(pre-empted)")
    # No known cause — shouldn't happen, but fail loud.
    raise RuntimeError("ctx.cancel set with no recognised cause")
```

### Timeout: per-turn, wall-clock, durable, cooperative-only

`@task(timeout=...)` is **per-turn**, **wall-clock**, **durable**
across crashes within a turn, and **cooperative-only**:

- **Per-turn**: each handler turn (fresh entry, suspended-to-resume,
  steering drain re-entry) gets a fresh budget of `timeout` seconds.
  Multi-turn conversations don't burn the budget across turns.
- **Wall-clock**: `now - turn_started_at` is the anchor, not the
  amount of CPU time spent. Sleeping handlers still time out.
- **Durable**: a crash mid-turn does NOT reset the budget. On
  recovery, the framework reads the persisted turn-start timestamp
  and respawns the watchdog with `remaining = max(0, timeout -
  (now - turn_started_at))`, clamped to `[0, timeout]` for
  clock-skew safety. If the recovered watchdog computes
  `remaining == 0`, it fires immediately — so the recovered handler
  sees `ctx.timeout_exceeded == True` from its first checkpoint.
- **Cooperative-only**: when the watchdog fires it sets
  `ctx.timeout_exceeded = True`, then sets `ctx.cancel`, then
  exits. It does NOT cancel the lease renewal; it does NOT
  force-stop the handler. An ignoring handler runs until process
  death or external `TaskRun.cancel()`.

Worked example — crash mid-turn:

```python
@task(name="long_op", timeout=timedelta(seconds=30))
async def long_op(ctx: TaskContext[str]) -> str:
    # Lifetime 1: handler runs for 25 seconds, then container crashes.
    # Lifetime 2 (recovery, ~3 seconds later): turn_started_at is preserved;
    #   watchdog spawns with remaining ≈ 2 seconds (30 - 28).
    while not ctx.cancel.is_set():
        await do_unit()
    if ctx.timeout_exceeded:
        return "(timed out)"
    raise asyncio.CancelledError()
```

### Shutdown: `ctx.exit_for_recovery()`

When the container is shutting down (`ctx.shutdown.is_set()`), a
handler that is mid-turn and cannot finish cleanly should call
`ctx.exit_for_recovery()` instead of returning a value, calling
`ctx.suspend()`, or raising. The framework recognises the returned
sentinel and:

1. flushes `ctx.metadata` (the auto-flush invariant applies here,
   same as every terminal-of-turn boundary);
2. releases the lease on the persisted record (explicit CAS clear,
   not just stopping renewal);
3. leaves the stored status as `in_progress` (NOT transitions to
   `suspended` — the conversation continues on the next process
   start);
4. signals the in-process caller with the standard cooperative-cancel
   `TaskResult` shape (their `.result()` raises `TaskCancelled`);
5. preserves any queued steering inputs in the persisted state — they
   are NOT drained during shutdown; on recovery they remain queued.

The recovery scan on the next process startup re-enters the handler
with `ctx.entry_mode == "recovered"`.

```python
@task(name="long_chat", steerable=True)
async def long_chat(ctx: TaskContext[dict]) -> dict:
    history = ctx.metadata.get("history", [])
    history.append({"role": "user", "content": ctx.input["message"]})

    if ctx.shutdown.is_set():
        # Container is going down. Don't try to finish or suspend.
        # Save what we have and ask the framework to resurrect on next start.
        ctx.metadata["history"] = history
        return await ctx.exit_for_recovery()

    reply = await llm_call(history)
    history.append({"role": "assistant", "content": reply})
    ctx.metadata["history"] = history
    return await ctx.suspend(output={"reply": reply})
```

**Contrast against alternatives:**

| Shape | When to use | Stored outcome | Caller observes |
|---|---|---|---|
| `await ctx.exit_for_recovery()` | Container is shutting down AND you want this turn re-entered later | `in_progress` (preserved across shutdown) | `TaskCancelled` raised |
| `await ctx.suspend(output=X)` | Handler reached a clean checkpoint AND wants to expose `X` to the caller | `suspended` (caller must `.run()` again to advance) | `TaskResult(status="suspended", output=X)` |
| `raise asyncio.CancelledError()` | Handler decided to abort but the task is conceptually done | `completed` (terminal) | `TaskCancelled` raised |

**Misuse**: calling `ctx.exit_for_recovery()` when
`ctx.shutdown.is_set() == False` raises `RuntimeError` at the call
site (visible in user-code tracebacks). The task ends in `failed`,
not silently `in_progress` — misuse is loudly visible in operator
logs.

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
    passed to `ctx.suspend(output=...)`.
  - `result.status: Literal["completed", "suspended"]` — what *kind*
    of outcome this is, with the corresponding convenience properties
    `result.is_completed` and `result.is_suspended`. Note: this is a
    **different literal** from the four-state `TaskStatus`; it's
    specifically the caller-observable outcome.
  - `result.suspension_reason: str | None` — populated only on the
    `"suspended"` branch when the handler returned via
    `ctx.suspend(reason=...)`.
- Steering does NOT introduce a third status value. The first turn's
  caller observes the natural multi-turn outcome (`"suspended"` if
  the handler called `ctx.suspend(...)`, `"completed"` if it
  returned, or a typed exception if it raised). The steerer's
  `.result()` resolves with the next turn's outcome — or raises
  `TaskConflictError(current_status=...)` if the handler ended the
  task instead of suspending. See §4 Steering for the full mechanic.
- `Task.start()` returns a `TaskRun[Output]` handle you can poll,
  stream, or `await run.result()`-on. `TaskRun.cancel()` sets the
  cancel signal (along with `ctx.cancel_requested = True`); the
  handler chooses the terminal shape via its reaction to
  `ctx.cancel.is_set()`.

### Input-acceptance preconditions (`LastInputIdPreconditionFailed`, `TaskPreconditionFailed`)

For sequential-input semantics (don't accept input *N* unless the
last-accepted input was *N-1*), `.start(... if_last_input_id=...)`
applies an HTTP-`If-Match`-style precondition. Mismatch raises
`LastInputIdPreconditionFailed` (a subclass of `TaskPreconditionFailed`).

### Steering-queue backpressure (`SteeringQueueFull`)

Steerable tasks have a bounded steering input queue; once full,
new `.start()` calls raise `SteeringQueueFull`.

### Unsuccessful outcomes (`TaskFailed`, `TaskCancelled`)

When a task ends without producing a normal return value, the
*stored* task status is still `completed` — the task is finished
either way — but `.run()` / `.result()` raises one of two typed
exceptions so the caller can branch on **why** it ended:

- `TaskFailed` — the handler raised an unhandled exception. Carries
  a structured `error` dict (`type`, `message`, optional `cause`).
- `TaskCancelled` — the handler ended via the cooperative-cancel path
  (typically by raising `asyncio.CancelledError` after observing
  `ctx.cancel.is_set()`, or by returning the framework's
  `ExitForRecovery` sentinel via `ctx.exit_for_recovery()` — see §4
  Shutdown).

In addition, `TaskNotFound` is raised by `handle.result()` (and by
`.start()` when resuming) if the referenced `task_id` has been
deleted out from under the caller, and `TaskConflictError` is the
**single error type** for any "task is busy / not available" state:

| Scenario | What raises `TaskConflictError` | `current_status` carried |
|---|---|---|
| `.run()` / `.start()` against an in-progress non-steerable task with a live owner elsewhere | scheduling primitive | `"in_progress"` |
| `.run()` / `.start()` against an in-progress task whose lease has been evicted (split-brain protection) | scheduling primitive — observably identical to the live-elsewhere case from the caller's perspective | `"in_progress"` |
| Steerer's `.result()` after the handler returns or raises (terminal-with-queued-steerer) | resolved future | `"completed"` / `"failed"` / `"cancelled"` depending on terminal kind |
| `.run()` / `.start()` against an already-terminal task | scheduling primitive | the terminal status |

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
`stream_handler_factory`, `steerable`, `ephemeral`,
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
| `cancel` | `asyncio.Event` | Set when cancellation is requested for any reason (timeout, external `.cancel()`, or steering input). Read with `ctx.cancel.is_set()` / `await ctx.cancel.wait()`. |
| `timeout_exceeded` | `bool` | `True` once the per-turn timeout watchdog has fired for this turn. Set BEFORE `ctx.cancel` is set, so a handler observing `ctx.cancel.is_set() == True` is guaranteed to see at least one cause boolean already `True`. Never reset within a turn. |
| `cancel_requested` | `bool` | `True` once `TaskRun.cancel()` was invoked against this run. Set BEFORE `ctx.cancel` is set. Never reset. |
| `pending_input_count` | `int` | Live count of queued steering inputs (reflects current backlog, including inputs queued mid-handler). Reads as `0` for non-steerable tasks. |
| `is_steered_turn` | `bool` | `True` if and only if THIS invocation of the handler was constructed by the steering-drain code path. Every other entry path (fresh, normal resume, recovery) yields `False`. Orthogonal to `entry_mode`: `(entry_mode="recovered", is_steered_turn=True)` is a legal combination when a previous process crashed mid-drain. |
| `shutdown` | `asyncio.Event` | Set when the container is shutting down. Precondition for calling `ctx.exit_for_recovery()`. |
| `retry_attempt` | `int` | Cross-lifetime retry counter (see §4). |
| `recovery_count` | `int` | Increments each time the task is re-acquired by a new lifetime (after a crash). |

Methods:

- `await ctx.suspend(output=...)` — park the task in `suspended`.
- `await ctx.stream(chunk)` — emit an incremental chunk to consumers.
- `await ctx.exit_for_recovery()` — graceful-shutdown shape. See §4 Shutdown.

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
  Four values only. Unsuccessful terminations (failure / cancel) are
  still `"completed"` from the store's perspective; the *cause* is
  surfaced through the typed exceptions in §4.
- **`TaskResult.status = Literal["completed", "suspended"]`** —
  the *caller-observable outcome* of a single `.run()` / `.result()`
  call. Two values:
  - `"completed"` — handler returned normally; `result.output` is
    the return value.
  - `"suspended"` — handler called `ctx.suspend(output=...)`;
    `result.output` is the suspend envelope; `result.suspension_reason`
    is the optional reason passed in.

`TaskResult` exposes `is_completed` and `is_suspended` boolean
properties — preferred over string compares.

Steering does NOT introduce a third status value. Steering is plain
multi-turn (see §4 Steering): the first turn's caller observes the
natural multi-turn outcome (`"suspended"` if the handler called
`ctx.suspend(...)`, `"completed"` if it returned, or the typed
exception if it raised), and the steerer's `.result()` resolves with
the next turn's outcome (or raises `TaskConflictError` if the
handler ended the task before draining).

`TaskRun` is the handle returned by `Task.start()`. Useful members:

- `await run.result()` — block until terminal-for-this-caller; same
  `TaskResult` semantics as above.
- `async for chunk in run` — stream incremental output (see
  Streaming).
- `await run.cancel()` — signal cancellation; sets
  `ctx.cancel_requested = True` and then `ctx.cancel`. The handler
  decides the terminal shape (returns normally, suspends, or raises).
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
| `TaskCancelled` | `.run()` / `.result()` | Handler ended via the cooperative-cancel path (e.g., re-raised `asyncio.CancelledError` after observing `ctx.cancel.is_set()`) OR via `ctx.exit_for_recovery()`. |
| `TaskNotFound` | `handle.result()` / `.start()` | Referenced `task_id` has been deleted between calls. |
| `TaskConflictError` | `.run()` / `.start()` / `handle.result()` (steerer) | The **single** error type for any "task is busy / not available" state — live-elsewhere non-steerable, dead-evicted (split-brain protection), or terminal-with-queued-steerer. `.current_status` carries the observed terminal/in-progress label. |
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

### Pattern F — Steerable chat: queueing new inputs mid-flight

```python
@task(name="steerable_chat", steerable=True)
async def steerable_chat(ctx: TaskContext[dict]) -> dict:
    history = ctx.metadata.get("history", []) if ctx.entry_mode != "fresh" else []
    history.append({"role": "user", "content": ctx.input["message"]})

    if ctx.is_steered_turn and ctx.pending_input_count > 0:
        # Multiple inputs already queued behind us — fast-suspend so
        # the framework can drain to the freshest input without doing
        # work for stale ones.
        ctx.metadata["history"] = history
        return await ctx.suspend(output={"skipped_early": True})

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
            return await ctx.suspend(output={"interrupted": True})
        reply_buf.append(chunk)

    reply = "".join(reply_buf)
    history.append({"role": "assistant", "content": reply})
    ctx.metadata["history"] = history
    return await ctx.suspend(output={"reply": reply})
```

Caller side, showing the plain-multi-turn semantics:

```python
session = f"chat:{user_id}:{conversation_id}"

# Turn 1 starts a slow generation.
run1 = await steerable_chat.start(task_id=session, input={"message": "Tell me a long story."})

# 50ms later, user changes their mind.
run2 = await steerable_chat.start(task_id=session, input={"message": "Actually, what's 2 + 2?"})

# First caller's run resolves with turn 1's natural outcome.
# Strategy A handler suspends on ctx.cancel.is_set() → status="suspended"
# with the handler's `output={"interrupted": True}` delivered unconditionally.
r1 = await run1.result()
assert r1.is_suspended
assert r1.output == {"interrupted": True}

# Steering caller's run resolves with turn 2's outcome.
r2 = await run2.result()
assert r2.is_suspended          # the steerable handler ends each turn via ctx.suspend(...)
print(r2.output["reply"])       # "4"
```

What this pattern covers that Pattern C doesn't:

- **`steerable=True`** turns `.start()`-on-`in_progress` from
  `TaskConflictError` into "queue + cancel".
- **`ctx.cancel.is_set()`** is the in-handler signal to wind down
  cleanly. Suspending with a partial output is the canonical shape.
- **`ctx.is_steered_turn` + `ctx.pending_input_count`** let a handler
  short-circuit when it's already multiple turns behind.
- **Plain multi-turn semantics**: turn 1's caller sees turn 1's
  outcome; turn 2's caller sees turn 2's outcome. The handler's
  emitted `output=` is delivered unconditionally — no "supersede"
  branch.
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

Recovery is **framework-managed** — there is no developer-tunable
threshold. The framework reclaims abandoned in-progress records
automatically through three internal layers: a hardened scan at
startup, a periodic background scan, and inline reclaim on
scheduling primitives (`.run()` / `.start()` / `get_active_run()`)
when they encounter an in-progress record whose previous lifetime is
no longer live. The decision "is the previous lifetime still
running?" is derived from the persisted record alone, not from any
configuration knob.

```python
@task(name="resumable")
async def resumable(ctx: TaskContext[int]) -> int:
    if ctx.entry_mode == "fresh":
        ctx.metadata["seen"] = ctx.input
        raise SystemExit("simulate a crash")  # tear lifetime 1 down
    assert ctx.entry_mode == "recovered"
    return ctx.metadata["seen"]

# Lifetime 1: writes watermark, then dies.
with pytest.raises(SystemExit):
    await resumable.run(task_id="t-1", input=42)
# Lifetime 2: framework's inline reclaim catches the dead lease →
#             recovered entry mode.
result = await resumable.run(task_id="t-1", input=42)
assert result.output == 42
```

### What the framework persists at lifecycle boundaries

| Boundary | What is persisted |
|----------|-------------------|
| `start` | Input, initial counters, namespace snapshot. |
| `suspend` | `Suspended` envelope, namespace snapshot, queued inputs (steerable). |
| Handler returns or raises | Terminal status (`completed`), final namespace snapshot, output (or structured error). |
| Steering drain re-entry | New turn-start timestamp; namespace snapshot. |
| `ctx.exit_for_recovery()` | Namespace snapshot; status preserved as `in_progress`; lease released. |
| `flush()` (handler-initiated) | The addressed namespace only, atomically. |

The framework **auto-flushes** `ctx.metadata` at every
terminal-of-turn boundary (normal-suspend, normal-complete,
cooperative-cancel, exception, suspend-with-queued-steering,
return-with-queued-steering, raise-with-queued-steering,
shutdown-via-`exit_for_recovery`). You may still call
`ctx.metadata.flush()` explicitly as a fence before at-most-once
side effects — but you do NOT need it just to guarantee durability
across a graceful boundary.

### Operational counters

- `recovery_count` — how many times this task has been re-acquired by
  a new lifetime. Useful as a recovery-loop health signal.
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
