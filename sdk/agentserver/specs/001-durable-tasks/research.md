# Research: Durable Tasks for Long-Running Agents

**Phase 0 Output** — resolves all technical unknowns from the plan.

---

## R-1: HTTP Client for Task Storage API

**Decision**: Use `httpx.AsyncClient` for all HTTP calls to the Foundry Task Storage API.

**Rationale**: The core package currently uses `starlette` (ASGI framework) but has no outbound HTTP client dependency. `httpx` is the de-facto standard async HTTP client for Python, provides first-class `async/await` support, has excellent timeout and retry control, supports transport-level injection for testing (via `ASGITransport`), and is already a transitive dependency via `starlette`'s test utilities. It is also the recommended client for Azure-style auth token injection via `Authorization: Bearer` headers.

**Alternatives considered**:
- `aiohttp` — heavier, different API style, would be a new paradigm alongside starlette
- `azure.core.pipeline` — full Azure SDK HTTP pipeline; too heavy for internal wire-level calls that don't need the full policy chain
- `urllib3` — sync-only, incompatible with async-first design

---

## R-2: Authentication in Hosted Mode

**Decision**: Use `azure.identity.aio.DefaultAzureCredential` with scope `https://ai.azure.com/.default` to obtain bearer tokens for the Task Storage API.

**Rationale**: The container spec mandates `DefaultAzureCredential` for hosted environments. The managed identity in the Foundry hosting environment provides a token automatically. The SDK already has `azure-identity` as a dependency in the broader Azure SDK ecosystem.

**Dependency note**: `azure-identity` will be an optional dependency — imported lazily at runtime when `is_hosted=True`. Local mode uses no auth.

**Alternatives considered**:
- Manual token acquisition via IMDS — lower-level, more code, no added value over DefaultAzureCredential
- API key auth — not supported by the Task Storage API

---

## R-3: Lease Renewal Mechanism

**Decision**: Use `asyncio.Task` with a simple `asyncio.sleep` loop running at half the lease duration (30s for the default 60s TTL). The renewal task is cancelled on completion, suspension, or shutdown.

**Rationale**: The Python `asyncio` event loop is already the execution context for the ASGI server. An `asyncio.Task` is the lightest-weight mechanism for periodic background work. The half-TTL interval provides a safety margin — even if one renewal fails, the next attempt fires before the lease expires.

**Error handling**: Lease renewal failures are logged at WARNING level. After 3 consecutive failures, the framework signals `ctx.cancel` to give the function a chance to checkpoint. The lease is not forcibly released — if the TTL expires, the dual-identity reclaim mechanism handles recovery.

**Alternatives considered**:
- `threading.Timer` — violates async-first constitution principle, thread-unsafe with asyncio
- External scheduler (APScheduler) — overkill, new dependency, unnecessary for a single timer

---

## R-4: Local Filesystem Provider Architecture

**Decision**: Implement `LocalFileDurableTaskProvider` using JSON files under `$HOME/.durable-tasks/{agent_name}/{session_id}/`. Each task is a single JSON file named `{task_id}.json`. A file lock (`fcntl.flock` on Linux, `msvcrt.locking` on Windows) prevents concurrent access in multi-process local scenarios.

**Rationale**: The container spec defines `$HOME` as durable per-session storage. JSON files are human-readable, debuggable, and require no external dependencies. The directory structure mirrors the API's `(agent_name, session_id)` scoping. File locking provides minimal concurrency safety for developers who run multiple local processes.

**Lease simulation**: The local provider stores `lease.expires_at` as an ISO timestamp. On reads, expired leases are treated as released. This gives full parity with the hosted API's lease semantics without a background expiry process.

**Alternatives considered**:
- SQLite — adds complexity, harder to inspect/debug, overkill for local dev
- In-memory dict — doesn't survive process restart, defeats the purpose of durability testing

---

## R-5: Provider Abstraction Design

