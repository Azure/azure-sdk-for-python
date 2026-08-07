# Release History

## 1.1.0b1 (Unreleased)

### Features Added

- Added Invocations package identity to the combined `x-platform-server` value.
- Added the preview `azure.ai.agentserver.invocations.voice` submodule, a typed
  implementation of Voice Live Bridge Protocol `1.0` over the existing
  `invocations_ws` transport.
- Added `VoiceAgentServerHost`, immutable Voice events, ordered multi-item text
  output, proactive admission, cancellation and terminal arbitration, handoff,
  and session controls without exposing wire frames.
- Added exact-message deduplication, bounded callback coordination and cleanup,
  cooperative cancellation, content-free protocol metrics, strict protocol
  validation, and per-connection replay-free state.

### Bugs Fixed

- Preserved an application-selected WebSocket close code in structured close
  diagnostics when the handler returns or raises after successfully sending the close frame.
- Preserved application-selected close codes when cancellation races an in-flight
  WebSocket close, without treating pre-I/O failures as committed closes, and
  added a first-terminal-wins close-code source classification.
- Propagated `x-platform-server` and incoming W3C trace context through the
  WebSocket upgrade and connection lifetime directly in Invocations, without
  changing Core middleware behavior.
- Accepted opaque non-empty inbound Voice envelope IDs while retaining the
  `m_` namespace for SDK-generated frames, matching the protocol contract.
- Validated known Voice caller-context fields while preserving additive metadata
  and open channel values, and rejected explicit `null` for typed startup fields.
- Kept connection-lifetime Voice startup context charged to the process-wide
  customer-memory budget until the connection and any cancellation-resistant
  SDK-owned callback tasks release it.
- Moved Voice readiness arbitration to the actual WebSocket transport-attempt
  boundary so application frames received while `session.ready` is still waiting
  on local send locks are rejected without misclassifying immediate peer replies.
- Prepared and validated Voice terminal frames before committing local terminal
  state, and completed post-wire response bookkeeping before propagating cancellation.
- Kept a self-cancelled response in the active protocol slot after its customer
  callback returns, until the Bridge terminal outcome or connection teardown,
  preventing a later response from starting during cancellation arbitration.
- Replaced eviction-based Voice message and identity tombstones with exact,
  byte-bounded fail-closed ledgers of binary SHA-256 digests so old messages
  and input items can never be replayed after falling out of a recent window.
  Response terminal, playback, abandoned-admission, and
  output-item ownership state now share one exact connection-lifetime ledger.
- Registered `/invocations_ws` ahead of overlapping WebSocket catch-all routes
  and mounts while rejecting exact endpoint conflicts.
- Made Voice connection shutdown cancellation-safe and bounded all teardown
  phases by one absolute cleanup deadline.

### Other Changes

- Voice now ships in the Invocations distribution and shares its package version
  and release artifact; no separate Voice package or server identity is required.
- Voice follows the existing `invocations_ws` tracing behavior: the transport
  emits structured close diagnostics but creates no framework-owned connection
  or turn spans.

## 1.0.0 (2026-08-07)

### Bugs Fixed

- Added SSE keep-alive comments to idle `POST /invocations` event streams when
  `SSE_KEEPALIVE_INTERVAL` is configured, preventing hosted proxy idle timeouts
  from disconnecting clients before the agent emits its final events.

### Other Changes

- Updated the minimum `azure-ai-agentserver-core` dependency to the stable
  `2.0.0` release.

## 1.0.0b8 (2026-08-03)

### Samples

- Added samples showing how to build crash-resilient invocation agents on top of the new core resilient-task primitive: `resilient_multiturn` (suspend/resume conversation), `resilient_langgraph` (real-time streaming LangGraph integration with crash recovery + steering), and `resilient_research` (multi-stage research loop with checkpointing). See the [Resilient Task Developer Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/tasks-guide.md) for the underlying API.

### Bugs Fixed

- The cancel (`POST /invocations/{id}/cancel`) and get (`GET /invocations/{id}`) endpoints now resolve the session id consistently with the invoke endpoint, so custom cancel/get handlers can reliably look up per-session state.

### Other Changes

- Bumped the minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b10`, which adds an opt-in gate for resilient-task startup recovery so invocations-only agents no longer make a blocking task-store call during startup.

## 1.0.0b7 (2026-07-22)

### Features Added

- AsyncAPI docs endpoints — `InvocationAgentServerHost` now accepts optional
  `asyncapi_spec_json` (dict) and/or `asyncapi_spec_yaml` (raw YAML string)
  constructor args, served at `GET /invocations/docs/asyncapi.json` and
  `GET /invocations/docs/asyncapi.yaml` respectively. Either representation
  returns `404` if not registered. See README for details.

### Other Changes

- Bumped minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b8`.

## 1.0.0b6 (2026-06-28)

### Features Added

