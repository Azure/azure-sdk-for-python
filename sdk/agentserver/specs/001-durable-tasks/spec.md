# Feature Specification: Durable Tasks for Long-Running Agents

**Feature Branch**: `feat/durable-tasks`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Convenience APIs for durable long-running agent tasks — crash-resilient execution with automatic lease management, recovery, and graceful shutdown. Based on the Foundry Task Storage protocol spec."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Run agent work as a crash-safe durable task (Priority: P1)

A developer building a long-running agent (multi-step reasoning, tool chains, research loops) needs their work to survive container crashes, OOM kills, and redeployments. They decorate an async function with `@durable_task` and the framework handles task registration, lease management, automatic renewal, and cleanup — the developer writes only their business logic.

**Why this priority**: This is the foundational capability. Without crash-safe task execution, every other feature is moot. A developer who can turn `async def work(ctx) -> Result` into a durable unit of work has the minimum viable product.

**Independent Test**: A developer decorates a function, invokes it with `.run(...)`, and receives the typed result. If the process is killed mid-execution, restarting the process automatically recovers and re-runs the function from scratch (or from a checkpoint if the developer saved one).

**Acceptance Scenarios**:

1. **Given** a function decorated with `@durable_task`, **When** the developer calls `task.run(task_id=..., input=...)`, **Then** the framework creates a task in the Foundry Task Storage API, acquires a lease, runs the function, and deletes the task on success — returning the typed result.
2. **Given** a durable task is running, **When** the container crashes mid-execution, **Then** on restart the framework detects the stale task (via dual-identity lease reclamation), re-acquires the lease, and dispatches the function to the resume callback.
3. **Given** a durable task function raises an unhandled exception, **When** no retry policy is configured, **Then** the framework marks the task as completed with a structured error and the caller receives a `TaskFailed` exception.
4. **Given** a durable task is running, **When** `SIGTERM` is received, **Then** the framework signals the `ctx.shutdown` event, force-expires all active leases, and exits — leaving tasks recoverable by the next container instance.

---

### User Story 2 — Suspend and resume tasks for human-in-the-loop workflows (Priority: P2)

A developer building a multi-turn agent with human approval steps needs to pause execution, release the container's resources, and resume later when external input arrives. The developer calls `ctx.suspend(reason=...)` inside their function and the framework handles lease release, state persistence, and re-entry when triggered.

**Why this priority**: Suspend/resume is the key differentiator for interactive agents. Many real-world agents need human approval, external data, or user replies before continuing. Without this, developers must hand-roll complex state machines.

**Independent Test**: A developer suspends a running task with a reason, the container can be deactivated, and when an external trigger arrives (via `POST /tasks/resume`), the framework re-enters the same function with the preserved context.

**Acceptance Scenarios**:

1. **Given** a running durable task, **When** the function calls `return await ctx.suspend(reason="awaiting approval")`, **Then** the framework transitions the task to `suspended`, releases the lease, and the function exits cleanly.
2. **Given** a suspended task, **When** an external system sends `POST /tasks/resume` with the task ID, **Then** the framework re-fetches the task from the store, acquires a new lease, dispatches the function to the resume callback, and returns an empty-body response with the appropriate status code.
3. **Given** a suspended task, **When** the container restarts, **Then** the framework does not attempt to resume suspended tasks automatically — they wait for an explicit external trigger.

---

### User Story 3 — Track task progress and observe status from outside (Priority: P3)

A developer or external observer (dashboard, CLI, monitoring) needs to see what a running task is doing — its current phase, step count, or any developer-defined progress information. The developer writes `ctx.metadata.set("phase", "researching")` inside the function and any observer can read it.

**Why this priority**: Observability is essential for production agents but builds on the foundation of P1 and P2. Without progress tracking, long-running tasks are black boxes.

**Independent Test**: A developer sets metadata inside a running task, and a separate process can read the current metadata values via the task handle.

