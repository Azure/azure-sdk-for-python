# Feature Specification: Automatic task recovery (defense-in-depth)

**Feature Branch**: `feature/agentserver-durable-tasks` (continuing on current branch; no new branch)
**Created**: 2026-05-30
**Status**: Draft (awaiting user approval)
**Input**: User description: "Three-layer defense-in-depth recovery: hardened R-startup with internal retries, infrequent periodic reclaim loop, plus lease-liveness check on every user-space entry point (.run / .start / get_active_run). Remove `stale_timeout` from the developer surface entirely. Handle the platform's split-brain (orphan sandbox) case via 409 + `$.error.code == 'binding_mismatch'`."

## Context

> **Pre-release scope note.** The durable-task primitive in `azure-ai-agentserver-core` is being developed for the first time on the `feature/agentserver-durable-tasks` branch and has not been released. This spec is therefore an in-place evolution of an unshipped contract — there is no migration path to write, no rename map to publish, and the change set MUST NOT be framed as "breaking" in CHANGELOG, dev guide, or anywhere else. Every reference in this document to "removing" or "replacing" a surface is shorthand for "rewriting an unreleased pre-release contract".

This spec is the direct continuation of `sdk/agentserver/specs/stale-timeout-analysis.md`, which arrived at the following conclusion through user pushback on the recently shipped `stale_timeout` decorator surface (`feature/agentserver-durable-tasks` commit `ef8b27c656`):

- `stale_timeout` should not be a developer-facing concept *at all*. Recovery is the framework's responsibility.
- `.run()` / `.start()` are scheduling primitives, not recovery primitives. Their callsite outcome must be the standard scheduling decision regardless of any recovery side-effect.
- The current codebase has exactly one automatic recovery path: a one-shot startup scan. No periodic background loop, no callsite-driven recovery free of `stale_timeout`. This leaves mid-lifetime orphans unrecoverable.
- The platform may, due to a bug, spin up two sandboxes for the same session. The task-store API is the arbiter — orphan sandbox writes are rejected with `HTTP 409 + {"error": {"code": "binding_mismatch"}}`. The framework must treat that signal as authoritative eviction.

This spec turns those conclusions into deliverable work. The analysis doc is reference material; this spec is the contract.

### Scope expansion: steering is plain multi-turn

A second simplification rides on the same release branch. The current steering implementation introduces a synthetic `TaskResult.status == "superseded"` plus a parallel `_pending_steering_futures` array on `TaskManager`, and `_try_drain_steering` races ahead of the suspend/complete path to resolve the original caller's future with that synthetic status. This contradicts the durable-task mental model and must be removed:

- **Steering is plain multi-turn with a queueing mechanism on top — nothing more.** The original caller and the steerer are simply caller-of-turn-N and caller-of-turn-N+1. From either caller's perspective the observable contract is identical to plain multi-turn — they don't have a separate "steering" status to branch on.
- **The framework cannot observe "supersede".** `ctx.cancel` is an *advisory* hint that more input is queued. The handler may yield immediately, wind down to a safe checkpoint and then suspend, or ignore the hint and finish the turn — all three look identical at the framework boundary (each ends in `await ctx.suspend(...)` or `return V` or a raise). A status that pretends the framework can distinguish "the handler was superseded" from "the handler suspended normally" leaks a non-fact.
- **Output must never be dropped on the floor.** A handler's `ctx.suspend(output=X)` always belongs to the current turn's caller; the suspend resolution path already owns that delivery. The drain logic must not race the suspend resolution and replace `output=X` with `None`.
- **Terminal-of-turn outcomes propagate naturally.** If the handler suspends, the current turn's caller sees `TaskResult(status="suspended", output=X)`; if a steering input is queued, the framework re-enters the handler with that input as the next turn — same as the second turn of any plain multi-turn task. If the handler returns or raises, the task is *terminal* (no re-entry possible); the current turn's caller sees the natural success or failure outcome, and any queued steering input becomes unservicable.

This spec therefore also: removes `"superseded"` from `TaskResult.status`; removes `_pending_steering_futures`; restructures `_try_drain_steering` to run strictly *after* the suspend resolution AND the lifecycle-boundary `flush_all()`; codifies what happens to a queued steering input when the handler chose to terminate (return or raise) rather than suspend; and closes a verified gap where the current steering-drain code path silently skips the metadata auto-flush that the developer guide promises at every lifecycle boundary (verified against `_manager.py:1156-1175` and `_manager.py:1197-1223`; the `flush_all()` at the non-steering boundaries `_manager.py:1179`, `:1227`, `:1268`, `:1333` is correct, but the steering-drain shortcut bypasses both the flush and the terminal write — unflushed metadata writes from the displaced turn are lost on crash). Detailed requirements in FR-020 through FR-024a.

### Scope expansion: task API transport on `azure.core` pipeline

A third simplification rides on the same release branch. `HostedTaskProvider` (`azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_client.py`) is currently built directly on `httpx.AsyncClient` with no policy stack — no retry, no structured logging, no distributed tracing, no request-id correlation, no shared bearer-token policy, no user-agent moniker. The sibling `FoundryStorageProvider` (responses package) already migrated to `azure.core.AsyncPipelineClient` and carries the policy chain the platform expects, plus a hard-won lesson: `ContentDecodePolicy` MUST be excluded because it eagerly decodes every body as JSON in middleware and crashes with `UnicodeDecodeError` on gzip / non-UTF-8 / gateway-HTML payloads before app code can handle the response (responses package `CHANGELOG.md:73`, `_foundry_provider.py:167-175`).

The task client must be brought onto the same transport and inherit the same lesson. Specifically:

- The `azure.core` pipeline gives us first-class retry (`AsyncRetryPolicy`), bearer-token auth (`AsyncBearerTokenCredentialPolicy`), correlation headers (`RequestIdPolicy`, `DistributedTracingPolicy`), user-agent moniker (`UserAgentPolicy`), and a single seam where the task-store error classifier from FR-013 can be invoked. None of these exist on the current raw-httpx path; the rewrite is what lets FR-013 / FR-014 / FR-016 / FR-017 be implemented at all (without the policy chain there is no consistent place to inspect 409 bodies or trigger the eviction local-cleanup).
- `azure.core` does NOT auto-raise on non-2xx (unlike `httpx.Response.raise_for_status`). The migration MUST therefore replace every `response.raise_for_status()` call site with explicit status inspection that funnels through `_classify_store_write_error` (FR-013) — converting the existing 404→`None` / 404→`TaskNotFound` branches into a uniform classified-error path.
- `ContentDecodePolicy` MUST NOT be added to the pipeline. The task client's serializers MUST call `http_response.text()` (or equivalent) directly at the call site, wrapped in `try/except (UnicodeDecodeError, json.JSONDecodeError)` so a gzip / HTML / corrupted body becomes a classified transport error instead of a buried middleware crash. This is the responses-storage gzip-fix invariant, restated for the task client.
- The `httpx` dependency MAY be removed from `azure-ai-agentserver-core` entirely once `HostedTaskProvider` no longer needs it (verify via grep of the durable package; if no remaining consumer exists, drop from `pyproject.toml` install requires).

Detailed requirements in FR-025 through FR-030.

### Scope expansion: cancel-signal carries a reason; per-turn timeout budget

A fourth simplification rides on the same release branch. `ctx.cancel` is currently a bare `asyncio.Event` used as both the timeout watchdog's signal (`_manager.py:1029`) and the steering drain's "more input is queued, please wind down" signal (`_manager.py:1485-1486`). Two consequences fall out:

- **The handler cannot distinguish *why* it was asked to wind down.** Strategies B and C from the steering framing (wind down to checkpoint vs. ignore and finish) might legitimately want to depend on whether the cancel was "more user input arrived" (steering) vs. "you've blown the per-turn deadline" (timeout) — but today both arrive as the same anonymous `is_set() → True`. There is no `ctx.cancel.reason` API.
- **The execution-timeout watchdog is spawned in `_execute_task` *outside* the loop that handles steering-drain re-entry, so the budget is shared across all generations of a single `_execute_task` invocation.** A 30s-budget steerable task whose first generation runs 25s before suspending and triggering a drain has only 5s left before the watchdog fires on generation 2 — even though the developer almost certainly expected each turn to get its own 30s window. This contradicts the "steering is plain multi-turn" framing of FR-020..FR-024a, where every turn is its own logical unit.

