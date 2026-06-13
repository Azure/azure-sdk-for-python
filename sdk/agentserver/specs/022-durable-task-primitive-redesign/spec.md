# Feature Specification: Durable-task primitive

**Feature Branch**: `feature/agentserver-durable-tasks` (existing branch — no new branch per @RaviPidaparthi 2026-06-13)
**Created**: 2026-06-13
**Status**: Draft
**Input**: User description: "Cut a speckit spec from the living draft at `sdk/agentserver/specs/021-narrow-redesign.md` — limit to creating the spec only."

**Reference**: This spec is the speckit form of the living draft at `sdk/agentserver/specs/021-narrow-redesign.md`. That draft was iterated over ~2 days through 17 resolved design questions (Q1–Q17). When the speckit form is silent on a detail, the living draft is the source of additional rationale; when the two contradict, this spec wins (the living draft is historical-iteration-shaped while this spec is normative).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — One-shot task is simple and ephemeral (Priority: P1)

A developer writes `@task`-decorated async function for short-lived work (LLM call, tool invocation, scoring). They invoke it via `await my_task.run(input=...)`; they get the handler's return value back directly, or an exception is raised. The task record disappears the moment the handler exits — no persistent storage of inputs, outputs, errors, or metadata after termination. If the developer doesn't supply a `task_id`, the framework auto-generates one (typically a GUID); `input_id` collapses to the same value (one-shot is 1:1 between task and input).

**Why this priority**: This is the maximally-simple developer experience for the most common use case. If this doesn't work cleanly the primitive is unfit for purpose.

**Independent Test**: Two parts (one per API form):
- For `.run()`: define a `@task`-decorated handler returning a typed value; assert (a) `output = await gen.run(input=...)` returns the typed value directly to the caller (NOT a `TaskRun` handle), (b) on handler raise the corresponding `TaskFailed` is raised to the caller, (c) the framework's task record is gone after terminal exit (verified via local provider's internal enumeration showing no record for that task_id).
- For `.start()`: assert that `run = await gen.start(input=...)` (no explicit `task_id`) returns a `TaskRun` handle where `run.task_id` is a framework-auto-generated non-empty string and `run.input_id == run.task_id` (one-shot 1:1 invariant).

**Acceptance Scenarios**:

1. **Given** a `@task`-decorated function `gen(ctx: TaskContext[GenInput]) -> GenOutput`, **When** the developer calls `output = await gen.run(input=GenInput(...))`, **Then** the call returns the handler's return value typed as `GenOutput` (no `TaskResult` wrapper), and no task record persists after the call.
2. **Given** a `@task`-decorated function that raises `MyError`, **When** the developer calls `await gen.run(task_id="t1", input=...)`, **Then** the call raises `TaskFailed(error={"type": "MyError", ...})` (the exception carries only the `error` dict; `task_id` is not on the exception — caller has it from the call site / run handle) and the record is deleted.
3. **Given** a `@task`-decorated function with no explicit `task_id`, **When** the developer calls `run = await gen.start(input=...)`, **Then** `run.task_id` is a framework-auto-generated string and `run.input_id == run.task_id`.

---

### User Story 2 — Multi-turn chain accepts inputs across turns without per-turn registration ceremony (Priority: P1)

A developer writes `@multi_turn_task(steerable=False)`-decorated function that processes one conversational turn at a time. The developer calls `.run(task_id="conv-42", input=...)` for the first turn; the handler runs and returns a turn output. On the next turn, they call `.run(task_id="conv-42", input=...)` again with the same `task_id`; the framework transitions the chain from `suspended` back to `in_progress`, hydrates `ctx.metadata` from the prior turn, and invokes the handler with the new input. The chain stays alive across turns indefinitely. If the developer wants to stop the chain, they call `multi_turn_task.delete(task_id="conv-42")`.

**Why this priority**: This is the primary capability for long-lived conversations: multi-turn chains are first-class rather than modeled as one-shot work.

**Independent Test**: Define a `@multi_turn_task` handler that increments a metadata counter on each call and returns the count; invoke it 3 times sequentially with the same `task_id`; assert (a) each call returns the correct sequential count, (b) `ctx.metadata` is the same dict across turns, (c) record is in `suspended` between turns (verified via local provider enumeration), (d) `payload["input"]` is null between turns, (e) `payload["_last_input_id"]` reflects the most recent input_id, (f) `multi_turn_task.delete(task_id)` removes the record.

**Acceptance Scenarios**:

1. **Given** a `@multi_turn_task(steerable=False)` chain at `task_id="chat-1"` with metadata `{"history": [I1]}` in `suspended`, **When** the developer calls `output = await chat.run(task_id="chat-1", input=I2)`, **Then** the chain transitions to `in_progress`, handler runs with `ctx.metadata["history"] == [I1]` and `ctx.input == I2`, handler appends and returns; on return chain transitions to `suspended` with `metadata == {"history": [I1, I2]}` and `payload["input"] == null`.
2. **Given** a `@multi_turn_task(steerable=False)` chain currently in `in_progress`, **When** the developer calls `.run(task_id=..., input=...)` (concurrent turn), **Then** the call raises `TaskConflictError(current_status="in_progress")`.
3. **Given** an active multi-turn chain, **When** the developer calls `multi_turn_task.delete(task_id=...)`, **Then** the chain record is deleted (force-delete via provider), any in-flight handler's `.result()` resolves with `TaskCancelled` (cause "chain_deleted" in framework structured logs), and a subsequent `.run()` on the same `task_id` creates a fresh chain.

---

### User Story 3 — Steerable multi-turn chain queues concurrent inputs without losing them (Priority: P2)

A developer writes `@multi_turn_task(steerable=True)` for a conversation that needs steering — i.e., a new user message arriving mid-turn should queue up rather than be rejected. The developer calls `.start(task_id, input_id, input)` for the first turn; while it's running, they call `.start(task_id, input_id_2, input_2)`. The first handler observes `ctx.cancel.is_set()` (steering signal); it cooperatively returns. The framework promotes the queued input as the next turn. The second `TaskRun.result()` resolves with the second turn's output.

**Why this priority**: Steering is the key differentiator for chat-style use cases where the developer can't predict input arrival timing. P2 because non-steerable chains (P1) cover the simpler case.

**Independent Test**: Define a `@multi_turn_task(steerable=True)` handler that watches `ctx.cancel` and returns early when set; call `.start()` twice in quick succession with the same `task_id`; assert (a) first call returns a TaskRun handle, (b) second call returns a TaskRun handle (NOT a conflict error), (c) first handler observed `ctx.cancel.is_set()`, (d) both TaskRun's `.result()` eventually resolve with their respective outputs, (e) chain ends in `suspended` after both runs complete.

**Acceptance Scenarios**:

1. **Given** a `@multi_turn_task(steerable=True)` chain in `in_progress` running turn 1, **When** the developer calls `.start(task_id, input_id=X, input=...)` for turn 2, **Then** the second call returns a `TaskRun` handle without raising; the first handler's `ctx.cancel` is set; turn 2 promotes after turn 1's clean return.
2. **Given** a `@multi_turn_task(steerable=False)` chain in `in_progress` running turn 1, **When** the developer calls a second `.start()` while turn 1 is in flight, **Then** the second call raises `TaskConflictError(current_status="in_progress")` (no queuing — steering is opt-in via `steerable=True`).

---

### User Story 4 — Per-turn handler exception does NOT kill the multi-turn chain (Priority: P1)

A developer's `@multi_turn_task` handler raises an exception mid-turn (LLM hallucination, tool failure, transient network error). The framework delivers the exception to the failing turn's `.result()` listener, transitions the chain to `suspended` (NOT `completed`), and accepts subsequent inputs normally. Any queued steerers promote and run their turns. The chain stays alive; the developer's next `.run()` / `.start()` succeeds.

**Why this priority**: Without this, a single transient turn failure would destroy long-lived conversations — unacceptable for production use cases.

**Independent Test**: Define a `@multi_turn_task` handler that raises `MyError` on EVERY call AND increments a process-local invocation counter. Call `.start(task_id="c1", input_id="i1", input=...)`; await the result — assert (a) `TaskFailed` is raised on `.result()`, (b) the chain record is in `suspended` (NOT `completed`) and the counter == 1. Call `.start(task_id="c1", input_id="i2", input=...)` again — assert (c) the second call returns a TaskRun (i.e., the chain accepts a new input — was NOT terminated by the first raise), (d) awaiting it ALSO raises `TaskFailed`, (e) the counter == 2 (handler was re-invoked, proving the chain stayed alive across raises).

**Acceptance Scenarios**:

1. **Given** a `@multi_turn_task` chain in `in_progress` whose handler raises `MyError`, **When** the framework processes the raise, **Then** the chain record PATCHes to `suspended` (NOT `completed`); `payload["input"]` is cleared; `payload["_retry_attempt"]` is cleared; no `payload["error"]` is written; the failing turn's `TaskRun.result()` raises `TaskFailed`; a subsequent `.run()` on the same `task_id` succeeds.
2. **Given** a steerable `@multi_turn_task` chain with a queued input behind turn 1, **When** turn 1's handler raises, **Then** turn 1's caller sees `TaskFailed`; the queued steerer PROMOTES and runs as the next turn with `ctx.entry_mode == "resumed"`; the chain remains alive.

