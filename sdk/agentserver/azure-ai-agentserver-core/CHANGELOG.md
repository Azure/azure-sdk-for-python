# Release History

## 2.0.0b9 (2026-07-28)

### Features Added

- Added Agent Server-managed OTLP/gRPC export when `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` is configured.
- Task-record schema cleanup: framework-reserved wire keys in the persisted task record no longer carry a leading `_` (e.g. the `task_name` tag; the `schema_version` / `last_input_id` / `turn_started_at` / `retry_attempt` / `steering` payload keys; the `input` / `steering_input_<seq>` / `output` attachment keys) — only the `__attachment_ref__` discriminator keeps its marker. The `source` stamp now includes `hosting_environment` (from `FOUNDRY_HOSTING_ENVIRONMENT`), and the payload now carries a `schema_version` (currently `"1"`). Tasks persisted before this change (lacking `payload.schema_version`) are deleted rather than recovered by the recovery scan.
- Added a **resilient task primitive** for building long-running agents that survive container restarts, out-of-memory kills, and redeployments. Decorate an async function with `@task` (one-shot) or `@multi_turn_task` (multi-turn conversations); the framework persists task state to a task store and automatically recovers and re-invokes in-flight work after a crash. Available from `azure.ai.agentserver.core.tasks`, with `TaskContext`, `TaskRun`, configurable retries (`RetryPolicy`), cancellation, steering, and a typed exception set (`TaskFailed`, `TaskCancelled`, `TaskConflictError`, `TaskManagerNotInitialized`, and others). See the [Resilient Task Developer Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/tasks-guide.md).
- Added an **event streaming** API (`azure.ai.agentserver.core.streaming`) for publishing incremental task output to one or more subscribers, with in-memory and file-backed buffering and live or replay delivery. This makes it straightforward to serve Server-Sent Events (SSE) responses that a client can disconnect from and resume. See the [Streaming Developer Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/streaming-guide.md).
- Exposed `resolve_state_subdir(name)` on the public `azure.ai.agentserver.core` surface. It resolves an on-disk state subdirectory (e.g. `"tasks"`, `"streams"`, `"responses"`) under the shared agent-server state root (`AGENTSERVER_STATE_ROOT`, or `~/.agentserver` when unset), so protocol packages persist state under the same operator-controlled root.

### Other Changes

- `streams.use_file_backed_replay(...)` now has ergonomic defaults so the common case is a single call supplying only `cursor_fn`: `storage_dir` defaults to `resolve_state_subdir("streams")` (a `streams` directory under the agent-server state root, alongside `tasks`), `ttl_seconds` defaults to 600 (10 minutes), and serialization defaults to JSON.
- File-backed replay streams now sanitize the stream id before using it as an on-disk filename: well-formed ids (`[A-Za-z0-9._-]`, no `.`/`..` segment) are used verbatim, and any id containing a path separator or other unsafe character is SHA-256 hash-encoded to an `h_<hex>` filename so it can never escape the storage directory or collide with another stream. The file-backed terminal sentinel is now written as `{"__terminal__": true}` (the non-durable `emit_time` field was dropped; close-time is best-effort on rehydration).
- The per-attachment value cap was raised from 2 MiB to **10 MiB** (per-input payloads spill into `task.attachments`). The 1 MB `task.payload` budget, the inline-promotion thresholds (`_input` 200 KiB, steering input 20 KiB), and the 20-attachments-per-task limit are unchanged.
- `@task` / `@multi_turn_task` now require an explicit `name=` (the stable recovery/identity anchor); the previous `func.__qualname__` fallback is removed because it silently rebound task identity when a handler was renamed or moved, orphaning in-flight tasks. Omitting `name` (or passing whitespace) now raises `ValueError` at decoration.
- The per-turn task `timeout` now defaults to **1 day** when unset (previously unbounded) and enforces **1 day as a hard ceiling** — a larger or negative value is rejected at registration (`ValueError`). This caps a single handler invocation only; multi-turn chains still live indefinitely across turns (the budget resets each turn).
- A caller-supplied `input_id` on `Task.start` / `Task.run` (and the multi-turn equivalents) is now validated against the same charset/length pattern as `task_id`; an invalid id raises `ValueError` before any provider call.
- `RetryPolicy` now enforces hard caps at construction (fail-fast, not clamped): `max_attempts` must be 1–10 and `max_delay` must be 0–1 hour; out-of-range values raise `ValueError`. The zero-argument module-level presets (`exponential_backoff()`, `fixed_delay()`, `linear_backoff()`) now match their `RetryPolicy.<preset>()` classmethod values so retry cadence is identical across the Python and .NET implementations.
- Added `azure-core` as a dependency, and a `hosted` optional-dependencies extra (pulling in `azure-identity`) for hosted-agent deployments.
- `resolve_graceful_shutdown_timeout()` now honors the `AGENTSERVER_GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS` environment variable, letting operators shorten shutdown so task checkpoints can flush before long-running requests finish.
- Added diagnostic logging (logger `azure.ai.agentserver.streaming`) to the event-streaming subsystem covering stream creation/deletion, crash-recovery rehydration of file-backed streams, and corruption/lock-contention failures, to aid debugging in production.