Additionally, the watchdog docstring at `_manager.py:1018-1021` claims *"If [the handler] doesn't [check ctx.cancel], the lease will eventually expire and the task will be recovered"* — that claim is **false**. The renewal loop is driven by a separate `renewal_cancel` event that the watchdog does not touch. If a handler ignores `ctx.cancel`, the lease keeps being renewed and the task runs indefinitely until process death or an explicit `terminate()`. We keep the watchdog cooperative-only (changing it to forcibly cancel renewal would break the user's repeatedly-stated principle that the handler is in charge of cancellation), but the docstring MUST be corrected so operators and reviewers don't rely on a self-recovery property that doesn't exist.

Detailed requirements in FR-031 through FR-034.

## Design invariant (load-bearing)

**Caller-observable behavior of `.run() / .start() / get_active_run()` is invariant across `live | dead+reclaimed | dead+evicted` lease states.** These methods are scheduling/lookup primitives whose contract is defined entirely against the "task is already running in the current process" mental model. The framework opportunistically uses them as *additional signals* to trigger recovery (reclaim when the lease is dead), but the reclaim is a hidden side effect — it never changes the caller's observable outcome.

Concretely:

| Entry point | Lease: Live (mine) | Lease: Dead+reclaimed | Lease: Dead+evicted (`binding_mismatch`) |
|---|---|---|---|
| `.run()` steerable | queue + await result | reclaim → queue + await result | `TaskConflictError` |
| `.run()` non-steerable | `TaskConflictError` | reclaim → `TaskConflictError` | `TaskConflictError` |
| `.start()` steerable | queue + return `TaskRun` | reclaim → queue + return `TaskRun` | `TaskConflictError` |
| `.start()` non-steerable | `TaskConflictError` | reclaim → `TaskConflictError` | `TaskConflictError` |
| `.get_active_run()` | return `TaskRun` | reclaim → return `TaskRun` | return `None` |

The eviction column collapses to the "running elsewhere / not active here" outcome the caller would have observed anyway. No new error types, no new return shapes, no leaked "evicted" state for user code to branch on. Eviction is purely a framework-internal concern that produces WARNING logs and triggers local cleanup; the caller's contract is unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Handler authors never see recovery knobs (Priority: P1)

A developer wires a durable task with `@task` and calls `.run()` / `.start()`. They do not configure any recovery timeout. If their handler is interrupted (crash, deploy, OOM), the framework re-invokes it transparently with `ctx.entry_mode == "recovered"`. The developer's only recovery-related concern is reading `ctx.entry_mode` if they want to branch on it.

**Why this priority**: This is the API-surface promise the user reframed `stale_timeout` against ("framework's responsibility"). Without it, every subsequent layer is moot — we'd be back to leaking implementation knobs into handler authoring.

**Independent Test**: Author a handler. Verify `@task`, `Task.options()`, `TaskOptions.__slots__`, and `TaskContext` expose no `stale_timeout` / `_is_stale` / timeout-related fields. Inspect `__all__` in `durable/__init__.py`. Run the existing developer guide-doc-review meta-test and confirm no mention of `stale_timeout` survives.

**Acceptance Scenarios**:

1. **Given** a fresh `@task` definition, **When** the developer inspects the public API, **Then** no recovery timeout knob exists on the decorator, on `Task.options()`, on `TaskOptions`, or in `TaskContext`.
2. **Given** the developer reads `docs/durable-task-guide.md`, **When** they search for "stale_timeout", **Then** the term appears zero times. Recovery is described in one paragraph as "automatic, framework-managed; observable via `ctx.entry_mode`".

---

### User Story 2 - Split-brain orphan sandbox cannot duplicate execution (Priority: P1)

The platform mistakenly spawns two sandboxes (A and B) for the same session. The store accepts writes from A and rejects writes from B with `HTTP 409` + body `$.error.code == "binding_mismatch"`. Despite both sandboxes deriving the same `lease_owner`, the handler must execute exactly once (in A), and B's user-space callers must observe the exact same outcomes they would observe if the task were live in some other sandbox they don't control — never silently producing duplicate side effects.

**Why this priority**: Without this, every multi-sandbox event is a correctness incident — duplicate billing, duplicate model calls, duplicate user-visible writes. This is the highest-stakes failure mode and the one the platform explicitly built the `binding_mismatch` contract to prevent.

**Independent Test**: A provider stub configured to return `409 + binding_mismatch` for writes from one of two `TaskManager` instances pointed at the same session_id. Drive R-startup, Layer-2 scan, Layer-3 inline reclaim (`.run`/`.start`/`get_active_run`), `lease_renewal_loop`, and terminal write on the rejected side. Verify each path classifies the error as `evicted`, logs at WARNING, and does not retry. Verify the handler executes exactly once on the accepted side. Verify the caller-observable outcomes match the design-invariant table above.

**Acceptance Scenarios**:

1. **Given** orphan sandbox B with same `lease_owner` as active sandbox A, **When** B's `_recover_stale_tasks` attempts to reclaim an in_progress record, **Then** the PATCH receives `409 + binding_mismatch` and B skips that record with a WARNING log, never retries, never aborts the scan loop.
2. **Given** orphan sandbox B has an active handler local to it whose lease renewal PATCH receives `409 + binding_mismatch`, **When** the renewal loop next runs, **Then** the framework marks the local task evicted, cancels the local execution task, suppresses any terminal write, and surfaces the eviction to any awaiter as `TaskConflictError` (the same error type used for live-non-steerable conflict).
3. **Given** a caller invokes `.run(task_id)` or `.start(task_id)` on orphan sandbox B for an in_progress task, **When** B's inline reclaim PATCH is rejected with `409 + binding_mismatch`, **Then** the caller receives `TaskConflictError` — the exact same error type and shape they would receive if the task were live and non-steerable. No new "evicted" error type, no new error fields, no leaked split-brain state.
4. **Given** a caller invokes `.get_active_run(task_id)` on orphan sandbox B for an in_progress task, **When** B's inline reclaim PATCH is rejected with `409 + binding_mismatch`, **Then** the caller receives `None` — the exact same return value they would receive if the task were not active in their process. No exception is raised.
5. **Given** both sandboxes have run end-to-end and the test inspects the store, **Then** exactly one `completed`/`failed` terminal record exists, written by A.

---

### User Story 3 - Late-join consumers via `get_active_run` recover orphans automatically (Priority: P1)

A developer (typically a streaming HTTP handler servicing a "GET stream" request) calls `manager.get_active_run(task_id)` to attach to an in-flight task. Today this returns `None` if no in-memory entry exists — even if the store shows the task is `in_progress` with a dead lease (i.e., a same-process orphan). The new behavior: `get_active_run` consults the store, performs inline reclaim on a dead-lease record, and returns a usable `TaskRun` handle bound to the now-live recovered run. **The observable contract of `get_active_run` is unchanged from the caller's perspective** — it still returns a `TaskRun` when the task is live in this process and `None` when it isn't; the change is that "dead lease in the store" now resolves to "live in this process" instead of silently to `None`.

**Why this priority**: This is the gap that today produces the worst symptom — `None` silently returned to user code, which then says "task not active" when in reality it's stuck `in_progress` and recoverable. P1 because it's a silent correctness gap in an existing public method.

**Independent Test**: Create an in_progress record bypassing the manager (or simulate a lost lease_renewal_loop). Call `get_active_run(task_id)` on a fresh `TaskManager`. Verify it does NOT return `None` — instead it performs reclaim, returns a `TaskRun`, and the handler re-enters with `entry_mode == "recovered"`.

**Acceptance Scenarios**:

1. **Given** an in_progress record exists with a dead lease (instance_id from a prior process; or `lease_expires_at < now`), **When** user code calls `get_active_run(task_id)`, **Then** the framework inline-reclaims and returns a `TaskRun[Any]` handle. `entry_mode == "recovered"` is observable in the re-entered handler.
2. **Given** an in_progress record with a live lease held by THIS process, **When** `get_active_run(task_id)` is called, **Then** the existing in-memory handle is returned (unchanged from today).
3. **Given** a record in any terminal state, **When** `get_active_run(task_id)` is called, **Then** `None` is returned (unchanged from today).
4. **Given** orphan sandbox B (split-brain), **When** `get_active_run(task_id)` is called and the inline reclaim PATCH is rejected with `binding_mismatch`, **Then** `None` is returned — same return shape as "not active in this process". The eviction is logged at WARNING for operators; user code observes no special signal.

---

### User Story 4 - Inline reclaim on direct user activity (`.run` / `.start`) (Priority: P2)

When a caller invokes `.run()` or `.start()` on a `task_id` whose record is `in_progress` with a dead lease, the framework opportunistically performs an inline reclaim (PATCHes `lease_instance_id` to this process, re-enters the handler with `entry_mode="recovered"`) as a *hidden side effect*, then services the caller's request with exactly the same outcome that would have been observed if the task had been live in this process all along (see the design invariant table). The reclaim is invisible to the caller — they never see "reclaimed" as a distinct state, and the entry point's contract is unchanged.

**Why this priority**: P2 because Layer 2 (background scan) will catch the same orphans within ~5 minutes. Layer 3 on `.run`/`.start` is a responsiveness optimization — orphans recovered the instant traffic arrives instead of waiting up to a full scan interval.

**Independent Test**: Synthetically create an in_progress record with a dead lease (no lease_renewal alive). Call `.run(task_id, input)` and `.start(task_id, input)` on a manager that has NOT run its periodic scan. Verify (a) inline reclaim happens as a side effect (assert via internal hook or log capture), (b) the caller-observable outcome matches the design-invariant table exactly (same shape as the live-in-process case), (c) `entry_mode == "recovered"` is visible inside the handler but NOT exposed via the `.run`/`.start` return surface.

**Acceptance Scenarios**:

1. **Given** an in_progress record with dead lease, a steerable task, **When** `.run()` is called with new input, **Then** inline reclaim runs as a side effect, input is queued onto the recovered run, and `.run()` resolves with the recovered run's `TaskResult` — identical to the live-in-process steerable case.
2. **Given** an in_progress record with dead lease, a non-steerable task, **When** `.start()` is called, **Then** inline reclaim runs as a side effect and the call raises `TaskConflictError` carrying `current_status="in_progress"` — identical to the live-in-process non-steerable case.
3. **Given** two concurrent `.run()` calls landing on the same dead-lease record, **When** both attempt inline reclaim, **Then** ETag CAS produces exactly one winner; the loser re-reads and falls through to the live-lease branch (queue or conflict). No double-execution. Both callers see live-lease semantics.
4. **Given** an in_progress record with a live lease in this process, **When** `.run()`/`.start()` is called, **Then** NO reclaim is attempted (zero extra PATCHes); standard scheduling outcome only.
5. **Given** an in_progress record with a dead lease and the reclaim PATCH is rejected with `binding_mismatch`, **When** `.run()` or `.start()` is called (steerable OR non-steerable), **Then** the caller receives `TaskConflictError` — the same error type as live-non-steerable conflict. The eviction is logged WARNING for operators; no new error type, no new field on the exception.

---

### User Story 5 - Periodic background reclaim (Layer 2 safety net) (Priority: P2)

A long-lived foundry container accumulates same-process orphan tasks (handler crashed mid-run without writing terminal state; lease_renewal_loop died but the manager kept going). A background async task inside `TaskManager` runs every ~5 minutes, calls the same hardened `_recover_stale_tasks` logic, and reclaims any orphans bounded by the scan interval — even when no user-space code touches those task IDs.

**Why this priority**: P2 because R-startup (P3 below) catches cross-process orphans deterministically and Layer 3 catches same-process orphans on user traffic. Layer 2 is the "what about tasks nobody touches?" safety net. Important for containers that run for days; less critical for short-lived processes.

**Independent Test**: Spin up a `TaskManager` with an artificially short scan interval (test-only override). Synthesize an orphan in_progress record after startup. Wait for one scan cycle. Verify the orphan is reclaimed and `entry_mode == "recovered"` is observed without any `.run`/`.start`/`.get_active_run` call.

**Acceptance Scenarios**:

1. **Given** `TaskManager` is running, **When** a same-process orphan is synthesized after startup and the periodic scan fires, **Then** the orphan is reclaimed and re-entered as `entry_mode="recovered"` without any user-space callsite involvement.
2. **Given** the periodic scan finds a record owned by sibling sandbox A (split-brain), **When** B's scan attempts reclaim, **Then** the `binding_mismatch` response is classified as eviction and B logs/skips without retry.
3. **Given** `TaskManager.shutdown()` is called, **When** the shutdown completes, **Then** the periodic scan task is cancelled and does not survive the manager lifetime.

---

### User Story 6 - Hardened startup recovery (Priority: P3)

`TaskManager.startup()` calls `_recover_stale_tasks` which lists `in_progress` records owned by this session and re-claims them. The hardening: per-record `try/except` so one bad record doesn't abort the whole scan; bounded internal retries on transient provider errors (5xx, 429, timeouts); structured logging for every reclaimed, skipped, and failed record with reason.

**Why this priority**: P3 because the path already exists — this is a hardening pass, not a new capability. It's still required for production confidence (a single corrupt record shouldn't bring down recovery for an entire session).