---

### User Story 5 — Caller attaches to a SPECIFIC in-flight turn (Priority: P2)

A developer wants to attach to a specific in-flight turn of a multi-turn chain by `(task_id, input_id)` from another coroutine within the same process (or after inline-recovery reclaim). They call `multi_turn_task.get_active_run(task_id, input_id)`. If the chain's currently in-flight input is owned by THIS process and matches `input_id`, they get the `TaskRun`; otherwise `None`. They can then `await run.result()` to get the turn's output. Cross-process attach is NOT supported (the framework does not persist past outputs and has no interprocess result channel — see FR-023). There is no way to attach to a terminated run.

**Why this priority**: Exact `(task_id, input_id)` matching lets callers attach only to the in-flight turn they intended.

**Independent Test**: Start a multi-turn chain with turn 1 in flight (`input_id="i1"`); call `get_active_run(task_id, "i1")` — expect a non-None TaskRun. Call `get_active_run(task_id, "i2")` — expect None. Wait for turn 1 to complete; call `get_active_run(task_id, "i1")` again — expect None (no retrospective attach).

**Acceptance Scenarios**:

1. **Given** a multi-turn chain with `input_id="i5"` currently in flight in this process, **When** another coroutine in the same process invokes `multi_turn_task.get_active_run(task_id, input_id="i5")`, **Then** the call returns a `TaskRun` bound to that in-flight turn; awaiting `run.result()` yields the turn's output.
2. **Given** a multi-turn chain with `input_id="i5"` currently in flight in this process, **When** another coroutine in the same process invokes `multi_turn_task.get_active_run(task_id, input_id="i6")`, **Then** the call returns `None`.
3. **Given** a multi-turn chain whose turn `i5` has already terminated, **When** any caller invokes `multi_turn_task.get_active_run(task_id, input_id="i5")`, **Then** the call returns `None` (no retrospective attach).

---

### User Story 6 — Crash recovery preserves observational identity with non-crash execution (Priority: P1)

A handler is running mid-turn; the process crashes. The recovery scanner reclaims the in-progress task and re-invokes the handler with `ctx.entry_mode == "recovered"` and `ctx.input` set to the **persisted** input — the same input the original handler was processing. If a new caller arrives during the reclaim with a different input, that new input is treated identically to the non-crash case: rejected (`TaskConflictError`) for non-steerable, queued for steerable. There is no "caller-supplied input replaces persisted input" path.

**Why this priority**: This is the core durability promise. Crash recovery must be observationally invisible — the same code paths run with the same inputs whether or not a crash happened.

**Independent Test**: Configure a `@multi_turn_task(steerable=False)` chain; start it with `input_id="i1"`; simulate lease expiry mid-handler (via test harness); confirm the scanner reclaims and re-invokes with `ctx.input == I1` (NOT a new input) and `ctx.entry_mode == "recovered"`. Then have a different caller invoke `.start(task_id, input_id="i2", input=I2)` during recovery: expect `TaskConflictError(current_status="in_progress")`.

**Acceptance Scenarios**:

1. **Given** an in-progress task whose lease has expired, **When** the recovery scanner reclaims, **Then** the handler is re-invoked with `ctx.input` = the persisted `payload["input"]` and `ctx.entry_mode == "recovered"`.
2. **Given** an in-progress task whose lease has expired, **When** a new caller invokes `.start(task_id, input=NEW_INPUT)` inline (discovering the expired lease before the scanner does), **Then** the framework reclaims with the **persisted** input (NOT `NEW_INPUT`), and the caller's call is treated as a concurrent-input event per non-crash rules (raise or queue).

---

### Edge Cases

- **Fire-and-forget multi-turn raise**: handler raises with no listener on `.result()`. Framework MUST emit a structured failure log/telemetry event regardless of listener presence. Framework MUST consume the unawaited future exception to avoid asyncio's "exception was never retrieved" warning.
- **`multi_turn_task.delete(task_id)` while in-flight handler is mid-PATCH**: handler's next PATCH after lease invalidation hits `TaskNotFound`; framework's manager translates to terminal cleanup; caller's `.result()` resolves with `TaskCancelled` (cause "chain_deleted" in framework logs). Anything the handler wrote in the race window between lease-invalidation and PATCH-failure is silently lost (accepted design trade-off).
- **`multi_turn_task.delete(task_id)` racing queued-steerer promotion**: if delete arrives before the promotion CAS, queued steerers resolve with `TaskCancelled`. If promotion CAS already succeeded → that turn cancels via the same path. The DELETE invalidates the chain's etag; in-flight promotion CAS fails and the manager catches it.
- **Timeout signal ignored by handler**: cooperative cancellation is the design. If the handler doesn't observe `ctx.cancel.is_set()`, it runs to completion; the framework does NOT force-stop. Caller's `.result()` returns whatever the handler returned (or raises whatever it raised). The timeout watchdog is re-armed on steering drain so each promoted turn gets a fresh timeout budget.
- **`Task.options()` is not part of the public surface**: developers who want variants of the same handler with different options author multiple `@task` / `@multi_turn_task` decorators with distinct `name=` values. Cleaner Python pattern; no registration-name collision.
- **`/tasks/resume` HTTP route is not part of the public surface**: framework no longer exposes a route for platform-initiated resume. `entry_mode="resumed"` is still produced by developer-initiated `.run()` / `.start()` on a `suspended` task — only the platform-trigger path goes away.
- **Deployment-config flip on `steerable_conversations` (responses-team concern)**: `derive_task_id` includes the `steerable` flag in its partition key; flipping the config produces different `task_id` values for the same logical request. Records under the previous flag value become unreachable from the current dispatch path; they remain in storage until service TTL housekeeping reclaims them. No primitive-mismatch errors; the deployer accepts abandoning in-flight tasks if they flip the config.

## Requirements *(mandatory)*

### Functional Requirements

#### Decorators and identifier supply

- **FR-001**: System MUST provide a `@task` decorator that produces a one-shot durable task (single-input, single-output, single execution). The decorator accepts `name=` (required, `str`), `title=` (optional, `str | None` — **static string only; no callable-factory form**), `timeout=` (optional, `timedelta | None`), `retry=` (optional, `RetryPolicy | None`). The `steerable=` argument MUST be rejected for `@task` (one-shot has no steering surface). One-shot tasks are always ephemeral (no `ephemeral=` argument). Passing a non-string to `title=` MUST raise `TypeError` at decoration time. The decorator MUST return a **`Task[Input, Output]`** instance (NOT a `MultiTurnTask`) — the two are distinct public classes (see FR-069).
- **FR-002**: System MUST provide a `@multi_turn_task(steerable=True|False)` decorator that produces a multi-turn chain primitive. The decorator accepts `name=` (required, `str`), `title=` (optional, `str | None` — **static string only; no callable-factory form**), `timeout=` (optional, `timedelta | None`), `retry=` (optional, `RetryPolicy | None`), `steerable=` (default `False`). Passing a non-string to `title=` MUST raise `TypeError` at decoration time. The decorator MUST return a **`MultiTurnTask[Input, Output]`** instance (NOT a `Task`) — the two are distinct public classes (see FR-069).
- **FR-003**: Handler signature is `async def fn(ctx: TaskContext[Input]) -> Output` for both primitives — the same shape for both primitives. All identifiers (`task_id`, `input_id`) accessed via `ctx`.
- **FR-004**: One-shot `async .run(...)` / `async .start(...)` MUST accept the following keyword arguments: `input` (required, typed `Input`), `task_id` (optional `str | None` — if omitted, framework auto-generates a GUID), `input_id` (optional `str | None` — if omitted, defaults to `task_id` per one-shot 1:1 invariant), `if_last_input_id` (optional `str | None = None` precondition argument; on mismatch the framework MUST raise `LastInputIdPreconditionFailed(actual_last_input_id)` per FR-076). `.run()` returns `Output`; `.start()` returns `TaskRun[Output]`.
- **FR-005**: Multi-turn `async .run(...)` / `async .start(...)` MUST accept the following keyword arguments: `input` (required, typed `Input`), `task_id` (required `str` — identifies the chain), `input_id` (optional `str | None` — if omitted, framework auto-generates a separate GUID per turn), `if_last_input_id` (optional `str | None = None` precondition argument; on mismatch the framework MUST raise `LastInputIdPreconditionFailed(actual_last_input_id)` per FR-076). `.run()` returns `Output`; `.start()` returns `TaskRun[Output]`.
- **FR-006**: `Task.options(**overrides)` MUST NOT be part of the public surface.

#### Multi-turn ergonomics

- **FR-007**: Multi-turn handler `return X` MUST be treated as implicit suspend. The chain MUST stay alive and accept the next input. Framework MUST stamp an internal `suspension_reason="run_completion"` on the record (not exposed to caller; diagnostic-only).
- **FR-008**: Multi-turn `ctx.suspend(...)` MUST NOT be part of the public surface. `return X` is the only clean exit.
- **FR-009**: System MUST NOT introduce a `ctx.end_chain()` symbol. Chain cleanup is via `multi_turn_task.delete(task_id)` only.

#### Per-turn failure semantics (Q6, Q14)

