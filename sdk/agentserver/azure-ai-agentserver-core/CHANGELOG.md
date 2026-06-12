# Release History

## 2.0.0b6 (Unreleased)

### Features Added

- **Public read API: `Task.get(task_id) -> TaskSnapshot | None`** —
  read-only introspection for any non-deleted task in any status
  (pending, in_progress, suspended, completed). Returns ``None``
  for missing tasks (does NOT raise ``TaskNotFound``). Never
  reclaims, never extends the lease, never PATCHes. Mirrors the
  instance-method shape of ``Task.get_active_run`` as its
  read-only sibling.

  New public type ``TaskSnapshot`` exposes only developer-facing
  fields (``task_id``, ``status``, ``created_at``, ``updated_at``,
  ``started_at``, ``completed_at``, ``output``, ``error``,
  ``suspension_reason``, ``metadata``, ``lease_expiry_count``).
  Framework-internal storage details (lease, etag, raw payload,
  raw attachments, source, tags) are deliberately excluded.

  ```python
  snap = await my_task.get("task-123")
  if snap is None:
      ...  # never existed or was deleted
  else:
      print(snap.status, snap.output, snap.error)
  ```

- **Per-output payloads up to 2 MB** for both `return` values from
  durable-task handlers and `ctx.suspend(output=...)` values. Outputs
  are stored entirely in a framework-managed attachment slot, so they
  never compete with the shared 1 MB task-payload budget. New
  developer-facing exception:

  | Limit | Value | Exception |
  |---|---|---|
  | Per-output maximum size (serialized JSON) | **2 MB** | `OutputTooLarge` |

  Like `InputTooLarge`, the check runs client-side **before** any
  network call. If you have a use case that genuinely needs > 2 MB
  per output, externalize it (write to blob storage, return a
  reference).

- **Per-input payloads up to 2 MB** for both the initial function
  input and each queued steering input. Pass arbitrarily large input
  values to `Task.start(...)` (up to the 2 MB ceiling) and the
  framework handles persistence transparently.

  New limits + exceptions:

  | Limit | Value | Exception |
  |---|---|---|
  | Per-input maximum size (serialized JSON) | **2 MB** | `InputTooLarge` |
  | Maximum queued steering inputs | **9** | `SteeringQueueFull` |

  All limits are enforced client-side **before** any network call, so
  failures surface as typed Python exceptions, not opaque HTTP errors.

  Public API surface unchanged — handlers see `ctx.input` as the
  deserialized value regardless of input size.

### Breaking Changes

- **`EventStreamGoneError` removed** from
  `azure.ai.agentserver.core.streaming`. Spec 019 FR-E-001/-002
  collapsed the previously-distinct `Gone` (registered then
  destroyed) and `NotFound` (never registered) error types into a
  single `EventStreamNotFoundError`. Every "this id is not
  currently a live stream" condition — never-registered,
  explicitly-deleted, or close-clock-TTL elapsed — now raises
  `EventStreamNotFoundError` and wire-maps to HTTP 404. The
  previous distinction's actionable value at the consumer's layer
  was zero (right behavior is the same either way) and it leaked
  the registry's internal tombstone bookkeeping.

- **Replay-backing tombstone is now time-deterministic, not
  buffer-state-driven.** Spec 019 FR-E-005 replaces the previous
  "Closed + buffer empty + had emit" auto-transition with a
  close-clock model: when a replay backing (`ReplayEventStream`
  or `FileBackedReplayEventStream` configured with `ttl_seconds`)
  is closed, the registry tombstones the id at the wall-clock
  moment `close_time + ttl_seconds`, regardless of who is
  observing. Per-event TTL eviction continues to run during ACTIVE
  to bound long-running stream memory.

- `AttachmentTooLarge` and `AttachmentLimitExceeded` are no longer
  exported from `azure.ai.agentserver.core.durable`. Attachments are
  a framework storage-layer concept that developers never name;
  surfacing the attachment-vocabulary errors on the developer API
  leaked the internal split between `payload` and `attachments`. The
  framework now catches the internal `_AttachmentTooLarge` raised by
  a provider and re-raises a developer-facing exception based on
  which channel the violation occurred on:

  - `payload["input"]` (or steering inputs) → `InputTooLarge`
  - handler return / `ctx.suspend(output=...)` → `OutputTooLarge`

