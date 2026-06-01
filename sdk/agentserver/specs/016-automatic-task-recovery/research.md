# Research: Durable-task primitive contract hardening (Phase 0)

This artifact captures the design decisions that led to spec 016, restated in the speckit Decision / Rationale / Alternatives format. The iteration history that produced these decisions is in [`cancel-surface-proposal.md`](./cancel-surface-proposal.md) and the session plan; this document is the consolidated reference.

All decisions are **locked in**. There are no outstanding NEEDS CLARIFICATION items. Two implementation choices are deferred to `/speckit.tasks` (FR-009 test-hook shape; internal `_steering["generation"]` deletion); both are plan-phase implementation decisions, not unresolved contract questions.

---

## Decision 1 — Recovery is automatic; no developer knob (`stale_timeout` removed)

**Decision**: Remove `stale_timeout` from `@task`, `Task.options()`, `TaskOptions`, `TaskContext`, every public docstring, doc, and sample. Recovery is framework-managed and observable only via `ctx.entry_mode == "recovered"`.

**Rationale**: `stale_timeout` was a developer-facing knob that leaked an implementation concern (recovery liveness heuristic) into handler authoring. Recovery is the framework's responsibility — the handler's only concern is idempotency, signalled via `ctx.entry_mode`. Keeping the knob forced every handler author to make a decision they have no business making.

**Alternatives considered**:
- Keep `stale_timeout` with a sensible default — rejected: still leaks the knob; default values are wrong for most workloads.
- Move `stale_timeout` to a global config — rejected: still developer-facing; doesn't fix the "I have to think about this" problem.

---

## Decision 2 — Three-layer recovery architecture

**Decision**: Provide three internal recovery paths sharing a single reclaim helper: (a) hardened startup scan with per-record `try/except` and bounded retries on transient errors; (b) periodic background scan with an internal-only interval; (c) inline reclaim invoked from `.run()` / `.start()` / `get_active_run()` when those entry points observe a dead-lease in-progress record.

**Rationale**: The current codebase has one recovery path (startup scan). Mid-lifetime orphans are unrecoverable. Layer (b) catches orphans no caller touches. Layer (c) recovers the moment relevant traffic arrives. All three sharing a single reclaim helper guarantees consistent CAS protection and consistent classification of outcomes.

**Alternatives considered**:
- Only periodic scan (drop layers (a) and (c)) — rejected: startup scan is deterministic for cross-process orphans; inline reclaim is responsive when traffic is bursty.
- Per-entry-point custom recovery logic — rejected: violates DRY; risks divergent error handling.

---

## Decision 3 — Caller-observable invariance across lease states (`binding_mismatch` is internal)

**Decision**: `.run()` / `.start()` / `get_active_run()` outcomes MUST be identical for the live-lease, dead-lease-reclaimable, and dead-lease-evicted (`binding_mismatch`) cases — collapsed to the "live elsewhere / not active here" outcome the caller would have observed against a live competitor. No new error type, no new return shape, no leaked split-brain state.

**Rationale**: User direction: "Re open question, there shoul dbe no change in behviour for get_active_run.. the behaviour of all of these methods start/run/get_active_run remain the same as how they would respond if the task is already running in current progress." Eviction is purely framework-internal — it produces operator logs but never reaches user code as a distinguishable signal. This keeps the caller's mental model simple ("the task is either mine, or not").

**Alternatives considered**:
- New `TaskEvictedError` exception type — rejected: forces every caller to branch on eviction; provides no actionable difference from the existing "task is busy" outcome.
- Boolean `was_evicted` field on `TaskConflictError` — rejected: same problem; leaks an internal concern.

---

## Decision 4 — Steering is plain multi-turn with a queue (no `superseded` status)

**Decision**: Remove `TaskResult.status == "superseded"`, remove `TaskResult.is_superseded`, remove parallel future-tracking on `TaskManager`. The steering drain re-enters the handler exactly like any other multi-turn re-entry. The current turn's caller observes the natural suspend/completed/failed outcome from the handler. If the handler terminates instead of suspending, queued steerers receive `TaskConflictError` (same shape as a fresh `.start()` against an already-terminal task). Metadata auto-flushes at every terminal-of-turn boundary, including drain shortcuts.

