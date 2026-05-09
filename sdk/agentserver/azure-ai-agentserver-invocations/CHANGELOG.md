# Release History

## 1.0.0b4 (Unreleased)

### Features Added

- `invocations_ws` (WebSocket) protocol support on `InvocationAgentServerHost`.
  Register a handler with the new `@app.ws_handler` decorator to host a
  full-duplex WebSocket endpoint at `/invocations_ws` on the same host that
  serves `POST /invocations`. The SDK calls `await websocket.accept()` before
  invoking the handler, runs WebSocket Ping/Pong keep-alive in the background
  (default 30 s; configurable via the new `ws_ping_interval` constructor
  argument), closes the connection cleanly on handler return, and maps
  uncaught exceptions to RFC 6455 close code `1011`. Each connection emits a
  structured close-event log line carrying `ws.session_id`, `ws.close_code`,
  and `ws.duration_ms`, and the same fields are recorded as OpenTelemetry
  span attributes. `/readiness`, OTEL export, graceful shutdown, and the
  `x-platform-server` identity header continue to be inherited from
  `azure-ai-agentserver-core`.

### Breaking Changes

### Bugs Fixed

### Other Changes

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