- Container protocol version `2.0.0` support: reads `x-agent-user-id` and `x-agent-foundry-call-id` from inbound requests and binds them to the request-scoped platform context so the per-request call ID is forwarded on outbound Foundry 1P calls (`x-agent-user-id` is not forwarded to 1P). The values are also exposed on `request.state.user_id` and `request.state.call_id`.

### Breaking Changes

- Replaced `request.state.user_isolation_key` / `request.state.chat_isolation_key` with `request.state.user_id` / `request.state.call_id` per container protocol version `2.0.0`.

## 1.0.0b5 (2026-06-12)

### Bugs Fixed

- Fixed exception tracing for streaming responses so errors raised while iterating streaming results are captured correctly and invocation/session logging context is reset after streaming completes.

## 1.0.0b4 (2026-05-21)

### Features Added

- Error source classification headers: All HTTP error responses now include `x-platform-error-source` with a value of `user`, `platform`, or `upstream` to indicate which component caused the error. Developer handler exceptions and missing handler registrations are classified as `upstream`. Exceptions tagged with the platform error tag are classified as `platform` and additionally include `x-platform-error-detail` with truncated exception details (max 2048 characters) for diagnostics.
- WebSocket protocol support — `InvocationAgentServerHost` now hosts `/invocations_ws` alongside `POST /invocations`. Register the handler with the new `@app.ws_handler` decorator. The route is registered lazily on first decoration, so hosts without a registered handler return HTTP 404.
- WebSocket Ping/Pong keep-alive — disabled by default; enable by setting the `WS_KEEPALIVE_INTERVAL` env var (auto-injected by AgentService into hosted-agent containers; surfaced on `app.config.ws_ping_interval` in `azure-ai-agentserver-core>=2.0.0b4`). `0` (or unset) disables keep-alive. Wired through to Hypercorn's `websocket_ping_interval` by `AgentServerHost._build_hypercorn_config`.
- WebSocket telemetry — structured close-event log line carrying `azure.ai.agentserver.invocations_ws.session_id`, `close_code`, and `duration_ms` (via the standard `logging` `extra` dict). Session ID honours the `FOUNDRY_AGENT_SESSION_ID` env var for HTTP/WS correlation.
- New samples: `samples/ws_invoke_agent/` (echo) and `samples/ws_bidirectional_streaming_agent/` (concurrent token streaming with cancel/bye control messages).

### Breaking Changes

- Removed the automatic `invoke_agent` server span that was created on each `/invocations` request. Trace context propagation is now handled by the core `TraceContextMiddleware`, and user-created spans inside handlers are correctly parented without framework-generated spans.
- Removed `_safe_set_attrs` and `_wrap_streaming_response` internal helpers (no longer needed without framework-level span management).

### Other Changes

- Platform header name constants (e.g. `x-platform-error-source`, `x-platform-error-detail`) are now imported from `azure-ai-agentserver-core` (`_platform_headers` module) instead of being defined locally. Error source classification helpers remain internal to this package.
- Simplified request handling: baggage entries (`invocation_id`, `session_id`) are still set on each request, but span creation and lifecycle management are left to downstream frameworks.

## 1.0.0b3 (2026-04-22)

### Features Added

- All HTTP responses now include an `x-request-id` header for request correlation, inherited from `RequestIdMiddleware` in `azure-ai-agentserver-core>=2.0.0b3`. The value is resolved from the OpenTelemetry trace ID, an incoming `x-request-id` header, or a generated UUID.

### Other Changes

- Bumped minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b3`.

## 1.0.0b2 (2026-04-17)

### Features Added

- Startup configuration logging — `InvocationAgentServerHost` logs whether an OpenAPI spec is configured at INFO level during construction.
- Inbound request logging — `InboundRequestLoggingMiddleware` from `azure-ai-agentserver-core` is now wired automatically by `AgentServerHost`. All inbound HTTP requests are logged at INFO level (start) and at INFO or WARNING level (completion) with method, path, status code, duration, and correlation headers.

## 1.0.0b1 (2026-04-14)

### Features Added

- Initial release of `azure-ai-agentserver-invocations`.
- `InvocationAgentServerHost` — a Starlette-based host subclass for the invocations protocol.
- Decorator-based handler registration (`@app.invoke_handler`, `@app.get_invocation_handler`, `@app.cancel_invocation_handler`).
- Optional `GET /invocations/{id}` and `POST /invocations/{id}/cancel` endpoints.
- `GET /invocations/docs/openapi.json` for OpenAPI spec serving.
- Invocation ID tracking and session correlation via `agent_session_id` query parameter.
- Distributed tracing with GenAI semantic convention span attributes.
- W3C Baggage propagation of `invocation_id` and `session_id` for cross-service correlation.
- Structured logging with `invocation_id` and `session_id` via `contextvars`.
- Streaming response support with span lifecycle management.
- Cooperative mixin inheritance for multi-protocol composition.