**Rationale**: User direction: "I am now reconsidering the cancellation sinal having reason... steering is just multi turn with queueing mechanics. To the caller calling start/run he sees no different betwene either." The framework cannot observe whether the handler honored cooperative cancel — all three handler strategies (yield / wind-down / ignore-and-finish) look identical at the framework boundary. A status that pretends the framework knows is a non-fact on the public surface.

**Alternatives considered**:
- Keep `superseded` with documentation clarifying it's the framework's best-guess — rejected: leaks a non-fact.
- Make `superseded` opt-in via a decorator flag — rejected: doesn't fix the conceptual leak.

---

## Decision 5 — `ctx.cancel` stays bare; independent cause booleans per cause

**Decision**: `ctx.cancel` remains a bare `asyncio.Event`. Two new public `bool` properties on `TaskContext`: `ctx.timeout_exceeded` (set by the timeout watchdog before `ctx.cancel.set()`) and `ctx.cancel_requested` (set by `TaskRun.cancel()` before `ctx.cancel.set()`). Both never reset; multiple can be `True` simultaneously when causes stack. Steering pressure is observable via `ctx.pending_input_count > 0`. `ctx.shutdown` remains a separate `asyncio.Event` (different concern, different handler action).

**Rationale**: User direction across three iterations (Iter 14b, multiple turns): composite cases are real (steering → timeout → explicit cancel can stack); first-reason-wins (the alternative wrapper-class designs) discards information. Independent booleans accumulate naturally; no information loss. The handler can branch on any combination of causes.

**Alternatives considered**:
- `CancelSignal` wrapper class with a `.reason: CancelReason` enum (Iter 12-13 proposal) — rejected: first-reason-wins loses information in composite cases; wrapping class is unnecessary indirection on a hot path; the `is_set()` / `wait()` compatibility wrapper is more surface than two `bool` properties.
- Fold `ctx.shutdown` into the cancel enum — rejected: shutdown requires a different handler action (`ctx.exit_for_recovery()`) and is optional to implement; merging conflates two distinct concerns.
- Single `ctx.cancel_reason: Literal[...]` property without booleans (Proposal D) — rejected: same first-reason-wins problem as the enum.
- Zero new surface; document a 3-way `if` recipe (Proposal A) — rejected: fall-through "must be timeout" inference is fragile; can't differentiate timeout from external cancel.

---

## Decision 6 — Steering surface cleanup (`pending_input_count`, `is_steered_turn`, drop `steering_generation`)

**Decision**: Replace `ctx.pending_inputs: Sequence[Any]` (entry-time snapshot exposing future-turn input data) with `ctx.pending_input_count: int` (live count, no data exposure). Rename `ctx.was_steered: bool` (sticky-True after any drain forever) to `ctx.is_steered_turn: bool` and fix the semantic (True only when THIS invocation was constructed by the drain code path). Drop `ctx.steering_generation` from the public surface entirely. `is_steered_turn` is orthogonal to `entry_mode` — both can vary independently.

**Rationale**:
- `pending_inputs` exposing the queued data tricked developers into thinking they could process those inputs in the current execution. They can't — queued inputs belong to future turns. The live integer count gives the legitimate information (pace decisions like "rapid-drain if >2") without the misleading data exposure.
- `was_steered` answered the wrong question ("has the task ever been steered?") via a sticky-True bug. The developer's actual need is "is this current invocation a drain re-entry?". Rename + fix.
- `steering_generation` counted drains specifically (not normal turns), so it's not a useful "session length" metric; handler-owned `ctx.metadata` counters cover any legitimate use case. Internal `_steering["generation"]` field MAY be retained for framework bookkeeping pending a plan-phase trace.

**Alternatives considered**:
- Keep `pending_inputs` with documentation that it's a snapshot — rejected: documentation doesn't fix the misleading API shape; developers will hit it.
- Fix `was_steered` in place without renaming — rejected: name still confuses (past-tense suggests "task was steered at some point").
- Extend `EntryMode` with `"steered"` — rejected: user direction explicitly preserved EntryMode purity; drain re-entry can compose with crash-recovery (entry_mode="recovered", is_steered_turn=True), so the two axes are orthogonal and must remain separately observable.

