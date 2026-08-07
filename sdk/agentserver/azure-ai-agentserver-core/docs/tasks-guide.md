# Resilient Tasks — Developer Guide

This is the developer guide for `azure.ai.agentserver.core.tasks` —
the resilient-task primitive that turns an `async def` function into a
crash-resilient unit of agent work.

If your agent needs to survive container crashes, OOM kills, or
redeployments without losing its place, you want this. If your turn
of work could plausibly outlive the request that started it (long
LLM calls, multi-step tool chains, multi-message conversations), you
want this.

---

## 1. Why

There is **one primitive in two flavours**:

- **`@task`** — *one-shot*. A single resilient run of a function.
  Returns its `Output`, then the record is gone. Use for "do this
  one thing resiliently".

- **`@multi_turn_task`** — *chain*. A series of turns sharing a
  conversation identity (a `task_id`). Each `return X` is one turn;
  the chain stays alive in between turns and can accept more inputs.
  Use for chat sessions, agents that work across multiple user
  messages, resilient orchestrations.

Both run the same way under the hood: lease-based crash recovery, a
single typed input per turn, a `TaskContext` handle, optional retry,
optional steering (for `multi_turn_task`).

What this primitive solves:

- **Crash survival.** If the process dies mid-call, the next
  process picks up the same task with the same input and runs the
  handler again (or, for a chain in `suspended`, the next caller
  resumes the chain).
- **Identity.** A `task_id` is the resilient name of the work. Two
  callers naming the same `task_id` don't double-execute — they
  attach to the same run.
- **Typed inputs and outputs.** Generic in `Input` and `Output`;
  the framework persists the input and surfaces the output through
  a typed handle.
- **Cooperative cancellation.** The caller can ask the handler to
  stop; the handler decides how to wind down.
- **Lightweight, small surface.** A few decorators, a few classes,
  a handful of exceptions.

What this primitive deliberately does **not** do:

- Deterministic replay. The handler is re-invoked from the top on
  recovery; effects are your responsibility. Persist watermarks in an
  application-owned `FoundryStateStore` for at-most-once patterns (see §6).
- Workflow orchestration (fan-out / fan-in / child workflows). If
  you want Temporal-style orchestration, use Temporal; you can
  still wrap resilient tasks inside it.
- An application data store. Use `FoundryStateStore` for durable JSON
  state and a blob store for large values.
- A queue. One `task_id` is one logical job — not a competing-consumer
  pull queue.

---

## 2. Mental model

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your code                               │
│                                                                 │
│  @task                              @multi_turn_task            │
│  async def summarize(ctx):          async def chat(ctx):        │
│      return work(ctx.input)             return reply(ctx.input) │
│                                                                 │
│  await summarize.run(input=X)       await chat.run(             │
│                                         task_id="c1", input=X)  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │   (your async caller)
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Resilient task framework                     │
│                                                                 │
│   - persists input + metadata + lease                           │
│   - invokes your handler with TaskContext                       │
│   - watches for crashes, reclaims abandoned leases              │
│   - delivers output via TaskRun.result() / await run            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           Task store (hosted or local file-backed)              │
│                                                                 │
│   PATCH-with-ETag store of task records:                        │
│     id, status, lease_owner, payload, attachments, etag         │
└─────────────────────────────────────────────────────────────────┘
```

### One-shot vs multi-turn — at a glance

|                          | `@task` (one-shot) | `@multi_turn_task` (chain) |
|--------------------------|--------------------|-----------------------------|
| Lifetime                 | One run            | Multiple turns, chain stays alive between turns |
| `task_id` on `.start`    | Optional (auto-gen GUID) | Mandatory |
| `input_id`               | Defaults to `task_id` (1:1) | Per turn (auto-gen GUID per turn) |
| Terminal status          | `completed` / `failed` / `cancelled` → record deleted | `suspended` between turns; deleted only via `.delete(task_id)` |
| `.delete(task_id)`       | Not available (auto-cleans on terminal) | Available — chain-level delete |
| Handler `return X`       | Finishes the run; `await run.result()` resolves to `X` | Finishes the **turn**; chain goes to `suspended`; caller receives `X` |
| Steering queue           | n/a                | `steerable=True` opt-in    |
| Concurrent `.start` on same `task_id` while in-flight | `TaskConflictError` | If `steerable=True`: queued; else `TaskConflictError` |

---

## 3. Hello world

### Enabling resilient tasks

The resilient `TaskManager`'s **startup recovery scan** — a network round-trip
to the hosted task store that reclaims tasks left in-flight by a crashed prior
instance — runs at startup when **either** of the following holds:

1. at least one durable task has been declared (`@task` / `@multi_turn_task`) —
   an app that uses tasks gets recovery automatically, **or**
2. it was explicitly force-enabled via `set_resilient_tasks_enabled(True)`.

The force-enable is useful when tasks are registered *lazily* (declared after
startup): it starts the periodic recovery loop up front so a task declared
later is still recovered.

```python
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled

set_resilient_tasks_enabled(True)  # force-enable recovery before any task
```

Use `resilient_tasks_enabled()` to read the current switch state.

The `TaskManager` itself is always constructed (a cheap, in-memory object that
makes no task-store calls until a task is used), so `get_task_manager()` and
`.run()` / `.start()` work regardless of the switch. A server that neither
declares a task nor sets the switch (e.g. an invocations-only host) simply
skips the startup recovery scan and pays none of its latency.

### One-shot

```python
import asyncio
from azure.ai.agentserver.core.tasks import task, TaskContext, set_resilient_tasks_enabled

# Optional: force-enable recovery even before the first task is declared.
# Declaring the @task below already enables recovery on its own.
set_resilient_tasks_enabled(True)

@task(name="summarize")
async def summarize(ctx: TaskContext[str]) -> str:
    # ctx.input is typed as str; the framework persisted it before invoking us.
    return ctx.input.upper()

async def main():
    # Lifecycle-aware: creates fresh, attaches to in-flight, recovers a
    # crashed prior lifetime — all automatic. task_id is optional.
    output: str = await summarize.run(input="hello")
    print(output)  # 'HELLO'

asyncio.run(main())
```

### Multi-turn chain

```python
import asyncio
from azure.ai.agentserver.core.tasks import multi_turn_task, TaskContext, set_resilient_tasks_enabled

# Optional: force-enable recovery even before the first task is declared.
# Declaring the @multi_turn_task below already enables recovery on its own.
set_resilient_tasks_enabled(True)

@multi_turn_task(name="chat")
async def chat(ctx: TaskContext[dict]) -> dict:
    return {"reply": f"Echo: {ctx.input['msg']}",
            "input_id": ctx.input_id}

async def main():
    # Turn 1 — fresh chain.
    r1 = await chat.run(task_id="conv-7", input={"msg": "hi"})
    print(r1)  # {"reply": "Echo: hi", "input_id": "<turn-1-guid>"}

    # Turn 2 — same task_id resumes the persisted chain; same handler
    # is invoked with the new ctx.input.
    r2 = await chat.run(task_id="conv-7", input={"msg": "what's up?"})
    print(r2)  # {"reply": "Echo: what's up?", "input_id": "<turn-2-guid>"}

asyncio.run(main())
```

---

## 4. Concepts

### 4.1 Identifiers

- **`task_id`** — the resilient name of the work.
  - One-shot: optional; the framework generates a GUID when omitted.
    Two callers passing the same `task_id` for a one-shot **converge**
    (the second caller either attaches to the first's in-flight run
    or sees `TaskConflictError` if it has already terminated).
  - Multi-turn: mandatory; identifies the chain.

- **`input_id`** — the resilient name of one input within the chain.
  - One-shot: defaults to `task_id` (one run, one input — the 1:1
    invariant).
  - Multi-turn: per turn; the framework generates a GUID per turn
    unless the caller supplies one (callers managing their own per-
    message ids — e.g. chat clients — pass them through).

- **`if_last_input_id="<prev>"`** — an optional precondition on
  `.start` / `.run`. The framework verifies that the chain's
  currently-stored last-accepted `input_id` equals `<prev>` before
  accepting the new input. If a concurrent caller advanced the
  chain first, the call raises `LastInputIdPreconditionFailed`.
  Use this when your caller is reasoning about message ordering
  (HTTP `If-Match`-style optimistic concurrency on the input
  queue).

### 4.2 Entry mode

The handler can branch on `ctx.entry_mode`:

| Value         | Means                                                      |
|---------------|------------------------------------------------------------|
| `"fresh"`     | First invocation for this `(task_id, input_id)`            |
| `"resumed"`   | This is a subsequent turn of an existing chain (multi-turn)|
| `"recovered"` | A previous lifetime ran this same `(task_id, input_id)` and didn't finish (lease was abandoned); the framework is re-invoking with the persisted input |

```python
@multi_turn_task(name="checkpointer")
async def step(ctx: TaskContext[dict]) -> dict:
    if ctx.entry_mode == "recovered":
        # Load your application checkpoint from Foundry State Store.
        last_done = await load_last_done_step(ctx.task_id)
    ...
