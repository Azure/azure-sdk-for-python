# Data Model: Durable Tasks for Long-Running Agents

**Phase 1 Output** — defines entities, fields, relationships, state transitions, and validation rules.

---

## 1. Public Types

### 1.1 `DurableTask[Input, Output]`

The object returned by the `@durable_task` decorator. Not callable directly — use `.run()`, `.start()`, or `.options()`.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Identifies the task function for logging/dashboards. Defaults to `fn.__qualname__`. |
| `_fn` | `Callable[[TaskContext[Input]], Awaitable[Output]]` | The decorated async function (internal). |
| `_defaults` | `DurableTaskOptions` | Frozen options from the decorator (internal). |

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `async def run(*, task_id: str, input: Input, session_id: str \| None = None, **overrides) -> Output` | `Output` | Invoke-and-wait. Creates task, acquires lease, runs function, returns result. |
| `start` | `async def start(*, task_id: str, input: Input, session_id: str \| None = None, **overrides) -> TaskRun[Output]` | `TaskRun[Output]` | Fire-and-forget. Returns handle immediately. |
| `options` | `def options(**overrides) -> DurableTask[Input, Output]` | `DurableTask[Input, Output]` | Returns a new `DurableTask` with merged options (immutable — original unchanged). |

---

### 1.2 `TaskContext[Input]` (Generic)

The single parameter to a durable function. Provides identity, input, metadata, and signals.

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `task_id` | `str` | ❌ | Unique task identifier. |
| `title` | `str` | ❌ | Human-readable title. |
| `session_id` | `str` | ❌ | Session scope. |
| `agent_name` | `str` | ❌ | Agent name from config. |
| `tags` | `dict[str, str]` | ❌ | Merged decorator + call-site tags. |
| `input` | `Input` | ❌ | Typed, validated input. |
| `metadata` | `TaskMetadata` | ✅ | Mutable progress dict. |
| `run_attempt` | `int` | ❌ | Increments on framework-managed retries. |
| `lease_generation` | `int` | ❌ | Increments on each restart-reclamation. |
| `cancel` | `asyncio.Event` | ❌ | Request-level cancellation signal. |
| `shutdown` | `asyncio.Event` | ❌ | Container-level shutdown signal. |

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `suspend` | `async def suspend(*, reason: str \| None = None, output: Output \| None = None) -> Suspended[Output]` | `Suspended[Output]` | Suspends the task, releases lease, persists state. Must be used as `return await ctx.suspend(...)`. |

---

### 1.3 `TaskRun[Output]` (Generic)

Handle returned by `.start()`. Provides external observation and control.

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | Task identifier. |
| `status` | `TaskStatus` | Current status (may require refresh). |
| `metadata` | `TaskMetadata` | Read-only metadata snapshot. |

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `result` | `async def result() -> Output` | `Output` | Awaits task completion and returns the typed output. Raises `TaskFailed` on failure, `TaskSuspended` on suspension. |
| `cancel` | `async def cancel() -> None` | `None` | Signals cancellation to the running task. |
| `delete` | `async def delete() -> None` | `None` | Deletes the task record from the store. |
| `refresh` | `async def refresh() -> None` | `None` | Re-fetches task state from the store, updating `status` and `metadata`. |

---

### 1.4 `TaskMetadata`

Mutable progress dict attached to the task context. Persisted to the task record's `payload`.

| Method | Signature | Description |
|--------|-----------|-------------|
| `set` | `def set(key: str, value: Any) -> None` | Set a key-value pair. |
| `get` | `def get(key: str, default: Any = None) -> Any` | Get a value by key. |
| `increment` | `def increment(key: str, delta: int = 1) -> None` | Atomically increment a numeric value. |
| `append` | `def append(key: str, value: Any) -> None` | Append to a list value. |
| `to_dict` | `def to_dict() -> dict[str, Any]` | Return a snapshot of all metadata. |

**Persistence**: Metadata changes are batched and flushed to the task record via a payload PATCH on a debounced interval (configurable, default 5s). Immediate flush on suspend, complete, or explicit `await ctx.metadata.flush()`.

---

### 1.5 `Suspended[Output]` (Generic)

Sentinel return type from `ctx.suspend()`. Used as `return await ctx.suspend(...)`.

| Field | Type | Description |
|-------|------|-------------|
| `reason` | `str \| None` | Human-readable suspension reason. |
| `output` | `Output \| None` | Optional snapshot for observers. |

