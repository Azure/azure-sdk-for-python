# Data Model: Durable-task primitive contract hardening (Phase 1)

The durable-task primitive is a Python SDK library; it has no entity-relationship model in the database-design sense. Its "model" is two surfaces:

1. **The public-API contract** — `TaskContext`, `TaskResult`, `Task`, `TaskRun`, `TaskManager`, `EntryMode`, exception classes. Enumerated in [`./spec.md`](./spec.md) §Core Durable-Task Primitive Conformance §Affected public symbols; this artifact does not duplicate that.
2. **The persisted record shape** — the structure of the task record stored in the task-store (Foundry hosted store or the local file-based provider), including the fields this spec adds/changes.

This artifact captures (2).

---

## Persisted record — fields changed or added by this spec

The task-store schema is owned by the platform. The fields below are all in the `payload` sub-object of the record (per the existing convention: top-level keys prefixed with `_` are primitive-reserved per spec 015).

### `_turn_started_at` (NEW; FR-023)

- **Purpose**: Durable wall-clock anchor for the per-turn timeout budget. The watchdog computes `remaining = max(0, opts.timeout - (now - _turn_started_at))` on every (re-)spawn.
- **Type**: ISO-8601 UTC timestamp string (e.g., `"2026-06-01T20:11:00.123456+00:00"`).
- **Location**: `payload["_turn_started_at"]` (top-level, per the spec-015 `_` prefix convention). Field name is a plan-phase decision; an alternative location is inside `payload["_lease"]` if that's structurally cleaner. The contract is "present and durable at every turn-start boundary".
- **Set sites**: every store write that transitions the record's status into `in_progress` for a NEW turn:
  - Fresh `.run()` / `.start()` on a fresh task (initial create write).
  - Resume from `suspended` → `in_progress` (developer initiated via `.run()`).
  - Steering drain re-entry (same CAS write that bumps `_steering["generation"]`).
- **Set sites that MUST NOT re-stamp**: recovery (re-entering an `in_progress` record with `entry_mode == "recovered"`) — recovery is mid-turn; the existing value is preserved so the recovered watchdog sees the remaining budget.
- **Read sites**: the framework only — read at watchdog (re-)spawn time. Never on the public `TaskInfo` surface.
- **Fallback**: if the field is absent (legacy records during the rollout window), fall back to `remaining = opts.timeout.total_seconds()` + DEBUG log.

### `_steering` payload subsection (EXISTING; modified by FR-013/14/15)

The pre-existing `_steering` payload subsection carries:
- `pending_inputs: list[Any]` — FIFO queue of steering inputs awaiting drain. UNCHANGED in shape; the public surface change is to remove `ctx.pending_inputs` and add `ctx.pending_input_count` (which reads from the in-memory tracker, NOT from this field directly).
- `active_input: Any` — the input currently being processed by the handler. UNCHANGED.
- `generation: int` — monotonically increasing per drain. UNCHANGED in this spec; FR-021 only drops the public `ctx.steering_generation` field. Plan-phase decision: whether to delete the internal field entirely (deferred per Decision 11 in `research.md`).
- `cancel_requested: bool` — internal flag the drain code path uses to decide whether to pre-set `ctx.cancel` on the new generation. UNCHANGED. (Note: this internal name is unrelated to the NEW PUBLIC `ctx.cancel_requested` boolean which is set by `TaskRun.cancel()`.)
- `drain_in_progress: bool` — guard to detect crash-mid-drain on recovery. UNCHANGED.
- **REMOVED**: any `generation_results` field (already removed per spec 013 US4 scenario 11 work; restated here as not-coming-back).

### Lease metadata (EXISTING; semantics change per FR-004a)

The pre-existing `lease` sub-object carries:
- `owner: str` — the stable lease owner. **Format changes** per FR-004a from `"session:{session_id}"` to a format incorporating both `agent_name` (from `FOUNDRY_AGENT_NAME`) and `session_id`. Concrete format is a plan-phase decision: candidates are `"{agent_name}:{session_id}"`, `"agent={agent_name};session={session_id}"`, or similar. The contract is "both components present and stable across process restarts within the same (agent, session) pair".
- `instance_id: str` — ephemeral per-process identifier; CHANGED on every process restart. UNCHANGED in this spec.
- `expires_at: str` — ISO-8601 UTC expiry timestamp. UNCHANGED.
- `generation: int` — monotonic per (re-)claim. UNCHANGED.
- `expiry_count: int` — count of past lease expiries. UNCHANGED.

### Terminal records — payload `pending_inputs` cleanup (FR-012)

