# Resilient Task & Streaming Primitives — Design Specification

**Status:** Authoritative, source-of-truth specification.
**Scope:** The **`@task` resilient-task primitive** and the **`streams`
streaming primitive** in `azure-ai-agentserver-core` — i.e.
everything that ships under `azure.ai.agentserver.core.tasks.*`
and `azure.ai.agentserver.core.streaming.*`. NOT a spec for the
rest of the core package (the hosting foundation, middleware,
logging, tracing, server-side ASGI plumbing, etc. are outside
this document's scope).
**Audience:** Implementers building or maintaining these two
primitives in any language (Python, .NET, …), and contributors
modifying the canonical Python implementation. Treat this document
as the only doc a re-implementer needs.
**Out of scope:** Everything else in `azure-ai-agentserver-core`
beyond the two named primitives. The `azure-ai-agentserver-responses`
and `azure-ai-agentserver-invocations` packages. Response-event-stream
wire shapes. HTTP route plumbing for response APIs. The platform
itself.

This document is the authoritative single source of truth for the
two primitives in scope.

It **references** the *Foundry Task Storage Protocol Specification*
as the authoritative description of the hosted task store's HTTP
contract (routes, request/response envelopes, server-side merge
rules, authentication, activation, ETag/CAS, error codes). Where
this spec talks about wire shape, the framework MUST conform to
that protocol spec; this spec only describes **how the framework
uses** the store, plus the framework-reserved keys / conventions
it layers on top.

---

## Table of contents

### Part I — Orientation
- §1. Purpose and design goals
- §2. Non-goals
- §3. Architecture overview
- §4. Glossary (forward-reference)

### Part II — Programming model (developer-facing concepts)
- §5. The resilient task primitive
- §6. Lifecycle and entry mode
- §7. Identity (`task_id`, `agent_name`, `session_id`, lease owner)
- §8. Inputs, outputs, and per-input size limit
- §9. Persistence ownership (framework vs developer)
- §10. Crash recovery
- §11. Suspend, resume, and multi-turn
- §12. Steering primitive
- §13. Cancellation and cause booleans
- §14. Timeout (per-turn, cooperative)
- §15. Retry
- §16. Shutdown and `exit_for_recovery`
- §17. Metadata namespaces

### Part III — Storage contract (wire-level)
- §18. Reference to the Foundry Task Storage Protocol
- §19. The framework's view of the task record
- §20. Framework-reserved payload keys
- §21. Framework-reserved tag and source values
- §22. Lease structure and ownership semantics (+ §22.1 lease write rules)
- §23. Attachments and input promotion (+ §23.9 key validation, §23.10 clear-all)
- §24. Status state machine (+ §24.1 transition matrix, §24.2 terminal immutability, §24.3 delete force semantics)
- §25. ETag (optimistic concurrency) usage
- §26. Recovery — internal lifecycle (no public HTTP endpoint)

### Part IV — Provider abstraction (storage backends)
- §27. `TaskProvider` interface
- §28. Hosted provider (HTTP)
- §28a. Field validation (shared between providers)
- §29. Local provider (file-backed)
- §30. Provider auto-selection
- §31. Background loops
- §31a. List filter parity (internal `list()`)

### Part V — Public API surface (language-agnostic)
- §32. `task` and `multi_turn_task` decorators
- §33. `Task` (one-shot) and `MultiTurnTask` (multi-turn) handles
- §34. `TaskContext`
- §35. `TaskRun`
- §35a. Read-only inspection (internal — via the task manager's provider)
- §36. `TaskRun.result()` returns `Output` directly
- §37. Application state ownership
- §38. `RetryPolicy`
- §39. Error taxonomy

### Part VI — Streaming primitive (peer subpackage)
- §40. Why streaming is decoupled from `@task`
- §41. `EventStream` protocol
- §42. The `streams` registry
- §43. Stream lifecycle states (Active ↔ Closed; registry tombstones)
- §44. Concrete backings (live, replay, file-backed)
- §45. Cursor and `subscribe(after=...)`
- §46. TTL eviction and the close-clock (replay backings)
- §47. Streaming error taxonomy
- §48. Third-party stream-impl pattern

### Part VII — Implementation guidance (algorithms)
- §49. Cold-start sequence
- §50. `.start()` lifecycle resolution
- §51. Steering append (atomic)
- §52. Steering drain (two-phase)
- §53. Suspend write
- §54. Recovery + reclaim
- §55. Periodic recovery loop
- §56. Lease renewal loop
- §57. Per-turn watchdog
- §58. Orphan attachment cleanup

### Part VIII — Conformance items
- §59. Conformance items (C-1 … C-N)

### Part IX — References
- §60. References

### Part X — Appendices (informative)
- §A. Language-mapping cheat sheet
- §B. Representative full task record
- §C. Steering sequence (append → cancel → drain → result)
- §D. Cold-start recovery sequence

---
## Part I — Orientation

### §1. Purpose and design goals

The resilient-task primitive turns a single async agent function into a
**crash-resilient, steerable, long-running** unit of work backed by a
resilient task store. It exists to close the gap between:

- **What the platform sees.** A unit of work it can place, restart,
  liveness-check, and reclaim.
- **What the application owns.** A plain function the developer writes
  once, that survives container crashes, OOM kills, redeployments, and
  cooperative cancellation without hand-rolling lease, heartbeat,
  checkpoint, recovery, or steering plumbing.

The streaming primitive (`azure.ai.agentserver.core.streaming`) is a
**peer** to the resilient primitive — it does *not* nest under
`@task`. It exists to give every async producer/consumer pair in the
agentserver family a single Protocol to program against (in-memory live
fan-out, in-memory replay with cursor, file-backed crash-recoverable
replay), independent of whether the producer happens to be a `@task`.

Five design goals constrain every decision in this document:

1. **Single invariant for the resilient primitive.** For any given
   `task_id`, at most one handler runs at a time. Every other behavior
   falls out of this invariant.
2. **Crash-recovery is first-class, not a feature.** Every API
   decision is evaluated against the question "what does this look
   like after a crash?" A primitive that disappears at the crash
   boundary (a per-call kwarg, an in-memory listener, a closure-only
   state) is not acceptable; it must be reified into the resilient
   record or it must be on the developer.
3. **Cooperative everywhere.** The framework signals; it does not
   preempt. Cancellation, timeout, and steering all reduce to "set
   `ctx.cancel`; let the handler decide the terminal shape." Forced
   teardown belongs to the platform layer, not the primitive.
4. **Storage shape is the public contract.** The framework writes a
   structured task record. The shape of that record (which
   payload keys are reserved, what attachments look like, what tags
   are stamped) is part of the spec — implementers in other languages
   MUST produce byte-compatible records so a recovery scan from one
   process can pick up a task created by another.
5. **Pay only for what you use.** Streaming is decoupled because
   handlers that do not stream pay nothing. Attachments are
   thresholded because small inputs pay only the inline cost.
   Steering is opt-in because non-steerable tasks pay no queue
   overhead.

### §2. Non-goals

The primitive is intentionally narrow. The following are explicit
non-goals — they will NOT be added to the spec without explicit
re-scoping:

1. **Not deterministic replay.** No record-and-replay of effects.
   After a crash the handler is re-invoked from the top; only
   framework state (`ctx.input` and lifecycle counters)
   survives. Determinism inside the handler is the developer's
   responsibility — the standard at-most-once side-effect pattern in
   §10 covers the common case.
2. **Not a workflow engine.** No fan-out/fan-in, no child workflows,
   no signals or timers as first-class primitives. Use Temporal /
   Orleans for that — `@task` can live inside
   such an engine but does not replace it.
3. **Not an application-data store.** Durable application state,
   watermarks, and deduplication tokens belong in `FoundryStateStore`.
   Per-input payloads up to 10 MiB are accepted via the attachments
   mechanism (§23), but anything larger MUST be externalized by the caller.
4. **Not a competing-consumer queue.** A `task_id` identifies one
   logical unit of work owned by one current lifetime. N workers
   pulling jobs off a shared queue is the wrong fit; use a queue.
5. **Not multi-process streaming.** The streaming primitive's bundled
   backings are single-process. A future remote-backed implementation
   could plug into the same protocol but is out of scope here.
6. **No exactly-once side-effect guarantee.** The framework provides
   at-most-once via a developer-issued dedup token (the at-most-once
   pattern). Anything stronger requires external transactionality.
7. **Single wire shape.** The framework reads and writes exactly
   the shapes documented in this spec. The primitive is in private
   preview; there is no version-skew compatibility to maintain.

### §3. Architecture overview

The framework's runtime decomposes into the following components.
Boxes are types/objects; arrows show the dominant call direction.

```
                    ┌──────────────────────────────┐
                    │       application code        │
                    │   (user-written @task funcs)  │
                    └──────────────┬───────────────┘
                                   │  decorator registration
                                   ▼
   ┌─────────────┐    .start /   ┌─────────────────┐    create / get /
   │   caller    │ ─ .run ────▶  │  Task (handle)  │ ─  update / list  ──▶ ┌──────────────┐
   │ (HTTP,etc.) │ ◀─ TaskRun ─  │                 │                       │ TaskProvider │
   └─────────────┘    Output     └─────────┬───────┘                       └──────┬───────┘
                                            │                                     │
                                  invokes user fn                          ┌──────┴──────┐
                                            │                              │ Hosted via  │
                                            ▼                              │ HTTP +      │
                                   ┌─────────────────┐                     │ classifier  │
                                   │   TaskContext   │                     └──────┬──────┘
                                   │  (ctx.input,    │                            │
                                   │   ctx.cancel,…) │                            ▼
                                   └────────┬────────┘                  ┌──────────────────┐
                                            │ suspend /                 │   Foundry Task   │
                                            │ exit_for_recovery         │  Storage (HTTP)  │
                                            ▼                            └──────────────────┘
                                   ┌─────────────────┐                                ▲
                                   │   TaskManager   │ ──── lease_renewal_loop ──────┤
                                   │  (singleton)    │ ──── periodic_recovery_loop ─┤
                                   │                 │ ──── timeout_watchdog ───────┤
                                   └─────────────────┘                              │
                                                                                    │
                                  ┌────────────────────────────────────────┐        │
                                  │  Local file provider (dev/test only)   │ ◀──────┘
                                  │  (~/.agentserver/tasks/<agent>/<sess>/…)   │
                                  └────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────────────┐
   │ Streaming subpackage (PEER — not nested under @task)              │
   │                                                                   │
   │   ┌───────────────────┐    get_or_create(id)   ┌──────────────┐  │
   │   │  streams registry │ ──────────────────────▶│  EventStream │  │
   │   │  (process-level)  │ ◀───────────────────── │  (3 backings)│  │
   │   └───────────────────┘     delete(id)          └──────┬───────┘  │
   │            │                                            │         │
   │            │                              emit / subscribe        │
   │            ▼                                            ▼         │
   │  use_in_memory_live() /                       producers /         │
   │  use_in_memory_replay() /                     consumers           │
   │  use_file_backed_replay()                                         │
   └──────────────────────────────────────────────────────────────────┘
```

**Key relationships:**

- The `Task` handle is the developer-facing object created by the
  `@task` decorator; the singleton `TaskManager` is the *runtime*
  that owns the active-task table, the periodic recovery loop, and
  the provider.
- The `TaskProvider` is an abstraction over the task store. Two
  concrete providers ship: `HostedTaskProvider` (HTTP-backed, used
  when the platform is detected) and `LocalFileTaskProvider`
  (JSON-on-disk under
  `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/tasks/<agent>/<session>/<task>.json`
  by default; used otherwise). The framework auto-selects.
- The `TaskContext` is what the handler receives; it is wired by the
  manager and exposes both inputs (`input`, `metadata`, `entry_mode`)
  and signals (`cancel`, `shutdown`, cause booleans).
- Three background loops run while the manager is up: the periodic
  recovery scan (default 300s), one lease-renewal loop per active
  task (half the lease duration), and one timeout watchdog per
  active execution (when the task declares a timeout).
- The streaming subpackage is independent. Handlers that want to
  stream do `await streams.get_or_create(id)` and `emit` / `close`
  on the returned object; the HTTP layer attaches `subscribe(after=…)`
  consumers. The framework never touches a stream from the resilient
  path.

### §4. Glossary (forward-referenced)

| Term | Meaning |
|---|---|
| **Task** | A unit of resilient work, identified by `task_id`, persisted in the task store. |
| **Lifetime** | One contiguous in-memory execution of a task by a particular process. A task can have multiple lifetimes over its life (each crash starts a new lifetime). |
| **Turn** | One handler invocation. A fresh task with no resume/recover is one turn. A suspend/resume cycle is two turns. A steering-driven re-entry is the next turn. |
| **Generation / sequence number** | Monotonic counter inside the steering queue used to derive attachment keys; never reused (see §23). |
| **Lease** | The fenced ownership record on the task. While a process holds the lease, no other lifetime is allowed to run the task. |
| **Entry mode** | The framework's signal to the handler about WHY this turn started: `fresh` (first), `resumed` (after suspend or steering drain), `recovered` (previous lifetime crashed). |
| **Steering** | A new caller `.start()` against an already-running steerable task: the new input is queued, the current turn is cancelled cooperatively, and on the next turn the queued input is consumed. |
| **Attachment** | Per-task secondary storage slot for values larger than a payload-friendly inline threshold (§23). |
| **Ref / attachment ref** | The sentinel value the framework writes into `payload` to indicate "this slot has been promoted to `attachments[<key>]`" (§23.3). |
| **Cause boolean** | A read-only field on `TaskContext` (`timeout_exceeded`, `cancel_requested`) or counter (`pending_input_count`) that explains why `ctx.cancel` was set. |
| **Promotion** | The framework's act of moving an oversized input from inline `payload` into `attachments`, replacing the inline value with a ref (§23). |
| **Drain** | Popping a single steering input off the queue and re-entering the handler with it (§52). |
| **Reclaim** | A different lifetime taking over a task whose lease has expired (§54). |

---


## Part II — Programming model

This part is the developer-facing mental model. It is normative for
behavior visible to handler code, but the *wire-level realization* of
each concept lives in Part III.

### §5. The resilient task primitive

A resilient task is created by decorating a single async function:

```
@task(name="my_task")              # decorator
async def my_task(ctx) -> Out:     # exactly one parameter: TaskContext[Input]
    return ...
```

The decoration registers the function with the process-wide
descriptor table (consulted at recovery time). The returned object —
the *task handle* — is what callers invoke (`.run()` / `.start()`).

The framework guarantees one invariant: **for a given `task_id`, at
most one handler runs at a time in any process owning the active
lease.** Every higher-level behavior in this spec is derived from
that invariant.

### §6. Lifecycle and entry mode

The task store records each task in one of four statuses:

| Status | Meaning |
|---|---|
| `pending` | Created, not yet picked up by a handler. (Rarely observed by handler code — the framework moves through it atomically.) |
| `in_progress` | A handler is currently executing this task (or claims to be — a stale lease may need to be reclaimed). |
| `suspended` | (Multi-turn only.) Handler's turn ended with `return X`; the chain is parked between turns awaiting the next `.run()` / `.start()` to drive the next turn. |
| `completed` | Terminal. The handler is finished (success, raise, cancel) and will not run again. The *outcome* (success / failure / cancelled) is communicated via the typed exceptions (§39) — **NOT encoded in the status field**. |

Every time the framework invokes the handler, it computes an entry
mode from the persisted state and exposes it as `ctx.entry_mode`:

| Persisted state at entry | `entry_mode` | What it means |
|---|---|---|
| No task / status `pending` | `"fresh"` | First invocation. No prior state. |
| `suspended` | `"resumed"` | Caller provided new input; resume from where we suspended. |
| `in_progress` (previous lifetime died) | `"recovered"` | We are the new lifetime; check your watermark. |
| `in_progress` (steerable, mid-flight, steering drain) | `"resumed"` (with `ctx.is_steered_turn = True`) | Another input was queued; we are the next-turn re-entry. |

The handler is REQUIRED to be safe to enter in any of these modes.
Branching on `ctx.entry_mode` at the top is the canonical pattern.

`entry_mode` and `is_steered_turn` are orthogonal. The combination
`(entry_mode="recovered", is_steered_turn=True)` is legal: a previous
process crashed mid-drain and the recovered handler is taking over.

### §7. Identity

A task is identified by three independent strings:

| Field | Source | Lifetime | Purpose |
|---|---|---|---|
| `task_id` | Caller-supplied at `.start()` / `.run()`. | Identical across resume / recovery / steering. | The conversation / unit-of-work key. |
| `agent_name` | Platform-supplied (env `FOUNDRY_AGENT_NAME`); fallback `"unknown-agent"`. | Fixed per process. | Scoping; multiple agents share a store. |
| `session_id` | Platform-supplied (env `FOUNDRY_AGENT_SESSION_ID`). | Fixed per process. | Scoping; multiple sessions share an agent. |

The framework derives the **lease owner** string from both
`agent_name` AND `session_id`:

```
lease_owner = "<agent_name>|session:<session_id>"
```

Deriving the owner from BOTH components (not session alone) prevents
silent cross-agent ownership collisions in topologies where two
different agents happen to share a session identifier.

Each *process* generates a fresh **instance id** at startup:

```
lease_instance_id = "worker-<pid>-<rand8hex>-<unix_seconds>"
```

The `(owner, instance_id)` pair lets recovery distinguish:

- **Same-owner same-instance** = my own running task (renew, do not reclaim).
- **Same-owner different-instance** = a previous lifetime of mine that
  is gone (reclaim immediately on cold start; no expiry wait).
- **Different-owner** = someone else's task; do not touch.

#### `task_id` validation

Implementers MUST reject `task_id` values that:

- Are empty.
- Exceed 256 characters.
- Contain characters outside `[a-zA-Z0-9\-_.:]`.

Rejection is at the call site (`.start()` / `.run()` raise) before
any network is touched.

### §8. Inputs, outputs, and the per-input size limit

A task carries exactly one **input** value at any time — the value
passed to `.start(input=...)` or `.run(input=...)`. The input is JSON-
serialized for persistence and is re-hydrated into `ctx.input` on
every handler entry (fresh, resumed, recovered).

The handler's return value (or the value passed to
(the handler's `return X`) is the **output**, also JSON-serialized.

| Bound | Limit | Raised as |
|---|---|---|
| Per-input maximum size | **10 MiB** after JSON serialization, for the function input AND each individual queued steering input. | `InputTooLarge` from `.start()` / `.run()` — pre-network, at the call site. |
| Concurrent queued steering inputs | **9** | `SteeringQueueFull` from `.start()` against a steerable task whose queue is full. |

Inputs and outputs that fit easily in the inline payload budget stay
inline. Inputs whose JSON size exceeds a per-channel threshold are
**promoted** into the task's `attachments` slot transparently —
developers do not configure or opt in. See §23 for the wire
mechanism; the per-input ceiling above is the only developer-visible
limit.

The framework uses JSON canonicalization rules (`sort_keys=True`,
separators `(",", ":")`) when computing serialized sizes and content
hashes (§23.6). Implementers MUST use the same canonicalization for
both, or hashes will not match across implementations.

If the handler's input or output cannot be JSON-serialized (e.g. it
contains non-JSON-native types), the framework raises before the
HTTP call. Implementations using a richer model (Pydantic-style)
SHOULD attempt model-aware serialization (`model_dump`) first.

### §9. Persistence ownership

The framework persists:

- The current `ctx.input` value (inline or as an attachment ref).
- Lifecycle counters: `retry_attempt`, `recovery_count` (the
  `expiry_count` of the lease record), `last_input_id` (the
  optional caller-provided chain head — see §11).
- A per-turn `turn_started_at` ISO-8601 UTC timestamp used by the
  watchdog (§14) to compute remaining budget across crashes.
- Steering state (`pending_inputs` queue, `cancel_requested`,
  `drain_in_progress`, `active_input`, `next_input_seq`) for
  steerable tasks (§12).
- The handler's terminal outcome: a structured `error` dict on
  failure (when persisted by the layer above the primitive),
  `suspension_reason` on suspend. The handler's `return X` value
  is NOT persisted in the record — it resolves the in-process
  caller's `TaskRun.result()` future and is then no longer
  reachable from the persisted record.

The framework does NOT persist:

- Handler-local variables.
- In-memory closures over the handler's body.
- Caller-provided callbacks or futures (those are bound to a single
  lifetime; a crash discards them).
- Streaming events (those live in the streaming subpackage, which has
  its own backings; see Part VI).
- Any application state the developer chooses to compute. The developer
  is responsible for that through `FoundryStateStore`, a framework
  checkpointer, a custom database, or blob storage.

The dividing line is "what does the framework need to decide
`entry_mode` and reproduce `ctx`?" — that is what it persists; nothing
more.

When the persisted input has a top-level string `call_id` field, the
framework MUST bind a `FoundryAgentRequestContext` with that `call_id`
before invoking every fresh, resumed, or recovered handler attempt, and
MUST reset the binding afterward. Typed task inputs SHOULD declare
`call_id` explicitly when handler SDK calls need Foundry call continuity.

### §10. Crash recovery

Recovery is **framework-managed**. There is no developer-tunable
threshold and no opt-in.

**When recovery happens:**

1. **Cold start** of a new process. The manager's `startup()` scans
   the task store for tasks owned by `(agent_name, session_id)`
   whose lease has expired OR whose lease is owned by a different
   instance of the same owner (a previous dead lifetime). Each is
   reclaimed inline.
2. **Periodic scan.** While the manager is up, a background loop
   re-runs the same scan every 300 seconds (default; see §31). This
   catches tasks that became reclaimable AFTER cold start — typically
   leases that expired during this process's lifetime because a sibling
   process died.
3. **Inline reclaim.** When a caller `.start()`s a `task_id` whose
   current record shows an `in_progress` status with an expired or
   foreign-instance lease, the lifecycle resolver reclaims it inline
   (no waiting for the periodic scan).

**What recovery does:**

The reclaiming process:

1. Issues a PATCH that re-takes the lease atomically: new
   `lease_owner` (always self), new `lease_instance_id` (always
   self), new `lease_expires_at`, bumps the lease's `expiry_count` IF the
   previous lease had actually expired (not bumped for same-owner
   dead-instance handoff). This PATCH MUST be guarded by the read
   `etag` for CAS safety.
2. Reads the (now self-owned) record, looks up the registered
   resume callback by `source.name` (§21), invokes the handler
   with `ctx.entry_mode="recovered"` and the persisted `ctx.input`
   re-hydrated.
3. From the handler's perspective, recovery looks identical to a fresh
   entry except that `entry_mode == "recovered"`. Application state is
   loaded independently from State Store.

**Crash-recovery does NOT consume the retry budget** (§15). A
lifetime that died before the handler raised does not advance
`retry_attempt`.

**Pattern — at-most-once side effect across recovery:**

```python
store = await FoundryStateStore.get_or_create(
    f"agents/my-agent/tasks/{ctx.task_id}",
    user_isolation=True,
)
item = await store.get_item("effect")
state = dict(item.value) if item else {}
if state.get("dedup_token") is None:
    token = uuid4().hex
    state["dedup_token"] = token
    await store.set_item("effect", state)
    await do_side_effect(idempotency_key=token)
# crash-recovered lifetimes re-issue the call with the SAME token,
# letting the downstream system de-dupe.
```

This pattern is the standard answer to "I crashed mid-effect; how
do I avoid duplicate effects?" The framework does NOT provide
exactly-once semantics — the developer issues the dedup token and
fences it before the effect.

### §11. Suspend, resume, and multi-turn

Multi-turn chains end every turn with a bare `return X` from the
handler. The framework treats this **return-is-implicit-suspend**:

1. Transitions the stored status from `in_progress` to `suspended`
   with `suspension_reason="run_completion"`.
2. Does NOT persist `X` anywhere in the task record. `X` resolves
   the caller's `await run.result()` in-process and is then gone.
3. Clears `payload["input"]` (and the corresponding attachment if
   the input was promoted) — the consumed input is no longer needed
   and would inflate the next payload write.
4. Clears `steering["active_input"]` (mechanism state lives, but
   the consumed input value goes).
5. Clears `payload["retry_attempt"]` so the next turn starts with
   a fresh retry budget.
6. Preserves `payload["last_input_id"]` so the next
   `if_last_input_id` precondition can be evaluated.

The caller's `await run.result()` resolves to `X` directly (typed
as the handler's `Output`). No wrapper class.

The next `.run(task_id=same, input=new)` or
`.start(task_id=same, input=new)` transitions the status back to
`in_progress` and re-invokes the handler with
`ctx.entry_mode="resumed"` and `ctx.input=new`.

The same machinery is what multi-turn conversations and
human-in-the-loop approval flows ride.

One-shot tasks do NOT use this mechanism. A one-shot `@task`
handler's `return X` is a terminal completion: the framework
resolves the caller's `.result()` with `X` and then deletes the
record (one-shot is always ephemeral).

#### Multi-turn raise semantics

If a multi-turn handler RAISES (an unhandled exception other than
`asyncio.CancelledError`), the chain still transitions to
`suspended` (NOT `completed` / `failed`) so subsequent turns can
continue:

1. Transitions to `suspended` with
   `suspension_reason="run_completion"`.
2. NO `payload["error"]` is written — the chain record does not
   carry the per-turn failure diagnostic.
3. The framework emits a structured ERROR log named
   `resilient_task_handler_failure` with `task_id`, `input_id`,
   `error_type`, `error_message`.
4. The caller's `await run.result()` raises
   `TaskFailed(error=TaskErrorDict(...))`.
5. Queued steerers (multi-turn `steerable=True`) promote per §12:
   the next queued input becomes the next turn's input, and the
   handler re-invokes with `ctx.entry_mode="resumed"`,
   `ctx.is_steered_turn=True`.

#### Chain identity: `input_id` and `if_last_input_id`

Both `.run()` and `.start()` accept two optional keyword arguments
that thread caller-supplied chain identity through the persisted
record:

- **`input_id`** — record-only. The framework writes
  `payload["last_input_id"] = input_id` after accepting the input;
  no precondition is checked.
- **`if_last_input_id`** — precondition. The framework requires the
  stored `last_input_id` to equal `if_last_input_id` (the
  predecessor the caller claims to be extending). Mismatch raises
  `LastInputIdPreconditionFailed(actual_last_input_id=<stored>)`.

For multi-turn, `input_id` is the per-turn identity. For one-shot,
`input_id` defaults to `task_id` (the 1:1 invariant `task_id ==
input_id`).

A caller-supplied `input_id` MUST be validated against the same
charset/length pattern as `task_id` (`^[a-zA-Z0-9\-_.:]{1,256}$`);
a violation raises `ValueError` at the call site before any provider
call (fail-fast).

Implementations MUST reject `if_last_input_id` provided without
`input_id` (`TypeError` at the call site). The pair is orthogonal:
`input_id` alone is idempotency / chain-head tracking;
`(input_id, if_last_input_id)` together is HTTP-`If-Match`-style
chain extension.

### §12. Steering primitive

`@multi_turn_task(steerable=True)` upgrades a multi-turn chain from
"one turn at a time" to "callers can queue a new input while a turn
is mid-flight."

Steering is exclusive to multi-turn chains. One-shot `@task` does
not support steering (the one-shot lifecycle is one input one run);
`@multi_turn_task` without `steerable=True` accepts concurrent
`.start` calls only as `TaskConflictError`.

#### What `.start()` does on an in-flight steerable chain

`.start(task_id=<chain-id>, input=NEW)` against an in-flight
steerable chain:

1. The new input is **queued** at the tail of an internal
   pending-inputs FIFO.
2. The cancel signal is raised on the currently-executing turn —
   `ctx.cancel.is_set()` becomes True for the handler that is
   running right now. `ctx.pending_input_count` flips from 0 to
   the live backlog size.
3. A new `TaskRun` handle is returned to the caller. Its
   `.result()` resolves with **whatever the next turn emits** —
   the caller is the *steerer* of the next turn.

If the steering queue is at its cap (9), `.start()` raises
`SteeringQueueFull`.

#### What the first turn's caller sees

The first turn's caller observes the natural multi-turn outcome of
the in-flight turn:

| Handler ends turn 1 with... | First caller's `await run.result()` |
|---|---|
| `return X` (clean return) | Resolves with `X` (typed as `Output`). The chain transitions to `suspended` (return-is-implicit-suspend). The framework then promotes the queued steering input as the next turn. |
| `raise SomeError` (non-CancelledError) | Raises `TaskFailed(error=...)`. The chain stays alive in `suspended` with no `payload["error"]` written; the queued steerer is promoted as the next turn. |
| `raise asyncio.CancelledError()` | Raises `TaskCancelled()`. The chain stays alive in `suspended`; the queued steerer is promoted as the next turn. |
| Handler calls `ctx.exit_for_recovery()` (shutdown only) | Raises `TaskDeferred()`. The chain stays `in_progress`; the recovery scanner re-invokes the handler in a future lifetime. The queued steerer remains queued. |

The handler's `return X` value is delivered **unconditionally** to
the first caller; it is never replaced by what a later turn
produces.

#### Cooperative cancellation in steering

`ctx.cancel` is advisory. The framework sets it when a steering
input arrives (alongside the cause counter
`ctx.pending_input_count`), but does not preempt the handler. The
handler decides:

- **A — Yield immediately.** Check `ctx.cancel.is_set()` (or
  `ctx.pending_input_count > 0`) at the next boundary and `return`
  with whatever you have.
- **B — Wind down to a safe checkpoint.** Finish the current tool
  call / token batch, persist a clean checkpoint, then `return`
  with the final value.
- **C — Ignore cancel and finish.** Do not read `ctx.cancel`; let
  the handler complete. The chain still transitions to
  `suspended` and the queued steerer is promoted as the next
  turn.

#### Steering observability fields

On a steering-driven re-entry, `TaskContext` exposes:

- `ctx.is_steered_turn: bool` — `True` iff this turn was
  constructed by the steering-drain code path. False for every
  other entry path. Orthogonal to `entry_mode`:
  `(entry_mode="recovered", is_steered_turn=True)` is legal.
- `ctx.pending_input_count: int` — live count of currently queued
  steering inputs. Reads as 0 for non-steerable chains. Useful for
  "I am three turns behind, I should short-circuit even harder"
  decisions. It is derived from the **in-process observed** steering
  state (the property is synchronous — it does NOT issue a store read
  per access), and is **failure-tolerant** (any compute failure reads
  as 0). It is recorded *before* `ctx.cancel` is set (see §13 ordering
  invariant) by both the same-process enqueue and the cross-process
  steering poll, and is decremented as the drain consumes inputs, so a
  handler that observes `ctx.cancel.is_set()` for a steering cause
  already sees `pending_input_count >= 1`. It must be backed by a
  settable runtime field (historically it was read from an attribute
  that was never storable, so it was stuck at 0).

#### Force delete

`MultiTurnTask.delete(task_id)` is the only API that force-removes
a chain. It cancels the in-flight turn (active caller's
`.result()` resolves with `TaskCancelled`), resolves all queued
steerer callers' `.result()` futures with `TaskCancelled`, and
force-deletes the record. Idempotent (no-op on a missing chain).

### §13. Cancellation and cause booleans

`ctx.cancel` is a bare event (e.g. `asyncio.Event` in Python). The
framework sets it from multiple causes; a handler observing the bare
event does NOT know *why* it was set. Three independent **cause
booleans** answer the why:

| Cause | Set when | Reset? |
|---|---|---|
| `ctx.timeout_exceeded: bool` | Per-turn timeout watchdog has fired for this turn. | Never within a turn. |
| `ctx.cancel_requested: bool` | `TaskRun.cancel()` was invoked against this run from external caller code. | Never within a turn. |
| `ctx.pending_input_count: int` (read as a count, not boolean) | Live count of queued steering inputs >= 1. | Decrements as drains consume inputs. |

**Causes accumulate.** Multiple cause booleans can be `True`
simultaneously (e.g., timeout AND external cancel AND steering).

**Ordering invariant.** Each cause is set BEFORE the framework sets
`ctx.cancel`. A handler observing `ctx.cancel.is_set() == True` is
guaranteed to see at least one cause already set (cause booleans
or pending_input_count > 0).

Canonical reaction pattern:

```python
while not ctx.cancel.is_set():
    await do_a_unit_of_work()
# Branch on cause:
if ctx.timeout_exceeded:
    return "(timed out — partial result)"
if ctx.cancel_requested:
    raise asyncio.CancelledError()           # caller observes TaskCancelled
if ctx.pending_input_count > 0:
    return "(pre-empted by queued steering input)"
raise RuntimeError("ctx.cancel set with no recognised cause")
```

The handler's choice of terminal shape (`return X` / `raise`)
controls what the caller observes. The framework does NOT pick
the terminal shape on the handler's behalf. For multi-turn,
`return X` is the implicit-suspend boundary (chain stays alive,
caller's `.result()` resolves to `X`); for one-shot, `return X`
ends the run (record is deleted).

### §14. Timeout (per-turn, cooperative)

`@task(timeout=...)` is **cooperative-only**. When the budget elapses,
the framework:

1. Sets `ctx.timeout_exceeded = True`.
2. Sets `ctx.cancel`.
3. Exits the watchdog.

It does **NOT** force-stop the handler, end the task, or cancel
the lease renewal. An ignoring handler runs until process exit or
external `TaskRun.cancel()`.

The budget is **per-turn** and **wall-clock**:

- Each handler turn (fresh entry, suspended-to-resume) gets a
  fresh budget.
- A process crash mid-turn does NOT reset the budget. When the
  recovered handler enters, the watchdog computes
  `remaining = max(0, timeout - (now - turn_started_at))` from the
  persisted `turn_started_at` and fires immediately if elapsed.
- Clock skew is clamped to `[0, timeout]` in both directions.
- **Steering drain re-entry re-arms the watchdog.** The watchdog is
  spawned per turn — initial entry AND every in-place steering drain
  re-entry — so a steered turn gets a fresh full budget rather than
  inheriting whatever remained on the prior turn's watchdog. The
  persisted `turn_started_at` is stamped per drain (§52), so both the
  in-process drain path and a crash-then-recover from a drained turn
  honor the new turn's budget.

The framework MUST persist `payload["turn_started_at"]` (ISO-8601
UTC, `+00:00` offset form — consistent with all other task-record
timestamps and the .NET port; readers also accept a legacy `Z` suffix)
at every turn-start boundary: fresh entry, suspended -> in_progress
resume, steering drain re-entry. It is NOT re-stamped on crash
recovery — that is precisely what allows the watchdog to honor the
original budget across crashes.

### §15. Retry

`@task(retry=RetryPolicy(...))` and
`@multi_turn_task(retry=RetryPolicy(...))` configure the framework's
retry behavior for handler-raised exceptions.

`RetryPolicy` parameters:

| Field | Default | Meaning |
|---|---|---|
| `max_attempts` | `3` | Total failure-retry budget across all lifetimes. Counts the original try. |
| `initial_delay` | `1 second` | Delay before the first retry. |
| `backoff_coefficient` | `2.0` | Multiplier for exponential backoff. |
| `max_delay` | `60 seconds` | Cap on per-retry delay. |
| `jitter` | `True` | Add randomized jitter to delays. |
| `retry_on` | `None` (all exceptions) | Tuple of exception types to retry; others propagate. A bare exception class is accepted as a single-element tuple. |

**Hard caps (normative, fail-fast).** `RetryPolicy(...)` rejects a misconfiguration at
construction (raises, does NOT clamp) so a task turn cannot retry unboundedly:

- `max_attempts` must be **1–10** (inclusive; counts the first try). `> 10` → `ValueError`.
- `max_delay` must be **0 – 1 hour**. `> 1 hour` → `ValueError`.
- `initial_delay` / `max_delay` must be `>= 0`; `max_attempts >= 1`; `backoff_coefficient >= 1.0`;
  `max_delay >= initial_delay`. Zero delays are valid ("retry immediately").

**Preset values (normative).** The bundled presets — available both as
`RetryPolicy.<preset>(...)` classmethods and as module-level `tasks.<preset>(...)` wrappers with
identical zero-argument defaults (mirrored field-for-field by the .NET port) — are:

| Preset | `max_attempts` | `initial_delay` | `max_delay` | `backoff_coefficient` | `jitter` |
|---|---|---|---|---|---|
| `exponential_backoff()` | `3` | `1 s` | `60 s` | `2.0` | `True` |
| `fixed_delay()` | `3` | `5 s` | `5 s` | `1.0` | `False` |
| `linear_backoff()` | `5` | `1 s` | `60 s` | `1.0` (additive) | `False` |
| `no_retry()` | `1` | `0 s` | `0 s` | `1.0` | `False` |

Semantics:

- **`retry_attempt` is the cross-lifetime counter.** Persisted as
  `payload["retry_attempt"]`. Re-hydrated on every handler entry
  via `ctx.retry_attempt`. Increments only when the handler raises
  (not on crash). Cleared on every turn-start boundary so each new
  turn (multi-turn) or each new run (one-shot) gets a fresh budget.
- **Crash recovery does NOT consume the budget.** A lifetime that
  is gone before the handler raised does not advance
  `retry_attempt`. The recovered handler sees the same
  `ctx.retry_attempt` value the crashed lifetime saw.
- **`return X` bypasses retry.** A handler that returns
  (multi-turn = implicit suspend; one-shot = terminal completion)
  is not a failure; the retry counter is unaffected.
- When `retry_attempt >= max_attempts`, the framework gives up:
  it stops re-invoking, and the awaiting caller observes
  `TaskFailed(error=TaskExhaustedRetriesErrorDict(...))` carrying
  `attempts`, `last_error`, `last_error_type`, `traceback`.

#### Interim retry persistence

Between every failed attempt and the next retry the framework
PATCHes only `payload["retry_attempt"] = <attempt + 1>`. NO
`payload["error"]` is written between attempts — the per-turn
failure diagnostic is not projected onto the record. The status
stays `in_progress` throughout.

When the budget is exhausted (or the exception is non-retryable),
the failure handler runs:

- **One-shot (`@task`)**: the record is DELETED entirely; nothing
  survives on disk. The caller observes `TaskFailed` raised from
  `.result()`.
- **Multi-turn (`@multi_turn_task`)**: the chain transitions to
  `suspended` with `suspension_reason="run_completion"`; NO
  `payload["error"]` is written; queued steerers promote per §12.
  The caller of the failing turn observes `TaskFailed` raised
  from `.result()`. The chain stays alive — a future
  `.run()`/`.start()` against the same `task_id` resumes the
  chain with a fresh retry budget.

The framework emits a structured ERROR log named
`resilient_task_handler_failure` on every handler raise (including
non-final attempts). Observers learn "what just failed, which
attempt am I on" from logs, NOT from a persisted `error` field on
the record.

`TaskFailed.error` is one of two `TypedDict` shapes:

```python
class TaskErrorDict(TypedDict):
    type: str            # exception class name, e.g. "ValueError"
    message: str         # str(exc)
    traceback: str       # traceback.format_exc()

class TaskExhaustedRetriesErrorDict(TypedDict):
    type: Literal["exhausted_retries"]
    attempts: int
    last_error: str
    last_error_type: str
    traceback: str
```

Type-checkers can discriminate on the `type` literal.

### §16. Shutdown and `exit_for_recovery`

The container can be shut down at any time (deployment, rolling
restart, eviction). The framework sets `ctx.shutdown` when it
receives the shutdown signal. The handler has three legitimate
responses:

| Shape | When to use | Stored outcome | Caller observes |
|---|---|---|---|
| `await ctx.exit_for_recovery()` | Container shutting down AND you want this turn re-entered later. | `in_progress` (preserved across shutdown). | `TaskDeferred`. |
| `return X` (multi-turn) | Handler reached a clean checkpoint AND wants to expose `X` to the caller. | `suspended` (caller can `.run()` again to drive the next turn). | `X` (typed as `Output`). |
| `raise asyncio.CancelledError()` | Handler decided to abort. | One-shot: record deleted. Multi-turn: chain transitions to `suspended` (stays alive). | `TaskCancelled()`. |

`ctx.exit_for_recovery()` is the resilient-deferral primitive. The
method:

1. **Releases ownership** of the persisted record so the next
   process can take over (force-expires the lease).
2. Leaves status as `in_progress` (NOT `suspended`).
3. Raises `TaskDeferred()` upward — the caller of `.result()`
   sees this. Semantically distinct from `TaskCancelled`: the
   task is not cancelled; this lifetime is just deferring to the
   next.
4. Preserves any queued steering inputs — they are NOT drained
   during shutdown; on recovery they remain queued.

When the recovery scanner re-acquires the deferred task, the
handler re-enters with `ctx.entry_mode="recovered"` and the
persisted `payload["input"]` — exactly as if the lifetime had
crashed.

Misuse: calling `ctx.exit_for_recovery()` when
`ctx.shutdown.is_set() == False` MUST raise `RuntimeError` at the
call site. This makes misuse loudly visible to operators (the task
ends in error, not silently `in_progress`).

### §17. Application state ownership

The task record contains only framework lifecycle state and persisted
task input. Handlers MUST use an application-owned `FoundryStateStore`
or another dedicated persistence layer for conversation state,
checkpoints, watermarks, and deduplication tokens.

State Store operations are independent from task lifecycle PATCHes.
They MUST NOT renew the task lease, change the task etag, or become part
of suspend, complete, fail, drain, or `exit_for_recovery` transitions.

---


## Part III — Storage contract (wire-level)

This part documents how the framework projects the programming model
onto the resilient task record. The HTTP routes, request/response
envelopes, and server-side merge rules themselves are defined by the
*Foundry Task Storage Protocol* specification; this section names which
fields the framework reads/writes and what the framework-reserved
keys mean.

### §18. Reference to the Foundry Task Storage Protocol

The hosted task store's transport-level contract — routes
(`POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`,
`DELETE /tasks/{id}`), authentication, activation, payload PATCH merge
semantics, attachment PATCH merge semantics, ETag/CAS rules,
classification of 409/412 responses — is specified by
`foundrysdk_specs/specs/hosted-agents/container-spec/docs/foundry-task-storage-protocol-spec.md`.

This document does **not** restate that contract. Implementers MUST
conform to the protocol spec for any hosted-provider implementation.
The conformance items in §59 reference both this document and the
protocol spec.

Where this spec uses terms like "PATCH" or "etag", it does so under
the protocol spec's definitions.

### §19. The framework's view of the task record

The framework writes/reads the following fields on every task record.
Field meanings beyond this table are defined in the protocol spec.

| Field | Type | Owned by | Set on |
|---|---|---|---|
| `id` | string | caller | `create`. |
| `agent_name` | string | framework | `create`. |
| `session_id` | string | framework | `create`. |
| `status` | `pending` / `in_progress` / `suspended` / `completed` | framework | `create`, status transitions (§24). |
| `title` | string \| null | caller | `create` (optional). |
| `description` | string \| null | caller | `create` (optional). |
| `lease` | LeaseInfo (§22) | framework | `create`, every renewal, every reclaim. |
| `payload` | object | framework + developer | almost every transition (§20). |
| `tags` | map of string -> string | framework + caller | `create` (framework stamps `task_name`); caller-set tags allowed. |
| `error` | object \| null | framework | on handler raise. |
| `suspension_reason` | string \| null | framework | on suspend. |
| `source` | object | framework | `create` (§21). |
| `attachments` | object \| null | framework + developer | on input promotion / drain / suspend / orphan cleanup (§23). |
| `etag` | string | server | every server-issued response. |
| `created_at` | ISO-8601 string | server | `create`. |
| `updated_at` | ISO-8601 string | server | every PATCH. |
| `started_at` | ISO-8601 string \| null | server | **set once on first `in_progress` transition; never updated thereafter** (lease re-acquisition, recovery scanner takeover, and suspend/resume cycles do NOT reset). |
| `completed_at` | ISO-8601 string \| null | server | terminal transition. |

Caller-controlled fields (`tags` keys NOT starting with `_task_`,
`title`, `description`) are passed through verbatim. Framework-owned
fields MUST NOT be set by caller code.

### §20. Framework-reserved payload keys

`payload` is the JSON object that holds the framework's runtime state.
The framework reserves the following top-level keys:

| Key | Type | Lifetime | Meaning |
|---|---|---|---|
| `input` | any JSON value, or a ref dict (§23) | Set on every `in_progress` transition; cleared at suspend; cleared by drain after consumption. | The current input value (or a ref to its attachment). |
| `last_input_id` | string \| null | Set when caller supplies `input_id`. | Chain-head tracking (§11). |
| `turn_started_at` | ISO-8601 UTC string | Set at every turn-start boundary; NEVER re-stamped on recovery. | Source of truth for the per-turn watchdog (§14). |
| `retry_attempt` | integer | Incremented on handler raise; reset to 0 on steering drain. (Not also reset on success in the canonical Python implementation.) | Resilient retry counter (§15). |
| `steering` | object (see below) | Only present on steerable tasks. | Steering mechanism state (§12). |
| `schema_version` | string | Stamped at `create` (currently `"1"`); a future migrator may bump it via a payload PATCH. | Task-document schema version (§38). Its **presence** is required — a stale in-progress task lacking it is treated as pre-schema legacy and **deleted** (not recovered) by the recovery scan. |

The framework does NOT persist the handler's return value in the
task record. There is no `payload["output"]` key and no `output`
attachment. The handler's return value resolves the in-process
caller's `TaskRun.result()` future and is then no longer reachable
from the persisted record. Per-turn outputs that need to survive
crashes are the handler's responsibility — write them through
your own storage (e.g., LangGraph checkpoint, your own DB) before
returning.

Likewise, `error` from a handler raise is NOT persisted. The
framework emits a structured ERROR log (named
`resilient_task_handler_failure`) on every handler raise, but the
chain record itself does not carry the per-turn diagnostic.

`steering` object shape:

| Sub-key | Type | Meaning |
|---|---|---|
| `pending_inputs` | array of input values OR refs (§23) | FIFO of queued steering inputs. |
| `next_input_seq` | integer | Monotonic counter for promoted-attachment key allocation (NEVER reused). |
| `cancel_requested` | boolean | Resilient cancel signal; set on steering append; cleared after drain when pending is empty. |
| `drain_in_progress` | boolean | True between the start of a drain PATCH and the next turn-start; protects against partial drain on crash. |
| `active_input` | any JSON value OR ref | The single input being drained (mirror copy used by the race-recovery contract). Cleared at suspend / terminal. |

Implementers in other languages MUST use these exact key names. A
process built in language X must be able to recover a task created
by language Y.

Keys NOT in this table are caller-controlled (e.g. user metadata
namespaces); the framework leaves them alone.

### §21. Framework-reserved tag keys and `source` shape

#### Reserved tag keys

The framework stamps the following `tags` entries on `create`:

| Tag key | Value | Purpose |
|---|---|---|
| `task_name` | The decorator's required `name`. | Server-side `LIST` filtering by task name. |

Tag keys starting with `_task_` are RESERVED. Caller-supplied tags
using this prefix are stripped at the call site with a warning;
the framework does not pass them to the server.

#### `source` shape

The framework stamps `source` on `create`:

```
{
   "type":                "agentserver.task",
   "name":                "<the decorator's required name>",
   "server_version":      "<sdk_name>/<sdk_version> (<runtime>/<version>)",
   "hosting_environment": "<FOUNDRY_HOSTING_ENVIRONMENT, or \"\" in local/dev>"
}
```

`source.name` is the **canonical identity anchor** for recovery
routing — the framework looks up the registered handler callback
by matching `source.name` against the decorator-supplied names.
`source.type` is currently a single fixed string but is reserved
for future namespacing. `hosting_environment` is immutable creation
provenance stamped from the `FOUNDRY_HOSTING_ENVIRONMENT` env var
(always written; `""` when unset/empty). The **schema version**
lives in `payload` (not `source`) because `source` is immutable per
the Task API — a future migrator must be able to bump it via a
payload PATCH.

### §22. Lease structure and ownership semantics

`lease` is a sub-object with the following fields:

| Field | Type | Meaning |
|---|---|---|
| `owner` | string | `<agent_name>\|session:<session_id>` (§7). Stable across process lifetimes. |
| `instance_id` | string | `worker-<pid>-<rand8hex>-<unix_seconds>`. Fresh per process. |
| `generation` | integer | Increments each time the lease is re-acquired with a different `instance_id`. Mirrored to `ctx.recovery_count`. The local provider AND the hosted task store both bump this. |
| `expires_at` | ISO-8601 UTC string | When the lease expires (and another process may reclaim). |
| `expiry_count` | integer | Number of times ownership has changed via **actual expiry** (i.e. lease was reclaimed because the prior lease's `expires_at` passed, NOT because the same owner restarted). **Server- / provider-only counter** — the framework never writes this field (it is not on `TaskPatchRequest`). The hosted task store bumps it; the local file provider also bumps it on actual-expiry reclaim for parity (so local-mode tests can assert expiry-counter behavior). Surfaced on the framework's internal `TaskInfo`; NOT projected onto the public `TaskRun` handle (lease bookkeeping is framework-internal). |
| `heartbeat_at` | ISO-8601 UTC string | Wall time of the most recent lease write (acquisition, renewal, or force-expire). Stamped by the provider on every lease-touching PATCH. **Provider-only field** — the framework never writes this; consumers and observability tooling read it to distinguish "fresh lease" from "lease that hasn't expired yet". NOT projected onto the public `TaskRun` handle — it's a framework / operator concern, not a developer one. |

The framework's interaction with the lease:

- On `create`, the framework sets `lease_owner = self.owner`,
  `lease_instance_id = self.instance_id`, and
  `lease_duration_seconds = 60` (the framework default).
- The lease renewal loop (§56) renews at half the lease duration
  (every 30s by default), but its next tick is computed
  DYNAMICALLY from the per-task last-refresh time, NOT a fixed
  cadence. So a PATCH within the last `interval` seconds fully
  shadows the next heartbeat.
- **Every PATCH the framework issues** (renewal, metadata,
  steering, suspend, drain, complete, fail, reclaim) MUST
  piggyback (`lease_owner`, `lease_instance_id`,
  `lease_duration_seconds`) to refresh the lease as a side effect.
  See §25.4.
- On reclaim (§54), the framework PATCHes the lease to itself with
  `if_match: <last-seen etag>` for CAS. BOTH the inline reclaim
  AND the cold-start/periodic scan reclaim use `if_match` (closes
  the prior known gap).
- On `ctx.exit_for_recovery()` (§16), the framework force-expires
  the lease so the next process can reclaim immediately.

The framework recognizes three lease states for a foreign-instance
or expired record:

1. **Live and same-instance** — my own running task; do nothing.
2. **Live and different-instance, same-owner** — a previous lifetime
   of mine. RECLAIM immediately (no expiry wait). `expiry_count` is
   NOT bumped (the server only bumps on actual-expiry handoff, and
   this isn't one).
3. **Expired (any owner)** — RECLAIM. `expiry_count` IS bumped
   (server-side, in the hosted store; AND in the local provider
   for parity — see the table above).

**Important: the framework never writes `expiry_count`.** It is not
a field on `TaskPatchRequest` (only `lease_owner`,
`lease_instance_id`, `lease_duration_seconds` are writable). The
hosted task store and the local file provider both increment it
server-side / provider-side on actual-expiry ownership change; the
framework only reads it.

#### 22.1 Lease write rules (provider-enforced, identical for hosted and local)

These rules MUST be enforced by **both** providers identically.
Violations raise the internal `_HostedConflict` (§39) which the
framework translates to public exceptions per the translation table
(also §39). Local file provider raises the same logical conditions
directly, with the same internal classification, so the framework
behaves identically against either backing.

| # | Rule | When violated |
|---|---|---|
| LSE-W-1 | `lease_duration_seconds` MUST be `0` (force-expire) OR in the range `10..3600` (renewal). | Reject as `invalid_request` (400). |
| LSE-W-2 | The triplet `(lease_owner, lease_instance_id, lease_duration_seconds)` is all-or-nothing. Supplying any one without all three is rejected. | Reject as `invalid_request` (400). |
| LSE-W-3 | Lease acquisition / renewal against a record whose lease is currently held by a **different** owner AND not yet expired is rejected. | Raise `_HostedConflict(_code="lease_held_by_another")` → `TaskConflictError(current_status="in_progress")`. |
| LSE-W-4 | When transitioning a task from `in_progress` → `pending`, the supplied `(lease_owner, lease_instance_id)` MUST match the record's current lease. | Raise `_HostedConflict(_code="lease_held_by_another")`. |
| LSE-W-5 | Lease renewal (no status change, `lease_duration_seconds > 0`) is only valid when the current status is `in_progress`. Renewing on `pending` / `suspended` / `completed` is rejected. | Reject as `invalid_request` (400). |
| LSE-W-6 | `lease_duration_seconds = 0` (force-expire) cannot be combined with a status transition in the same PATCH. | Reject as `invalid_request` (400). |
| LSE-W-7 | Force-expire (`lease_duration_seconds = 0`) requires the caller's `(lease_owner, lease_instance_id)` to match the current lease UNLESS the lease is already expired (in which case any caller may force-expire). | Raise `_HostedConflict(_code="lease_held_by_another")` if mismatched and lease is still live. |
| LSE-W-8 | `started_at` is **immutable** after the first `in_progress` transition. Lease re-acquisition (including expired-lease takeover by a different owner OR same-owner restart) MUST NOT update `started_at`. The original wall-clock time of the first turn-start is preserved across recovery, restarts, and suspend/resume cycles. | (Behavioral — observable via the task manager's provider; not on the public `TaskRun` handle.) |
| LSE-W-9 | On lease handoff to a different owner where the prior lease was **expired**, `expiry_count` MUST be incremented. Same-owner different-instance handoff before expiry does NOT bump. | (Behavioral — observable via the task manager's provider; not on the public `TaskRun` handle.) |
| LSE-W-10 | On every successful lease write (acquisition, renewal, force-expire), the provider MUST stamp the lease's `heartbeat_at` field to "now". This field exists on `LeaseInfo` so consumers and observability tooling can distinguish a fresh lease from one that simply hasn't expired yet. | (Behavioral — observable through `LeaseInfo.heartbeat_at` in the internal `TaskInfo`. Not on the public surface.) |

### §23. Attachments and input promotion

The hosted task store provides a second per-task storage slot,
`attachments`, alongside `payload`. The two stores have different
budgets:

| Slot | Per-task cap | Per-value cap | Entry count cap |
|---|---|---|---|
| `payload` | 1 MB | n/a (shared) | unlimited keys |
| `attachments` | n/a (per-entry only) | 10 MiB per attachment | 20 attachments max |

`attachments` lets the framework lift the per-input ceiling from
"however much fits in payload alongside everything else" to
**10 MiB per input** without evicting metadata budget.

#### 23.1 PATCH merge semantics

The hosted store's merge semantics for `attachments` mirror `tags`:

- Key present with non-null value -> **upsert** (new) or **replace** (existing).
- Key present with `null` -> **delete** that entry.
- Key absent -> **unchanged**.
- `attachments` field absent entirely -> no attachment changes.

PATCHes that include BOTH `payload` and `attachments` are atomic
across both stores. This is load-bearing: every promote, drain,
suspend, and orphan-cleanup write co-PATCHes payload + attachments
in a single round trip.

#### 23.2 Thresholds + always-attachment for output (framework-owned)

The framework treats different channels differently. Inputs use a
size threshold; output ALWAYS uses an attachment (no threshold,
no inline shape).

| Channel | Promotion rule | Attachment key |
|---|---|---|
| Function input (`payload["input"]`) | > 200 KiB serialized → ref; otherwise inline. | `input` |
| Each steering input (entry in `steering["pending_inputs"]`) | > 20 KiB serialized → ref; otherwise inline. | `steering_input_<seq>` |

Different rules because:

- The function input is set once per turn-start. A 200 KiB inline
  budget keeps small inputs cheap and only spills clearly-large ones.
- Steering inputs may accumulate (up to 9 queued). A 20 KiB
  threshold caps the worst-case inline payload contribution from
  steering at ~180 KiB even when the queue is full.

There is no `output` channel and no output promotion. The
framework does not persist handler return values; outputs resolve
the in-process caller's `TaskRun.result()` future directly and are
never projected onto the task record.

Sizes are measured in bytes of canonical JSON
(`sort_keys=True`, separators `(",", ":")`).

Worst-case framework attachment usage:
`input` (1) + `steering_input_*` (up to 9) =
**10 of 20** per-task attachment slots. Leaves 10 slots free for
future use.

#### 23.3 Wire shapes — two only

A slot that would hold an input (`payload["input"]`, an entry in
`steering["pending_inputs"]`) is represented in exactly one of two
shapes:

**Inline** (size <= threshold): the raw JSON value, verbatim.

**Ref** (size > threshold): a single-magic-key dict pointing at the
attachment:

```json
{
   "__attachment_ref__": {
      "key":  "<attachment-key>",
      "hash": "sha256:<64 lowercase hex chars>"
   }
}
```

**Detection rule** (used everywhere the framework reads a slot):
the slot is a ref iff (1) it is a JSON object, (2) it has exactly
one key, (3) that key is `__attachment_ref__`, (4) the value is an
object with both `key` and `hash`. Everything else is inline.

The inline + ref shapes are **disjoint**: a developer-supplied
inline value cannot accidentally be misread as a ref because the
detection rule's 4-step structure is too specific to occur
incidentally.

#### 23.4 Single wire shape

The framework reads and writes exactly the inline + ref shapes
documented in §23.3. The primitive is in private preview; there is
no version-skew compatibility to maintain.

#### 23.5 Sequence number invariants (steering)

`payload["steering"]["next_input_seq"]` is the monotonic counter
the framework uses to derive `steering_input_<seq>` keys. Critical
invariants:

- **Advances ONLY on promotion.** Inline steering appends do not
  bump `next_input_seq`.
- **Never reused.** A drained-and-deleted key is never re-allocated;
  the next promoted append always uses the current
  `next_input_seq`, then `next_input_seq += 1`.
- **Stable for surviving entries.** A drain pops the head of
  `pending_inputs` and (if it was a ref) deletes the corresponding
  `steering_input_<seq>` attachment. It does NOT renumber any
  other entry. A queue of `[ref_3, ref_4]` becomes `[ref_4]` after
  one drain; `ref_4` keeps its key.

This invariant is what allows the framework to drain without
re-uploading attachments — a property that would be impossible if
keys encoded queue position.

#### 23.6 Content hash

Every ref carries `hash: "sha256:<hex>"` where the hex is the
SHA-256 of the canonical JSON bytes
(`sort_keys=True`, separators `(",", ":")`) of the attachment
value. The framework writes the hash on promotion.

**Hash validation (known gap).** The canonical Python
implementation today writes the hash on every promotion but does
NOT validate it on read — `_read_input_value()` resolves the ref
key against `attachments` and returns the value without
recomputing the hash. Other-language implementers SHOULD validate
on read (recompute hash from the attachment value, compare against
the ref's hash, raise on mismatch) to detect store-side
corruption. Cross-implementation byte-compatibility requires using
the SAME canonicalization rules so a write from one language can
be validated by another.

The hash is sufficient for ref validity once validated (no separate
write-timestamp is needed): SHA-256 birthday-bound collision
probability at fleet trillion/sec × 100 years is < 1 in 10^33.

#### 23.7 Caps and pre-network enforcement

Caps:

- Per-attachment value: **10 MiB** serialized.
- Per-task attachment count: **20**.

The framework enforces (pre-network) and surfaces developer-facing
exceptions based on which channel the violation occurs on:

| Cap | Where enforced | Developer-facing exception |
|---|---|---|
| Per-value (10 MiB) on `input` | Create + PATCH, both providers | `InputTooLarge` (the framework remaps an internal `_AttachmentTooLarge` based on attachment-key prefix) |
| Per-value (10 MiB) on `steering_input_<seq>` | Steering append site (always reads state first to count) | `InputTooLarge` |

| Per-task count (20) on `create` | Create path | `_AttachmentLimitExceeded` (internal) — reachable only via direct provider use, which is unsupported |
| Per-task count (20) on `patch` | Local provider (cheap count); hosted PATCH relies on server-side check | `_AttachmentLimitExceeded` (internal) |

Internal exceptions `_AttachmentTooLarge` and
`_AttachmentLimitExceeded` are **provider-internal** — they are
NOT exported from `tasks/__init__.py`. The framework catches
`_AttachmentTooLarge` and re-raises the appropriate developer-
facing exception based on the attachment key prefix (`input` /
`steering_input_*` → `InputTooLarge`).
`_AttachmentLimitExceeded` is unreachable in normal framework
operation (worst case is 11 of 20 slots; see §23.2) and if it ever
propagates indicates a framework bug — caught at the boundary and
converted to `RuntimeError`.

#### 23.8 Atomic co-writes

These transitions MUST be single PATCHes carrying BOTH `payload` and
`attachments`:

1. **Promote on `.start()` (fresh)**: `attachments["input"] = <value>`
   + `payload["input"] = {ref}` (CREATE on the hosted store).
2. **Promote on resume**: same fields, but PATCH.
3. **Suspend (multi-turn turn-end via `return X`)**:
   - `payload["input"] = null`
   - `payload["steering"]["active_input"] = null`
   - `payload["retry_attempt"] = null` (fresh budget for the next turn)
   - `attachments["input"] = null` (delete) IF the input was a ref
4. **Steering append (promoted)**: `payload["steering"]["pending_inputs"]
   += [{ref}]`, `attachments["steering_input_<seq>"] = <value>`,
   `payload["steering"]["next_input_seq"] += 1`,
   `payload["steering"]["cancel_requested"] = true`.
5. **Steering drain (promoted entry, Phase 1)**:
   `payload["steering"]["pending_inputs"]` without the popped
   head, `attachments["steering_input_<seq>"] = null`,
   plus the new turn's `turn_started_at`.
6. **One-shot completion**: the record is deleted (one-shot is
   always ephemeral).
7. **Failure**: one-shot → record deleted; multi-turn → status="suspended"
   with `suspension_reason="run_completion"`. No `payload["error"]`
   is written; the per-turn failure surfaces to the caller via
   `TaskFailed(error=...)` and via the structured log
   `resilient_task_handler_failure`.
8. **Resume (suspended → in_progress)**: status="in_progress",
   `turn_started_at` re-stamped, `retry_attempt` reset to 0.
   New input written (inline or as ref + attachment per §23.2).

Splitting any of these into multiple PATCHes opens a crash window
where the attachment exists without its ref (or vice versa). The
framework treats this as a single-PATCH invariant.

#### 23.9 Attachment key validation

Attachment keys MUST match the regex `^[a-zA-Z0-9_.\-]{1,64}$` and
MUST NOT be empty after trimming whitespace. Both providers enforce
this on every CREATE / PATCH write. The framework's reserved keys (`input`, `steering_input_<seq>`) all conform.
Developer-supplied attachment keys (none exist today — attachments
are framework-owned per §23.7) would also be validated against this
regex if the surface is ever expanded.

#### 23.10 Clear-all gesture

In addition to per-key null-as-delete (§23.1), the provider accepts a
top-level "clear all attachments" gesture:

- Wire form: `PATCH ... { "attachments": null }`.
- Effect: deletes every attachment on the task, regardless of which
  keys currently exist. Per-key entries supplied in the same PATCH
  are NOT applied (the clear takes precedence).
- Typed-API form: `TaskPatchRequest.clear_attachments = true`. When
  set, the hosted provider serializes `attachments: null`; the local
  provider clears the attachments dict directly. Mutually exclusive
  with `attachments={...}` (per-key patch) in the same request — the
  combination is rejected as `invalid_request`.
- The framework today never emits this gesture; per-key delete
  covers all current needs. It is documented for parity with the
  service and for future internal callers (e.g. orphan-attachment
  cleanup post-recovery).

DELETE on a task removes all attachments along with the task. The
local provider achieves this trivially (attachments live in the
same JSON file as the task record; unlinking the file removes
both). The hosted provider relies on the service's blob-cleanup
hook.

### §24. Status state machine

The framework drives the following transitions:

```
            create()                                handler returns
              │                                    or raises
              ▼                                    ┌──────────────┐
        ┌──────────┐    auto-start  ┌──────────────│  completed   │
        │ pending  │ ──────────────▶│ in_progress  │ (terminal)   │
        └──────────┘                │              │              │
                                    │              └──────────────┘
                                    │  return X (multi-turn)
                                    ▼              ▲
                              ┌──────────┐         │
                              │suspended │ ────────┘
                              └──────────┘ .run/.start with new input
                                    ▲
                                    │
                                    │ reclaim (same status,
                                    │ new lease)
                                    │
                                    └─── in_progress (foreign lease)
```

Notes:

- The framework usually creates with `status = in_progress` directly
  (the `pending` state is rarely externally observed).
- `in_progress -> in_progress` is the most-traversed transition
  (every lease renewal, every reclaim, every steering drain, every
  successful retry).
- `completed` is terminal; the *outcome* (success / failure /
  cancel) is communicated through the typed exceptions, not via a
  separate status value.
- `ctx.exit_for_recovery()` preserves `in_progress` and force-expires
  the lease — it is the only way to release ownership without moving
  to a different status (§16).

#### 24.1 Allowed transition matrix (provider-enforced)

The provider rejects PATCHes whose declared `status` transition is
not in this table. Internal classification `_HostedConflict(_code="invalid_state_transition")`,
translated to a generic framework error at the boundary (this
condition should never escape to developer code — the framework
chooses transitions, not the developer; if it ever does escape it's
a framework bug per Workstream C).

| From → To | `pending` | `in_progress` | `suspended` | `completed` |
|---|---|---|---|---|
| `pending` | n/a | ✅ | ❌ | ✅ |
| `in_progress` | ✅ (with matching lease) | ✅ (lease renewal) | ✅ | ✅ |
| `suspended` | ✅ | ✅ | ✅ | ✅ |
| `completed` | ❌ (terminal) | ❌ | ❌ | ✅ (no-op only — see §24.2) |

#### 24.2 Terminal immutability

A PATCH against a task whose current status is `completed` is
rejected UNLESS the PATCH is a no-op `completed → completed` AND
carries no other field changes (no `payload`, no `tags`, no
`error`, no `suspension_reason`, no lease). The no-op pass-through
returns the existing record without modification — this lets
idempotent retry-loops behave predictably.

Any other PATCH against a completed task raises
`_HostedConflict(_code="task_immutable")` → translated to
`TaskConflictError(current_status="completed")`.

#### 24.3 Delete force semantics

DELETE on a task in any **non-terminal** status (`pending`,
`in_progress`, `suspended`) requires `force=true`. Without it the
provider rejects the delete as `invalid_request` (400) — note this
is **NOT** a conflict (409); the service's PR 2135250 explicitly
moved this from 409 → 400 with code `invalid_request`.

DELETE on a **terminal** (`completed`) task always succeeds (no
force required).

DELETE additionally honors `If-Match`: when supplied, the
provider rejects the delete with `_HostedConflict(_code="etag_mismatch")`
→ `EtagConflict` if the supplied etag does not match the current
record.

### §25. ETag (optimistic concurrency) + in-process write serialization

The framework uses the hosted store's ETag/CAS protocol per the
Foundry Task Storage Protocol spec.

#### 25.1 Etag tracking — always-on after the first read/create

After the first successful read/create on a `task_id`, **every
subsequent PATCH MUST carry `If-Match` with the latest known etag**
for that task. The framework tracks the latest etag in the
in-memory active-task entry, updating it from every PATCH/GET
response. `delete()` is the only operation that MUST NOT carry
`if_match` — deletion is intentionally unconditional and tolerates
a concurrent winner.

**No blind writes.** This applies to *every* PATCH-issuing site,
including those that hold the per-task write lock and call the
provider directly to avoid re-entrant lock acquisition (e.g. the
queued-steering-cancel path): such sites MUST go through the
lock-held update helper that selects `If-Match` from the tracked
etag, never a bare `provider.update` with no `if_match`.

The service-returned `etag` value is passed verbatim as `If-Match`
on the next PATCH. The framework does NOT strip surrounding quotes,
normalize whitespace, or otherwise rewrite it.

#### 25.2 Per-task in-process write queue

Without coordination, the framework has multiple concurrent
PATCH-issuing code paths against the same task: lease renewal
heartbeats, metadata flushes (handler-issued AND auto-flush at
turn boundaries), steering append, steering drain Phase-1/3,
suspend, complete, fail, output writes, and reclaim. All of these
race in-process for the same etag and can produce avoidable 412
conflicts in steady state.

The framework MUST serialize these writes through a **per-task
asyncio lock** held for the read-state + compute-PATCH + apply
cycle. Reads (e.g., `Task.get(task_id)`) do NOT take this lock —
they're snapshot operations that don't move the etag.

The read MUST happen **inside** the lock for any read-modify-write
sequence (steering drain, queued-steering-cancel, etc.), so the
record read and the PATCH are atomic with respect to other
in-process writers (notably the lease-renewal heartbeat). A site
that reads the record (or pins an etag) *before* acquiring the lock
can have its etag invalidated by the heartbeat between the read and
the write, which under contention starves the retry budget. Because
the per-task lock is a **non-reentrant** `asyncio.Lock`, the
framework provides two helpers: a lock-acquiring update (for callers
that do not hold the lock) and a lock-held update (for callers that
already hold it, e.g. the drain); both select `If-Match` from the
tracked etag and refresh it on success.

Lock lifecycle:

- Per-`task_id` `asyncio.Lock` allocated lazily on first write.
- Released after the PATCH response is recorded (etag updated).
- Removed from the in-memory lock table when the local active-task
  entry is torn down (no leaked locks).

In-process contention now serializes; cross-process contention
(another worker reclaimed the lease) still surfaces as 412 because
the queue is in-process only.

#### 25.3 412 (etag conflict) resolution — per-operation policy

When a PATCH inside the queue gets a 412, the appropriate response
depends on the operation's INTENT. There is no single retry rule:

| Operation | On 412, do what |
|---|---|
| Metadata flush | re-read state, overwrite the addressed namespace with local value (last-write-wins), retry (up to 5 attempts). |
| Steering append | re-read `steering`, append to the NEW state's `pending_inputs`, bump `next_input_seq` from the NEW state, retry (up to 5 attempts). Idempotent when `input_id` is supplied. |
| Steering drain (Phase 1) | re-read `steering`, drain the NEW head, retry (up to 5 attempts). |
| Steering drain (Phase 3) | re-read, retry (up to 5 attempts). |
| Lease renewal heartbeat | re-read lease; if still ours, retry; otherwise signal eviction. |
| Suspend / complete / fail terminal writes | **RE-READ + decide.** A 412 here means our etag is stale — that's all we know on its own. Re-read the record, then choose: (a) if the lease is **no longer ours** (`lease.owner` differs OR `lease.instance_id` differs OR `lease.expiry_count` bumped past our cached value) → ABANDON and signal awaiters via the eviction path (C-LSE-4 / C-ERR-2); the new owner is authoritative and our terminal would clobber their in-flight recovery. (b) If `status` is already terminal (`completed`) → ABANDON; another actor already wrote the terminal. (c) Otherwise (lease still ours, status still `in_progress`) → retry the terminal PATCH against the new etag, up to 5 attempts. Steering inputs that another process appended between our read and our retry are silently superseded by the terminal write — that is correct behavior because the steerer's `.result()` MUST then raise `TaskConflictError(current_status="completed")` per C-STR-6, which is how cross-process steering-after-terminate is supposed to surface. |
| Output write (part of suspend/complete) | inherits the parent operation's policy. |
| Resume-clear-output (part of resume) | re-read, retry (up to 5 attempts). |
| Recovery reclaim (inline) | ABANDON. The 412 IS the race-detection — another process beat us to the reclaim. Let the next caller / scan re-evaluate. |
| Recovery reclaim (cold-start / periodic) | ABANDON. Same reasoning. |

Default retry budget is 5 attempts unless noted. Each retry
re-acquires the per-task lock before the re-read + re-merge + re-write
cycle. `LastInputIdPreconditionFailed` (for `if_last_input_id`) and
`EtagConflict` (for low-level callers) propagate as today.

#### 25.4 Auto-extension piggyback on every PATCH

Every PATCH the framework issues — renewal, metadata, steering,
suspend, etc. — MUST include the lease-extension trio
(`lease_owner`, `lease_instance_id`, `lease_duration_seconds`) so
the lease is refreshed as a side effect. The renewal loop's next
tick is computed dynamically from the per-task last-refresh time
(NOT a fixed cadence), so a PATCH within the last `interval`
seconds fully shadows the next heartbeat. See §56.

**Lease renewal requires `in_progress`.** The task store accepts the
lease-extension trio as a *renewal* only when the record is already
`in_progress`, and as a *claim* only when the same PATCH transitions
the record INTO `in_progress` (e.g. reclaim, or the steering-drain
Phase-1 PATCH per §52). A PATCH that carries the lease trio against a
`suspended`/`pending`/terminal record WITHOUT a status flip to
`in_progress` is rejected ("lease renewal is only supported for
in_progress tasks"). Therefore any framework path that writes to a
record left `suspended` by a prior turn (notably the steering drain)
MUST set `status='in_progress'` in the same PATCH. The local provider
enforces this same rule so the conflict is reproducible without a
hosted deployment.

### §26. Recovery — internal lifecycle, no public HTTP endpoint

There is no HTTP route for resume. Resume is initiated from
caller code via the normal `Task.start` / `Task.run` (one-shot)
or `MultiTurnTask.start` / `MultiTurnTask.run` (multi-turn) entry
points. The framework's lifecycle state machine transitions a
`suspended` task back to `in_progress` and re-enters the handler
without exposing a server-side endpoint.

Crash recovery for tasks that died mid-`in_progress` is handled
internally by the periodic recovery scanner described in §55:
the scanner detects abandoned leases and re-invokes the handler
with the persisted `payload["input"]` and
`entry_mode="recovered"`.

---

## Part IV — Provider abstraction (storage backends)

> **Visibility:** Everything in this part is **framework-internal**.
> The `TaskProvider` interface and the two concrete providers
> (`HostedTaskProvider`, `LocalFileTaskProvider`) are NOT part of
> the public surface defined in Part V — in the canonical Python
> implementation, all of these live in `_`-prefixed modules
> (`_provider.py`, `_client.py`, `_local_provider.py`) and are
> NOT re-exported from `tasks/__init__.py`'s `__all__`. The
> abstraction exists to keep the manager testable and to let the
> framework swap hosted vs. local backends — but framework
> consumers are not expected (and not supported) to construct or
> consume providers directly. This part documents the contract a
> re-implementer (in another language) MUST satisfy when writing
> the provider layer.

### §27. `TaskProvider` interface

The framework abstracts over the storage backend via a single
async interface. Two providers ship: hosted (HTTP-backed) and local
(file-backed); a third (in-memory) is conceptually possible.

```
class TaskProvider:
    async def create(request: TaskCreateRequest) -> TaskInfo: ...
    async def get(task_id: str) -> TaskInfo | None: ...
    async def update(task_id: str, patch: TaskPatchRequest) -> TaskInfo: ...
    async def delete(task_id: str, *, force: bool = False, cascade: bool = False) -> None: ...
    async def list(*, agent_name: str | None = None,
                       session_id: str | None = None,
                       status: TaskStatus | None = None,
                       tag: dict[str, str] | None = None,
                       source_type: str | None = None) -> list[TaskInfo]: ...
```

Semantic requirements:

- `get(task_id)` MUST return `None` for missing tasks (not raise).
- `update()` MUST honor the `if_match` field on the patch for CAS.
- `update()` payload MUST shallow-merge.
- `update()` tags MUST null-as-delete merge.
- `update()` attachments MUST null-as-delete merge (§23.1).
- `delete()` MUST be idempotent at the SCHEDULING level (multiple
  `.delete()` calls do not error). The provider's lower-level
  `provider.delete(task_id)` MAY raise `TaskNotFound` for already-
  deleted records; callers of the provider directly MUST handle
  this. The canonical Python implementation's hosted provider
  raises on 404 and the local provider raises on missing files;
  `MultiTurnTask.delete(task_id)` shields user code from these by catching
  "not found" substring matches and re-raising as `TaskNotFound`
  the first time, and being a no-op only at the user-facing
  `Task` surface.
- `list(...)` MUST filter server-side; framework relies on it.

`TaskCreateRequest` and `TaskPatchRequest` are simple structs
mirroring the writable subset of `TaskInfo` (plus `if_match`,
`lease_owner`, `lease_instance_id`, `lease_duration_seconds`).

### §28. Hosted provider (HTTP)

The hosted provider implements `TaskProvider` over HTTP against the
Foundry Task Storage service. Selected when the platform-supplied
environment variable `FOUNDRY_HOSTING_ENVIRONMENT` is set.

Key implementation notes:

- **API version:** Pinned at framework build time. The framework
  carries one `_API_VERSION` constant (current canonical value:
  `"v1"`) and passes it as the `api-version` query parameter on
  every request.
- **Authentication:** Bearer token from a `TokenCredential`
  resolved at request time. Scope is `https://ai.azure.com/.default`.
- **User-Agent:** Identifies the framework + version + runtime
  (`ai-agentserver-core/<version>`).
- **Custom error classification:** The provider classifies every
  non-success response into one of four labels and raises a typed
  `TransportClassifiedError(classification=<label>)`. The full
  classifier matrix:

| Condition | Label | Notes |
|---|---|---|
| HTTP 409 with body `error.code == "binding_mismatch"` | `evicted` | The agent's binding does not match the platform's view (orphan sandbox). Triggers the local-cleanup sequence. |
| HTTP 409 with any other body (or malformed body) | `conflict` | Generic lifecycle conflict. |
| HTTP 412 | `conflict` | Precondition / ETag mismatch. |
| HTTP 408, 429 | `transient` | Request timeout / rate limited — retryable. |
| HTTP 5xx | `transient` | Server-side error — retryable. |
| Network failure, socket timeout, connection reset | `transient` | Transport-level errors. |
| Body parse error (decode/JSON) on otherwise-success response | `transient` | Treated as transport-level. |
| HTTP 4xx other than 408/409/412/429 | `permanent` | Caller bug; do not retry. |

`evicted` is the most-load-bearing label: it gates the
local-cleanup sequence that prevents split-brain when the platform
has already evicted this sandbox in favor of another.

- **Body parsing (defensive):** The provider parses response bodies
  defensively — incomplete or non-JSON bodies do NOT crash the
  framework. Gzip decompression is performed manually (the SDK
  pipeline's `ContentDecodePolicy` is intentionally excluded so the
  provider controls decode error handling). When the body cannot be
  decoded or parsed, the provider raises a
  `TransportClassifiedError` carrying a `body_prefix` truncated to
  256 characters (`_BODY_PREFIX_LIMIT`) for operator triage. The
  prefix never contains bearer tokens or full response bodies.
- **ETag tracking on every write.** The provider remembers the
  most recent ETag returned by the server (from any GET, POST, or
  PATCH response) per task and includes it as `if_match` on every
  subsequent PATCH. This is what makes per-op 412 policy (§25.3)
  enforceable from the framework: the framework never has to ask
  the provider to "go fetch and then PATCH"; the provider already
  knows the current ETag. The hosted provider's local ETag cache
  is in-memory and per-process; cross-process correctness is
  provided by the server-side check itself (412 on mismatch).
- **Lease-extension piggyback.** Every PATCH carries an updated
  `lease.expires_at` (computed by the framework as `now +
  lease_duration`). The framework computes the renewal cadence
  dynamically by tracking when the last successful PATCH ran
  (§22 / §31).
- **Logging policy:** A custom `TaskApiLoggingPolicy` logs
  request/response method + URL + status + the same 256-char body
  prefix, with secrets redacted.
- **Required dependency:** A `TokenCredential` factory must be
  installed (e.g. via `azure-identity` in the Python implementation).
  The hosted provider does not function without a credential
  source.

### §28a. Field validation (shared between providers)

Every PATCH and CREATE write touches the same input-validation
surface, enforced identically by **both** providers. These rules are
the wire contract — the service rejects on the wire, the local
provider rejects pre-write so a developer running locally observes
the same failures they would observe deployed.

Violations raise an `invalid_request`-coded error (the framework
classifies these as `_HostedConflict` or a structured
`TaskPreconditionFailed` — see §39).

#### 28a.1 Field length and format

| Field | Constraint | Required on CREATE? |
|---|---|---|
| `id` | regex `^[a-zA-Z0-9_-]{1,128}$` | optional (provider generates if absent) |
| `agent_name` | length 1..128 after trim | yes |
| `session_id` | length 1..128 after trim | yes |
| `title` | length 1..256 after trim | yes |
| `description` | length 1..1024 after trim | optional |
| `suspension_reason` | length 1..256 after trim | only when status=suspended |
| Tag key | regex `^[a-zA-Z0-9_.\-]{1,64}$` | n/a |
| Tag value | length ≤ 256 chars | n/a |
| Tag entry count | ≤ 16 total entries | n/a |
| Attachment key | regex `^[a-zA-Z0-9_.\-]{1,64}$`, non-empty after trim | n/a (see §23.9) |

#### 28a.2 JSON-byte budgets

Sizes measured as UTF-8 byte length of canonical JSON
(`sort_keys=True`, separators `(",", ":")`).

| Bucket | Max bytes |
|---|---|
| `payload` (inline JSON) | 1 MB (1024 × 1024) |
| `error` (JSON dict) | 64 KB (64 × 1024) |
| `source` (JSON dict) | 4 KB (4 × 1024) |
| `attachments` per-value | 10 MiB (10 × 1024 × 1024) — see §23.7 |
| `attachments` total entries | 20 — see §23.7 |

Note: `payload` at 1 MB is intentionally narrower than the per-
input ceiling. The framework offloads large inputs / outputs into
`attachments` (§23) to lift each developer-observable input or
output to the 10 MiB per-attachment cap without consuming the
payload budget. The developer never sees this offload; they
observe an effective 10 MiB limit on `ctx.input` /
the handler's `return X` for the turn.

#### 28a.3 Source field validation

When `source` is supplied on CREATE, it MUST be a JSON object AND
contain a non-empty `type` field. Optional structured fields
(`routine_name`, `routine_run_id`, `dispatch_id`,
`action_correlation_id`, `created_at`, `updated_at`) are passed
through verbatim. Unknown fields are preserved (extension data).

`source` is immutable after CREATE (§24, immutable-fields list).

#### 28a.4 Error field validation

When `error` is supplied (PATCH), it MUST be a JSON object. The
provider requires `message` and `type` as non-empty strings; both
are part of the developer-observable structured-error envelope
(§39 — `TaskFailed.error`). The `code` field defaults to `"error"`
if not supplied.

#### 28a.5 Reserved-on-input status values

- Status `"failed"` is rejected on input. Failures are represented
  as `status="completed"` with a non-null `error` per §24 / §39.
- Status `"done"` is a legacy alias for `"completed"` — accepted on
  read and in list filters; the provider normalizes it to
  `"completed"` everywhere else. New code uses `"completed"`.

#### 28a.6 Immutable fields on PATCH

These fields are set at CREATE and reject any PATCH that includes
them:

`id`, `agent_name`, `session_id`, `title`, `description`, `source`.

PATCHes that include any of the above raise `invalid_request`. The
framework never patches them (they're set at create-time).

### §29. Local provider (file-backed)

Selected when `FOUNDRY_HOSTING_ENVIRONMENT` is NOT set (i.e. local
dev, tests). State lives under
`${AGENTSERVER_STATE_ROOT:-~/.agentserver}/tasks/<agent_name>/<session_id>/<task_id>.json`.
The state root is `AGENTSERVER_STATE_ROOT` (the single operator knob),
defaulting to `~/.agentserver`; the task subsystem owns the `tasks`
subdirectory beneath it (resolved via `resolve_state_subdir("tasks")`).

Implementation MUST:

- **Enforce every field-validation rule in §28a.** Local rejects on
  write the same way the service rejects on the wire — same
  regexes, length caps, byte budgets. A developer running locally
  must observe the same accept / reject decisions they would
  observe deployed.
- **Enforce the state-transition matrix (§24.1), terminal
  immutability (§24.2), and delete force semantics (§24.3).**
- **Enforce all lease write rules (§22.1)** — duration bounds,
  all-or-nothing triplet, conflict on different-owner takeover,
  EnsureLeaseMatches on `in_progress → pending`, lease renewal only
  on `in_progress`, force-expire mutual-exclusion with status
  transition, force-expire ownership check, expiry_count bump on
  expired-takeover, **`started_at` immutability across lease
  re-acquisition (set once on first `in_progress`; never updated by
  expired-lease reclaim, recovery takeover, or suspend/resume)**,
  `heartbeat_at` stamp on every lease write.
- **Enforce attachment validation (§23.9) and support the clear-all
  gesture (§23.10).**
- **Support list-filter parity (§31a)** — `has_error`, `lease_expired`,
  pagination via `after` cursor (plain `task_id` for local; opaque
  service token for hosted), `limit` (default 20, max 100), `order`
  asc/desc by `created_at`, reject `before`, normalize "done" →
  "completed" in the status filter, `agent_name` + `session_id`
  optional.
- Generate fresh ETags on every write (e.g. SHA of the JSON bytes).
- Reject `update()` calls whose `if_match` does not match the
  current ETag and raise `_HostedConflict(_code="etag_mismatch")` —
  the SAME internal classification the hosted provider produces on
  412.
- Apply `payload` PATCH semantics per §F1: when the patch value is
  a JSON object, shallow-merge into the current payload; for any
  other JSON type (array, string, number), full-replace; explicit
  `null` is a no-op (matches the service's `JsonValueKind.Null`
  branch).
- Apply `tags` null-as-delete merge, `attachments` null-as-delete
  merge (per-key) plus top-level clear-all per §23.10 — identical
  to the hosted provider's semantics.
- Apply status-transition side effects (§24.x); specifically:
  - `→ pending` clears the lease AND clears `suspension_reason`.
  - `→ in_progress` sets `started_at` if null AND clears
    `suspension_reason` AND clears `completed_at`.
  - `→ completed` clears the lease AND clears `suspension_reason`
    AND sets `completed_at` if null.
  - `→ suspended` clears the lease AND sets `suspension_reason`
    AND clears `completed_at`.
- Validate attachment size + count BEFORE writing (raise the
  internal `_AttachmentTooLarge` / `_AttachmentLimitExceeded` so
  the framework can re-raise as the developer-facing
  `InputTooLarge` per §39).
- Treat missing/corrupt files as `get() -> None`.
- Detect lease expiry against `expires_at` (UTC) and refuse renewal
  when an `if_match` mismatch indicates a competing process.
- **Bump the lease's `expiry_count` on every real lease handoff** (any
  reclaim where the prior lease's `expires_at` was past) — parity
  with the hosted server's behavior (§22). Without this, the
  developer-observable `LeaseInfo.expiry_count` is permanently
  stuck at 0 in local mode and tests asserting recovery behavior
  cannot use the local provider. The bump is part of the reclaim
  PATCH (it does NOT happen on a passive `get()` — `get()` is
  read-only).

The local provider does NOT spawn HTTP; it does NOT need an event
loop beyond the framework's; it has no network failure modes. It
has no concurrency: single-process operation means writes are
naturally serialized; `_HostedConflict(_code="lease_ownership_changed")`
(the service's Cosmos-race recovery code) is not reachable in
local and need not be raised by it.

### §30. Provider auto-selection

The framework decides at TaskManager construction time:

```
if env.get("FOUNDRY_HOSTING_ENVIRONMENT"):
    provider = HostedTaskProvider(...)
else:
    provider = LocalFileTaskProvider(...)
```

No developer opt-in / opt-out flag. This is intentional — code is
identical between local and hosted; the only thing that changes is
the storage backend selected.

### §31. Background loops

The framework runs THREE classes of background loops while the
manager is up:

| Loop | Cadence | Scope | Purpose |
|---|---|---|---|
| `_periodic_recovery_loop` | Every 300s (framework constant `_PERIODIC_RECOVERY_INTERVAL_SECONDS`). | Process-wide (one per manager). | Reclaim tasks that became reclaimable after cold-start. The `provider.list(...)` call passes `source_type=_SOURCE_TYPE` to scope to framework-owned tasks only. |
| `lease_renewal_loop` | Dynamic — half the lease duration (default 30s) computed against the per-task last-refresh time so a recent PATCH within the interval fully shadows the next tick. NOT a fixed cadence. | One per active task. | Renew the lease before expiry. |
| `_timeout_watchdog` | One-shot sleep for `min(remaining, timeout)` seconds. | One per active task that declares a timeout. | Set `ctx.timeout_exceeded` then `ctx.cancel` when budget expires. |

All loops are interruptible via cancel events and MUST exit cleanly
on `TaskManager.shutdown()`. The lease renewal loop additionally:

- **Computes its next tick dynamically** from the per-task
  last-refresh time recorded after every PATCH (renewal, metadata,
  steering, suspend, etc.). If a PATCH refreshed the lease 2s ago
  and the interval is 30s, the next tick is at +28s, not +30s
  from loop start. This makes the renewal loop's heartbeat
  PATCH-count drop to 0 in steady state when the task has any
  write traffic.
- After successful renewal (or when the heartbeat is shadowed),
  invokes an optional steering-poll callback that reads the
  steering queue and short-circuits the current turn if a new
  input has arrived since last drain.
- Signals an external cancel-event on 3 consecutive failures OR
  immediately on `evicted` classification.

The periodic recovery loop additionally:

- Passes `source_type=_SOURCE_TYPE` to `provider.list(...)` so the
  scan returns only framework-owned tasks. Foreign-typed records
  in the same `(agent_name, session_id)` scope are not picked up.
- Walks `task_info.attachments` for `steering_input_*` keys whose
  ref slot is no longer present in `pending_inputs` and PATCHes
  them away (orphan cleanup — defense in depth against a partial
  crash between an attachment add and the queue append).

### §31a. List filter parity (internal `list()`)

`Task._list()` is internal — not exported, no developer-facing
surface. Framework-internal callers (recovery scans, observability
shims) use `manager.list_tasks(...)` directly. The list operation's
filter and pagination surface MUST be identical between hosted and
local so internal call sites compose correctly across the two
backings.

**Filters** (every implementation MUST support these):

| Filter | Type | Semantics |
|---|---|---|
| `agent_name` | string \| None | Match exact. Optional — when null, no agent-scope filter applied. |
| `session_id` | string \| None | Match exact. Optional — when null, no session-scope filter applied. |
| `status` | string \| None | Match exact (after legacy `"done"` → `"completed"` normalization per §28a.5). |
| `source_type` | string \| None | Match `source.type` exact. |
| `tag` | list[(key, value)] \| None | Match all pairs (AND semantics). Each pair tested as exact equality. |
| `has_error` | bool \| None | When set, filter to (`true`) tasks with non-null `error` or (`false`) tasks with null `error`. |
| `lease_expired` | bool \| None | When set, filter to (`true`) tasks whose `lease.expires_at <= now` or (`false`) the opposite. |
| `lease_owner` | string \| None | Match `lease.owner` exact. |
| `omit_attachment_values` | bool | When true, returned tasks carry attachment keys with `None` values (skip per-row blob reads for paging through many tasks). Default false. |

**Pagination**:

- `limit` defaults to 20, max 100 (provider clamps over-cap to 100).
- `after` is an opaque cursor string. The local provider uses
  plain `task_id` (no Cosmos continuation-token concept). The
  hosted provider round-trips whatever opaque token the service
  returns (up to 4096 chars). Internal callers treat it as opaque
  regardless of which provider is underneath.
- `before` is **rejected** (forward-only cursor pagination — matches
  the service's explicit rejection per PR 2122040).
- `order` accepts `"asc"` or `"desc"`. Default `"desc"`. Sorts by
  `created_at`.

**Response**:

- `Data` — the page of tasks (or DTOs).
- `LastId` — the opaque continuation cursor to pass back as `after`
  on the next call; `None` when no more pages.
- `HasMore` — `true` when more pages remain.

---

## Part V — Public API surface

This part defines the language-agnostic shapes every implementation
MUST expose. Names are given in the Python style; idiomatic naming
in other languages is acceptable but the *behavior* and *parameters*
MUST match.

### §32. `task` and `multi_turn_task` decorators

The framework exposes **two decorators**. Each wraps an
`async def fn(ctx: TaskContext[Input]) -> Output` function and
returns a typed handle of a **distinct class**.

```
@task(
    name:    str,                       # REQUIRED
    title:   str | None = None,         # static; no callable factory
    timeout: timedelta | None = None,
    retry:   RetryPolicy | None = None,
)
async def one_shot(ctx: TaskContext[I]) -> O: ...
# → Task[I, O]

@multi_turn_task(
    name:      str,                     # REQUIRED
    title:     str | None = None,
    timeout:   timedelta | None = None,
    retry:     RetryPolicy | None = None,
    steerable: bool = False,            # opt-in steering queue
)
async def chain(ctx: TaskContext[I]) -> O: ...
# → MultiTurnTask[I, O]
```

Both decorators accept ONLY the kwargs listed. Unknown kwargs raise
`TypeError` at decoration time. `title` is a static string — the
callable-factory form is not accepted (rarely used, simpler surface,
cleaner type).

Per-decorator kwarg semantics:

| Kwarg | Meaning |
|---|---|
| `name` | **Required.** Stable identity for recovery routing — written to `source.name` and the `task_name` tag. Must be an explicit non-empty string; there is no function-derived default (deriving it from `func.__qualname__` would silently rebind identity on rename/move and strand in-flight tasks). Changing it strands existing tasks. |
| `title` | Human-readable title written to `TaskInfo.title`. |
| `timeout` | **Per-turn** cooperative wall-clock watchdog (§14). Defaults to **1 day** when unset; a supplied value may raise the budget up to **7 days, which is a hard ceiling** — a larger or negative value is rejected at registration (`ValueError`, fail-fast, not clamped). This caps a single uninterrupted handler invocation only; it is **not** a task-lifetime bound (a multi-turn chain lives indefinitely — the budget resets every turn; the task's overall lifetime is governed by the platform's 30-day sliding-TTL inactivity cleanup). When elapsed, the framework sets `ctx.timeout_exceeded` then `ctx.cancel`. |
| `retry` | `RetryPolicy` for handler-raised exceptions (§15). `None` (default) = no retry. |
| `steerable` | (`@multi_turn_task` only.) Enables `.start()` against an in-flight chain to queue a steering input instead of raising `TaskConflictError` (§12). |

There is no `ephemeral` kwarg. One-shot `@task` is **always**
ephemeral — the record is deleted on terminal exit. Multi-turn
`@multi_turn_task` is **never** ephemeral — the chain stays alive
in `suspended` between turns and is removed only via
`MultiTurnTask.delete(task_id)` (§35).

All decorator options are recovery-safe: after a crash the framework
only knows about the registered decorator's view. Per-call option
overrides are deliberately not supported.

The handler's first parameter MUST be named `ctx`. The framework
binds positionally, but it validates the name at decoration time so
guide examples and call sites stay consistent.

The two return classes (`Task[I, O]` and `MultiTurnTask[I, O]`)
are deliberately distinct (NOT a subclass relationship). The type
checker can therefore enforce "no `.delete()` on one-shot" and
"multi-turn `get_active_run` requires `(task_id, input_id)`"
statically.

#### Framework-owned constants exposed on this surface

| Constant | Value | Where it shows up |
|---|---|---|
| `_DEFAULT_LEASE_SECONDS` | `60` | Default lease TTL on `create`. |
| `_DEFAULT_MAX_PENDING_STEERING` | `9` | Maximum concurrent queued steering inputs. Hard-coded; not developer-tunable. |
| `_PERIODIC_RECOVERY_INTERVAL_SECONDS` | `300` | Cadence of the periodic recovery loop (§55). |
| `_INPUT_THRESHOLD_BYTES` | `200 * 1024` | Function-input promotion threshold (§23.2). |
| `_STEERING_THRESHOLD_BYTES` | `20 * 1024` | Steering-input promotion threshold (§23.2). |
| `_MAX_ATTACHMENT_SIZE_BYTES` | `2 * 1024 * 1024` | Per-attachment serialized cap (§23.7). |
| `_MAX_ATTACHMENTS` | `20` | Per-task attachment-entry cap (§23.7). |
| `_MAX_TASK_ID_LENGTH` | `256` | Max characters in `task_id` (§7). |
| `_VALID_TASK_ID_RE` | `^[a-zA-Z0-9\-_.:]+$` | Valid `task_id` regex (§7). |

These are framework invariants. Implementations in other languages
MUST use these exact values for byte-compatibility with the canonical
Python implementation; any value change would silently change
recovery / overflow behavior across processes that share a store.

### §33. `Task` (one-shot) and `MultiTurnTask` (multi-turn) handles

The two decorators produce two distinct classes. Their entry-point
signatures differ in identifier rules: one-shot `task_id` is
OPTIONAL (auto-generated as a GUID when omitted, per the 1:1
one-shot invariant `task_id == input_id`); multi-turn `task_id` is
MANDATORY (it identifies the chain).

```
class Task(Generic[Input, Output]):
    name: str

    async def run(
        self, *,
        input:            Input,
        task_id:          str | None = None,
        input_id:         str | None = None,
        if_last_input_id: str | None = None,
    ) -> Output: ...

    async def start(
        self, *,
        input:            Input,
        task_id:          str | None = None,
        input_id:         str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]: ...

    async def get_active_run(
        self, task_id: str,
    ) -> TaskRun[Output] | None: ...


class MultiTurnTask(Generic[Input, Output]):
    name: str

    async def run(
        self, *,
        task_id:          str,
        input:            Input,
        input_id:         str | None = None,
        if_last_input_id: str | None = None,
    ) -> Output: ...

    async def start(
        self, *,
        task_id:          str,
        input:            Input,
        input_id:         str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]: ...

    async def get_active_run(
        self, task_id: str, input_id: str,
    ) -> TaskRun[Output] | None: ...

    async def delete(self, task_id: str) -> None: ...
```

`.run()` blocks until the run / turn reaches a terminal-for-this-
caller state and returns the handler's `Output` directly, or raises
a typed exception (§39).

`.start()` returns immediately with a `TaskRun[Output]` handle the
caller can `await` (sugar for `.result()`), `await .result()` on,
or `.cancel()`. The handle's public surface is described in §35.

Both `.run` and `.start` accept the same `input_id` /
`if_last_input_id` chain primitives (§11). Implementations MUST
raise `TypeError` at the call site when `if_last_input_id` is
provided without `input_id`.

`get_active_run` looks up the currently-running run / turn:

- One-shot (`Task.get_active_run(task_id)`): (1) checks the
  in-process active-task table; if found, returns the bound
  `TaskRun`. (2) Otherwise consults the store via
  `provider.get(task_id)`. If the record exists with status
  `in_progress` and the lease is dead (per `_lease_is_dead`,
  §22), this method INLINE-RECLAIMS the task — same code path
  as `.start()`'s "reclaim sub-case" — and returns a `TaskRun`
  bound to the newly-spawned recovery execution. If the record
  does not exist OR status is not reclaimable from this
  process's perspective, returns `None`. Implementers SHOULD
  make this method idempotent against a recently-completed
  reclaim.
- Multi-turn (`MultiTurnTask.get_active_run(task_id, input_id)`):
  returns the in-flight handle iff the chain is currently
  running with the **exact** `input_id`; otherwise `None`. The
  required `input_id` argument prevents accidental cross-turn
  attach.

`MultiTurnTask.delete(task_id)` force-removes the chain: cancels
the in-flight turn (active caller's `.result()` resolves with
`TaskCancelled()`), resolves all queued steerer callers' futures
with `TaskCancelled()`, and force-deletes the record. Idempotent
(no-op if the chain is already gone).

There is no per-call override for `title` / `retry` / `steerable` /
`timeout` — all of those are decorator-configured for recovery
safety.

The `Task` class has **no** `.delete()` method. One-shot tasks
are always ephemeral; the framework deletes the persisted record
on terminal exit.

### §34. `TaskContext`

The single argument every handler receives. Read-only properties:

| Property | Type | Description |
|---|---|---|
| `input` | `Input` | The typed input value. |
| `task_id` | `str` | Task identity. |
| `input_id` | `str` | Per-turn input identity. For one-shot, defaults to `task_id` (1:1 invariant). For multi-turn, the framework auto-generates a GUID per turn unless the caller supplied one. |
| `entry_mode` | `"fresh" \| "resumed" \| "recovered"` | Why this turn started (§6). |
| `cancel` | event-like (`asyncio.Event` in Python) | Set when cancellation is requested for any reason. |
| `shutdown` | event-like | Set when the container is shutting down. Precondition for `exit_for_recovery()`. |
| `timeout_exceeded` | `bool` | True once the per-turn timeout fired. Set BEFORE `cancel` (§13 ordering invariant). Never reset within a turn. |
| `cancel_requested` | `bool` | True once external `TaskRun.cancel()` was called. Set BEFORE `cancel`. Never reset within a turn. |
| `pending_input_count` | `int` | Live count of currently queued steering inputs (multi-turn `steerable=True` only). Reads as `0` for non-steerable tasks AND for any provider failure (failure-tolerant). Computed on every access so it reflects inputs queued mid-handler. |
| `is_steered_turn` | `bool` | True iff this turn was constructed by the steering-drain code path. False otherwise. |
| `retry_attempt` | `int` | Cross-lifetime retry counter (§15). |

Public method:

```
async def exit_for_recovery() -> None: ...
```

`exit_for_recovery()` — see §16. MUST raise `RuntimeError` if
`shutdown.is_set() == False`; otherwise releases the lease without
writing a terminal status, leaves the task `in_progress`, and raises
`TaskDeferred` upward to the caller of `.result()`. The recovery
scanner re-invokes the handler with the persisted `payload["input"]`
in a future process lifetime.

`TaskContext` has NO `suspend()` method. Multi-turn handlers end a
turn with bare `return X`; the framework treats the return as an
implicit suspend (chain stays alive in `suspended`; caller's
`await run.result()` resolves to `X`).

The handler's first parameter MUST be named `ctx`. The framework
binds positionally, but it validates the name at decoration time so
guide examples and call sites stay consistent.

Implementations MUST NOT expose public setters for any cause boolean
or counter. They are framework-owned read-only fields.

### §35. `TaskRun`

The handle returned by `.start()`. Slim public surface:

| Member | Type | Description |
|---|---|---|
| `run.task_id` | `str` | Task identity. |
| `run.input_id` | `str` | Per-turn input identity. |
| `await run.result()` | `Output` | Block until terminal-for-this-caller; returns the handler's typed return value directly OR raises a typed exception (§39). |
| `await run.cancel()` | `None` | Signal cooperative cancellation. MUST set `ctx.cancel_requested = True` BEFORE setting `ctx.cancel` (ordering invariant — handler observing `ctx.cancel` is guaranteed to see at least one cause boolean already True). The handler picks the terminal shape. |
| `await run` | `Output` | Awaiting the run directly is sugar for `await run.result()`. |
| `run.is_queued` | `bool` | `True` when this handle represents a *queued* (not-yet-promoted) steering input on a steerable chain — i.e. `.start()` landed mid-turn and the input is awaiting drain — and `False` for a freshly-started or active run. The supported way to distinguish a queued steering handle from a fresh one; cancelling a queued run removes the queued slot and resolves `result()` with `TaskCancelled` without affecting the active turn. |

That is the entire surface. The handle deliberately has NO
`status` / `delete` / `refresh` / `lease_expiry_count`:

- Chain-level deletion uses `MultiTurnTask.delete(task_id)`.
- Read-only inspection of the persisted record goes through
  the task manager's provider (`await manager.provider.get(task_id)`
  returns the internal `TaskInfo`).
- Lease bookkeeping is framework-internal — developers don't
  observe it.

**`TaskRun` is NOT an async iterable.** It does not implement
`__aiter__` / `__anext__`; there is no `async for chunk in run`
syntax. Incremental streaming is a peer subpackage
(`azure.ai.agentserver.core.streaming`, Part VI), NOT a property
of the task handle. Producers emit to a `streams` registry id;
consumers attach via `streams.get(id).subscribe(after=...)`.

The two surfaces are decoupled because a stream may span multiple
task turns, multiple functions writing to the same id, or a
non-`@task` producer. Coupling stream iteration to `TaskRun`
would re-couple lifetime in ways the SOT intentionally avoids. Other-
language implementers MUST NOT add task-handle iteration as
"syntactic sugar" — it would re-introduce the very coupling we
removed. If a developer wants a single `await run` plus an
incremental stream, they explicitly attach to the streaming
registry (Part VI).


### §35a. Read-only inspection — internal

There is no `TaskSnapshot` type and no `Task.get(task_id)` method
on the public surface. Read-only inspection of a persisted task
record is done through the task manager's provider directly —
`await manager.provider.get(task_id)` returns the internal
`TaskInfo` envelope, which is the framework's own storage shape
(see §19). The public decorator surface stays small and
write-shaped on purpose: anything an external observer wants
about a task record is available on `TaskInfo`, and the framework
does not project a parallel "snapshot wrapper" onto the public
surface.

For active-execution inspection (attach to an in-flight run from
a different coroutine or request handler), use
`Task.get_active_run(task_id)` / `MultiTurnTask.get_active_run(task_id,
input_id)` — both return a `TaskRun` handle bound to the live
execution (or `None` if the task is not currently in flight in
this process and cannot be reclaimed inline).

### §36. `TaskRun.result()` returns `Output` directly

`await TaskRun.result()` (and equivalently `await task_run`)
resolves to the handler's typed return value of type `Output` —
no wrapper class, no envelope. Failure / cancellation /
deferral conditions surface as typed exceptions raised at the
`await` site (see §39).

There is no `TaskResult` wrapper class and no `Suspended` sentinel
on the public surface. Multi-turn handlers use a bare `return X`
to end a turn; the chain implicit-suspends and the caller's
`await run.result()` resolves to `X` directly. The framework does
not persist `X` anywhere in the task record — `X` lives only in
the in-process future the caller is awaiting.


### §37. Application state ownership

No task metadata facade is exposed on `TaskContext` or `TaskRun`.
Application durability is provided by `FoundryStateStore` and remains
independent from task leases and lifecycle transitions. See §17.

### §38. `RetryPolicy`

```
class RetryPolicy:
    initial_delay:        timedelta = timedelta(seconds=1)
    backoff_coefficient:  float     = 2.0
    max_delay:            timedelta = timedelta(seconds=60)
    max_attempts:         int       = 3
    retry_on:             tuple[type[Exception], ...] | None = None
    jitter:               bool      = True

    # Presets:
    @classmethod
    def exponential_backoff(cls, ...) -> RetryPolicy: ...
    @classmethod
    def fixed_delay(cls, delay: timedelta, ...) -> RetryPolicy: ...
    @classmethod
    def linear_backoff(cls, ...) -> RetryPolicy: ...
    @classmethod
    def no_retry(cls) -> RetryPolicy: ...
```

`max_attempts` counts total tries including the first (so
`max_attempts=3` means 1 original + 2 retries). `retry_on=None`
means retry every exception type; pass a tuple to scope. The delay
calculation is exponential by default; if `jitter=True`,
implementations MUST add randomized fractional jitter to avoid
synchronized retries across instances.

### §39. Error taxonomy

The public exception surface is seven types. Every developer-observable
condition the framework can signal surfaces through one of these. Each
carries only **new information** the caller doesn't already have (the
caller already knows the `task_id` they passed, and has `task_id` /
`input_id` on the `TaskRun` handle they hold); exceptions do not
redundantly carry `task_id`.

#### Outcome exceptions (raised from `.run()` / `TaskRun.result()`)

| Exception | Fields | When |
|---|---|---|
| `TaskFailed` | `error: TaskErrorDict \| TaskExhaustedRetriesErrorDict` | Handler raised an unhandled exception (or retries were exhausted). Inspect `error` for the structured diagnostic. |
| `TaskCancelled` | — (bare) | This run / turn was cancelled: cooperative `TaskRun.cancel()` honoured by the handler raising `CancelledError`; per-turn `timeout=` watchdog honoured the same way; queued steerer cancelled before promotion; `MultiTurnTask.delete()` invalidated an in-flight run. Multi-turn chains stay alive (queued steerers promote per §11); one-shot is gone. |
| `TaskDeferred` | — (bare) | Handler called `ctx.exit_for_recovery()` during shutdown. This lifetime is deferring — the task stays `in_progress` and the recovery scanner re-invokes the handler in a future process lifetime. Semantically DISTINCT from `TaskCancelled`. |

`TaskCancelled` MUST NOT inherit `asyncio.CancelledError` —
generic `except CancelledError` handlers would swallow it
silently, which is the wrong behavior for a task-level signal.

`TaskCancelled` and `TaskDeferred` carry **no fields**. Cancellation
causes can compound (e.g., `cancel_requested` AND `timeout_exceeded`
fire together) and the framework cannot deterministically pick a
single "reason" string. Causes are observable via the structured
failure log (§structured-logs) and via the handler-side cause
booleans on `TaskContext` (§34). For deferral, the meaning is
uniform — there is nothing to disambiguate.

`TaskFailed.error` is a `TypedDict`. The framework constructs one
of two shapes:

```
class TaskErrorDict(TypedDict):
    type: str         # exception class name, e.g. "ValueError"
    message: str      # str(exc)
    traceback: str    # traceback.format_exc()

class TaskExhaustedRetriesErrorDict(TypedDict):
    type: Literal["exhausted_retries"]
    attempts: int
    last_error: str
    last_error_type: str
    traceback: str
```

The `TaskFailed.error` field union is `TaskErrorDict |
TaskExhaustedRetriesErrorDict`; type-checkers can discriminate on
the `type` literal.

#### Pre-resolution exceptions (raised from `.run()` / `.start()`)

| Exception | Fields | When |
|---|---|---|
| `TaskConflictError` | `current_status: str` | `.run` / `.start` against a task in a state that can't accept the call: one-shot in_progress or completed; non-steerable multi-turn in_progress. `current_status` lets the caller distinguish in-flight (attach via `get_active_run`) vs. terminal (need a new `task_id` or accept the existing outcome). |
| `LastInputIdPreconditionFailed` | `actual_last_input_id: str \| None` | The `if_last_input_id` precondition does not match. Caller already knows what they passed via `if_last_input_id=`; `actual` is the new info. |
| `SteeringQueueFull` | — (bare) | Multi-turn `steerable=True` only. Steering queue at capacity. Caller backs off / surfaces 429. |
| `InputTooLarge` | — (bare) | Input write rejected because the serialized input exceeds the per-input cap. Caller shrinks or chunks the input. |

#### Net surface

Seven exceptions: `TaskFailed`, `TaskCancelled`, `TaskDeferred`,
`TaskConflictError`, `LastInputIdPreconditionFailed`,
`SteeringQueueFull`, `InputTooLarge`. Plus two `TypedDict`s
(`TaskErrorDict`, `TaskExhaustedRetriesErrorDict`) and the public
type alias `JSONValue` for the metadata value space.

#### Internal exceptions (NOT part of the public surface)

| Exception | Purpose |
|---|---|
| `TaskNotFound` | Internal classifier raised by the manager / provider when a record is missing. The public surface absorbs this: `MultiTurnTask.delete` is idempotent (no-op on missing record), `get_active_run` returns `None` on missing, and there is no `.get()` / `.refresh()` on `TaskRun`. Developers never catch `TaskNotFound`. |
| `TaskPreconditionFailed` | Internal precondition-failure base. Specific precondition failures get their own typed subclass (e.g., `LastInputIdPreconditionFailed`); the bare base is not exported. |
| `EtagConflict` | Optimistic concurrency conflict at the provider boundary. Framework retries internally; only escapes for low-level callers manipulating etags directly. |
| `_HostedConflict(_code: str, status_code: int, ...)` | Single internal type the hosted provider's response classifier raises for service responses with a structured error code. The framework matches on `_code` to dispatch (see §39.1). The local provider raises the same type with the same `_code` directly, so internal call-site code is provider-agnostic. |
| `_AttachmentTooLarge` / `_AttachmentLimitExceeded` | Provider-internal cap-violation signals. Framework catches at attachment-write sites and re-raises as `InputTooLarge` (input writes) based on the attachment-key prefix. |
| `TransportClassifiedError(classification: "transient" \| "evicted" \| "conflict" \| "permanent")` | Hosted provider's classification wrapper around lower-level HTTP failures. Internal to hosted provider; framework dispatches on `classification`. |

The underscore prefix on `_AttachmentTooLarge` /
`_AttachmentLimitExceeded` / `_HostedConflict` is the Python-canonical
signal for "package-private; never imported by developer code." Other-
language implementations MUST place the equivalent exceptions at
package-private visibility — never as documented developer-facing
types.

#### 39.1 Service error codes → internal `_HostedConflict` → developer-facing

The hosted task service emits distinct error codes per condition.
The hosted provider's response classifier wraps each in
`_HostedConflict(_code=...)`. The framework's lifecycle code then
matches on `_code` and either retries silently or translates into
a developer-facing exception. The local provider raises the same
`_HostedConflict(_code=...)` directly so the framework's dispatch
table works against either backing.

| Service `code` | HTTP | When emitted | Framework action |
|---|---|---|---|
| `task_immutable` | 409 | PATCH on a `completed` task (except no-op completed → completed) | Translate → `TaskConflictError(current_status="completed")`. |
| `invalid_state_transition` | 409 | PATCH whose declared status transition is not in §24.1 matrix | **Framework bug** — the framework drives transitions, not the developer. Log + raise `RuntimeError`. |
| `lease_held_by_another` | 409 | Lease acquisition / renewal against a record whose lease is held by a different owner (and not expired) | Translate → `TaskConflictError(current_status="in_progress")`. |
| `task_already_exists` | 409 | CREATE on an existing `task_id` | Framework's lifecycle resolution branches on existing task; this only escapes if the framework's `.start()` race-resolution path is broken. Translate → `TaskConflictError(current_status=<observed status>)`. |
| `lease_ownership_changed` | 409 | Service Cosmos race: between read and write, another owner stole the lease | Hosted-only. Treat as `lease_held_by_another`. |
| `etag_mismatch` | 412 | If-Match precondition failure | **Retry** with re-read (transparent to developer); after bounded retries exhausted, escape as `EtagConflict` (internal — only escapes to low-level callers). |
| `invalid_request` | 400 | Any field-validation violation (§28a) or lease-rule violation (§22.1) or delete-without-force on non-terminal (§24.3) | Translate → internal `TaskPreconditionFailed`. For the specific `if_last_input_id` mismatch, translate → `LastInputIdPreconditionFailed(actual_last_input_id=<stored>)`. |

**Zero new developer-visible exception types from this table.**
All translation targets above are either in the seven-name public
surface or are internal types absorbed before reaching developer
code. The internal `_HostedConflict._code` strings never appear in
developer code, error messages, docstrings, or exported names —
they are pure dispatch keys.

---

## Part VI — Streaming primitive

### §40. Why streaming is decoupled from `@task`

Streaming is a **separate, peer subpackage** of
`azure-ai-agentserver-core` — it does not nest under `@task`. Three
reasons:

1. **Lifecycle.** A stream can span multiple `@task` invocations
   (multi-turn / multi-function fan-in); coupling its lifetime to a
   single handler's body breaks reconnection on multi-turn UIs.
2. **Polymorphism.** The same protocol is used by handlers that
   are not `@task` decorated (plain handlers, HTTP layer, ad-hoc
   producers).
3. **Pay-only-for-what-you-use.** Handlers that don't stream pay
   nothing: no buffer, no factory, no registry tombstone.

The decorator carries NO streaming-related kwarg. `TaskContext`
has NO streaming attribute. Handlers that want to stream do this
explicitly:

```python
from azure.ai.agentserver.core.streaming import streams

stream = await streams.get_or_create(stream_id)
await stream.emit({"event": "progress"})
...
await stream.emit(final_chunk, close=True)
```

### §41. `EventStream` protocol

The data-flow surface (lifecycle is the registry's job, §42).

```
class EventStream(Protocol):
    async def emit(payload: Any, *, close: bool = False) -> None: ...
    async def close() -> None: ...
    def subscribe(*, after: int | None = None) -> AsyncIterator[Any]: ...
    async def last_cursor() -> int | None: ...
```

Method contracts:

- **`emit(payload, close=False)`** — multicast `payload` to all
  currently-attached subscribers. The framework never inspects,
  validates, or rewrites the payload. If `close=True`, the emit
  and the close-of-stream are **observably atomic for currently-
  attached subscribers**: every subscriber attached BEFORE this
  call sees BOTH the payload AND the end-of-stream signal.
  Late-subscriber behavior depends on backing:
  - **Live-only backings** (`BroadcastEventStream`): late
    subscribers see neither the payload nor any earlier history.
  - **Replay backings** (`ReplayEventStream`,
    `FileBackedReplayEventStream`): late subscribers may replay
    the buffered payload (including the one delivered with
    `close=True`) AND then terminate cleanly, subject to TTL
    eviction (§46).

  Raises `EventStreamClosedError` if already closed,
  `EventStreamNotFoundError` if destroyed.

- **`close()`** — transition active -> closed. **Idempotent**:
  calling on already-closed or destroyed stream is a no-op (never
  raises). Subscribers attached at close drain remaining items
  then their iterators terminate cleanly.

- **`subscribe(after=N)`** — return an `AsyncIterator` over
  payloads. NOT a coroutine: do not `await` it; immediately use it
  with `async for` / `aiter()` / `anext()`. If `after=N` is
  supplied AND the active backing supports cursored replay,
  yield only payloads whose cursor value is strictly greater than
  `N`; backings without cursor support silently ignore non-`None`
  values. Raises `EventStreamNotFoundError` synchronously at the
  call site if the stream is destroyed.

- **`last_cursor()`** — return the highest cursor seen so far, or
  `None`. While active: highest persisted cursor (`None` if zero
  emits or backing has no cursor support). After close: the last
  cursor seen even if those events have since been TTL-evicted —
  this is load-bearing for the file-backed replay's rehydration
  path. After destroy: raises `EventStreamNotFoundError`.

  `last_cursor()` is a **read-only watermark query**. It does NOT
  trigger the destroy transition (which is driven by the TTL-since-
  close clock, §46). Implementations MUST keep it side-effect-free.

  `last_cursor()` is the EMITTER's recovery primitive. It is NOT
  the workflow-recovery primitive — workflow watermarks belong in an
  application-owned State Store, never in stream cursors.

### §42. The `streams` registry

A process-level singleton that owns the lifecycle of all SDK-bundled
`EventStream` instances:

```
streams.use_in_memory_live()                                    # configurator (sync)
streams.use_in_memory_replay(cursor_fn=..., ttl_seconds=...)    # configurator (sync)
streams.use_file_backed_replay(cursor_fn=...)                   # configurator (sync)
#   all kwargs optional: storage_dir defaults to
#   resolve_state_subdir("streams"); ttl_seconds defaults to 600 (10 min);
#   serializer/deserializer default to JSON. Explicit args override.

await streams.get(id)                  # raises NotFound if never registered
await streams.get_or_create(id)        # atomic per id
await streams.delete(id)               # idempotent; installs tombstone
```

Six methods total: three sync configurators + three async
lifecycle methods.

Atomicity: `get_or_create(id)` MUST be safe under concurrent
callers. The implementation uses a per-id lock to prevent
split-brain construction when two coroutines race to create the
same id. The lock is acquired only on the slow path (first
access for an id); subsequent `get_or_create` calls return the
cached instance without taking the lock.

Tombstones: `delete(id)` causes the next `get(id)` against that
id to raise `EventStreamNotFoundError`. The registry uses an
internal "destroyed" marker to remember the deletion (the
"delete is symmetric with `rm -f` but still leaves a marker"
rule), but the **error surface is unified**: every "the id is
not currently a live stream" condition raises
`EventStreamNotFoundError`. This covers all three paths
into the missing-stream state:

- the id was never registered;
- the id was registered and then explicitly `delete(id)`d;
- the id was registered, then transitioned to Closed, then the
  TTL-since-close clock elapsed (§46) and the registry
  auto-tombstoned the id.

The next `get_or_create(id)` against a tombstoned id clears the
tombstone and constructs a fresh stream.

Note: `get(id)` does NOT itself install a tombstone — only
`delete(id)` and the TTL-since-close auto-transition do.

Why this is one error type:

The previous design distinguished `EventStreamGoneError` (the
resource once existed and is destroyed) from
`EventStreamNotFoundError` (the resource was never registered).
That distinction has no actionable value at the consumer:
either way, the right behavior is the same (subscribe to a new
id, or treat this id as missing). It also leaked the registry's
internal bookkeeping (tombstone vs no-tombstone) into the
developer-facing API. Collapsing into a single
`EventStreamNotFoundError` makes the rule one-line: "any
attempt to use an id that is not currently a live stream raises
`EventStreamNotFoundError`."

#### Process-wide factory selection

Each `use_*` configurator replaces the registry's stream factory
**globally for the process**. Subsequent `get_or_create(id)` calls
use the new factory; existing stream instances are unaffected.
Configurators are synchronous and idempotent. The default factory
(if no configurator is called) produces `BroadcastEventStream`
instances.

This makes "configure once at app startup, use everywhere"
trivial: a single `streams.use_in_memory_replay(ttl_seconds=600)`
at process init is the complete configuration step. There is no
per-stream factory override on `get_or_create`.

### §43. Stream lifecycle states

Every concrete `EventStream` instance has exactly **two** states:

```
              emit*
            ┌──────────┐
            │          │
            ▼          │
┌──────────────────┐   │   ┌─────────────────┐
│      Active      │ ──┴── │      Closed     │
└──────────────────┘       └─────────────────┘
        │                          │
        │                          │
        │                          │  (then: registry tombstones
        │                          │   the id on delete() or
        │                          │   TTL-since-close elapse —
        │                          │   see §42, §46. The next
        │                          │   get(id) raises
        │                          │   EventStreamNotFoundError.)
        └─── delete() ─────────────┘
```

State semantics:

- **Active.** Accepts `emit` and `subscribe`. Always-the-initial
  state on construction. `close()` -> Closed (idempotent on
  already-closed). `delete()` removes the instance from the
  registry and tombstones the id; subsequent `get(id)` raises
  `EventStreamNotFoundError`.
- **Closed.** `emit` raises `EventStreamClosedError`.
  `subscribe()` still works for replay backings (yields drained
  history, then terminates cleanly when buffer is exhausted or
  TTL-since-close elapses). `last_cursor()` still works.
  `close()` is a no-op. `delete()` removes the instance from
  the registry and tombstones the id.

There is **no per-instance "destroyed" state** — destruction
happens at the registry level. The framework tracks an instance
as Active or Closed; once the registry tombstones the id, the
instance reference is dropped and any cached reference held by
a caller is stale (further operations on it raise
`EventStreamNotFoundError` because the registry routes the call
to a tombstoned id).

The TTL-since-close auto-transition (§46) governs when the
registry decides to tombstone a Closed stream's id. For replay
backings constructed with `ttl_seconds`: once the stream is
closed, the framework starts a `close_time + ttl_seconds`
clock; when it elapses, the registry tombstones the id. This is
deterministic (time-based, not buffer-state-based) and works
whether or not anyone is currently subscribed.

`BroadcastEventStream` (live-only) and any other backing
constructed without `ttl_seconds` do NOT auto-tombstone; they
only tombstone via explicit `delete(id)`.

### §44. Concrete backings

Three SDK-bundled implementations:

| Backing | Use case | Behavior |
|---|---|---|
| `BroadcastEventStream` | Live consumers attach before the producer starts. | No buffer. `subscribe(after=...)` is accepted but the `after` argument is silently ignored. Late subscribers miss earlier events. `subscribe()` returns an iterator over events emitted AFTER attach. Multi-subscriber (each gets a private cursor/queue). Goes away ONLY via explicit `delete(id)` — no TTL auto-tombstone. |
| `ReplayEventStream` | Late subscribers need history. | Per-stream buffer retains all events. `subscribe(after=N)` is honored iff `cursor_fn` was supplied to the configurator; otherwise `after` is ignored. `ttl_seconds`, if supplied, drives per-event eviction (regardless of Active/Closed — events older than `now - ttl_seconds` are evicted from the buffer; see §46). When Closed AND `close_time + ttl_seconds` elapses, the registry auto-tombstones the id. |
| `FileBackedReplayEventStream` | Crash-recoverable history (multi-turn UIs, resilient response streaming). | Persists each emit to `storage_dir/<filename>.jsonl` (id sanitized per the C-STR-FBR-1 filename-safety rule). **Constructor rehydrates** from an existing file if present — restart-safe. Same per-event TTL + close-clock semantics as `ReplayEventStream`. Optional `serializer: Callable[[Any], bytes]` and `deserializer: Callable[[bytes], Any]` for non-JSON payloads (default JSON). `delete()` (and TTL-since-close auto-tombstone) clean up the file BEFORE the registry tombstones the id. |

Per-backing TTL + tombstone matrix:

| Backing | Per-event TTL eviction | Close-clock tombstone |
|---|---|---|
| `BroadcastEventStream` | N/A (no buffer) | Never (no `ttl_seconds`) |
| `ReplayEventStream` (no `ttl_seconds`) | Never (events live forever in buffer) | Never (no clock) |
| `ReplayEventStream` (with `ttl_seconds=T`) | Active OR Closed: events older than `now - T` evicted from buffer | Closed AND `now > close_time + T` -> registry tombstones id |
| `FileBackedReplayEventStream` (no `ttl_seconds`) | Never | Never |
| `FileBackedReplayEventStream` (with `ttl_seconds=T`) | Same as above; file truncated when events evicted | Same as above; file removed BEFORE tombstone |

Constructor selection happens through the registry's
configurators (`use_in_memory_live()`, etc.) — application code at
startup picks the backing once and `streams.get_or_create(id)`
constructs that kind of stream from then on.

Switching backings mid-flight is allowed (configurator calls are
idempotent; subsequent `get_or_create` uses the new factory) but
existing stream instances are unaffected.

### §45. Cursor and `subscribe(after=...)`

A cursor is a strictly increasing integer extracted from each
payload via a developer-supplied `cursor_fn: Callable[[payload], int]`
passed to the configurator. The framework:

- Never assumes the payload has any particular field
  (`sequence_number`, `event_id`, etc.).
- **Designed for `int` cursors** (string cursors introduce the
  silent-wrong-comparison footgun — `"10" > "9"` is False).
  **Known gap (canonical Python implementation):** the registry
  does NOT validate the return type of `cursor_fn` at construction
  or use time; an implementation that returns non-int values will
  silently mis-compare. Other-language implementers SHOULD add the
  validation (`cursor_fn(sample) is int`) at configurator time so
  the failure is loud, not silent.
- Uses `cursor_fn` lazily: only when `subscribe(after=...)` is
  called or `last_cursor()` is asked.

Replay backings without a `cursor_fn` accept `subscribe(after=N)`
calls but silently ignore the `after` argument and yield the full
retained history.

### §46. TTL eviction and the close-clock (replay backings)

When constructed with `ttl_seconds=T`, replay backings:

**Per-event eviction** (runs regardless of Active/Closed):

- Stamp each emitted event with an `emit_time`.
- Evict events whose age >= `T`, on `emit()` and `subscribe()`.
  The buffer never holds events older than `T` once an operation
  triggers an eviction sweep.

This rule is what bounds long-running active streams that emit
continuously for hours or days — the buffer's memory footprint is
proportional to the emit-rate × `T`, not to the total duration.
Without per-event TTL on active streams, a multi-day producer
would buffer indefinitely.

**Close-clock auto-tombstone** (Closed only):

- When the stream transitions to Closed, the framework records
  `close_time` and starts a wall-clock countdown for `T`.
- When `now >= close_time + T`, the registry tombstones the id
  (file-backed: removes the file FIRST). The next `get(id)` raises
  `EventStreamNotFoundError`.

Why a close-clock, not "buffer empty + at least one emit":

- The previous design ("Closed AND buffer empty AND
  `total_emit_count > 0`") was observer-driven (the check fired
  on `emit()` or `subscribe()`), required `total_emit_count > 0`
  to avoid a fast-path on never-emitted streams, and explicitly
  excluded `last_cursor()` from the check. All of that complexity
  came from trying to derive a destroy moment from buffer state.
- The close-clock is **time-deterministic**: from
  `close_time + T` onward, the id is tombstoned regardless of
  who is observing. There is no "buffer briefly not empty when
  the destroy fires" corner case to reason about, because for
  every event in the buffer, `emit_time <= close_time`, so
  `emit_time + T <= close_time + T`. By the time the close-clock
  fires, every per-event TTL has already elapsed and every event
  has been evicted on the next eviction sweep. The two rules are
  consistent by construction.
- It eliminates the `total_emit_count > 0` carve-out: a stream
  that was created, closed, and never emitted to behaves like
  any other Closed stream — it tombstones at `close_time + T`.
  No special-case for empty-emit streams.
- Subscribers attached just before close drain naturally (their
  iterators terminate when the buffer is exhausted), and any
  late subscriber arriving between `close_time` and
  `close_time + T` can still replay the (possibly TTL-thinned)
  history. After `close_time + T`, the id is gone.

Implementation note: implementations MAY drive the close-clock
either via a wall-clock timer (best for hosted/long-lived
processes) or via an opportunistic check on `get(id)` / `emit()`
/ `subscribe()` (best for tests). Either approach yields the same
observable behavior: subscribers always raise
`EventStreamNotFoundError` at or after `close_time + T`.

`last_cursor()` continues to work in the Closed state even after
all events have been evicted — it returns the last cursor the
backing ever saw, NOT the current buffered max. This is required
for the rehydration path (a process restarting picks up the
high-water mark for resuming a not-yet-tombstoned stream).

### §47. Streaming error taxonomy

```
EventStreamError                     # base
  ├── EventStreamClosedError         # emit on closed stream
  └── EventStreamNotFoundError       # any "id is not currently a
                                     #   live stream" condition —
                                     #   never registered, deleted,
                                     #   or close-clock elapsed
```

Wire mapping (informative — HTTP plumbing is in callers, not the
framework):

| Exception | Suggested HTTP status |
|---|---|
| `EventStreamClosedError` | 5xx (this is a server-side bug — the producer kept emitting after closing). |
| `EventStreamNotFoundError` | 404 Not Found. |

#### Consolidated: when is `EventStreamNotFoundError` raised?

`EventStreamNotFoundError` is the single error type for every
"the id is not currently a live stream" condition. It fires for
**three independent reasons**, all surfaced as the same
exception:

| Path to NotFound | Broadcast (live) | Replay (in-memory) | Replay (file-backed) |
|---|---|---|---|
| 1. `get(id)` for an id that was never registered. | ✓ | ✓ | ✓ |
| 2. Explicit `streams.delete(id)` → instance removed + registry tombstones the id. Works in ANY state (Active or Closed). | ✓ | ✓ | ✓ (file removed before tombstone) |
| 3. Closed stream's close-clock elapses (`now >= close_time + ttl_seconds`) → registry tombstones the id. Requires the backing to have been constructed with `ttl_seconds`. | ✗ (no TTL) | ✓ | ✓ (file removed before tombstone) |

Key invariants to take away:

- `BroadcastEventStream` NEVER auto-tombstones — it has no TTL
  machinery. The ONLY path is explicit `delete()`.
- For replay backings, the close-clock fires deterministically at
  `close_time + ttl_seconds`. There is no `total_emit_count > 0`
  carve-out and no buffer-state condition; a stream created,
  closed, and never emitted to behaves like any other Closed
  stream — tombstoned at `close_time + ttl_seconds`.
- Per-event TTL runs regardless of Active/Closed, on `emit()` and
  `subscribe()`. This is what bounds buffer memory for long-lived
  active streams.
- `last_cursor()` is side-effect-free — it does not trigger the
  close-clock check, does not evict events, and does not
  tombstone. It returns the high-water mark seen so far.
- Once the registry tombstones an id, any stale instance
  reference held by a caller raises `EventStreamNotFoundError`
  on the next operation (the operation is routed through the
  registry, which sees the tombstone).

### §48. Third-party stream-impl pattern

The `streams` registry owns ONLY the three SDK-bundled backings.
Third-party `EventStream` implementations ship their OWN peer
registry (don't try to plug into `streams`). This keeps each
registry's tombstone/factory state local.

Consumers can hold references to any `EventStream`-shaped instance
— the registry-vs-not distinction is invisible to consumers.

The `EventStream` Protocol does NOT include a destructive method
(no `destroy` / `dispose` on the Protocol itself); destruction
lives on the registry. Third-party registries SHOULD follow the
same pattern: keep destruction off the data-flow Protocol.

---

## Part VII — Implementation guidance (algorithms)

This part sketches the framework's load-bearing algorithms in
language-agnostic pseudocode. Implementations MAY structure the
control flow differently as long as the externally-observable
behavior matches. References in brackets are to the source files
in the canonical Python implementation.

### §49. Cold-start sequence

On `TaskManager.startup()`:

```
1. Register every decorator-discovered function into the resume-callback
   table, keyed by source.name. [_REGISTERED_DESCRIPTORS]
2. Resolve self.owner and self.instance_id from env (§7).
3. Call self._recover_stale_tasks() — list tasks via:
       provider.list(agent_name = self.agent_name,
                     session_id  = self.session_id,
                     status      = "in_progress",
                     lease_owner = self.owner,
                     source_type = _SOURCE_TYPE)   # framework-only scope
   For each result:
     a. Look at lease.owner and lease.instance_id.
     b. If lease.owner != self.owner: skip (not ours). [Practically
        unreachable because the filter already restricts to our
        owner; defensive.]
     c. If lease.owner == self.owner AND lease.instance_id == self.instance_id:
        skip (would be impossible in a fresh process; defensive).
     d. Otherwise (same-owner different-instance OR expired):
        — Call self.steering_cleanup_orphan_attachments(task_info)
          (§58) to clean up any orphan steering_input_* attachments
          left by a partial crash.
        — Call self._reclaim_one(task_info) — PATCH lease to self
          with if_match=etag, then invoke the registered resume
          callback with entry_mode='recovered', re-hydrated input,
          and metadata. On 412: ABANDON (the next scan re-evaluates).
4. Spawn _periodic_recovery_loop() as a background task.
5. Return.
```

The cold-start scan blocks `startup()` until done — handlers
intended to be recovered must be visible before any HTTP route goes
live. Implementers exposing the framework over HTTP MUST gate
route binding on `startup()` having returned.

### §50. `.start()` lifecycle resolution

The framework's most-complex decision tree. On `Task.start(task_id, input, ...)`:

```
1. Validate task_id (§7).
2. Read task store for task_id (single GET).
3. Compute lifecycle action:

     - If GET returned None (task not found):
         -> CREATE
     - If status == 'pending':
         -> ADOPT (rare; transition to in_progress)
     - If status == 'suspended':
         -> RESUME (transition to in_progress with new input;
                    clears prior output — see §11, §23.8 item 8)
     - If status == 'completed':
         -> RAISE TaskConflictError(current_status='completed')
     - If status == 'in_progress':
         If lease is dead (expired OR same-owner different-instance):
             -> RECLAIM-AND-INVOKE (transition to in_progress with same owner, new instance)
         Else if task is steerable AND in-process active execution exists for task_id:
             -> STEERING-APPEND (queue input; do NOT enter handler)
         Else:
             -> RAISE TaskConflictError(current_status='in_progress')

4. Execute the chosen action via the appropriate transition PATCH.
   For RESUME, the PATCH MUST be a single co-PATCH carrying:
     - status: 'in_progress'
     - payload['input']: new serialized input (inline or ref)
     - payload['turn_started_at']: utc_now_iso()
     - payload['retry_attempt']: 0   (fresh retry budget for the resumed turn)
     - attachments['_input']: new value (or absent if inline)
5. If action ∈ {CREATE, ADOPT, RESUME, RECLAIM-AND-INVOKE}:
     Spawn lease_renewal_loop, watchdog (if timeout configured), execute_task_loop.
     Return a TaskRun bound to this execution.
6. If action == STEERING-APPEND:
     Return a TaskRun whose .result() resolves with the NEXT-TURN outcome
     (the queued steerer is bound to the next turn).
```

The reclaim sub-case includes input precondition validation
(`if_last_input_id`) before the transition PATCH.

The framework does NOT write `payload["output"]` on any
transition. The handler's return value resolves the in-process
caller's `TaskRun.result()` future and is never projected onto
the chain record.

### §51. Steering append (atomic)

When `.start()` resolves to STEERING-APPEND, the framework
executes this PATCH as a single round-trip:

```
1. Read current payload (already in memory from the lifecycle GET).
2. steering   = payload.get('steering', {})
3. pending   = list(steering.get('pending_inputs', []))
4. If len(pending) >= 9: raise SteeringQueueFull.
5. serialized = canonical_json(input)
6. If size(serialized) > 20 KiB:
     next_seq = steering.get('next_input_seq', 0)
     key      = f'steering_input_{next_seq}'
     ref      = {'__attachment_ref__': {'key': key, 'hash': sha256(serialized)}}
     pending.append(ref)
     steering['next_input_seq'] = next_seq + 1
     attachments_patch = {key: input}
   else:
     pending.append(input)         # raw inline
     attachments_patch = None
7. steering['pending_inputs']   = pending
   steering['cancel_requested'] = True
8. payload_patch = {'steering': steering}
   if input_id provided: payload_patch['last_input_id'] = input_id
9. PATCH(task_id, payload=payload_patch, attachments=attachments_patch,
        lease_owner=self.owner, lease_instance_id=self.instance_id,
        lease_duration_seconds=60, if_match=etag)
10. Locally: signal the active execution's ctx.cancel via the in-process
    context registry (no remote signal needed — the active execution
    is in this process).
```

The PATCH MUST carry both `payload` and `attachments` (when
promoted) so the queue entry and its backing attachment are added
in the same etag transaction.

### §52. Steering drain (two-phase, two-PATCH)

At every turn-end boundary (suspend, complete, raise), if there
are queued steering inputs, the framework drains the head and
re-enters the handler. The drain is two-phase AND two-PATCH to be
crash-safe — `drain_in_progress=True` between the two PATCHes is
the breadcrumb recovery uses to know "we are mid-drain":

```
Phase 1 — "Drain start" PATCH (atomic across payload + attachments):
  1. Read current task record (we need etag, payload, attachments).
  2. steering = dict(payload['steering'])
  3. pending  = list(steering['pending_inputs'])
  4. If pending is empty: return None (no drain happens; caller
     proceeds to suspend/complete normally).
  5. next_entry  = pending.pop(0)
  6. attachments_patch = {}
  7. If next_entry is a ref (§23.3):
        attachments_patch[ref_key(next_entry)] = None    # delete attachment
        active_input_value = read attachment at ref_key  # resolve via _read_input_value
     else:
        active_input_value = next_entry
  8. steering['active_input']      = active_input_value
  9. steering['pending_inputs']    = pending
 10. steering['drain_in_progress'] = True
 11. steering['cancel_requested']  = len(pending) > 0     # more pending => keep advisory
 12. payload['steering']          = steering
 13. payload['turn_started_at']   = utc_now_iso()        # fresh turn-start boundary
 14. PATCH(task_id, status='in_progress', payload=payload,
        attachments=attachments_patch, lease piggyback, if_match=etag)

     [NB: status MUST be set to 'in_progress' in this PATCH. The turn-end
      boundary that triggered the drain already wrote status='suspended'
      (multi-turn return/raise => suspended; see §12). The drain starts a
      NEW turn, so it reclaims the record suspended->in_progress. This is
      ALSO required for correctness of the lease piggyback: the task store
      rejects a lease *renewal* on a non-in_progress task ("lease renewal is
      only supported for in_progress tasks") but ACCEPTS lease params as part
      of a suspended->in_progress *claim*. Omitting the status flip makes the
      Phase-1 PATCH 409 and the steered turn never runs.]

     [NB: Phase 1 does NOT set payload['input'] or write a ref/attachment
      for active_input. Only the in-memory ctx receives the value (Phase 2).
      Recovery from a crash BETWEEN Phase 1 and Phase 3 reads
      steering['active_input'] as the source of truth for the input,
      via the race-recovery contract.
      No output co-clear is needed — the framework does not write
      payload['output'] / output attachments on any transition.]

Phase 2 — Handler re-entry (in-memory only):
 15. Construct a fresh TaskContext with:
       entry_mode='resumed', is_steered_turn=True,
       input=active_input_value (deserialized via input_type),
       metadata reused from previous ctx,
       cancel_event=fresh (re-set if cancel_requested still True),
       retry_attempt=0.
 16. Update the in-process _ActiveTask.context pointer.
 17. Invoke the handler with the new ctx.

Phase 3 — "Drain end" PATCH (after handler re-entered):
 18. steering['drain_in_progress'] = False
 19. payload['steering']          = steering
 20. payload['retry_attempt']     = 0     # Drain resets retry budget
 21. PATCH(task_id, payload=payload, lease piggyback)
     (No attachments touched in Phase 3.)

Phase 4 — On the next turn-end:
 22. The handler returns/suspends/raises. The terminal handler clears
     active_input as part of its suspend/complete PATCH (§53).
```

**Race-recovery contract.** If the process crashes:

- **Between Phase 1 PATCH and Phase 2 handler entry:** recovery
  reads `drain_in_progress=True` and `active_input != null` and
  re-enters with `is_steered_turn=True` using `active_input` as
  the input.
- **Between Phase 2 handler entry and Phase 3 PATCH:** same — the
  new ctx is in-memory only; recovery re-enters from `active_input`.
- **After Phase 3 PATCH:** `drain_in_progress=False`. Recovery
  treats the task as a normal mid-turn task; reads `payload['input']`
  if set (typically null at this point — the handler has not yet
  written a turn-start input) and re-enters as a normal recovery.

**Atomicity note for Phase 1.** "Single PATCH" here means one
HTTP round-trip carrying BOTH the payload and the attachment
changes. The hosted store applies both atomically against the
etag. There is no in-between state where the attachment is
deleted but the queue still references it, OR vice-versa.

**Conflict retry.** A 412 (etag conflict) on Phase 1 triggers a
bounded retry (up to 5 attempts) that re-reads the record and
replays the drain. Exhausting the retries raises `RuntimeError`
to the caller.

**Watchdog scope.** The per-turn timeout watchdog is respawned on
every turn-start boundary — initial entry AND steering drain re-entry
(via `_spawn_watchdog_for_turn` inside the drain loop) — so a steered
turn gets a fresh full per-turn budget (§14, §57) rather than sharing
the prior turn's watchdog. The persisted `turn_started_at` (stamped
per drain) additionally backs the RECOVERY path.

### §53. Suspend write

When a multi-turn handler ends a turn with `return X`:

```
1. Read current task (we need etag and the input slot to know if it was promoted).
2. payload_patch = {
       'metadata': metadata.to_dict(),  # auto-flush of touched namespaces
       'input': null,                   # consumed input goes away
       'retry_attempt': null,          # fresh retry budget for next turn
   }
3. If task.payload['steering'] is set:
       steering = dict(task.payload['steering'])
       steering['active_input'] = null
       payload_patch['steering'] = steering
4. # NB: The framework does NOT persist X anywhere on the task record
   # (§11, §20, C-OUT). The handler's return value is delivered to
   # the in-process awaiter of TaskRun.result() ONLY. No payload['output']
   # write, no '_output' attachment.
   attachments_patch = {}
5. If task.payload['input'] was a ref (§23.3):
       attachments_patch[ref_key(task.payload['input'])] = null
6. PATCH(task_id, status='suspended', suspension_reason='run_completion',
        payload=payload_patch, attachments=attachments_patch,
        lease piggyback, if_match=etag)
```

Properties this guarantees:

- **No output persistence.** Whether the handler returns a value or
  not, nothing about that value lands on the resilient record. After
  suspend the record reflects `status=suspended`, no `output` key.
  Awaiters of `TaskRun.result()` receive the value in-process before
  the chain enters its next turn; replay-after-crash returns to the
  handler with no output replay path.
- **Atomic input + steering + attachment clears.** Single PATCH
  carries the `input` clear, the `steering.active_input` clear, the
  `retry_attempt` reset, AND the deletion of the promoted `input`
  attachment (when applicable). There is no crash window where the
  attachment exists without its ref or vice-versa.
- **`last_input_id` preserved.** Not touched here so the
  `if_last_input_id` precondition on the next `start()` still resolves.

### §54. Recovery + reclaim

Both reclaim sites (inline and cold-start/periodic) MUST use
`if_match` for CAS. There is no longer a difference between them
in this respect.

**Inline reclaim — `_reclaim_one(task_info)` (lifecycle resolver):**

```
1. Build a PATCH that re-takes the lease:
      lease_owner            = self.owner       # always self
      lease_instance_id      = self.instance_id # always self
      lease_duration_seconds = 60
      if_match               = task_info.etag   # CAS-guarded
2. PATCH(task_info.id, ...)
   On 412: ABANDON per §25.3 — the conflict IS the race-detection;
   the next caller / scan re-evaluates.
3. Re-read task_info (now with self as lease owner). Record the new etag.
4. Look up the resume callback by source.name.
5. If no callback found: log and skip (decorator not registered in
   this process — the framework cannot recover what it does not know).
6. Hydrate ctx.input from payload['input'] (resolving ref via
   attachments if necessary).
7. Compute entry_mode based on stored status:
      in_progress => 'recovered'
      suspended   => 'resumed'
      pending     => 'fresh'
8. If drain_in_progress is True: set is_steered_turn=True; use
   active_input as ctx.input (NOT payload['input']).
9. Spawn lease_renewal_loop, watchdog (with remaining-from-turn-start),
   execute_task_loop with the recovered ctx.
```

**Cold-start / periodic reclaim — `_recover_stale_tasks()`:**

```
1. provider.list(agent_name, session_id, status="in_progress",
                 lease_owner=self.owner,
                 source_type=_SOURCE_TYPE)
   The source_type filter scopes to framework-owned tasks ONLY;
   foreign-typed records in the same scope are never picked up.
2. For each task_info:
   a. Build the same reclaim PATCH as inline reclaim, INCLUDING
      if_match = task_info.etag.
   b. PATCH(task_info.id, ...). On 412: ABANDON (the conflict IS
      the race-detection — let the next scan or the next caller
      re-evaluate).
   c. Same handler dispatch as steps 3-9 of inline reclaim.
```

**Liveness predicate (`_lease_is_dead`).** The framework's
"is this lease dead" check is:

```
1. If active_locally (this process has an _ActiveTask entry for
   this id): NOT dead.
2. If lease.owner == self.lease_owner AND not active_locally:
   DEAD (previous lifetime of mine).
3. If lease.owner != self.lease_owner AND lease.owner is set:
   NOT dead (foreign owner — caller observes the live-elsewhere
   conflict shape; do not reclaim).
4. If lease.owner is empty: DEAD (no live executor claims it).
```

Note: the predicate does NOT directly consult `expires_at`. The
hosted store enforces expiry server-side at PATCH time by
rejecting an attempted reclaim against a still-live foreign
lease; the framework relies on the server response (which the
classifier turns into `evicted` / `conflict` labels) to handle
the lost-race case. The local provider mirrors this behavior:
attempting to reclaim a not-yet-expired foreign lease yields a
classified conflict, and the local provider bumps `expiry_count`
when the prior lease's `expires_at` (UTC) has actually passed
(parity with the hosted store).

### §55. Periodic recovery loop

```
loop:
    await sleep(300 seconds) OR cancel_event
    if cancel_event set: break
    await self._recover_stale_tasks()   # same as cold-start scan
```

The interval is intentionally **NOT** developer-tunable: shortening
it inflates list-bandwidth without improving recovery latency
(inline reclaim already catches in-flight starts); lengthening it
delays reclaim of expired-during-process-lifetime tasks beyond
acceptable bounds.

### §56. Lease renewal loop

```
interval = max(1, lease_duration_seconds // 2)
failures = 0
loop:
    await sleep(interval) OR cancel_event
    if cancel_event set: break

    if last_refresh_provider() shows a recent piggyback refresh:
        # Skip: a payload PATCH within the last interval already
        # refreshed the lease as a side effect.
        continue

    try:
        PATCH(task_id, lease_owner, lease_instance_id, lease_duration_seconds)
        failures = 0
        if steering_poll_callback: await steering_poll_callback()
    except TransportClassifiedError as exc:
        if exc.classification == 'evicted':
            # Orphan-sandbox eviction. Stop renewing immediately;
            # signal local cleanup callback to cancel execution,
            # suppress pending terminal write, signal awaiters with
            # TaskConflictError.
            on_cancel_callback.set()
            break
        failures += 1
        if failures >= 3 and on_cancel_callback:
            on_cancel_callback.set()
            break
    except Exception:
        failures += 1
        ...
```

The `last_refresh_provider` optimization avoids an extra HTTP
round-trip on every renewal when the framework already piggybacked
lease ownership on a payload PATCH within the last interval.

### §57. Per-turn watchdog

```
async def _timeout_watchdog(timeout_seconds, cancel_event, ctx,
                            remaining_seconds=None):
    if remaining_seconds is None:
        sleep_for = timeout_seconds
    else:
        # Clamp to [0, timeout_seconds] for clock-skew safety.
        sleep_for = max(0.0, min(remaining_seconds, timeout_seconds))

    if sleep_for > 0:
        await sleep(sleep_for)

    # ORDERING INVARIANT: cause boolean BEFORE cancel event.
    ctx.timeout_exceeded = True
    cancel_event.set()
```

`remaining_seconds = None` is fresh-entry / drain-re-entry; the
budget is the full timeout. `remaining_seconds = computed` is
crash-recovery, where the manager computes
`opts.timeout_seconds - (now - persisted_turn_started_at)` and
passes it. A negative or zero value fires immediately so the
recovered handler sees the cause from its first checkpoint.

### §58. Orphan attachment cleanup

```
async def _steering_cleanup_orphan_attachments(task_info):
    if not task_info.attachments:
        return
    steering_keys = {k for k in task_info.attachments
                       if k.startswith('steering_input_')}
    if not steering_keys:
        return
    pending = task_info.payload.get('steering', {}).get('pending_inputs', [])
    referenced = {ref_key(e) for e in pending if is_ref(e)
                                              and ref_key(e).startswith('steering_input_')}
    orphans = steering_keys - referenced
    if not orphans:
        return
    PATCH(task_info.id, attachments={k: null for k in orphans},
          if_match=task_info.etag)
```

This is **defense-in-depth**. The happy path (single-PATCH
atomicity at append + drain) never produces orphans. A future
code path that splits a write across multiple PATCHes could
leave one; this cleanup runs once per recovery and closes the
window for ~one extra PATCH per task per cold-start.

Implementers MAY omit this if they can prove the single-PATCH
invariant holds across all transitions (today's framework can).

---

## Part VIII — Conformance items

This section enumerates the invariants every conformant implementation
MUST satisfy. The items are testable; the canonical Python
implementation has a regression test covering each (see
`azure-ai-agentserver-core/tests/tasks/` and `tests/streaming/`).

Items are grouped by area. Each item is identified `C-AREA-N`
(e.g. `C-LCM-1` = Lifecycle item #1).

### C-LCM (lifecycle + state machine)

- **C-LCM-1.** Status MUST be one of exactly four values:
  `pending`, `in_progress`, `suspended`, `completed`. No other
  value is legal in the store.
- **C-LCM-2.** Unsuccessful outcomes (failure, cancellation) are
  communicated via typed exceptions (NEVER via a fifth status
  value). For one-shot (`@task`) tasks the record is deleted on
  terminal exit (one-shot is always ephemeral). For multi-turn
  (`@multi_turn_task`) tasks the chain transitions to `suspended`
  with `suspension_reason="run_completion"` on either successful
  `return X` or a handler raise — the chain stays alive and the
  caller observes the per-turn outcome via the typed exception
  (`TaskFailed` / `TaskCancelled`) or the returned `Output`.
- **C-LCM-3.** `ctx.entry_mode` MUST be one of `fresh`, `resumed`,
  `recovered`. The combination `(entry_mode=recovered,
  is_steered_turn=True)` is legal and MUST be supported.
- **C-LCM-4.** For any given `task_id`, at most one handler runs
  at a time across the cluster of processes that share the
  `(agent_name, session_id)` scope. The lease + ETag CAS
  combination enforces this.
- **C-LCM-5.** Status transitions MUST be enforced against the §24.1
  matrix. Invalid transitions raise `_HostedConflict(_code="invalid_state_transition")`
  — this is a framework bug (framework drives transitions, not the
  developer) and at the boundary maps to `RuntimeError`.
- **C-LCM-6.** Terminal-status tasks are immutable per §24.2. PATCH
  on a `completed` task is rejected EXCEPT for the no-op
  `completed → completed` with no other field changes. Violations
  raise `_HostedConflict(_code="task_immutable")` →
  `TaskConflictError(current_status="completed")`.
- **C-LCM-7.** DELETE on a non-terminal task without `force=true`
  MUST be rejected as `invalid_request` (400). DELETE on a terminal
  task always succeeds without `force`. DELETE honors `If-Match`
  when supplied (412 / `etag_mismatch` on mismatch). Per §24.3.
- **C-LCM-8.** PATCHes that include any of `id`, `agent_name`,
  `session_id`, `title`, `description`, `source` MUST be rejected
  as `invalid_request` (§28a.6 / §24).

### C-ID (identity)

- **C-ID-1.** `task_id` validation MUST reject empty / length>256 /
  characters outside `[a-zA-Z0-9\-_.:]` at the call site, before
  any network is touched.
- **C-ID-2.** `lease_owner` MUST be derived from BOTH
  `agent_name` AND `session_id` (format
  `<agent_name>|session:<session_id>`).
- **C-ID-3.** `lease_instance_id` MUST be fresh per process; a
  same-`(owner, instance_id)` lease record indicates "my own task";
  same-owner-different-instance indicates "previous lifetime of
  mine, RECLAIM."
- **C-ID-4.** `source.name` MUST be the routing key for resume
  callback discovery. Two tasks with the same `source.name` are
  routed to the same callback on recovery; tasks with no matching
  registered callback are skipped (logged, not raised) — the
  framework cannot recover what it does not know.

### C-LSE (lease)

- **C-LSE-1.** Lease renewal MUST run at half the lease duration.
  Default lease duration is 60 seconds; default renewal interval
  is 30 seconds.
- **C-LSE-2.** All reclaim PATCHes — inline (via `_reclaim_one`)
  AND cold-start / periodic-scan reclaims — MUST be guarded by
  `if_match=etag`. On `412`, the framework MUST treat the reclaim
  as ABANDONED for this scan (another process beat us to it; do
  not retry). This is the unified rule that closes the prior
  known gap where periodic-scan reclaims wrote without
  `if_match`.
- **C-LSE-3.** `expiry_count` MUST be a server-side counter ONLY.
  Implementations MUST NOT add it to the patch-request shape; the
  framework MUST NOT write the field. The hosted store bumps it
  on actual-expiry ownership change (not on same-owner
  different-instance handoff). The local file provider MUST also
  bump `expiry_count` on the reclaim write that completes a real
  lease handoff (parity with the hosted store, so
  the lease's `expiry_count` works in local mode and so tests
  asserting recovery behavior can run against the local
  provider).
- **C-LSE-4.** Eviction (HTTP 409 + `error.code=binding_mismatch`)
  classified as `evicted` MUST trigger the local cleanup sequence:
  cancel local execution, suppress pending terminal write, signal
  awaiters with `TaskConflictError`.
- **C-LSE-5.** `ctx.exit_for_recovery()` MUST force-expire the lease
  and leave status as `in_progress` (NOT `suspended`).
- **C-LSE-6.** `lease_duration_seconds` MUST be `0` (force-expire) OR
  in range `10..3600`. Other values MUST be rejected as
  `invalid_request` by both providers (§22.1 LSE-W-1).
- **C-LSE-7.** Lease params are an all-or-nothing triplet: supplying
  any subset of `(lease_owner, lease_instance_id, lease_duration_seconds)`
  without all three MUST be rejected as `invalid_request` (§22.1 LSE-W-2).
- **C-LSE-8.** Lease acquisition / renewal against a record whose
  lease is held by a different owner and not yet expired MUST be
  rejected as `_HostedConflict(_code="lease_held_by_another")` →
  developer-observable `TaskConflictError(current_status="in_progress")`
  (§22.1 LSE-W-3).
- **C-LSE-9.** `in_progress → pending` transition MUST verify the
  supplied `(lease_owner, lease_instance_id)` matches the record's
  current lease (`EnsureLeaseMatches` per §22.1 LSE-W-4).
- **C-LSE-10.** Lease renewal (no status change, `duration > 0`) MUST
  be rejected when the current status is anything other than
  `in_progress` (§22.1 LSE-W-5).
- **C-LSE-11.** Force-expire (`lease_duration_seconds=0`) MUST NOT be
  combined with a status transition in the same PATCH (§22.1
  LSE-W-6).
- **C-LSE-12.** Force-expire MUST verify lease ownership unless the
  lease is already expired (§22.1 LSE-W-7).
- **C-LSE-13.** `started_at` MUST be set exactly once on the first `in_progress` transition and MUST NOT be updated thereafter — lease re-acquisition (different-owner takeover OR same-owner restart after expiry), recovery scanner takeover, and suspend/resume cycles MUST all preserve the original `started_at` value (§22.1 LSE-W-8).
- **C-LSE-14.** On every successful lease write, the provider MUST
  stamp `lease.heartbeat_at = now` (§22.1 LSE-W-10). The field is
  on `LeaseInfo`; it is NOT exposed on the public surface.

### C-INP (input + chain)

- **C-INP-1.** `input_id` provided without `if_last_input_id` MUST
  succeed; the framework records the id in `last_input_id`.
- **C-INP-2.** `if_last_input_id` provided without `input_id` MUST
  raise `TypeError` at the call site.
- **C-INP-3.** `if_last_input_id` mismatch MUST raise
  `LastInputIdPreconditionFailed` (subclass of
  `TaskPreconditionFailed`).

### C-SUS (suspend / resume)

- **C-SUS-1.** A multi-turn handler's `return X` MUST clear
  `payload["input"]` AND `payload["steering"]["active_input"]`
  AND any promoted input attachment, in a single PATCH that also
  transitions the chain to `suspended`.
- **C-SUS-2.** The next `.run()` / `.start()` against a `suspended`
  chain MUST re-invoke the handler with `entry_mode="resumed"`
  and the NEW `input` (not the consumed one).
- **C-SUS-3.** The handler's `return X` value MUST be delivered
  unconditionally to the in-process caller awaiting
  `TaskRun.result()` — even if steering inputs are queued. `X`
  resolves the future and is then no longer reachable from the
  persisted record (the framework does NOT write `payload["output"]`).
- **C-SUS-4.** The framework MUST NOT write `payload["output"]`
  and MUST NOT use the `output` attachment slot. The suspend
  PATCH writes `status="suspended"`, `suspension_reason="run_completion"`,
  clears `payload["input"]` and `payload["retry_attempt"]`, and
  preserves `payload["last_input_id"]`. No output / error
  projection onto the chain record.

### C-STR (steering)

- **C-STR-1.** Steering queue cap MUST be 9; appending past it
  MUST raise `SteeringQueueFull` from `.start()`.
- **C-STR-2.** Append MUST set `steering["cancel_requested"]=True`
  and signal `ctx.cancel` on the in-process active execution.
- **C-STR-3.** `next_input_seq` MUST be monotonic and advance ONLY
  on promotion (inline appends do NOT bump it).
- **C-STR-4.** A drain MUST NOT renumber any other queue entry's
  attachment key. Surviving promoted entries keep their
  original `steering_input_<seq>` keys.
- **C-STR-5.** A drain MUST be carried in a single PATCH that
  removes the head from `pending_inputs`, deletes the
  corresponding attachment (if any), and sets the new turn's
  input / `turn_started_at`.
- **C-STR-6.** Multi-turn handler ending a turn with `return X`
  MUST transition the chain to `suspended` and promote the next
  queued steering input as the next turn's input. The queued
  steerer's `.result()` resolves with whatever the promoted turn
  emits.
- **C-STR-7.** Multi-turn handler ending a turn with `raise` (any
  non-CancelledError exception) MUST transition the chain to
  `suspended` (NOT `completed` / `failed`) — the chain stays
  alive — and promote the next queued steering input as the next
  turn. The failing turn's caller observes `TaskFailed(error=...)`;
  the queued steerer's `.result()` resolves with whatever the
  promoted turn emits.
- **C-STR-8.** First turn's caller MUST observe the natural
  multi-turn outcome of the in-flight turn (the handler's
  `return X` resolved to that caller; or the handler's `raise`
  raised to that caller as `TaskFailed` / `TaskCancelled`). It
  MUST NOT be replaced by what a later turn produces.

### C-CAN (cancellation + cause booleans)

- **C-CAN-1.** Cause booleans MUST be `timeout_exceeded`,
  `cancel_requested`; plus the cause counter `pending_input_count`.
- **C-CAN-2.** Each cause MUST be set BEFORE `ctx.cancel` is set
  (ordering invariant). A handler observing
  `ctx.cancel.is_set() == True` MUST be guaranteed to see at least
  one cause already set (or `pending_input_count > 0`).
- **C-CAN-3.** Causes MUST accumulate (never reset within a turn).
- **C-CAN-4.** `TaskCancelled` MUST NOT inherit `asyncio.CancelledError`
  (would be suppressed by generic handlers).
- **C-CAN-5.** `TaskRun.cancel()` MUST set `ctx.cancel_requested =
  True` BEFORE setting `ctx.cancel`.

### C-TMO (timeout watchdog)

- **C-TMO-1.** Timeout is **per-turn** and **wall-clock**.
- **C-TMO-2.** `payload["turn_started_at"]` MUST be re-stamped at
  every turn-start boundary (fresh, resumed, drain re-entry — Phase 1
  of §52). It MUST NOT be re-stamped on crash recovery.
- **C-TMO-3.** Recovered watchdog MUST compute
  `remaining = max(0, timeout - (now - turn_started_at))` and
  fire immediately if elapsed.
- **C-TMO-4.** Clock skew MUST be clamped to `[0, timeout]` in
  both directions.
- **C-TMO-5.** Watchdog MUST set `ctx.timeout_exceeded = True`
  BEFORE setting `ctx.cancel` (C-CAN-2 ordering).
- **C-TMO-6.** Watchdog MUST be cooperative-only. It MUST NOT
  force-stop the handler, terminate the task, or cancel lease
  renewal.
- **C-TMO-7.** A fresh watchdog SHOULD be spawned on every
  turn-start boundary (fresh, resumed, drain re-entry). The
  canonical Python implementation today only spawns on fresh /
  resumed entries; drain re-entry inherits the original watchdog.
  This is a known gap (see §14).

### C-RET (retry)

- **C-RET-1.** `retry=None` MUST mean "no retry" (the handler's
  raise propagates directly to the caller as `TaskFailed`).
- **C-RET-2.** `retry_attempt` MUST be exposed on
  `TaskContext.retry_attempt` and persisted as
  `payload["retry_attempt"]`. Cleared at every turn-start
  boundary.
- **C-RET-3.** Crash recovery MUST NOT consume retry budget. A
  lifetime that died before the handler raised MUST NOT advance
  `retry_attempt`.
- **C-RET-4.** Between attempts, the framework MUST PATCH only
  `payload["retry_attempt"]` (the counter advance). NO
  `payload["error"]` is written between attempts.
- **C-RET-5.** When `retry_attempt >= max_attempts`, the framework
  MUST raise `TaskFailed(error=TaskExhaustedRetriesErrorDict(...))`
  to the awaiting caller. The dict's `type` MUST be the literal
  `"exhausted_retries"`; `attempts`, `last_error`, `last_error_type`,
  `traceback` MUST be present.
- **C-RET-6.** No persisted `error` field on the chain record.
  The framework's structured ERROR log (named
  `resilient_task_handler_failure`, with `task_id`, `input_id`,
  `error_type`, `error_message`) is the resilient failure
  observability surface; the chain record itself does not
  carry the per-turn diagnostic.

### C-STATE (application state)

- **C-STATE-1.** Task payloads MUST NOT contain application metadata
  namespaces.
- **C-STATE-2.** Application State Store writes MUST NOT renew task
  leases or change task etags.
- **C-STATE-3.** Suspend, complete, fail, drain, and recovery-deferral
  transitions MUST NOT implicitly flush application state.

### C-ATT (attachments + promotion)

- **C-ATT-1.** Two wire shapes only: inline (raw value) OR ref
  (`{"__attachment_ref__": {"key": ..., "hash": "sha256:..."}}`).
- **C-ATT-2.** Detection rule: a slot is a ref iff it is a dict
  with exactly one key `__attachment_ref__` whose value is a dict
  with both `key` and `hash`.
- **C-ATT-3.** Promotion thresholds: function input > 200 KiB;
  steering input > 20 KiB. Outputs are not persisted at all
  (§11, §20, C-OUT) — there is no `output` attachment. Measured
  in canonical-JSON bytes. Framework-reserved attachment keys:
  `input`, `steering_input_<seq>`.
  Worst-case framework attachment usage: 1 + 9 = 10 of 20 slots;
  10 slots remain free.
- **C-ATT-4.** Per-attachment cap: 10 MiB serialized. Per-task
  attachment count cap: 20. Per-value cap MUST be enforced
  client-side on every write site (create + patch) in both
  providers. Provider-level violations MUST surface as the
  internal `_AttachmentTooLarge` / `_AttachmentLimitExceeded`
  (underscore-prefixed; NOT exported). The framework MUST
  re-raise as the developer-facing `InputTooLarge` (for `input`
  / `steering_input_*` keys).
  Per-task count cap MUST be enforced on `create` and SHOULD be
  enforced on `patch` when current state is cheaply available;
  the canonical Python implementation enforces count on
  local-provider patches and on framework-orchestrated
  steering-append patches (which fetch state anyway) but NOT on
  the bare hosted PATCH (which would require an extra round-trip).
  The server enforces in the gap.
- **C-ATT-5.** Promotion / drain / suspend / orphan-cleanup
  PATCHes MUST carry BOTH `payload` and `attachments` in a single
  round-trip.
- **C-ATT-6.** Hash algorithm MUST be SHA-256 over canonical
  JSON bytes (`sort_keys=True`, separators `(",", ":")`), formatted
  as `sha256:<64 lowercase hex chars>`.
- **C-ATT-7.** Orphan attachment cleanup (§58) MUST run on
  recovery for tasks with `steering_input_*` keys not referenced
  in `pending_inputs`.
- **C-ATT-8.** Attachment keys MUST match `^[a-zA-Z0-9_.\-]{1,64}$`
  and MUST be non-empty after trim. Validated on every CREATE and
  PATCH write (§23.9).
- **C-ATT-9.** Clear-all gesture: PATCH with `attachments: null`
  (typed-API `TaskPatchRequest.clear_attachments = true`) MUST
  delete every attachment on the task. Mutually exclusive with
  per-key `attachments={...}` in the same request — combination
  MUST be rejected as `invalid_request` (§23.10).
- **C-ATT-10.** DELETE on a task MUST remove all attachments along
  with the task. Local achieves this trivially via unlinking the
  JSON file; hosted relies on the service's blob-cleanup hook
  (§23.10).

### C-VAL (field validation — shared between providers)

- **C-VAL-1.** Task `id` MUST match `^[a-zA-Z0-9_-]{1,128}$`. Empty
  or non-matching ids rejected as `invalid_request` (§28a.1).
- **C-VAL-2.** `agent_name`, `session_id`, `title` MUST be required
  on CREATE (length 1..128 / 1..128 / 1..256 after trim respectively).
- **C-VAL-3.** `description` MUST be ≤ 1024 chars after trim.
- **C-VAL-4.** `suspension_reason` MUST be ≤ 256 chars after trim,
  AND only allowed when target status is `suspended` (§28a.1, §S5).
- **C-VAL-5.** Tag keys MUST match `^[a-zA-Z0-9_.\-]{1,64}$`. Tag
  values MUST be ≤ 256 chars. Total tag entries MUST be ≤ 16.
- **C-VAL-6.** Byte budgets MUST be enforced per §28a.2: `payload`
  ≤ 1 MB, `error` ≤ 64 KB, `source` ≤ 4 KB (canonical-JSON byte
  measurement: `sort_keys=True`, separators `(",", ":")`).
- **C-VAL-7.** `source` when supplied MUST be a JSON object with a
  non-empty `type` field (§28a.3). Optional structured fields
  pass through; unknown fields are preserved.
- **C-VAL-8.** `error` when supplied MUST be a JSON object with
  non-empty `message` and `type` strings (§28a.4). `code` defaults
  to `"error"` when missing.
- **C-VAL-9.** Status `"failed"` MUST be rejected on input. Status
  `"done"` MUST be normalized to `"completed"` on read and in list
  filters (§28a.5).
- **C-VAL-10.** PATCHes including any of `id`, `agent_name`,
  `session_id`, `title`, `description`, `source` MUST be rejected
  as `invalid_request` (§28a.6).
- **C-VAL-11.** Payload PATCH semantics per §F1: when the patch
  value is a JSON object, shallow-merge into current payload; for
  any other JSON type (array, string, number), full-replace; null
  is no-op.

### C-REC (recovery)

- **C-REC-1.** Cold-start recovery MUST run as part of
  `TaskManager.startup()` BEFORE any HTTP route binds. Implementers
  MUST gate route binding on `startup()` returning.
- **C-REC-2.** Periodic recovery loop MUST run every 300 seconds
  (default `_PERIODIC_RECOVERY_INTERVAL_SECONDS`). It MUST share
  the same `_recover_stale_tasks` implementation as the cold-start
  scan (no divergence between cold-start filters and periodic-scan
  filters). The shared filter MUST include
  `source_type=<framework constant>` (C-FLT-1).
- **C-REC-3.** Inline reclaim MUST be invoked on `.start()` against
  an `in_progress` task whose lease is dead. The lifecycle resolver
  MUST NOT block on the periodic loop.
- **C-REC-4.** Recovery MUST NOT consume the retry budget
  (C-RET-2 reiterated for emphasis).
- **C-REC-5.** `drain_in_progress=True` at recovery time MUST be
  honored: re-enter with `is_steered_turn=True` and use
  `active_input` as `ctx.input`.

### C-ERR (error taxonomy)

- **C-ERR-1.** `TaskNotFound` MUST be raised only for genuinely
  missing tasks.
- **C-ERR-2.** `TaskConflictError` MUST be the SINGLE error type
  for any "task is busy / not available" state.
  `current_status` carries the observed status.
- **C-ERR-3.** `TaskFailed.error` MUST be a structured dict with
  at minimum `type` and `message`; `cause` is optional.
- **C-ERR-4.** `_HostedConflict(_code, status_code)` is an internal
  discriminator type. It is NOT exported and MUST NOT appear in
  any public exception hierarchy, docstring, or error message.
  The hosted provider's response classifier raises it for service
  responses carrying a structured error code; the local provider
  raises it directly for equivalent conditions. The framework
  matches on `_code` per the §39.1 translation table.
- **C-ERR-5.** Service error codes (`task_immutable`,
  `invalid_state_transition`, `lease_held_by_another`,
  `task_already_exists`, `lease_ownership_changed`, `etag_mismatch`,
  `invalid_request`) MUST translate to the developer-facing
  exceptions per §39.1. The translation table is the contract;
  no service-code string appears in developer-visible types.
- **C-ERR-6.** `etag_mismatch` MUST be retried transparently by the
  framework (bounded retries with re-read). It escapes to
  low-level callers as `EtagConflict` only when retries are
  exhausted (the developer never sees it through `Task.run` /
  `Task.start` / `MultiTurnTask.run` / `MultiTurnTask.start`).
- **C-ERR-7.** `invalid_state_transition` is a framework bug
  (framework drives transitions, not the developer). The
  framework MUST log this condition and convert it to a
  `RuntimeError` rather than propagating to developer code as a
  task-API concept.

### C-STM (streaming protocol)

- **C-STM-1.** `EventStream` MUST be a 4-method protocol: `emit`,
  `close`, `subscribe`, `last_cursor`. No destructive method on
  the Protocol itself.
- **C-STM-2.** Stream states are exactly `Active` and `Closed`.
  There is no per-instance `Gone` state; destruction is a
  registry-level concept (tombstone) surfaced as
  `EventStreamNotFoundError` on the next operation against the
  id.
- **C-STM-3.** `emit(close=True)` MUST be observably atomic — every
  subscriber attached BEFORE this call sees both the payload AND
  the end-of-stream signal.
- **C-STM-4.** `close()` MUST be idempotent (no-op on already-closed
  or destroyed).
- **C-STM-5.** `subscribe()` MUST return an `AsyncIterator`
  directly (not a coroutine that resolves to one).
- **C-STM-6.** `subscribe(after=N)`: if cursor support, yield only
  payloads with cursor strictly greater than `N`; if no cursor
  support, silently ignore the `after` argument.
- **C-STM-7.** `last_cursor()` MUST work on `Closed` streams even
  after all events have been TTL-evicted (load-bearing for
  rehydration).
- **C-STM-8.** Cursor TYPE is DESIGNED to be `int` (string cursors
  introduce silent-wrong-comparison bugs). Implementations SHOULD
  validate `cursor_fn` returns `int` at configurator time. The
  canonical Python implementation does not validate today (a known
  gap).
- **C-STM-9.** Cursored backings MUST honor `cursor_fn` — never
  assume payload field names (`sequence_number`, `event_id`, etc.).

### C-STR-REG (streaming registry)

- **C-STR-REG-1.** Six methods only on the registry: three sync
  configurators (`use_in_memory_live`, `use_in_memory_replay`,
  `use_file_backed_replay`) + three async lifecycle methods
  (`get`, `get_or_create`, `delete`).
- **C-STR-REG-2.** Default backing MUST be `BroadcastEventStream`
  (live, no buffer).
- **C-STR-REG-3.** `get_or_create(id)` MUST be atomic under
  concurrent callers (per-id lock).
- **C-STR-REG-4.** `delete(id)` MUST be idempotent and MUST
  install a tombstone (even for ids that were never registered)
  so a subsequent `get(id)` raises `EventStreamNotFoundError`.
- **C-STR-REG-5.** Tombstone MUST be cleared on the next
  `get_or_create(id)` for the same id.
- **C-STR-REG-6.** `get(id)` MUST raise `EventStreamNotFoundError`
  for ANY id that is not currently a live stream — whether it
  was never registered, was explicitly `delete(id)`d, or had its
  close-clock elapse (§46). `get(id)` MUST NOT itself install a
  tombstone (only `delete(id)` and the close-clock auto-tombstone
  do). There is no `EventStreamGoneError` — that error type has
  been removed; every "id is not live" condition surfaces
  uniformly as `EventStreamNotFoundError`.

### C-STR-TTL (replay TTL)

- **C-STR-TTL-1.** Per-event TTL eviction MUST run on every
  `emit()` and `subscribe()` call, regardless of whether the
  stream is `Active` or `Closed`. (Active streams use TTL to
  bound buffer memory for long-running producers; Closed streams
  use TTL to keep the per-event lifetime consistent until the
  close-clock fires.)
- **C-STR-TTL-2.** Auto-tombstone MUST happen when the stream is
  `Closed` AND `now >= close_time + ttl_seconds` (the
  "close-clock"). This is deterministic and time-driven, NOT
  observer- or buffer-state-driven. There is no
  `total_emit_count > 0` carve-out; a stream created, closed,
  and never emitted to tombstones at `close_time + ttl_seconds`
  like any other Closed stream. Implementations MAY drive the
  clock via a wall-clock timer (preferred for production) or via
  an opportunistic check on `get()` / `emit()` / `subscribe()`
  (acceptable for tests). `last_cursor()` MUST remain
  side-effect-free and MUST NOT trigger the tombstone check.
- **C-STR-TTL-3.** `BroadcastEventStream` (live-only) MUST NOT
  auto-tombstone; it tombstones only via explicit `delete()`.
- **C-STR-TTL-4.** The close-clock and per-event TTL are
  consistent by construction: for every event still in the
  buffer at `close_time`, `emit_time <= close_time`, so
  `emit_time + ttl_seconds <= close_time + ttl_seconds`. By the
  time the close-clock fires, every per-event TTL has elapsed
  and the next eviction sweep removes the events. Implementations
  do NOT need to special-case "buffer not yet empty when the
  close-clock fires."

### C-STR-FBR (file-backed replay)

- **C-STR-FBR-1.** Each stream MUST persist to
  `storage_dir/<filename>.jsonl`, where `<filename>` is derived from
  the stream id by the **filename-safety rule (normative)**: a
  well-formed id — matching `^[A-Za-z0-9._-]+$` with no `.`/`..` path
  segment — is used verbatim (for readability and cross-language
  compatibility); ANY other id (containing a path separator, a `.`/`..`
  segment, a NUL, or any other filesystem-unsafe character) MUST be
  deterministically SHA-256 hash-encoded to an `h_<hex>` stem so it can
  never escape `storage_dir` or collide with a sibling stream. A
  well-formed id that itself matches the reserved `h_<64hex>` shape is
  also hash-encoded, so the verbatim and hashed namespaces stay disjoint
  (no verbatim id can alias another id's hash).
- **C-STR-FBR-2.** Constructor MUST rehydrate from an existing
  file (crash-recovery friendly).
- **C-STR-FBR-3.** Optional `serializer` / `deserializer` callbacks
  MUST be honored for non-JSON payloads. Default uses JSON.
- **C-STR-FBR-4.** `delete()` and the close-clock auto-tombstone
  MUST clean up the file before the registry tombstones the id.
- **C-STR-FBR-5.** **File format.** Each emitted event is a single
  JSONL line wrapping the payload + arrival time:

  ```
  {"emit_time": <float seconds>, "payload": <serialized payload>}
  ```

  On close, a sentinel line is appended:

  ```
  {"__terminal__": true}
  ```

  The terminal sentinel carries **no** timestamp: close-time is
  best-effort. On rehydration the close-clock (§46) is anchored at the
  last real event's `emit_time` (or `now` when the file held no events),
  NOT at a terminal-record timestamp. A terminal record MUST be accepted
  even when it carries no `emit_time`; a NON-terminal record missing
  `emit_time` remains malformed and MUST raise.
- **C-STR-FBR-6.** **Rehydration robustness.** Constructor MUST
  tolerate a trailing partial line (e.g. from a crash mid-write)
  by truncating it. Mid-file malformed JSON lines MUST raise
  (corruption signal, not recoverable). The TERMINAL sentinel, if
  present anywhere mid-file, MUST be ignored unless it is the
  final line.
- **C-STR-FBR-7.** **Concurrency.** Implementations MUST use a
  single-writer lock (POSIX `fcntl` advisory lock preferred,
  `.lock` sentinel-file fallback) to prevent two processes from
  appending to the same file concurrently. The lock guards the
  file for the lifetime of the stream instance.
- **C-STR-FBR-8.** **Compaction.** After ~1000 evictions,
  implementations SHOULD rewrite the file to compact away evicted
  lines (avoids unbounded file growth on long-lived streams with
  short TTLs).

### C-OUT (output persistence) — *removed*

The framework does NOT persist handler outputs. There is no
`payload["output"]` key, no `output` attachment, and no
`OutputTooLarge` exception. A multi-turn handler's `return X`
resolves the in-process caller's `TaskRun.result()` future
directly; a one-shot handler's `return X` does the same and the
record is then deleted (one-shot is always ephemeral). Per-turn
outputs that must survive crashes are the handler's responsibility
(write through your own storage before returning).

### C-INTROSPECT (introspection)

- **C-INTROSPECT-1.** Read-only inspection of a persisted task
  record MUST be available through the task manager's provider:
  `await manager.provider.get(task_id)` returns the framework's
  internal `TaskInfo` envelope (or `None` if the record does not
  exist). The decorator surface (`Task` / `MultiTurnTask`) does NOT
  expose a public `.get(task_id)` method; introspection goes
  through the provider.
- **C-INTROSPECT-2.** Active-execution inspection MUST be available
  through `Task.get_active_run(task_id)` / `MultiTurnTask.get_active_run(task_id, input_id)`,
  which return a `TaskRun` handle bound to the live execution
  (or `None` if the task is not currently in flight in this
  process and cannot be reclaimed inline).

### C-WQ (per-task write serialization)

- **C-WQ-1.** All in-process writes to a single `task_id` MUST
  be serialized through a per-task FIFO write queue (§25.2).
  Concurrent metadata flushes, lease renewals, steering
  appends, and drain writes within the same process MUST NOT
  race against each other.
- **C-WQ-2.** The write queue is in-process only. Cross-process
  serialization is provided by the server's ETag/CAS check
  (412 on mismatch), not by the queue.
- **C-WQ-3.** Per-op 412 policy MUST follow the table in §25.3:
  retries with re-read for metadata-flush / steering-append /
  drain Phase 1 / drain Phase 3 / lease-renewal (with
  ownership re-check); RE-READ-AND-DECIDE for terminal writes
  (retry if lease still ours and status still in_progress,
  ABANDON if lease lost or status already terminal); ABANDON
  for reclaims; default budget 5 attempts.

### C-FLT (recovery scan filter)

- **C-FLT-1.** The cold-start AND periodic recovery scans MUST
  include `source_type=<framework constant>` in the `list()`
  filter so the framework only inspects tasks created by its
  own decorator. Tasks created by other systems (sharing the
  same agent_name + session_id scope) MUST NOT be enumerated
  by the framework's reclaim path. This closes a gap where a
  multi-tenant session could surface unrelated records and the
  framework would attempt to dispatch them to nonexistent
  callbacks.

### C-PRV (provider abstraction)

- **C-PRV-1.** `provider.get(task_id)` MUST return `None` for
  missing tasks (not raise).
- **C-PRV-2.** `provider.update()` MUST honor `if_match` for CAS.
- **C-PRV-3.** Payload merge MUST be shallow (top-level keys
  merged; nested objects replaced wholesale).
- **C-PRV-4.** Tags merge MUST be per-key with null-as-delete.
- **C-PRV-5.** Attachments merge MUST be per-key with null-as-delete
  (mirrors tags; §23.1).
- **C-PRV-6.** Provider `delete()` MAY raise on missing records
  (the canonical Python implementations do — hosted raises on
  404, local raises on missing file). The user-facing
  `MultiTurnTask.delete(task_id)` MUST catch "not found" provider exceptions
  and re-raise as `TaskNotFound`; the higher-level
  `Task`-managed delete path SHOULD be idempotent (no-op on
  already-deleted). Implementers MAY make `provider.delete()`
  itself idempotent if their store cleanly distinguishes.
- **C-PRV-7.** `provider.list(...)` MUST filter server-side.
- **C-PRV-8.** `provider.list(...)` MUST support `agent_name` and
  `session_id` as **optional** filters (workspace-wide listing when
  both are null), matching the service. The local provider MUST
  also accept both as optional (search across all
  `<agent_name>/<session_id>/` directories under the storage root).
- **C-PRV-9.** `provider.list(...)` MUST support these additional
  filters, all optional, all enforced server-side: `has_error`,
  `lease_expired`, `lease_owner`, `tag` (list of key:value pairs,
  AND semantics), `source_type`, `status` (with legacy `"done"` →
  `"completed"` normalization).
- **C-PRV-10.** `provider.list(...)` MUST support pagination via
  opaque `after` cursor + `limit` (default 20, max 100, provider
  clamps over-cap). `before` MUST be rejected as `invalid_request`
  (cursor pagination forward-only). `order` accepts `"asc"` or
  `"desc"` by `created_at` (default `"desc"`). Per §31a.
- **C-PRV-11.** `provider.list(...)` MUST support
  `omit_attachment_values` boolean. When true, returned tasks
  carry attachment keys with `None` values (skip per-row blob
  reads). Default false. Per §31a.
- **C-PRV-12.** The opaque pagination cursor in the response
  (`LastId` / `next_page_token`) MUST be treated as opaque by the
  framework. The local provider mints its own cursor (plain
  `task_id`); the hosted provider round-trips whatever opaque
  token the service returns (up to 4096 chars).

### C-OBS (observability — minimal)

- **C-OBS-1.** The framework MUST emit structured log events at:
  `create`, `lease renewal failure`, `eviction detected`,
  `reclaim`, `recovery start`, `recovery skip (no callback)`,
  `suspend`, `complete`, `fail`, `steering append`, `steering
  drain`, `orphan attachment cleanup`. Log level minimum `INFO`
  except where noted.
- **C-OBS-2.** Logger names MUST be hierarchical under
  `azure.ai.agentserver.tasks` (or language-equivalent).

---


## Part IX — References

- **Foundry Task Storage Protocol Specification** — the wire-level
  contract for the hosted task store (routes, request/response
  envelopes, server-side merge rules, authentication, activation,
  ETag/CAS, error codes). The framework conforms to that contract;
  this document only describes how the framework *uses* the store.
- **Speckit specs (historical, dev-side only)** — `001-resilient-tasks`
  through `018-task-attachments` under contributor `specs/` working
  trees. Each is a point-in-time record of how a specific feature
  was scoped and built; the current state of every feature lives
  in THIS document. These are not source-controlled and are
  intentionally not linked.
- **Canonical Python implementation:**
  `sdk/agentserver/azure-ai-agentserver-core/azure/ai/agentserver/core/tasks/`
  and `.../streaming/`. Tests at `tests/tasks/` and
  `tests/streaming/` cover the conformance items in Part VIII.

## Part X — Appendices (informative)

### §A. Language-mapping cheat sheet

The body of this spec uses Python-style names and types
(`asyncio.Event`, `MutableMapping`, `AsyncIterator`, `timedelta`,
`@classmethod`). These are illustrative; the *behavior* is what
implementers MUST match. Mappings:

| Spec uses | Conceptual meaning | .NET idiom | Notes |
|---|---|---|---|
| `asyncio.Event` | Awaitable level-triggered signal. | `ManualResetEventSlim` / `TaskCompletionSource<bool>`. | Must be set-once / observable many times. |
| `asyncio.CancelledError` | Cooperative-cancel exception that callers may raise to bail. | `OperationCanceledException` (with the framework's own custom subclass). | The framework's `TaskCancelled` MUST NOT inherit the language's generic cancel exception (C-CAN-4). |
| `MutableMapping` | Dict-like with `__getitem__` / `__setitem__` / `__contains__` / `__iter__` / `.get()`. | `IDictionary<string, object?>` or a custom map type. | Mutation visibility limited to the namespace. |
| `AsyncIterator` | Iterator over `__anext__` that may suspend. | `IAsyncEnumerable<T>`. | `subscribe()` returns this directly (not an awaitable that resolves to one). |
| `timedelta` | Duration. | `TimeSpan`. | All durations in the spec MAY be expressed in seconds. |
| `tuple[type[Exception], ...]` | Type predicate for retryable exceptions. | `Func<Exception, bool>` or `IReadOnlyList<Type>`. | Used by `RetryPolicy.retry_on`. |
| `@classmethod` factory presets | Static factory methods. | `static` methods. | `RetryPolicy.exponential_backoff()` etc. |
| Pydantic `model_dump()` | Optional model-aware serialization. | `System.Text.Json` / `Newtonsoft.Json` round-trip. | Implementer note: try model-aware first, fall back to plain JSON. |
| Starlette `Route` | HTTP route binding. | ASP.NET Core `MapPost`. | The framework does not contribute any HTTP route by itself; route bindings are the host framework's concern. |

The spec uses these Python names because the canonical
implementation lives in Python. Re-implementations SHOULD use
language-idiomatic names while preserving the documented behavior.

### §B. Representative full task record

A single JSON document showing how every concept in this spec
composes. This is a deep-research task mid-life: function input
was promoted, three steering inputs are queued (one inline, two
promoted), one drain has already happened so `next_input_seq` is
ahead of the live keys, and framework state slots are set.

```json
{
  "object": "task",
  "id": "research-session-abc123",
  "agent_name": "resilient-research-agent",
  "session_id": "session-abc123",
  "title": "Deep research on transformer trends 2026",
  "status": "in_progress",

  "lease": {
    "owner": "resilient-research-agent|session:session-abc123",
    "instance_id": "worker-12-3f8a9d-1780912345",
    "generation": 7,
    "expires_at": "2026-06-09T04:05:30.123Z",
    "expiry_count": 0
  },

  "tags":   { "task_name": "deep_research" },
  "source": {
    "type":                "agentserver.task",
    "name":                "deep_research",
    "server_version":      "azure-ai-agentserver-core/2.0.0b6 (python/3.12)",
    "hosting_environment": "AzureFoundry"
  },

  "payload": {
    "schema_version": "1",
    "input": {
      "__attachment_ref__": {
        "key":  "input",
        "hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      }
    },

    "steering": {
      "pending_inputs": [
        "Quick note: prioritise post-2024 papers",
        {
          "__attachment_ref__": {
            "key":  "steering_input_3",
            "hash": "sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
          }
        },
        {
          "__attachment_ref__": {
            "key":  "steering_input_4",
            "hash": "sha256:f0e1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d"
          }
        }
      ],
      "next_input_seq":    5,
      "cancel_requested":  true,
      "drain_in_progress": false,
      "active_input":      null
    },

    "turn_started_at": "2026-06-09T03:50:00.000000+00:00",
    "retry_attempt":   0,
    "last_input_id":   "msg_abc123"
  },

  "attachments": {
    "input": {
      "topic":   "deep learning trends 2026",
      "depth":   "comprehensive",
      "context": "<~800 KB of caller-supplied reference material>"
    },
    "steering_input_3": {
      "instruction": "refocus on transformer architectures",
      "context":     "<~600 KB of caller-supplied reference material>"
    },
    "steering_input_4": {
      "instruction": "include reinforcement learning hybrids",
      "context":     "<~500 KB of caller-supplied reference material>"
    }
  },

  "etag":         "\"5e00450b-0000-0800-0000-6a223e670000\"",
  "created_at":   "2026-06-09T03:45:00.000Z",
  "updated_at":   "2026-06-09T03:55:30.123Z",
  "started_at":   "2026-06-09T03:45:01.234Z",
  "completed_at": null,
  "error":              null,
  "suspension_reason":  null
}
```

What this single document demonstrates:

| Concept | Where to look |
|---|---|
| Status, identity, timestamps | top-level fields |
| Lease (§22) | `lease.owner`, `lease.instance_id`, `lease.generation` |
| Framework-stamped routing (§21) | `tags.task_name`, `source.name` |
| Input promoted to attachment (§23) | `payload.input` is a ref; `attachments.input` holds the value |
| Application state (§17) | Stored separately in Foundry State Store, not in this task record |
| Steering queue with mixed shapes (§12, §23) | `steering.pending_inputs[0]` inline; `[1]`, `[2]` refs |
| Monotonic seq invariant (§23.5) | `next_input_seq: 5` with live keys `steering_input_3` + `steering_input_4` — one drain consumed `steering_input_0/1/2`, no renumbering |
| Steering mechanism state (§12) | `cancel_requested`, `drain_in_progress`, `active_input` |
| Per-turn watchdog source of truth (§14) | `turn_started_at` |
| Resilient retry counter (§15) | `retry_attempt` |
| Last-input-id chain (§11) | `last_input_id` |
| ETag CAS (§25) | `etag` |
| Worst-case attachment count (§23.2) | 4 of 20 slots used here; framework reserves at most 11 (1 + 9 + 1) |

Simpler scenarios drop fields:

- **Small inputs only**: `payload.input` is the raw JSON value;
  `pending_inputs` is all raw values; `attachments` is absent
  (no output is ever persisted; §11/§20/C-OUT).
- **Handler returned `X` from a turn (multi-turn implicit suspend)**:
  `payload` has no `output` key; `attachments` has no `output`
  entry. The handler's return value is delivered to the in-process
  awaiter of `TaskRun.result()` only.
- **Just-after-resume**: `payload.input` holds the new input
  (inline or ref); no `output` key on the record (and never was).
- **Cold start, no steering**: `steering` absent; `next_input_seq`
  doesn't appear.

### §C. Steering sequence (append → cancel → drain → result)

```
                                                              ┌─ time ─▶
Caller A                Framework                Caller B              Handler
   │  .start(t,A) ───▶ create + execute_task ───────────────────────▶ enter(fresh, input=A)
   │                                                                  │
   │                                                                  │ doing work...
   │                            .start(t,B) ◀───────│                 │
   │                            ↓                                     │
   │              steering_append PATCH (queue B,                     │
   │              cancel_requested=true, attachment if >20K)          │
   │              + signal ctx.cancel locally  ─────────────────────▶ ctx.cancel.is_set() == True
   │                                                                  │
   │                                                                  │ winds down via strategy A
   │                                                                  │  → return X
   │              ◀──────────── suspend resolves                      │
   │                            future of A with                      │
   │                            await run.result() → X                │
   │                                                                  │
   │                            _try_drain_steering()                 │
   │                            ↓                                     │
   │                            Phase 1 PATCH: pop B,                 │
   │                            delete steering_input_<seq>,         │
   │                            drain_in_progress=true,               │
   │                            turn_started_at refreshed            │
   │                            ↓                                     │
   │                            build new ctx,                        │
   │                            entry_mode=resumed,                   │
   │                            is_steered_turn=true ────────────────▶ enter(resumed steered, input=B)
   │                            ↓                                     │
   │                            Phase 3 PATCH: drain_in_progress=     │
   │                            false, _retry_attempt=0               │
   │                                                                  │
   │                                                                  │ handler runs to completion
   │                                                                  │  → return Y
   │                       _handle_suspend(): write suspended,        │
   │                       clear active_input, clear input,           │
   │                       delete input attachment if ref            │
   │                                            ─────▶ B's future     │
   │                                                  await run.result()
   │                                                    → Y
   ▼                                            ▼                     ▼
```

If between Phase 1 and Phase 3 the process crashes, the next
recovery reads `drain_in_progress=true` and re-enters from
`active_input` with `is_steered_turn=true` (§52 race-recovery
contract).

### §D. Cold-start recovery sequence

```
Process starts:
   1. TaskManager.__init__():
       - lease_owner   = "<agent>|session:<sess>"
       - instance_id   = "worker-<pid>-<rand>-<unix>"
       - register decorator-discovered functions in
         _resume_callbacks  by source.name
   2. await manager.startup():
       a. Provider.list(agent, sess, status="in_progress",
                        lease_owner=self.owner,
                        source_type=_SOURCE_TYPE)   # framework-only scope
       b. For each task in the list:
           - if active_locally: skip
           - _steering_cleanup_orphan_attachments(task) (§58)
           - reclaim (PATCH lease to self, with if_match=etag —
             on 412, ABANDON; next scan re-evaluates)
           - look up resume callback by source.name
           - if no callback: log and skip (we cannot recover
             what we did not register)
           - hydrate ctx.input from payload['input'] (resolve
             ref via attachments if needed)
           - entry_mode := computed from status + drain_in_progress
           - spawn lease_renewal_loop, watchdog, execute_task_loop
       c. spawn _periodic_recovery_loop as background task
   3. Bind HTTP routes (only AFTER step 2 returns).
```

The "bind HTTP routes only after `startup()` returns" rule is
load-bearing — it guarantees that handlers waiting to be
recovered are visible before any HTTP traffic could land that
might call into them.

**Note on the recovery-scan list filter.** The list call passes
`source_type=_SOURCE_TYPE` so the scan returns ONLY tasks created
by this framework. Foreign-typed records in the same
`(agent_name, session_id, lease_owner)` scope are never picked
up. This avoids the wasted-reclaim case where a foreign record
matching the lease owner triple would otherwise be PATCH-touched
before being dropped by the resume-callback lookup.

---


---

## Document status

- **Version:** 1.0 (initial unified authoritative spec).
- **Maintenance:** Update this document on every change that
  affects developer-visible behavior or wire shape. Update the
  conformance items in Part VIII when adding new behaviors.
- **Format:** Markdown; intended for both human reading and agent
  consumption.
- **Location:** `sdk/agentserver/azure-ai-agentserver-core/docs/task-and-streaming-spec.md`.
  This document is source-controlled and is the ground-truth
  reference for Copilot/agent grounding when building or modifying
  the primitives.
