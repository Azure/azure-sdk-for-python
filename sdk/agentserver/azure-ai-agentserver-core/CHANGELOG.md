# Release History

## 2.0.0b4 (Unreleased)

### Features Added

- **Durable long-running agents** — New `@durable_task` decorator and supporting types for building crash-resilient, long-running agents that survive container crashes, OOM kills, and redeployments. Key capabilities:
  - **Lifecycle automation** — `.run()` and `.start()` automatically start, resume, or recover tasks based on their current state in the task store.
  - **Entry mode awareness** — `ctx.entry_mode` tells the function whether it was entered `"fresh"`, `"resumed"` from suspension, or `"recovered"` from a crash.
  - **Suspend & resume** — `ctx.suspend(output=..., reason=...)` pauses execution for multi-turn agent patterns (e.g., waiting for user input).
  - **TaskResult wrapper** — `run()` and `result()` return `TaskResult[Output]` with `.is_completed` / `.is_suspended` properties, making suspension a normal return value instead of an exception.
  - **Streaming** — `ctx.stream(chunk)` emits incremental output; consumers iterate with `async for chunk in task_run`.
  - **Cancellation & timeout** — Cooperative cancel via `ctx.cancel` event, configurable `timeout`, and `terminate()` for forced shutdown.
  - **RetryPolicy** — Configurable retry with factory presets: `.exponential_backoff()`, `.fixed_delay()`, `.linear_backoff()`, `.no_retry()`.
  - **Source auto-stamping** — The framework automatically stamps every task with provenance metadata: `type` (`agentserver.durable_task`), `name` (the decorator `name` option — the stable identity anchor), and `server_version` (the `x-platform-server` header value). Source is framework-owned and not user-overridable. A reserved tag `_durable_task_name` is also auto-stamped for LIST API filtering by function name.
  - **Callable factories** — `tags`, `title`, and `description` accept `Callable[[Input, task_id], T]` for dynamic metadata computed at task creation time.
  - **TaskMetadata** — Dict-like mutable progress metadata (`ctx.metadata["key"] = value`) with debounced auto-flush to the task store. Supports `[]`, `in`, `for`, `len`, `del`, plus convenience methods `.increment()` and `.append()`.
  - **Handle operations** — `TaskRun.metadata` for progress snapshot reads, `TaskRun.delete()` for task cleanup, `TaskRun.refresh()` for re-fetching state from the store, `TaskRun.lease_expiry_count` for monitoring ownership churn.
  - **TaskContext.description** — `ctx.description` exposes the task description string within the running function.
  - **Configurable shutdown grace** — `DurableTaskManager(shutdown_grace_seconds=25.0)` controls how long the manager waits for tasks to checkpoint before force-expiring leases during shutdown.
  - **Task listing** — `my_task.list(status=...)` returns all tasks for a specific durable task function, automatically scoped by function name (via tag) and source type. Supports `status` and `session_id` filters.
- **Steerable durable tasks** — New `steerable=True` parameter on `@durable_task` enables mid-flight steering where new inputs can be queued while a task is still running. Key capabilities:
  - **Input queue** — `start()` on an in-progress steerable task queues the new input and returns a `TaskRun` handle immediately, instead of raising `TaskConflictError`.
  - **Cancel signal** — `ctx.cancel` is automatically set when new inputs arrive, giving the function a cooperative signal to short-circuit.
  - **Automatic drain** — The framework drains the queue after the function suspends or completes, re-entering with the next queued input using `entry_mode="resumed"` and `was_steered=True`.
  - **Superseded results** — Previous generation's `TaskRun.result()` resolves with `status="superseded"` and `is_superseded=True`.
  - **Context enrichment** — `ctx.was_steered`, `ctx.previous_input`, `ctx.pending_inputs`, and `ctx.generation` provide full steering context.
  - **Queue limits** — `max_pending` (default 10) prevents unbounded queue growth; raises `SteeringQueueFull` when exceeded.
  - **Crash recovery** — `drain_in_progress` flag in persisted state enables recovery from mid-drain crashes.
  - **Distributed steering** — Lease renewal loop polls for pending inputs from other processes and sets `ctx.cancel` accordingly.
  - **Etag-aware completion** — Steerable tasks use optimistic concurrency on completion to detect concurrent steering.

### Breaking Changes

- **`source` parameter removed** — The `source` keyword argument has been removed from `@durable_task()`, `.run()`, `.start()`, and `.options()`. Source provenance is now auto-stamped by the framework and cannot be overridden by developers. Use `tags` for custom metadata.

### Bugs Fixed

- **Local provider payload merge** — Fixed `_local_provider.py` to use strict shallow merge per Protocol Spec §11: root-level keys are now always replaced, not recursively merged. Previously nested dicts were merged with `dict.update()`, which was more forgiving than the real Task Storage API.
- **Task recovery routing** — `_find_resume_callback()` now matches by `source.name` (the auto-stamped function name) first, then falls back to title prefix match. Previously relied only on fragile title prefix heuristic.

