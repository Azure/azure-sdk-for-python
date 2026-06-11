# Durable Task & Streaming Primitives — Design Specification

**Status:** Authoritative, source-of-truth specification.
**Scope:** The **`@task` durable-task primitive** and the **`streams`
streaming primitive** in `azure-ai-agentserver-core` — i.e.
everything that ships under `azure.ai.agentserver.core.durable.*`
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
two primitives in scope. It **supersedes** any prior dev-side
speckit specs or scratch reference docs that existed during the
design iterations leading to the current implementation.

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
- §5. The durable task primitive
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
- §22. Lease structure and ownership semantics
- §23. Attachments and input promotion
- §24. Status state machine
- §25. ETag (optimistic concurrency) usage
- §26. Recovery `POST /tasks/resume` endpoint

### Part IV — Provider abstraction (storage backends)
- §27. `TaskProvider` interface
- §28. Hosted provider (HTTP)
- §29. Local provider (file-backed)
- §30. Provider auto-selection
- §31. Background loops

### Part V — Public API surface (language-agnostic)
- §32. `task` decorator and `TaskOptions`
- §33. `Task` handle (`run`, `start`, `options`)
- §34. `TaskContext`
- §35. `TaskRun`
- §36. `TaskResult` and `Suspended`
- §37. `TaskMetadata`
- §38. `RetryPolicy`
- §39. Error taxonomy

### Part VI — Streaming primitive (peer subpackage)
- §40. Why streaming is decoupled from `@task`
- §41. `EventStream` protocol
- §42. The `streams` registry
- §43. Stream lifecycle states (Active → Closed → Gone)
- §44. Concrete backings (live, replay, file-backed)
- §45. Cursor and `subscribe(after=...)`
- §46. TTL eviction (replay backings)
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

The durable-task primitive turns a single async agent function into a
**crash-resilient, steerable, long-running** unit of work backed by a
durable task store. It exists to close the gap between:

- **What the platform sees.** A unit of work it can place, restart,
  liveness-check, and reclaim.
- **What the application owns.** A plain function the developer writes
  once, that survives container crashes, OOM kills, redeployments, and
  cooperative cancellation without hand-rolling lease, heartbeat,
  checkpoint, recovery, or steering plumbing.

The streaming primitive (`azure.ai.agentserver.core.streaming`) is a
**peer** to the durable primitive — it does *not* nest under
`@task`. It exists to give every async producer/consumer pair in the
agentserver family a single Protocol to program against (in-memory live
fan-out, in-memory replay with cursor, file-backed crash-recoverable
replay), independent of whether the producer happens to be a `@task`.

Five design goals constrain every decision in this document:

1. **Single invariant for the durable primitive.** For any given
   `task_id`, at most one handler runs at a time. Every other behavior
   falls out of this invariant.
2. **Crash-recovery is first-class, not a feature.** Every API
   decision is evaluated against the question "what does this look
   like after a crash?" A primitive that disappears at the crash
   boundary (a per-call kwarg, an in-memory listener, a closure-only
   state) is not acceptable; it must be reified into the durable
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
   durable state (`ctx.input`, `ctx.metadata`, framework counters)
   survives. Determinism inside the handler is the developer's
   responsibility — the standard at-most-once side-effect pattern in
   §10 covers the common case.
2. **Not a workflow engine.** No fan-out/fan-in, no child workflows,
   no signals or timers as first-class primitives. Use Temporal /
   Durable Functions / Orleans for that — `@task` can live inside
   such an engine but does not replace it.
3. **Not a bulk-data store.** `ctx.metadata` is small (tens of KB
   per namespace; the whole task payload caps at 1 MB). It is a
   watermark / dedup-token store, not a chat-log store. Per-input
   payloads up to 2 MB are accepted via the attachments mechanism
   (§23) but anything larger MUST be externalized by the caller.
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
   └─────────────┘   TaskResult  └─────────┬───────┘                       └──────┬───────┘
                                            │                                     │
                                  invokes user fn                          ┌──────┴──────┐
                                            │                              │ Hosted via  │
                                            ▼                              │ HTTP +      │
                                   ┌─────────────────┐                     │ classifier  │
                                   │   TaskContext   │                     └──────┬──────┘
                                   │  (ctx.input,    │                            │
                                   │   ctx.metadata, │                            │
                                   │   ctx.cancel,…) │                            ▼
                                   └────────┬────────┘                  ┌──────────────────┐
                                            │ flush / suspend /         │   Foundry Task   │
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
                                  │  (~/.durable-tasks/<agent>/<sess>/…)   │
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
- The `TaskProvider` is an abstraction over the durable store. Two
  concrete providers ship: `HostedTaskProvider` (HTTP-backed, used
  when the platform is detected) and `LocalFileTaskProvider`
  (JSON-on-disk under `~/.durable-tasks/<agent>/<session>/<task>.json`
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
  consumers. The framework never touches a stream from the durable
  path.

### §4. Glossary (forward-referenced)

| Term | Meaning |
|---|---|
| **Task** | A unit of durable work, identified by `task_id`, persisted in the task store. |
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

### §5. The durable task primitive

A durable task is created by decorating a single async function:

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
| `suspended` | Handler called `ctx.suspend(output=...)` and returned. Awaiting `.run()` / `.start()` to bring it back to life. |
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
`ctx.suspend(output=...)`) is the **output**, also JSON-serialized.

| Bound | Limit | Raised as |
|---|---|---|
| Per-input maximum size | **2 MB** after JSON serialization, for the function input AND each individual queued steering input. | `InputTooLarge` from `.start()` / `.run()` — pre-network, at the call site. |
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
- A snapshot of every touched `ctx.metadata` namespace at every
  terminal-of-turn boundary (suspend, complete, cancel, raise,
  steering drain, `exit_for_recovery`) and at every explicit
  `metadata.flush()` call.
- Lifecycle counters: `retry_attempt`, `recovery_count` (the
  `expiry_count` of the lease record), `_last_input_id` (the
  optional caller-provided chain head — see §11).
- A per-turn `_turn_started_at` ISO-8601 UTC timestamp used by the
  watchdog (§14) to compute remaining budget across crashes.
- Steering state (`pending_inputs` queue, `cancel_requested`,
  `drain_in_progress`, `active_input`, `next_input_seq`) for
  steerable tasks (§12).
- The handler's terminal outcome: `payload["output"]` (set on
  successful completion for `ephemeral=False` tasks, and on
  `ctx.suspend(output=X)` when `X != None` — see §20 "Output
  field lifecycle" for the asymmetric write-only semantics),
  structured `error` dict on failure, `suspension_reason` on
  suspend.

The framework does NOT persist:

- Handler-local variables.
- In-memory closures over the handler's body.
- Caller-provided callbacks or futures (those are bound to a single
  lifetime; a crash discards them).
- Streaming events (those live in the streaming subpackage, which has
  its own backings; see Part VI).
- Any bulk data the developer chooses to compute. The developer is
  responsible for that — typically through a sibling framework
  (LangGraph checkpoint, custom DB, blob storage) with only a small
  reference token in `ctx.metadata`.

The dividing line is "what does the framework need to decide
`entry_mode` and reproduce `ctx`?" — that is what it persists; nothing
more.

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
   self), new `lease_expires_at`, bumps `lease_expiry_count` IF the
   previous lease had actually expired (not bumped for same-owner
   dead-instance handoff). This PATCH MUST be guarded by the read
   `etag` for CAS safety.
2. Reads the (now self-owned) record, looks up the registered
   resume callback by `source.name` (§21), invokes the handler
   with `ctx.entry_mode="recovered"` and the persisted `ctx.input`
   re-hydrated.
3. From the handler's perspective, the recovery looks identical to
   a fresh entry except that `entry_mode == "recovered"` and any
   `ctx.metadata` writes from the previous lifetime are already
   present.

**Crash-recovery does NOT consume the retry budget** (§15). A
lifetime that died before the handler raised does not advance
`retry_attempt`.

**Pattern — at-most-once side effect across recovery:**

```python
if ctx.metadata.get("dedup_token") is None:
    token = uuid4().hex
    ctx.metadata["dedup_token"] = token
    await ctx.metadata.flush()      # fence
    await do_side_effect(idempotency_key=token)
# crash-recovered lifetimes re-issue the call with the SAME token,
# letting the downstream system de-dupe.
```

This pattern is the standard answer to "I crashed mid-effect; how
do I avoid duplicate effects?" The framework does NOT provide
exactly-once semantics — the developer issues the dedup token and
fences it before the effect.

### §11. Suspend, resume, and multi-turn

`await ctx.suspend(output=...)` is the explicit "this turn is done;
park me; wake me when the caller has more input" boundary. It:

1. Transitions the stored status from `in_progress` to `suspended`.
2. Persists a snapshot of every touched metadata namespace.
3. Persists the optional `output` envelope.
4. Clears `payload["input"]` (and the corresponding attachment if
   the input was promoted) — the consumed input is no longer needed
   and would only inflate the next payload write.
5. Clears `_steering["active_input"]` (mechanism state lives, but
   the consumed input value goes).
6. Resolves the caller's `.run()` / `.start()` with a
   `Suspended(output=...)`-bearing `TaskResult(status="suspended")`.

The next `.run(task_id=same, input=new)` or
`.start(task_id=same, input=new)` transitions the status back to
`in_progress` and re-invokes the handler with
`ctx.entry_mode="resumed"`, `ctx.input=new`, and `ctx.metadata`
re-hydrated.

This same machinery is what multi-turn conversations and
human-in-the-loop approval flows ride. The framework does NOT
distinguish "multi-turn" from "single-call with one suspend" — they
are the same primitive applied iteratively.

#### Chain identity: `input_id` and `if_last_input_id`

Both `.run()` and `.start()` accept two optional keyword arguments
that thread caller-supplied chain identity through the persisted
record:

- **`input_id`** — record-only. The framework writes
  `payload["_last_input_id"] = input_id` after accepting the input;
  no precondition is checked.
- **`if_last_input_id`** — precondition. The framework requires the
  stored `_last_input_id` to equal `if_last_input_id` (the
  predecessor the caller claims to be extending). Mismatch raises
  `LastInputIdPreconditionFailed` (a subclass of
  `TaskPreconditionFailed`).

Implementations MUST reject `if_last_input_id` provided without
`input_id` (TypeError at the call site). The pair is orthogonal:
`input_id` alone is idempotency / chain-head tracking;
`(input_id, if_last_input_id)` together is HTTP-`If-Match`-style
chain extension.

### §12. Steering primitive

`@task(steerable=True)` upgrades a task from "one input at a time"
to "callers can queue a new input while the handler is mid-flight."

#### What `.start()` does on an in-flight steerable task

Non-steerable (default): `.start()` against `in_progress` raises
`TaskConflictError`.

Steerable, against `in_progress`:

1. The new input is **queued** at the tail of an internal
   pending-inputs FIFO.
2. The cancel signal is raised on the currently-executing turn —
   `ctx.cancel.is_set()` becomes True for the handler that is
   running right now. `ctx.pending_input_count` flips from 0 to the
   live backlog size.
3. A new `TaskRun` handle is returned to the caller. Its `.result()`
   resolves with **whatever the next turn emits** — the caller is
   treated as the *steerer* of the next turn.

If the steering queue is at its cap (9), `.start()` raises
`SteeringQueueFull`.

#### What the first turn's caller sees

The first turn's caller observes the **natural multi-turn outcome**
— there is no separate "supersede" mechanism on the public surface:

| Handler ends turn 1 with... | First caller's `TaskResult` |
|---|---|
| `return await ctx.suspend(output=X)` | `TaskResult(status="suspended", output=X, suspension_reason=R)`. The framework then re-enters for the queued steering input. |
| `return value` | `TaskResult(status="completed", output=value)`. The task is terminal; the queued steerer's `.result()` raises `TaskConflictError(current_status="completed")`. |
| `raise SomeError` | `.result()` raises the appropriate typed exception. Task is terminal; queued steerers raise `TaskConflictError(current_status="failed")`. |

