# Release History

## 1.0.0b4 (Unreleased)

### Features Added

- Added WebSocket invocation protocol (`invocations_ws`) — merged from the standalone `azure-ai-agentserver-websocket` package.
  - New `InvocationWSAgentServerHost` class exposing a single persistent WebSocket endpoint at `/invocations_ws/ws` for invoke / get_invocation / cancel_invocation actions, with built-in streaming support via async generators.
  - New `InvocationWSContext` and `InvocationWSError` types passed to handler functions.
  - Decorator-based handler registration: `@app.ws_invoke_handler`, `@app.ws_get_invocation_handler`, `@app.ws_cancel_invocation_handler`.
  - Built-in WebSocket keep-alive with configurable `ws_ping_interval` (default 30 s) to survive Azure APIM / Load Balancer idle timeouts.
  - OpenAPI spec discovery endpoint at `GET /invocations_ws/docs/openapi.json`.
  - Distributed tracing with GenAI semantic-convention spans (`invoke_agent`, `get_invocation`, `cancel_invocation`) and span attributes under the `azure.ai.agentserver.invocations_ws.*` namespace.
  - Cooperative multiple inheritance with `InvocationAgentServerHost` so a single host can serve both HTTP (`invocations`) and WebSocket (`invocations_ws`) protocols.

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
