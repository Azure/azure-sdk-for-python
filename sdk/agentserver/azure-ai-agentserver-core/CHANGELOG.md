# Release History

## 2.0.0b4 (Unreleased)

### Breaking Changes

- **Public API cleanup for the durable-task primitive** (per spec 015). The `@task` decorator and related types have been simplified to ship a tighter, more honest surface ahead of GA:
  - **Renames** — `DurabilityContext.run_attempt` → `retry_attempt`; `lease_generation` → `recovery_count`; `generation` → `steering_generation`.
  - **`retry_attempt` is now durable across crash/recovery** — persisted at `payload["_retry_attempt"]` and re-hydrated on every TaskContext construction. `RetryPolicy.max_attempts` now means "total failure-retries across all lifetimes"; crash recovery does NOT consume the budget. The counter resets to 0 on successful invocation and on steering drain.
  - **Drops from `@task` and `TaskOptions`** — `TaskSuspended` exception (removed entirely), `description`, `store_input` (storage is now always implicit), `lease_duration_seconds`, `max_pending` (server-side back-pressure lives at a different layer).
  - **Drops from `TaskContext`** — `title`, `description`, `tags`, `agent_name`, `previous_input` (and the underlying `_steering["previous_input"]` slot).
- **Metadata is now a callable namespace facility.** Instead of a single bag, `ctx.metadata` is the default namespace and `ctx.metadata("name")` returns a sibling namespace. Each namespace tracks dirty state independently and is snapshotted at lifecycle boundaries. **Auto-flush has been deleted entirely** (`start_auto_flush`/`stop_auto_flush` and the background loop are gone); persistence is explicit at lifecycle transitions (start/suspend/complete/fail/cancel/terminate). Persistence layout: default namespace at `payload["metadata"]`, named namespaces at `payload["metadata:<name>"]`.
- **Primitive-reserved payload slots use the `_*` top-level convention.** `payload["_last_input_id"]`, `payload["_retry_attempt"]`, `payload["_steering"]` replace the previous `payload["_framework"]` nested namespace. The primitive does not enforce naming on the developer-facing metadata API — that enforcement is the responsibility of higher framework layers (see the `azure-ai-agentserver-responses` CHANGELOG).

### Bugs Fixed

- **Input data cleared at suspend for steerable tasks** (privacy / data minimization). The framework now clears `payload["input"]`, `_steering["active_input"]`, and `_steering["previous_input"]` at the suspend transition. These hold mirror copies of consumed user input that is no longer needed once the handler returns. Recovery transitions still preserve these slots because the handler will re-run with them; completion transitions are unaffected (terminal entries are deleted via `ephemeral=True` or retained via `ephemeral=False` by operator choice). See `docs/durable-task-developer-guide.md` §"Data Retention on Suspend".
- **Suspended-resume input patch is now etag-protected**. Concurrent resumes of the same suspended task race safely under the standard etag retry loop instead of silently overwriting each other.
- **TaskManager shutdown tolerates lifespan cancellation**. The graceful shutdown sleep and lease-expire steps are now wrapped to catch `asyncio.CancelledError` so that handlers always reach the `execution_task.cancel()` step and can wind down cleanly, even when the lifespan task is itself being cancelled by the host.
- **LocalFileTaskProvider default storage path** now honors the `AGENTSERVER_DURABLE_TASKS_PATH` environment variable. Without an explicit path, the provider still defaults to `~/.durable-tasks`. Enables operator / crash-harness isolation of durable task state without code changes.

### Other Changes

- **Removed dead `_steering["generation_results"]` write block in `_try_drain_steering`.** The field was added as forward-compat scaffolding for durable backup of superseded-result delivery but had no consumer anywhere in the codebase. The in-process superseded-result delivery via `TaskResult(output=…, status="superseded")` is unchanged. If durable replay of superseded results becomes a requirement in the future, restore the write here with a corresponding recovery-side read path.

### Features Added

- **Input acceptance preconditions on `Task.start(...)`**. New optional `input_id` and `if_last_input_id` keyword arguments model HTTP `If-Match: <etag>` semantics on a task's input queue. `input_id` records the new input's identity; `if_last_input_id` is the precondition value that the framework verifies against the task's stored last input id before any state mutation. Mismatch raises the new typed exception `LastInputIdPreconditionFailed` (subclass of new base `TaskPreconditionFailed`). The id is recorded in a framework-reserved namespace (`payload["_framework"]["last_input_id"]`) atomically with the input persist via etag protection, so concurrent callers cannot lose the precondition. Generic — usable by any package with sequential-input or optimistic-concurrency semantics. See `docs/durable-task-developer-guide.md` §"Input Acceptance Preconditions".

### Features Added