---

### 1.6 `TaskStatus` (Literal)

```python
TaskStatus = Literal["pending", "in_progress", "suspended", "completed"]
```

---

### 1.7 Exception Types

| Exception | Inherits | Fields | When Raised |
|-----------|----------|--------|-------------|
| `TaskFailed` | `Exception` | `task_id: str`, `error: dict[str, Any]` | Task function raised an unhandled exception. |
| `TaskSuspended` | `Exception` | `task_id: str`, `reason: str \| None`, `output: Any \| None` | Awaiting a suspended task's result. |
| `TaskCancelled` | `asyncio.CancelledError` | `task_id: str` | Task was cancelled. |
| `TaskNotFound` | `Exception` | `task_id: str` | Task ID not found in the store. |

---

## 2. Internal Types

### 2.1 `DurableTaskManager`

Lifecycle orchestrator. One per `AgentServerHost`. Manages all active tasks.

| Field | Type | Description |
|-------|------|-------------|
| `_provider` | `DurableTaskProvider` | Storage backend (hosted or local). |
| `_config` | `AgentConfig` | Resolved platform config. |
| `_active_tasks` | `dict[str, _ActiveTask]` | Currently running tasks by ID. |
| `_resume_callbacks` | `dict[str, Callable]` | Registered durable task functions by name. |

| Method | Description |
|--------|-------------|
| `async startup()` | Initialize provider, recover stale tasks. |
| `async shutdown()` | Signal shutdown on all active tasks, force-expire leases. |
| `async create_and_run(...)` | Create task, acquire lease, run function, return result. |
| `async create_and_start(...)` | Create task, acquire lease, dispatch function, return handle. |
| `async handle_resume(task_id)` | Re-fetch task, acquire lease, dispatch to resume callback. |

---

### 2.2 `DurableTaskClient`

HTTP client for the Foundry Task Storage API. Internal only.

| Method | HTTP | Path | Description |
|--------|------|------|-------------|
| `async create_task(...)` | `POST` | `/storage/tasks` | Create a new task. |
| `async get_task(task_id)` | `GET` | `/storage/tasks/{id}` | Get a single task. |
| `async update_task(task_id, ...)` | `PATCH` | `/storage/tasks/{id}` | Update status, lease, payload, etc. |
| `async delete_task(task_id, ...)` | `DELETE` | `/storage/tasks/{id}` | Delete a task. |
| `async list_tasks(...)` | `GET` | `/storage/tasks` | List tasks with filters. |

Auth: Bearer token from `DefaultAzureCredential` in hosted mode. None in local mode.

---

### 2.3 `DurableTaskProvider` (Protocol)

Storage abstraction. Structural typing via `typing.Protocol`.

```python
class DurableTaskProvider(Protocol):
    async def create(self, task: TaskCreateRequest) -> TaskInfo: ...
    async def get(self, task_id: str) -> TaskInfo | None: ...
    async def update(self, task_id: str, patch: TaskPatchRequest) -> TaskInfo: ...
    async def delete(self, task_id: str, *, force: bool = False, cascade: bool = False) -> None: ...
    async def list(self, *, agent_name: str, session_id: str, status: TaskStatus | None = None) -> list[TaskInfo]: ...
```

---

### 2.4 `TaskInfo`

Internal representation of a task record from the store.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Task ID. |
| `agent_name` | `str` | Agent scope. |
| `session_id` | `str` | Session scope. |
| `title` | `str \| None` | Human-readable title. |
| `status` | `TaskStatus` | Current status. |
| `lease` | `LeaseInfo \| None` | Active lease details. |
| `payload` | `dict[str, Any] \| None` | Task payload (contains input, metadata, output buckets). |
| `tags` | `dict[str, str] \| None` | Tags. |
| `error` | `dict[str, Any] \| None` | Error details (on failure). |
| `suspension_reason` | `str \| None` | Reason for suspension. |
| `etag` | `str` | Optimistic concurrency token. |
| `created_at` | `str` | ISO 8601 creation timestamp. |
| `updated_at` | `str` | ISO 8601 last update timestamp. |

---

### 2.5 `LeaseInfo`

| Field | Type | Description |
|-------|------|-------------|
| `owner` | `str` | Stable lease owner (e.g., `session:{session_id}`). |
| `instance_id` | `str` | Ephemeral instance identifier. |
| `generation` | `int` | Fencing token — increments on re-acquisition. |
| `expires_at` | `str` | ISO 8601 expiry timestamp. |
| `expiry_count` | `int` | Number of times ownership changed via expiry. |