```

### 4.3 Inputs and outputs

The handler signature is `async def fn(ctx: TaskContext[Input]) -> Output`.
The framework infers `Input` and `Output` from the annotation; the
typing flows through `task_id.run(input=X) -> Output`.

- **Inputs are persisted before the handler runs.** That is the
  guarantee crash recovery rests on: a recovered handler is invoked
  with the same `ctx.input` it would have seen in the lost lifetime.
- **Outputs are not persisted.** When the handler returns, the
  value resolves the caller's `await run.result()` — that is the
  only place it appears. There is no `payload["output"]` and no
  output attachment to inspect later. If you want to keep a
  per-turn artifact across crashes, write it through your handler
  (LangGraph checkpoint, your own DB, etc.) before you return.
- **Per-input size limit** ≈ 10 MiB (after JSON serialization).
  Larger inputs raise `InputTooLarge` at the caller before any
  network round-trip. Externalize (blob store + reference) for
  bigger payloads.
- **Persist `call_id` in typed task input.** When a task input exposes a
  top-level `call_id` field, the framework restores
  `FoundryAgentRequestContext` before every fresh, resumed, or recovered
  handler attempt. This lets SDK calls inside recovered handlers keep the
  original Foundry call identity.

### 4.4 The handler's context (`TaskContext`)

```python
class TaskContext:
    input: Input                   # the value the caller passed
    task_id: str
    input_id: str                  # per-turn id
    entry_mode: Literal["fresh", "resumed", "recovered"]
    retry_attempt: int             # 0 on the first try
    is_steered_turn: bool          # True iff this turn was promoted from the queue
    pending_input_count: int       # how many newer turns are queued

    # Cancellation signals — all cooperative.
    cancel: asyncio.Event          # any-cause cancel
    cancel_requested: bool         # cause: TaskRun.cancel() was called
    timeout_exceeded: bool         # cause: per-task timeout fired
    shutdown: asyncio.Event        # container is shutting down

    async def exit_for_recovery(self) -> None: ...
```

The first parameter MUST be named `ctx`. The framework binds
positionally, but it validates the name at decoration time so the
guide examples and your code stay consistent.

### 4.5 Durable application state

Task lifecycle state and application state are intentionally separate.
Create a `FoundryStateStore` with a stable application scope, then store
conversation checkpoints, watermarks, and deduplication tokens there.
State Store writes do not PATCH the task record or renew its lease.

```python
from azure.ai.agentserver.core.storage import FoundryStateStore

store = await FoundryStateStore.get_or_create(
    f"agents/my-agent/tasks/{ctx.task_id}",
)
state = await store.get_item("state")
await store.set_item("state", {"score": 42})
```

### 4.6 The result handle (`TaskRun`)

`.start(...)` returns a `TaskRun[Output]`:

```python
class TaskRun(Generic[Output]):
    task_id: str
    input_id: str
    is_queued: bool                       # True iff this is a queued steering input

    async def result(self) -> Output: ...
    async def cancel(self) -> None: ...
    def __await__(self) -> Output: ...    # so `output = await run` works
```

That is the entire `TaskRun` surface. The framework intentionally
does **not** expose `.delete`, `.refresh`, `.status`, or
`.lease_expiry_count` on the handle — for chain-level deletion use
`MultiTurnTask.delete(task_id)`, and for status inspection consult
the store directly via the task manager.

`run.is_queued` is `True` only when `.start()` landed against an
in-flight steerable chain and the input was **queued** (not yet
promoted to an active turn); it is `False` for a freshly-started or
active run. Cancelling a queued run removes its queued slot and
resolves `result()` with `TaskCancelled` without disturbing the
active turn. Composed protocol layers use it to decide whether to
acknowledge a request as `queued`.

### 4.7 Steering (multi-turn only)

Pass `steerable=True` to `@multi_turn_task` to opt into the steering
queue. With steering on, a `.start` against an in-flight chain
**queues** the new input rather than raising — the framework
delivers it as the next turn after the current turn ends.

```python
@multi_turn_task(name="conv", steerable=True)
async def conv(ctx: TaskContext[dict]) -> dict:
    return await llm(ctx.input)