- **FR-010**: Multi-turn handler `raise E` MUST transition the chain record `in_progress → suspended` (NOT `completed`). The chain stays alive.
- **FR-011**: On multi-turn raise, the framework MUST PATCH the record atomically with: `status=suspended`, `payload.input=null`, `payload._retry_attempt=null`, `suspension_reason="run_completion"` (same as clean return). No `payload.error` MUST be written. `payload._last_input_id` MUST be unchanged. Steering queue MUST be unchanged.
- **FR-012**: On multi-turn raise, the failing turn's `TaskRun.result()` MUST raise `TaskFailed(error_dict)` (or `TaskCancelled()` — bare, no fields — if the handler raised `CancelledError` per cooperative cancel rules). `TaskCancelled` carries NO fields: cancellation causes can compound (e.g., cancel_requested + timeout_exceeded both true), and the framework cannot deterministically pick one; cause detail lives in framework structured logs (FR-015). Caller already has the `task_id` from the run handle.
- **FR-013**: On multi-turn raise, any queued steerers MUST PROMOTE — the head of the queue dispatches as the next turn with `ctx.entry_mode == "resumed"`.
- **FR-014**: For one-shot handler raise, the framework MUST transition `in_progress → completed`, delete the record (always ephemeral), and raise `TaskFailed` on the caller's `.result()`.
- **FR-015**: The framework MUST emit a structured failure log/telemetry event for every handler failure (one-shot or multi-turn), independent of listener presence. The framework MUST consume any unawaited future exception to prevent asyncio's "exception was never retrieved" warnings.

#### Read / attach APIs

- **FR-016**: `Task.get(task_id) -> TaskSnapshot | None` MUST NOT be part of the public surface.
- **FR-017**: `TaskSnapshot` type MUST NOT be part of the public surface.
- **FR-018**: `TaskResult[O]` envelope type MUST NOT be part of the public surface. `.run()` and `TaskRun.result()` MUST return `Output` directly (typed `-> Output`). (Cross-reference: FR-052 adds the ID-visibility nuance for callers that need to read the auto-generated `task_id` / `input_id`.)
- **FR-019**: `Suspended[O]` envelope type MUST NOT be part of the public surface.
- **FR-020**: `TaskStatus` literal type MUST NOT be part of public exports (orphaned after `TaskRun.status` removal).
- **FR-021**: `OutputTooLarge` exception MUST NOT be part of public exports (no output write sites left to raise it).
- **FR-022**: One-shot `async task.get_active_run(task_id: str) -> TaskRun | None` MUST return `None` unless `task_id` is currently in-flight in this process or reclaimable inline. No retrospective attach.
- **FR-023**: Multi-turn `async multi_turn_task.get_active_run(task_id: str, input_id: str) -> TaskRun | None` MUST take BOTH `task_id` and `input_id`. MUST return `None` unless that exact `(task_id, input_id)` is currently in-flight **in this process or reclaimable inline by this process** (same scoping as the one-shot variant per FR-022). Cross-process attach is NOT supported — there is no persisted output store and no interprocess result channel.
- **FR-024**: System MUST provide a public `async multi_turn_task.delete(task_id: str) -> None` classmethod (force-delete via provider, `force=True` per §24.3). Removes the chain record + any queued inputs. Idempotent (delete on non-existent task_id is a no-op).

#### Storage / persistence

- **FR-025**: Framework MUST NOT write `payload["output"]` on any terminal exit (no output persistence on the record). Framework MUST NOT serialize the handler's output value or apply any output-size check — there is no output write site, so size and serialization concerns do not arise.
- **FR-026**: Framework MUST NOT promote large outputs to the `_output` attachment slot. The `_output` attachment key is unused; framework MUST NOT write or delete it.
- **FR-027**: Framework MUST NOT write `payload["error"]` on terminal failure (no error persistence on the record).
- **FR-028**: Framework MUST clear `payload["input"]` (and any input-attachment) at the `in_progress → suspended` transition (multi-turn) and at the `in_progress → completed` transition (one-shot, just before record deletion). Input is needed only while `in_progress` for crash-recovery re-delivery.
- **FR-029**: Framework MUST keep `payload["_last_input_id"]` across the `in_progress → suspended` transition. Used for `if_last_input_id` precondition matching on next `.run()` / `.start()` and for `get_active_run(task_id, input_id)` exact-match. `payload["_last_input_id"]` MUST NOT be used as the crash-recovery input source — the recovery input source is `payload["input"]` for an active in-flight turn (per FR-033), and `payload["_steering"].active_input` during the steering-drain window when the manager has dequeued a queued input but not yet PATCHed it as the new in-flight `payload["input"]`.
- **FR-030**: Framework MUST keep `payload["_retry_attempt"]` while `in_progress` (crash-safe retry budget tracking); MUST clear it at the `in_progress → suspended` / `→ completed` transition (consistent with input clear). New turns start fresh with `_retry_attempt=0`.
- **FR-031**: Framework MUST NOT PATCH an interim `error` field between retry attempts. (The watermark write has no read-back path.)
- **FR-032**: Steering queue MUST stay in `payload["_steering"]` on the chain task record (no separate pending-record kind).

#### Recovery (Q13)

- **FR-033**: Crash recovery (lease expired mid-handler) MUST always re-invoke the handler with the **persisted** `payload["input"]`, regardless of whether reclaim is performed by the scanner or inline by a new `.start()` / `.run()`.
- **FR-034**: A new `.start()` / `.run()` against an `in_progress` task with expired lease MUST: (a) acquire the lease via CAS, (b) re-invoke the handler with the persisted input (`entry_mode="recovered"`), (c) evaluate the caller's new input through the standard non-crash path — either `TaskConflictError(current_status="in_progress")` for one-shot / non-steerable multi-turn, or queue the input for steerable multi-turn.
- **FR-035**: System MUST guarantee observational identity between crash and non-crash flows for the same logical sequence of `.run()` / `.start()` calls.

#### Cancellation, timeout, shutdown

- **FR-036**: All cancellation in the framework MUST be cooperative. The framework MUST set `ctx.cancel` (and other cause booleans like `ctx.timeout_exceeded`); the handler observes and exits. The framework MUST NOT force-stop a handler that ignores the cancel signal.
- **FR-037**: `TaskRun.cancel()` MUST exist and use cooperative cancel semantics. For a handle bound to a queued (not-yet-promoted) steerer, `cancel()` MUST remove the input from the steering queue and resolve the handle's `.result()` with `TaskCancelled` (cause "cancelled_before_start" in framework structured logs).
- **FR-038**: `timeout=` decorator argument MUST apply per handler invocation (per-turn for multi-turn). The timeout watchdog MUST set `ctx.timeout_exceeded` + `ctx.cancel` on expiry — no automatic raise. For multi-turn, the watchdog MUST be re-armed on each turn dispatch (including the steering-drain path) — each turn gets a fresh timeout budget.
- **FR-039**: `ctx.exit_for_recovery()` MUST exist on both primitives. It force-expires the lease, leaves status `in_progress` (not suspended) and keeps `payload["input"]` and steering queue. Caller's `.result()` raises **`TaskDeferred`** — a distinct exception, NOT `TaskCancelled`. Semantically: the task is not terminated; this lifetime is deferring to the next. The recovery scanner re-invokes the handler in the next process lifetime; a future caller can attach via `multi_turn_task.get_active_run(task_id, input_id)` (multi-turn) once the scanner reclaims.
- **FR-040**: `ctx.shutdown` MUST exist as the graceful-shutdown signal exposed to the handler.

#### Retry (Q7)

- **FR-041**: `RetryPolicy` MUST be accepted on both `@task(retry=...)` and `@multi_turn_task(retry=...)`. Mechanics within a handler invocation MUST be per-handler-invocation: `ctx.retry_attempt` is a cross-lifetime counter, crash recovery does not consume budget, and suspend bypasses retry.
- **FR-042**: For one-shot, post-retry-exhaustion MUST: delete the record (always ephemeral) and raise `TaskFailed` on the caller's `.result()`.
- **FR-043**: For multi-turn, post-retry-exhaustion MUST: transition chain to `suspended` per FR-010/FR-011 (chain stays alive); raise `TaskFailed` on the failing turn's `.result()`; subsequent turns get fresh retry budgets.

#### Metadata (Q8)

- **FR-044**: `ctx.metadata` MUST be the callable-namespace facade. The `TaskMetadata` class MUST expose:
  - Default-namespace access via `ctx.metadata[key]` / `ctx.metadata[key] = value` / `del ctx.metadata[key]` / `key in ctx.metadata` / `iter(ctx.metadata)` (standard mapping protocol via `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`).
  - `ctx.metadata.get(key, default=None) -> JSONValue | None` — same shape as `dict.get`.
  - Namespace selection via `ctx.metadata(namespace: str) -> TaskMetadata` (callable) returning a sub-facade scoped to `namespace`.
  - `ctx.metadata.flush()` async method as the explicit fence (forces persisted-state visibility before the next handler operation).
  - Reserved namespace prefix `_`: any namespace whose name starts with `_` is framework-reserved. Developers MUST NOT pass a `_`-prefixed namespace; the framework MUST raise `ValueError` at decoration / write time when developer code attempts to.