The handler's emitted `output=` via `ctx.suspend(...)` is delivered
**unconditionally** to the first caller; it is NEVER replaced by what
a later turn produces.

#### Cooperative cancellation in steering

`ctx.cancel` is advisory. The framework signals it when a steering
input arrives (alongside the cause counter `ctx.pending_input_count`),
but does not preempt the handler. The handler decides:

- **A — Yield immediately.** Check `ctx.cancel.is_set()` (or
  `ctx.pending_input_count > 0`) at the next boundary and
  `return await ctx.suspend(output=...)` right away.
- **B — Wind down to a safe checkpoint.** Finish the current tool
  call / token batch, persist a clean checkpoint, then
  `return await ctx.suspend(output=...)`.
- **C — Ignore cancel and finish.** Do not read `ctx.cancel`; let
  the handler run to completion. The task ends; the queued steerer
  gets a `TaskConflictError`.

#### Steering observability fields

On a steering-driven re-entry, `TaskContext` exposes:

- `ctx.is_steered_turn: bool` — `True` iff this turn was constructed
  by the steering-drain code path. False for every other entry path.
  Orthogonal to `entry_mode`: `(entry_mode="recovered",
  is_steered_turn=True)` is legal.
- `ctx.pending_input_count: int` — live count of currently queued
  steering inputs (reads against the durable record, not a local
  snapshot, so it reflects the backlog as of the read). Reads as 0
  for non-steerable tasks. Useful for "I am three turns behind, I
  should short-circuit even harder" decisions.

#### Composing multi-turn + steering

A task can be both steerable AND multi-turn. They are the SAME
mechanism, not orthogonal modes. Every turn's `ctx.suspend()`
checkpoint is the boundary at which the next queued steering input
(if any) drives the next turn.

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
    return await ctx.suspend(output="(pre-empted)")
raise RuntimeError("ctx.cancel set with no recognised cause")
```

The handler's choice of terminal shape (return / raise / suspend)
controls the `TaskResult` the caller observes. The framework does
NOT pick the terminal shape on the handler's behalf.

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
  persisted `_turn_started_at` and fires immediately if elapsed.
- Clock skew is clamped to `[0, timeout]` in both directions.
- **Known gap on steering drain re-entry:** the canonical Python
  implementation spawns the watchdog ONCE per `_execute_task`
  invocation; steering drain re-enters in-place inside
  `_execute_task_loop` without spawning a fresh watchdog. The
  steered turn inherits whatever budget remained on the original
  watchdog. The persisted `_turn_started_at` IS stamped per drain
  (§52 Phase 1), so a CRASH-then-recover from a drained turn
  correctly honors the new turn's budget; the in-process drain
  path itself does not. Other-language implementers SHOULD spawn
  a fresh watchdog per drain to honor the design intent.

The framework MUST persist `payload["_turn_started_at"]` (ISO-8601
UTC) at every turn-start boundary: fresh entry, suspended -> in_progress
resume, steering drain re-entry. It is NOT re-stamped on crash
recovery — that is precisely what allows the watchdog to honor the
original budget across crashes.

### §15. Retry

`@task(retry=RetryPolicy(...))` configures the framework's retry
behavior for handler-raised exceptions.

`RetryPolicy` parameters:

| Field | Default | Meaning |
|---|---|---|
| `max_attempts` | `3` | Total failure-retry budget across all lifetimes. Counts the original try. |
| `initial_delay` | `1 second` | Delay before the first retry. |
| `backoff_coefficient` | `2.0` | Multiplier for exponential backoff. |
| `max_delay` | `60 seconds` | Cap on per-retry delay. |
| `jitter` | `True` | Add randomized jitter to delays. |
| `retry_on` | `None` (all exceptions) | Tuple of exception types to retry; others propagate. |

Presets: `exponential_backoff()`, `fixed_delay(delay)`,
`linear_backoff()`, `no_retry()`.

Semantics:

- **`retry_attempt` is the cross-lifetime counter.** Persisted as
  `payload["_retry_attempt"]`. Re-hydrated on every handler entry.
  Increments only when the handler RAISES (not on crash). Reset
  to 0 explicitly on steering drain (§52). For successful
  completion, the canonical Python implementation does NOT also
  reset (the `_handle_success` PATCH writes only metadata + output);
  this is benign for `ephemeral=True` tasks (record deleted) but
  leaves the counter populated in `ephemeral=False` records. Other-
  language implementers SHOULD also reset on success for symmetry.
- **Crash recovery does NOT consume the budget.** A lifetime that
  is gone before the handler raised does not advance `retry_attempt`.
- **Suspend bypasses retry.** A handler that calls
  `ctx.suspend(...)` is not a failure; the retry counter is
  unaffected.
- When `retry_attempt >= max_attempts`, the framework gives up:
  it stops re-invoking; the awaiting caller observes `TaskFailed`
  with the last captured error.

#### Interim retry persistence (the `error` field across attempts)

Between every failed attempt and the next retry the framework
PATCHes the in-progress record with:

```
error   = {"type": "<ExceptionClassName>",
           "message": "<str(exc)>",
           "attempt": <current_attempt_number>}
