# Feature Specification: Durable-task primitive — pre-release contract hardening

**Feature Branch**: `feature/agentserver-durable-tasks` (continuing on current branch; no new branch)
**Created**: 2026-05-30
**Status**: Draft (awaiting user approval)
**Input**: A series of design discussions during the pre-release iteration of the durable-task primitive surfaced six inter-related defects in the public surface and recovery infrastructure. This spec consolidates the closure of all of them into one cohesive PR before the primitive ships.

## Pre-release scope note

> The durable-task primitive in `azure-ai-agentserver-core` is being developed for the first time on the `feature/agentserver-durable-tasks` branch and has not been released. This spec is an in-place evolution of an unshipped contract — there is no migration path to write, no rename map to publish, and the change set MUST NOT be framed as "breaking" in CHANGELOG, dev guide, or anywhere else. Every reference to "removing" or "replacing" a surface is shorthand for "rewriting an unreleased pre-release contract".

## Context

The primitive's pre-release surface has accumulated six inter-related defects. Each is a small thing on its own; together they undermine the primitive's "handler stays simple; framework owns the hard parts" promise. This spec is the closure plan.

1. **Recovery is leaky.** The framework today has one automatic recovery path (a one-shot startup scan). Mid-lifetime orphans are unrecoverable without a developer-facing `stale_timeout` knob — itself an implementation concern that should never have leaked into handler authoring. The platform may also mistakenly spin up two sandboxes for the same session (a known platform bug). The task-store rejects orphan-sandbox writes with `HTTP 409 + $.error.code == "binding_mismatch"`, but the framework doesn't treat that signal as eviction.

2. **Steering is over-modeled.** The current implementation synthesises a `TaskResult.status == "superseded"` value, drops handler-emitted output on the floor in the suspend-with-queued-input path, maintains a parallel future-tracking dict on `TaskManager`, and silently skips the metadata auto-flush invariant on drain boundaries. Steering is conceptually multi-turn with a queueing mechanism on top; the surface should reflect that and nothing more.

3. **Cancellation surface is confused.** `ctx.cancel` is overloaded (timeout watchdog AND steering drain set it with no way for the handler to distinguish). `ctx.pending_inputs: Sequence[Any]` exposes future-turn input data the handler cannot legitimately process. `ctx.was_steered` is sticky-True after any drain forever (its computation conflates history with current state). `ctx.steering_generation` exposes a counter the handler has no use case for. `TaskRun.terminate()` duplicates `.cancel()` with marginal-but-distinct semantics and significant plumbing cost.

4. **Timeout is per-invocation and non-durable.** `@task(timeout=...)` resets on every fresh handler entry, including crash recovery and steering drain re-entry; net effective compute per turn is unbounded under repeated crash + recovery. The watchdog docstring also claims an ignored timeout triggers automatic lease expiry / recovery — that claim is false.

5. **Shutdown has no first-class API.** The only ways to leave a task `in_progress` for restore-on-restart are `raise asyncio.CancelledError` (asyncio coupling leaks into handler code; easily swallowed by stray `try/except`) or letting the framework force-cancel at grace expiry (developer is passive). `ctx.suspend()` — the obvious thing to reach for — silently transitions the task to `suspended` and breaks the restore-on-restart goal.

6. **Transport has no policy stack.** The hosted task-store client is a raw `httpx.AsyncClient` — no retry, no correlation headers, no distributed tracing, no shared bearer-token policy, no user-agent moniker, and no consistent seam for the new eviction classifier. The sibling responses-storage provider already runs on `azure.core.AsyncPipelineClient` and learned a critical lesson on the way: `ContentDecodePolicy` must be excluded because it eagerly decodes every body as JSON in middleware and crashes on gzip / non-UTF-8 / gateway-HTML payloads. The task client needs the same migration and the same exclusion.

Reference material captured during iteration: `sdk/agentserver/specs/stale-timeout-analysis.md` and `sdk/agentserver/specs/016-automatic-task-recovery/cancel-surface-proposal.md`. This spec is the contract.

## Design invariants (load-bearing)

These invariants are the *what*; the *how* is left to the plan phase.

### Invariant 1 — Caller-observable behavior of scheduling primitives is invariant across lease states

`.run()` / `.start()` / `get_active_run()` are scheduling/lookup primitives whose contract is defined entirely against the "task is already running in the current process" mental model. The framework opportunistically uses them as *additional signals* to trigger recovery (reclaim when the lease is dead), but the reclaim is a hidden side effect — it never changes the caller's observable outcome.

| Entry point | Lease: Live (mine) | Lease: Dead (reclaimable) | Lease: Dead (evicted via `binding_mismatch`) |
|---|---|---|---|
| `.run()` steerable | queue + await result | reclaim → queue + await result | `TaskConflictError` |
| `.run()` non-steerable | `TaskConflictError` | reclaim → `TaskConflictError` | `TaskConflictError` |
| `.start()` steerable | queue + return `TaskRun` | reclaim → queue + return `TaskRun` | `TaskConflictError` |
| `.start()` non-steerable | `TaskConflictError` | reclaim → `TaskConflictError` | `TaskConflictError` |
| `get_active_run()` | return `TaskRun` | reclaim → return `TaskRun` | return `None` |

The eviction column collapses to the "running elsewhere / not active here" outcome the caller would have observed anyway. No new error types, no new return shapes, no leaked "evicted" state for user code to branch on. Eviction is purely a framework-internal concern that produces operator-facing WARNING logs.

### Invariant 2 — Steering is multi-turn with a queue

From either caller's perspective, the observable contract is identical to plain multi-turn. There is no "superseded" status. A handler's `ctx.suspend(output=X)` always belongs to the current turn's caller. If the handler terminates (return or raise), the task is terminal and any queued steering input becomes unservicable — the queued caller receives `TaskConflictError` (same shape as a fresh `.start()` against an already-terminal task).

### Invariant 3 — Cancellation is cooperative; the handler chooses the terminal shape

`ctx.cancel` is an advisory signal. The handler decides whether to suspend, complete, or raise in response. The framework does not force a terminal shape on the handler. The cause(s) of cancellation (timeout, external cancel call, steering pressure) are observable as independent state on `TaskContext` so the handler can branch by cause if it chooses.

### Invariant 4 — Metadata is durably persisted at every terminal-of-turn boundary

Whenever the framework writes a suspend / complete / failure / shutdown-preserve record, the current turn's `ctx.metadata` snapshot is durably persisted in the same write — regardless of whether a steering drain is about to re-enter the handler. Handler authors can trust that work checkpointed to `ctx.metadata` survives any graceful boundary.

### Invariant 5 — Timeout is per-turn, wall-clock, and durable within a turn

`@task(timeout=...)` is a per-turn deadline measured against a durable wall-clock anchor. New turns get a fresh budget; crash recovery within a turn preserves the budget (recovery does NOT reset). Suspended idle time between turns is free. The watchdog is cooperative-only — an ignoring handler runs until process death or external cancel; the lease is NOT force-expired by the watchdog.

### Invariant 6 — Recovery has a single discoverable shape for handler authors

The only signal a handler ever needs to acknowledge for recovery is `ctx.entry_mode == "recovered"`. No timeout knobs, no liveness flags, no policy configuration. The framework owns the rest.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Recovery is automatic; no developer knob (Priority: P1)