---

## 3. State Machine

```
                ┌──────────┐                ┌──────────────┐
   POST ───────►│ pending  │ ◄──── PATCH ──►│ in_progress  │ ◄── PATCH renews
                └────┬─────┘   status        └──────┬───────┘
                     │                              │
                     │                              ▼
                     │                       ┌────────────┐
                     │                       │ suspended  │
                     │                       └──────┬─────┘
                     │                              │
                     ▼                              ▼
                ┌────────────────────────────────────┐
                │             completed              │ (terminal)
                └────────────────────────────────────┘
```

### Valid Transitions (SDK-managed)

| From | To | SDK Trigger | API Call |
|------|----|-------------|----------|
| (none) | `in_progress` | `.run()` / `.start()` | `POST /tasks` with lease params and `status: "in_progress"` |
| `in_progress` | `completed` | Function returns normally | `DELETE` (ephemeral) or `PATCH status=completed` (non-ephemeral) |
| `in_progress` | `completed` | Function raises exception | `DELETE` (ephemeral) or `PATCH status=completed + error` (non-ephemeral) |
| `in_progress` | `suspended` | `return await ctx.suspend(...)` | `PATCH status=suspended` |
| `suspended` | `in_progress` | `POST /tasks/resume` (external trigger) | `PATCH status=in_progress` with new lease |
| `in_progress` | `in_progress` | Process restart (dual-identity reclaim) | `PATCH` with new `instance_id` (same `owner`) |

### Transitions NOT managed by SDK (out of scope)

- `pending → in_progress` (tasks are created directly as `in_progress`)
- `in_progress → pending` (requeue — not exposed in convenience API)
- `pending → completed` (no-op resolution — not exposed)

---

## 4. Payload Layout (Convention)

The Task Storage API has a single `payload` field (any JSON, max 1 MB). The convenience layer organizes it into named buckets:

```json
{
  "input": { ... },
  "metadata": { ... },
  "output": { ... }
}
```

| Bucket | Set by | When | Mutable |
|--------|--------|------|---------|
| `input` | Framework | On `POST /tasks` (create) | ❌ Never modified after creation |
| `metadata` | Developer via `ctx.metadata` | During execution (PATCH) | ✅ Shallow-merge PATCH |
| `output` | Framework | On suspend (always), on complete (non-ephemeral only) | ❌ Set once at exit |

The `error` field is stored on the task's top-level `error` property (not inside `payload`).

---

## 5. Relationships

```
AgentServerHost  1──────1  DurableTaskManager
                              │
                              ├── 1  DurableTaskProvider (protocol)
                              │       ├── HostedDurableTaskProvider (httpx → API)
                              │       └── LocalFileDurableTaskProvider (filesystem)
                              │
                              ├── *  _ActiveTask (in-memory tracking)
                              │       ├── TaskContext[Input]
                              │       ├── asyncio.Task (execution)
                              │       └── asyncio.Task (lease renewal)
                              │
                              └── *  resume_callbacks (name → fn)

DurableTask[I, O]  ──uses──▶  DurableTaskManager  (via host reference)
TaskRun[O]         ──uses──▶  DurableTaskManager  (via handle methods)
```

---

## 6. Validation Rules

| Rule | Location | Error |
|------|----------|-------|
| `task_id` must be 1-256 chars, `[a-zA-Z0-9\-_.:]+` | `DurableTask.run/start` | `ValueError` |
| Input must be JSON-serializable | `DurableTask.run/start` | `TypeError` |
| Pydantic input must pass model validation | `DurableTask.run/start` | `pydantic.ValidationError` |
| Decorated function must be `async def` | `@durable_task` (decoration time) | `TypeError` |
| Decorated function must accept exactly one `TaskContext[T]` param | `@durable_task` (decoration time) | `TypeError` |
| `lease_duration_seconds` must be ≥ 1 | `@durable_task` / `.options()` | `ValueError` |
| `metadata` key must be a string | `TaskMetadata.set/get/increment/append` | `TypeError` |
| `metadata.increment` value must be numeric | `TaskMetadata.increment` | `TypeError` |
| `metadata.append` target must be a list (or absent) | `TaskMetadata.append` | `TypeError` |
