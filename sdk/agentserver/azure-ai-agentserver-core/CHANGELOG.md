# Release History

## 2.0.0b4 (Unreleased)

The durable-task primitive (`@task`, `TaskContext`, `TaskRun`, `TaskResult`,
`TaskManager`) ships in this release. The shape below is the **initial-release
contract** for the primitive; nothing here is a delta against a prior release
of the primitive (it has not shipped before). For non-durable-task changes in
this release (developer-guide tightening, transport-layer policies, observability,
config), see the subsections after "Public surface".

### Public surface — durable-task primitive

**Top-level package** (`from azure.ai.agentserver.core.durable import ...`):

`task`, `Task`, `RetryPolicy`, `TaskContext`, `TaskMetadata`, `TaskResult`,
`TaskRun`, `Suspended`, `TaskStatus`, `EntryMode`, `TaskFailed`,
`TaskCancelled`, `TaskNotFound`, `TaskConflictError`,
`LastInputIdPreconditionFailed`, `SteeringQueueFull`, `TaskPreconditionFailed`,
`StreamHandler`, `StreamHandlerFactory`, `QueueStreamHandler`.

**`@task(...)` decorator keywords**: `name`, `title`, `tags`, `timeout`,
`ephemeral`, `retry`, `steerable`, `stream_handler_factory`. The same keywords
are accepted by `Task.options(...)` to derive a variant with overrides.

**`Task.run()` / `Task.start()` call-site keywords**: `task_id`, `input`,
`input_id`, `if_last_input_id`.

**`TaskResult.status`** is `Literal["completed", "suspended"]` — two values only.
There is no third status. Steering is plain multi-turn (see §4 Steering of the
dev guide): the first turn's caller observes the natural outcome; the steerer's
`.result()` resolves with the next turn's outcome (or raises `TaskConflictError`
if the handler ended the task).

**`TaskConflictError`** is the **single error type** for any "task is busy / not
available" state. It carries `current_status` so the caller can branch on which
flavor of conflict it is: live-elsewhere non-steerable, dead-evicted
(split-brain protection), or terminal-with-queued-steerer.

**`TaskContext`** public properties: `input`, `entry_mode`, `task_id`,
`metadata`, `cancel` (bare `asyncio.Event`), `timeout_exceeded` (`bool`),
`cancel_requested` (`bool`), `pending_input_count` (`int`, live), `is_steered_turn`
(`bool`), `shutdown` (`asyncio.Event`), `retry_attempt`, `recovery_count`.
Public methods: `await ctx.suspend(output=...)`, `await ctx.stream(chunk)`,
`await ctx.exit_for_recovery()`.

**`@task(timeout=...)`** is **per-turn**, **wall-clock**, **durable** across
crashes within a turn, and **cooperative-only**. Each handler turn (fresh entry,
suspended-to-resume, steering drain re-entry) gets a fresh budget. A crash
mid-turn does NOT reset the budget; the recovered watchdog computes
`remaining = max(0, timeout - (now - turn_started_at))` clamped to
`[0, timeout]`. The watchdog sets `ctx.timeout_exceeded = True` then
`ctx.cancel.set()` then exits — it does NOT force-stop the handler.

**`ctx.exit_for_recovery()`** is the prescribed shutdown shape. Callable only
when `ctx.shutdown.is_set() == True`; misuse raises `RuntimeError` at the call
site. The framework flushes metadata, releases the lease, leaves the stored
status as `in_progress`, signals the caller with `TaskCancelled`, and preserves
queued steering inputs. The recovery scan on next process startup re-enters the
handler with `ctx.entry_mode == "recovered"`.

**`ctx.metadata`** auto-flushes at every terminal-of-turn boundary
(normal-suspend, normal-complete, cooperative-cancel, exception,
suspend-with-queued-steering, return-with-queued-steering,
raise-with-queued-steering, shutdown-via-`exit_for_recovery`). Explicit
`ctx.metadata.flush()` calls remain available as a fence before at-most-once
side effects but are NOT required for durability across graceful boundaries.

**Recovery** is framework-managed and observable only via
`ctx.entry_mode == "recovered"`. Three internal layers — hardened startup
scan, periodic background scan, inline reclaim on scheduling primitives —
share a single reclaim helper guarded by ETag CAS. The lease owner string
incorporates both agent name (`FOUNDRY_AGENT_NAME`) and session ID, so two
different agents sharing a session ID cannot collide on lease ownership.

**Eviction (split-brain protection)** is handled silently by the framework.
Store-write rejections of `HTTP 409` with body `$.error.code == "binding_mismatch"`
are classified as `evicted`; the local cleanup sequence (cancel execution,
suppress terminal write, signal awaiters with `TaskConflictError`) runs
atomically. Caller-observable outcomes at scheduling primitives are identical
to the live-elsewhere case — only operator WARNING logs differentiate.