A developer wires a durable task with `@task` and calls `.run()` / `.start()`. They do not configure any recovery timeout. If their handler is interrupted (crash, deploy, OOM), the framework re-invokes it transparently with `ctx.entry_mode == "recovered"`. The developer's only recovery-related concern is reading `ctx.entry_mode` if they want to branch on it.

**Why this priority**: This is the API-surface promise the rest of the spec relies on. Without it, every subsequent layer leaks implementation knobs into handler authoring.

**Acceptance Scenarios**:

1. **Given** a fresh `@task` definition, **When** the developer inspects the public API (decorator, `Task.options()`, `TaskOptions`, `TaskContext`), **Then** no recovery timeout knob exists on any of them. No public symbol named `stale_timeout` exists anywhere on the package surface.
2. **Given** the developer reads `docs/durable-task-guide.md`, **When** they search for "stale_timeout", **Then** the term appears zero times. Recovery is described in one paragraph as "automatic, framework-managed; observable via `ctx.entry_mode`".

---

### User Story 2 — Split-brain orphan sandbox cannot duplicate execution (Priority: P1)

The platform mistakenly spawns two sandboxes (A and B) for the same session. The store accepts writes from A and rejects writes from B with `HTTP 409` + body `$.error.code == "binding_mismatch"`. Despite both sandboxes deriving the same `lease_owner`, the handler must execute exactly once (in A), and B's user-space callers must observe outcomes identical to "the task is live in some other sandbox you don't control" — never silently producing duplicate side effects.

**Why this priority**: Without this, every multi-sandbox event is a correctness incident — duplicate billing, duplicate model calls, duplicate user-visible writes. The platform explicitly built the `binding_mismatch` contract to prevent this; the framework must honor it.

**Acceptance Scenarios**:

1. **Given** orphan sandbox B with same `lease_owner` as active sandbox A, **When** B's recovery scan attempts to reclaim an in-progress record, **Then** the framework classifies the response as "evicted", logs WARNING, never retries, and never aborts the scan loop.
2. **Given** orphan sandbox B has an active handler whose lease renewal is rejected with `binding_mismatch`, **When** the renewal loop next runs, **Then** the framework marks the local task evicted, cancels the local execution, suppresses any terminal write, and surfaces the eviction to any awaiter as `TaskConflictError`.
3. **Given** a caller invokes `.run()` / `.start()` on orphan sandbox B for an in-progress task, **When** B's inline reclaim is rejected with `binding_mismatch`, **Then** the caller receives `TaskConflictError` — identical in type and shape to the live-non-steerable-conflict case. No new error type, no new field on the exception, no leaked split-brain state.
4. **Given** a caller invokes `get_active_run()` on orphan sandbox B for an in-progress task, **When** B's inline reclaim is rejected with `binding_mismatch`, **Then** the caller receives `None` — identical to "task is not active in this process". No exception is raised.
5. **Given** both sandboxes have run end-to-end, **Then** exactly one terminal record exists in the store, written by A.

---

### User Story 3 — Recovery happens via three layers without developer involvement (Priority: P1)

The framework provides three independent recovery paths, all internal: (a) hardened startup scan that survives per-record failures and retries transient provider errors; (b) periodic background scan that catches orphans no caller touches; (c) inline reclaim on user-traffic entry points (`.run()`, `.start()`, `get_active_run()`) so an orphan is recovered the moment relevant traffic arrives instead of waiting for the next scan cycle. All three use the same single reclaim helper with CAS-based race protection. The developer sees none of this.

**Why this priority**: P1 because (b) and (c) are the actual fix for the gap the removed `stale_timeout` knob was trying to address; (a) is the production-readiness pass that lets the system survive a single bad record. Together they make recovery a framework property the developer can rely on without configuration.

**Acceptance Scenarios**:

1. **Given** an in-progress record with a dead lease, **When** a fresh `TaskManager` starts up, **Then** the record is reclaimed during startup scan and the handler re-enters with `entry_mode == "recovered"`.
2. **Given** a same-process orphan synthesised after startup, **When** the periodic background scan fires (test override of the interval for determinism), **Then** the orphan is reclaimed and re-entered with `entry_mode == "recovered"` without any user-space callsite involvement.
3. **Given** an in-progress record with a dead lease and a caller invokes `.run()` / `.start()` / `get_active_run()`, **When** the framework processes the call, **Then** inline reclaim runs as a hidden side effect AND the caller observes exactly the outcome defined in Invariant 1's table for the corresponding live-lease case. The reclaim is never exposed on the return type, the exception type, or any public field.
4. **Given** two concurrent callers attempt inline reclaim on the same dead-lease record, **When** both proceed, **Then** CAS produces exactly one winner; the loser re-reads and falls through to the live-lease branch. No double-execution.
5. **Given** the recovery scan encounters a mix of healthy records, transient failures, evictions, vanished records, and parse errors, **When** the scan runs, **Then** every record is processed independently (a single failure does NOT abort the scan), transient errors are retried with bounded backoff, and every outcome is logged with a classification reason.

---

### User Story 4 — `get_active_run()` returns a usable handle for dead-lease in-progress records (Priority: P1)

A developer (typically a streaming HTTP handler servicing a GET-stream request) calls `manager.get_active_run(task_id)` to attach to an in-flight task. The current implementation returns `None` if no in-memory entry exists — even if the store shows the task is `in_progress` with a dead lease. The new behavior: `get_active_run()` consults the store, performs inline reclaim on a dead-lease record, and returns a usable `TaskRun` handle bound to the now-live recovered run. The observable contract is unchanged from the caller's perspective — it still returns `TaskRun` when the task is live in this process and `None` when it isn't; the change is that "dead lease in the store" now resolves to "live in this process" instead of silently to `None`.

**Why this priority**: This is the gap that today produces the worst symptom — `None` silently returned to user code which then says "task not active" when in reality it's stuck in-progress and recoverable.

**Acceptance Scenarios**:

1. **Given** an in-progress record exists with a dead lease, **When** `get_active_run(task_id)` is called, **Then** the framework inline-reclaims and returns a `TaskRun` handle. `entry_mode == "recovered"` is observable in the re-entered handler.
2. **Given** an in-progress record with a live lease held by THIS process, **When** `get_active_run()` is called, **Then** the existing in-memory handle is returned (no behavior change).
3. **Given** a record in any terminal state, **When** `get_active_run()` is called, **Then** `None` is returned (no behavior change).
4. **Given** an orphan-sandbox case where the inline reclaim is rejected with `binding_mismatch`, **When** `get_active_run()` is called, **Then** `None` is returned — same return shape as "not active in this process". The eviction is logged at WARNING for operators.

---

### User Story 5 — Steering is plain multi-turn with a queue (Priority: P1)

A developer wires a steerable handler that uses `ctx.suspend(output=X)` between turns. A first caller invokes `.run(task_id, input=I1)` and a second caller invokes `.start(task_id, input=I2)` mid-flight. The framework treats this as exactly equivalent to the plain multi-turn pattern: caller-1's `TaskResult` is whatever the handler emitted on turn-1; the handler re-enters with I2 as turn-2; caller-2's `TaskResult` reflects whatever turn-2 emits. Neither caller observes a "superseded" status. If the handler chose to terminate (return or raise), the task is terminal; caller-1 sees the natural outcome, caller-2's queued input fails with `TaskConflictError`. Metadata writes from the displaced turn are durably persisted before the drain re-enters.

**Why this priority**: P1 because today the steering path synthesises a public `superseded` status, drops handler-emitted output on the floor in the suspend-with-queued-input case, maintains a parallel future-tracking abstraction, and silently skips the metadata auto-flush invariant on drain boundaries. Each is a public-surface defect on an unshipped contract.