- **FR-045**: Framework auto-flush MUST run at lifecycle boundaries (suspend / success / cancel / retry-exhausted). For multi-turn, auto-flush at handler-raise is load-bearing — flushed metadata MUST be visible to the next turn's handler (per Q6 chain-stays-alive semantic). Auto-flush MUST also run before each step of the 7-step ordering in FR-053 (specifically: step 2 happens BEFORE the record PATCH in step 4 — see FR-053).
- **FR-046**: For one-shot, metadata MUST be invocation-local (record deleted on terminal; no cross-invocation visibility). Developers MUST NOT rely on `ctx.metadata` for cross-invocation state in one-shot.

#### TaskRun handle shape (Q9)

- **FR-047**: `TaskRun[Output]` public surface MUST expose (using async method semantics where I/O is implied):
  - `task_id: str` — read-only attribute
  - `input_id: str` — read-only attribute
  - `metadata: TaskMetadata` — read-only property
  - `async result() -> Output` — awaits in-flight execution; raises per the exception taxonomy
  - `async cancel() -> None` — cooperative cancel per FR-037 / FR-054
  - `__await__()` — equivalent to `result()` (allows `output = await run` shorthand)
- **FR-048**: `TaskRun` MUST NOT expose `delete()`, `refresh()`, `status`, or `lease_expiry_count`.

#### Not included surface (Q12, Q15, Q17)

- **FR-049**: `POST /tasks/resume` HTTP route MUST NOT be exposed. `_resume_route.py` does not exist in the final tree; `TaskManager.handle_resume()` does not exist; associated tests are rewritten around developer-initiated resume paths. `entry_mode="resumed"` semantic stays for developer-initiated `.run()` / `.start()` on suspended tasks.
- **FR-050**: Stale docstring at `azure/ai/agentserver/core/durable/__init__.py:18-19` claiming `async for chunk in task_run` MUST be corrected (streaming is the peer subpackage; `TaskRun` has no `__aiter__`).

#### Decorator argument validation (Q10 gap)

- **FR-051**: Both `@task` and `@multi_turn_task` decorators MUST reject unknown / unsupported keyword arguments at decoration time, raising `TypeError`. Specifically: `tags=`, `ephemeral=` (not accepted per FR-001), and `steerable=` on `@task` (one-shot has no steering surface per FR-001) MUST all raise. The accepted-kwargs allow-list is exactly `name=`, `title=`, `timeout=`, `retry=` (both primitives), plus `steerable=` (multi-turn only).

#### Identifier ergonomics (Q9 / Q10 / 021 §2.1 use-case table)

- **FR-052**: `.run()` MUST return `Output` directly (no wrapper — same shape as FR-018; this FR adds the ID-visibility nuance). Auto-generated `task_id` / `input_id` values are NOT exposed via `.run()`'s return path. Callers who need ID visibility MUST use `.start() + await run` (per the three documented use cases in 021 §2.1: "don't care" / "explicit IDs supplied" / "want auto-gen visible via handle"). The `inspect.signature(Task.run).return_annotation` MUST resolve to `Output` (not `Awaitable[TaskResult[Output]]` or any wrapper).

#### Multi-turn raise — explicit ordering of operations (Q14 7-step)

- **FR-053**: On multi-turn handler `raise E`, the framework MUST apply the following operations in this exact order:
  1. Run `_handle_multi_turn_failure` (or its dedicated equivalent).
  2. Auto-flush `ctx.metadata` (per Q8 — load-bearing for cross-turn marker propagation).
  3. Clear `payload["input"]` and `payload["_retry_attempt"]`.
  4. PATCH chain record to `suspended` (NOT `completed`) with `suspension_reason="run_completion"`.
  5. Resolve current caller's `.result()` future. Outcome depends on what the handler raised: if the handler raised `asyncio.CancelledError` (cooperative cancel / timeout honored), resolve with bare `TaskCancelled()`; for any other `E`, resolve with `TaskFailed(error_dict)`. (Per FR-012 / FR-055.)
  6. If queued steerers exist, promote the head (dequeue input, transition `suspended → in_progress`, dispatch handler with the queued input).
  7. If no queued steerers, leave the chain in `suspended` awaiting future `.run()` / `.start()`.

#### Cancellation / deletion / shutdown matrix (Q14 10-row)