**Acceptance Scenarios**:

1. **Given** a running durable task, **When** the function calls `ctx.metadata.set("steps_completed", 3)`, **Then** an external observer calling `handle.metadata.get("steps_completed")` sees the value `3`.
2. **Given** a running durable task, **When** the function updates metadata multiple times, **Then** each update is persisted to the task record via a payload PATCH.

---

### User Story 4 — Develop and test locally without platform dependencies (Priority: P4)

A developer working on their laptop (no Azure, no hosted environment) needs the full durable task lifecycle to work identically — create, lease, renew, recover, complete. The framework automatically uses a local filesystem-backed provider when platform environment variables are absent.

**Why this priority**: Local development parity is critical for developer experience. If developers can't test crash recovery locally, they'll only discover bugs in production.

**Independent Test**: A developer runs their agent locally without any Azure credentials or platform environment variables. Tasks are stored as JSON files on disk. Killing and restarting the process triggers recovery of stale tasks.

**Acceptance Scenarios**:

1. **Given** no `FOUNDRY_HOSTING_ENVIRONMENT` variable is set, **When** the developer creates a `DurableTaskClient`, **Then** the framework automatically selects a local filesystem provider storing tasks under `$HOME/.durable-tasks/`.
2. **Given** a local filesystem provider, **When** the developer runs the full task lifecycle (create, start, update, complete, delete), **Then** all operations succeed with identical semantics to the hosted API.
3. **Given** a local task is in progress, **When** the developer kills the process and restarts, **Then** the framework detects the stale task (expired lease) and dispatches it to the resume callback.

---

### Edge Cases

- What happens when the lease expires before renewal succeeds? The task becomes stale; on the next startup, recovery reclaims it via dual-identity (same owner, new instance ID).
- What happens when multiple restarts occur rapidly? Each restart increments the lease `generation` counter. Only the latest instance holds a valid lease.
- What happens when `SIGTERM` is received during task creation (before the lease is acquired)? The task remains `pending` and is picked up on the next startup.
- What happens when the local filesystem provider runs out of disk? The framework raises an error on the write operation; the developer handles it.
- What happens when a durable task function returns without explicitly completing? The framework treats a normal return as success — deletes the task (ephemeral) or marks it completed (non-ephemeral).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `@durable_task` decorator that turns an async function into a crash-resilient unit of work with automatic task lifecycle management.
- **FR-002**: Decorated functions MUST accept a single `TaskContext[InputType]` parameter that provides typed input, metadata access, cancellation signals, and suspension capability.
- **FR-003**: System MUST support two invocation patterns: fire-and-forget (`task.start(...)`) returning a handle immediately, and invoke-and-wait (`task.run(...)`) returning the typed result.
- **FR-004**: System MUST manage task leases automatically — acquiring on start, renewing at half the lease duration in a background loop, and releasing on completion, suspension, or shutdown.
- **FR-005**: System MUST recover stale tasks on startup — querying owned in-progress tasks via dual-identity (stable `lease_owner` + ephemeral `lease_instance_id`) and dispatching them to the resume callback.
- **FR-006**: System MUST provide a single resume callback entry point that handles new work, restart recovery, and external triggers identically.
- **FR-007**: System MUST support task suspension via `ctx.suspend(reason=...)` — releasing the lease, persisting state, and enabling later re-entry via external trigger.
- **FR-008**: System MUST handle graceful shutdown (SIGTERM) by signalling `ctx.shutdown`, force-expiring all active leases, and exiting cleanly.
- **FR-009**: System MUST provide mutable metadata on the task context (`ctx.metadata.set/get/increment/append`) persisted to the task record for external observability.
- **FR-010**: System MUST provide a local filesystem-backed task provider (`LocalFileDurableTaskProvider`) with identical semantics when platform environment variables are absent.
- **FR-011**: System MUST support typed inputs via Pydantic models, dataclasses, or plain types — validated at the boundary and available as `ctx.input`.
- **FR-012**: System MUST support three exit modes: return a value (success), `return await ctx.suspend(...)` (suspend), or raise an exception (failure with structured error).
- **FR-013**: System MUST support per-task cancellation via `ctx.cancel` event (request-level) distinct from `ctx.shutdown` (container-level).
- **FR-014**: System MUST expose all durable task components from the `azure-ai-agentserver-core` package. Protocol packages (invocations, responses) integrate with core but do not define their own task primitives.
- **FR-015**: System MUST auto-register a `POST /tasks/resume` endpoint on the host for external trigger integration. The endpoint returns an empty body with the appropriate status code (202 accepted, 404 not found, 409 conflict) — no response body content is needed.
- **FR-016**: The lower-level primitives (`DurableTaskClient`, `TaskHandle`) MUST exist internally but are NOT part of the public API — the `@durable_task` decorator and `TaskContext` are the primary developer-facing surface.