**Acceptance Scenarios**:

1. **Given** a steerable handler whose turn-1 calls `await ctx.suspend(output="checkpoint A")`, **When** caller-2 has previously queued an input via `.start()`, **Then** caller-1's `TaskResult` is `status="suspended", output="checkpoint A"` (the handler's emitted output is delivered untouched). The framework re-enters the handler with caller-2's input as turn-2 with `ctx.entry_mode == "resumed"` and `ctx.is_steered_turn == True`. Caller-2's `TaskResult` reflects whatever turn-2 emits.
2. **Given** a steerable handler whose turn-1 returns a value (handler chose to ignore `ctx.cancel`), **When** caller-2 has previously queued an input, **Then** caller-1's `TaskResult` is `status="completed", output=value` and the task is terminal. Caller-2's `TaskRun.result()` raises `TaskConflictError` with `current_status="completed"` — identical to a fresh `.start()` against an already-terminal task.
3. **Given** a steerable handler whose turn-1 raises, **When** caller-2 has previously queued an input, **Then** caller-1's `TaskResult` propagates the exception. The task is terminal. Caller-2's `TaskRun.result()` raises `TaskConflictError` with `current_status="failed"`.
4. **Given** any handler that writes `ctx.metadata["marker"] = "value"` without calling `flush()` explicitly, **When** any terminal-of-turn boundary fires (normal suspend, normal complete, cooperative cancel, exception, suspend-with-drain, return-with-drain), **Then** the marker survives a simulated crash + reload from the provider. The auto-flush invariant holds across all boundaries.
5. **Given** the public `TaskResult` type, **When** the developer inspects its `status` Literal, **Then** the only values are `"completed" | "suspended"`. `"superseded"` does not exist on the surface.

---

### User Story 6 — Cancellation cause is observable via independent signals; cancel surface is minimal (Priority: P2)

A handler author who wants to branch on *why* it was asked to wind down — e.g., "if I was steered, save partial work and let the next turn pick it up; if I timed out, log + raise; if an operator explicitly cancelled, commit and exit" — observes independent state on `TaskContext`: `ctx.timeout_exceeded` (set when the timeout watchdog fires), `ctx.cancel_requested` (set when an external `TaskRun.cancel()` is called), and `ctx.pending_input_count` (live count of queued steering inputs). The composite `ctx.cancel.is_set()` remains the default "should I stop?" check. Causes accumulate; nothing is lost if multiple fire in sequence.

The handler-facing surface also drops misleading or duplicate fields: `ctx.pending_inputs: Sequence[Any]` (a snapshot that misled developers into thinking they could process queued inputs in current execution) is replaced by the live `ctx.pending_input_count: int`. `ctx.was_steered` (sticky-True after any drain forever) is renamed to `ctx.is_steered_turn` with semantics fixed to "this specific invocation is a drain re-entry". `ctx.steering_generation` is dropped from the public surface entirely. `TaskRun.terminate()` and `TaskTerminated` are removed — `.cancel()` is the single API for "stop this task", and the handler chooses the terminal shape.

**Why this priority**: P2 — none of these are correctness gaps in the sense that user-supplied data is lost. They are mental-model gaps that surface as wrong handler behavior under steering / timeout / cancel combinations and as significant unnecessary complexity in the public surface.

**Acceptance Scenarios**:

1. **Given** a non-steerable task whose timeout fires, **When** the handler reads `ctx` state at the next checkpoint, **Then** `ctx.cancel.is_set() == True`, `ctx.timeout_exceeded == True`, `ctx.cancel_requested == False`, `ctx.pending_input_count == 0`.
2. **Given** any handler against which an external `TaskRun.cancel()` is called, **When** the handler reads `ctx` state, **Then** `ctx.cancel.is_set() == True`, `ctx.cancel_requested == True`, `ctx.timeout_exceeded == False`.
3. **Given** a steerable handler with a queued steering input, **When** the handler reads `ctx` state, **Then** `ctx.cancel.is_set() == True`, `ctx.pending_input_count >= 1`, `ctx.timeout_exceeded == False`, `ctx.cancel_requested == False`. As additional `.start()` calls land mid-execution, `ctx.pending_input_count` reflects the live backlog (not an entry-time snapshot).
4. **Given** a composite case where steering fires, then the watchdog fires, then `TaskRun.cancel()` is called, all before the handler's next checkpoint, **When** the handler reads `ctx` state, **Then** ALL THREE causes are observable simultaneously: `ctx.pending_input_count >= 1` AND `ctx.timeout_exceeded == True` AND `ctx.cancel_requested == True`. Booleans accumulate; no first-cause-wins discard.
5. **Given** existing handler code using `if ctx.cancel.is_set():` or `await ctx.cancel.wait()`, **When** the new properties land, **Then** that code continues to work unchanged. `ctx.cancel` remains a bare `asyncio.Event`.
6. **Given** the public surface of `TaskContext`, **When** the developer inspects it, **Then** `ctx.was_steered`, `ctx.pending_inputs`, `ctx.steering_generation` are absent; `ctx.is_steered_turn`, `ctx.pending_input_count`, `ctx.timeout_exceeded`, `ctx.cancel_requested` are present.
7. **Given** `ctx.is_steered_turn`, **When** a steerable task is steered in turn-2, then suspended, then resumed by a fresh `.run()` from the developer in turn-3, **Then** turn-3 enters with `ctx.is_steered_turn == False` — historical drains do NOT pollute the current invocation. In contrast, a true drain re-entry enters with `ctx.is_steered_turn == True`.
8. **Given** the orthogonality of `entry_mode` and `is_steered_turn`, **When** a previous process crashed mid-drain and the new process picks up the queued steering input, **Then** the handler re-enters with `ctx.entry_mode == "recovered"` AND `ctx.is_steered_turn == True` — both axes report independently.
9. **Given** the public `TaskRun` type, **When** the developer inspects it, **Then** `terminate` is absent and importing `TaskTerminated` raises `ImportError`. A handler that wants to force-fail on cancellation does so by raising in response to `ctx.cancel.is_set()`.

---

### User Story 7 — Per-turn durable wall-clock timeout (Priority: P2)

A handler author who configures `@task(timeout=timedelta(seconds=N))` gets a per-turn deadline that is anchored to a durable wall-clock timestamp. Each fresh turn (fresh `.run()` / `.start()`, suspended-to-in_progress resume, steering drain re-entry) gets the full N-second budget. Crash recovery within a turn does NOT reset the budget — the recovered handler observes only the remaining time. Suspended idle time between turns is free. The watchdog is cooperative-only; if the handler ignores `ctx.cancel`, the task runs until process death or external cancel.

**Why this priority**: P2 — the current per-invocation in-process timer is wrong on two axes (shared budget across drain re-entries; non-durable across crashes) and the watchdog's source comment misleads operators about self-recovery behavior. Mechanically small to fix.

**Acceptance Scenarios**:

1. **Given** a steerable `@task(timeout=timedelta(seconds=N))`, **When** turn-1 runs for some duration, suspends, and turn-2 starts via fresh `.run()`, **Then** turn-2 gets a fresh ~N-second window. The shared-budget bug is not present.
2. **Given** the same task, **When** turn-1 runs for some duration and is steered (drain re-enters), **Then** the drained generation also gets a fresh ~N-second window.
3. **Given** a non-steerable `@task(timeout=timedelta(seconds=N))`, **When** the handler runs for M seconds then crashes, and recovery picks up at +(M+δ) wall-clock since turn-start, **Then** the recovered watchdog spawns with `remaining ≈ N − M − δ` and fires at approximately the original N-second deadline relative to turn-start.
4. **Given** the same task, **When** recovery is delayed past the deadline, **Then** the recovered handler enters with `ctx.cancel.is_set() == True` AND `ctx.timeout_exceeded == True` from the first checkpoint. No grace period.
5. **Given** the source of the timeout watchdog, **When** a reviewer reads its docstring, **Then** the docstring accurately states: cooperative-only; setting `ctx.timeout_exceeded` then `ctx.cancel`; an ignoring handler runs until process death or external `TaskRun.cancel()` the handler chooses to honor. The misleading lease-expiry claim is gone. Watchdog-fired log message stays at INFO.

---

### User Story 8 — Shutdown has a discoverable API (Priority: P2)

A developer writing a long-running handler observes `ctx.shutdown.is_set()` and wants the framework to restore the task on the next process startup. They reach for `await ctx.exit_for_recovery()` — a framework API that returns a sentinel the framework recognises as "leave the task `in_progress`; the recovery loop owns the next entry". No parameters (the framework already knows the cause). Calling it outside shutdown is a developer error and raises `RuntimeError` at the API surface, so misuse cannot accidentally leave a task `in_progress`.

**Why this priority**: P2 — closes a documentation-and-discoverability gap that the rest of the recovery infrastructure silently relies on. The pre-existing alternatives — `raise asyncio.CancelledError` or letting the framework force-cancel — are undocumented escape hatches.

**Acceptance Scenarios**:

1. **Given** a handler that on `ctx.shutdown.is_set()` checkpoints to `ctx.metadata` and calls `return await ctx.exit_for_recovery()`, **When** the framework processes the call, **Then** the stored record has `status == "in_progress"`, the metadata snapshot is durable, the lease is released, and any in-process awaiter observes a clean cancellation signal.
2. **Given** the task is left `in_progress` per scenario 1, **When** a fresh `TaskManager` starts on a new process, **Then** the recovery scan reclaims the task and re-enters the handler with `ctx.entry_mode == "recovered"`, `ctx.recovery_count` incremented, and metadata rehydrated.
3. **Given** a handler calls `await ctx.exit_for_recovery()` when `ctx.shutdown.is_set() == False`, **When** the framework processes the call, **Then** a `RuntimeError` is raised at the call site indicating the precondition violation. The exception propagates through the normal exception path and the task ends in `failed` — the misuse is loudly visible in operator logs AND in the resulting record; it cannot silently leave the task `in_progress`.
4. **Given** `ctx.exit_for_recovery()`'s signature, **When** the developer inspects it, **Then** it accepts no `reason`, no `output`, no positional arguments — only `self`. Partial work belongs in `ctx.metadata` (auto-flushed at this boundary per Invariant 4).
5. **Given** a handler that calls `ctx.exit_for_recovery()` while steering inputs are queued, **When** the framework processes the call, **Then** the queued inputs are preserved in the persisted state (the framework does NOT drain them during shutdown). On the next process startup, recovery re-enters the handler and the queue drains naturally at the next turn boundary.

---

### User Story 9 — Task-store transport is built on `azure.core` (Priority: P2)

The hosted task-store client runs on `azure.core.AsyncPipelineClient` with the standard policy stack: retry on transient failures, bearer-token auth, correlation headers, distributed tracing, structured logging with header allow-list, stable user-agent moniker. The chain explicitly excludes `ContentDecodePolicy` because eager body-decode-in-middleware crashes on gzip / non-UTF-8 / gateway-HTML payloads (the responses-storage gzip lesson, restated for the task client). The classifier seam for `binding_mismatch` and other store errors funnels through a single function used at every write site. The `httpx` runtime dependency is removed once no other code under `azure-ai-agentserver-core/azure/` imports it.

**Why this priority**: P2 — the current raw-httpx path works end-to-end but offers no consistent seam for the eviction classifier in US2 and lacks the operational guarantees every other Azure SDK client provides. This work is a prerequisite for the classifier work in US2.

**Acceptance Scenarios**:

1. **Given** a fake transport injected into the pipeline serving a 503 then a 200, **When** any task verb is invoked, **Then** the call succeeds after exactly one retry.
2. **Given** a fake transport returning HTTP 409 with body `{"error": {"code": "binding_mismatch", ...}}` to any write verb, **When** the call is made, **Then** the classifier returns "evicted", the pipeline does NOT retry (exactly one request observed), and the caller observes the eviction-mapped outcome per Invariant 1.
3. **Given** a fake transport returning a gzip-encoded JSON response, **When** any read verb is invoked, **Then** the response deserialises correctly. The pipeline transparently decompresses; the call-site serializer reads decompressed bytes. No middleware crash occurs.
4. **Given** a fake transport returning a non-JSON 200 body, **When** any verb expecting JSON is invoked, **Then** the call-site serializer raises a classified transport error carrying the response status and a truncated body prefix for operator diagnosis.
5. **Given** the developer inspects the pipeline policy chain on `HostedTaskProvider`, **Then** the chain includes (in order): request-id, headers, user-agent (sdk_moniker `ai-agentserver-core/{VERSION}`), retry, bearer-token credential, task-API logging, distributed tracing. The chain MUST NOT include `ContentDecodePolicy`.
6. **Given** `grep -r 'import httpx' azure-ai-agentserver-core/azure/ai/agentserver/core/`, **Then** zero matches are returned after the migration. If `httpx` is no longer imported anywhere in the runtime, it is removed from the production install requirements (test-only dev dependency is acceptable for transport fixtures during transition).

---

### Edge Cases