---

## Decision 7 — Per-turn, wall-clock, durable timeout

**Decision**: `@task(timeout=...)` is per-turn (each new turn — fresh `.run()` / `.start()`, suspended-to-in_progress resume, drain re-entry — gets the full budget), wall-clock (anchored to a durable per-turn-start timestamp persisted in the record), and durable across crashes within a turn (recovery within the turn preserves the budget). The watchdog is cooperative-only — an ignoring handler runs until process death or external cancel; the lease is NOT force-expired. The misleading watchdog docstring claiming automatic lease-expiry recovery is corrected.

**Rationale**: User direction: "We need per-turn, wallclock, durable.. the perturn includes crash recoveries. Doe snot include other turns including steering turns." The current per-invocation in-process `asyncio.sleep` is wrong on two axes: it shares budget across drain re-entries (treating them as continuations of the same turn) and it resets on crash recovery (net effective compute per turn is unbounded). The durable wall-clock anchor closes both gaps.

**Alternatives considered**:
- Per-invocation non-durable timer (status quo) — rejected: unbounded compute under repeated crash + recovery.
- Per-turn fresh-on-recovery — rejected: violates "wall-clock per turn" — a turn that spans multiple recoveries should still hit the configured deadline.
- Force-expire the lease on watchdog fire — rejected: violates the "handler is in charge of cancellation" principle established for steering; user explicit direction "cooperative only".
- Add a separate `terminate_on_timeout` flag — rejected: re-introduces the force-fail surface that FR-022 (terminate removal) explicitly closes.

---

## Decision 8 — `ctx.exit_for_recovery()` is the prescribed shutdown shape

**Decision**: Add `async def exit_for_recovery(self)` on `TaskContext` (no parameters; precondition `ctx.shutdown.is_set()` is true, else `RuntimeError` at the call site). Returns a sentinel the framework recognises as "preserve `in_progress` status; the recovery scan re-enters on next-process startup".

**Rationale**: User direction confirmed Option II (explicit framework API) with constraints: no parameters (framework knows the cause), only callable during shutdown (precondition enforced). Today the only ways to leave a task `in_progress` for restore-on-restart are `raise asyncio.CancelledError` (asyncio coupling leaks into handler code; easily swallowed by stray `try/except`) or letting the framework force-cancel at grace expiry (developer is passive). `ctx.suspend()` silently transitions to `suspended` (which is NOT auto-recovered). The explicit framework API closes the discoverability gap.

**Alternatives considered**:
- Document `raise asyncio.CancelledError` as the prescribed pattern (Option I) — rejected: weird-looking, asyncio-coupled, easy to swallow by a stray `try/except`; not discoverable from the dev guide.
- Add a `reason=` parameter (e.g., `ctx.exit_for_recovery(reason="shutdown")`) — rejected: the framework already knows the cause (`ctx.shutdown` is the only legitimate trigger).
- Allow `exit_for_recovery()` outside shutdown context — rejected: would defeat the lifecycle contract; misuse must be loudly visible.

---

## Decision 9 — Transport on `azure.core.AsyncPipelineClient`; `ContentDecodePolicy` excluded

**Decision**: Migrate `HostedTaskProvider` from raw `httpx.AsyncClient` to `azure.core.AsyncPipelineClient` with the standard policy stack (request-id, headers, user-agent, retry, bearer-token credential, task-API logging, distributed tracing). `ContentDecodePolicy` MUST be excluded — the responses-storage gzip lesson, restated. Body parsing happens at the call site with defensive error handling.

**Rationale**: The current raw-httpx path has no policy stack — no retry, no correlation headers, no distributed tracing, no shared bearer-token policy, no user-agent, and no consistent seam for the FR-006 classifier. The sibling `FoundryStorageProvider` already runs on `azure.core` and learned the `ContentDecodePolicy` lesson: it eagerly decodes every body as JSON in middleware and crashes on gzip / non-UTF-8 / gateway-HTML payloads before app code can handle the response. The task client needs the same migration and the same exclusion.