### Public surface — transport layer

**`HostedTaskProvider`** is built on `azure.core.AsyncPipelineClient` with the
standard policy chain (request-id, headers, user-agent, retry,
`AsyncBearerTokenCredentialPolicy`, task-API logging, distributed tracing).
`ContentDecodePolicy` is intentionally excluded — body parsing happens at the
call site with defensive error handling (the responses-storage gzip lesson).
The retry policy is configured to retry on 5xx / 408 / 429 only; never on 409
regardless of body. The `credential` parameter on `HostedTaskProvider.__init__`
is typed `AsyncTokenCredential`.

The `httpx` package is no longer a production dependency of
`azure-ai-agentserver-core`.

### Documentation

- **Consolidated developer guide** (`docs/durable-task-guide.md`) is the
  end-to-end learning arc for the durable-task primitive. New §4 subsections:
  Cancellation (independent cause booleans), Timeout (per-turn / wall-clock /
  durable / cooperative-only), Shutdown (`ctx.exit_for_recovery()`). The
  Steering subsection is rewritten for plain multi-turn semantics. The
  Reference section enumerates the final `TaskContext` surface. The
  Stale-task-recovery section is gone — recovery is framework-managed with
  no developer knob.
- **Doc-review meta-test** (`tests/durable/test_dev_guide_review.py`) is
  extended with the spec 016 presence/absence invariants — guide will fail
  CI if `stale_timeout` / `superseded` / `is_superseded` /
  `_pending_steering_futures` / `was_steered` / `pending_inputs` /
  `steering_generation` / `CancelSignal` / `TaskTerminated` / `.terminate(`
  reappear in the guide body, or if `ctx.timeout_exceeded` /
  `ctx.cancel_requested` / `ctx.pending_input_count` / `ctx.is_steered_turn` /
  `ctx.exit_for_recovery` go missing from §4 Concepts or §5 Reference.

### Bugs Fixed

- **Input data cleared at suspend for steerable tasks** (privacy / data
  minimization). The framework clears `payload["input"]` and
  `_steering["active_input"]` at the suspend transition.
- **Suspended-resume input patch is now etag-protected**. Concurrent resumes
  of the same suspended task race safely under the standard etag retry loop.
- **TaskManager shutdown tolerates lifespan cancellation**. The graceful
  shutdown sleep and lease-expire steps are wrapped to catch
  `asyncio.CancelledError` so handlers always reach the
  `execution_task.cancel()` step.
- **Lease owner string includes agent name AND session ID**. Two different
  agents sharing a session ID no longer collide on lease ownership.
- **Steering surface is plain multi-turn**. Removed the dead
  `_steering["generation_results"]` write block and the parallel
  `_pending_steering_futures` tracking; steerers now bind through the same
  result-future mechanism as the first-turn caller. The first turn's
  `ctx.suspend(output=X)` emission is delivered unconditionally — never
  replaced by what a later turn produces.
- **Per-turn timeout durability**. `@task(timeout=...)` is anchored to a
  persisted per-turn-start timestamp; crash recovery resumes the watchdog
  with the correct remaining budget; clock-skew is clamped to
  `[0, timeout]`.
- **Watchdog docstring corrected**. The previous claim that the timeout
  watchdog would "eventually expire the lease and the task will be
  recovered" was false; the watchdog is cooperative-only and an ignoring
  handler runs until process death or external `TaskRun.cancel()`.

### Features Added — non-durable-task

- **Input acceptance preconditions on `Task.start(...)`**. New optional
  `input_id` and `if_last_input_id` keyword arguments model HTTP
  `If-Match: <etag>` semantics on a task's input queue. Mismatch raises
  `LastInputIdPreconditionFailed` (subclass of `TaskPreconditionFailed`).
- Added `_platform_headers` module with cross-cutting protocol header name
  constants.
- Added `TraceContextMiddleware` — pure-ASGI middleware that propagates
  W3C trace context from incoming HTTP requests.
- Added `enable_sensitive_data` parameter to `configure_observability()`.
- Added A365 tracing export support.
- Added `resolve_agent_id()`, `resolve_agent_blueprint_id()`,
  `resolve_agent_tenant_id()` config helpers.
- Added `gen_ai.agent.blueprint.id` and `microsoft.tenant.id` span
  attributes to `FoundryEnrichmentSpanProcessor`.
- `AgentConfig.ws_ping_interval` from `WS_KEEPALIVE_INTERVAL` env var.
- Removed `request_span()` from `AgentServerHost` (handled automatically by
  `TraceContextMiddleware`).

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
