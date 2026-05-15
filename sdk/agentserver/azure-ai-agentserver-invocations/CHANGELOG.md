# Release History

## 1.0.0b4 (2026-05-15)

### Features Added

- Error source classification headers: All HTTP error responses now include `x-platform-error-source` with a value of `user`, `platform`, or `upstream` to indicate which component caused the error. Developer handler exceptions and missing handler registrations are classified as `upstream`. Exceptions tagged with the platform error tag are classified as `platform` and additionally include `x-platform-error-detail` with truncated exception details (max 2048 characters) for diagnostics.
- WebSocket protocol support — `InvocationAgentServerHost` now hosts `/invocations_ws` alongside `POST /invocations`. Register the handler with the new `@app.ws_handler` decorator. The route is registered lazily on first decoration, so hosts without a registered handler return HTTP 404.
- WebSocket Ping/Pong keep-alive — disabled by default; enable by passing `InvocationAgentServerHost(ws_ping_interval=<seconds>)` or by setting the `WS_KEEPALIVE_INTERVAL` env var (auto-injected by AgentService into hosted-agent containers). The constructor argument takes precedence; `0` (or unset) disables keep-alive. Wired through to Hypercorn's `websocket_ping_interval`.
- WebSocket telemetry — structured close-event log line and OpenTelemetry span attributes `azure.ai.agentserver.invocations_ws.{session_id,close_code,duration_ms}`. Session ID honours the `FOUNDRY_AGENT_SESSION_ID` env var for HTTP/WS correlation.
- New samples: `samples/ws_invoke_agent/` (echo) and `samples/ws_bidirectional_streaming_agent/` (concurrent token streaming with cancel/bye control messages).

### Breaking Changes

### Bugs Fixed

### Other Changes

- Platform header name constants (e.g. `x-platform-error-source`, `x-platform-error-detail`) are now imported from `azure-ai-agentserver-core` (`_platform_headers` module) instead of being defined locally. Error source classification helpers remain internal to this package.

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