**Independent Test**: Provider stub returning a mix of: success, 5xx-transient, 429-throttle, 409+binding_mismatch (eviction), 404 (vanished), and one entry whose record-shape parsing fails. Run `_recover_stale_tasks`. Verify successes are reclaimed, transients are retried with success, evictions are skipped+WARN-logged, vanished records are skipped+INFO-logged, parsing failures are skipped+ERROR-logged. The scan completes; no exception escapes.

**Acceptance Scenarios**:

1. **Given** a list of 10 in_progress records with mixed outcomes per the table above, **When** R-startup runs, **Then** all reclaimable records are reclaimed; non-reclaimable records are logged with reason; no exception propagates out of the scan.
2. **Given** a transient 5xx on a single record, **When** R-startup hits it, **Then** the framework retries up to N times with backoff before classifying it as failed-for-this-cycle and moving on.

---

### User Story 7 - Steering is plain multi-turn with a queue (Priority: P1)

A developer wires a steerable handler that uses `ctx.suspend(output=X)` between turns. A first caller invokes `.run(task_id, input=I1)` and a second caller invokes `.start(task_id, input=I2)` mid-flight (steering). The framework treats this as exactly equivalent to the plain multi-turn pattern where I1 is processed, the handler suspends with output X1, and I2 is processed next: caller-1's `TaskResult` is `status="suspended", output=X1` (whatever the handler emitted), and caller-2's `TaskResult` will be whatever turn-2's handler emits. Neither caller observes a "superseded" status because such a status is not a thing the framework can determine. If the handler chose to ignore `ctx.cancel` and finish turn-1 by returning a value (or raising), the task is terminal; caller-1 sees the normal completed/failed outcome, and caller-2's queued input is rejected with `TaskConflictError` (because the task is now terminal — no different from `.start()`ing a terminal task).

**Why this priority**: P1 because today the steering path synthesizes a public `superseded` status, drops handler-emitted output on the floor in the suspend+queued case, and maintains a parallel future-tracking abstraction (`_pending_steering_futures`) that has no counterpart in the multi-turn mental model. Every one of these is a public-surface defect on an unshipped contract, and each cascades into developer confusion if not fixed before release.

**Independent Test**: Parametrize handler turn-1 across `(suspend(output=X), suspend(output=None), return V, raise E)` × caller-2 timing across `(steer-while-running, no-steer)`. Drive each combination and assert: caller-1's `TaskResult` exactly matches plain multi-turn (no `superseded` ever observed; emitted output never replaced with `None`); caller-2's `TaskResult` matches "first turn of a fresh-or-suspended task" when the handler suspended, and matches `TaskConflictError` when the handler returned or raised; the in-memory `_pending_steering_futures` attribute does not exist.

**Acceptance Scenarios**:

1. **Given** a steerable handler whose turn-1 calls `await ctx.suspend(output="checkpoint A")`, **When** caller-2 has previously called `.start(task_id, input=I2)` mid-flight, **Then** caller-1's `TaskResult` is `status="suspended", output="checkpoint A"` (the handler's emitted output is delivered untouched; no "superseded" label, no output replacement). The framework then re-enters the handler with `I2` as turn-2, with `ctx.entry_mode == "resumed"` and `ctx.was_steered == True`. Caller-2's `TaskResult` reflects whatever turn-2 emits.
2. **Given** a steerable handler whose turn-1 calls `return "final"` (handler chose to ignore `ctx.cancel`), **When** caller-2 has previously called `.start(task_id, input=I2)` mid-flight, **Then** caller-1's `TaskResult` is `status="completed", output="final"`. The task is terminal. Caller-2's `TaskResult` future raises `TaskConflictError` with `current_status="completed"` — the SAME exception type and shape they would receive from a fresh `.start()` against an already-terminal task.
3. **Given** a steerable handler whose turn-1 raises `RuntimeError("boom")`, **When** caller-2 has previously called `.start(task_id, input=I2)` mid-flight, **Then** caller-1's `TaskResult` propagates `RuntimeError("boom")` (the normal error path). The task is terminal. Caller-2's `TaskResult` future raises `TaskConflictError` with `current_status="failed"`.
4. **Given** the public type `TaskResult`, **When** the developer inspects its `status` Literal, **Then** the only values are `"completed" | "suspended"`. `"superseded"` does not appear in the Literal, the `is_superseded` property does not exist, and no docstring or guide references it.
5. **Given** the implementation of `TaskManager`, **When** the developer inspects the instance attributes, **Then** no `_pending_steering_futures` attribute exists. The steerer's `TaskRun.result()` future is bound to the next turn's handler-invocation result future via the same mechanism that binds the first turn's caller — there is no parallel queue.
6. **Given** a handler in turn-2 whose `ctx.suspend(output=X)` runs and there is NO further queued input, **When** the suspend persists, **Then** caller-2's `TaskResult` is `status="suspended", output=X`. No drain branch executes; behavior is identical to suspend on a non-steerable task.

---

### User Story 8 - Task API on `azure.core` pipeline (Priority: P2)

The framework operator (Foundry platform engineer) and the SDK author (us) need the task-store transport to deliver the same operational guarantees as every other Azure SDK client: bounded retry on transient failures with exponential backoff, correlation headers on every request, distributed-tracing spans hooked into the OpenTelemetry exporter the host process is configured with, structured request/response logging with header allow-listing, a stable `User-Agent` moniker, and a single uniform error-classification seam (per FR-013) instead of ad-hoc `raise_for_status` calls. Today `HostedTaskProvider` is a raw `httpx.AsyncClient` with no policy chain, so each of these is either missing or implemented inconsistently across call sites. The migration to `azure.core.AsyncPipelineClient` consolidates the transport behavior to match the responses-storage path, while explicitly carrying forward the responses-storage gzip lesson: `ContentDecodePolicy` MUST be excluded.

**Why this priority**: P2 — not a correctness gap on its own (the current httpx path does work end-to-end), but it is a *prerequisite* for FR-013 / FR-014 / FR-016 / FR-017 (the eviction classifier and local-cleanup sequence) and for the retry behavior FR-006 implicitly assumes. Implementing those FRs cleanly on raw httpx would mean re-inventing the policy machinery we already have in `azure.core`. P2 because no caller-visible API changes — the migration is internal — but it must land before or alongside the eviction work to avoid wasted intermediate scaffolding.