# Mid-conversation steering: user changes their mind 50 ms into turn 1.
r1 = asyncio.create_task(conv.start(task_id="c1", input={"msg": "Plan a trip to Rome"}))
await asyncio.sleep(0.05)
r2 = asyncio.create_task(conv.start(task_id="c1", input={"msg": "Actually, Paris"}))
# r1 resolves with turn 1's outcome; r2 resolves with turn 2's outcome.
```

The handler observes `ctx.cancel.is_set()` during turn 1 if there's
something queued — it can wind down early and let the queued turn
take over (see §6 "interruptible turns").

### 4.8 Retry

Per-turn (multi-turn) or per-run (one-shot). Configure via the
decorator:

```python
from datetime import timedelta
from azure.ai.agentserver.core.tasks import RetryPolicy

@task(
    name="fetch",
    retry=RetryPolicy(
        max_attempts=3,
        initial_delay=timedelta(seconds=1),
        max_delay=timedelta(seconds=10),
        backoff_coefficient=2.0,
        jitter=True,
    ),
)
async def fetch(ctx: TaskContext[str]) -> bytes: ...
```

Retries are **off by default** (no `retry=` ⇒ a single attempt). The
`RetryPolicy` is validated at construction and **fails fast** on
misconfiguration (rejected, never silently clamped):

- `max_attempts` must be **1–10** (inclusive; counts the first try);
  `> 10` raises `ValueError`.
- `max_delay` must be **0 – 1 hour**; `> 1 hour` raises `ValueError`.
- `initial_delay` / `max_delay` must be `>= 0`, `backoff_coefficient`
  must be `>= 1.0`, and `max_delay >= initial_delay` — otherwise
  `ValueError`.

The delay for attempt *n* is
`min(initial_delay * backoff_coefficient ** n, max_delay)`, ±25% when
`jitter=True`.

`ctx.retry_attempt` (0-based) is exposed if your handler wants to
branch. The retry counter resets at every new turn boundary
(multi-turn) so a new turn starts with a fresh budget.

When the budget is exhausted, the caller sees
`TaskFailed(error=TaskExhaustedRetriesErrorDict(...))` (vs the
normal `TaskFailed(error=TaskErrorDict(...))` for a non-retryable
raise).

`ctx.retry_attempt` is persisted: **crash recovery does NOT consume
retry budget**. If attempt 2 of 3 crashes mid-flight, the recovered
handler sees `ctx.retry_attempt == 2` and still has its third
attempt available — the recovery is not counted as an extra retry.

### 4.9 Cancellation

Cancellation is **cooperative**. The framework never force-stops a
running handler. The handler observes `ctx.cancel` (an
`asyncio.Event`) and chooses how to wind down:

- Raise `asyncio.CancelledError` → caller sees `TaskCancelled`.
- `return X` → caller sees `X` (treated as a normal completion;
  for multi-turn that's an implicit suspend of the chain).
- Call `await ctx.exit_for_recovery()` (only valid when
  `ctx.shutdown` is set) → caller sees `TaskDeferred`; the task
  stays `in_progress`; the recovery scanner re-invokes the
  handler in a future process lifetime.

When the handler sees `ctx.cancel.is_set()`, it can branch on
the cause via the cause-discriminator booleans:

| Trigger                              | `ctx.cancel_requested` | `ctx.timeout_exceeded` | `ctx.shutdown.is_set()` |
|--------------------------------------|------------------------|------------------------|-------------------------|
| `await run.cancel()` (caller-cancel) | `True`                 | `False`                | `False`                 |
| Per-turn `timeout=` watchdog fires   | `False`                | `True`                 | `False`                 |
| Container graceful shutdown          | `False`                | `False`                | `True`                  |

`ctx.is_steered_turn` and `ctx.pending_input_count` round out the
steering-observability surface: a steerable handler that sees
`ctx.cancel.is_set()` AND `ctx.pending_input_count > 0` knows the
cancel was triggered by a newer turn being queued behind it and
can choose to wind down early so the next turn gets the lane.

### 4.10 Timeout

Each task can specify a `timeout` on its decorator. It defaults to
**1 day** when unset, and **7 days is a hard ceiling** — a larger or
negative value is rejected at decoration (`ValueError`, fail-fast). The
watchdog is **per-turn**, **wall-clock**, and **resilient**:

- **Per-turn (NOT a task lifetime)** — the budget caps how long a
  *single* handler invocation (one turn) may run uninterrupted. It
  resets at every turn boundary (multi-turn) or at the start of each
  fresh run (one-shot). Do **not** conflate it with the task's lifetime:
  a multi-turn task can stay alive **indefinitely** — the timeout resets
  every turn and never expires the task as a whole. The task's *overall*
  lifetime is governed separately by the platform's **30-day sliding
  TTL**: a task is cleaned up only after 30 days with **no new turns**,
  and every turn resets that window. If a recovered handler is
  re-invoked with the same `ctx.input` after a crash, the timeout starts
  from the persisted turn-start timestamp — not from the new lifetime's
  re-invocation.
- **Wall-clock** — the watchdog uses the persisted turn-start
  timestamp (UTC) and "now" wall-clock. It survives crashes: a
  recovered handler that started its turn one minute before a
  process death and has a 90-second budget gets ~30 seconds before
  the watchdog fires.
- **Resilient** — the persisted turn-start timestamp means the
  watchdog's view of "time elapsed" is the same across crashes,
  so a long-running turn cannot game the budget by triggering
  recovery to reset its clock.

When the watchdog fires it sets `ctx.cancel` and flips
`ctx.timeout_exceeded`. It is cooperative — it does NOT force-stop the
handler. The handler decides what to do (see §4.9).

### 4.11 Shutdown

Container shutdown sets `ctx.shutdown` (an `asyncio.Event`) AND
`ctx.cancel`. The intended handler response is to call
`await ctx.exit_for_recovery()`, which:

1. Releases the lease without writing a terminal status.
2. Raises `TaskDeferred` to the caller of `.result()`.
3. Leaves the task `in_progress` so the next process lifetime's
   recovery scanner picks it up and re-invokes the handler with
   the persisted `ctx.input`.

`exit_for_recovery()` is only meaningful during shutdown; calling
it outside that context is a programming error.

### 4.12 Multi-turn chain deletion

```python
await chat.delete("conv-7")
```

Force-removes the chain: cancels any in-flight turn, resolves all
queued steerer callers with `TaskCancelled`, and deletes the
record. Idempotent (no-op if the chain is already gone).

---

## 5. Reference

### 5.1 Decorators

```python
def task(
    *,
    name: str,                          # required — used for registration / recovery
    title: str | None = None,           # static label for telemetry
    timeout: timedelta | None = None,   # per-turn watchdog; defaults to 1 day, hard cap 7 days
    retry: RetryPolicy | None = None,   # None = no retry
) -> Callable[[Handler], Task[Input, Output]]: ...