- **FR-054**: `TaskRun.cancel()` on a one-shot task: cooperative cancel signal sent via `ctx.cancel`. Caller-visible outcome depends ENTIRELY on what the handler raises (per FR-015 / FR-053 step 5): if handler raises `asyncio.CancelledError` → caller's `.result()` raises `TaskCancelled` (bare, no fields); if handler raises any OTHER exception `E` → caller's `.result()` raises `TaskFailed(error_dict)`; if handler returns `Output` normally → caller's `.result()` returns `Output` (observing `ctx.cancel` is set DOES NOT auto-convert a clean return into `TaskCancelled`). Record deleted after terminal exit (always ephemeral). `TaskCancelled` carries no fields — cancellation causes can compound and aren't deterministically pickable by the framework. Cause detail (e.g., "cancel_requested") is emitted in framework structured logs (FR-015). Caller already has the `task_id` from the run handle.
- **FR-055**: `TaskRun.cancel()` on a multi-turn in-flight turn: same cooperative cancel semantic as FR-054. If handler raises `asyncio.CancelledError` → caller's `.result()` raises `TaskCancelled`; if handler raises any other `E` → `TaskFailed(error_dict)`; if handler returns `Output` → `.result()` returns `Output`. **Chain stays alive** in all three cases (cancel is a per-turn signal, not chain-wide); queued steerers PROMOTE per FR-013.
- **FR-056**: `timeout=` expiry on one-shot: cooperative-only signaling. Framework sets `ctx.timeout_exceeded` + `ctx.cancel`; **the framework NEVER raises automatically and NEVER force-stops the handler**. Caller-visible outcome follows the same rules as FR-054: if handler raises `asyncio.CancelledError` → `TaskCancelled` (cause "timeout_exceeded" in framework logs); if handler raises other `E` → `TaskFailed`; if handler returns `Output` → returns `Output` normally (a handler is permitted to observe `ctx.timeout_exceeded` and return early with a partial result). Record deleted after terminal exit. If handler ignores all signals → runs to completion (cooperative cancellation IS the design; see also FR-038).
- **FR-057**: `timeout=` expiry on multi-turn: same per-turn semantic as FR-056 for the in-flight turn. Chain stays alive (turn-suspend per FR-007 on the handler's terminal action); queued steerers PROMOTE and get a fresh timeout watchdog per turn (watchdog MUST be re-armed on steering drain per FR-038).
- **FR-058**: `ctx.exit_for_recovery()` (both primitives): force-expires lease, leaves status `in_progress` (per FR-039); caller's `.result()` raises **`TaskDeferred`** (NOT `TaskCancelled` — the task is deferring this lifetime, not terminating); preserves `payload["input"]` and steering queue for next-lifetime recovery.
- **FR-059**: Process lease expiry (mid-handler crash, both primitives): future is leaked locally; scanner reclaims; new lifetime re-invokes handler with persisted input (per FR-033). For multi-turn, queued steerers persist on the record; queue intact post-reclaim.
- **FR-060**: `multi_turn_task.delete(task_id)` while in-flight: force-delete via provider DELETE with `force=True`. Active caller's `.result()` raises `TaskCancelled` (cause "chain_deleted" in framework structured logs) via lease-loss path. ALL queued steerers' `.result()` futures raise `TaskCancelled` — resolved before any promotion attempt. Record removed. Idempotent (second delete is a no-op).
- **FR-061**: Race: `delete()` happens mid-promotion (FR-053 step 6). Regardless of timing, the eventual outcome MUST be `TaskCancelled` for all callers (force-delete is NOT cooperative — handler cooperation is irrelevant). Two sub-cases: (a) if promotion CAS already succeeded before delete arrived → the newly-promoted turn's `.result()` raises `TaskCancelled` via the FR-060 lease-loss path (NOT FR-055's cooperative cancel — delete invalidates the lease and the handler's next PATCH hits `TaskNotFound`, then the manager translates to terminal cleanup). (b) If delete arrived before promotion CAS → queued head never runs; resolved with `TaskCancelled` directly. DELETE invalidates the chain etag; in-flight promotion CAS fails; the manager MUST catch the CAS failure and resolve queued futures with `TaskCancelled` rather than retrying.
- **FR-062**: Process shutdown (`ctx.shutdown` set, graceful): if handler returns within grace period → normal result. If grace expires → treated like crash (in_progress retained for next-lifetime recovery). For multi-turn, queued steerers persist on the record.

#### Entry-mode matrix (Q11 normative)

- **FR-063**: `ctx.entry_mode` MUST take exactly these values for the corresponding scenarios:
  - Fresh `.run()` / `.start()` on non-existent task_id → `"fresh"`.
  - `.run()` / `.start()` on a `suspended` multi-turn record (next turn) → `"resumed"`.
  - Scanner reclaim of an expired-lease in-progress record → `"recovered"`.
  - **Inline** reclaim by `.run()` / `.start()` of an expired-lease in-progress record → `"recovered"` (same as scanner per Q13 — no observable difference between the two reclaim paths).
  - Queued steerer later promoted to in_progress (multi-turn) → `"resumed"`.
  - Multi-turn raise → suspended → next `.run()` / `.start()` on the same chain → `"resumed"` (chain was in `suspended`; new input being applied; the previous-turn failure is invisible to the new handler from the record alone).

#### Inline recovery 5-step algorithm (Q13)

- **FR-064**: For `.start()` / `.run()` against an `in_progress` record with expired lease, the framework MUST execute these 5 steps in order: (1) acquire lease via CAS on lease etag; (2) determine `entry_mode = "recovered"`; (3) re-invoke handler with **persisted** `payload["input"]` (NOT caller's new input); (4) evaluate caller's new input through standard non-crash path — `TaskConflictError(current_status="in_progress")` for one-shot or non-steerable multi-turn; queued for steerable multi-turn; (5) return value: for the conflict case raises `TaskConflictError`; for the queue case returns a `TaskRun` bound to the **queued input** (not the recovered turn — the new caller has no handle to the recovered turn from this `.start()`). To attach to the recovered turn, the caller would need `get_active_run(task_id, persisted_input_id)` — which they typically don't know.

#### Internal dead-code cleanup (Q17)

- **FR-065**: The following internal-only code MUST NOT exist in the final implementation:
  - `_result.py` (entire file)
  - `Suspended` class in `_run.py`
  - `TaskContext.suspend()` method in `_context.py`
  - `_build_output_co_write()` in `_manager.py`
  - All output write/clear PATCH sites in `_manager.py` (success / suspend / failure / resume / drain output projections)
  - `_handle_failure` post-exhaustion error-dict construction (the `ephemeral=False` branch)
  - Interim retry-attempt `error` field PATCH between attempts
  - `_resume_route.py` (entire file)
  - `TaskManager.handle_resume()` method
  - `Task.options()` method in `_decorator.py`
  - `TaskRun.delete()` and `TaskRun.refresh()` methods in `_run.py`
  - `TaskRun._provider`, `_terminate_event`, `_terminate_reason_ref`, `_status`, `_lease_expiry_count` slots
  - `TaskInfo.output` and `TaskInfo.error` fields (internal model — dead with no output/error writes)

#### Responses package migration (021 §7)

- **FR-066**: `azure-ai-agentserver-responses` migration MUST register TWO task primitives per orchestrator: one `@task` (one-shot) for cases where `derive_task_id` produces a fresh per-request id, and one `@multi_turn_task(steerable=self._options.steerable_conversations)` for cases where the chain shape applies. Dispatch at `start_durable` time per the 6-row matrix in 021 §7.1. The `derive_task_id` partition logic that maps a request's `(store, prev_resp_id, conv_id)` shape to a stable `task_id` MUST be preserved unchanged — it is the load-bearing identifier-supply rule that keeps chains stable across turns.
- **FR-067**: The responses-package recovery branches (`ctx.suspend(reason="crash_failed")` / `ctx.suspend(reason="non_bg_crash_failed")` at `_durable_orchestrator.py:450,464`) MUST be rewritten to `return None` (NOT `raise`). Rationale: the response store holds the authoritative crash record via `_persist_crash_failed`; `.result()` should resolve successfully so any internal listener treats the response-store record as the source of truth (not a framework-level error). This is a deliberate choice — NOT because `return None` and `raise` are equivalent (they're not). Additionally, the normal-turn-return `ctx.suspend(reason="awaiting_next_turn")` call MUST be rewritten to `return None` per FR-008 (multi-turn `ctx.suspend()` is not part of the public surface). Total: **three** `ctx.suspend(...)` call sites are rewritten — two recovery branches + one normal turn-return. The `if self._options.steerable_conversations:` guards that today wrap the `ctx.suspend()` call sites MUST also be removed — return-is-implicit-suspend works the same regardless of steering mode, so the per-mode guard becomes unnecessary.
- **FR-068**: The responses-package bookkeeping-task variant (the body that holds `in_progress` waiting for an external `complete_bookkeeping_task` signal) MUST have its durability contract documented in code comments AND verified in a recovery-scenario test before the decorator switch. The documented contract MUST state, in this order: (a) the signal is persisted by `_persist_bookkeeping_signal` in the response store (NOT in `payload`); (b) on recovery, a recovered bookkeeping body MUST re-read the response store to determine whether the underlying work completed (the body MUST NOT rely on `payload` state for completion-check); (c) if the signal never arrives within `bookkeeping_timeout_seconds`, the body returns `None` and the response store records a "bookkeeping_timed_out" terminal state; (d) on graceful shutdown (`ctx.shutdown` set), the body returns `None` without raising — letting the recovery scanner pick it up in the next lifetime; (e) the body's normal terminal exit is `return` (not `raise`) so any internal listener treats the response-store record as the source of truth (consistent with FR-067's `return None` rationale). Migration MUST NOT regress crash-recovery behavior for this path. Additionally: deployment-time flips of `steerable_conversations` from one value to the other will produce a new `task_id` partition (because `derive_task_id` factors `steerable_conversations` into the id); existing chains under the old value will be orphaned and rely on service-side TTL for cleanup. This is acceptable but MUST be documented in the responses-package CHANGELOG.

#### Invocations-package durable samples migration

- **FR-068b**: The `azure-ai-agentserver-invocations` package's durable samples on this branch MUST be migrated to the design's primitive set. Specifically, the four durable samples MUST be rewritten:
  - `samples/durable_research/agent.py` — today's `@task(name="deep_research", steerable=True)` decorator MUST become `@multi_turn_task(name="deep_research", steerable=True)`. The `return await ctx.suspend()` call site (~line 413) MUST become `return None` (or `return <terminal-output-value>` if there is one). The docstring references to `ctx.suspend(...)` and the `Suspended` sentinel MUST be rewritten to describe the return-is-implicit-suspend semantic.
  - `samples/durable_multiturn/agent.py` — today's `@task(name="session_workflow")` MUST become `@multi_turn_task(name="session_workflow")` — **`steerable=False`** (default; verified against `samples/durable_multiturn/agent.py` + `samples/durable_multiturn/app.py`: the sample is sequential turns with no parallel-input pattern and no `prev_resp_id` / concurrent-input handling). The `return await ctx.suspend(reason="awaiting_user_input", output=output)` call site (~line 118) MUST become `return output`.
  - `samples/durable_langgraph/agent.py` — today's `@task(name="langgraph_session", steerable=True)` MUST become `@multi_turn_task(name="langgraph_session", steerable=True)`. All four `ctx.suspend(reason="awaiting_user_input"|"steered", output=...)` call sites MUST become `return output` (or `return None` where no output is constructed).
  - `samples/durable_copilot/agent.py` — today's `@task(name="copilot_session", steerable=True)` MUST become `@multi_turn_task(name="copilot_session", steerable=True)`. All four `ctx.suspend(reason=...)` call sites MUST become `return output` (or `return None`).
- **FR-068c**: After migration, the corresponding e2e tests under `azure-ai-agentserver-invocations/tests/e2e/` (`test_durable_research_live.py`, `test_durable_multiturn.py`, `test_durable_copilot_live.py`) MUST be green against the migrated samples. If any test asserts on observable behavior that the design changes (e.g., chain-completes-on-raise vs chain-stays-alive per Q6), the test MUST be updated to match the new contract — NOT papered over. If a sample's purpose was to demonstrate `ctx.suspend(reason="X")` for documentation purposes, the sample MUST be rewritten to demonstrate the equivalent `return X` semantic with a comment explaining the implicit-suspend behavior.
- **FR-068d** (TRACKED ON `feature/agentserver-durable-agent-demo` BRANCH — NOT on this branch): The `durable-agent-demo` sample (Azure-deployable durable research agent) lives on the separate `feature/agentserver-durable-agent-demo` branch — see `sdk/agentserver/azure-ai-agentserver-invocations/samples/durable-agent-demo/` on that branch (README.md, build.sh, demo-client.sh, infra/, src/durable-research-agent/agent.py, azure.yaml). That branch's `samples/durable-agent-demo/src/durable-research-agent/agent.py` MUST be migrated with the same translation rules as FR-068b (`@task(steerable=True)` → `@multi_turn_task(steerable=True)`; `ctx.suspend(...)` → `return X`). The migration MUST happen as a separate PR on `feature/agentserver-durable-agent-demo` AFTER this design's PR merges on `main`, OR as a coordinated cross-branch effort if the demo owner prefers to align timing. The bundled wheels referenced by `build.sh` MUST be rebuilt against the merged `azure-ai-agentserver-core` and `azure-ai-agentserver-invocations` packages. The `demo-client.sh` end-to-end demo run MUST pass against the migrated codebase. (Any `durable-agent-demo` directory on THIS branch is a stale leftover that has been removed; see commit history.)

#### Local provider (Q16)

- **FR-068a**: The local file provider (`_local_provider.py`) MUST require NO code change to support the design. Output write sites live in `_manager.py`, not in the provider; the provider is a generic PATCH/DELETE engine that does not know about `payload["output"]` specifically. The manager simply stops emitting output-projection PATCHes, and the provider behavior is correct automatically. Conformance tests asserting `_output` attachment behavior (C-OUT in SOT, plus related C-ATT-3/4/5 entries) MUST be removed or rewritten because no code generates the writes they assert on. Spec 020's local-provider list parity is unaffected.

#### Public-surface type system (Appendix A of 021)

- **FR-069**: `Task` and `MultiTurnTask` MUST be **two distinct public Python classes** (NOT a single combined class with mode flags; NOT subclasses). Each decorator MUST return the corresponding class. The type checker MUST be able to statically enforce: (a) `.delete(task_id)` is callable ONLY on `MultiTurnTask` (and the equivalent classmethod `multi_turn_task.delete(task_id)`); (b) multi-turn `get_active_run(task_id, input_id)` requires BOTH args while one-shot `task.get_active_run(task_id)` takes only `task_id`. Both MUST be exported from `azure.ai.agentserver.core.durable.__init__.py` `__all__`.
- **FR-070**: System MUST export a public recursive type alias `JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]` from the durable package. `TaskMetadata` values MUST be constrained to `JSONValue` (instead of untyped `Any`). Writing a non-JSON-serializable value to `ctx.metadata` SHOULD raise `TypeError` at write time (or be rejected by the auto-flush serializer at the latest).
- **FR-071**: System MUST export two public TypedDicts:
  - `TaskErrorDict` with fields `type: str` (exception class name), `message: str` (str(exc)), `traceback: str` (formatted traceback).
  - `TaskExhaustedRetriesErrorDict` with fields `type: Literal["exhausted_retries"]`, `attempts: int`, `last_error: str`, `last_error_type: str`, `traceback: str`.
  - `TaskFailed.error` MUST be typed `TaskErrorDict | TaskExhaustedRetriesErrorDict` (NOT untyped `dict`).
- **FR-072**: The `TaskContext[Input]` public surface MUST expose exactly the following members (this list is normative — adding or removing requires a spec amendment). `ctx.suspend()` is not included for multi-turn handlers per FR-008:
  - **Identifiers** (read-only): `ctx.task_id: str`, `ctx.input_id: str`
  - **Input**: `ctx.input: Input`
  - **Metadata facade**: `ctx.metadata: TaskMetadata`
  - **Cancellation / shutdown signals**: `ctx.cancel: asyncio.Event`, `ctx.cancel_requested: bool`, `ctx.timeout_exceeded: bool`, `ctx.shutdown: asyncio.Event`
  - **Recovery / entry context**: `ctx.entry_mode: EntryMode`, `ctx.retry_attempt: int`
  - **Steering observability** (multi-turn steerable=True only; constants on one-shot): `ctx.is_steered_turn: bool`, `ctx.pending_input_count: int`
  - **Control**: `ctx.exit_for_recovery()` (raises `TaskDeferred` on caller per FR-039)
- **FR-073**: `RetryPolicy` MUST be a regular Python class with `__slots__` + explicit `__init__` (NO `@dataclass` per repo convention — verified against `azure/ai/agentserver/core/durable/_retry.py`). All preset factories (`exponential_backoff(...)`, `fixed_delay(...)`, `linear_backoff(...)`, `no_retry()`) MUST enumerate their kwargs explicitly (no `...` in signatures). Public attributes: `max_attempts: int`, `initial_delay: float`, `max_delay: float`, `backoff_coefficient: float`, `jitter: float`, `retry_on: tuple[type[Exception], ...] | None`. Delay formula: `min(initial_delay * backoff_coefficient ** attempt, max_delay)`, with optional ±`jitter` fraction applied per attempt. `retry_on=None` means retry on all exceptions; otherwise only the listed exception types trigger retry.
- **FR-074**: `TaskNotFound` and `TaskPreconditionFailed` MUST NOT be exported from `azure.ai.agentserver.core.durable.__init__.py` `__all__`. Both MAY remain as internal exception types where the framework still needs them (e.g., `TaskNotFound` on provider lookup; `TaskPreconditionFailed` on provider rejection). No public API surfaces `TaskNotFound` to developers (`multi_turn_task.delete()` is idempotent, `get_active_run()` returns `None`, no `.get()` / `.refresh()` exists); `TaskPreconditionFailed` has no distinct developer-actionable contract.
- **FR-075**: `TaskFailed.__cause__` MUST NOT be set to the original handler exception. The structured `error` dict (FR-071) is the documented surface for failure inspection. Rationale: enabling `__cause__` would require pickle/serialization of arbitrary exception objects across crash recovery boundaries, which is not supported.
- **FR-076**: `LastInputIdPreconditionFailed` MUST carry only `actual_last_input_id: str | None` (the value persisted on the record at the time of the precondition check). The exception MUST NOT carry an `expected_last_input_id` field — the caller passed that value via `if_last_input_id=` (per FR-004 / FR-005) and already knows it. Caller's typical action on this exception is to retry with the actual value (or surface the concurrency conflict).
- **FR-077**: All public exceptions MUST follow the Pythonic "carry only new info" rule:
  - `TaskCancelled`, `TaskDeferred`, `SteeringQueueFull`, `InputTooLarge` carry NO fields (caller has `task_id` / `input_id` from the run handle or call site).
  - `TaskFailed(error)`, `TaskConflictError(current_status)`, `LastInputIdPreconditionFailed(actual_last_input_id)` carry only their respective new-info field.
  - No public exception carries a `task_id` field.
  - The name `TaskCancelledError` (with `Error` suffix) MUST NOT exist as a public symbol — only `TaskCancelled`. Importing `TaskCancelledError` from the durable package MUST raise `ImportError`.

### Key Entities

- **`@task` decorator**: produces a `Task[Input, Output]` Python object for one-shot durable execution. Always ephemeral; no chain semantics; auto-gen task_id supported.
- **`@multi_turn_task(steerable=)` decorator**: produces a **`MultiTurnTask[Input, Output]`** Python object for multi-turn chain execution. **`MultiTurnTask` is a distinct public class from `Task`** (NOT a subclass / not a single combined class — see FR-069). Steerable opt-in; chain lives until explicit delete.
- **`TaskRun[Output]`**: per-turn handle returned by `.start()` / `get_active_run`. Slim shape (per FR-047): `task_id`, `input_id`, `metadata`, `result()`, `cancel()`, `__await__`. No status, no delete, no refresh.
- **`TaskContext[Input]`**: handler-side context. Public surface enumerated in FR-072; `ctx.suspend` is not included for multi-turn per FR-008.
- **`TaskFailed` / `TaskCancelled` / `TaskDeferred` / `TaskConflictError` / `LastInputIdPreconditionFailed` / `SteeringQueueFull` / `InputTooLarge`** (7 public exceptions): `TaskDeferred` is raised when `ctx.exit_for_recovery()` is called; semantically distinct from `TaskCancelled` (task stays `in_progress`, not terminated). `TaskCancelled` and `TaskDeferred` carry NO fields (caller has task_id/input_id from the run handle; cancellation causes can compound and aren't deterministically pickable). Other exceptions carry no redundant `task_id` field — only **new information** fields are present (`TaskFailed.error`, `TaskConflictError.current_status`, `LastInputIdPreconditionFailed.actual_last_input_id`). `TaskCancelledError` (with `Error` suffix) does NOT exist — only `TaskCancelled`.
- **`TaskErrorDict` / `TaskExhaustedRetriesErrorDict`** (public TypedDicts per FR-071): the precise shapes of `TaskFailed.error`. Use precise shapes instead of an untyped `dict`.
- **`JSONValue`** (public type alias per FR-070): the recursive type for `TaskMetadata` values. Constrain metadata values instead of using `Any`.
- **`RetryPolicy`**: accepted on both decorators. Regular Python class with `__slots__` + explicit `__init__` (NO `@dataclass` per repo convention).
- **`TaskMetadata`**: callable namespace facade. Values constrained to `JSONValue` (FR-070).
- **`EntryMode`**: literal (`"fresh"` | `"resumed"` | `"recovered"`). Per FR-039 / Q11 entry_mode matrix.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer using `@task` for a one-shot task observes ZERO persistent storage of inputs / outputs / errors / metadata after terminal exit. Verified by enumerating the local provider's records before and after a `.run()` call — record count unchanged.
- **SC-002**: A developer using `@multi_turn_task` for a chat-style conversation can invoke the handler N times sequentially against the same `task_id` and observe correct per-turn metadata accumulation. Verified by E2E test in `tests/durable/test_multi_turn_chain.py`.
- **SC-003**: A multi-turn handler that raises an exception does NOT terminate the chain. The chain accepts subsequent inputs without intervention. Verified by E2E test with N=10 deliberate failures followed by successful turns.
- **SC-004**: Crash recovery (simulated via `_crash_harness`) reproduces the same handler-input pair the original execution was processing. Verified across all 4 recovery scenarios in `tests/durable/test_crash_recovery.py`.
- **SC-005**: `get_active_run(task_id, input_id)` for multi-turn returns the correct handle if and only if `(task_id, input_id)` matches an in-flight run. Tested with N matched and N+M mismatched `input_id` queries.
- **SC-006**: The `azure-ai-agentserver-core` Python source tree MUST be grep-clean for unsupported public-surface and storage symbols after implementation. Verified by grep at the end of impl pass. Required-empty grep terms: `TaskResult`, `Suspended`, `TaskSnapshot`, `TaskStatus`, `OutputTooLarge`, `Task\.get\b`, `Task\.options`, `TaskRun\.delete`, `TaskRun\.refresh`, `TaskRun\.status`, `TaskRun\.lease_expiry_count`, `ctx\.suspend\(`, `ephemeral=`, `/tasks/resume`, `handle_resume`, `_resume_route`, `_build_output_co_write`, `payload\["output"\]`, `payload\["error"\]`, `_output`-attachment write sites. Also verify absent internal slots/fields per FR-065 (`TaskRun._provider`, `_terminate_event`, `_terminate_reason_ref`, `_status`, `_lease_expiry_count`; `TaskInfo.output`, `TaskInfo.error`). Public-export exclusions (per FR-021 / FR-074): grep `__all__` in `durable/__init__.py` for `OutputTooLarge`, `TaskNotFound`, `TaskPreconditionFailed` — MUST be absent. The classes themselves MAY remain in `_exceptions.py` / `_exceptions_internal.py` for internal use; only their public export is absent.
- **SC-007**: No compatibility shims are added; the implementation exposes only the public surface specified here. Verified by code-review.
- **SC-008**: Downstream package `azure-ai-agentserver-responses` (per the §7 analysis in the living draft) uses the durable-task primitive cleanly. Per-row verification against the 6-row matrix in 021 §7.1:
  - Row 1 (`store=False`): no task primitive invoked; no framework lifecycle.
  - Row 2 (`store=True, no conv_id, no prev_resp_id`): `@task` (one-shot); record deleted on terminal.
  - Row 3 (`store=True, prev_resp_id only, steering off`): `@task` (one-shot) per fork-style task_id derivation; record deleted on terminal.
  - Row 4 (`store=True, prev_resp_id only, steering on`): `@multi_turn_task(steerable=True)`; chain stays alive across turns; steering queue functional.
  - Row 5 (`store=True, conv_id, steering off`): `@multi_turn_task(steerable=False)`; sequential turns SUCCEED; concurrent turns still return 409 conversation_locked.
  - Row 6 (`store=True, conv_id, steering on`): `@multi_turn_task(steerable=True)`; same as row 4 for chain semantics.
  All six rows verified by responses' E2E test suite. Two task registrations per orchestrator (one `@task` + one `@multi_turn_task(steerable=opt_in)`); per-request dispatch in `start_durable`; three `ctx.suspend(reason=...)` call sites rewritten to `return None` per FR-067; bookkeeping-task variant verified per FR-068.
- **SC-009**: Downstream package audit (per 021 §7.7) completed before merge: [ ] `azure-ai-agentserver-invocations` durable samples on this branch — explicit migration per FR-068b/c (4 samples + 3 live e2e tests + 1 langgraph smoke test + structure / shippable-bar test updates); [ ] `azure-ai-agentserver-invocations/samples/durable-agent-demo` — cross-branch hand-off filed on `feature/agentserver-durable-agent-demo` per FR-068d (NOT in this branch's PR); [ ] `azure-ai-agentserver-ghcopilot` — grep audit; [ ] `azure-ai-agentserver-optimization` — grep audit; [ ] in-tree samples (under `samples/` of any package other than invocations) — grep audit; [ ] tests outside `azure-ai-agentserver-core` — grep audit. Each item produces either a concrete migration patch (with paired e2e green) or a "no-op" justification (with the grep evidence).
- **SC-009a**: All 4 `azure-ai-agentserver-invocations` durable samples on this branch (`durable_research`, `durable_multiturn`, `durable_langgraph`, `durable_copilot`) MUST be green end-to-end after migration:
  - Grep clean in `samples/`: zero `@task(...steerable=True...)` usages (must be `@multi_turn_task(...)`); zero `ctx.suspend(...)` usages; zero `Suspended` sentinel references; zero `TaskResult` / `TaskSnapshot` references.
  - Live e2e tests pass: `tests/e2e/test_durable_research_live.py`, `tests/e2e/test_durable_multiturn.py`, `tests/e2e/test_durable_copilot_live.py` all green against the migrated samples + migrated `azure-ai-agentserver-core`.
  - Smoke test for `durable_langgraph`: `tests/e2e/test_durable_langgraph_smoke.py` (NEW, added as part of T-7.9) imports the migrated decorator + invokes one turn and asserts the chain transitions to `suspended` after `return`. Full live e2e for `durable_langgraph` is out of scope for this branch (no live test exists today) and tracked as a follow-up.
  - Structure test passes: `tests/test_durable_samples_structure.py` (asserts the sample shape) is updated or stays valid per the new primitive split.
  - Shippable-bar test passes: `tests/test_samples_shippable_bar.py` is updated to reflect the new decorator + return-is-implicit-suspend pattern.
  - **`durable-agent-demo` migration is tracked separately on `feature/agentserver-durable-agent-demo` branch per FR-068d** — not in scope for this branch's PR. (Any `durable-agent-demo` directory on this branch is a stale leftover and has been removed.)
- **SC-010**: Multi-turn handler raise + queued steerers: the 7-step order of operations from FR-053 is observable in a single E2E test. Verifies: auto-flush happens BEFORE record PATCH (metadata visible to next turn); current TaskFailed resolves BEFORE queued steerer promotes; queued promotion uses persisted-cleared input slot; chain ends in `suspended` with empty queue.
- **SC-011**: Metadata propagation across raise (Q8 load-bearing semantic): handler writes `ctx.metadata["last_failure_reason"] = "X"` before raising; next turn's handler observes `ctx.metadata["last_failure_reason"] == "X"`. Tested for raise, cooperative cancel, and retry-exhaustion paths.
- **SC-012**: Retry policy conformance: (a) `max_attempts=N` is applied per-turn for multi-turn (each turn gets a fresh budget; chain stays alive after exhaustion per FR-043); (b) `payload["_retry_attempt"]` is cleared on suspend transition (next turn starts with `_retry_attempt=0`); (c) no interim `error` field is PATCHed between retry attempts (verified by inspecting record between consecutive `ctx.retry_attempt` invocations).
- **SC-013**: `entry_mode` matrix (FR-063) verified by E2E test that produces each of the six listed scenarios and asserts the exact entry_mode literal. Includes both scanner-recovery and inline-recovery yielding `"recovered"` (no observable difference between them).
- **SC-014**: Cancellation/deletion/shutdown matrix (FR-054 through FR-062): one E2E test per matrix row verifies the specified caller-visible result, queued-steerer outcome, and record state after. Includes the delete-vs-promotion race rule (FR-061) with deterministic outcome regardless of timing.
- **SC-015**: Inline-recovery algorithm (FR-064) verified: a `.start()` against an expired-lease in-progress record returns a handle bound to the **queued** new input (steerable=True) or raises `TaskConflictError` (steerable=False / one-shot); the recovered handler runs with the **persisted** input; both observable behaviors match the non-crash case.
- **SC-016**: Public-surface type system verified (FR-069 through FR-077):
  - **Class split (FR-069)**: a mypy/pyright type-checking test asserts that `@task`-decorated handlers produce `Task[I, O]` instances and `@multi_turn_task`-decorated handlers produce `MultiTurnTask[I, O]` instances. Type checker rejects (a) calling `.delete()` on a `Task` (one-shot), (b) calling multi-turn `get_active_run(task_id)` without `input_id`, (c) cross-assigning a `Task` value to a `MultiTurnTask` variable.
  - **JSONValue (FR-070)**: `from azure.ai.agentserver.core.durable import JSONValue` succeeds; the alias is reachable as a public symbol; mypy/pyright accepts the recursive shape.
  - **TypedDicts (FR-071)**: `from azure.ai.agentserver.core.durable import TaskErrorDict, TaskExhaustedRetriesErrorDict` succeeds; `TaskFailed.error` is typed precisely (not `dict`); a runtime test constructs both shapes and confirms field-set parity.
  - **TaskContext surface (FR-072)**: a snapshot test compares the public attributes of `TaskContext` (via `dir(ctx)` filtered to non-underscore names) against the FR-072 list; new public ctx surface members require updating the snapshot AND the FR.
  - **RetryPolicy (FR-073)**: `RetryPolicy.__class__.__mro__` does NOT include `dataclasses._DATACLASS_SENTINEL` (or equivalent dataclass marker); `RetryPolicy.__slots__` is non-empty; preset factories have explicit kwargs (verified via `inspect.signature`).
- **SC-017**: Exception public-surface verified (FR-074 + FR-075 + FR-076 + FR-077):
  - `OutputTooLarge`, `TaskNotFound`, `TaskPreconditionFailed`, `TaskCancelledError` (with `Error` suffix) MUST NOT appear in `azure.ai.agentserver.core.durable.__all__`.
  - `from azure.ai.agentserver.core.durable import TaskNotFound` MUST raise `ImportError` (the public namespace MUST NOT re-export it). The class MAY exist in internal modules (e.g., `_exceptions_internal.py`) for framework use; only the public re-export is not included.
  - `inspect.signature(TaskCancelled)` and `inspect.signature(TaskDeferred)` and `inspect.signature(SteeringQueueFull)` and `inspect.signature(InputTooLarge)` all show `()` (no parameters).
  - `inspect.signature(TaskFailed)` shows `(error)`; `inspect.signature(TaskConflictError)` shows `(current_status)`; `inspect.signature(LastInputIdPreconditionFailed)` shows `(actual_last_input_id)`.
  - No public exception class has a `task_id` attribute.
  - `TaskFailed.__cause__` for a raised handler exception is `None` (not the original exception object) — verified via a test that raises a custom exception from a handler, catches `TaskFailed`, and asserts `caught.__cause__ is None`.
- **SC-018**: Decorator argument validation verified (FR-001 + FR-002 + FR-051):
  - **Accepted kwargs**: `@task(name=..., title="x", timeout=..., retry=...)` MUST succeed for both decorators (plus `steerable=` on `@multi_turn_task` only). Verified at decoration time.
  - **`title` static-string-only**: `@task(name="t", title=lambda input, task_id: "x")` MUST raise `TypeError` at decoration time (callable-factory form is not accepted per FR-001). Same assertion for `@multi_turn_task` per FR-002. Non-string types (int, dict, list) MUST also raise `TypeError`.
  - **Not included kwargs**: `@task(name="t", ephemeral=False)`, `@task(name="t", steerable=True)`, `@task(name="t", tags=["x"])`, `@multi_turn_task(name="t", ephemeral=False)`, `@multi_turn_task(name="t", tags=["x"])` MUST all raise `TypeError` at decoration time per FR-051.
  - **Allow-list completeness**: the decorator's accepted-kwargs allow-list (`name`, `title`, `timeout`, `retry`, plus `steerable` for multi-turn) MUST match FR-001 / FR-002 exactly — verified by introspecting `inspect.signature` of each decorator.

## Assumptions

- **A2**: The SOT spec at `sdk/agentserver/azure-ai-agentserver-core/docs/task-and-streaming-spec.md` and the developer guide at `docs/durable-task-guide.md` will be updated in lockstep with the implementation (per Principle IX). Stale references to unsupported concepts (TaskSnapshot, TaskResult, TaskStatus, etc.) are tracked in Q17 of the living draft and addressed during the docs sweep.
- **A3**: The local file provider (`_local_provider.py`) requires NO code change because output write sites live in the manager, not the provider (verified in Q16 of the living draft). The local provider just stops receiving output-projection PATCHes from the manager.
- **A4**: Hosted provider (`HostedTaskProvider`) requires no schema changes; the design narrows what the framework writes (no `payload["output"]` / `_output` attachment / `payload["error"]`) but doesn't add new fields.
- **A5**: Responses' steering opt-in flag (`steerable_conversations: bool = False`) stays opt-in; this design does not change deployment-time configuration semantics.

## Docs ↔ Samples Loop *(mandatory IF this spec touches developer-facing guides or samples)*

### Authoritative guides

- `sdk/agentserver/azure-ai-agentserver-core/docs/task-and-streaming-spec.md` — the SOT (language-agnostic). MUST be updated to reflect this design; cleanup sections enumerated in Q17 of `sdk/agentserver/specs/021-narrow-redesign.md`.
- `sdk/agentserver/azure-ai-agentserver-core/docs/durable-task-guide.md` — the developer-facing consolidated guide. MUST be rewritten where it references unsupported concepts (`Task.get`, `Task.options`, `ctx.suspend()`, `ephemeral=False`, `TaskResult`, `TaskStatus`, `async for chunk in task_run`, etc.).

### Authoring sequence

1. Update `task-and-streaming-spec.md` (SOT) first to reflect the durable-task contract — rewrite §26 (resume route), §35a (TaskSnapshot), `TaskResult`/`Suspended` definitions, `payload["output"]` / `payload["error"]` mentions, `ephemeral` parameter, etc. Apply the Q17 cleanup list.
2. Update `durable-task-guide.md` to mechanically reflect the SOT changes; rewrite examples using `ctx.suspend()` to use `return X`; drop the `Task.options()` section; drop the `Task.get` section; fix the stale `async for chunk in task_run` docstring.
3. Author/update tests for FR-001 through FR-077 alongside the guide (per Principle VII — TDD); tests landed RED first.
4. Implementation iterations follow; if a sample comes out wrong, the guide is wrong → fix the guide, re-derive the sample.
5. Audit downstream packages per SC-009.

### Loop completion criterion

A developer following only `durable-task-guide.md` can write a working `@task` or `@multi_turn_task` handler from scratch; every code example in the guide is mechanically reproducible from the documented surface; every sample has a passing E2E test; no behavior the samples rely on lives only in implementation code.

### What goes where

| Knowledge | Lives in |
|---|---|
| Wire contract / state machine / lease rules / record shape | `task-and-streaming-spec.md` (SOT) |
| Developer-facing API surface, decorator semantics, handler patterns, ctx surface, error taxonomy | `durable-task-guide.md` |
| Per-package primitive-selection logic (e.g., responses' matrix dispatch per spec §7) | Downstream package docs (e.g., `azure-ai-agentserver-responses/docs/`) |
| Migration cleanup steps for downstream packages | Downstream package CHANGELOG entries |

## Durability Contract Conformance *(mandatory IF this spec touches code in the durability surface)*

### Exit checklist (Constitution Principle X)

- [ ] **Contract update?** Yes — this spec defines the durable-task primitive's behavior across multiple rows: handler-failure semantic (Q6/FR-010-13), recovery input-source semantic (Q13/FR-033-35), output/error persistence (FR-025-27), and the read-API surface (FR-016-21). The `durability-contract.md` document MUST be amended with a change-log entry covering these rows in the same PR.
- [ ] **Affected rows / paths?** All rows × all paths × `stream=F/T` may exercise the primitive because the handler-failure semantic and `.result()` shape apply uniformly. The update is to the primitive itself, not to a row-specific behavior — the contract document needs a header-level note plus per-row callouts.
- [ ] **Conformance tests added?** Per FR-001 through FR-077; tests landed RED before implementation green per Principle VII.
- [ ] **TDD ordering verified?** Reviewer verifies test-first ordering from commit history.
- [ ] **No synthetic-crash shortcuts?** Tests use real SIGTERM-long-grace / SIGTERM-short-grace / SIGKILL via `_crash_harness`. No mocking, no fabricated `DurabilityContext`, no direct calls to internal failure-marker functions.
- [ ] **Completeness meta-test still passes?** `pytest tests/e2e/durability_contract/test_contract_completeness.py` green.
- [ ] **Dev guide / handler guide updated?** Per the Docs ↔ Samples Loop section above.

## Core Durable-Task Primitive Conformance *(mandatory IF this spec touches the public surface of `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`)*

### Exit checklist (Constitution Principle XII)

- [ ] **Public surface affected?** Yes — this spec defines the durable-task primitive's public surface. Almost every symbol in `azure/ai/agentserver/core/durable/__init__.py` `__all__` is affected (included, excluded, renamed, or specified). Every affected symbol gets a paired conformance test per Principle XII.
- [ ] **Affected symbols enumerated?** Captured comprehensively in `sdk/agentserver/specs/021-narrow-redesign.md` §3 Q17 (consolidated cleanup list). To summarize here:
  - **Included**: `@multi_turn_task` decorator, `multi_turn_task.delete(task_id)` classmethod, `TaskRun.input_id` attribute, multi-turn `get_active_run(task_id, input_id)` signature.
  - **Not included**: `Task.get`, `Task.options`, `TaskResult`, `Suspended`, `TaskSnapshot`, `TaskStatus`, `OutputTooLarge`, `TaskRun.delete`, `TaskRun.refresh`, `TaskRun.status`, `TaskRun.lease_expiry_count`, `ctx.suspend()` (multi-turn), `ephemeral=` arg, `/tasks/resume` route, `handle_resume` method.
  - **Behavior**: `@task` (one-shot-only), `.run()` / `.result()` return type (returns `Output` directly), `get_active_run` (no retrospective attach), multi-turn handler raise (Q6 — chain stays alive), inline-recovery input source (Q13 — persisted wins), queued-steerer behavior on raise (Q14 — promote not reject).
- [ ] **Conformance gap-list document produced?** A `conformance-gap-list.md` will live alongside this spec's directory, mapping each FR to the existing test file that needs extension OR the new test file that needs creation, with justification per case (per FR-030 in Spec 015 successors).
- [ ] **Non-duplication rule satisfied?** Where existing tests in `tests/durable/` cover a surface area already, the change EXTENDS the existing file rather than creating a parallel test.
- [ ] **Conformance tests added?** Every FR has a paired test asserting name, location, presence-in-`__all__`, type, and contract-documented behavior.
- [ ] **TDD ordering verified?** Conformance tests landed RED before implementation green; reviewer verifies test-first ordering from commit history.
- [ ] **No synthetic-bypass shortcuts?** Tests do not monkey-patch `TaskContext` fields, do not instantiate `TaskContext` directly outside framework wiring, do not call internal `_`-prefixed APIs to bypass public-surface enforcement.
- [ ] **Completeness meta-test still passes?** `pytest azure-ai-agentserver-core/tests/durable/test_contract_completeness.py` green.
- [ ] **Consolidated dev guide updated?** `durable-task-guide.md` updated per the Docs ↔ Samples Loop section.

---

## Reference

For the full design history, alternatives considered, and rationale behind each FR, see the living draft at `sdk/agentserver/specs/021-narrow-redesign.md`. Q1 through Q17 in that draft's §3 capture every design decision; §7 covers downstream impact on `azure-ai-agentserver-responses`; §8 is the iteration log.