**Independent Test**: A fake `AsyncHttpTransport` injected into the pipeline serves canned responses for each task verb (POST /tasks, GET, PATCH, DELETE, list pagination). Drive the public `TaskProvider` protocol methods through `HostedTaskProvider`. Verify: each request carries `User-Agent`, `x-ms-client-request-id`, and an `Authorization: Bearer` header; a 5xx response triggers `AsyncRetryPolicy` retries; a 409 with `$.error.code == "binding_mismatch"` returns `"evicted"` from the classifier and is NOT retried; a gzip-encoded response body is consumed correctly by the call-site serializers without triggering a `ContentDecodePolicy` (because there isn't one); a 200 with a non-JSON body raises a classified transport error, not a buried middleware crash.

**Acceptance Scenarios**:

1. **Given** the `HostedTaskProvider` initialization path, **When** the developer inspects the pipeline policies, **Then** the chain MUST include `RequestIdPolicy`, `HeadersPolicy`, `UserAgentPolicy` (sdk_moniker `ai-agentserver-core/{VERSION}`), `AsyncRetryPolicy`, `AsyncBearerTokenCredentialPolicy(credential, "https://ai.azure.com/.default")`, a task-API logging policy, and `DistributedTracingPolicy`. The chain MUST NOT include `ContentDecodePolicy`.
2. **Given** a fake transport returning HTTP 503 on the first attempt and 200 on the retry, **When** `HostedTaskProvider.get(task_id)` is called, **Then** the call succeeds after one retry. The number of attempted requests observed by the transport is exactly 2.
3. **Given** a fake transport returning HTTP 409 with body `{"error": {"code": "binding_mismatch", ...}}`, **When** any task verb writes to the store, **Then** `_classify_store_write_error` (per FR-013) returns `"evicted"`. The pipeline MUST NOT retry (the retry policy is configured to NOT retry on 409). The caller observes the FR-014/015 outcome appropriate to the call site.
4. **Given** a fake transport returning HTTP 200 with `Content-Encoding: gzip` and a valid gzipped JSON body, **When** `HostedTaskProvider.get(task_id)` is called, **Then** the result deserializes correctly. The pipeline transparently decompresses the body (default httpx-transport behavior) and the call-site serializer reads decompressed bytes. No middleware crash occurs because no `ContentDecodePolicy` is present.
5. **Given** a fake transport returning HTTP 200 with a non-JSON body (e.g., gateway HTML), **When** any verb that expects JSON is called, **Then** the call-site serializer raises a classified transport error (mapped to `"permanent"` per FR-013). The error MUST carry the response's body text (or a truncated prefix) in its message so operators can diagnose the misconfiguration.
6. **Given** the pipeline is set up, **When** OpenTelemetry is configured in the host process, **Then** `DistributedTracingPolicy` creates a span per request with status code and method recorded. (Smoke test only — verify the policy is present and not silenced; full tracing verification is out of scope.)
7. **Given** the `httpx` import in `azure/ai/agentserver/core/durable/_client.py`, **When** the migration lands, **Then** the import MUST be removed. If no other file under `azure/ai/agentserver/core/` imports `httpx`, the dependency MUST be removed from `pyproject.toml`'s install requires (note: `httpx` may still be a test-only dependency for transport-test fixtures — keep it under dev-dependencies in that case).

---

### User Story 9 - Cancel signal carries a reason; per-turn timeout budget (Priority: P2)

A handler author who wants to branch on *why* it was asked to wind down — e.g., "if I was steered, save partial work and let the next turn pick it up; if I timed out, log + raise" — needs `ctx.cancel.reason`. A steerable task whose handler suspends mid-turn after burning 25 seconds of a 30-second `@task(timeout=timedelta(seconds=30))` budget needs the steering-driven re-entry to get a *fresh* 30 seconds for the next turn — not the 5 seconds left over from generation 1's clock. And the watchdog's source-comment claim that an ignored timeout "will eventually [cause the lease to] expire and the task will be recovered" needs to go, because it is not true with the current cooperative-only design and we don't want to change that design.

**Why this priority**: P2 — none of these are correctness gaps in the sense that user-supplied data is lost (the metadata-flush gap covered by FR-024a is the actual correctness-bug ride-along). But they are mental-model gaps that surface as wrong handler behavior under steering + timeout combinations, and at least one (the shared-budget bug) actively prevents handler authors from reasoning correctly about per-turn deadlines. Mechanically small to fix, mostly internal, but each gets a public-surface touch (`ctx.cancel.reason`) so it must be sequenced with the steering rewrite, not added as an afterthought.

**Independent Test**: Steerable handler that records `ctx.cancel.reason` at every checkpoint. Drive a 3-turn scenario where turn-1 is steered mid-flight (cancel reason `"steering"` observed), turn-2 runs to a `@task(timeout=timedelta(seconds=5))` deadline with no steering pressure (cancel reason `"timeout"` observed at ~5s from turn-2's start, NOT at "5s minus elapsed-in-turn-1"), turn-3 starts cleanly (`ctx.cancel.is_set() == False`, `ctx.cancel.reason == None`).

**Acceptance Scenarios**:

1. **Given** a steerable handler that records `ctx.cancel.reason` whenever `ctx.cancel.is_set()` becomes true, **When** a second input is queued via `.start()` mid-flight, **Then** the handler observes `ctx.cancel.reason == "steering"` at the next checkpoint.
2. **Given** a non-steerable `@task(timeout=timedelta(seconds=5))` handler, **When** 5 seconds elapse without the handler completing, **Then** the handler observes `ctx.cancel.is_set() == True` AND `ctx.cancel.reason == "timeout"`.
3. **Given** a steerable `@task(timeout=timedelta(seconds=5))` task whose turn-1 handler runs for 4 seconds before suspending (no steering), **When** turn-2 starts via a fresh `.run()`, **Then** turn-2's watchdog spawns afresh and `ctx.cancel` does NOT fire until ~5 seconds *after turn-2 begins*. Turn-2 gets the full configured timeout budget, not the residual.
4. **Given** a steerable `@task(timeout=timedelta(seconds=5))` task whose turn-1 burns 4 seconds and is then steered (drain re-enters generation 2 within the same `_execute_task` invocation), **When** generation 2's handler runs, **Then** generation 2's watchdog ALSO spawns afresh — `ctx.cancel` does NOT fire until ~5 seconds *after generation 2's drain re-entry*. Drain re-entry is "logically a new turn" per the FR-020..FR-024a framing, so it gets the full timeout budget.
5. **Given** the source of `_timeout_watchdog` in `_manager.py`, **When** a reviewer reads its docstring, **Then** the docstring accurately states that the watchdog is cooperative-only and that an ignoring handler will run until process death or explicit `terminate()`. The misleading claim about lease expiry MUST be removed. Operator-facing log message at watchdog firing MUST remain INFO-level, NOT WARNING — exceeding the timeout is the developer's responsibility to react to, not a framework-level alarm.
6. **Given** `ctx.cancel.set()` was called multiple times in succession (e.g., timeout fired immediately after steering set the signal), **When** the handler reads `ctx.cancel.reason`, **Then** it observes the FIRST reason ("first-reason-wins"). Subsequent `.set(reason=...)` calls after the event is already set are no-ops with respect to `.reason`.
7. **Given** existing handler code that uses `if ctx.cancel.is_set():` or `await ctx.cancel.wait()`, **When** the `CancelSignal` wrapper lands, **Then** that code MUST continue to compile and run unchanged. The new `.reason` property is purely additive.

---

### Edge Cases

- **Same-process orphan whose `lease_owner` matches mine and whose `lease_instance_id` matches my CURRENT instance**: this means the in-memory state was lost (manager restarted within the same process, an exotic case). Treat as live-lease but no in-memory entry: see User Story 3 acceptance for `get_active_run` — the framework must NOT consider this evicted, must NOT re-PATCH the lease_instance_id (it's already mine), should construct a new in-memory entry that re-enters the handler. Open question called out in §5.
- **Reclaim of a task whose execution was completed-but-not-persisted before the previous process died**: the next process re-enters the handler with `entry_mode="recovered"`; handler must be idempotent. This is the existing recovery contract (Spec 012), not changed by this spec.
- **Provider returns `429 Too Many Requests` during inline reclaim**: classified as `transient`. The Layer-3 caller path retries a small bounded number of times (≤2) before giving up; on giving up, falls back to the existing live-lease branch (which will treat the record as live since we couldn't prove otherwise) — caller may receive `TaskConflictError`. This is a degraded but safe outcome.
- **`lease_renewal_loop` receives a transient 5xx**: keep retrying per existing renewal policy. Only `binding_mismatch` (or a permanent classification) is treated as eviction.
- **Test environment without an asyncio event loop in shutdown**: the periodic scan task must be cancellable from `shutdown()` even if the loop is closing. Use the existing cancellation patterns from `lease_renewal_loop`.
- **Steering input queued, handler then terminates (return / raise) instead of suspending**: per US7 the task is terminal; the queued input is unservicable and the steerer's `TaskRun.result()` future raises `TaskConflictError` with the appropriate `current_status` (`"completed"` or `"failed"`). This is the same outcome the steerer would observe from a fresh `.start()` against an already-terminal task — no special "queue was orphaned" error type. The framework MUST drop the queued input from `_steering.pending_inputs` in the same store write that records the terminal transition (one write, one consistent state).
- **Steering input queued, handler suspends but the store rejects the suspend persist (etag conflict)**: existing recovery semantics apply — the suspend retry path reads the current record and decides. If the record turned terminal in the meantime, the suspend is abandoned (the same terminal-with-queue cleanup as above applies). If the record is still in_progress, the suspend persist retries.
- **Multiple steering inputs queued (caller-2 and caller-3 both `.start()` while turn-1 is running)**: the queue preserves FIFO order. Turn-1's caller observes their natural suspend/return outcome. If turn-1 suspended, turn-2 runs with caller-2's input; when it suspends, turn-3 runs with caller-3's input; etc. Plain multi-turn semantics extended over a queue. If turn-1 terminated (return/raise), ALL queued inputs (caller-2 AND caller-3) get `TaskConflictError` in the same store write.
- **`AsyncRetryPolicy` interaction with `_classify_store_write_error`**: the retry policy's default retry classification must be overridden so that 409 responses are NEVER retried (regardless of `binding_mismatch` body) — etag conflicts (`conflict` per FR-013) need a re-read-and-evaluate decision at the caller, and `binding_mismatch` (`evicted`) explicitly must not retry. The pipeline MUST retry on 5xx, 408, 429 (with `Retry-After` honor) only. Tests must include a 409 case to assert "exactly one request attempted".
- **`AsyncBearerTokenCredentialPolicy` token refresh during retry**: if a 401 is encountered, the bearer-token policy refreshes the token and the retry policy re-issues the request. This is `azure.core`'s default behavior; no additional spec work needed beyond confirming the policy is in the chain.
- **Body inspection on `httpx.Response` vs `azure.core.HttpResponse`**: existing `HostedTaskProvider` tests against `httpx.AsyncClient` will break when the transport is replaced. Migration must update the test fixtures (`tests/durable/conftest.py` or equivalents) to use an `azure.core` transport fake. Plan for a transitional period where both fixtures exist if necessary, but the final state is all-`azure.core`.
- **Watchdog respawn race (FR-032)**: when steering drain re-enters and a fresh watchdog is spawned for the new generation, the *previous* generation's watchdog (if still pending) MUST be cancelled atomically with the spawn — otherwise two watchdogs target the same `ctx.cancel` and the earlier one will fire prematurely. Implementation must hold the watchdog task handle in the closure that survives across iterations and cancel + recreate at each drain re-entry. The `_execute_task` outer `finally` block must also cancel whichever watchdog is current when the handler exits.
- **Watchdog respawn + retry (FR-032)**: retries within `_execute_task_loop` already share the watchdog (that is intentional per "retries don't get extra time"); steering-drain re-entry does NOT. The distinction is "the same logical turn retried" vs. "a new logical turn". The respawn site is exactly at the `continue` branch in `_try_drain_steering`'s caller, not at the retry `continue` branch.
- **`ctx.cancel.set()` called by the handler itself**: handlers MUST NOT call `ctx.cancel.set(...)` directly — it's framework-owned. If they need to signal cancellation of dependent work, they should use their own `asyncio.Event`. The public surface for `CancelSignal` MAY expose `set` for tooling needs, but the developer guide MUST document `ctx.cancel` as read-only-for-handlers.
- **Test environment without an asyncio event loop in shutdown** is the existing edge case from the recovery scope; the cancel-signal changes don't alter it. Watchdog cleanup happens in `_execute_task`'s `finally` block under the same cancellation patterns.

## Requirements *(mandatory)*

### Functional Requirements

**Removal of developer-facing recovery surface:**

- **FR-001**: The `@task` decorator MUST NOT accept a `stale_timeout` argument. Any caller passing it MUST receive a `TypeError` from the decorator factory.
- **FR-002**: `TaskOptions` MUST NOT define a `stale_timeout` slot. Any caller constructing `TaskOptions(stale_timeout=...)` MUST receive a `TypeError`.
- **FR-003**: `Task.options()` MUST NOT accept a `stale_timeout` keyword. Any caller passing it MUST receive a `TypeError`.
- **FR-004**: The function `_is_stale` (and any other timeout-heuristic helper) MUST be removed from `azure/ai/agentserver/core/durable/_decorator.py`. No code anywhere in the durable package MUST reference it after this spec lands.
- **FR-005**: `docs/durable-task-guide.md` §7 "Stale-task recovery and `stale_timeout`" subsection MUST be removed and replaced with a brief recovery paragraph that mentions only `ctx.entry_mode == "recovered"`. The word `stale_timeout` MUST appear zero times in any developer-facing doc, sample, README, or docstring.

**Internal recovery architecture (three layers):**

- **FR-006 (Layer 1 — Hardened R-startup):** `TaskManager._recover_stale_tasks` MUST iterate records with per-record `try/except` so a single failure does not abort the scan. It MUST retry transient provider errors (5xx, 429, network timeouts) up to N times (internal constant; default 3) with exponential backoff before classifying as failed-for-this-cycle. Every reclaim attempt MUST emit a structured log at INFO (success) or WARNING/ERROR (failure with reason).
- **FR-007 (Layer 2 — Periodic reclaim):** `TaskManager.startup()` MUST start a background async task that periodically calls `_recover_stale_tasks` with an interval of approximately 300 seconds (internal constant, not on the public surface). `TaskManager.shutdown()` MUST cancel this task cleanly.
- **FR-008 (Layer 3 — Inline reclaim on `.run` / `.start`):** `.run()` and `.start()` MUST, when arriving at a record with `status == "in_progress"`, check lease liveness. If the lease is dead (see FR-010), they MUST perform inline reclaim via `_reclaim_one(task_id)` as a *hidden side effect*. The caller-observable outcome MUST be IDENTICAL to the outcome these methods would produce against a live-in-this-process task (per the design-invariant table): steerable → queue input → resolve/return; non-steerable → `TaskConflictError`. The reclaim itself MUST NOT be exposed via the return type, raised exception type, or any public field.
- **FR-009 (Layer 3 — `get_active_run` parity):** `TaskManager.get_active_run(task_id)` MUST consult the provider for the record (not only in-memory state). If the record is `in_progress` with a dead lease, it MUST perform inline reclaim via `_reclaim_one(task_id)` as a *hidden side effect* and then return a `TaskRun` bound to the now-live recovered run — the same return shape as the live-in-this-process case. If the record is in any terminal state, it MUST return `None`. The reclaim itself MUST NOT be exposed via the return type or any public field. Eviction handling: see FR-015.

**Lease-liveness signal:**

- **FR-010**: The "lease is dead" determination MUST be derived from the record itself. A lease is considered dead when EITHER:
  - the stored `lease_instance_id` does not match THIS process's `_instance_id` AND is not in any other in-memory active-task tracking structure, OR
  - the stored `lease_expires_at < now` (UTC).
  These conditions are OR'd: any one being true means dead. A lease is live only if `lease_instance_id == self._instance_id` AND `lease_expires_at >= now` (or the record references a known active in-memory entry).

**Single reclaim helper:**

- **FR-011**: A private helper `TaskManager._reclaim_one(task_id) -> ReclaimOutcome` MUST be the single source of truth for "given a dead-lease in_progress record, claim it and re-enter the handler". It MUST be used by all three callers: R-startup (per record), Layer-2 periodic scan, and Layer-3 inline reclaim. `ReclaimOutcome` MUST encode at least: `Reclaimed` (CAS won, handler re-entered), `RaceLost` (CAS lost; record is now live elsewhere), `Evicted` (binding_mismatch), `TransientFailure` (will be retried by caller), `RecordTerminal` (terminal between read and PATCH; nothing to do), `NotFound` (404).
- **FR-012**: The CAS PATCH in `_reclaim_one` MUST use ETag conditional update (`If-Match`) so two concurrent claims produce exactly one winner. The losing side MUST receive `RaceLost` and re-read the record to decide its next step.

**Error classifier:**

- **FR-013**: A new internal classifier `_classify_store_write_error(response_or_exc) -> Literal["transient", "evicted", "conflict", "permanent"]` MUST be defined and used by every store-write site (reclaim, lease renewal, terminal write, input enqueue). Mapping rules:
  - `transient`: HTTP 5xx, asyncio/network timeouts, Cosmos `429` throttling.
  - `evicted`: HTTP `409` AND response body has `$.error.code == "binding_mismatch"`. Caller MUST stop, log WARNING, never retry.
  - `conflict`: HTTP `412` (Cosmos ETag mismatch); OR HTTP `409` with any other / absent error code body. Caller re-reads and re-evaluates; bounded RMW retry permitted.
  - `permanent`: HTTP `404`, `400`, or unrecognized 4xx without a known error code. Caller does not retry; escalates as bug/log at ERROR.
- **FR-014**: When `_classify_store_write_error` returns `evicted` for any path that touches a locally-running task (specifically `lease_renewal_loop` or terminal write), the framework MUST:
  (a) cancel the local execution task,
  (b) suppress any pending terminal write,
  (c) signal the awaiting `TaskRun` future (if any) with an eviction error (mapped to `TaskConflictError`),
  (d) log at WARNING with task_id, session_id, and the binding_mismatch correlation.
- **FR-015**: When `_classify_store_write_error` returns `evicted` during inline reclaim in `.run()`, `.start()`, or `get_active_run()`, the framework MUST map the eviction to the entry point's "task is running elsewhere / not active in this process" outcome — preserving the design invariant that callers never see a distinct eviction signal:
  - `.run()` and `.start()` (steerable OR non-steerable): raise `TaskConflictError` with `current_status="in_progress"`. This is the SAME exception type used for live-non-steerable conflict. No new error type, no new field on the exception. The fact that the conflict was due to eviction (vs. a live competing handler) MUST be visible only in operator logs (WARNING with `binding_mismatch` correlation), never on the exception surface.
  - `.get_active_run()`: return `None`. This matches the "task is not active in this process" return value the caller would observe for any other reason (terminal state, never started). The eviction MUST be visible only in operator logs (WARNING with `binding_mismatch` correlation), never on the return value.

**Eviction-driven local cleanup:**

- **FR-016**: The `lease_renewal_loop` MUST inspect every PATCH response via `_classify_store_write_error`. On `evicted`, it MUST trigger the local-cleanup sequence in FR-014 atomically (cancel + suppress + signal + log) and exit the renewal loop without further PATCH attempts.
- **FR-017**: The terminal-write path in `TaskManager` MUST inspect its PATCH response via `_classify_store_write_error`. On `evicted`, it MUST discard the local result without surfacing it to the store and log per FR-014.

**Test-only hooks (no public surface impact):**

- **FR-018**: A test-only async helper `TaskManager._force_reclaim_orphans()` MAY be added (private, `_`-prefixed) so unit tests can drive Layer-2 deterministically without waiting for the 300s interval. If added, it MUST NOT appear in `__all__` and MUST be documented as test-only.
- **FR-019**: An internal constant `_PERIODIC_RECLAIM_INTERVAL_SECONDS` MAY be importable for tests to monkeypatch a shorter interval. Production code MUST NOT expose this on any public type or function signature.

**Steering surface collapse (steering is plain multi-turn):**

- **FR-020 (remove `superseded` from the public surface)**: `TaskResult.status` MUST be the Literal `"completed" | "suspended"` only. The value `"superseded"` MUST NOT appear in the Literal, in any docstring, or in any developer-facing guide / sample / README. The property `TaskResult.is_superseded` MUST NOT exist. No code path in the framework MUST set `status="superseded"` on a `TaskResult` returned to user code.
- **FR-021 (suspend path delivers handler output AND flushes metadata at the turn boundary)**: When a handler returns `Suspended(output=X, reason=R)`, the current turn's caller's `TaskResult` MUST be exactly `TaskResult(task_id=..., status="suspended", output=X, suspension_reason=R)`. This MUST hold whether or not a steering input is queued at the moment the suspend resolves. The framework MUST NOT race a drain ahead of the suspend resolution; the steps at the suspend boundary MUST execute in this exact order: (1) `await ctx.metadata.flush_all()` to persist the current turn's namespace snapshots — IDENTICAL to the non-steering suspend path at `_manager.py:1179`; (2) persist the suspend record (including the `Suspended` envelope and the metadata snapshot) via `_handle_suspend`; (3) resolve the current turn's `result_future`. Only after all three complete may `_try_drain_steering` re-enter the handler for the queued input. The pre-rework code path that skips both the flush AND the suspend persistence when a drain is pending (`_manager.py:1156-1175`) MUST be replaced — that path causes silent loss of the turn's unflushed metadata writes on process crash.
- **FR-022 (return / raise paths are terminal AND flush metadata before terminal write)**: When a handler `return`s a value `V`, the steps at the completion boundary MUST execute in this exact order: (1) `await ctx.metadata.flush_all()` to persist the terminal turn's namespace snapshots — IDENTICAL to the non-steering completion path at `_manager.py:1227`; (2) persist the terminal record via `_handle_success` (the SAME store write MUST also clear `_steering.pending_inputs` if non-empty — single write, single consistent state); (3) resolve the current turn's `result_future` with `TaskResult(status="completed", output=V)`; (4) for every queued steerer whose future was awaiting the next turn, resolve their `TaskRun.result()` future with `TaskConflictError(current_status="completed")` — the exact same exception type and shape a fresh `.start()` against an already-terminal task would raise. When a handler raises, the same ordering applies with `_handle_failure` instead of `_handle_success` and `current_status="failed"` for queued steerers. The pre-rework code path that skips the flush AND the terminal write when a drain is pending (`_manager.py:1197-1223`) MUST be replaced — that path causes silent loss of the terminal turn's unflushed metadata writes on process crash. No new error type for "queue orphaned by terminal".
- **FR-023 (delete `_pending_steering_futures`)**: The parallel `_pending_steering_futures: dict[str, list[asyncio.Future]]` attribute on `TaskManager` MUST be removed. The steerer's `TaskRun.result()` future MUST be bound to the active result future for the next turn via the same mechanism that binds the first turn's caller — there is exactly one "current generation's result future" per task at any time, and `.start()` on a running steerable task registers the steerer as the awaiter of the next generation's result future (the one created when the drain re-enters the handler loop). The signature of `_try_drain_steering` MUST NOT take a `partial_output` parameter (because the suspend / complete path now owns delivery of the current turn's output — see FR-021).
- **FR-024 (`_try_drain_steering` is re-entry only)**: After FR-021 / FR-022 / FR-023, the sole responsibility of `_try_drain_steering` MUST be: (a) read `_steering.pending_inputs`; (b) if empty, return None (no-op); (c) if non-empty, pop the head input, advance `_steering.generation`, persist the steering-state mutation with CAS, bind a fresh result future for the new generation (the one already held by the next steerer in line, if any, else a brand-new future), and return a new `TaskContext` for the next handler invocation. The function MUST NOT resolve any caller-visible future as part of this work (caller-1's future was already resolved by the suspend path; caller-2's future is what the new generation's result future IS). The function MUST NOT touch `ctx.metadata` in any way — flush ownership belongs to the FR-021 / FR-022 boundary; the new generation's context simply inherits a fresh (post-flush, post-snapshot) metadata view from the just-persisted record, not the in-memory buffer of the prior turn.
- **FR-024a (metadata auto-flush invariant — load-bearing)**: For *every* terminal-of-turn boundary, regardless of code path (steerable or not, drain pending or not, fresh / resumed / recovered entry mode), `await ctx.metadata.flush_all()` MUST execute before the framework writes the terminal/suspend record AND before the caller's `result_future` is resolved. The exhaustive list of boundaries (covering today's `_execute_task_loop`):
  1. Normal suspend (`_manager.py:1179`) — already correct.
  2. Normal completion (`_manager.py:1227`) — already correct.
  3. `asyncio.CancelledError` — cooperative cancel or `terminate()` (`_manager.py:1268`) — already correct.
  4. Unhandled exception, retries exhausted (`_manager.py:1333`) — already correct.
  5. **Suspend with queued steering input (currently `_manager.py:1156-1175`) — MUST be added** per FR-021.
  6. **Return with queued steering input (currently `_manager.py:1197-1223`) — MUST be added** per FR-022.
  After this spec lands, the developer-guide claim in `durable-task-guide.md` (§4 "Metadata as a callable namespace facade", §5 "What the framework persists at lifecycle boundaries") that "writes you forget to explicitly flush are still durable across a graceful boundary" MUST hold for every steerable-task code path, not just the non-steering ones. A test (see SC-014) MUST assert this for all six boundaries above.

**Task API transport on `azure.core` pipeline:**

- **FR-025 (replace `httpx.AsyncClient` with `AsyncPipelineClient`)**: `HostedTaskProvider.__init__` MUST construct `self._client` as `azure.core.AsyncPipelineClient(base_url=..., policies=[...])`. The direct `httpx.AsyncClient` instance MUST be removed. `_get_headers()` (current bearer-token assembly) MUST be removed — the credential is supplied via `AsyncBearerTokenCredentialPolicy` and no per-request token assembly is needed at the call sites. Every `await self._client.<method>(...)` call site MUST be migrated to construct an `azure.core.rest.HttpRequest` and send it via `self._client.send_request(request)`.
- **FR-026 (policy chain composition)**: The pipeline MUST be composed of, in order: `policies.RequestIdPolicy()`, `policies.HeadersPolicy()`, `policies.UserAgentPolicy(sdk_moniker=f"ai-agentserver-core/{VERSION}")`, `policies.AsyncRetryPolicy(retry_on_status_codes=[408, 429, 500, 502, 503, 504], retry_total=3)` (or equivalent constructor — the constraint is: retry on 5xx + 408 + 429, do NOT retry on 409 or 4xx generally), `policies.AsyncBearerTokenCredentialPolicy(credential, "https://ai.azure.com/.default")`, a task-API logging policy (see FR-027), and `policies.DistributedTracingPolicy()`. The chain MUST NOT include `policies.ContentDecodePolicy()` — call-site serializers consume the response body directly with defensive error handling.
- **FR-027 (task-API logging policy)**: A logging policy MUST be defined for the task API (either as a new `_task_api_logging_policy.py` module modeled after `_foundry_logging_policy.py` in the responses package, or by reusing `policies.HttpLoggingPolicy` with an explicit header allow-list). The allow-list MUST include `x-ms-client-request-id`, `x-ms-request-id`, `etag`, `if-match`, `retry-after`, and the standard Azure operational headers. It MUST NOT log `Authorization` headers or request/response bodies at any level above DEBUG.
- **FR-028 (`_classify_store_write_error` integration)**: Every status-bearing call site in `HostedTaskProvider` MUST replace `response.raise_for_status()` with explicit status inspection that funnels through `_classify_store_write_error` (FR-013). The function MUST accept an `azure.core.rest.HttpResponse` (or the exception wrapping it) and MUST be tolerant of: (a) non-JSON response bodies (returns `"conflict"` for an unparseable 409, NOT `"evicted"` — `evicted` requires the body to parse AND contain `$.error.code == "binding_mismatch"`); (b) empty bodies; (c) bodies that decode but lack the `$.error` envelope (returns `"conflict"` or `"permanent"` per status). The 404 → `None` (for `get`) and 404 → `TaskNotFound` (for `update`, `delete`) branches MUST be preserved by mapping `"permanent"` with a 404 status to the appropriate per-verb outcome.
- **FR-029 (call-site body parsing is defensive)**: Every call-site `http_response.text()` or `.json()` access MUST be wrapped to catch `UnicodeDecodeError`, `json.JSONDecodeError`, and `azure.core.exceptions.DecodeError`. On failure, the call site MUST surface a classified transport error (mapped to `"permanent"`) carrying the response status, `x-ms-request-id` (if present), and a truncated body prefix for operator diagnostics. This is the carry-forward of the responses-storage `ContentDecodePolicy` removal lesson: parsing happens at the call site, never in middleware.
- **FR-030 (`httpx` dependency removal)**: After FR-025 lands, `import httpx` MUST NOT appear anywhere under `azure/ai/agentserver/core/durable/`. If a grep of `azure-ai-agentserver-core/azure/` for `httpx` returns zero matches after the migration, `httpx` MUST be removed from `pyproject.toml`'s `install_requires` (it MAY remain as a dev-dependency for legacy transport-test fixtures during the migration's transitional period, but the production runtime MUST NOT pull it in).

**Cancel signal with reason; per-turn timeout budget:**

- **FR-031 (`CancelSignal` wraps `ctx.cancel` with a reason)**: `ctx.cancel` MUST become a `CancelSignal` instance, a small wrapper class that preserves the existing `asyncio.Event`-shaped API (`is_set() -> bool`, `wait() -> Awaitable[None]`) and adds a `.reason: Literal["timeout", "steering"] | None` property. The class MUST be defined alongside `TaskContext` in the durable public surface (importable from `azure.ai.agentserver.core.durable`). Backward-compatible: existing handler code using `if ctx.cancel.is_set():` and `await ctx.cancel.wait()` MUST continue to work unchanged. The `.set(reason=...)` method MUST follow first-reason-wins semantics — if the signal is already set, subsequent `.set()` calls are no-ops with respect to both the event state and the recorded reason. Implementation choice between composition (wrap `asyncio.Event`) vs. inheritance is left to the plan phase; composition is recommended to avoid CPython-internal coupling.
- **FR-032 (per-turn watchdog respawn)**: The timeout watchdog MUST be (re-)spawned at the start of every logical turn, where "logical turn" means: (a) every fresh handler invocation entering `_execute_task` (already the case today via `create_and_start` / `_start_existing_task`); AND (b) **every drain-driven re-entry inside `_execute_task_loop`** (NOT today — currently the watchdog is spawned once outside the loop at `_manager.py:1074-1082`). When a drain re-enters via `_try_drain_steering`, the framework MUST cancel the previous generation's watchdog and spawn a new one with the full `opts.timeout.total_seconds()` budget. Retry re-iterations within the same generation share the original watchdog (per the existing "retries don't get extra time" semantics) — only steering-drain re-entry triggers a respawn. Implementation MUST keep at most one live watchdog task at a time; the cleanup `finally` block at `_manager.py:1097-1103` MUST cancel whichever watchdog is current.
- **FR-033 (set reason at the source)**: `_timeout_watchdog` MUST call `ctx.cancel.set(reason="timeout")` (not bare `ctx.cancel.set()`). `_try_drain_steering` MUST construct the new generation's context with a `CancelSignal` that — if `steering["cancel_requested"]` is true — is already in the `set(reason="steering")` state. (The existing site at `_manager.py:1485-1486` that conditionally calls `cancel_event.set()` MUST switch to `cancel_event.set(reason="steering")`.) The new generation thus enters its handler with the reason visible from the very first checkpoint, not at some race-dependent later moment.
- **FR-034 (watchdog docstring correctness)**: The docstring of `TaskManager._timeout_watchdog` at `_manager.py:1018-1021` MUST be rewritten. The current text *"If [the function] doesn't [check ctx.cancel and exit gracefully], the lease will eventually expire and the task will be recovered."* is **false** and MUST be removed. The replacement MUST state explicitly: (a) the watchdog is cooperative-only; it sets `ctx.cancel.set(reason="timeout")` and exits; (b) if the handler ignores `ctx.cancel`, the task continues to run; the lease keeps being renewed; the only ways to interrupt are (i) the handler eventually noticing and exiting, (ii) the process terminating, or (iii) an explicit `manager.terminate(task_id)` call. The watchdog-fired log message MUST stay at INFO level (NOT WARNING) — exceeding the timeout is a developer-handler concern, not a framework alarm. The developer guide MUST also be updated (per the Docs↔Samples Loop section) so the documented behavior of `timeout=` matches the (correct) implementation.

### Key Entities

- **`ReclaimOutcome`**: Discriminated outcome returned by `_reclaim_one`. Variants: `Reclaimed | RaceLost | Evicted | TransientFailure | RecordTerminal | NotFound`. Internal-only type; never appears on the public surface.
- **`_classify_store_write_error`**: Pure function taking either an exception or an HTTP-like response object and returning one of `"transient" | "evicted" | "conflict" | "permanent"`. Internal-only.
- **Periodic-reclaim async task**: A long-lived background task owned by `TaskManager`. Created in `startup()`, cancelled in `shutdown()`. Internal-only.
- **`CancelSignal`**: Public class on the `azure.ai.agentserver.core.durable` surface. Wraps an `asyncio.Event` and adds `reason: Literal["timeout", "steering"] | None`. Replaces the bare `asyncio.Event` previously assigned to `ctx.cancel`. `set(reason=...)` is first-reason-wins.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Searching the published `azure-ai-agentserver-core` package surface (every `__all__`, every public function signature, every public docstring) for the string `stale_timeout` returns zero matches.
- **SC-002**: In a split-brain simulation (two `TaskManager` instances, same session_id, provider stub returning `409 + binding_mismatch` for writes from one), the handler executes exactly once across both instances. Zero duplicate completed/failed terminal records in the store.
- **SC-003**: For an in_progress record with a dead lease, `get_active_run(task_id)` returns a usable `TaskRun` (not `None`) and the handler re-enters with `entry_mode == "recovered"`.
- **SC-004**: With the periodic interval set to 1 second (test override), a synthesized post-startup orphan is reclaimed within ≤ 2 seconds without any user-space `.run`/`.start`/`.get_active_run` call.
- **SC-005**: `_recover_stale_tasks` driven against a provider stub returning a mix of success, 5xx-transient, 429, 409+binding_mismatch, 404, and parse-error responses completes without raising; every record is logged with a classification reason.
- **SC-006**: `pytest azure-ai-agentserver-core/tests/durable/test_contract_completeness.py` is green after the changes.
- **SC-007**: After this spec lands, no test in the durable package references `stale_timeout` (the previous decorator surface is rewired to use the test-only hooks in FR-018/FR-019).
- **SC-008**: The developer guide doc-review meta-test (per FR-025 in Spec 015) passes against the updated `durable-task-guide.md`.
- **SC-009 (design invariant)**: A parametrized test sweeps `(.run | .start | get_active_run)` × `(steerable | non-steerable)` × `(live-mine | dead-reclaimable | dead-evicted)` and asserts the observable return/raise matches the design-invariant table exactly. The eviction column produces the SAME `TaskConflictError` (for `.run`/`.start`) or the SAME `None` (for `get_active_run`) as the corresponding "task is live elsewhere / not active here" case — distinguishable only by WARNING log records, not by any caller-visible field.
- **SC-010 (steering surface)**: Searching the `azure-ai-agentserver-core` package surface for the string `superseded` returns zero matches. Searching for `is_superseded` returns zero matches. Searching for `_pending_steering_futures` returns zero matches. `TaskResult.status.__args__` equals `("completed", "suspended")`.
- **SC-011 (steering is multi-turn)**: A parametrized test sweeps `(handler turn-1 ends with: suspend(output=X), suspend(output=None), return V, raise E)` × `(steerer queued mid-flight: yes, no)`. For every cell, caller-1's `TaskResult` is identical to the corresponding cell in plain multi-turn (no `superseded` ever observed; emitted output never replaced). For the `(terminal, steerer queued)` cells, the steerer's `TaskRun.result()` raises `TaskConflictError` with the appropriate `current_status`. For the `(suspend, steerer queued)` cells, the steerer's `TaskRun.result()` resolves with whatever turn-2 emits, exactly as if turn-2 had been kicked off by a post-suspend `.start()`.
- **SC-012 (transport migration completeness)**: `grep -r 'import httpx' azure-ai-agentserver-core/azure/ai/agentserver/core/` returns zero matches. `grep -r 'AsyncPipelineClient' azure-ai-agentserver-core/azure/ai/agentserver/core/durable/_client.py` returns at least one match. The pipeline policy chain enumerated in FR-026 is asserted by an introspection test that inspects `HostedTaskProvider._client._pipeline._impl_policies` (or the public equivalent) and verifies presence + ordering + absence-of-`ContentDecodePolicy`.
- **SC-013 (transport behavior)**: A fake `AsyncHttpTransport` injected into the pipeline verifies (a) automatic retry on 503 (exactly 2 requests observed for a one-retry-success); (b) NO retry on 409 regardless of body (exactly 1 request observed); (c) `Authorization: Bearer <token>` header on every request; (d) `User-Agent: ai-agentserver-core/<VERSION>` on every request; (e) `x-ms-client-request-id` populated on every request; (f) gzipped response body decoded correctly end-to-end with no `ContentDecodePolicy` in the chain; (g) non-JSON 200 body raises a classified transport error carrying the response status and a truncated body prefix.
- **SC-014 (metadata auto-flush invariant)**: A parametrized test sweeps the six lifecycle boundaries enumerated in FR-024a: `(normal-suspend, normal-complete, cooperative-cancel, terminate, unhandled-exception, suspend-with-queued-steering, return-with-queued-steering, raise-with-queued-steering)`. For each cell, the handler writes a marker (`ctx.metadata["marker"] = "set_in_turn_N"`) WITHOUT calling `flush()` explicitly, then triggers the boundary. The test asserts that on a subsequent fresh load of the task record from the provider (simulating a crash and re-read), the marker is present. The current code passes the first four cells and fails the last four; after FR-021 / FR-022 / FR-024a land, all eight MUST pass.
- **SC-015 (per-turn timeout budget)**: A test runs a steerable `@task(timeout=timedelta(seconds=2))` handler whose turn-1 sleeps 1.5s, then suspends. Asserts: turn-1 completes without `ctx.cancel` firing. The test then either (a) calls `.run()` for a fresh turn-2 OR (b) calls `.start()` mid-flight to trigger a drain. In both cases, turn-2's handler observes `ctx.cancel.is_set() == False` at start and the cancel does NOT fire until ~2s after turn-2's *own* start. The "shared budget" bug is detected by a regression assertion that turn-2's effective timeout is NOT `2 - elapsed_in_turn_1`.
- **SC-016 (cancel reason visibility)**: A test sweeps three scenarios: (a) non-steerable `@task(timeout=timedelta(seconds=1))` handler that sleeps past the deadline → asserts `ctx.cancel.reason == "timeout"` at the next checkpoint. (b) Steerable handler steered mid-flight by `.start()` → asserts `ctx.cancel.reason == "steering"` at the next checkpoint. (c) Steerable + timeout handler whose timeout fires WHILE a steering input is also queued → asserts the reason observed is whichever fired FIRST (deterministic first-reason-wins semantics). Existing handler code patterns `if ctx.cancel.is_set():` and `await ctx.cancel.wait()` MUST continue to pass without modification.

## Assumptions

- The platform's task-store API contract is fixed: orphan-sandbox writes are rejected with exactly `HTTP 409` and response body `$.error.code == "binding_mismatch"`. If the platform later uses a different status or body shape, FR-013 must be updated and the classifier re-targeted (but the architectural design is unchanged).
- Cosmos DB ETag CAS via `If-Match` is available on the task store and used by the provider adapter for the PATCH operations involved in `_reclaim_one`, `lease_renewal_loop`, and terminal writes. If any adapter currently issues unconditional PATCHes, that adapter is in scope to fix.
- Reads against the task store are not rejected for orphan sandboxes; only writes are. (The framework needs to read records even from the orphan sandbox to make the eviction determination.)
- The current `_active_tasks` in-memory tracker on `TaskManager` is the authoritative source for "which tasks are live in THIS process". The Layer-3 lease-liveness check uses this in combination with the stored `lease_instance_id` per FR-010.
- A single `TaskManager` process serves a single `session_id` (foundry one-process-per-session model). Multi-session-per-process is not a target of this spec.

## Docs ↔ Samples Loop *(mandatory IF this spec touches developer-facing guides or samples)*

### Authoritative guides

- `sdk/agentserver/azure-ai-agentserver-core/docs/durable-task-guide.md` — owns the recovery mental model and the developer-visible contract. After this spec, the only recovery-related content is: a paragraph stating that recovery is automatic and observable via `ctx.entry_mode == "recovered"`. No knobs, no timeouts, no implementation discussion.

### Authoring sequence

1. **Update `durable-task-guide.md` first.** Remove §7 "Stale-task recovery and `stale_timeout`" subsection. Replace with a one-paragraph statement in the existing recovery section. Remove any mention of `stale_timeout` from the `@task` option table.
2. **Mechanically derive sample test setup.** Tests in `tests/durable/` that synthesize in_progress records to exercise recovery should follow the guide: they observe `ctx.entry_mode == "recovered"` and never reference any timeout knob.
3. **If a test needs to express something the guide doesn't describe, the guide is wrong.** In particular, if any test needs to set a "fake stale timeout" to make recovery trigger, the test setup must change to use `_force_reclaim_orphans()` (test-only hook, FR-018) or the periodic-interval override (FR-019) — not a developer-facing API.
4. **Update CHANGELOG** entry for 2.0.0b4 (the in-development pre-release section) to drop the just-added "stale_timeout is now decorator-level" bullet and reflect the new shape: "`stale_timeout` removed; recovery is fully automatic". This is an in-place edit of an unreleased section, not a versioned change-note — the durable-task primitive has not shipped, so the bullet is being rewritten, not deprecated.

### Loop completion criterion

- A developer reading only `durable-task-guide.md` can correctly understand: (a) they never configure recovery, (b) `ctx.entry_mode == "recovered"` is the only signal they need to handle for idempotency, (c) split-brain eviction is invisible to them — if they get `TaskConflictError`, treating it as ownership conflict is correct.
- The doc-review meta-test passes.
- No test in `tests/durable/` sets `stale_timeout=` or references the `_is_stale` symbol.

### What goes where

| Knowledge | Lives in |
|---|---|
| Recovery is automatic; `ctx.entry_mode == "recovered"` is the only handler-author concern | `durable-task-guide.md` (Recovery section) |
| `TaskConflictError` is the single error type for any "task is busy / not available to this caller" state (live-non-steerable, dead+evicted, terminal). Don't branch on cause. | `durable-task-guide.md` (Errors section) |
| Three-layer recovery architecture, classifier semantics, ReclaimOutcome shape, periodic interval | Internal — module docstrings + this spec only. NOT in the developer guide. |
| `binding_mismatch` protocol contract | Internal — `_classify_store_write_error` docstring + this spec only. |
| Split-brain test fixture (provider stub returning binding_mismatch) | `tests/durable/conftest.py` (or test module). Documented inline. |
| Steering = plain multi-turn + a queue (no `superseded` status, no parallel future array). Handler decides what to do with `ctx.cancel`; framework never claims to know if the handler honored it. The metadata auto-flush invariant (FR-024a) holds at *every* terminal-of-turn boundary, drain or no drain. | `durable-task-guide.md` (Steering section, rewritten per FR-020..FR-024a) |
| Terminal-with-queued-input outcome (`TaskConflictError` to every queued steerer, same shape as terminal `.start()`) | `durable-task-guide.md` (Errors section) — one sentence under `TaskConflictError`. |
| `HostedTaskProvider` is built on `azure.core.AsyncPipelineClient` (FR-025..FR-030). Internal-only — no developer-facing surface. | Module docstring + this spec only. NOT in the developer guide. |
| `ContentDecodePolicy` MUST never be added to the task pipeline (responses-storage gzip lesson, FR-029 carry-forward). | Inline comment at the pipeline-construction site + this spec only. |
| `ctx.cancel` is a `CancelSignal` with `.reason` (`"timeout"` / `"steering"` / `None`). Handlers MAY branch on `.reason` to decide strategy. `is_set()` and `wait()` work as before — pure additive change. | `durable-task-guide.md` (Steering section: cancel-reason mention + branching example; §5 Reference: `CancelSignal` entry). |
| Per-turn timeout budget: every logical turn (including drain re-entry) gets a fresh `opts.timeout` window. Retries inside the same generation share the original watchdog. | `durable-task-guide.md` (Timeout subsection in §5 or new subsection in §4 if missing). |
| Watchdog is cooperative-only — handler must check `ctx.cancel`; if ignored, task runs until process death or `terminate()`. | `durable-task-guide.md` (Timeout subsection) + corrected source docstring at `_manager.py:_timeout_watchdog`. |

## Durability Contract Conformance *(mandatory IF this spec touches code in the durability surface)*

### Exit checklist (Constitution Principle X)

- [ ] **Contract change?** This spec changes recovery behavior but does NOT change the row × path matrix in `sdk/agentserver/specs/durability-contract.md` — the matrix is about what gets persisted under crash and how the response stream behaves. Recovery is a separate axis. **Decision needed:** add a "Recovery" subsection to the contract doc covering the binding_mismatch protocol and the (lease-state × steerable) callsite outcome table from §6 of the analysis doc? Recommend YES.
- [ ] **Affected rows / paths?** Strictly speaking, none of the existing rows. But the matrix should gain a new "Lease eviction (binding_mismatch)" cross-cutting note that applies to every row: if eviction is detected mid-handler, the local execution is cancelled, no terminal record is written from this process, and the awaiting future fails with `TaskConflictError`. **Action: amend the contract doc with a change-log entry covering this in the same PR as the implementation.**
- [ ] **Conformance tests added?** New test module `tests/durable/test_split_brain_eviction.py` covering FR-013 through FR-017. Parametrize across the entry points (`.run`, `.start`, `.get_active_run`, `lease_renewal_loop`, terminal write). No row/path parametrization needed since this is cross-cutting.
- [ ] **TDD ordering verified?** Tests land RED before implementation lands GREEN. Commits ordered accordingly.
- [ ] **No synthetic-crash shortcuts?** Use the real provider stub to return `409 + binding_mismatch`; do not monkey-patch the classifier or fabricate `Evicted` outcomes.
- [ ] **Completeness meta-test still passes?** `pytest tests/e2e/durability_contract/test_contract_completeness.py` green after changes.
- [ ] **Dev guide / handler guide updated?** Per the Docs ↔ Samples Loop section above.

## Core Durable-Task Primitive Conformance *(mandatory IF this spec touches the public surface of `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`)*

### Exit checklist (Constitution Principle XII)

- [ ] **Public-surface change?** YES. This spec removes `stale_timeout` from `@task`, `Task.options()`, `TaskOptions.__slots__`, the `@task` overload signatures, and any docstring references. Also changes the behavior of `TaskManager.get_active_run` from "in-memory lookup only" to "store query + inline reclaim on dead lease". Both are tracked in Principle XII scope. **Additionally (FR-020..FR-024a)**: `TaskResult.status` Literal narrows from `"completed" | "suspended" | "superseded"` to `"completed" | "suspended"`, the `TaskResult.is_superseded` property is removed, the `_pending_steering_futures` internal attribute is removed, `_try_drain_steering` loses its `partial_output` parameter, and the lifecycle-boundary `flush_all()` invariant is extended to cover the two steering-drain shortcuts that currently bypass it. The observable semantics of `.run()` / `.start()` on a steerable task with a queued input shift: the original caller now sees the natural suspend / completed / failed outcome (with the handler's emitted output preserved on suspend AND the turn's unflushed metadata writes durably persisted) rather than a synthetic `superseded` status with silently lost metadata; queued steerers whose turn never runs (because the handler terminated) now receive `TaskConflictError` instead of `superseded`. **Additionally (FR-031..FR-034)**: `TaskContext.cancel` changes type from `asyncio.Event` to the new public `CancelSignal` class (added to `__all__`), gaining a `.reason` property without breaking existing `is_set()`/`wait()` patterns; the timeout watchdog is respawned per logical turn (including drain re-entry) so each turn gets the full `opts.timeout` budget; the misleading `_timeout_watchdog` docstring about lease expiry is corrected.
- [ ] **Affected symbols enumerated?**
  - `@task` decorator: `stale_timeout` keyword removed from all overloads and the factory.
  - `Task.options()`: `stale_timeout` keyword removed.
  - `TaskOptions`: `stale_timeout` slot removed.
  - `_is_stale` (internal but referenced widely): removed.
  - `TaskManager.get_active_run(task_id)`: behavior change — now performs reclaim; signature unchanged.
  - `TaskResult.status`: Literal narrowed (remove `"superseded"`).
  - `TaskResult.is_superseded`: property removed.
  - `TaskManager._pending_steering_futures`: attribute removed.
  - `TaskManager._try_drain_steering`: `partial_output` keyword parameter removed; semantics narrowed to "re-entry only" per FR-024.
  - `HostedTaskProvider.__init__`: signature unchanged externally, but `credential` SHOULD be re-typed to `azure.core.credentials_async.AsyncTokenCredential` for proper typing (current `Any` was a side effect of the raw-httpx era). All other public methods (`create`, `get`, `update`, `delete`, `list`, `aclose`) keep their existing signatures; bodies are rewritten to use the pipeline.
  - `CancelSignal`: NEW public class added to `azure.ai.agentserver.core.durable`'s `__all__`. Replaces the bare `asyncio.Event` previously held at `TaskContext.cancel`. Backward-compatible API surface (`is_set()`, `wait()`) plus a new `.reason` property.
  - `TaskContext.cancel`: type changes from `asyncio.Event` to `CancelSignal`. The attribute name is unchanged; existing handler call patterns work unchanged; the change is purely additive.
  - `__all__` in `durable/__init__.py`: MUST gain `CancelSignal`. Verify no `stale_timeout` mentions; verify no `superseded` mentions.
- [ ] **Conformance gap-list document produced?** Required deliverable in this spec's directory: `conformance-gap-list.md`. For each affected surface, record the existing test file covering current behavior, the decision (extend test X / create new test Y) with justification, and the task ID in `tasks.md` that lands the test RED.
- [ ] **Non-duplication rule satisfied?** Existing `tests/durable/test_lifecycle.py`, `test_options.py`, `test_decorator_validation.py` cover the relevant surface; extend them with the negative assertions ("`@task(stale_timeout=...)` raises TypeError") rather than creating parallel modules. `get_active_run` recovery behavior extends `test_get_active_run.py` (or its equivalent — verify in gap list) rather than spawning a new module. Split-brain is a genuinely new concern and gets its own module per the §6 fixture's complexity.
- [ ] **Conformance tests added?** Per the gap list. Every removed/changed symbol gets a paired test asserting its new behavior (TypeError on removed kwarg; reclaim semantics on `get_active_run`).
- [ ] **TDD ordering verified?** RED-first, GREEN-second commits.
- [ ] **No synthetic-bypass shortcuts?** No direct monkeypatching of `TaskContext`. Use the provider stub and the test-only hooks (FR-018, FR-019) only.
- [ ] **Completeness meta-test still passes?** `pytest azure-ai-agentserver-core/tests/durable/test_contract_completeness.py` green.
- [ ] **Consolidated dev guide updated?** Per the Docs ↔ Samples Loop section above. The doc-review meta-test passes.