- **Unified streaming primitive** — new `azure.ai.agentserver.core.streaming`
  subpackage exposing a `streams` registry singleton + `EventStream`
  Protocol + four exception types. The registry is the single
  process-level lifecycle owner; pick a backing once at app startup
  via one of three strongly-typed configurators:

  ```python
  streams.use_in_memory_live()                      # default — multicast, no buffer
  streams.use_in_memory_replay(cursor_fn=..., ttl_seconds=600)
  streams.use_file_backed_replay(storage_dir=..., ttl_seconds=600)
  ```

  Then anywhere in the process: `stream = await streams.get_or_create(id)`
  where `id` is the **per-turn / per-invocation identifier**
  (`invocation_id` for invocations, `response_id` for responses).
  Subscribers attach via `async for ev in stream.subscribe(after=N)`.
  Streaming is now fully decoupled from `@task` — handlers explicitly
  opt in by calling the registry. See
  [`docs/streaming-guide.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/streaming-guide.md)
  for the full developer guide, including tombstone retention,
  per-turn id convention, and exception/wire mapping.

  Public surface = 5 exports: `streams`, `EventStream`,
  `EventStreamError`, `EventStreamClosedError`,
  `EventStreamNotFoundError`. (Spec 019 FR-E-001 removed
  `EventStreamGoneError`; see Breaking Changes above.) The three
  SDK-bundled backings are selected at app startup via the
  registry's `use_in_memory_live()` /
  `use_in_memory_replay(...)` / `use_file_backed_replay(...)` config-
  urators; external callers obtain stream instances exclusively via
  `await streams.get_or_create(id)` and program against the Protocol.

- **Durable tasks** — new `@task` decorator and supporting types
  (`TaskContext`, `TaskResult`, `TaskRun`, `RetryPolicy`,
  `TaskConflictError`, `TaskFailed`, `TaskCancelled`) for
  crash-resilient long-running agents. Tasks survive container
  restarts, OOM kills, and redeployments; the framework re-enters the
  handler with `ctx.entry_mode == "recovered"` and a populated
  `ctx.metadata` after a crash. Supports multi-turn suspend/resume via
  `ctx.suspend()`, cooperative cancel via `ctx.cancel`, per-turn
  wall-clock timeout via `@task(timeout=...)`, and steering of in-flight
  tasks via `@task(steerable=True)`. For streaming, handlers use the
  new `streams` registry (above) — `@task` itself has no streaming-
  related kwarg. See the
  [developer guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/durable-task-guide.md)
  for the full API and patterns reference.

### Other Changes

- **Local file provider parity with the hosted task service (spec 020).**
  The local file-backed task provider used in dev mode now enforces
  the same validation, state machine, lease semantics, attachment
  rules, and list-filter surface as the hosted task service. This
  closes silent "works locally, fails in service" divergences:

  - Field validation: task id regex (`^[a-zA-Z0-9_-]{1,128}$`),
    required `agent_name` / `session_id` / `title` on create, tag key
    regex (`^[a-zA-Z0-9_.\-]{1,64}$`) + max 16 entries + max 256 char
    values, payload ≤ 1 MB, error ≤ 64 KB, source ≤ 4 KB,
    suspension_reason ≤ 256 chars, `source.type` required when source
    supplied, `"failed"` status rejected, `"done"` legacy alias
    normalized to `"completed"`, attachment key regex.
  - State machine: full `pending` ⇄ `in_progress` ⇄ `suspended` →
    `completed` transition matrix enforcement; terminal-task
    immutability (PATCH on `completed` rejected except no-op
    `completed → completed`); immutable fields on PATCH (`id`,
    `agent_name`, `session_id`, `title`, `description`, `source`);
    `suspension_reason` only allowed with `status=suspended`; DELETE
    on non-terminal task without `force=true` rejected; DELETE honors
    `If-Match`.
  - Lease: duration must be 0 (force-expire) or 10..3600;
    `(lease_owner, lease_instance_id, lease_duration_seconds)` are
    all-or-nothing; different-owner takeover when the existing lease
    is live is rejected; `in_progress → pending` requires matching
    lease; lease renewal only allowed on `in_progress`; force-expire
    cannot combine with status change and requires lease ownership
    unless already expired; `expiry_count` bumps on different-owner
    takeover when the prior lease was expired; `started_at` resets
    on re-acquisition when prior was expired; new `heartbeat_at`
    field stamped on every lease write.
  - Status-transition side effects: transitions to / from each state
    now clear / set the right combination of `lease`,
    `suspension_reason`, `started_at`, `completed_at`.
  - PATCH semantics: `payload` patch branches on type (object →
    shallow merge, non-object → full replace; previously assumed dict).
  - Attachments: per-key null-as-delete (existing) plus new
    top-level clear-all gesture via `TaskPatchRequest.clear_attachments`
    flag (mirrors the service's `attachments: null` wire form).
  - List filters: `has_error`, `lease_expired`, `omit_attachment_values`
    added; pagination via `after` cursor + `limit` (default 20, max
    100); `order` accepts `"asc"` / `"desc"` by `created_at`;
    `before` parameter rejected (forward-only cursor pagination);
    status filter normalizes `"done"` → `"completed"`; `agent_name`
    and `session_id` are now optional (workspace-wide listing).

- **Hosted provider distinguishes service error codes internally
  (spec 020).** The hosted task service now returns distinct error
  codes (`task_immutable`, `invalid_state_transition`,
  `lease_held_by_another`, `task_already_exists`,
  `lease_ownership_changed`, `etag_mismatch`, `invalid_request`).
  The framework's response classifier now dispatches on these so
  retry-able codes (`etag_mismatch`, `lease_ownership_changed`)
  are retried transparently, while terminal conflicts surface as
  the appropriate developer-facing `TaskConflictError` /
  `TaskPreconditionFailed`. **No new developer-visible exception
  types** — internal dispatch is fully absorbed inside the
  framework. Existing `except TaskConflictError:` callers keep
  working unchanged.

- The hosted task-store transport is now built on
  `azure.core.AsyncPipelineClient` instead of `httpx` / `aiohttp`;
  neither `httpx` nor `aiohttp` is a production dependency of this
  package anymore.

- **Removed the `samples/` directory.** The standalone in-process
  samples (`durable_retry`, `durable_streaming`, `selfhosted_invocation`)
  have been deleted. End-to-end usage of the `@task` and streaming
  primitives is demonstrated in the runnable HTTP-host samples shipped
  with `azure-ai-agentserver-invocations` and
  `azure-ai-agentserver-responses`, which match how the primitives
  are actually consumed in production.

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