- **Durable long-running agents** — New `@task` decorator and supporting types for building crash-resilient, long-running agents that survive container crashes, OOM kills, and redeployments. Key capabilities:
  - **Lifecycle automation** — `.run()` and `.start()` automatically start, resume, or recover tasks based on their current state in the task store.
  - **Entry mode awareness** — `ctx.entry_mode` tells the function whether it was entered `"fresh"`, `"resumed"` from suspension, or `"recovered"` from a crash.
  - **Suspend & resume** — `ctx.suspend(output=..., reason=...)` pauses execution for multi-turn agent patterns (e.g., waiting for user input).
  - **TaskResult wrapper** — `run()` and `result()` return `TaskResult[Output]` with `.is_completed` / `.is_suspended` properties, making suspension a normal return value instead of an exception.
  - **Streaming** — `ctx.stream(chunk)` emits incremental output; consumers iterate with `async for chunk in task_run`.
  - **Cancellation & timeout** — Cooperative cancel via `ctx.cancel` event, configurable `timeout`, and `terminate()` for forced shutdown.
  - **RetryPolicy** — Configurable retry with factory presets: `.exponential_backoff()`, `.fixed_delay()`, `.linear_backoff()`, `.no_retry()`.
  - **Source auto-stamping** — The framework automatically stamps every task with provenance metadata: `type` (`agentserver.task`), `name` (the decorator `name` option — the stable identity anchor), and `server_version` (the `x-platform-server` header value). Source is framework-owned and not user-overridable. A reserved tag `_task_name` is also auto-stamped for LIST API filtering by function name.
  - **Callable factories** — `tags`, `title`, and `description` accept `Callable[[Input, task_id], T]` for dynamic metadata computed at task creation time.
  - **TaskMetadata** — Dict-like mutable progress metadata (`ctx.metadata["key"] = value`) with debounced auto-flush to the task store. Supports `[]`, `in`, `for`, `len`, `del`, plus convenience methods `.increment()` and `.append()`.
  - **Handle operations** — `TaskRun.metadata` for progress snapshot reads, `TaskRun.delete()` for task cleanup, `TaskRun.refresh()` for re-fetching state from the store, `TaskRun.lease_expiry_count` for monitoring ownership churn.
  - **TaskContext.description** — `ctx.description` exposes the task description string within the running function.
  - **Configurable shutdown grace** — `TaskManager(shutdown_grace_seconds=25.0)` controls how long the manager waits for tasks to checkpoint before force-expiring leases during shutdown.
  - **Task listing** — `my_task.list(status=...)` returns all tasks for a specific task function, automatically scoped by function name (via tag) and source type. Supports `status` and `session_id` filters.
- **Steerable tasks** — New `steerable=True` parameter on `@task` enables mid-flight steering where new inputs can be queued while a task is still running. Key capabilities:
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

- **`source` parameter removed** — The `source` keyword argument has been removed from `@task()`, `.run()`, `.start()`, and `.options()`. Source provenance is now auto-stamped by the framework and cannot be overridden by developers. Use `tags` for custom metadata.

### Bugs Fixed

- **Local provider payload merge** — Fixed `_local_provider.py` to use strict shallow merge per Protocol Spec §11: root-level keys are now always replaced, not recursively merged. Previously nested dicts were merged with `dict.update()`, which was more forgiving than the real Task Storage API.
- **Task recovery routing** — `_find_resume_callback()` now matches by `source.name` (the auto-stamped function name) first, then falls back to title prefix match. Previously relied only on fragile title prefix heuristic.

### Other Changes
- Added `_platform_headers` module with cross-cutting protocol header name constants (`x-request-id`, `x-platform-server`, `x-agent-session-id`, `x-platform-error-source`, `x-platform-error-detail`, and others). Protocol packages now import shared header name strings from core instead of maintaining their own copies.
- Added `TraceContextMiddleware` — a lightweight pure-ASGI middleware that propagates W3C trace context (`traceparent`, `tracestate`) and baggage from incoming HTTP requests. Any spans created by downstream frameworks (e.g. MAF / agent-framework) are automatically children of the caller's trace without additional framework spans.
- Added `enable_sensitive_data` parameter to `configure_observability()` to control whether prompts, tool arguments, and results are recorded in telemetry. Respects `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` environment variable.
- Added A365 tracing export support — when `FOUNDRY_HOSTING_ENVIRONMENT` and `FOUNDRY_AGENT365_TRACING_ENABLED` are set, telemetry is exported via the A365 observability pipeline.
- Added `resolve_agent_id()`, `resolve_agent_blueprint_id()`, and `resolve_agent_tenant_id()` config helpers for new Foundry environment variables (`FOUNDRY_AGENT_INSTANCE_CLIENT_ID`, `FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID`, `FOUNDRY_AGENT_TENANT_ID`).
- Added `gen_ai.agent.blueprint.id` and `microsoft.tenant.id` span attributes to the `FoundryEnrichmentSpanProcessor`.
- `AgentConfig.ws_ping_interval` — new field resolved from the `WS_KEEPALIVE_INTERVAL` environment variable (auto-injected by AgentService into hosted-agent containers). `0` disables; negative/non-finite values raise `ValueError` at startup. `AgentServerHost._build_hypercorn_config` wires this into Hypercorn's `websocket_ping_interval` so any protocol package serving WebSocket routes inherits keep-alive without per-package wiring.

### Breaking Changes

- Removed `request_span()` method from `AgentServerHost`. Trace context propagation is now handled automatically by `TraceContextMiddleware`.

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