**Decision**: Define a `DurableTaskProvider` `Protocol` class with async methods matching the Task Storage API operations (create, get, update, delete, list). The `DurableTaskManager` holds a provider reference and delegates all storage operations through it.

**Rationale**: The Protocol pattern (PEP 544) enables structural typing — any class implementing the right methods satisfies the protocol without inheriting. This is idiomatic Python and follows the existing patterns in the codebase (no heavy ABC inheritance trees). Two implementations: `HostedDurableTaskProvider` (HTTP → Task Storage API) and `LocalFileDurableTaskProvider` (filesystem).

**Provider selection**: Automatic based on `AgentConfig.is_hosted` — set by the `FOUNDRY_HOSTING_ENVIRONMENT` env var (already resolved in `_config.py`).

---

## R-6: Decorator Return Type and Task Registration

**Decision**: `@durable_task` returns a `DurableTask[Input, Output]` object. This object is not callable directly — the developer uses `.run(...)` or `.start(...)`. The `DurableTask` type is generic, carrying the input and output types from the decorated function's signature.

**Rationale**: The container spec explicitly states that the decorator returns a typed wrapper, not a callable. This prevents confusion between "I'm running my function locally" and "I'm running a durable task". The `.run(...)` and `.start(...)` methods make the execution mode explicit.

**Type extraction**: At decoration time, the framework inspects the function's type annotations to extract `Input` from `TaskContext[Input]` and `Output` from the return type. This enables generic type checking (e.g., `.run()` returns `Output`).

---

## R-7: Resume Route Integration

**Decision**: The `POST /tasks/resume` route is auto-registered on the `AgentServerHost` when durable tasks are enabled. The route handler receives the task ID from the request body, re-fetches the task from the store, acquires a new lease, and dispatches it to the registered resume callback.

**Response**: Empty body. Status codes:
- `202 Accepted` — resume dispatched successfully
- `404 Not Found` — task ID not found or not in a resumable state
- `409 Conflict` — task is already in progress (lease held)

**Integration point**: The `AgentServerHost._base.py` already supports route registration via the Starlette `Route` list. The durable task subsystem adds its route during host startup.

---

## R-8: Shutdown Coordination

**Decision**: Hook into the existing `AgentServerHost` shutdown lifecycle (SIGTERM handler in `_base.py`). On shutdown:
1. Signal `ctx.shutdown` event on all active task contexts
2. Wait up to the graceful shutdown timeout for tasks to checkpoint
3. Force-expire all active leases (PATCH with `lease_duration_seconds=0`)
4. Allow the ASGI server to drain

**Rationale**: The existing `_base.py` already handles SIGTERM and configurable graceful shutdown timeout. The durable task subsystem registers a shutdown callback via the existing `_shutdown_fn` slot.

---

## R-9: Input Serialization Strategy

**Decision**: Support three input types:
1. **Pydantic models** (preferred) — `model_dump()` for serialization, `model_validate()` for deserialization
2. **Dataclasses** — `dataclasses.asdict()` for serialization, constructor for deserialization
3. **Plain types** (str, int, dict, list) — JSON-serializable as-is

Detection is automatic via type inspection at decoration time.

**Rationale**: The spec says "favours Pydantic models because they validate at the boundary" but the implementation should be pragmatic — not all developers use Pydantic. Dataclasses are in the stdlib. Plain types are useful for simple tasks.

---

## R-10: Concurrency Model — Single Active Task vs. Multiple

**Decision**: Support multiple concurrent durable tasks per process. Each task gets its own `asyncio.Task` for execution and its own lease renewal loop. The `DurableTaskManager` tracks all active tasks by ID.

**Rationale**: While the typical case is one task per invocation, the spec allows multiple. A developer might start a primary task and spawn helper tasks. The manager must track all of them for proper shutdown coordination.

**Constraint**: All tasks within a process share the same `lease_owner` (derived from `session_id`). Each task has a unique `lease_instance_id`.
