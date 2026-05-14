# Durable Task Developer Guide

> Developer guidance for building crash-resilient agents with `@durable_task` — the single decorator for turning async functions into units of work that survive container crashes, OOM kills, and redeployments.

---

## Table of Contents

- [Overview](#overview)
  - [Why This Exists](#why-this-exists)
  - [What You Get](#what-you-get)
- [Getting Started](#getting-started)
- [Lifecycle Automation](#lifecycle-automation)
  - [State Diagram](#state-diagram)
  - [Entry Mode Decision Table](#entry-mode-decision-table)
  - [.run() vs .start() vs .get() vs .list()](#run-vs-start-vs-get-vs-list)
- [TaskContext](#taskcontext)
  - [Properties Reference](#properties-reference)
  - [Branching on Entry Mode](#branching-on-entry-mode)
- [Suspend & Resume](#suspend--resume)
  - [Multi-Turn Conversations](#multi-turn-conversations)
- [Steering](#steering)
  - [What Steering Solves](#what-steering-solves)
  - [Generation Model](#generation-model)
  - [Enabling Steering](#enabling-steering)
  - [The Three-Phase Cancel Pattern](#the-three-phase-cancel-pattern)
  - [Steering Flow Diagram](#steering-flow-diagram)
  - [What Happens to Each Generation](#what-happens-to-each-generation)
  - [Rapid-Fire Steering](#rapid-fire-steering)
  - [Preserving Fidelity with External SDKs](#preserving-fidelity-with-external-sdks)
  - [Steering Recovery](#steering-recovery)
  - [Complete Steering Example](#complete-steering-example)
- [Streaming](#streaming)
  - [Custom Stream Handlers](#custom-stream-handlers)
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

### Why This Exists

Azure AI Foundry Hosted Agents run your code in platform-managed containers.
Those containers can be killed at any time — OOM kills, node preemptions,
rolling deployments, or unexpected crashes. Without durability, any in-flight
work is lost and the agent starts from scratch.

Agent frameworks fall into two camps:

| Category | Examples | What they need |
|----------|----------|----------------|
| **Externally stateful** — the framework owns durability | Temporal, Durable Functions, Orleans | Platform visibility: lifecycle tracking, lease-based liveness, status reporting on top of the framework's own durability |
| **Locally stateful** — the container holds state | LangGraph (SQLite checkpointer), Claude SDK tool loops, hand-written agents | A crash-safe entry point: lease-based liveness so the platform knows when to restart, plus run / resume / progress / suspend primitives the developer would otherwise hand-roll |

`@durable_task` serves both camps. It is **not** a replacement for Temporal or
Durable Functions — it is the thin durable wrapper around the boundary between
the platform and your code. It does not make your function deterministic or
replayable. It turns `run(input) → output` into a unit of work that survives
a container crash, a deployment, or an idle-deactivation — with hooks for
progress, suspension, cancellation, and steering that compose with whatever
framework you use underneath.

### What You Get

Decorate your async function, and the framework guarantees it runs to completion
— even if the container restarts mid-execution. On recovery, your function is
re-invoked with the same input and last-saved metadata, so it can pick up where
it left off.

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
- Steering — submit a new input to a running task without cancel/wait/restart

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
`.start()`, `.get()`, and `.list()` methods. The function itself takes a single `TaskContext`
parameter.

If the container crashes mid-execution, the framework automatically recovers the
task on restart — before any HTTP handlers go live. Your function is re-invoked
with `ctx.entry_mode = "recovered"` and the same input. No caller action is needed.

If a caller calls `.run()` with a `task_id` that is already in progress,
the framework raises `TaskConflictError` — it does not create a duplicate.

---

## Lifecycle Automation

Every call to `.run()` or `.start()` follows the same state machine. You never
manually check task state or call resume — the framework does it for you.

### State Diagram

What the framework does when you call `.run()` or `.start()`:

```
                        .run() / .start()
                              │
                              ▼
                    ┌───── task exists? ─────┐
                    │                        │
                   No                       Yes
                    │                        │
                    ▼                        ▼
              ┌──────────┐         ┌──── status? ──────────────────────────┐
              │  Create  │         │            │            │             │
              │  & Start │      pending    suspended    in_progress    completed
              └──────────┘         │            │            │             │
                    │              ▼            ▼            ▼             ▼
                  fresh         fresh       resumed      stale?      ephemeral?
                                                           │             │
                                                     ┌─────┴─────┐  ┌───┴───┐
                                                    Yes          No Yes      No
                                                     │            │   │       │
                                                     ▼            ▼   ▼       ▼
                                                 recovered   steerable? fresh¹ TaskConflict
                                                                  │            Error
                                                            ┌─────┴─────┐
                                                           Yes          No
                                                            │            │
                                                            ▼            ▼
                                                     Queue input   TaskConflict
                                                     + cancel →      Error
                                                     drain resumes
                                                     ("resumed",
                                                      was_steered)
```

¹ Ephemeral completed tasks were auto-deleted on completion, so they appear as
"no task exists" and a fresh task is created transparently.

### Entry Mode Decision Table

| Current State | Action | `ctx.entry_mode` | `ctx.was_steered` |
|---|---|---|---|
| No task exists | Create and start | `"fresh"` | `False` |
| `pending` | Start | `"fresh"` | `False` |
| `suspended` | Resume with new input | `"resumed"` | `False` |
| `in_progress` (stale) | Recover | `"recovered"` | `True` if steering state exists ¹ |
| `in_progress` (not stale, **steerable**) | Queue input, signal cancel → drain resumes | `"resumed"` | `True` |
| `in_progress` (not stale, not steerable) | **Raises `TaskConflictError`** | — | — |
| `completed` (ephemeral) | Task was auto-deleted → create fresh | `"fresh"` | `False` |
| `completed` (non-ephemeral) | **Raises `TaskConflictError`** | — | — |

¹ When recovering a steerable task that crashed mid-drain, the initial recovery
enters with `"recovered"` and `was_steered=True`. The framework then drains
the pending queue, re-entering the function with `entry_mode="resumed"` and
`was_steered=True` for each queued input. See [Steering Recovery](#steering-recovery).

A task is considered **stale** when its last update is older than `stale_timeout`
(default: 300 seconds). This means the previous execution likely crashed.

### .run() vs .start() vs .get() vs .list()

| Method | Blocks? | Returns | Use When |
|--------|---------|---------|----------|
| `.run()` | Yes — awaits completion | `TaskResult[Output]` | You want the result inline |
| `.start()` | No — returns immediately | `TaskRun[Output]` | You want a handle for polling/streaming |
| `.get()` | No — reads from store | `TaskInfo \| None` | You want to query task state without executing |
| `.list()` | No — reads from store | `list[TaskInfo]` | You want all tasks for this function |

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

`.list()` returns all tasks created by this decorated function. It is automatically
scoped — each function only sees its own tasks:

```python
# List all suspended tasks for this function
suspended = await greet.list(status="suspended")
for t in suspended:
    print(t.id, t.status, t.created_at)

# List all tasks (any status)
all_tasks = await greet.list()
```

> `.list()` is automatically scoped — each decorated function only sees tasks it
> created. The `name` option on `@durable_task` is the key that determines which
> tasks belong to this function.

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
| `ctx.agent_name` | `str` | Agent name from platform configuration |
| `ctx.lease_generation` | `int` | Lease generation counter (increments on recovery) |
| `ctx.cancel` | `asyncio.Event` | Set when cancellation is requested (including steering cancel) |
| `ctx.shutdown` | `asyncio.Event` | Set when the container is shutting down |
| `ctx.run_attempt` | `int` | Framework retry attempt counter (0-indexed) |
| `ctx.title` | `str` | Human-readable task title |
| `ctx.tags` | `dict[str, str]` | Merged decorator + call-site tags |
| `ctx.description` | `str \| None` | Task description (from decorator or call-site) |
| `ctx.generation` | `int` | Steering generation counter (0 for first run, increments on each steer) |
| `ctx.previous_input` | `Input \| None` | The superseded generation's input (set when steering state is present) |
| `ctx.pending_inputs` | `Sequence[Any]` | Read-only snapshot of queued steering inputs at function entry |
| `ctx.was_steered` | `bool` | `True` when this entry involves steering — the function is being re-entered with a new input from the steering queue. Always check this to detect steering; `entry_mode` will be `"resumed"` for normal steering drains or `"recovered"` for crash recovery of a mid-drain |

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
        # For steerable tasks, check ctx.was_steered for steering context
        if ctx.was_steered:
            # This resume was triggered by steering — ctx.previous_input
            # has the superseded generation's input
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

Each call to `.run(task_id=session_id, input={"message": "..."})` or
`.start(task_id=session_id, input={"message": "..."})` resumes the
same task with the new message. The framework handles the transition
from `suspended` to `in_progress` automatically.

---

## Steering

Steering extends the suspend/resume pattern for scenarios where a user sends
a new message while the agent is still processing the previous one. Without
steering, a `.start()` on an `in_progress` task raises `TaskConflictError` —
the caller must cancel, wait for the function to exit, and then start again.
With steering, the framework handles this automatically.

### What Steering Solves

Consider a chat UI. The user sends "Tell me about Python", then immediately
types "Actually, tell me about Rust" before the first reply finishes. Without
steering:

1. The caller sees `TaskConflictError` on the second `.start()`
2. The caller must call `run.cancel()` and wait for the function to exit
3. Then call `.start()` again with the new input
4. Race conditions abound — what if another message arrives during step 2?

With steering, the caller just calls `.start()` again. The framework queues
the new input, signals the running function to cancel, and re-enters the
function with the new input once the current generation exits. No manual
cancel/wait/restart dance.

### Generation Model

Each time the framework enters the durable function, it increments a
**generation** counter. This gives each invocation a stable identity:

```
Generation 0: fresh start with input A            → entry_mode="fresh",   was_steered=False
Generation 1: steered — input B replaced input A   → entry_mode="resumed", was_steered=True
Generation 2: steered — input C (short-circuited)  → entry_mode="resumed", was_steered=True
Generation 3: normal resume — user sends input D   → entry_mode="resumed", was_steered=False
```

Generations are persisted in the task payload. Each `TaskRun` returned to a
caller is bound to a specific generation, so there is no ambiguity about which
invocation a caller is observing.

### Enabling Steering

Add `steerable=True` to the decorator:

```python
@durable_task(name="chat_session", steerable=True)
async def chat_session(ctx: TaskContext[dict]) -> dict:
    ...
```

| Decorator Option | Type | Default | Description |
|------------------|------|---------|-------------|
| `steerable` | `bool` | `False` | Enable steering support |
| `max_pending` | `int` | `10` | Maximum queued inputs. Excess raises `SteeringQueueFull` |

When `steerable=False` (default), behavior is unchanged — `.start()` on an
`in_progress` task raises `TaskConflictError`.

### The Three-Phase Cancel Pattern

When a steering input arrives, the framework sets `ctx.cancel` on the running
function. But cancel can arrive at three different points. Your function must
handle all three:

```python
@durable_task(name="agent_session", steerable=True)
async def agent_session(ctx: TaskContext[dict]) -> dict:
    message = ctx.input["message"]
    invocation_id = ctx.input["invocation_id"]

    invocation_store.save(invocation_id, {"status": "running"})

    # ── Phase 1: Pre-entry cancel ───────────────────────────────
    # Cancel was already set before the function body runs.
    # This happens in rapid-fire scenarios where multiple inputs
    # queue up faster than the function can start.
    if ctx.cancel.is_set():
        invocation_store.save(invocation_id, {
            "status": "cancelled", "reason": "steered",
        })
        return await ctx.suspend(reason="steered")

    # ── Phase 2: Mid-stream cancel ──────────────────────────────
    # Check cancel between each chunk of work. This is where most
    # steering cancels land in practice.
    reply = ""
    async for token in call_llm_streaming(message):
        reply += token
        if ctx.cancel.is_set():
            break  # Stop producing — save what we have

    # ── Phase 3: Post-completion cancel ─────────────────────────
    # Cancel arrived after the LLM finished but before we returned.
    # The reply is complete, but it will be superseded by the next
    # generation. Save the result so it is not lost.
    was_steered = ctx.cancel.is_set()

    result = {"reply": reply, "partial": was_steered}
    if was_steered:
        invocation_store.save(invocation_id, {
            "status": "superseded", "output": result,
        })
        return await ctx.suspend(reason="steered")

    invocation_store.save(invocation_id, {
        "status": "completed", "output": result,
    })
    return await ctx.suspend(reason="awaiting_user_input", output=result)
```

**Key rule**: Always save your work before returning, even when cancelled.
The user's message was received and should be preserved (appended to
conversation history, written to your store, etc.). Only the *reply generation*
is interrupted — not the input recording.

> **⚠️ Steerable tasks MUST suspend when steered — never return normally or
> raise.** When `ctx.cancel.is_set()` due to steering, always exit with
> `return await ctx.suspend(reason="steered")`. This keeps the task alive so
> the framework can drain the pending queue and resume with the next input.
>
> - **Normal return** → task completes → next `.start()` creates a fresh task
>   → conversation continuity broken
> - **Raise exception** → task enters failure/retry path → wrong lifecycle
> - **Suspend** ✅ → task stays alive → framework resumes with next queued input

### Steering Flow Diagram

```
    Caller A: .start(input=A)              Caller B: .start(input=B)
         │                                       │
         ▼                                       │
    ┌──────────────┐                             │
    │ Gen 0: fresh │ ◄── function starts         │
    │  processing  │                             │
    │    ...       │ ◄── ctx.cancel.set() ◄──────┤ input B queued
    │  (checks     │                             │
    │   cancel)    │                             │
    │  break       │                             │
    └──────┬───────┘                             │
           │ returns via suspend(reason="steered")
           ▼                                     │
    ┌──────────────────┐                         │
    │ Framework drains │                         │
    │  pending queue   │                         │
    │ (pops input B)   │                         │
    └──────┬───────────┘                         │
           │                                     │
           ▼                                     │
    ┌──────────────┐                             │
    │ Gen 1:resumed│ ◄── function re-entered     │
    │ was_steered  │     ctx.previous_input = A  │
    │ ctx.input = B│                             │
    │  processing  │                             │
    │    ...       │                             │
    │  (completes) │                             │
    └──────┬───────┘                             │
           │ returns via suspend()               │
           ▼                                     │
    Caller B's TaskRun                     Caller A's TaskRun
    resolves with result                   resolved earlier with
                                           "superseded" status
```

### What Happens to Each Generation

| Scenario | Status Written to Store | `TaskRun` Resolution |
|----------|------------------------|----------------------|
| Pre-entry cancel (Phase 1) | `"cancelled"` — input preserved, no reply attempted | Superseded |
| Mid-stream cancel (Phase 2) | `"superseded"` — partial reply saved | Superseded |
| Post-completion cancel (Phase 3) | `"superseded"` — full reply saved | Superseded |
| Normal completion | `"completed"` — full reply | Completed |

Superseded `TaskRun` handles resolve when the framework drains the queue and
starts the next generation. Callers polling these handles see the result of
their specific generation.

### Rapid-Fire Steering

When multiple inputs arrive in quick succession:

```
User types: "What is Python?"  →  "Actually, Rust"  →  "No wait, Go"
```

The framework queues all of them. Only the last one (Go) runs to completion:

```
Gen 0: "What is Python?"   → cancel pre-set → Phase 1 short-circuit
Gen 1: "Actually, Rust"    → cancel pre-set → Phase 1 short-circuit
Gen 2: "No wait, Go"       → queue empty → full execution
```

**Important**: Each short-circuited generation still enters the function.
This is by design — it gives the developer a chance to:

- Record the user's message in conversation history
- Write a `"cancelled"` status to the invocation store
- Perform any other bookkeeping

The framework does NOT silently discard queued inputs. Every input gets a
function invocation, even if that invocation immediately short-circuits.

### Preserving Fidelity with External SDKs

When wrapping external LLM SDKs (Claude, Copilot, LangGraph), steering adds
a layer on top of the SDK's own interruption model. Be aware of how each SDK
handles cancellation:

**Streaming SDKs (Claude, OpenAI)**: These use `async for token in stream`.
Breaking out of the loop is clean — the SDK handles connection cleanup. Check
`ctx.cancel.is_set()` between chunks:

```python
async with client.messages.stream(...) as stream:
    async for text in stream.text_stream:
        reply += text
        if ctx.cancel.is_set():
            break  # SDK cleans up the stream
```

**Event-based SDKs (Copilot)**: These deliver results via callbacks. Use
`session.abort()` to stop event delivery, then let the handler drain:

```python
session.on(handler)       # Register callback
session.send(message)     # Start generation (non-blocking)
# Wait for either completion or cancel:
done, _ = await asyncio.wait(
    [completion_event.wait(), cancel_wait()],
    return_when=asyncio.FIRST_COMPLETED,
)
if ctx.cancel.is_set():
    session.abort()       # Stop further events
```

**Graph SDKs (LangGraph)**: These run a graph to completion. Use checkpoint
IDs to fork from a known state rather than replaying the full graph:

```python
if ctx.was_steered and ctx.previous_input:
    # Fork from the checkpoint before the superseded run
    checkpoint_id = ctx.metadata.get("stable_checkpoint_id")
    config = {"configurable": {"thread_id": ..., "checkpoint_id": checkpoint_id}}
```

### Steering Recovery

If the container crashes while a steered task is processing:

1. The task is `in_progress` with steering state in the payload
2. On container restart, the framework detects the stale task
3. If there are pending inputs in the queue, the framework recovers with
   `entry_mode="recovered"` and `was_steered=True`, then drains the queue
4. If a drain was in progress when the crash occurred, the framework
   resumes the drain from the persisted `active_input`
5. Each drained input re-enters the function with `entry_mode="resumed"`
   and `was_steered=True`

No data is lost — the pending queue and generation counter are persisted in
the task payload.

> **How to detect steering**: Always use `ctx.was_steered` — never check
> `entry_mode` for steering. Steering re-entries arrive as `"resumed"`
> (because the task suspended and is being resumed with a new input). The
> `was_steered` flag tells you whether steering context (`previous_input`,
> `generation`, `pending_inputs`) is meaningful.

### Complete Steering Example

A full steerable chat session combining all patterns:

```python
from azure.ai.agentserver.core.durable import TaskContext, durable_task
from my_app.store import FileStore

invocation_store = FileStore("./invocations")
conversation_store = FileStore("./conversations")


@durable_task(name="chat_session", steerable=True)
async def chat_session(ctx: TaskContext[dict]) -> dict:
    session_id = ctx.input["session_id"]
    message = ctx.input["message"]
    invocation_id = ctx.input["invocation_id"]

    # Mark invocation as running (inside the durable boundary)
    invocation_store.save(invocation_id, {"status": "running"})

    # Load conversation history from external store (not task metadata)
    history = conversation_store.load(session_id) or []
    history.append({"role": "user", "content": message})

    # ── Phase 1: Pre-entry cancel ───────────────────────────────
    if ctx.cancel.is_set():
        conversation_store.save(session_id, history)
        invocation_store.save(invocation_id, {
            "status": "cancelled",
            "reason": "steered",
            "message_preserved": True,
        })
        return await ctx.suspend(reason="steered")

    # ── Phase 2: Stream response, checking cancel ───────────────
    reply = ""
    was_aborted = False
    async for token in call_llm_streaming(message, history):
        reply += token
        if ctx.cancel.is_set():
            was_aborted = True
            break

    # ── Phase 3: Save result ────────────────────────────────────
    if reply:
        history.append({"role": "assistant", "content": reply})
    conversation_store.save(session_id, history)

    output = {"reply": reply, "partial": was_aborted}

    if was_aborted or ctx.cancel.is_set():
        invocation_store.save(invocation_id, {
            "status": "superseded", "output": output,
        })
        return await ctx.suspend(reason="steered")

    # Normal completion — suspend awaiting next user message
    invocation_store.save(invocation_id, {
        "status": "completed", "output": output,
    })
    return await ctx.suspend(reason="awaiting_user_input", output=output)
```

The HTTP layer remains unchanged — callers call `POST /invoke` and poll
`GET /invocations/{id}`. The steering happens transparently inside the
durable task boundary.

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

`ctx.stream()` accepts any Python object — the framework simply passes it
through the stream handler with no serialization or transformation.

> **Important**: The default `QueueStreamHandler` holds items in an in-memory
> `asyncio.Queue`. They are **not persisted** and are **lost on crash**. If the
> process restarts mid-stream, the recovered task starts from scratch. If you
> need durable incremental output, implement a custom `StreamHandler` or write
> to your own store inside the task function alongside `ctx.stream()`.

### Custom Stream Handlers

The streaming path is pluggable via the `StreamHandler` protocol. Implement
`put()`, `get()`, and `close()` to control how stream items are buffered,
transported, or persisted:

```python
from azure.ai.agentserver.core.durable import StreamHandler

class RedisStreamHandler:
    """Example: fan-out streams via Redis."""

    def __init__(self, redis_client, channel: str):
        self._redis = redis_client
        self._channel = channel

    async def put(self, item):
        await self._redis.publish(self._channel, serialize(item))

    async def get(self):
        msg = await self._redis.subscribe_next(self._channel)
        if msg is None:
            raise StopAsyncIteration
        return deserialize(msg)

    async def close(self):
        await self._redis.publish(self._channel, "__CLOSED__")
```

Pass the handler at the call site — no decorator changes needed:

```python
handler = RedisStreamHandler(redis, channel="report-1")
task_run = await generate_report.start(
    task_id="report-1",
    input="Q3 Results",
    stream_handler=handler,
)
async for chunk in task_run:
    print(chunk, end="")
```

**Key rules:**

- `get()` must raise `StopAsyncIteration` after `close()` is called and all
  buffered items are drained. This is Python's native iterator exhaustion signal.
- `close()` is always called by the framework when the task finishes — whether
  it succeeds, fails, or is cancelled.
- If no `stream_handler` is provided, the framework uses `QueueStreamHandler`
  (in-memory `asyncio.Queue`) as the default.
- The handler instance survives steering restarts — items streamed before and
  after a steering cycle flow through the same handler.

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
| Streaming items | **Nobody** (default) | In-memory; pluggable via `StreamHandler` |

The task store powers lifecycle and recovery. **It is NOT your application
database.** You read from it via `.get()` to inspect task state, but you should
not depend on it as the persistence layer for your API responses.

### The Durable Boundary Rule

> **Everything that must survive a crash must happen inside the durable task function.**

The durable task function is the crash-recovery boundary. If the process dies,
the framework automatically re-invokes your function on container restart.
Additionally, a subsequent `.run()` / `.start()` call with the same `task_id`
will detect the stale task and recover it. Any work done *outside* the function
(e.g., in an HTTP handler, in an `asyncio.create_task` callback) is lost.

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
| `name` | `str` | Function `__qualname__` | **Stable task identity anchor.** Used for crash recovery routing and source stamping. If you ever rename your function, existing in-flight tasks are still recovered correctly because the framework matches on this name, not the Python function name. **Always provide an explicit name for production tasks.** |
| `retry` | `RetryPolicy \| None` | `None` | Retry policy on failure. See [RetryPolicy](#retrypolicy). |
| `ephemeral` | `bool` | `True` | Auto-delete task record on completion. |
| `tags` | `dict[str, str] \| Callable[[Any, str], dict[str, str]] \| None` | `{}` | Default tags (static or callable factory receiving `(input, task_id)`). |
| `title` | `str \| Callable[[Any, str], str] \| None` | `None` | Human-readable title or title factory. Defaults to `"{name}:{task_id[:8]}"` when not provided. |
| `description` | `str \| Callable[[Any, str], str \| None] \| None` | `None` | Task description (static or callable factory receiving `(input, task_id)`). |
| `store_input` | `bool` | `True` | Whether to persist input on the task record. |
| `timeout` | `timedelta \| None` | `None` | Execution timeout. When elapsed, `ctx.cancel` is set cooperatively. If the function does not exit, the lease eventually expires and the task is recovered. |
| `steerable` | `bool` | `False` | Enable steering. When True, `.start()` on an `in_progress` task queues the input instead of raising `TaskConflictError`. See [Steering](#steering). |
| `max_pending` | `int` | `10` | Maximum queued steering inputs. Excess raises `SteeringQueueFull`. |

> **Source provenance** is auto-stamped by the framework on every task. It records
> which function created the task and the SDK version. Source is not user-overridable;
> use `tags` for custom metadata.
>
> **Reserved tags**: The framework stamps internal tags (prefixed with `_durable_task_`)
> on every task for scoping and recovery. Any tags you provide with this prefix are
> silently stripped. Use unprefixed tag keys for your own metadata.

```python
@durable_task(
    name="analyze_document",
    ephemeral=False,        # Keep task record after completion
    tags={"team": "platform", "model": "gpt-4o"},
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
# Override tags for this specific call
result = await analyze_document.options(
    tags={"model": "gpt-4o-mini"},
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
| `TaskConflictError` | `.run()`, `.start()` | Task is `in_progress` (non-stale, non-steerable) or `completed` (non-ephemeral) |
| `TaskFailed` | `.run()`, `task_run.result()` | Unhandled exception in the task function |
| `TaskCancelled` | `.run()`, `task_run.result()` | Task was cancelled via `task_run.cancel()` |
| `TaskTerminated` | `.run()`, `task_run.result()` | Task was forcefully terminated (timeout or `task_run.terminate()`) |
| `TaskNotFound` | `task_run.refresh()`, `task_run.delete()` | Task record does not exist in the store |
| `SteeringQueueFull` | `.start()` | Steering queue has `max_pending` items. Caller should retry or back off |

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

Cooperative cancel sets `ctx.cancel`. If the function checks this event and
**returns normally**, the task completes as a success — not as cancelled. The
function decides its own outcome. `TaskCancelled` is only raised when the
function does not handle the cancel and the asyncio task is cancelled.

### Execution Timeout

Set a `timeout` to automatically cancel tasks that run too long. When the
timeout elapses, `ctx.cancel` is set cooperatively — the same signal used
by `handle.cancel()` and steering. If the function does not exit, the lease
eventually expires and the task is recovered on the next heartbeat.

```python
from datetime import timedelta

@durable_task(
    timeout=timedelta(minutes=5),
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

| Method | `ctx.cancel` set? | Hard cancel? | Outcome | Recoverable? |
|--------|-------------------|--------------|---------|--------------|
| `run.cancel()` | ✅ | ❌ | Success if function returns normally; `TaskCancelled` if unhandled | Yes (stays in_progress until function exits) |
| `run.terminate()` | ✅ | ✅ | `TaskTerminated` | No (goes to failed) |
| Timeout expired | ✅ then ✅ | After grace | `TaskTerminated` | No (goes to failed) |

---

## Best Practices

1. **Keep tasks idempotent for recovery.** When `entry_mode="recovered"`, the
   function re-runs from the top. Use `ctx.metadata` to track completed steps
   and skip them on re-entry.

2. **Branch on `entry_mode`.** Always handle at least `"fresh"` and `"recovered"`.
   For suspend/resume tasks, handle `"resumed"` as well. For steerable tasks,
   check `ctx.was_steered` inside the `"resumed"` branch.

3. **Persist results inside the durable boundary.** Any write that must survive
   a crash belongs inside the task function, not in the HTTP handler or a
   background `asyncio.create_task`.

4. **Use `ephemeral=True` for one-shot tasks.** If the task doesn't need to be
   queried after completion, let the framework auto-delete it. This keeps the
   task store clean.

5. **Keep task functions focused.** A task should do one logical unit of work.
   Compose multiple tasks rather than building monolithic functions.

6. **Check cancellation cooperatively.** Poll `ctx.cancel.is_set()` in long loops
   and exit cleanly when set. For steerable tasks, this is what enables the
   framework to drain the queue and start the next generation.

7. **Use `ctx.metadata` for progress, not for large data.** Metadata is flushed
   periodically to the task store. Keep values small and JSON-serializable.
   The task payload has a 1 MB cap — write conversation history, results, and
   growing data to your own store (database, blob, Redis).

8. **Always preserve user input on cancel.** When `ctx.cancel.is_set()` in a
   steerable task, save the user's message to your conversation store before
   returning. The *reply* is interrupted, not the *input recording*.

9. **Use the three-phase cancel pattern.** Check `ctx.cancel` at three points:
   before the LLM call (Phase 1), between chunks (Phase 2), and after
   completion (Phase 3). This covers all timing scenarios.

10. **Store conversation history externally.** Don't put growing data in
    `ctx.metadata`. Use an external store keyed by `session_id`. The task
    metadata is for lightweight progress signals only.

11. **Steerable tasks MUST suspend on cancel, not return normally or raise.**
    When `ctx.cancel.is_set()` due to steering, always `return await
    ctx.suspend(reason="steered")`. This keeps the task alive in `suspended`
    state so the framework can drain the pending queue and resume with the
    next input. If you return a normal value, the task completes — the next
    `.start()` creates a fresh task, breaking conversation continuity. If you
    raise an exception, the task enters the failure/retry path, which is also
    wrong. Suspend is the only correct exit for a steered cancel.

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
# ❌ BAD — default QueueStreamHandler is in-memory only
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

# ✅ ALSO GOOD — use a custom StreamHandler that persists
handler = DurableStreamHandler(store, ctx.task_id)
run = await stream_report.start(
    task_id="r1", input="...", stream_handler=handler,
)
```

### ❌ Storing conversation history in task metadata

```python
# ❌ BAD — metadata has a 1 MB cap and is not designed for growing data
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    history = ctx.metadata.get("history", [])
    history.append({"role": "user", "content": ctx.input["message"]})
    reply = await call_llm(history)
    history.append({"role": "assistant", "content": reply})
    ctx.metadata["history"] = history  # GROWS UNBOUNDED

# ✅ GOOD — use an external store, reference by session_id
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    session_id = ctx.input["session_id"]
    history = conversation_store.load(session_id) or []
    history.append({"role": "user", "content": ctx.input["message"]})
    reply = await call_llm(history)
    history.append({"role": "assistant", "content": reply})
    conversation_store.save(session_id, history)  # EXTERNAL STORE
```

### ❌ Discarding input on steering cancel

```python
# ❌ BAD — user's message is lost when cancel fires
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    if ctx.cancel.is_set():
        return await ctx.suspend(reason="steered")  # Message never saved!

# ✅ GOOD — always save the user's message before returning
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    history = load_history(ctx.input["session_id"])
    history.append({"role": "user", "content": ctx.input["message"]})
    if ctx.cancel.is_set():
        save_history(ctx.input["session_id"], history)  # PRESERVE INPUT
        return await ctx.suspend(reason="steered")
```

### ❌ Skipping Phase 1 cancel check

```python
# ❌ BAD — starts an expensive LLM call even when cancel is already set
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    # Missing Phase 1 check!
    reply = ""
    async for token in call_llm_streaming(ctx.input["message"]):
        reply += token
        if ctx.cancel.is_set():
            break
    ...

# ✅ GOOD — short-circuit before the LLM call
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    if ctx.cancel.is_set():          # Phase 1: pre-entry
        save_input_and_return(ctx)
        return await ctx.suspend(reason="steered")
    reply = ""
    async for token in call_llm_streaming(ctx.input["message"]):
        reply += token
        if ctx.cancel.is_set():      # Phase 2: mid-stream
            break
    ...
```

### ❌ Using `steerable=True` without `suspend()`

Steerable tasks **must** suspend on every exit — both on normal completion
(awaiting next user input) and on steering cancel. If the function returns
normally, the task completes and the framework has nowhere to drain the
pending queue. If it raises, the task enters the failure/retry path.

```python
# ❌ BAD — task completes, can't accept next turn or drain queue
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    reply = await call_llm(ctx.input["message"])
    return {"reply": reply}  # Task completes → next .start() creates fresh task

# ❌ BAD — raising on cancel enters the failure path
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    if ctx.cancel.is_set():
        raise RuntimeError("Cancelled")  # Wrong! Enters retry/failure path

# ✅ GOOD — always suspend: on cancel AND on normal completion
@durable_task(name="chat", steerable=True)
async def chat(ctx: TaskContext[dict]) -> dict:
    if ctx.cancel.is_set():
        return await ctx.suspend(reason="steered")  # Keep alive for drain
    reply = await call_llm(ctx.input["message"])
    return await ctx.suspend(reason="awaiting_user_input", output={"reply": reply})
```
