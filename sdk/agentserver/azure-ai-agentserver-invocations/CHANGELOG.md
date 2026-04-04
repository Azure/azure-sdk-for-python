# Release History

## 2.0.0b1 (Unreleased)

### Features Added

- `InvocationAgentServerHost` — a Starlette-based host subclass for the invocations protocol.
- Decorator-based handler registration (`@app.invoke_handler`).
- Cooperative mixin inheritance for multi-protocol composition.

### Breaking Changes

- Renamed `InvocationHandler` → `InvocationAgentServerHost` (now inherits from `AgentServerHost`).
- Removed `server` constructor parameter — the host IS the server.
- Removed W3C Baggage propagation for cross-service correlation.

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver-invocations`.
- `InvocationHandler` for wiring invocation protocol endpoints to an `AgentHost`.
- Decorator-based handler registration (`@invocations.invoke_handler`).
- Optional `GET /invocations/{id}` and `POST /invocations/{id}/cancel` endpoints.
- `GET /invocations/docs/openapi.json` for OpenAPI spec serving.
- Invocation ID tracking and session correlation via `agent_session_id` query parameter.
- Distributed tracing with GenAI semantic convention span attributes.
- Streaming response support with span lifecycle management.