payload = {"_retry_attempt": <attempt + 1>}
```

— the `error` field reflects the **most recent** failed attempt
(each retry overwrites the previous one); the `_retry_attempt`
bump is what makes the budget survive crashes between attempts.
The status stays `in_progress` throughout. The interim error
write deliberately omits a full `traceback` to keep the record
small — it is a watermark, not a forensic dump.

When the budget is exhausted (or the exception is non-retryable),
`_handle_failure` runs:

- For `ephemeral=True` (the default): the record is DELETED
  entirely; nothing survives on disk. The caller observes
  `TaskFailed` raised from `.result()`.
- For `ephemeral=False`: PATCH `status="completed"` with a
  richer `error` dict carrying either:
  - `{"type": "exhausted_retries", "attempts": N, "last_error": ...,
    "last_error_type": ..., "traceback": ...}` if retries were
    attempted, OR
  - `{"type": "<ExceptionClassName>", "message": ..., "traceback": ...}`
    if no retry policy was configured or the exception was
    non-retryable.
  The caller observes `TaskFailed(task_id, error_dict)` carrying
  whichever shape applies.

**Developer-facing inspection of `error` during interim retries.**
There is NO supported public API today. `TaskRun.refresh()`
mirrors only `status`, `lease.expiry_count`, and
`payload["metadata"]` onto the handle — it does NOT pull the
top-level `error` field. The framework's own provider is
internal (Part IV visibility callout). The only ways a separate
observer can learn "what just failed, which attempt am I on"
mid-retry today are:

- Read framework logs (`logger.warning("Task %s attempt %d failed
  (%s: %s), retrying in %.1fs", ...)`).
- Reach into the internal provider (test-only pattern; not
  supported in production user code).
- Run a parallel HTTP client against the hosted task store.

This is the same observability asymmetry described for
`payload["output"]` in §20: the record carries useful state, but
the public surface does not expose it. Implementations adding a
public read API for `task_record.error` SHOULD also define the
clearing semantics — particularly, whether the interim `error`
should be cleared on a successful eventual completion (today it
is overwritten implicitly because `_handle_success` is the
opposing branch; but on the `ephemeral=False` success path,
`_handle_success` writes payload only — `error` from the last
failed attempt is left intact in the persisted record).

### §16. Shutdown and `exit_for_recovery`

The container can be shut down at any time (deployment, rolling
restart, eviction). The framework sets `ctx.shutdown` when it
receives the shutdown signal. The handler has three legitimate
responses:

| Shape | When to use | Stored outcome | Caller observes |
|---|---|---|---|
| `await ctx.exit_for_recovery()` | Container shutting down AND you want this turn re-entered later. | `in_progress` (preserved across shutdown). | `TaskCancelled`. |
| `await ctx.suspend(output=X)` | Handler reached a clean checkpoint AND wants to expose `X` to the caller. | `suspended` (caller must `.run()` again). | `TaskResult(status="suspended", output=X)`. |
| `raise asyncio.CancelledError()` | Handler decided to abort but the task is conceptually done. | For `ephemeral=True` (the default): record deleted on terminal exit. For `ephemeral=False`: see "Cancellation persistence" note below. | `TaskCancelled`. |

#### Cancellation persistence (known gap)

The canonical Python implementation's cancel path
(`asyncio.CancelledError` observed inside `_execute_task_loop`)
ONLY (1) flushes metadata and (2) resolves the caller's
result-future with `TaskCancelled`. It does NOT write a terminal
status PATCH or call `_handle_success`/`_handle_failure`.

For `ephemeral=True` (the default), this is observationally fine
because the next periodic recovery scan or the next caller will
not find the record (no PATCH-to-terminal happened, but the lease
expires; subsequent reclaim re-enters with `entry_mode="recovered"`,
where the handler must use `ctx.metadata` watermarks to avoid
re-doing work). For `ephemeral=False`, the record stays
`in_progress` after a cancel, and recovery will re-enter the
handler — which may not be what the operator wanted.

Other-language implementers SHOULD write a terminal-status PATCH
on cancel for `ephemeral=False` tasks (status = `completed`,
error or a `cancelled: true` marker) to make the cancel
durable. The canonical Python implementation treats this as a
known gap; for the common `ephemeral=True` case it is invisible.

`ctx.exit_for_recovery()` is special. Invoking it:

1. Returns a framework sentinel that the manager recognizes (the
   user code does `return await ctx.exit_for_recovery()`).
2. Flushes all touched metadata namespaces.
3. **Releases ownership** of the persisted record so the next
   process can take over (force-expires the lease).
4. Leaves status as `in_progress` (NOT `suspended`).
5. Signals the in-process caller with `TaskCancelled`.
6. Preserves any queued steering inputs — they are NOT drained
   during shutdown; on recovery they remain queued.

Misuse: calling `ctx.exit_for_recovery()` when `ctx.shutdown.is_set()
== False` MUST raise `RuntimeError` at the call site. This makes
misuse loudly visible to operators (the task ends `failed`, not
silently `in_progress`).

### §17. Metadata namespaces

`ctx.metadata` is a **callable namespace facade** for the small,
durable, per-task state the handler owns:

- `ctx.metadata["key"] = value` — read/write the **default**
  namespace, persisted at `payload["metadata"]`.
- `ctx.metadata("session")["upstream_id"] = sid` — read/write a
  **named** sibling namespace, persisted at
  `payload["metadata:session"]`.

Each namespace is independent: a write to one does not dirty the
other; `flush()` on one persists only that namespace's data.

`metadata.flush()` is the fence the developer uses to make
at-most-once side-effect patterns work across a crash. The framework
**auto-flushes** all touched namespaces at every terminal-of-turn
boundary, so writes the developer forgets to flush are still durable
across a graceful boundary. Explicit `flush()` is for mid-handler
fence semantics.

**Naming convention:** namespaces and top-level metadata keys
starting with `_` are RESERVED for the framework. The primitive
treats this as a convention at the API surface; layers built on top
(e.g. the responses framework's `_responses` namespace) MAY enforce
it more strictly.

`TaskMetadata` MUST expose dict-like semantics
(`__getitem__`/`__setitem__`/`__contains__`/`__iter__`/`.get()`/`.to_dict()`)
plus:

- `flush()` — persist this namespace only.
- `increment(key)` — in-memory atomic numeric increment **on the
  metadata namespace object** (read/modify/write under an in-
  memory lock). The change is NOT pushed to the store until the
  next `flush()` / auto-flush. This is NOT a store-level
  compare-and-swap; concurrent processes incrementing the same
  key would race at the store level. Use for handler-local
  counters that get flushed at clean boundaries; for cross-
  process atomic counters, use the store's CAS protocol directly
  via the provider.
- `append(key, value)` — append to a list-valued key. Same
  in-memory semantics as `increment`: atomic within the namespace
  object, NOT atomic against the durable record.

Flush failures are logged, not raised — a failed flush should not
crash a handler. The framework retries on the next flush call or
auto-flush boundary.

---


## Part III — Storage contract (wire-level)

This part documents how the framework projects the programming model
onto the durable task record. The HTTP routes, request/response
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
| `tags` | map of string -> string | framework + caller | `create` (framework stamps `_task_name`); caller-set tags allowed. |
| `error` | object \| null | framework | on handler raise. |
| `suspension_reason` | string \| null | framework | on suspend. |
| `source` | object | framework | `create` (§21). |
| `attachments` | object \| null | framework + developer | on input promotion / drain / suspend / orphan cleanup (§23). |
| `etag` | string | server | every server-issued response. |
| `created_at` | ISO-8601 string | server | `create`. |
| `updated_at` | ISO-8601 string | server | every PATCH. |
| `started_at` | ISO-8601 string \| null | server | first `in_progress` transition. |
| `completed_at` | ISO-8601 string \| null | server | terminal transition. |

Caller-controlled fields (`tags` keys NOT starting with `_task_`,
`title`, `description`) are passed through verbatim. Framework-owned
fields MUST NOT be set by caller code.

### §20. Framework-reserved payload keys

`payload` is the JSON object that holds both the framework's
runtime state and the developer's metadata. The framework reserves
the following top-level keys, all starting with `_` or named
`input`/`metadata`/`output`:

| Key | Type | Lifetime | Meaning |
|---|---|---|---|
| `input` | any JSON value, or a ref dict (§23) | Set on every `in_progress` transition; cleared at suspend; cleared by drain after consumption. | The current input value (or a ref to its attachment). |
| `metadata` | object | Persisted at boundaries; auto-flushed. | The DEFAULT user metadata namespace. |
| `metadata:<ns>` | object | Same as above. | NAMED user metadata namespace `<ns>`. |
| `output` | any JSON value | Set in two scenarios: (1) handler returns normally on `ephemeral=False` tasks — `payload["output"]` is the serialized return value; (2) handler `ctx.suspend(output=X, ...)` with `X != None`. NEVER set on failure (use `error` field). NEVER cleared on resume — see "Output field lifecycle" note below. | Caller-observable terminal/suspend snapshot. |
| `_last_input_id` | string \| null | Set when caller supplies `input_id`. | Chain-head tracking (§11). |
| `_turn_started_at` | ISO-8601 UTC string | Set at every turn-start boundary; NEVER re-stamped on recovery. | Source of truth for the per-turn watchdog (§14). |
| `_retry_attempt` | integer | Incremented on handler raise; reset to 0 on steering drain. (Not also reset on success in the canonical Python implementation.) | Durable retry counter (§15). |
| `_steering` | object (see below) | Only present on steerable tasks. | Steering mechanism state (§12). |

`_steering` object shape:

| Sub-key | Type | Meaning |
|---|---|---|
| `pending_inputs` | array of input values OR refs (§23) | FIFO of queued steering inputs. |
| `next_input_seq` | integer | Monotonic counter for promoted-attachment key allocation (NEVER reused). |
| `cancel_requested` | boolean | Durable cancel signal; set on steering append; cleared after drain when pending is empty. |
| `drain_in_progress` | boolean | True between the start of a drain PATCH and the next turn-start; protects against partial drain on crash. |
| `active_input` | any JSON value OR ref | The single input being drained (mirror copy used by the race-recovery contract). Cleared at suspend / terminal. |

Implementers in other languages MUST use these exact key names. A
process built in language X must be able to recover a task created
by language Y.

Keys NOT in this table are caller-controlled (e.g. user metadata
namespaces); the framework leaves them alone.

#### Output field lifecycle (`payload["output"]`)

The `output` field has asymmetric write/read semantics — important
for re-implementers to get right and for callers to understand:

**Write sites (only two):**

1. **Normal completion on `ephemeral=False`** — `_handle_success`
   PATCHes `status="completed"` with `payload["output"] = <serialized
   return value>`. For `ephemeral=True` (the default), the whole
   record is DELETED on terminal success; no output is persisted
   anywhere.
2. **Suspend with non-null output** — `_handle_suspend` PATCHes
   `status="suspended"` with `payload["output"] = <serialized X>`
   when the handler called `ctx.suspend(output=X, ...)` with
   `X != None`. Suspending with `output=None` (or omitting `output=`)
   does NOT write the field, so any prior value remains.

**No clear sites.** The resume PATCH (`_start_existing_task`) does
NOT clear `payload["output"]`. A suspend → resume → suspend cycle
where the second suspend passes `output=None` leaves the persisted
record carrying the FIRST suspend's output value. This is stale
data, not a current snapshot, after the first resume.

**No framework read sites.** The framework itself never reads
`payload["output"]` back from the store. The value delivered to
the caller's `TaskResult.output` is the IN-PROCESS result-future
value at terminal time, not a re-read of the persisted record.

**No developer-accessible read path.** `TaskRun.refresh()` mirrors
`status`, `lease.expiry_count`, and `payload["metadata"]` onto the
handle but does NOT expose `payload["output"]`. The `TaskProvider`
interface and its concrete implementations (`HostedTaskProvider`,
`LocalFileTaskProvider`) are **internal** — they live in `_`-
prefixed modules and are NOT re-exported from
`durable/__init__.py`'s `__all__`. The only ways to read the
persisted `output` slot today are: (a) the test suite's pattern
of importing private modules (e.g. `from durable._local_provider
import LocalFileTaskProvider`), which framework consumers MUST
NOT do in production; (b) writing a parallel client against the
hosted task store's HTTP API. There is no supported developer
read path.

**Implications:**

- Two processes never coordinate via `payload["output"]`. The
  first caller's in-process future is the only delivery channel.
- A handler that suspends multiple times SHOULD always pass an
  explicit `output=` (or `output=None` if the caller expects
  cleared) so the persisted state matches the handler's current
  intent. The framework does not actively reconcile.
- A new release that adds a developer-facing read API (e.g.
  `Task.get_last_output(task_id)`) MUST also add a clear-on-resume
  PATCH and define the multi-turn ownership semantics, or the new
  API will return stale values across resume boundaries.
- The error field is NOT subject to this issue — `_handle_failure`
  writes `error` and never `output`, so the two never share a slot.

### §21. Framework-reserved tag keys and `source` shape

#### Reserved tag keys

The framework stamps the following `tags` entries on `create`:

| Tag key | Value | Purpose |
|---|---|---|
| `_task_name` | The decorator's `name` (or `fn.__qualname__` fallback). | Server-side `LIST` filtering by task name. |

Tag keys starting with `_task_` are RESERVED. Caller-supplied tags
using this prefix are stripped at the call site with a warning;
the framework does not pass them to the server.

#### `source` shape

The framework stamps `source` on `create`:

```
{
   "type":           "agentserver.task",
   "name":           "<the decorator's name (or fn.__qualname__)>",
   "server_version": "<sdk_name>/<sdk_version> (<runtime>/<version>)"
}
```

`source.name` is the **canonical identity anchor** for recovery
routing — the framework looks up the registered handler callback
by matching `source.name` against the decorator-supplied names.
`source.type` is currently a single fixed string but is reserved
for future namespacing.

### §22. Lease structure and ownership semantics

`lease` is a sub-object with the following fields:

| Field | Type | Meaning |
|---|---|---|
| `owner` | string | `<agent_name>\|session:<session_id>` (§7). Stable across process lifetimes. |
| `instance_id` | string | `worker-<pid>-<rand8hex>-<unix_seconds>`. Fresh per process. |
| `generation` | integer | Increments each time the lease is re-acquired with a different `instance_id`. Mirrored to `ctx.recovery_count`. The local provider AND the hosted task store both bump this. |
| `expires_at` | ISO-8601 UTC string | When the lease expires (and another process may reclaim). |
| `expiry_count` | integer | Number of times ownership has changed via **actual expiry** (i.e. lease was reclaimed because the prior lease's `expires_at` passed, NOT because the same owner restarted). **Server-only counter** — the framework never writes this field (it is not on `TaskPatchRequest`). The hosted task store bumps it. The local file provider does NOT bump it (known divergence — `expiry_count` stays 0 forever in local mode). Mirrored to `TaskRun.lease_expiry_count`. |

The framework's interaction with the lease:

- On `create`, the framework sets `lease_owner = self.owner`,
  `lease_instance_id = self.instance_id`, and
  `lease_duration_seconds = 60` (the framework default).
- The lease renewal loop (§56) renews at half the lease duration
  (every 30s by default).
- Any payload PATCH the framework issues piggybacks
  (`lease_owner`, `lease_instance_id`, `lease_duration_seconds`)
  to refresh the lease as a side effect. The renewal loop skips
  redundant heartbeats when a recent piggyback already refreshed it.
- On reclaim (§54), the framework PATCHes the lease to itself with
  `if_match: <last-seen etag>` for CAS.
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
   (server-side, in the hosted store; NOT in the local provider —
   see the table above).

**Important: the framework never writes `expiry_count`.** It is not
a field on `TaskPatchRequest` (only `lease_owner`,
`lease_instance_id`, `lease_duration_seconds` are writable). The
hosted task store is solely responsible for incrementing it on
expiry-triggered ownership change; the local file provider
preserves whatever value is already there (so local-mode tests
that need to assert expiry-counter behavior have to use the
hosted provider or assert against `lease.generation` /
`ctx.recovery_count` instead).

### §23. Attachments and input promotion

The hosted task store provides a second per-task storage slot,
`attachments`, alongside `payload`. The two stores have different
budgets:

| Slot | Per-task cap | Per-value cap | Entry count cap |
|---|---|---|---|
| `payload` | 1 MB | n/a (shared) | unlimited keys |
| `attachments` | n/a (per-entry only) | 2 MB per attachment | 20 attachments max |

`attachments` lets the framework lift the per-input ceiling from
"however much fits in payload alongside everything else" to
**2 MB per input** without evicting metadata budget.

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

#### 23.2 Thresholds (framework-owned)

The framework promotes a value to an attachment ONLY when its
serialized form exceeds a channel-specific threshold:

| Channel | Threshold | Attachment key |
|---|---|---|
| Function input (`payload["input"]`) | > 200 KiB | `_input` |
| Each steering input | > 20 KiB | `_steering_input_<seq>` |

Different thresholds because:

- The function input is set once per turn-start. A 200 KiB inline
  budget keeps small inputs cheap and only spills clearly-large ones.
- Steering inputs may accumulate (up to 9 queued). A 20 KiB
  threshold caps the worst-case inline payload contribution from
  steering at ~180 KiB even when the queue is full.

Sizes are measured in bytes of canonical JSON
(`sort_keys=True`, separators `(",", ":")`).

#### 23.3 Wire shapes — two only

A slot that would hold an input (`payload["input"]`, an entry in
`_steering["pending_inputs"]`) is represented in exactly one of two
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

`payload["_steering"]["next_input_seq"]` is the monotonic counter
the framework uses to derive `_steering_input_<seq>` keys. Critical
invariants:

- **Advances ONLY on promotion.** Inline steering appends do not
  bump `next_input_seq`.
- **Never reused.** A drained-and-deleted key is never re-allocated;
  the next promoted append always uses the current
  `next_input_seq`, then `next_input_seq += 1`.
- **Stable for surviving entries.** A drain pops the head of
  `pending_inputs` and (if it was a ref) deletes the corresponding
  `_steering_input_<seq>` attachment. It does NOT renumber any
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

- Per-attachment value: **2 MB** serialized.
- Per-task attachment count: **20**.

The framework enforces:

- **Per-value (2 MB) cap** on EVERY write site (create AND patch)
  in BOTH providers (hosted and local) — pre-network — raising
  `InputTooLarge` / `AttachmentTooLarge`.
- **Per-task count (20) cap** on `create` and on `patch` paths
  that can read the current count first. The hosted provider's
  `update()` site **does NOT** enforce the count today (no
  current-state read; relies on the server) — `AttachmentLimitExceeded`
  is raised by the framework only at create-time and by the local
  provider's patch (which can cheaply count). The hosted PATCH
  relies on the server rejecting at the cap.

Promoted-input PATCHes count toward the per-task attachment count.
On steering append (which goes through framework code that DOES
fetch current state), the framework counts current attachments +
"about to be added" against the cap before issuing the PATCH.

#### 23.8 Atomic co-writes

These transitions MUST be single PATCHes carrying BOTH `payload` and
`attachments`:

1. **Promote on `.start()` (fresh)**: `attachments["_input"] = <value>`
   + `payload["input"] = {ref}` (CREATE on the hosted store).
2. **Promote on resume**: same fields, but PATCH.
3. **Suspend with promoted input**: `payload["input"] = null`,
   `payload["_steering"]["active_input"] = null`,
   `attachments["_input"] = null` (delete) — IF the input was a ref.
4. **Steering append (promoted)**: `payload["_steering"]["pending_inputs"]
   += [{ref}]`, `attachments["_steering_input_<seq>"] = <value>`,
   `payload["_steering"]["next_input_seq"] += 1`,
   `payload["_steering"]["cancel_requested"] = true`.
5. **Steering drain (promoted entry)**: `payload["_steering"]["pending_inputs"]`
   without the popped head, `attachments["_steering_input_<seq>"] = null`,
   plus the new turn's input/metadata/etc.

Splitting any of these into multiple PATCHes opens a crash window
where the attachment exists without its ref (or vice versa). The
framework treats this as a single-PATCH invariant.

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
                                    │  ctx.suspend()
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

### §25. ETag (optimistic concurrency)

The framework uses the hosted store's ETag/CAS protocol per the
Foundry Task Storage Protocol spec. Two implementation notes
relevant to *this* framework:

- The service-returned `etag` value is passed verbatim as
  `If-Match` on the next PATCH. The framework does NOT strip
  surrounding quotes, normalize whitespace, or otherwise rewrite
  it.
- 412 (precondition failed) on a `If-Match` PATCH is a CAS
  conflict. The framework handles it depending on call site:
  retry-with-fresh-read for renewal / reclaim writes; raise
  `LastInputIdPreconditionFailed` for `if_last_input_id`
  preconditions; raise `EtagConflict` for low-level callers.

### §26. Recovery `POST /tasks/resume` endpoint

The framework exposes a single Starlette-compatible HTTP route to
allow the platform (or any external trigger) to invoke a
suspended task's resume callback:

```
POST /tasks/resume
Content-Type: application/json

{"task_id": "<task-id>"}
```

Response codes:

| Code | Meaning |
|---|---|
| `202 Accepted` | Resume dispatched. |
| `400 Bad Request` | Malformed JSON, missing/non-string `task_id`. |
| `404 Not Found` | Task not found OR not in any resumable state (e.g. missing record entirely; the framework's `handle_resume` raises an exception whose message contains the substring `"not found"`). |
| `409 Conflict` | Task is already in a non-resumable state — `handle_resume` raised an exception whose message contains `"not 'suspended'"`, `"already"`, or `"conflict"`. The typical case: caller tried to resume a task whose status is `in_progress`. |
| `503 Service Unavailable` | Task manager singleton not initialized — `get_task_manager()` raised `RuntimeError`. |
| `500 Internal Server Error` | Any other unhandled exception during `handle_resume`. |

The body is empty on all responses. Implementations exposing the
framework over HTTP MUST register this route at exactly this path.

This is the only HTTP route the framework itself contributes. All
other HTTP plumbing (responses, invocations) lives in their
respective packages.

---

## Part IV — Provider abstraction (storage backends)

> **Visibility:** Everything in this part is **framework-internal**.
> The `TaskProvider` interface and the two concrete providers
> (`HostedTaskProvider`, `LocalFileTaskProvider`) are NOT part of
> the public surface defined in Part V — in the canonical Python
> implementation, all of these live in `_`-prefixed modules
> (`_provider.py`, `_client.py`, `_local_provider.py`) and are
> NOT re-exported from `durable/__init__.py`'s `__all__`. The
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
  `TaskRun.delete()` shields user code from these by catching
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
- **Logging policy:** A custom `TaskApiLoggingPolicy` logs
  request/response method + URL + status + the same 256-char body
  prefix, with secrets redacted.
- **Required dependency:** A `TokenCredential` factory must be
  installed (e.g. via `azure-identity` in the Python implementation).
  The hosted provider does not function without a credential
  source.

### §29. Local provider (file-backed)

Selected when `FOUNDRY_HOSTING_ENVIRONMENT` is NOT set (i.e. local
dev, tests). State lives under
`~/.durable-tasks/<agent_name>/<session_id>/<task_id>.json` by
default; override with `AGENTSERVER_DURABLE_TASKS_PATH`.

Implementation MUST:

- Generate fresh ETags on every write (e.g. SHA of the JSON bytes).
- Reject `update()` calls whose `if_match` does not match the
  current ETag.
- Apply `payload` shallow merge, `tags` null-as-delete merge,
  `attachments` null-as-delete merge — identical to the hosted
  provider's semantics. This is what makes "local feels like
  hosted" work: same merge rules, same recovery paths, same lease
  semantics.
- Validate attachment size + count BEFORE writing.
- Treat missing/corrupt files as `get() -> None`.
- Detect lease expiry against `expires_at` (UTC) and refuse renewal
  when an `if_match` mismatch indicates a competing process.

The local provider does NOT spawn HTTP; it does NOT need an event
loop beyond the framework's; it has no network failure modes.

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
| `_periodic_recovery_loop` | Every 300s (framework constant `_PERIODIC_RECOVERY_INTERVAL_SECONDS`). | Process-wide (one per manager). | Reclaim tasks that became reclaimable after cold-start. |
| `lease_renewal_loop` | Half the lease duration (default 30s). | One per active task. | Renew the lease before expiry. |
| `_timeout_watchdog` | One-shot sleep for `min(remaining, timeout)` seconds. | One per active task that declares a timeout. | Set `ctx.timeout_exceeded` then `ctx.cancel` when budget expires. |

All loops are interruptible via cancel events and MUST exit cleanly
on `TaskManager.shutdown()`. The lease renewal loop additionally:

- Skips its tick when a recent payload PATCH already refreshed the
  lease as a side effect (avoids redundant heartbeats).
- After successful renewal, invokes an optional steering-poll
  callback that reads the steering queue and short-circuits the
  current turn if a new input has arrived since last drain.
- Signals an external cancel-event on 3 consecutive failures OR
  immediately on `evicted` classification.

The periodic recovery loop additionally:

- Walks `task_info.attachments` for `_steering_input_*` keys whose
  ref slot is no longer present in `pending_inputs` and PATCHes
  them away (orphan cleanup — defense in depth against a partial
  crash between an attachment add and the queue append).

---

## Part V — Public API surface

This part defines the language-agnostic shapes every implementation
MUST expose. Names are given in the Python style; idiomatic naming
in other languages is acceptable but the *behavior* and *parameters*
MUST match.

### §32. `task` decorator and `TaskOptions`

The `task` decorator wraps an `async def fn(ctx: TaskContext[I]) -> O`
function and returns a `Task[I, O]` handle.

```
@task(
    name:        str | None = None,                     # default: fn.__qualname__
    title:       str | Callable[[I, str], str] | None = None,
    timeout:     timedelta | None = None,
    ephemeral:   bool = True,
    retry:       RetryPolicy | None = None,
    steerable:   bool = False,
)
```

| Kwarg | Meaning |
|---|---|
| `name` | Stable identity for recovery routing — written to `source.name` and the `_task_name` tag. Always set explicitly in production code; changing it strands existing tasks. |
| `title` | Human-readable title (string or callable evaluating to one); written to `TaskInfo.title`. |
| `timeout` | Per-turn cooperative budget (§14). When elapsed, the framework sets `ctx.timeout_exceeded` then `ctx.cancel`. |
| `ephemeral` | If `True`, the framework deletes the persisted record on terminal exit. Default `True`. |
| `retry` | `RetryPolicy` for handler-raised exceptions (§15). |
| `steerable` | Enables `.start()`-on-`in_progress` to queue a steering input instead of raising `TaskConflictError` (§12). |

All decorator options are recovery-safe: after a crash the framework
only knows about the registered decorator's view; per-call overrides
would silently disappear. The framework offers `Task.options(**overrides)`
to derive a variant with overrides without re-defining the function.

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

### §33. `Task` handle

The decorated function becomes a `Task[I, O]` exposing exactly two
keyword-only entry points (no positional args):

```
async def run(
    *,
    task_id:           str,
    input:             I,
    input_id:          str | None = None,
    if_last_input_id:  str | None = None,
) -> TaskResult[O]: ...

async def start(
    *,
    task_id:           str,
    input:             I,
    input_id:          str | None = None,
    if_last_input_id:  str | None = None,
) -> TaskRun[O]: ...
```

`.run()` blocks until the task reaches a terminal-for-this-caller
state and returns a `TaskResult` (or raises a typed exception).

`.start()` returns immediately with a `TaskRun` handle the caller
can poll, stream, or `await handle.result()` on.

Both accept the same `input_id` / `if_last_input_id` chain primitives
(§11). Implementations MUST raise at the call site when
`if_last_input_id` is provided without `input_id`.

`Task` also exposes:

- `Task.options(**overrides) -> Task` — derive a new handle with
  different option values, sharing the same function.
- `Task.get_active_run(task_id) -> TaskRun | None` — look up the
  currently-running task by id. Behavior: (1) checks the in-process
  active-task table; if found, returns the bound `TaskRun`. (2)
  Otherwise consults the store via `provider.get(task_id)`. If
  the record exists with status `in_progress` and the lease is
  dead (per `_lease_is_dead`, §22), this method INLINE-RECLAIMS
  the task — same code path as `.start()`'s "reclaim sub-case"
  — and returns a `TaskRun` bound to the newly-spawned recovery
  execution. If the record does not exist OR status is not
  reclaimable from this process's perspective, returns `None`.
  Implementers SHOULD make this method idempotent against a
  recently-completed reclaim — calling twice in quick succession
  should not start two recovery executions.

There is no per-call override for `title` / `retry` / `steerable` /
`ephemeral` / `timeout` — all of those are decorator-configured for
recovery safety.

### §34. `TaskContext`

The single argument every handler receives. Properties:

| Property | Type | Description |
|---|---|---|
| `input` | `I` | The typed input value. |
| `entry_mode` | `"fresh" \| "resumed" \| "recovered"` | Why this turn started (§6). |
| `task_id` | `str` | Task identity. |
| `metadata` | `TaskMetadata` | Callable namespace facade (§17). |
| `cancel` | event-like (`asyncio.Event` in Python) | Set when cancellation is requested for any reason. |
| `shutdown` | event-like | Set when the container is shutting down. Precondition for `exit_for_recovery()`. |
| `timeout_exceeded` | `bool` | True once the per-turn timeout fired. Set BEFORE `cancel` (§13 ordering invariant). Never reset within a turn. |
| `cancel_requested` | `bool` | True once external `TaskRun.cancel()` was called. Set BEFORE `cancel`. Never reset within a turn. |
| `pending_input_count` | `int` | Live count of currently queued steering inputs. Designed to be computed on every access via an internal callable provider (NOT a stored snapshot) so it reflects inputs queued mid-handler. Reads as `0` for non-steerable tasks AND for any provider failure (failure-tolerant). **Known gap (canonical Python implementation):** the in-memory side-channel that updates the live count is not currently populated by the steering append path, so handlers observe `0` even when `ctx.cancel` is set by steering. Other-language implementers MUST wire the side-channel from the steering-append path so this property reflects reality; the spec invariant (live count) is the design intent. |
| `is_steered_turn` | `bool` | True iff this turn was constructed by the steering-drain code path. False otherwise. |
| `retry_attempt` | `int` | Cross-lifetime retry counter (§15). |
| `recovery_count` | `int` | Increments each time the task was re-acquired by a new lifetime. Mirrored from the lease's `generation` field at construction time. |

Methods:

```
async def suspend(*, output: Any = None, reason: str | None = None) -> Suspended: ...
async def exit_for_recovery() -> Any: ...
```

`suspend(output=, reason=)` — see §11. Implementations MAY accept
both positional and keyword shorthand for `output=`. MUST be used
as `return await ctx.suspend(...)` — the returned value is an
opaque framework sentinel that the manager interprets as "transition
to suspended"; storing or wrapping the sentinel without returning
it leaves the task in `in_progress` with no path back.

`exit_for_recovery()` — see §16. MUST raise `RuntimeError` if
`shutdown.is_set() == False`; otherwise returns a private framework
sentinel that the manager interprets to flush metadata, release the
lease, and preserve `in_progress` status. Like `suspend()`, MUST be
used as `return await ctx.exit_for_recovery()`.

Implementations MUST NOT expose public setters for any cause boolean
or counter. They are framework-owned read-only fields.

### §35. `TaskRun`

The handle returned by `.start()`. Useful members:

| Member | Description |
|---|---|
| `await run.result()` | Block until terminal-for-this-caller; returns `TaskResult` or raises a typed exception. |
| `await run.cancel()` | Signal external cancellation. MUST set `ctx.cancel_requested = True` BEFORE setting `ctx.cancel` (ordering invariant — handler observing `ctx.cancel` is guaranteed to see at least one cause boolean already True). The handler picks the terminal shape. |
| `await run.delete()` | Delete the persisted record. Idempotent. Provider exceptions whose message contains the substring `"not found"` (case-insensitive) MUST be re-raised as `TaskNotFound(task_id)`; other exceptions propagate unchanged. |
| `await run.refresh()` | Re-fetch status, lease expiry count, and metadata snapshot from the store. |
| `run.status` | Last known `TaskStatus`. |
| `run.metadata` | Last known metadata dict snapshot. |
| `run.lease_expiry_count` | Last known lease `expiry_count`. |
| `await run` | Awaiting the run is sugar for `run.result()`. |

**`TaskRun` is NOT an async iterable.** It does not implement
`__aiter__` / `__anext__`; there is no `async for chunk in run`
syntax. This is a deliberate design choice from spec 017 (unified
streaming): incremental streaming is a peer subpackage
(`azure.ai.agentserver.core.streaming`, Part VI), NOT a property
of the task handle. Producers emit to a `streams` registry id;
consumers attach via `streams.get(id).subscribe(after=...)`.

The two surfaces are decoupled because a stream may span multiple
task turns, multiple functions writing to the same id, or a
non-`@task` producer. Coupling stream iteration to `TaskRun`
would re-couple lifetime in ways spec 017 explicitly broke. Other-
language implementers MUST NOT add task-handle iteration as
"syntactic sugar" — it would re-introduce the very coupling we
removed. If a developer wants a single `await run` plus an
incremental stream, they explicitly attach to the streaming
registry (Part VI).

### §36. `TaskResult` and `Suspended`

`TaskResult[O]` is the caller-observable outcome of a single
`.run()` / `.result()` call. Two values for its status:

| `TaskResult.status` | Meaning | `output` |
|---|---|---|
| `"completed"` | Handler returned normally. | The return value. |
| `"suspended"` | Handler called `ctx.suspend(output=X)`. | `X` (the suspend envelope). |

Convenience properties: `is_completed`, `is_suspended`.
Also exposes `suspension_reason: str | None` (populated only on the
suspended branch).

This `TaskResult.status` literal is DIFFERENT from the four-value
`TaskStatus` literal (`pending|in_progress|suspended|completed`).
The four-value literal is the *stored lifecycle state*; the
two-value `TaskResult.status` is the *caller-observable outcome of
this single call*. Unsuccessful terminations (failure / cancel)
are stored as `completed` but communicated to the caller via typed
exceptions, never as a third `TaskResult.status` value.

`Suspended[O]` is the type the handler returns from
`return await ctx.suspend(output=X, reason=R)`. It is what the
framework writes into the suspend envelope and what the caller's
`TaskResult.output` carries on the suspended branch.

### §37. `TaskMetadata`

Mutable mapping-like type returned by `ctx.metadata` and
`ctx.metadata(name)`. See §17 for semantics.

Required surface:

```
metadata["key"]                # __getitem__
metadata["key"] = value        # __setitem__
"key" in metadata              # __contains__
for k in metadata: ...         # __iter__
metadata.get("key", default)   # MutableMapping behavior
metadata.to_dict()             # plain dict snapshot
await metadata.flush()         # persist this namespace only
await metadata.increment(key)  # atomic numeric increment
await metadata.append(key, v)  # append to a list-valued key
```

**Note: `flush_all()` is framework-internal.** A `flush_all()`
method exists on the canonical Python `TaskMetadata` class
(non-underscored, so technically callable from user code) but
its docstring explicitly frames it as the framework's lifecycle
helper — called by the manager at suspend / complete / fail /
drain / `exit_for_recovery` boundaries to persist every dirty
namespace in one pass. It is NOT documented in the user-facing
developer guide, has no public-API samples, and there is no
developer use case where it should be needed: the framework
already calls `flush_all()` automatically at every terminal-of-
turn boundary, so any namespace the handler touched is durable
without explicit action. Per-namespace `flush()` is the only
fence pattern developers should reach for (to commit a specific
namespace before a side-effect operation). Other-language
implementers SHOULD make the equivalent of `flush_all()` either
package-private or otherwise not exposed on the language's
developer-facing surface; the canonical Python implementation's
non-underscored naming is an oversight, not a design decision.

#### Namespace facade behavior

`TaskMetadata` is implemented as a **callable namespace facade**:

- **Default namespace.** `ctx.metadata` itself binds to
  `payload["metadata"]`. All dict-like operations on `ctx.metadata`
  directly target this namespace.
- **Named namespaces.** `ctx.metadata(name)` returns a sibling
  `TaskMetadata` instance bound to `payload["metadata:<name>"]`.
- **Auto-vivification.** A named namespace does NOT have to exist
  in the persisted record before access — calling
  `ctx.metadata("ns")` creates an in-memory empty namespace that is
  persisted on first flush. The corresponding `payload["metadata:ns"]`
  key materializes only when there is something to write.
- **Sibling-independence.** A write to one namespace does NOT dirty
  any other namespace. `metadata.flush()` on namespace `A` does NOT
  persist namespace `B`.
- **Restoration.** On every handler entry, the framework constructs
  the root `TaskMetadata` instance via a restoration helper (e.g.
  `TaskMetadata.from_payload(payload)`) that walks every
  `metadata[:...]` key in the payload and pre-populates each
  namespace with its persisted contents. Handler reads from any
  named namespace see the post-restoration state without an
  additional round-trip.

#### Flush semantics

- `metadata.flush()` persists the namespace it is called on, atomically
  against the lease (the framework piggybacks lease ownership on
  the PATCH so a flush also acts as a heartbeat).
- **Framework-only auto-flush** at every terminal-of-turn boundary
  walks every dirty namespace (the internal `flush_all` helper
  described in §37). Handlers do not need explicit flushes for
  durability across a graceful boundary; explicit `flush()` is
  for mid-handler fence semantics across a CRASH.
- Flush failures are logged at WARN, not raised. A failed flush
  retries on the next flush call or the next auto-flush boundary.
- Flush is **safe to call from a finished handler** (no-op if the
  namespace has been auto-flushed and not subsequently dirtied).

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

The framework defines the following exception hierarchy. All
runtime conditions are surfaced via one of these.

#### Developer-facing (catch these)

| Exception | Raised by | When |
|---|---|---|
| `TaskFailed(task_id, error: dict)` | `.run()` / `.result()` | Handler raised an unhandled exception. `error` is a structured dict `{type, message, cause?}`. |
| `TaskCancelled(task_id)` | `.run()` / `.result()` | Handler ended via the cooperative-cancel path (e.g., re-raised `asyncio.CancelledError` after observing `ctx.cancel`) OR via `ctx.exit_for_recovery()`. MUST NOT inherit `asyncio.CancelledError` (would be suppressed by generic handlers). |
| `TaskNotFound(task_id)` | `handle.result()` / `.start()` | Referenced `task_id` has been deleted between calls. |
| `TaskConflictError(task_id, current_status)` | `.run()` / `.start()` / `handle.result()` (queued steerer) | Single error type for any "task is busy / not available" state — live-elsewhere non-steerable, evicted (split-brain protection), or terminal-with-queued-steerer. |
| `LastInputIdPreconditionFailed(task_id, expected, actual)` | `.start(if_last_input_id=...)` | Chain precondition not satisfied. Subclass of `TaskPreconditionFailed`. |
| `TaskPreconditionFailed(task_id, message)` | `.start(...)` | Base for input-acceptance preconditions. |
| `SteeringQueueFull(task_id, max_pending)` | `.start(...)` against steerable | Queue is at its cap (9). |
| `InputTooLarge(task_id, size_bytes, max_bytes)` | `.start()` / `.run()` | Input serialized > 2 MB. Subclass of `ValueError`. |
| `AttachmentTooLarge(task_id, attachment_key, size_bytes, max_bytes)` | Provider | A single attachment value > 2 MB. Subclass of `ValueError`. |
| `AttachmentLimitExceeded(task_id, current_count, max_count)` | Provider | Per-task attachment count cap (20) would be exceeded. Subclass of `ValueError`. |

#### Internal (advanced / framework-internal)

| Exception | Notes |
|---|---|
| `EtagConflict(task_id, message?)` | Optimistic concurrency conflict at the provider boundary. Framework retries internally; only escapes for low-level callers manipulating etags directly. |
| `TransportClassifiedError(classification: "transient" \| "evicted" \| "conflict" \| "permanent")` | Hosted provider's classification wrapper around HTTP failures. Internal to hosted provider; framework dispatches based on `classification`. |

`TaskCancelled` does NOT inherit `asyncio.CancelledError` by
design. Wrapping it under `CancelledError` causes generic asyncio
`except CancelledError` handlers to swallow it silently, which is
the wrong behavior for a *task-level* signal (it should propagate
to the caller's awaiting `.result()`).

The earlier `TaskTerminated` exception (and corresponding
`TaskRun.terminate()` API) has been REMOVED. The framework no
longer supports forced termination. Callers use `TaskRun.cancel()`
and the handler picks the terminal shape via its reaction to
`ctx.cancel`.

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
  `EventStreamGoneError` if destroyed.

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
  values. Raises `EventStreamGoneError` synchronously at the call
  site if the stream is destroyed.

- **`last_cursor()`** — return the highest cursor seen so far, or
  `None`. While active: highest persisted cursor (`None` if zero
  emits or backing has no cursor support). After close: the last
  cursor seen even if those events have since been TTL-evicted —
  this is load-bearing for the file-backed replay's rehydration
  path. After destroy: raises `EventStreamGoneError`.

  `last_cursor()` is a **read-only watermark query**. It does NOT
  trigger the `Closed -> Gone` auto-transition (which is driven by
  TTL eviction alone, not by any read). Implementations MUST keep
  it side-effect-free.

  `last_cursor()` is the EMITTER's recovery primitive. It is NOT
  the workflow-recovery primitive — workflow watermarks (what work
  is done) belong in `ctx.metadata`, batched per side-effecting
  operation, NEVER in stream cursors.

### §42. The `streams` registry

A process-level singleton that owns the lifecycle of all SDK-bundled
`EventStream` instances:

```
streams.use_in_memory_live()                                    # configurator (sync)
streams.use_in_memory_replay(cursor_fn=..., ttl_seconds=...)    # configurator (sync)
streams.use_file_backed_replay(storage_dir=..., cursor_fn=...,
                               ttl_seconds=..., serializer=...,
                               deserializer=...)                # configurator (sync)

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

Tombstones: `delete(id)` installs a tombstone unconditionally —
including for ids that were never registered (the "delete is
symmetric with `rm -f` but still leaves a marker" rule). The next
`get(id)` against a tombstoned id raises `EventStreamGoneError`
(the id is destroyed). A bare `get(id)` against an id that was
never registered AND never `delete`d raises
`EventStreamNotFoundError`. The tombstone is cleared on the next
`get_or_create(id)` for the same id, which constructs a fresh
stream.

Note: `get(id)` does NOT itself install a tombstone — only
`delete(id)` does.

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

Every concrete `EventStream` instance MUST traverse:

```
              emit*                     close            (replay only)
            ┌──────────┐                                  TTL eviction
            │          │                                  of last event
            ▼          │                                  after close
┌──────────────────┐   │   ┌─────────────────┐         ┌──────────────┐
│      Active      │ ──┴── │      Closed     │ ──────▶ │     Gone     │
└──────────────────┘       └─────────────────┘         └──────────────┘
        │                          │                          ▲
        │                          │                          │
        │       delete()           │      delete()            │
        └──────────────────────────┴──────────────────────────┘
```

State semantics:

- **Active.** Accepts `emit` and `subscribe`. Always-the-initial
  state on construction. `close()` -> Closed (idempotent on
  already-closed). `delete()` -> Gone.
- **Closed.** `emit` raises `EventStreamClosedError`.
  `subscribe()` still works for replay backings (yields drained
  history). `last_cursor()` still works. `close()` is a no-op.
  `delete()` -> Gone.
- **Gone.** All operations raise `EventStreamGoneError`. Terminal.

The Closed -> Gone auto-transition exists for `ReplayEventStream`
(and `FileBackedReplayEventStream`) constructed with `ttl_seconds`:
once the stream is closed AND its last replayable event has been
evicted by per-event TTL (and there was at least one emit), the
backing self-destructs and the registry tombstones the id.

`BroadcastEventStream` (live-only) does NOT auto-transition; it
only goes Gone via explicit `delete(id)`.

### §44. Concrete backings

Three SDK-bundled implementations:

| Backing | Use case | Behavior |
|---|---|---|
| `BroadcastEventStream` | Live consumers attach before the producer starts. | No buffer. `subscribe(after=...)` is accepted but the `after` argument is silently ignored. Late subscribers miss earlier events. `subscribe()` returns an iterator over events emitted AFTER attach. Multi-subscriber (each gets a private cursor/queue). Goes `Gone` ONLY via explicit `delete(id)` — no TTL auto-transition. |
| `ReplayEventStream` | Late subscribers need history. | Per-stream buffer retains all events. `subscribe(after=N)` is honored iff `cursor_fn` was supplied to the configurator; otherwise `after` is ignored. `ttl_seconds`, if supplied, evicts events per-event AFTER the stream is `Closed`. Auto-transition `Closed -> Gone` when the last event is evicted AND there was at least one emit. |
| `FileBackedReplayEventStream` | Crash-recoverable history (multi-turn UIs, durable response streaming). | Persists each emit to `storage_dir/<id>.jsonl`. **Constructor rehydrates** from an existing file if present — restart-safe. Same replay + TTL + cursor semantics as `ReplayEventStream`. Optional `serializer: Callable[[Any], bytes]` and `deserializer: Callable[[bytes], Any]` for non-JSON payloads (default JSON). `delete()` cleans up the file BEFORE installing the registry tombstone. |

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

### §46. TTL eviction (replay backings)

When constructed with `ttl_seconds`, replay backings:

- Stamp each emitted event with an arrival time.
- Evict events whose age >= `ttl_seconds`, on `emit()` and
  `subscribe()`. Eviction runs **regardless of stream state**
  (active OR closed); the buffer never holds events older than
  `ttl_seconds` once an operation triggers an eviction sweep.
- Auto-transition Closed -> Gone when the stream is `Closed` AND
  the buffer is empty AND there was at least one emit. The
  auto-transition is checked on `emit()` and `subscribe()` only;
  `last_cursor()` deliberately does NOT trigger it (so emitter
  watermark reads remain side-effect-free for the rehydration
  path).

Implementation note: TTL eviction running on an active stream is
intentional — it bounds the buffer's memory footprint even for
long-lived streams. The Closed -> Gone transition is what makes
the *id* go away; eviction on an active stream just trims old
events the late-subscriber would have seen.

`last_cursor()` continues to work in the Closed state even after
all events have been evicted — it returns the last cursor the
backing ever saw, NOT the current buffered max. This is required
for the rehydration path (a process restarting picks up the
high-water mark for resuming a not-yet-fully-evicted stream).

### §47. Streaming error taxonomy

```
EventStreamError                     # base
  ├── EventStreamClosedError         # emit on closed stream
  ├── EventStreamGoneError           # any op on destroyed stream
  └── EventStreamNotFoundError       # streams.get(id) on never-registered id
```

Wire mapping (informative — HTTP plumbing is in callers, not the
framework):

| Exception | Suggested HTTP status |
|---|---|
| `EventStreamClosedError` | 5xx (this is a server-side bug — the producer kept emitting after closing). |
| `EventStreamGoneError` | 410 Gone (resource existed and is destroyed). |
| `EventStreamNotFoundError` | 404 Not Found (never registered). |

#### Consolidated: when is `EventStreamGoneError` raised?

A common misconception is that `EventStreamGoneError` only fires
for closed streams whose TTL has elapsed. It actually fires in
**three independent scenarios**, only one of which is TTL-driven.
Implementers reading this section instead of triangulating across
§42 / §43 / §46 — here is the complete picture:

| Path to `GONE` | Broadcast (live) | Replay (in-memory) | Replay (file-backed) |
|---|---|---|---|
| 1. Explicit `streams.delete(id)` → backing's `_on_delete` flips state to GONE → registry tombstones the id. Works in ANY state (Active or Closed); does not require any emit or TTL elapse. | ✓ | ✓ | ✓ (deletes file before tombstone) |
| 2. TTL auto-transition: `state == CLOSED` AND buffer empty (every event evicted) AND `total_emit_count > 0`. Checked on `emit()` and `subscribe()` only — NOT on `last_cursor()`. Requires the backing to have been constructed with `ttl_seconds`. | ✗ (no TTL machinery) | ✓ | ✓ |
| 3. Registry-level tombstone for `delete(id)` on a never-registered id: subsequent `get(id)` raises `Gone` even though no stream ever existed. | ✓ (registry-level) | ✓ (registry-level) | ✓ (registry-level) |

Key invariants to take away:

- `BroadcastEventStream` NEVER auto-transitions to `Gone` on TTL —
  it has no buffer and no TTL machinery. The ONLY path is explicit
  `delete()`.
- For replay backings, the TTL auto-transition specifically requires
  `total_emit_count > 0`. A stream that was created, never emitted
  to, and then closed STAYS `Closed` forever (until explicit
  `delete()`); it does not silently auto-destruct.
- `last_cursor()` deliberately does NOT trigger the TTL
  auto-transition check — it's a read-only watermark query needed
  for the file-backed rehydration path.
- A `delete(id)` on a never-registered id installs a tombstone
  anyway, so the next `get(id)` correctly distinguishes "Gone (was
  destroyed)" from "NotFound (never existed)" — the symmetry is
  with `rm -f`, which is a no-op but still leaves the directory
  entry conceptually missing.

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
3. Call self._recover_stale_tasks() — list tasks in our (agent_name,
   session_id) scope with status=in_progress; for each:
     a. Look at lease.owner and lease.instance_id.
     b. If lease.owner != self.owner: skip (not ours).
     c. If lease.owner == self.owner AND lease.instance_id == self.instance_id:
        skip (would be impossible in a fresh process; defensive).
     d. Otherwise (same-owner different-instance OR expired):
        — Call self._steering_cleanup_orphan_attachments(task_info)
          (§58) to clean up any orphan _steering_input_* attachments
          left by a partial crash.
        — Call self._reclaim_one(task_info) — PATCH lease to self
          with if_match=etag, then invoke the registered resume
          callback with entry_mode='recovered', re-hydrated input,
          and metadata.
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
         -> RESUME (transition to in_progress with new input)
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
5. If action ∈ {CREATE, ADOPT, RESUME, RECLAIM-AND-INVOKE}:
     Spawn lease_renewal_loop, watchdog (if timeout configured), execute_task_loop.
     Return a TaskRun bound to this execution.
6. If action == STEERING-APPEND:
     Return a TaskRun whose .result() resolves with the NEXT-TURN outcome
     (the queued steerer is bound to the next turn).
```

The reclaim sub-case includes input precondition validation
(`if_last_input_id`) before the transition PATCH.

### §51. Steering append (atomic)

When `.start()` resolves to STEERING-APPEND, the framework
executes this PATCH as a single round-trip:

```
1. Read current payload (already in memory from the lifecycle GET).
2. steering   = payload.get('_steering', {})
3. pending   = list(steering.get('pending_inputs', []))
4. If len(pending) >= 9: raise SteeringQueueFull.
5. serialized = canonical_json(input)
6. If size(serialized) > 20 KiB:
     next_seq = steering.get('next_input_seq', 0)
     key      = f'_steering_input_{next_seq}'
     ref      = {'__attachment_ref__': {'key': key, 'hash': sha256(serialized)}}
     pending.append(ref)
     steering['next_input_seq'] = next_seq + 1
     attachments_patch = {key: input}
   else:
     pending.append(input)         # raw inline
     attachments_patch = None
7. steering['pending_inputs']   = pending
   steering['cancel_requested'] = True
8. payload_patch = {'_steering': steering}
   if input_id provided: payload_patch['_last_input_id'] = input_id
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
  2. steering = dict(payload['_steering'])
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
 12. payload['_steering']          = steering
 13. payload['_turn_started_at']   = utc_now_iso()        # FR-023: fresh turn-start boundary
 14. PATCH(task_id, payload=payload, attachments=attachments_patch or None,
        lease piggyback, if_match=etag)

     [NB: Phase 1 does NOT set payload['input'] or write a ref/attachment
      for active_input. Only the in-memory ctx receives the value (Phase 2).
      Recovery from a crash BETWEEN Phase 1 and Phase 3 reads
      _steering['active_input'] as the source of truth for the input,
      via the race-recovery contract.]

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
 19. payload['_steering']          = steering
 20. payload['_retry_attempt']     = 0     # FR-001: drain resets retry budget durably
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

**Watchdog scope (known gap).** The per-turn timeout watchdog is
spawned ONCE per execution in `_execute_task` and is NOT
respawned on drain re-entry today. As a result, a steered turn
shares the watchdog of the turn that drained it. Other-language
implementers SHOULD spawn a fresh watchdog on drain re-entry to
honor the design intent that every turn-start boundary gets a
fresh per-turn budget (§14, §57). The canonical Python
implementation has this as a known gap and is patched by relying
on the persisted `_turn_started_at` only on RECOVERY.

### §53. Suspend write

On `ctx.suspend(output=X, reason=R)`:

```
1. Read current task (we need etag and the input slot to know if it was promoted).
2. payload_patch = {
       'metadata': metadata.to_dict(),  # auto-flush of touched namespaces
       'input': null,                   # consumed input goes away
   }
3. If task.payload['_steering'] is set:
       steering = dict(task.payload['_steering'])
       steering['active_input'] = null
       payload_patch['_steering'] = steering
4. If output is not None:
       payload_patch['output'] = canonical_json(output)
   # NB: output=None (or omitted) does NOT clear the field. Any prior
   #     payload['output'] from an earlier suspend or completion remains.
   #     This is asymmetric on purpose to match current source; see §20
   #     "Output field lifecycle" for the implication for multi-turn use.
5. attachments_patch = {}
6. If task.payload['input'] was a ref (§23.3):
       attachments_patch[ref_key(task.payload['input'])] = null
7. PATCH(task_id, status='suspended', suspension_reason=R,
        payload=payload_patch, attachments=attachments_patch or null,
        lease piggyback, if_match=etag)
```

The suspend PATCH MUST carry payload + attachments in one round
trip — if the input was promoted, deleting the ref and the
attachment is atomic.

### §54. Recovery + reclaim

Two reclaim sites exist with different ETag-CAS posture:

**Inline reclaim — `_reclaim_one(task_info)` (lifecycle resolver):**

```
1. Build a PATCH that re-takes the lease:
      lease_owner            = self.owner       # always self
      lease_instance_id      = self.instance_id # always self
      lease_duration_seconds = 60
      if_match               = task_info.etag   # CAS-guarded
2. PATCH(task_info.id, ...)
3. Re-read task_info (now with self as lease owner).
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
1. Build a PATCH that re-takes the lease (same fields as above)
   EXCEPT without if_match.
2. PATCH(task_info.id, ...)
3-9. Same as inline reclaim.
```

**Known gap.** The startup scan and the periodic scan today do
NOT pass `if_match` on the reclaim PATCH. The lifecycle inline
reclaim (which races against caller `.start()` calls) DOES use
CAS. Other-language implementers SHOULD use `if_match` at both
sites for symmetric race protection; in practice, the startup
scan only races against other cold-starts (which the lease
owner-id distinction already protects against in the framework's
`_lease_is_dead` predicate, §22) and the periodic scan races
against rare cross-process expiry events that the framework
treats as benign.

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
the lost-race case.

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
                       if k.startswith('_steering_input_')}
    if not steering_keys:
        return
    pending = task_info.payload.get('_steering', {}).get('pending_inputs', [])
    referenced = {ref_key(e) for e in pending if is_ref(e)
                                              and ref_key(e).startswith('_steering_input_')}
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
`azure-ai-agentserver-core/tests/durable/` and `tests/streaming/`).

Items are grouped by area. Each item is identified `C-AREA-N`
(e.g. `C-LCM-1` = Lifecycle item #1).

### C-LCM (lifecycle + state machine)

- **C-LCM-1.** Status MUST be one of exactly four values:
  `pending`, `in_progress`, `suspended`, `completed`. No other
  value is legal in the store.
- **C-LCM-2.** Unsuccessful outcomes (failure, cancellation) are
  designed to be stored as `completed` with the *cause*
  communicated via typed exceptions (NEVER via a fifth status
  value). The canonical Python implementation today consistently
  writes a terminal `completed` for failures, and for `ephemeral=True`
  cancellation paths the record is deleted entirely on terminal
  exit; for `ephemeral=False` cancellation, see §16 known gap.
  Other-language implementers SHOULD always write terminal status.
- **C-LCM-3.** `ctx.entry_mode` MUST be one of `fresh`, `resumed`,
  `recovered`. The combination `(entry_mode=recovered,
  is_steered_turn=True)` is legal and MUST be supported.
- **C-LCM-4.** For any given `task_id`, at most one handler runs
  at a time across the cluster of processes that share the
  `(agent_name, session_id)` scope. The lease + ETag CAS
  combination enforces this.

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
- **C-LSE-2.** Inline reclaim PATCH (via `_reclaim_one`) MUST be
  guarded by `if_match=etag`. Cold-start and periodic recovery
  reclaim PATCHes today do NOT use `if_match` in the canonical
  Python implementation — see §54 known gap.
- **C-LSE-3.** `expiry_count` MUST be a server-side counter ONLY.
  Implementations MUST NOT add it to the patch-request shape; the
  framework MUST NOT write the field. The hosted store bumps it
  on actual-expiry ownership change (not on same-owner
  different-instance handoff). The local file provider in the
  canonical Python implementation does NOT bump it (known
  divergence; it stays 0 in local mode). Implementations of new
  providers MUST decide whether to mirror the hosted behavior or
  document the divergence explicitly.
- **C-LSE-4.** Eviction (HTTP 409 + `error.code=binding_mismatch`)
  classified as `evicted` MUST trigger the local cleanup sequence:
  cancel local execution, suppress pending terminal write, signal
  awaiters with `TaskConflictError`.
- **C-LSE-5.** `ctx.exit_for_recovery()` MUST force-expire the lease
  and leave status as `in_progress` (NOT `suspended`).

### C-INP (input + chain)

- **C-INP-1.** `input_id` provided without `if_last_input_id` MUST
  succeed; the framework records the id in `_last_input_id`.
- **C-INP-2.** `if_last_input_id` provided without `input_id` MUST
  raise `TypeError` at the call site.
- **C-INP-3.** `if_last_input_id` mismatch MUST raise
  `LastInputIdPreconditionFailed` (subclass of
  `TaskPreconditionFailed`).

### C-SUS (suspend / resume)

- **C-SUS-1.** `ctx.suspend(output=X)` MUST clear
  `payload["input"]` AND `payload["_steering"]["active_input"]`
  AND any promoted input attachment, in a single PATCH.
- **C-SUS-2.** The next `.run()` / `.start()` against a `suspended`
  task MUST re-invoke the handler with `entry_mode="resumed"` and
  the NEW `input` (not the consumed one).
- **C-SUS-3.** `output` passed to `ctx.suspend()` MUST be delivered
  unconditionally to the suspending turn's caller, even if
  steering inputs are queued.
- **C-SUS-4.** `payload["output"]` is set by `_handle_suspend` only
  when the suspend output is non-null AND by `_handle_success` only
  for non-ephemeral tasks. It is NEVER cleared by the resume PATCH.
  The framework never reads it back; the value is delivered to the
  caller via the in-process result-future, not via a re-read of the
  persisted record. There is currently NO public developer-facing
  read API for `payload["output"]` (see §20 "Output field
  lifecycle"). Implementations adding such an API MUST also add
  clear-on-resume semantics or define the multi-turn ownership
  rules to avoid returning stale values.

### C-STR (steering)

- **C-STR-1.** Steering queue cap MUST be 9; appending past it
  MUST raise `SteeringQueueFull` from `.start()`.
- **C-STR-2.** Append MUST set `_steering["cancel_requested"]=True`
  and signal `ctx.cancel` on the in-process active execution.
- **C-STR-3.** `next_input_seq` MUST be monotonic and advance ONLY
  on promotion (inline appends do NOT bump it).
- **C-STR-4.** A drain MUST NOT renumber any other queue entry's
  attachment key. Surviving promoted entries keep their
  original `_steering_input_<seq>` keys.
- **C-STR-5.** A drain MUST be carried in a single PATCH that
  removes the head from `pending_inputs`, deletes the
  corresponding attachment (if any), and sets the new turn's
  input / `_turn_started_at`.
- **C-STR-6.** Handler ending a turn with `return value` (NOT
  suspend) MUST cause queued steerers' `.result()` to raise
  `TaskConflictError(current_status="completed")`.
- **C-STR-7.** Handler ending a turn with `raise` MUST cause
  queued steerers' `.result()` to raise
  `TaskConflictError(current_status=<observed>)`.
- **C-STR-8.** First turn's caller MUST observe the natural
  multi-turn outcome, not a "supersede"-shaped value.

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
- **C-TMO-2.** `payload["_turn_started_at"]` MUST be re-stamped at
  every turn-start boundary (fresh, resumed, drain re-entry — Phase 1
  of §52). It MUST NOT be re-stamped on crash recovery.
- **C-TMO-3.** Recovered watchdog MUST compute
  `remaining = max(0, timeout - (now - _turn_started_at))` and
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

- **C-RET-1.** `_retry_attempt` MUST persist in `payload` and be
  re-hydrated on every entry.
- **C-RET-2.** Crash recovery MUST NOT consume the retry budget.
- **C-RET-3.** Suspend MUST NOT consume the retry budget.
- **C-RET-4.** Steering drain MUST reset `_retry_attempt` to 0.
  Successful completion SHOULD also reset for `ephemeral=False`
  tasks (the canonical Python implementation today does not, but
  this is a known gap; the counter is harmless on the terminal
  record because no further entry consults it).
- **C-RET-5.** Between each failed retry attempt and the next, the
  framework MUST persist `{error: {type, message, attempt}, payload:
  {_retry_attempt: <attempt+1>}}` in a single PATCH (status stays
  `in_progress`). The `error` field overwrites on every interim
  attempt; the `_retry_attempt` bump survives crashes.
- **C-RET-6.** The terminal-failure error dict for `ephemeral=False`
  tasks MUST carry `{type: "exhausted_retries", attempts, last_error,
  last_error_type, traceback}` if retries were attempted, OR
  `{type, message, traceback}` for a single non-retryable failure.
- **C-RET-7.** No public API today exposes the interim `error`
  field to developer code (`TaskRun.refresh()` mirrors only
  `status`, `lease.expiry_count`, and `payload["metadata"]`).
  Implementations adding a public read path MUST define the
  clearing semantics (specifically: whether interim `error` is
  cleared on eventual `_handle_success` for `ephemeral=False`
  tasks; today it is NOT cleared and persists into the
  successful-terminal record).

### C-MET (metadata)

- **C-MET-1.** Default namespace MUST persist at `payload["metadata"]`.
- **C-MET-2.** Named namespace `ns` MUST persist at
  `payload["metadata:<ns>"]`.
- **C-MET-3.** Top-level keys / namespace names starting with `_`
  are RESERVED for the framework.
- **C-MET-4.** Auto-flush MUST persist all touched namespaces at
  every terminal-of-turn boundary.
- **C-MET-5.** Flush failures MUST be logged, not raised.

### C-ATT (attachments + promotion)

- **C-ATT-1.** Two wire shapes only: inline (raw value) OR ref
  (`{"__attachment_ref__": {"key": ..., "hash": "sha256:..."}}`).
- **C-ATT-2.** Detection rule: a slot is a ref iff it is a dict
  with exactly one key `__attachment_ref__` whose value is a dict
  with both `key` and `hash`.
- **C-ATT-3.** Promotion thresholds: function input > 200 KiB;
  steering input > 20 KiB. Measured in canonical-JSON bytes.
- **C-ATT-4.** Per-attachment cap: 2 MB serialized. Per-task
  attachment count cap: 20. Per-value cap MUST be enforced
  client-side on every write site (create + patch) in both
  providers via `InputTooLarge` / `AttachmentTooLarge`. Per-task
  count cap MUST be enforced on `create` and SHOULD be enforced
  on `patch` when current state is cheaply available; the
  canonical Python implementation enforces count on local-provider
  patches and on framework-orchestrated steering-append patches
  (which fetch state anyway) but NOT on the bare hosted PATCH
  (which would require an extra round-trip). The server enforces
  in the gap. `AttachmentLimitExceeded` carries the typed cap
  violation when client-detected.
- **C-ATT-5.** Promotion / drain / suspend / orphan-cleanup
  PATCHes MUST carry BOTH `payload` and `attachments` in a single
  round-trip.
- **C-ATT-6.** Hash algorithm MUST be SHA-256 over canonical
  JSON bytes (`sort_keys=True`, separators `(",", ":")`), formatted
  as `sha256:<64 lowercase hex chars>`.
- **C-ATT-7.** Orphan attachment cleanup (§58) MUST run on
  recovery for tasks with `_steering_input_*` keys not referenced
  in `pending_inputs`.

### C-REC (recovery)

- **C-REC-1.** Cold-start recovery MUST run as part of
  `TaskManager.startup()` BEFORE any HTTP route binds. Implementers
  MUST gate route binding on `startup()` returning.
- **C-REC-2.** Periodic recovery loop MUST run every 300 seconds
  (default `_PERIODIC_RECOVERY_INTERVAL_SECONDS`). It MUST share
  the same `_recover_stale_tasks` implementation as the cold-start
  scan (no divergence between cold-start filters and periodic-scan
  filters).
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

### C-RTE (resume route)

- **C-RTE-1.** Implementations exposing the framework over HTTP
  MUST register `POST /tasks/resume` (§26).
- **C-RTE-2.** Response codes MUST be exactly as documented:
  202 / 400 / 404 / 409 / 503 / 500. Empty body.

### C-STM (streaming protocol)

- **C-STM-1.** `EventStream` MUST be a 4-method protocol: `emit`,
  `close`, `subscribe`, `last_cursor`. No destructive method on
  the Protocol itself.
- **C-STM-2.** Stream states are exactly `Active`, `Closed`, `Gone`.
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
- **C-STR-REG-4.** `delete(id)` MUST be idempotent and MUST install
  a tombstone (even for ids that were never registered) so a
  subsequent `get(id)` raises `EventStreamGoneError`
  (NOT `EventStreamNotFoundError`).
- **C-STR-REG-5.** Tombstone MUST be cleared on the next
  `get_or_create(id)` for the same id.
- **C-STR-REG-6.** `get(id)` for an id that was never registered
  AND never `delete()`d MUST raise `EventStreamNotFoundError`.
  `get(id)` MUST NOT itself install a tombstone (only `delete(id)`
  does). After `delete(id)`, subsequent `get(id)` raises
  `EventStreamGoneError`.

### C-STR-TTL (replay TTL)

- **C-STR-TTL-1.** TTL eviction MUST run on every `emit()` and
  `subscribe()` call, regardless of whether the stream is `Active`
  or `Closed`. (Active streams use TTL to bound buffer memory;
  Closed streams use TTL to drive the `Closed -> Gone` transition.)
- **C-STR-TTL-2.** `Closed -> Gone` auto-transition MUST happen
  when the stream is `Closed` AND the buffer is empty AND there
  was at least one emit. The check MUST run on `emit()` and
  `subscribe()` but MUST NOT run on `last_cursor()` (so the
  watermark read stays side-effect-free).
- **C-STR-TTL-3.** `BroadcastEventStream` (live-only) MUST NOT
  auto-transition `Closed -> Gone`; it goes `Gone` only via
  explicit `delete()`.

### C-STR-FBR (file-backed replay)

- **C-STR-FBR-1.** Each stream MUST persist to
  `storage_dir/<id>.jsonl`.
- **C-STR-FBR-2.** Constructor MUST rehydrate from an existing
  file (crash-recovery friendly).
- **C-STR-FBR-3.** Optional `serializer` / `deserializer` callbacks
  MUST be honored for non-JSON payloads. Default uses JSON.
- **C-STR-FBR-4.** `delete()` MUST clean up the file before
  installing the registry tombstone.
- **C-STR-FBR-5.** **File format.** Each emitted event is a single
  JSONL line wrapping the payload + arrival time:

  ```
  {"emit_time": <float seconds>, "payload": <serialized payload>}
  ```

  On close, a sentinel line is appended:

  ```
  {"__terminal__": true}
  ```

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
  `TaskRun.delete()` MUST catch "not found" provider exceptions
  and re-raise as `TaskNotFound`; the higher-level
  `Task`-managed delete path SHOULD be idempotent (no-op on
  already-deleted). Implementers MAY make `provider.delete()`
  itself idempotent if their store cleanly distinguishes.
- **C-PRV-7.** `provider.list(...)` MUST filter server-side.

### C-OBS (observability — minimal)

- **C-OBS-1.** The framework MUST emit structured log events at:
  `create`, `lease renewal failure`, `eviction detected`,
  `reclaim`, `recovery start`, `recovery skip (no callback)`,
  `suspend`, `complete`, `fail`, `steering append`, `steering
  drain`, `orphan attachment cleanup`. Log level minimum `INFO`
  except where noted.
- **C-OBS-2.** Logger names MUST be hierarchical under
  `azure.ai.agentserver.durable` (or language-equivalent).

---


## Part IX — References

- **Foundry Task Storage Protocol Specification** — the wire-level
  contract for the hosted task store (routes, request/response
  envelopes, server-side merge rules, authentication, activation,
  ETag/CAS, error codes). The framework conforms to that contract;
  this document only describes how the framework *uses* the store.
- **Speckit specs (historical, dev-side only)** — `001-durable-tasks`
  through `018-task-attachments` under contributor `specs/` working
  trees. Each is a point-in-time record of how a specific feature
  was scoped and built; the current state of every feature lives
  in THIS document. These are not source-controlled and are
  intentionally not linked.
- **Canonical Python implementation:**
  `sdk/agentserver/azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`
  and `.../streaming/`. Tests at `tests/durable/` and
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
| Starlette `Route` | HTTP route binding. | ASP.NET Core `MapPost`. | The `POST /tasks/resume` route shape (§26) is what matters; the binding mechanism is language-native. |

The spec uses these Python names because the canonical
implementation lives in Python. Re-implementations SHOULD use
language-idiomatic names while preserving the documented behavior.

### §B. Representative full task record

A single JSON document showing how every concept in this spec
composes. This is a deep-research task mid-life: function input
was promoted, three steering inputs are queued (one inline, two
promoted), one drain has already happened so `next_input_seq` is
ahead of the live keys, both default and named metadata
namespaces are populated, framework state slots are set.

```json
{
  "object": "task",
  "id": "research-session-abc123",
  "agent_name": "durable-research-agent",
  "session_id": "session-abc123",
  "title": "Deep research on transformer trends 2026",
  "status": "in_progress",

  "lease": {
    "owner": "durable-research-agent|session:session-abc123",
    "instance_id": "worker-12-3f8a9d-1780912345",
    "generation": 7,
    "expires_at": "2026-06-09T04:05:30.123Z",
    "expiry_count": 0
  },

  "tags":   { "_task_name": "deep_research" },
  "source": {
    "type":           "agentserver.task",
    "name":           "deep_research",
    "server_version": "azure-ai-agentserver-core/2.0.0b6 (python/3.12)"
  },

  "payload": {
    "input": {
      "__attachment_ref__": {
        "key":  "_input",
        "hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      }
    },

    "metadata": {
      "completed_phases":  3,
      "in_progress_phase": 4,
      "completed_subcalls": 2
    },
    "metadata:session": {
      "history": [
        { "role": "user",      "content": "Research deep learning trends" },
        { "role": "assistant", "content": "Phase 3 of 15..." }
      ],
      "turn_count": 5
    },

    "_steering": {
      "pending_inputs": [
        "Quick note: prioritise post-2024 papers",
        {
          "__attachment_ref__": {
            "key":  "_steering_input_3",
            "hash": "sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
          }
        },
        {
          "__attachment_ref__": {
            "key":  "_steering_input_4",
            "hash": "sha256:f0e1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d"
          }
        }
      ],
      "next_input_seq":    5,
      "cancel_requested":  true,
      "drain_in_progress": false,
      "active_input":      null
    },

    "_turn_started_at": "2026-06-09T03:50:00.000Z",
    "_retry_attempt":   0,
    "_last_input_id":   "msg_abc123"
  },

  "attachments": {
    "_input": {
      "topic":   "deep learning trends 2026",
      "depth":   "comprehensive",
      "context": "<~800 KB of caller-supplied reference material>"
    },
    "_steering_input_3": {
      "instruction": "refocus on transformer architectures",
      "context":     "<~600 KB of caller-supplied reference material>"
    },
    "_steering_input_4": {
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
| Framework-stamped routing (§21) | `tags._task_name`, `source.name` |
| Input promoted to attachment (§23) | `payload.input` is a ref; `attachments._input` holds the value |
| Multiple metadata namespaces (§17) | `payload.metadata` + `payload["metadata:session"]` |
| Steering queue with mixed shapes (§12, §23) | `_steering.pending_inputs[0]` inline; `[1]`, `[2]` refs |
| Monotonic seq invariant (§23.5) | `next_input_seq: 5` with live keys `_3` + `_4` — one drain consumed `_0`/`_1`/`_2`, no renumbering |
| Steering mechanism state (§12) | `cancel_requested`, `drain_in_progress`, `active_input` |
| Per-turn watchdog source of truth (§14) | `_turn_started_at` |
| Durable retry counter (§15) | `_retry_attempt` |
| Last-input-id chain (§11) | `_last_input_id` |
| ETag CAS (§25) | `etag` |

Simpler scenarios drop fields:

- **Small inputs only**: `payload.input` is the raw JSON value;
  `pending_inputs` is all raw values; `attachments` is `null` or
  absent.
- **After suspend**: `payload.input` is `null`,
  `_steering.active_input` is `null`, any promoted `_input`
  attachment is deleted in the same suspend PATCH.
- **Cold start, no steering**: `_steering` absent; `next_input_seq`
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
   │                                                                  │  → return await ctx.suspend(output=X)
   │              ◀──────────── suspend resolves                      │
   │                            future of A with                      │
   │                            TaskResult("suspended", X)            │
   │                                                                  │
   │                            _try_drain_steering()                 │
   │                            ↓                                     │
   │                            Phase 1 PATCH: pop B,                 │
   │                            delete _steering_input_<seq>,         │
   │                            drain_in_progress=true,               │
   │                            _turn_started_at refreshed            │
   │                            ↓                                     │
   │                            build new ctx,                        │
   │                            entry_mode=resumed,                   │
   │                            is_steered_turn=true ────────────────▶ enter(resumed steered, input=B)
   │                            ↓                                     │
   │                            Phase 3 PATCH: drain_in_progress=     │
   │                            false, _retry_attempt=0               │
   │                                                                  │
   │                                                                  │ handler runs to completion
   │                                                                  │  → return await ctx.suspend(output=Y)
   │                       _handle_suspend(): write suspended,        │
   │                       clear active_input, clear input,           │
   │                       delete _input attachment if ref            │
   │                                            ─────▶ B's future     │
   │                                                  TaskResult(     │
   │                                                  "suspended", Y) │
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
                        lease_owner=self.owner)
       b. For each task in the list:
           - if active_locally: skip
           - _steering_cleanup_orphan_attachments(task) (§58)
           - reclaim (PATCH lease to self, NO if_match today —
             see §54 known gap)
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
ONLY `agent_name + session_id + status="in_progress" + lease_owner`.
It deliberately does NOT include `source_type` or any `tag` filter
(unlike `TaskManager.list_tasks()` which DOES pass both
`source_type=_SOURCE_TYPE` and `tag={_task_name: ...}` because it
needs them for function-scoped queries). For recovery, the
`(agent_name, session_id, lease_owner)` triple is unique enough
in practice — only this framework constructs lease owners in the
`<agent>|session:<sess>` format for this (agent, session) pair —
so source_type filtering is redundant.

A foreign record with the same lease_owner but a different
`source.type` (or no `source` at all) would be matched by the
list and reclaimed (its lease patched to self), then dropped at
the `_find_resume_callback(task_info)` step — that lookup keys on
`source.name` against `_resume_callbacks`, so an unregistered
source.name logs+skips. The reclaim wastes one round-trip but no
foreign callback fires.

Other-language implementers MAY narrow defensively by adding
`source_type=_SOURCE_TYPE` to the list filter — this would
eliminate the "wasted reclaim of foreign records" case at the
cost of one extra server-side index lookup. The canonical Python
implementation accepts the wasted-reclaim cost because the
lease_owner narrowing is already tight in production topologies.

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