- **Same-process orphan whose lease metadata matches THIS process**: the framework MUST NOT treat this as eviction or re-PATCH the lease ownership (it's already ours); construct a new in-memory entry and re-enter the handler. This is an exotic case but real (manager restarted within the same process).
- **Recovery re-enters a handler that completed-but-did-not-persist before the previous process died**: handler must be idempotent. This is the pre-existing recovery contract; no change in this spec.
- **Transient provider failures during inline reclaim**: bounded retry, then degrade to the live-lease branch — the caller may receive `TaskConflictError` since we couldn't prove the lease was actually dead. Safe degraded outcome.
- **`AsyncRetryPolicy` interaction with `_classify_store_write_error`**: the retry policy is configured to NEVER retry on 409 (regardless of body content) — etag conflicts need re-read-and-evaluate, and `binding_mismatch` must not retry. The pipeline retries on 5xx, 408, 429 (with `Retry-After`) only.
- **Token refresh during retry**: standard `azure.core` bearer-token policy behavior; no additional spec work.
- **Test environment without a running event loop in shutdown**: the periodic recovery scan task and any in-flight watchdog must be cancellable from `shutdown()` even if the loop is closing. Use the existing patterns.
- **Suspend persist fails with etag conflict while a steering input is queued**: existing recovery semantics apply — re-read and decide. If the record turned terminal in the meantime, the suspend is abandoned and the terminal-with-queue cleanup runs (queued steerers get `TaskConflictError`).
- **Multiple steering inputs queued (caller-2 and caller-3 both `.start()` during turn-1)**: FIFO order is preserved. Turn-1 sees `ctx.pending_input_count == 2`; the drain re-enters with caller-2's input first; the new generation sees `ctx.pending_input_count == 1`. If turn-1 terminated instead of suspending, ALL queued inputs get `TaskConflictError` in the same store write that records the terminal transition.
- **Clock skew between hosts (mid-turn recovery on a different node)**: the recovered watchdog clamps `remaining` to `[0, opts.timeout]` so backwards skew can't extend the budget and forwards skew can't make sleep negative. Operators should run NTP-synchronised hosts; the framework degrades safely if skew is bounded.
- **`ctx.exit_for_recovery()` called during crash recovery**: if a recovered handler observes `ctx.shutdown.is_set()` later (because the new process is also going down), the same API applies and the task is preserved again for the next recovery cycle. The framework imposes no bounded-retry policy; if a task is stuck in a crash-recover-shutdown loop, operator intervention is required.
- **Handlers MUST NOT call `ctx.cancel.set()` directly** — it's framework-owned. Handlers needing to signal their own dependent work should use a separate `asyncio.Event`. The dev guide states `ctx.cancel`, `ctx.timeout_exceeded`, and `ctx.cancel_requested` are read-only from the handler's perspective.

---

## Requirements *(mandatory)*

### Functional Requirements

Requirements are grouped by theme. Each MUST be backed by at least one success criterion; tests follow per Constitution Principle XII.

#### Recovery and eviction

- **FR-001**: The developer-facing recovery surface (`stale_timeout`, any helper named after staleness) MUST be removed from `@task`, `Task.options()`, `TaskOptions`, `TaskContext`, and every public docstring, doc, or sample. Passing the removed kwarg MUST raise `TypeError`.
- **FR-002**: The framework MUST provide three recovery layers, all internal: (a) hardened startup scan that processes each record independently with bounded retries on transient errors, (b) periodic background scan with an internal-only interval, (c) inline reclaim invoked from `.run()` / `.start()` / `get_active_run()` when those entry points observe a dead-lease in-progress record. All three MUST share a single reclaim helper.
- **FR-003**: The reclaim helper MUST use compare-and-swap on the lease ownership so two concurrent claims produce exactly one winner; the loser MUST re-read and fall through. Race outcome MUST be deterministic.
- **FR-004**: "Lease is dead" MUST be derived from the record alone (lease ownership mismatch with this process AND no live in-memory entry, OR lease expiry passed). A lease is "live" only if BOTH ownership matches AND expiry is in the future, OR an in-memory entry tracks it.
- **FR-005**: `get_active_run(task_id)` MUST consult the store (not only in-memory state). If the record is in-progress with a dead lease, it MUST perform inline reclaim as a hidden side effect and return a usable `TaskRun`. Terminal records return `None`. Eviction returns `None`.
- **FR-006**: A single classifier MUST be defined for store-write errors with four outcomes: `transient` (5xx, timeouts, throttling), `evicted` (HTTP 409 + body `$.error.code == "binding_mismatch"`), `conflict` (412 etag mismatch, or 409 with any other body), `permanent` (404, 400, unrecognised 4xx). Every store-write site (reclaim, lease renewal, terminal writes, input enqueue) MUST funnel through this classifier.
- **FR-007**: On `evicted` classification at a site that owns a locally-running task (renewal loop, terminal write), the framework MUST: cancel the local execution, suppress any pending terminal write, signal awaiters with `TaskConflictError`, log WARNING with correlation.
- **FR-008**: On `evicted` classification during inline reclaim at scheduling entry points (`.run()` / `.start()` / `get_active_run()`), the framework MUST map the outcome per Invariant 1 (caller observes the live-elsewhere / not-active outcome, NOT a new error type). Operator-facing logs are the only differentiator.
- **FR-009**: Test-only hooks MAY be added to drive the periodic scan deterministically (an internal trigger function or an importable interval constant for monkeypatching). They MUST NOT appear on the public surface. Tests using them MUST assert on public-surface outcomes (caller-visible `TaskRun`, `ctx.entry_mode`, store state), never on internal reclaim outcome variants.

#### Steering is multi-turn

- **FR-010**: `TaskResult.status` MUST be the Literal `"completed" | "suspended"`. The value `"superseded"` MUST NOT appear anywhere in the public surface. The `TaskResult.is_superseded` property MUST NOT exist. No code path MUST set `status="superseded"` on any `TaskResult` returned to user code.
- **FR-011**: When a handler returns a suspend envelope, the current turn's caller's `TaskResult` MUST be exactly `TaskResult(status="suspended", output=X, suspension_reason=R)` where X and R come from the handler. This MUST hold whether or not a steering input is queued. The suspend record AND the metadata snapshot MUST be durably persisted BEFORE any drain re-enters the handler.
- **FR-012**: When a handler returns a value or raises, the task transitions to its terminal state in a single store write that also clears any queued steering inputs. Every queued steerer's `TaskRun.result()` MUST then raise `TaskConflictError` with the appropriate `current_status` — the exact same exception type and shape a fresh `.start()` against an already-terminal task would raise. No new error type.
- **FR-013**: Any parallel "steering futures" tracking structure on `TaskManager` MUST be removed. The steerer's `TaskRun.result()` future MUST be bound via the same mechanism that binds the first turn's caller — the active result future for the current generation.
- **FR-014**: The steering-drain code path MUST be re-entry-only: read the queue, advance the generation, persist the steering-state mutation, bind the next generation's result future, return a new `TaskContext`. It MUST NOT resolve caller-visible futures (the suspend / completion path owns that delivery) and MUST NOT touch `ctx.metadata` (the boundary owns the flush).
- **FR-015**: `ctx.metadata` MUST be durably flushed at EVERY terminal-of-turn boundary — including the steering-drain shortcut paths (suspend-with-queued-input, return-with-queued-input). The dev-guide claim that "writes you forget to flush are still durable across a graceful boundary" MUST hold uniformly.

#### Cancellation surface

- **FR-016**: `ctx.cancel` MUST remain a bare `asyncio.Event`. No wrapping class. Existing `if ctx.cancel.is_set():` and `await ctx.cancel.wait()` patterns continue to work.
- **FR-017**: Two new `bool` properties MUST be added to `TaskContext`: `ctx.timeout_exceeded` (set by the timeout watchdog before it sets `ctx.cancel`) and `ctx.cancel_requested` (set by `TaskRun.cancel()` before it sets `ctx.cancel`). Both default `False`, are flipped to `True` when their cause fires, and are NEVER reset. Booleans accumulate; multiple causes can be `True` simultaneously.
- **FR-018**: Each cause's boolean MUST be set BEFORE the framework sets `ctx.cancel`, so a handler observing `ctx.cancel.is_set() == True` is guaranteed to see at least one cause boolean already `True`.
- **FR-019**: `ctx.pending_inputs: Sequence[Any]` MUST be removed from `TaskContext`. A new public `int` property `ctx.pending_input_count` MUST replace it. The count MUST be live (reflects current backlog, including inputs queued mid-handler). The queued input data itself MUST NOT be exposed on the public surface.
- **FR-020**: `ctx.was_steered` MUST be renamed to `ctx.is_steered_turn` AND its semantics MUST be fixed: True if and only if THIS invocation of the handler was constructed by the steering-drain code path. Every other entry path (fresh, normal resume, recovery) MUST yield `False`. `is_steered_turn` is orthogonal to `entry_mode` — `(entry_mode="recovered", is_steered_turn=True)` is a legal combination.
- **FR-021**: `ctx.steering_generation` MUST be removed from the public surface. (Any internal generation counter retained for framework bookkeeping is an implementation concern, decided in the plan phase.)
- **FR-022**: `TaskRun.terminate()` and the `TaskTerminated` exception class MUST be removed. `TaskRun.cancel()` is the single API for "stop this task"; the handler chooses the terminal shape via its reaction to `ctx.cancel.is_set()`. All internal plumbing supporting the terminate pathway (per-task terminate events, reason refs, dedicated cancellation branches) MUST be removed alongside the public surface.

#### Timeout

- **FR-023**: `@task(timeout=...)` MUST be per-turn, wall-clock, and durable across crashes within a turn. The framework MUST persist a turn-start timestamp at every turn-start boundary (fresh `.run()` / `.start()`, suspended-to-in_progress resume, steering drain re-entry). Crash recovery MUST NOT re-stamp the timestamp; the recovered watchdog computes `remaining = max(0, opts.timeout − (now − turn_started_at))`, clamped to `[0, opts.timeout]` for clock-skew safety.
- **FR-024**: The timeout watchdog MUST be respawned at the start of every logical turn — fresh handler entry, steering drain re-entry, and crash recovery re-entry. Retries within the same generation continue to share the watchdog (intentional: retries don't get extra time). At most one watchdog is live at a time; the previous is cancelled before the next spawns.
- **FR-025**: The watchdog is cooperative-only. On firing, it MUST set `ctx.timeout_exceeded = True` then `ctx.cancel.set()` then exit. It MUST NOT cancel the lease renewal or force-stop the handler. If the recovered watchdog's `remaining == 0`, it MUST fire immediately so the recovered handler sees the timeout cause from its first checkpoint.
- **FR-026**: The watchdog source docstring and the dev-guide entry for `@task(timeout=...)` MUST accurately describe the cooperative-only semantic. The misleading claim about automatic lease expiry MUST be removed. The watchdog-fired log message stays at INFO (exceeding the deadline is a handler concern, not a framework alarm).

#### Shutdown

- **FR-027**: `TaskContext` MUST gain an async method `exit_for_recovery()` taking no parameters. It MUST be callable only when `ctx.shutdown.is_set() == True`; calling it outside shutdown MUST raise `RuntimeError` at the call site (visible in user-code tracebacks). The framework MUST recognise the returned sentinel and (a) flush `ctx.metadata`, (b) release the lease, (c) leave the stored `status` as `in_progress` (NOT transition to `suspended`), (d) signal in-process awaiters with the standard cooperative-cancel result. The recovery scan re-enters the handler on the next process startup with `entry_mode == "recovered"`.
- **FR-028**: Queued steering inputs at the time `exit_for_recovery()` is called MUST be preserved in the persisted state — the framework does NOT drain them during shutdown. On recovery they remain queued and drain at the next turn boundary.

#### Transport

- **FR-029**: The hosted task-store client MUST be built on `azure.core.AsyncPipelineClient`. The raw `httpx.AsyncClient` MUST be removed. Bearer-token assembly MUST be handled by the standard policy, not per-request code at every call site.
- **FR-030**: The pipeline policy chain MUST include, in order: request-id, headers, user-agent (sdk_moniker `ai-agentserver-core/{VERSION}`), retry (configured to retry on 5xx + 408 + 429 only — NEVER on 409 regardless of body), bearer-token credential, task-API logging, distributed tracing. The chain MUST NOT include `ContentDecodePolicy`.
- **FR-031**: The task-API logging policy MUST allow-list operational headers (`x-ms-client-request-id`, `x-ms-request-id`, `etag`, `if-match`, `retry-after`, plus standard Azure operational headers). It MUST NOT log `Authorization` headers or request/response bodies above DEBUG.
- **FR-032**: Every status-bearing call site MUST funnel through the FR-006 classifier (no ad-hoc `raise_for_status`). 404 → `None` (for `get`) and 404 → `TaskNotFound` (for `update`, `delete`) outcomes are preserved by mapping `permanent`+404 to the per-verb expected outcome.
- **FR-033**: Every call-site body-parsing access MUST be wrapped to catch decode errors (Unicode, JSON, `azure.core` decode error). On failure the call site MUST surface a classified transport error carrying the response status, request-id header (if present), and a truncated body prefix for operator diagnosis. Body parsing happens at the call site, NEVER in middleware (responses-storage gzip lesson).
- **FR-034**: After the migration, `httpx` MUST NOT be imported anywhere under `azure-ai-agentserver-core/azure/`. If grep returns zero matches, `httpx` MUST be removed from the package's production install requirements (it MAY remain as a dev/test-only dependency during transition).

### Key Entities

The spec exposes only one new developer-facing surface: the boolean / count properties on `TaskContext` and the `exit_for_recovery()` method. All other entities below are internal to the framework — the implementation MAY choose any concrete shape that satisfies the contract.

- **Cancellation cause booleans** (`ctx.timeout_exceeded`, `ctx.cancel_requested`) and **steering count** (`ctx.pending_input_count`): public read-only properties on `TaskContext`. See FR-016..FR-021.
- **`ctx.is_steered_turn`**: public read-only boolean on `TaskContext`. See FR-020.
- **`ctx.exit_for_recovery()`**: public async method on `TaskContext`. See FR-027.
- **Internal: reclaim outcome** — discriminated outcome returned by the framework's internal reclaim helper (reclaimed / race-lost / evicted / transient-failure / record-terminal / not-found). Concrete shape TBD in the plan phase; never appears on the public surface.
- **Internal: store-error classifier** — pure function returning one of `transient | evicted | conflict | permanent`. Concrete signature TBD in the plan phase.
- **Internal: periodic-reclaim background task** — long-lived task owned by `TaskManager`. Created in `startup()`, cancelled in `shutdown()`. Implementation concern.
- **Internal: durable per-turn-start timestamp** — payload field persisted at every turn-start boundary for FR-023's wall-clock budget computation. Field name and on-the-wire format are plan-phase decisions.
- **Internal: shutdown-preserve sentinel** — return value of `ctx.exit_for_recovery()` that the framework recognises. Implementation concern; the developer-facing API is the method, not direct sentinel construction.

---

## Success Criteria *(mandatory)*

Each criterion is observable behaviorally or via public-surface inspection; no internal-implementation assertions.

- **SC-001 (recovery surface clean)**: `grep -rn 'stale_timeout' azure-ai-agentserver-core/azure/ai/agentserver/core/` returns zero matches. No test in the durable test suite references `stale_timeout`.
- **SC-002 (split-brain isolation)**: In a split-brain simulation (two `TaskManager` instances against the same session, with the store rejecting one side's writes via `binding_mismatch`), the handler executes exactly once across both instances. Exactly one terminal record exists in the store.
- **SC-003 (get_active_run resurrects orphans)**: For an in-progress record with a dead lease, `get_active_run()` returns a usable `TaskRun` and the handler re-enters with `entry_mode == "recovered"`. For a record with a live lease in this process, the existing handle is returned. For a terminal record, `None` is returned. For an evicted record, `None` is returned (operator log captures the eviction).
- **SC-004 (periodic recovery)**: With an internal interval test-override, a post-startup orphan is reclaimed within the interval without any user-space call.
- **SC-005 (startup hardening)**: A startup scan driven against a provider stub returning a mix of healthy / 5xx / 429 / 409+binding_mismatch / 404 / parse-error responses completes without raising. Every record is logged with a classification reason; transient errors are retried up to the bounded limit; vanished and evicted records are skipped.
- **SC-006 (scheduling-primitive invariance)**: A parametrized test sweeps `(run | start | get_active_run)` × `(steerable | non-steerable)` × `(live-mine | dead-reclaimable | dead-evicted)` and asserts the observable return/raise matches Invariant 1's table exactly. The eviction column produces the SAME `TaskConflictError` (for `.run`/`.start`) or the SAME `None` (for `get_active_run`) as the corresponding "task is live elsewhere / not active here" case — distinguishable only by WARNING log records.
- **SC-007 (steering surface clean)**: Searching the package surface for `superseded`, `is_superseded`, and any parallel-steering-futures tracking attribute returns zero matches. `TaskResult.status` literal arguments are exactly `("completed", "suspended")`.
- **SC-008 (steering-as-multi-turn equivalence)**: A parametrized sweep `(turn-1 ends with: suspend(output=X), suspend(output=None), return V, raise E)` × `(steerer queued mid-flight: yes, no)` asserts: caller-1's `TaskResult` is identical to the plain multi-turn cell (no `superseded` ever observed; emitted output never replaced); for `(terminal, queued)` cells the steerer's future raises `TaskConflictError` with the correct `current_status`; for `(suspend, queued)` cells the steerer's future resolves with whatever turn-2 emits.
- **SC-009 (metadata auto-flush invariant)**: A parametrized sweep over every terminal-of-turn boundary (normal-suspend, normal-complete, cooperative-cancel, exception, suspend-with-queued-steering, return-with-queued-steering, raise-with-queued-steering, shutdown-via-exit_for_recovery) asserts that a handler-written metadata marker (without explicit `flush()`) survives a simulated crash + provider re-read.
- **SC-010 (cancel-cause booleans)**: A parametrized sweep covering timeout-only, external-cancel-only, steering-only, composite (all three), and live-count-vs-snapshot semantics asserts the new properties reflect the expected state. A backward-compat assertion verifies existing `ctx.cancel.is_set()` and `ctx.cancel.wait()` patterns continue to work. A surface inspection asserts presence of `is_steered_turn`, `pending_input_count`, `timeout_exceeded`, `cancel_requested` and absence of `was_steered`, `pending_inputs`, `steering_generation` on `TaskContext`.
- **SC-011 (is_steered_turn correctness)**: A steerable task that was steered in turn-2, then suspended, then resumed by a fresh `.run()` from the developer enters turn-3 with `ctx.is_steered_turn == False`. A true drain re-entry observes `ctx.is_steered_turn == True`. Orthogonality: `(entry_mode="recovered", is_steered_turn=True)` is observable when the previous process crashed mid-drain.
- **SC-012 (per-turn durable timeout)**: A parametrized sweep on `@task(timeout=N)` covering fresh-turn, drain-re-entry, crash-recovery-within-budget, and crash-recovery-past-deadline asserts the watchdog spawns with the correct `remaining` budget and `ctx.timeout_exceeded` fires at the deadline anchored to turn-start.
- **SC-013 (clock-skew clamping)**: A test injecting backwards and forwards clock skew between the turn-start timestamp and watchdog spawn asserts `remaining` is clamped to `[0, opts.timeout]` in both directions.
- **SC-014 (terminate surface removed)**: `hasattr(TaskRun, 'terminate') == False`. Importing `TaskTerminated` from the durable package raises `ImportError`. No internal plumbing or test references the removed pathway.
- **SC-015 (`exit_for_recovery` semantics)**: A parametrized sweep covering (a) shutdown path leaves status `in_progress` with durable metadata and a clean awaiter signal, (b) fresh process re-enters with `entry_mode == "recovered"` and rehydrated metadata, (c) misuse outside shutdown raises `RuntimeError` at the call site with the task ending in `failed`. `inspect.signature(TaskContext.exit_for_recovery).parameters` contains only `self`.
- **SC-016 (transport — surface)**: `grep -r 'import httpx' azure-ai-agentserver-core/azure/ai/agentserver/core/` returns zero matches. The pipeline policy chain on `HostedTaskProvider` includes (and orders) the required policies and excludes `ContentDecodePolicy`.
- **SC-017 (transport — behavior)**: A fake transport injected into the pipeline verifies retry on 503 (exactly two requests for a one-retry-success), no retry on 409 regardless of body, correlation/auth/user-agent headers present, gzip round-trip end-to-end, non-JSON 200 body classified into a transport error.
- **SC-018 (developer guide alignment)**: The developer-guide review meta-test passes against the updated guide. Concretely: no `stale_timeout` / `superseded` / `is_superseded` / `was_steered` / `pending_inputs` / `steering_generation` / `EtagConflict` / "lease will eventually expire" appears in the guide; `timeout_exceeded`, `cancel_requested`, `pending_input_count`, `is_steered_turn`, `exit_for_recovery` are documented; `@task(timeout=...)` description includes the words "per-turn", "wall-clock", and "durable".

---

## Assumptions

- **Platform contract: orphan-sandbox rejection.** The task-store API rejects orphan-sandbox writes with `HTTP 409` and body `$.error.code == "binding_mismatch"`. If the platform later changes status code or body shape, the classifier mapping (FR-006) is updated; the architectural design is unchanged.
- **Store CAS support.** ETag-based compare-and-swap (`If-Match`) is available on the task store and used by the provider adapter for PATCH operations involved in reclaim, lease renewal, and terminal writes. Any adapter currently issuing unconditional PATCHes is in scope to fix.
- **Reads are not rejected for orphan sandboxes.** Only writes are. The framework needs to read records even from an orphan sandbox to make the eviction determination.
- **Single session per process.** A `TaskManager` process serves a single `session_id` (foundry one-process-per-session model). Multi-session-per-process is not a target of this spec.
- **NTP-synchronised hosts (best-effort).** Clock-skew clamping (FR-023) protects the framework if skew is bounded, but operators should run NTP-synchronised hosts.

---

## Docs ↔ Samples Loop *(mandatory)*

### Authoritative surfaces

- **`sdk/agentserver/azure-ai-agentserver-core/docs/durable-task-guide.md`** — single developer-facing guide. Owns the mental model and the public-contract description. After this spec, the guide accurately reflects: recovery is automatic and `ctx.entry_mode == "recovered"` is the only handler-author signal; `TaskConflictError` is the single error type for any "task is busy / not available" state; `TaskResult.status` is `"completed" | "suspended"` only; steering is plain multi-turn with a queue; cancel causes are observable via independent booleans on `TaskContext`; `@task(timeout=...)` is per-turn / wall-clock / durable / cooperative-only; metadata auto-flushes at every terminal-of-turn boundary; `ctx.exit_for_recovery()` is the prescribed shutdown shape.
- **`sdk/agentserver/azure-ai-agentserver-core/CHANGELOG.md`** (pre-release section) — reflects every public-surface change as initial-release shape, NOT "breaking" (see the pre-release scope note at the top of this spec).
- **`sdk/agentserver/azure-ai-agentserver-core/tests/durable/test_dev_guide_review.py`** — meta-test enforcing guide ↔ implementation alignment. Gains new presence-and-absence invariants for the renamed / removed / added symbols.
- **Source docstrings** for any symbol whose contract changes (the timeout watchdog, the steering-drain code path, the pipeline-construction comment, `TaskResult` class docstring, the new `TaskContext` properties and `exit_for_recovery` method). All must agree with the developer guide.

### Authoring sequence

1. **Update the developer guide first** to match every contract in this spec. Steering, cancellation, timeout, shutdown, and metadata sections all get rewritten or extended; the §Reference section reflects the new `TaskContext` surface.
2. **Extend the guide-review meta-test** with the presence/absence invariants implied by FR-001 / FR-010 / FR-016..FR-021 / FR-027.
3. **Update the CHANGELOG** to enumerate the final public surface as initial-release shape.
4. **Update source docstrings** to agree with the guide.
5. **Write tests RED first, then code** per Constitution Principle XII.

If a test needs to express something the guide doesn't describe, the guide is wrong — fix the guide first.

### Samples affected

A scan of `azure-ai-agentserver-core/samples/` and `azure-ai-agentserver-invocations/samples/` for each removed / renamed symbol found:

| Surface change | Sample impact | Required action |
|---|---|---|
| `TaskResult.status="superseded"` removed | The string `"superseded"` appears in several invocation samples as their OWN application-level status (stored in their own per-sample stores, not the framework's `TaskResult`). Verified by surface search returning zero framework-API usages. | No change required. The dev guide must clearly state `TaskResult.status` is `"completed" | "suspended"` only so developers do not expect a `"superseded"` framework value. |
| `stale_timeout` removed | Zero matches in samples. | No change. |
| Cancel-cause booleans added; `ctx.cancel` unchanged | Samples use `ctx.cancel.is_set()` and `ctx.cancel.wait()` — fully backward-compatible. | Recommended (not required): add one worked example demonstrating composite-case branching on the new booleans (best home: an invocation sample with both steering and timeout paths). |
| Steering-surface cleanup (`pending_inputs` → `pending_input_count`, `was_steered` → `is_steered_turn`, `steering_generation` dropped) | Any sample using the old names must migrate. Audit during implementation: `grep -rn 'pending_inputs\|was_steered\|steering_generation' samples/`. | Required for any matching sample. Recorded in the conformance gap-list deliverable. |
| Metadata auto-flush invariant tightened | Samples use explicit `await ctx.metadata.flush()` (still recommended as a fence before at-most-once side effects). | No change. |
| Per-turn durable timeout | No sample currently sets `@task(timeout=...)`. | Recommended (not required): add one worked example. |
| Transport on `azure.core.AsyncPipelineClient` | Internal-only. | No change. |
| Terminal-with-queued-input shape | Samples don't currently catch `TaskConflictError` at the steerer side. | Recommended (not required): mention this outcome in the relevant sample READMEs. |

**Loop completion criterion (samples)**: the `durability-sample-checklist-template.md` (Constitution Principle IX) runs against any sample modified by this spec. Recommended-but-not-required updates above MAY be deferred with a one-line justification recorded in `tasks.md`.

---

## Durability Contract Conformance *(Constitution Principle X)*

This spec amends recovery behavior. The `durability-contract.md` matrix is about response-stream events under crash; recovery / eviction is a separate axis. The decision:

- [ ] **Amend `durability-contract.md`** with a cross-cutting note (NOT a new matrix row) covering the `binding_mismatch` protocol and the (lease-state × steerable) callsite outcome table from Invariant 1. The amendment lands in the same PR as the implementation.
- [ ] **FR-015 (metadata auto-flush)** lives at the *core-primitive* layer (Principle XII), not the *response-stream* layer (Principle X). Its conformance test lives in `tests/durable/`. The matrix gets no new row for this; the dev guide's lifecycle-boundary description is the relevant doc surface.
- [ ] **Conformance tests** for the new eviction / classifier behavior live in a new test module under `tests/durable/`. Parametrize across the entry points (`.run`, `.start`, `.get_active_run`, lease-renewal, terminal write).
- [ ] **TDD ordering**: tests land RED before implementation lands GREEN. Verified from commit history.
- [ ] **No synthetic shortcuts**: use the real provider stub to return `409 + binding_mismatch`; do not monkey-patch the classifier or fabricate eviction outcomes. Crash-recovery scenarios use the existing `_crash_harness` patterns from prior specs.
- [ ] **Completeness meta-test** (`test_contract_completeness.py`) stays green — this spec does not add a matrix row.
- [ ] **Dev guide updated** per the Docs ↔ Samples Loop section.
- [ ] **Sample checklist** run per the "Samples affected" subsection.

---

## Core Durable-Task Primitive Conformance *(Constitution Principle XII)*

### Affected public symbols

This spec touches the public surface of `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/` in the following ways. Every change MUST be backed by a conformance test landing RED before implementation.

**Removed:**
- `@task(stale_timeout=...)` kwarg, `Task.options(stale_timeout=...)`, `TaskOptions.stale_timeout` slot, any staleness-heuristic helper (FR-001).
- `TaskResult.status == "superseded"` value, `TaskResult.is_superseded` property (FR-010).
- `TaskRun.terminate()`, `TaskTerminated` exception (FR-022).
- `ctx.pending_inputs`, `ctx.was_steered`, `ctx.steering_generation` (FR-019, FR-020, FR-021).

**Added:**
- `ctx.timeout_exceeded: bool`, `ctx.cancel_requested: bool`, `ctx.pending_input_count: int`, `ctx.is_steered_turn: bool` on `TaskContext` (FR-016..FR-021).
- `TaskContext.exit_for_recovery()` async method (FR-027).

**Behavior-changed (signature unchanged):**
- `TaskManager.get_active_run(task_id)` — now consults the store and inline-reclaims dead leases (FR-005).
- `@task(timeout=...)` — semantic sharpened to per-turn / wall-clock / durable / cooperative-only (FR-023..FR-026).
- `TaskRun.cancel()` — handler now owns the terminal shape (no force-fail pathway) (FR-022).
- Bytes-on-the-wire behavior of `HostedTaskProvider`'s public methods — same public method signatures, but bodies migrate to `azure.core.AsyncPipelineClient` (FR-029..FR-034). The `credential` parameter type SHOULD be re-typed to `AsyncTokenCredential` for proper typing.

**Unchanged:**
- `ctx.cancel` remains a bare `asyncio.Event`. `ctx.shutdown` remains a separate bare `asyncio.Event`. `EntryMode` Literal values are unchanged.

### Exit checklist

- [ ] **Conformance gap-list document produced.** Required deliverable in this spec's directory: `conformance-gap-list.md`. For each affected symbol, record the existing test file covering current behavior, the decision (extend test X / create new test Y) with justification, and the task ID in `tasks.md` that lands the test RED.
- [ ] **Non-duplication rule satisfied.** Extend existing test files (`test_lifecycle.py`, `test_options.py`, `test_decorator_validation.py`, `test_steering.py`, the equivalent for `get_active_run`) rather than spawning parallel modules. A genuinely new concern (split-brain, transport) gets its own module — justified in the gap list.
- [ ] **Every removed / changed / added symbol has a paired conformance test** asserting its new behavior (TypeError on removed kwarg; reclaim semantics on `get_active_run`; presence/absence of cancel-cause booleans; etc.).
- [ ] **TDD ordering verified.** RED-first, GREEN-second commits.
- [ ] **No synthetic-bypass shortcuts.** No direct monkeypatching of `TaskContext`; use provider stubs and the test-only hooks declared in FR-009 only. Tests using FR-009 hooks assert public-surface outcomes, not internal classifier results.
- [ ] **Completeness meta-test** (`test_contract_completeness.py`) stays green.
- [ ] **Dev guide updated** per Docs ↔ Samples Loop above; doc-review meta-test passes.