def multi_turn_task(
    *,
    name: str,
    title: str | None = None,
    timeout: timedelta | None = None,   # per-turn watchdog; defaults to 1 day, hard cap 7 days
    retry: RetryPolicy | None = None,
    steerable: bool = False,
) -> Callable[[Handler], MultiTurnTask[Input, Output]]: ...
```

Each decorator produces a **distinct class** (`Task` vs
`MultiTurnTask`) — the type checker enforces "no `.delete()` on
one-shot" and "multi-turn `get_active_run` takes `(task_id,
input_id)`" statically.

### 5.2 `Task` (one-shot)

```python
class Task(Generic[Input, Output]):
    name: str

    async def run(
        self, *,
        input: Input,
        task_id: str | None = None,
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> Output: ...

    async def start(
        self, *,
        input: Input,
        task_id: str | None = None,
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]: ...

    async def get_active_run(self, task_id: str) -> TaskRun[Output] | None: ...
```

### 5.3 `MultiTurnTask`

```python
class MultiTurnTask(Generic[Input, Output]):
    name: str

    async def run(
        self, *,
        task_id: str,
        input: Input,
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> Output: ...

    async def start(
        self, *,
        task_id: str,
        input: Input,
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]: ...

    async def get_active_run(
        self, task_id: str, input_id: str,
    ) -> TaskRun[Output] | None: ...

    async def delete(self, task_id: str) -> None: ...
```

### 5.4 `TaskRun[Output]`

```python
class TaskRun(Generic[Output]):
    task_id: str
    input_id: str

    async def result(self) -> Output: ...
    async def cancel(self) -> None: ...
    def __await__(self) -> Generator[Any, None, Output]: ...
```

### 5.5 `TaskContext[Input]`

```python
class TaskContext(Generic[Input]):
    # Identifiers (read-only).
    input: Input
    task_id: str
    input_id: str
    entry_mode: EntryMode             # "fresh" | "resumed" | "recovered"
    retry_attempt: int                # 0 on the first try; survives crash recovery

    # Steering observability (multi-turn).
    is_steered_turn: bool             # True iff this turn was promoted from the queue
    pending_input_count: int          # how many newer turns are queued behind this one

    # Cancellation — all cooperative.
    cancel: asyncio.Event             # any-cause cancel
    cancel_requested: bool            # cause: TaskRun.cancel() was called
    timeout_exceeded: bool            # cause: per-turn timeout watchdog fired
    shutdown: asyncio.Event           # container is shutting down

    # Control.
    async def exit_for_recovery(self) -> None: ...
```

The handler's first parameter MUST be named `ctx`. The framework
binds positionally, but it validates the name at decoration time
so the guide examples and your handler stay consistent.

Read-only enumeration:

- `ctx.input`, `ctx.task_id`, `ctx.input_id`, `ctx.entry_mode`,
  `ctx.retry_attempt`
- `ctx.is_steered_turn`, `ctx.pending_input_count`
- `ctx.cancel`, `ctx.cancel_requested`, `ctx.timeout_exceeded`,
  `ctx.shutdown`
- `ctx.exit_for_recovery()`

### 5.6 Exceptions

Public exception taxonomy. Each carries only **new** information the
caller doesn't already have (the caller already has `task_id` /
`input_id` from the call site or `TaskRun`).

| Exception | Shape | When it is raised |
|-----------|-------|-------------------|
| `TaskFailed` | `error: TaskErrorDict \| TaskExhaustedRetriesErrorDict` | Handler raised; caller of `.result()` / `.run()` sees this. |
| `TaskCancelled` | bare | Cooperative cancel honoured (handler raised `CancelledError`); per-task timeout watchdog honoured; `MultiTurnTask.delete()` invalidating an in-flight run; queued steerer cancelled before promotion. |
| `TaskDeferred` | bare | Handler called `ctx.exit_for_recovery()` — the task continues resiliently; the recovery scanner re-invokes in a future lifetime. |
| `TaskConflictError` | `current_status: str` | `.start` / `.run` against an in-flight or terminal task that can't accept the call (one-shot in-progress / completed; multi-turn non-steerable in-progress). |
| `LastInputIdPreconditionFailed` | `actual_last_input_id: str \| None` | `if_last_input_id=` precondition didn't match. |
| `SteeringQueueFull` | bare | Steering queue at capacity (multi-turn `steerable=True` only). |
| `InputTooLarge` | bare | Input value exceeds the per-input cap. |
| `TaskManagerNotInitialized` | bare (subclasses `RuntimeError`) | A resilient-task operation (e.g. `.start` / `.run`) was attempted with no installed `TaskManager` — for example an in-process test harness that never ran the server lifespan, or a deployment where the manager failed to initialize at boot. |

`TaskFailed.error` is one of two `TypedDict`s:

```python
class TaskErrorDict(TypedDict):
    type: str            # exception class name, e.g. "ValueError"
    message: str         # str(exc)
    traceback: str       # traceback.format_exc()

class TaskExhaustedRetriesErrorDict(TypedDict):
    type: Literal["exhausted_retries"]
    attempts: int        # number of attempts made (>= max_attempts)
    last_error: str
    last_error_type: str
    traceback: str
```

### 5.7 `RetryPolicy`

```python
class RetryPolicy:
    initial_delay: timedelta
    backoff_coefficient: float
    max_delay: timedelta
    max_attempts: int
    retry_on: tuple[type[BaseException], ...] | None
    jitter: bool

    def __init__(
        self, *,
        initial_delay: timedelta = timedelta(seconds=1),
        backoff_coefficient: float = 2.0,
        max_delay: timedelta = timedelta(seconds=60),
        max_attempts: int = 3,
        retry_on: tuple[type[BaseException], ...] | None = None,
        jitter: bool = True,
    ) -> None: ...
```

Presets: `exponential_backoff(...)`, `fixed_delay(delay, ...)`,
`linear_backoff(...)`, `no_retry()`.

### 5.8 `JSONValue`

```python
JSONValue = Union[
    str, int, float, bool, None,
    list[JSONValue],
    dict[str, JSONValue],
]

```

### 5.9 `EntryMode`

```python
EntryMode = Literal["fresh", "resumed", "recovered"]
```

---

## 6. Patterns

### 6.1 Multi-turn agent (the common case)

```python
@multi_turn_task(name="session_agent")
async def session_agent(ctx: TaskContext[dict]) -> dict:
    # ctx.entry_mode is "fresh" on the first turn, "resumed" on
    # subsequent turns of this conversation.
    store = await FoundryStateStore.get_or_create(
        f"agents/session-agent/{ctx.task_id}",
    )
    item = await store.get_item("conversation")
    state = dict(item.value) if item else {"history": [], "turn": 0}
    history = state["history"]
    user_msg = ctx.input["message"]
    history.append({"role": "user", "content": user_msg})

    reply = await llm.chat(history)

    history.append({"role": "assistant", "content": reply})
    state["turn"] += 1
    await store.set_item("conversation", state)
    return {"reply": reply, "turn": state["turn"]}

# Turn 1.
r1 = await session_agent.run(task_id="conv-A", input={"message": "hi"})

# Turn 2 — same task_id resumes the chain; history is preserved.
r2 = await session_agent.run(task_id="conv-A", input={"message": "what time is it?"})
```

### 6.2 At-most-once side effects across crashes

```python
@task(name="charge_card")
async def charge_card(ctx: TaskContext[dict]) -> str:
    # Survive recovery: if we already charged in a prior lifetime,
    # don't double-charge.
    store = await FoundryStateStore.get_or_create(
        f"payments/tasks/{ctx.task_id}",
    )
    item = await store.get_item("charge")
    state = dict(item.value) if item else {}
    if state.get("charge_done"):
        return state["charge_receipt"]

    # Persist a dedup token before the side effect, then act.
    state["pending_charge_token"] = generate_uuid()
    await store.set_item("charge", state)

    receipt = await payment_gateway.charge(
        ctx.input["card"],
        ctx.input["amount"],
        idempotency_key=state["pending_charge_token"],
    )

    state["charge_done"] = True
    state["charge_receipt"] = receipt
    await store.set_item("charge", state)
    return receipt
```

### 6.3 Steering — interruptible long turn

```python
@multi_turn_task(name="thinker", steerable=True)
async def thinker(ctx: TaskContext[dict]) -> dict:
    partial = []
    async for chunk in slow_llm_stream(ctx.input):
        if ctx.cancel.is_set():
            # User changed their mind — surface what we have and bow out.
            return {"interrupted": True, "partial": "".join(partial)}
        partial.append(chunk)
    return {"reply": "".join(partial)}

# Turn 1 starts a slow generation.
r1 = asyncio.create_task(thinker.start(task_id="t1", input={"msg": "long question"}))
# 50 ms later the user pivots.
await asyncio.sleep(0.05)
r2 = asyncio.create_task(thinker.start(task_id="t1", input={"msg": "shorter question"}))
# r1.result() resolves with {"interrupted": True, ...}; r2 with the answer.
```

### 6.4 Graceful shutdown — `exit_for_recovery`

```python
@multi_turn_task(name="long_runner")
async def long_runner(ctx: TaskContext[dict]) -> dict:
    for step in plan(ctx.input):
        if ctx.shutdown.is_set():
            # Container is going down; defer to the next lifetime.
            await ctx.exit_for_recovery()      # raises TaskDeferred upstream
        await do(step)
    return {"done": True}
```

The caller awaiting `await run.result()` sees `TaskDeferred`. The
task record stays `in_progress`; the next lifetime's recovery
scanner re-invokes the handler with the same `ctx.input` and
`entry_mode="recovered"`.

### 6.5 Late-join an in-flight run

```python
# Caller A launched the work…
run_a = await chat.start(task_id="conv-9", input_id="i1", input={"msg": "hi"})

# … but caller B (different coroutine / different request) wants to
# attach to the same in-flight turn:
run_b = await chat.get_active_run("conv-9", "i1")
if run_b is not None:
    output = await run_b              # same Output that A sees
```

`get_active_run` returns `None` when the chain isn't in-flight for
that exact `(task_id, input_id)` — no retrospective attach to a
terminated turn.

### 6.6 Optimistic concurrency on the input queue

```python
prev_input_id = "msg-7"   # what the caller thinks the chain last accepted

try:
    await chat.run(
        task_id="conv-2",
        input_id="msg-8",
        input={"msg": "next"},
        if_last_input_id=prev_input_id,
    )
except LastInputIdPreconditionFailed as exc:
    # Concurrent caller advanced the chain to exc.actual_last_input_id;
    # re-fetch UI state and try again.
    ...
```

---

## 7. Operational notes

- **Heartbeats / lease.** The framework holds a lease on the
  task record while the handler runs and renews it automatically.
  If the process dies, the lease expires and the recovery scanner
  reclaims the record on a future process startup.
- **Recovery is from the persisted input.** A recovered handler is
  invoked with the same `ctx.input` the lost lifetime saw — not
  with any new input the caller may now be passing. (A caller's
  new `.start` against an in-flight record with an expired lease
  follows the normal lifecycle: rejected for one-shot /
  non-steerable, queued for `steerable=True` multi-turn.)
- **Structured failure logs.** Every handler raise emits an
  ERROR-level event named `resilient_task_handler_failure` with
  `task_id`, `input_id`, `error_type`, `error_message` fields —
  visible in your observability pipeline whether or not your caller
  awaited the failed `.result()`.
- **Storage backends.** The same primitive runs against the hosted
  task store and against a local file-backed store for development
  and tests.
- **Streaming** is a separate primitive in
  `azure.ai.agentserver.core.streaming` — `await streams.get_or_create(invocation_id)`
  gives the handler a stream handle. `TaskRun` itself is not
  iterable.

---

## 8. What This Is NOT

- **Not a deterministic-replay framework.** The handler is re-invoked
  from the top on recovery; the framework does not record and
  replay every effect. Determinism across re-invocations is the
  handler's responsibility — use application-owned State Store
  watermarks for at-most-once patterns (see §6.2).
- **Not a workflow engine.** No fan-out / fan-in, no child-workflow
  orchestration, no first-class signals or timers. If you need
  those, use Temporal and wrap resilient tasks
  inside them.
- **Not an application data store.** Persist conversation history,
  watermarks, and checkpoints through `FoundryStateStore` or a dedicated
  checkpointer. Keep large blobs in blob storage.
- **Not a queue.** A `task_id` identifies one logical unit of
  work. If you want competing consumers off a shared queue, use a
  different primitive.

---

## Quick FAQ

**Q. How do I do "fire and forget"?**
A. `await task_fn.start(input=...)` — the call returns a `TaskRun`
handle as soon as the work is registered. You can drop the handle
and the task runs resiliently; the next caller can attach via
`get_active_run(task_id)` if they care about the outcome.

**Q. Can two callers run the same `task_id` concurrently?**
A. No — `task_id` is the identity. The second caller either attaches
to the first's in-flight run (one-shot via the lifecycle merge),
gets queued (multi-turn `steerable=True`), or sees `TaskConflictError`.

**Q. Does the framework retry by default?**
A. No. Pass `retry=RetryPolicy(...)` to opt in.

**Q. Where should I store conversation history?**
A. Use `FoundryStateStore` for durable JSON conversation state or a
dedicated checkpointer such as LangGraph SqliteSaver.

**Q. I compose LangGraph with a resilient task. How do I fork its state on
steer/recovery, and why do I get `KeyError: 'checkpoint_ns'`?**
A. On a steered or crash-recovered turn, re-run from the last STABLE graph
checkpoint (recorded in State Store) rather than resuming the graph's latest
(possibly half-executed) tip — otherwise you mis-attribute the turn's input or
lose work. To fork, resolve that checkpoint with
`graph.get_state({"configurable": {"thread_id": ..., "checkpoint_id": cp}})` and
`update_state(...)`. The catch: LangGraph's sqlite checkpointer (`SqliteSaver` /
`AsyncSqliteSaver`) requires `checkpoint_ns` on the config it writes through, but
a resilient task only carries `thread_id` — so seed the default namespace
explicitly (`"checkpoint_ns": ""`) in that config, or the write raises
`KeyError: 'checkpoint_ns'`. And use `Command(resume=...)` only when the graph is
genuinely parked at an `interrupt()` (the normal next turn) — never to "resume" a
crash-drifted graph pending a non-interrupt node. See
`samples/resilient_langgraph` (invocations) and the responses
`sample_21_resilient_langgraph` for a worked pattern.

**Q. What if my handler ignores `ctx.cancel`?**
A. Cooperative cancel is a request; nothing forces the handler to
stop. If your handler must be interruptible, check
`ctx.cancel.is_set()` in your loop. `MultiTurnTask.delete(task_id)`
is the only call that force-cancels: it sets the cancel event AND
hard-cancels the underlying asyncio task so a non-cooperating
handler still exits.

**Q. How do I inspect a task's persisted state from outside the handler?**
A. Consult the task manager's provider directly:
`await manager.provider.get(task_id)` returns a `TaskInfo` snapshot.
The decorator's public surface intentionally doesn't expose a
`.get()` method — read paths go through the provider so the public
decorator surface stays small and write-shaped.