## 2.0.0b8 (2026-07-22)

### Features Added

- Added `azure.ai.agentserver.core.storage`, the protocol-neutral Foundry durable state-store layer. `FoundryStateStore.get_or_create(name, ...)` is the primary entry point -- an async classmethod that resolves (or creates, on first use) the store in one call. Store-level operations act on the bound store: `get()` (its descriptor), `update(...)` (its mutable `description` / `tags`), and `delete()` (the whole store, cascade-deleting every item). Item operations are explicit and consistently named: `create_item`, `set_item`, `get_item`, `delete_item`, `list_keys`. Store names are path-encoded with base64url on the wire, store-level `item_ttl_seconds` is configured once at create, optional `user_isolation` is declared at store create, and trusted callers may delegate end-user partitioning with `user_id` (`x-ms-user-id`). Response bodies (`StateStore`, `StateStoreItem`, `StateStoreItemRef`, `DeletedStateStore`, `DeletedStateStoreItem`, `StateStoreItemKey`) are typed model classes generated from a formal TypeSpec contract, not hand-written dataclasses. See the [Durable State Store Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/state-store-guide.md).

### Bugs Fixed

- Fixed span attribute enrichment under `opentelemetry-sdk` >= 1.43.0, where `span._attributes` became a `BoundedAttributes` (backed by `._dict`) that no longer supports item assignment. Enrichment now resolves the backing store so agent identity attributes are written on both older and newer OpenTelemetry SDKs.

## 2.0.0b7 (2026-06-28)

### Features Added

- Container protocol version `2.0.0` support: added the platform identity header constants `x-agent-user-id` (`USER_ID`) — the global, cross-agent per-user partition key — and `x-agent-foundry-call-id` (`FOUNDRY_CALL_ID`) — the opaque per-request call identifier — to the `_platform_headers` module.
- Added `FOUNDRY_AGENT_ID` environment variable support exposing the agent's stable GUID via `AgentConfig.agent_guid` and the `resolve_agent_guid()` helper.
- Added a request-scoped platform context: `FoundryAgentRequestContext`, `get_request_context()`, `set_request_context()`, and `reset_request_context()`. Protocol packages bind the inbound per-request call ID and user ID so that handler code (and the SDK HTTP pipeline) can read them. `FoundryAgentRequestContext.platform_headers()` builds the headers to forward on outbound Foundry 1P calls — the per-request call ID only; `x-agent-user-id` is **not** forwarded (it is not accepted/trusted by 1P services and is used only for container-side state partitioning).

### Breaking Changes

- Replaced the `x-agent-user-isolation-key` / `x-agent-chat-isolation-key` header constants (`USER_ISOLATION_KEY` / `CHAT_ISOLATION_KEY`) with `x-agent-user-id` (`USER_ID`) and `x-agent-foundry-call-id` (`FOUNDRY_CALL_ID`) per container protocol version `2.0.0`.

## 2.0.0b6 (2026-06-12)

### Bugs Fixed

- Populated agent metadata when operation IDs are zeroed so agent metadata remains available for telemetry and downstream processing.
- Suppressed noisy observability/exporter INFO logs by default in tracing setup while preserving DEBUG visibility when explicitly enabled.

## 2.0.0b5 (2026-05-25)

### Bugs Fixed

- Fixed the blueprint telemetry attribute key name from `gen_ai.agent.blueprint.id` to `microsoft.a365.agent.blueprint.id` to align with A365 schema and cross-SDK behavior.

## 2.0.0b4 (2026-05-21)

### Features Added

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
