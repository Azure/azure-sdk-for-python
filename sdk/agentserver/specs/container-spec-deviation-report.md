# Container Spec Deviation Report

> **Purpose:** Feed this document alongside [PR #46839](https://github.com/Azure/azure-sdk-for-python/pull/46839) to update `durable-task-convenience-api.md` in the specs repo.
>
> **Container spec:** `specs/hosted-agents/container-spec/docs/durable-task-convenience-api.md`
>
> **SDK implementation:** `sdk/agentserver/azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`

---

## 1. Implemented as Speced

These items match the container spec and need no changes:

| Item | Spec Ref | Notes |
|---|---|---|
| `@durable_task` decorator as primary surface | §2.1 | ✓ |
| `title` option (`str \| Callable`) | §2.1 | ✓ |
| `tags` option (static dict) | §2.1 | ✓ (also extended — see §3) |
| `retry` option | §2.1 | ✓ (shape differs — see §2i) |
| `timeout` option | §2.1 | `timedelta \| None`, default `None` ✓ |
| `lease_duration_seconds` | §2.1 | `int`, default `60` ✓ |
| `store_input` | §2.1, §3.2 | `bool`, default `True` ✓ |
| `ephemeral` | §2.1, §8 | `bool`, default `True` ✓ |
| `task.start(...)` fire-and-forget | §4.1 | Returns `TaskRun` handle ✓ |
| `task.run(...)` invoke-and-wait | §4.2 | ✓ (return type differs — see §2b) |
| `.options(...)` per-call overrides | §2.3 | ✓ |
| `TaskRun.task_id` | §4.1 | ✓ |
| `TaskRun.cancel(reason=)` | §4.1, §9 | ✓ |
| `TaskRun.terminate(reason=)` | §4.1, §9 | ✓ |
| `TaskRun.result()` | §4.1 | ✓ (return type differs) |
| `TaskContext.task_id` | §5 | ✓ |
| `TaskContext.title` | §5 | ✓ |
| `TaskContext.session_id` | §5 | ✓ |
| `TaskContext.tags` | §5 | ✓ |
| `TaskContext.input` (immutable, typed) | §5, §3.1 | ✓ |
| `TaskContext.run_attempt` | §5 | ✓ |
| `TaskContext.cancel` (`asyncio.Event`) | §5, §9.1 | ✓ |
| `ctx.suspend(reason=, output=)` | §5, §8.2 | Core mechanism ✓ (sentinel differs) |
| Streaming output | §7 | Present ✓ (API shape differs) |
| Success = `return value` | §8.1 | ✓ |
| Failure = unhandled exception | §8.3 | ✓ |
| `TaskFailed` on failure | §8.3 | ✓ |
| `TaskCancelled` on cancel | §8.3 | ✓ |
| `TaskTerminated` on terminate | §8.3 | ✓ |
| Hard-cancel grace period (5s default) | §9.1 | ✓ (now explicit via `cancel_grace_seconds`) |
| `store_input=False` → input unavailable on restart | §3.2 | ✓ |
| `ctx.shutdown` event | §5, §9.2 | `asyncio.Event` on `TaskContext` ✓ |
| `ctx.agent_name` | §5 | `str` on `TaskContext` ✓ |
| `ctx.lease_generation` | §5 | `int` on `TaskContext`, plumbed from task store lease info ✓ |
| `TaskMetadata` rich API (`.set()`, `.increment()`, `.append()`) | §5, §6.2 | Implemented in `_metadata.py` with debounced auto-flush ✓ |
| `TaskMetadata` dict protocol (`[]`, `in`, `for`, `len`, `del`) | §6.2 | MutableMapping virtual subclass with dirty-tracking ✓ |
| `handle.metadata` snapshot read | §4.1, §6.2 | `TaskRun.metadata` property + `refresh()` from store ✓ |
| `handle.delete()` | §4.1 | `TaskRun.delete()` removes task record from store ✓ |

---

## 2. Deviations (by Design)

These are deliberate changes from the spec. The spec should be updated to reflect these decisions.

### 2a. `run()` / `result()` return `TaskResult[Output]`, not raw `Output` — §4.2, §8

- **Spec:** `run()` returns raw `Output`; raises `TaskSuspended[OutputSnapshot]` on suspend.
- **Impl:** Returns `TaskResult[Output]` with `.output`, `.status`, `.is_suspended`, `.is_completed`, `.suspension_reason`, `.task_id`.
- **Rationale:** Suspension is a normal outcome for multi-turn agents — making it an exception is awkward when it's the expected path. A result wrapper with discriminated state is more Pythonic. Failures/cancel/terminate remain exceptions because they are genuinely exceptional.
- **Spec update needed:** Replace `TaskSuspended` exception on `run()`/`result()` with `TaskResult` return. Remove the `TaskSuspended` exception class from §4.2 and §8.2 tables.

### 2b. No `TaskOutcome` / `completion()` — §4.1

- **Spec:** `completion()` returns `TaskOutcome[Output]` (discriminated union: `Completed | Failed | Suspended | Terminated`).
- **Impl:** Replaced entirely by `TaskResult[Output]` on `result()`.
- **Rationale:** `TaskResult` covers the `Completed` and `Suspended` branches; `Failed`, `Cancelled`, and `Terminated` are raised as exceptions. This eliminates a 4-branch union type and simplifies consumer code.
- **Spec update needed:** Remove `completion()` method and `TaskOutcome` type from §4.1 `TaskRun` surface.

### 2c. No function-style API (`app.tasks.run(fn=...)`) — §2.2

- **Spec:** Ad-hoc invocation via `app.tasks.run(task_id=..., fn=quick_query, ...)`.
- **Impl:** Removed entirely.
- **Rationale:** Conflates registration and execution, creates ambiguity around lifecycle ownership, and couples tasks to the `app` host. `@durable_task` already works as a plain function call (not just as a decorator), so this second entry point adds near-zero value.
- **Spec update needed:** Remove §2.2 entirely. Update §2 intro ("Both surfaces produce the same lifecycle" → single surface). Remove `app.tasks.run/start` references throughout.

### 2d. No `wait_timeout` on `run()` — §4.2

- **Spec:** `run(..., wait_timeout=timedelta)` → raises `TaskWaitTimeout` on timeout.
- **Impl:** Not present.
- **Rationale:** Confusing alongside the decorator's `timeout` option. Callers who need bounded waiting use `.start()` and wrap `result()` in `asyncio.wait_for()`.
- **Spec update needed:** Remove `wait_timeout` from `run()` signature and `TaskWaitTimeout` exception. Add note about `asyncio.wait_for` pattern.

### 2e. `get_handle` → `task.get()` — §4.3

- **Spec:** `app.tasks.get_handle(task_id, DurableTaskType=process_turn)`.
- **Impl:** `my_task.get(task_id)` on the `DurableTask` object directly.
- **Rationale:** Scoping the lookup to the specific task type is safer (type-checked) and avoids requiring the caller to pass the type explicitly. Eliminates the `app.tasks` coupling.
- **Spec update needed:** Replace `app.tasks.get_handle(...)` with `task.get(task_id)` pattern.

### 2f. Streaming: single-chunk push, not named-stream tee — §7

- **Spec:** `ctx.stream("key", iterable)` tees an async iterable into a named stream; subscribers via `handle.stream("key")`.
- **Impl:** `ctx.stream(chunk)` pushes one chunk at a time; consumers do `async for chunk in handle`.
- **Rationale:** Single-stream model is simpler and matches real usage (one output stream per task). Named streams add routing complexity without a proven use case. The tee pattern implies buffering/replay, which conflicts with the "not persisted" design intent.
- **Spec update needed:** Replace §7.3 named-stream API with single-stream `ctx.stream(chunk)` / `async for chunk in handle` pattern.

### 2g. `ctx.suspend()` does not return `Suspended` sentinel — §5, §8.2

- **Spec:** `return await ctx.suspend(...)` returns a `Suspended[Output]` sentinel; framework inspects the return value.
- **Impl:** `await ctx.suspend(reason=, output=)` — the framework handles the exit internally (sets result future, never returns to user code).
- **Rationale:** The sentinel pattern is fragile — forgetting the `return` in `return await ctx.suspend(...)` silently breaks the suspend flow. Having `suspend()` handle the exit directly is safer.
- **Spec update needed:** Remove `Suspended[Output]` sentinel type. Update §8.2 to show that `ctx.suspend()` terminates execution (does not return).

### 2h. `RetryPolicy` shape — §8.3

- **Spec:** `RetryPolicy(backoff=ExponentialBackoff(initial=..., factor=...), retry_on=(...))`.
- **Impl:** `RetryPolicy(initial_delay=, backoff_coefficient=, max_delay=, max_attempts=, retry_on=, jitter=)` with factory methods `.exponential_backoff()`, `.fixed_delay()`, `.linear_backoff()`, `.no_retry()`.
- **Rationale:** Flat parameter list with preset factories is more ergonomic than nested backoff strategy objects.
- **Spec update needed:** Replace `RetryPolicy` + `ExponentialBackoff` with flat `RetryPolicy` and factory constructors.

---

## 3. Additions (not in spec)

These features were implemented but have no corresponding spec section. The spec should be updated to include them.

### 3a. `tags` callable factory — extends §2.1

- **Impl:** `tags: dict[str, str] | Callable[[Any, str], dict[str, str]]`
- **Purpose:** Compute tags from `(input, task_id)` at task creation time for dynamic routing/labeling (e.g., tag by tenant, model, priority).
- **Spec update needed:** Update §2.1 decorator options table: `tags` type from `dict[str, str]` to `dict[str, str] | Callable[[Input, task_id], dict[str, str]]`.

### 3b. `description` option — new

- **Impl:** `description: str | Callable[[Any, str], str | None] | None`
- **Purpose:** Human-readable task description for observability/UI tooling. Static string or callable factory receiving `(input, task_id)`.
- **Spec update needed:** Add `description` row to §2.1 decorator options table.

### 3c. `source` option — new

- **Impl:** `source: dict[str, Any] | None`
- **Purpose:** Immutable provenance metadata linking the task to its originating system, model version, batch ID, etc. Set at decorator level or overridden at call site.
- **Spec update needed:** Add `source` row to §2.1 decorator options table. Update §11.1 persistence mapping to show `source` on the task record.

### 3d. `cancel_grace_seconds` as explicit option — extends §9.1

- **Spec:** Mentions hard-cancel grace period (default 5s) in prose.
- **Impl:** `cancel_grace_seconds: float = 5.0` as an explicit decorator option.
- **Spec update needed:** Add `cancel_grace_seconds` row to §2.1 decorator options table.

### 3e. `TaskResult[Output]` class — new

- **Impl:** Generic result wrapper: `task_id`, `output`, `status: Literal["completed", "suspended"]`, `suspension_reason`, plus `is_suspended` / `is_completed` properties.
- **Purpose:** Replaces exception-based suspension handling (see §2b).
- **Spec update needed:** Add `TaskResult` to §4.2 and §8 as the return type of `run()` / `result()`.

### 3f. `TaskMetadata` dict-like protocol — extends §6.2

- **Impl (planned):** `TaskMetadata` will support `__setitem__`, `__getitem__`, `__iter__`, `__len__`, `__contains__`, `keys()`, `values()`, `items()` in addition to `.set()`, `.increment()`, `.append()`.
- **Purpose:** Natural dict syntax (`ctx.metadata["phase"] = "summarizing"`, `for k in ctx.metadata`) while preserving dirty-tracking and auto-flush.
- **Spec update needed:** Update §6.2 to document `TaskMetadata` as implementing `MutableMapping`-like protocol.

---

## 4. To Be Removed from Spec

These items are in the container spec but were deliberately rejected. The spec should remove them.

### 4a. `ctx.deadline(timedelta)` context manager — §9.3

- Trivial sugar over `asyncio.wait_for` — not worth framework complexity.
- Developers compose `ctx.cancel` with stdlib `asyncio.timeout` or `asyncio.wait_for` directly.
- **Spec action:** Remove §9.3 and the `ctx.deadline(...)` helper.

### 4b. `ctx.lease_expiry_count` — §5

- Low-value observability counter with no natural home in the current model.
- `lease_generation` (already implemented) is sufficient for restart-recovery awareness.
- Lease expiry details belong in operational logs, not the task context API.
- **Spec action:** Remove `lease_expiry_count` from §5 `TaskContext` definition.

### 4c. Named streams `ctx.stream("key", iterable)` / `handle.stream("key")` — §7.3

- No proven use case for multiple named streams per task.
- Single anonymous stream (`ctx.stream(chunk)` / `async for chunk in handle`) covers the primary LLM token streaming use case.
- Named streams add routing complexity and imply buffering/replay semantics that conflict with the "not persisted" design intent.
- **Spec action:** Replace §7.3 named-stream API with single-stream `ctx.stream(chunk)` / `async for chunk in handle`. Remove `handle.stream("key")` subscriber.

### 4d. Pydantic/dataclass boundary validation — §3.1

- Automatic dict-to-model coercion at the boundary adds a hard dependency on Pydantic.
- Developers can validate in their task function body if needed.
- The framework should remain serialization-agnostic.
- **Spec action:** Remove dict-to-model coercion language from §3.1. Keep the recommendation to use Pydantic but remove any implication the framework performs coercion.

### 4e. `handle.metadata.subscribe()` live updates — §6.2

- Spec proposes `async for snapshot in handle.metadata.subscribe()` for push-based live progress.
- Overkill for the use case — callers can poll `handle.metadata` on demand.
- Live subscription implies a persistent connection, relay infrastructure, and backpressure semantics that add significant complexity.
- **Spec action:** Remove `handle.metadata.subscribe()` from §6.2. Keep `handle.metadata` as a one-shot snapshot read.

---

## 5. Not Yet Implemented

All items from the original backlog have been implemented. No remaining gaps.

---

## 6. Open Questions Resolved (§14)

> All three open questions from §14 of the spec have been resolved.

| # | Spec Open Question | Resolution in Implementation |
|---|---|---|
| 1 | Ephemeral handle behaviour from different process | `task.get(task_id)` returns a typed handle. Ephemeral task visibility across processes depends on the backing store — no special error type added. |
| 2 | Stream multi-subscriber semantics | Simplified to single anonymous stream with `async for chunk in handle`. Each handle gets its own async iterator. No named-stream fan-out to design for. |
| 3 | `task.run()` blocking on suspend | **Resolved cleanly:** `run()` returns `TaskResult` with `is_suspended=True` instead of raising `TaskSuspended`. Suspension is a normal return, not a blocking + exception pattern. This is the cleanest answer to the spec's own question. |

---

## Summary of Spec Updates Needed

### Remove from spec
1. **Remove §2.2** (function-style API) — single decorator surface only
2. **Remove `TaskOutcome` / `completion()`** from §4.1 — replaced by `TaskResult`
3. **Remove `wait_timeout`** from `run()` and `TaskWaitTimeout` exception (§4.2)
4. **Remove `Suspended` sentinel** type — `ctx.suspend()` handles exit directly (§8.2)
5. **Remove §9.3** (`ctx.deadline()`) — trivial sugar, developers use `asyncio.wait_for`
6. **Remove `lease_expiry_count`** from §5 `TaskContext` — `lease_generation` suffices
7. **Remove named streams** from §7.3 — replace with single-stream `ctx.stream(chunk)` API
8. **Remove Pydantic boundary coercion** from §3.1 — framework stays serialization-agnostic
9. **Remove `handle.metadata.subscribe()`** from §6.2 — one-shot snapshot read only, no live push

### Update in spec
9. **Replace `TaskSuspended` exception** with `TaskResult[Output]` return type on `run()`/`result()` (§4.2, §8.2)
10. **Update `get_handle`** → `task.get(task_id)` (§4.3)
11. **Simplify streaming** to `ctx.stream(chunk)` / `async for chunk in handle` (§7.3)
12. **Flatten `RetryPolicy`** — remove nested `ExponentialBackoff`, add factory methods (§8.3)

### Add to spec
13. **Add new decorator options** to §2.1 table: `description`, `source`, `cancel_grace_seconds`, callable `tags`
14. **Add `TaskResult` class** documentation (new section or update §4.2)

### Housekeeping
15. **Close open questions** in §14 (all three resolved)