### Other Changes

## 2.0.0b3 (2026-04-22)

### Features Added

- `RequestIdMiddleware` — pure-ASGI middleware that sets an `x-request-id` response header on every response. The request ID is resolved from the OpenTelemetry trace ID, an incoming `x-request-id` header, or a generated UUID (in that priority). The resolved value is stored in ASGI scope state under the well-known key `agentserver.request_id` for use by sibling protocol packages. Automatically wired into `AgentServerHost`.

## 2.0.0b2 (2026-04-17)

### Features Added

- Startup configuration logging — `AgentServerHost` lifespan now emits three INFO-level log lines at startup: platform environment (agent name, version, port, session ID, SSE keep-alive), connectivity (project endpoint and OTLP endpoint masked to scheme://host, Application Insights configured flag), and host options (shutdown timeout, registered protocols). Sensitive values (Application Insights connection string) are never logged.
- `InboundRequestLoggingMiddleware` — pure-ASGI middleware wired automatically by `AgentServerHost` that logs every inbound HTTP request. Logs method, path (no query string), status code, duration in milliseconds, and correlation headers (`x-request-id`, `x-ms-client-request-id`). Status codes >= 400 are logged at WARNING; unhandled exceptions are logged as status 500 at WARNING. OpenTelemetry trace ID is included when an active trace exists.
- Inbound request logs now include `trace-id` extracted from the W3C `traceparent` header, even when no OTel span is active at middleware level. Previously the trace-id was only available after the endpoint handler created a request span.

### Bugs Fixed

- Fixed duplicate console log output when a `StreamHandler` was already present on the root logger (e.g. from `logging.basicConfig()` or framework setup). The SDK now detects any existing `StreamHandler` before adding its own, not just its sentinel-marked handler.

## 2.0.0b1 (2026-04-14)

This is a major architectural rewrite. The package has been redesigned as a lightweight hosting
foundation. Protocol implementations that were previously bundled in this package have moved to
dedicated protocol packages (`azure-ai-agentserver-responses`, `azure-ai-agentserver-invocations`).
See the [Migration Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/MigrationGuide.md)
for upgrading from 1.x versions.

### Breaking Changes

- **Package split**: All Responses API protocol types (models, handler decorators, SSE streaming)
  have moved to `azure-ai-agentserver-responses`. All Invocations protocol types have moved to
  `azure-ai-agentserver-invocations`. This package now contains only the shared hosting foundation.
- **`FoundryCBAgent` removed**: Replaced by `AgentServerHost`, a Starlette subclass that IS the
  ASGI app (no separate `.app` property or `register_routes()`).
- **`AgentRunContext` removed**: Protocol packages provide their own context types
  (`ResponseContext` in Responses, `request.state` in Invocations).
- **`TracingHelper` class removed**: Replaced by module-level functions (`request_span`,
  `end_span`, `record_error`, `trace_stream`) for a simpler functional API.
- **`AgentLogger` / `get_logger()` removed**: Use `logging.getLogger("azure.ai.agentserver")`
  directly, or rely on the SDK's automatic console logging setup.
- **`ErrorResponse.create()` removed**: Replaced by `create_error_response()` module-level function.
- **Health endpoint renamed**: `/healthy` → `/readiness`.
- **OpenTelemetry is now a required dependency** (was optional `[tracing]` extras in 1.x).
- **Environment variables changed**: `AGENT_LOG_LEVEL` and `AGENT_GRACEFUL_SHUTDOWN_TIMEOUT` are
  no longer read from `Constants`. Use the `log_level` and `graceful_shutdown_timeout` constructor
  parameters instead.

### Features Added

- `AgentServerHost` base class with built-in health probe (`/readiness`), graceful shutdown
  (configurable timeout), and Hypercorn-based ASGI serving.
- Cooperative mixin inheritance for multi-protocol composition — a single server can host both
  Responses and Invocations endpoints.
- Automatic OpenTelemetry tracing with Azure Monitor and OTLP exporters.
- `configure_observability` constructor parameter for overridable logging + tracing setup.
  Console `StreamHandler` is attached to the root logger by default so user `logging.info()`
  calls are visible without any extra configuration.
- `request_span()` context manager for creating request-scoped OTel spans with GenAI semantic
  convention attributes.
- `end_span()`, `record_error()`, `flush_spans()`, `trace_stream()` public functions for
  protocol SDK tracing lifecycle.
- `set_current_span()` / `detach_context()` for explicit OTel context management during
  streaming, ensuring child spans are correctly parented.
- `AgentConfig` dataclass for resolved configuration from environment variables (Foundry agent
  name, version, project ID, session ID, etc.).
- `create_error_response()` utility for standard error envelope JSON responses.
- `build_server_version()` for constructing `x-platform-server` header segments.
- HTTP access logging with configurable format via `access_log` and `access_log_format`
  constructor parameters.

## 1.0.0b1 (2025-11-07)

### Features Added

First version