### Key Entities

- **DurableTask**: A decorated async function wrapped with lifecycle management. Exposes `.start(...)`, `.run(...)`, and `.options(...)` for invocation.
- **TaskContext**: The single parameter to a durable function — provides `input`, `metadata`, `cancel`, `shutdown`, `suspend()`, `task_id`, `title`, `session_id`, `agent_name`, `tags`, `run_attempt`, `lease_generation`.
- **TaskRun**: A typed handle returned by `.start(...)` — provides `task_id`, `status`, `metadata`, `result()`, `cancel()`, `delete()`.
- **TaskMetadata**: Mutable progress dict on the task context — supports `set`, `get`, `increment`, `append`. Persisted to the task record.
- **LocalFileDurableTaskProvider**: Filesystem-backed provider for local development — stores tasks as JSON files under `$HOME/.durable-tasks/`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can make any async function crash-resilient by adding one decorator and zero infrastructure changes.
- **SC-002**: After a container crash, stale tasks are recovered and resumed within the container's startup time (not bounded by lease TTL) via dual-identity reclamation.
- **SC-003**: Suspend/resume round-trip works correctly — a suspended task can be resumed by an external trigger after arbitrary time, across container restarts.
- **SC-004**: Local development provides full lifecycle parity — developers can test crash recovery by killing and restarting the process without any platform dependencies.
- **SC-005**: The public API surface consists of fewer than 5 primary types (`durable_task`, `TaskContext`, `TaskRun`, `TaskMetadata`, plus exception types) — progressive disclosure keeps the simple case simple.
- **SC-006**: All durable task functionality ships in the `azure-ai-agentserver-core` package with no additional package dependencies required.

## Assumptions

- The Foundry Task Storage API (`/storage/tasks`) is available in the hosted environment and conforms to the protocol spec defined in the container spec PR.
- `$HOME` provides per-session durable storage that survives container restarts (as defined in the container image spec).
- The platform guarantees one logical writer per `(agent_name, session_id)` pair — lease conflicts on an active lease indicate misconfiguration, not normal contention.
- `depends_on_task_ids` (DAG dependencies) is out of scope for this implementation phase. Tasks are standalone units of work.
- Streaming output (`ctx.stream(...)`) is out of scope for this initial implementation — it can be added in a future iteration.
- The `ephemeral` flag (whether tasks are deleted on completion or kept) defaults to `True` — most tasks are short-lived execution trackers.
- Retry policies (`RetryPolicy`) are out of scope for this initial implementation — the developer handles retries in their function logic.
- The `@durable_task` decorator and `TaskContext` are the primary public API. The lower-level `DurableTaskClient` and `TaskHandle` exist internally to power the convenience layer but are not exposed as public API.
- Protocol packages (invocations, responses, githubcopilot) will integrate with the core durable task system via the host's `.AddDurableTasks()` builder extension — they do not define their own task primitives.