**Alternatives considered**:
- Stay on raw httpx with hand-rolled retry and headers — rejected: re-inventing the `azure.core` policy machinery is wasted scaffolding; the FR-006 classifier needs a consistent seam.
- Migrate to `azure.core` WITH `ContentDecodePolicy` — rejected: explicit gzip / non-UTF-8 / HTML crash risk; the responses-storage CHANGELOG documents this lesson with a reproducer.

---

## Decision 10 — Lease owner includes agent name AND session ID

**Decision**: `derive_lease_owner(...)` resolves both the agent name (from `FOUNDRY_AGENT_NAME`) and the session ID. The signature changes from `(session_id)` to `(agent_name, session_id)`. On-the-wire format is plan-phase detail; the contract is "both components present and stable across process restarts within the same (agent, session) pair".

**Rationale**: User direction (Iter 15). The current `session:{session_id}` derivation collides across two different agents that happen to share a session ID. `binding_mismatch` (FR-006) protects against split-brain on the same agent+session but is silent on this orthogonal case. Including the agent name closes the hole at the framework layer.

**Alternatives considered**:
- Rely solely on `binding_mismatch` to catch the collision — rejected: `binding_mismatch` is rejection at the platform layer; for the multi-agent collision case the platform might NOT reject (both processes are legitimate from the platform's perspective).
- Use a hash of `(agent, session)` for the owner string — rejected: harder to debug from operator logs; the readable format is preferred.

---

## Decision 11 — Remove `TaskRun.terminate()` and `TaskTerminated` entirely

**Decision**: Remove `TaskRun.terminate()`, the `TaskTerminated` exception, and all internal plumbing (per-task terminate events, reason refs, dedicated cancellation branches). `TaskRun.cancel()` is the single API for "stop this task"; the handler chooses the terminal shape via its reaction to `ctx.cancel.is_set()`.

**Rationale**: User direction: `terminate()` adds a third "stop the task" pathway that overlaps `.cancel()` with marginally different semantics (forced failure record vs. handler-chosen terminal). The plumbing cost is ~25 lines across ~13 call sites for marginal benefit. A handler that wants forced-failure semantics achieves it via `if ctx.cancel.is_set(): raise SomeError` — the right layering per the established "handler is in charge of cancellation" principle.

**Alternatives considered**:
- Keep `terminate()` with a `force=` parameter — rejected: still duplicate API surface; still violates the layering principle.
- Replace `terminate()` with `cancel(force_fail=True)` — rejected: same problem; force-fail belongs in the handler, not the framework.

---

## Plan-phase implementation decisions (NOT clarifications)

These are choices to be made during `/speckit.tasks`, not unresolved contract questions:

1. **FR-009 test-only hook shape** — interval-override-constant vs. trigger-function-on-manager. Both are valid; pick based on which is least invasive to existing tests during `/speckit.tasks` task breakdown. Recorded in `conformance-gap-list.md`.
2. **Internal `_steering["generation"]` retention** — trace every read site against the post-FR-013/14 invariants. If no load-bearing internal use remains, delete in the same PR (with a one-line gap-list note). Otherwise retain internally with an inline justification comment in `_manager.py`.
3. **`_turn_started_at` on-the-wire format** — payload field name + serialization. The contract is "ISO-8601 UTC string, persisted at every turn-start boundary, NOT re-stamped on recovery"; the exact field name (`_turn_started_at` vs. `_lease["turn_started_at"]` vs. some other location) is a plan-phase decision documented in `data-model.md`.

---

## Reference material

- [`./spec.md`](./spec.md) — the locked-in contract (469 lines).
- [`./cancel-surface-proposal.md`](./cancel-surface-proposal.md) — full iteration history of the cancel-surface design (Proposals A–E). Reference-only; not normative.
- [`durability-contract.md`](../durability-contract.md) — the response-stream durability matrix. Amended in this PR with the cross-cutting `binding_mismatch` note (Principle X).
- [`stale-timeout-analysis.md`](../stale-timeout-analysis.md) — earlier analysis that led to the recovery-as-framework-responsibility framing.