When the handler terminates (return or raise) with steering inputs queued, the SAME store write that records the terminal transition MUST also clear `payload["_steering"]["pending_inputs"]`. The framework MUST then resolve each queued steerer's `TaskRun.result()` future with `TaskConflictError(current_status="completed" | "failed")`. This is one store write, one consistent state — not two writes that could race.

---

## Public-surface contract (cross-reference)

The full public-surface contract is enumerated in `spec.md` §Core Durable-Task Primitive Conformance §Affected public symbols. Quick reference grouped by category:

| Category | Symbol | Status |
|---|---|---|
| Removed | `@task(stale_timeout=...)`, `Task.options(stale_timeout=...)`, `TaskOptions.stale_timeout` | FR-001 |
| Removed | `TaskResult.status == "superseded"`, `TaskResult.is_superseded` | FR-010 |
| Removed | `TaskRun.terminate()`, `TaskTerminated` | FR-022 |
| Removed | `ctx.pending_inputs`, `ctx.was_steered`, `ctx.steering_generation` | FR-019, FR-020, FR-021 |
| Added | `ctx.timeout_exceeded: bool`, `ctx.cancel_requested: bool`, `ctx.pending_input_count: int`, `ctx.is_steered_turn: bool` | FR-016..FR-021 |
| Added | `TaskContext.exit_for_recovery()` | FR-027 |
| Behavior-changed | `TaskManager.get_active_run(task_id)` (now consults store + inline reclaim) | FR-005 |
| Behavior-changed | `derive_lease_owner(...)` signature (agent + session) | FR-004a |
| Behavior-changed | `@task(timeout=...)` semantic (per-turn / wall-clock / durable / cooperative-only) | FR-023..FR-026 |
| Behavior-changed | `TaskRun.cancel()` (handler owns terminal shape) | FR-022 |
| Behavior-changed | `HostedTaskProvider.__init__` (`credential` re-typed to `AsyncTokenCredential`; bodies rewritten on pipeline) | FR-029..FR-034 |
| Unchanged | `ctx.cancel` (bare `asyncio.Event`), `ctx.shutdown` (separate bare `asyncio.Event`), `EntryMode` Literal values | — |

---

## Validation rules

The persisted-record validations the framework MUST enforce (in addition to whatever the task-store API itself validates):

- `_turn_started_at` MUST parse as ISO-8601 UTC if present. If unparseable, the framework logs ERROR and falls back to `remaining = opts.timeout.total_seconds()` (same as the absent-field case).
- Lease `owner` string parses into agent and session components consistently with `derive_lease_owner(agent, session)`. Records with an unparseable or legacy-format owner are considered orphan-ownership; the standard recovery path applies.
- On terminal transition with queued `pending_inputs`, the write MUST be atomic (single CAS PATCH) — no transient state in the store where status is terminal and inputs are still pending. The framework MUST verify the write was atomic via etag in the success path.

These validations live in the framework, not on the store. The store's existing schema validations are unchanged.

---

## State transitions affected

| Transition | Before this spec | After this spec |
|---|---|---|
| Fresh `.run()` / `.start()` | Creates record with `status="in_progress"`, lease owner `"session:{session_id}"` | Same record shape PLUS `_turn_started_at` stamp; lease owner now incorporates agent name |
| Suspend → resumed (developer-initiated `.run()`) | Status `suspended` → `in_progress` | Same PLUS `_turn_started_at` re-stamp (fresh turn) |
| Steering drain re-entry | Status remains `in_progress`; `_steering.generation++` | Same PLUS `_turn_started_at` re-stamp (drain re-entry is a new turn per FR-023) |
| Crash recovery (mid-turn) | Status `in_progress` (preserved); lease reclaimed | Same PLUS `_turn_started_at` NOT re-stamped (recovery is mid-turn); `entry_mode="recovered"` set on the recovered context |
| Terminal (return / raise) | Status → `completed` or `failed`; lease released | Same PLUS atomic clearing of `_steering.pending_inputs` if non-empty; queued steerers' futures resolve `TaskConflictError` |
| Shutdown via `ctx.exit_for_recovery()` | (didn't exist) | Status remains `in_progress`; lease released; in-process awaiter signaled; metadata flushed |
| Eviction (`binding_mismatch`) | (silent failure on the renewal loop) | Caller-observable per Invariant 1 (caller sees `TaskConflictError` from `.run()`/`.start()` or `None` from `get_active_run()`); operator WARNING log |

---

## Out of scope for this artifact

- Database schema migration scripts — not applicable (pre-release; no production data; legacy records during rollout are orphan-ownership and reclaimed by standard recovery).
- API request/response schemas of the task-store — owned by the platform; not in this spec's scope.
- In-memory dataclasses on `TaskManager` (e.g., `_ActiveTask`) — implementation detail; concrete shape decided during `/speckit.tasks`.
