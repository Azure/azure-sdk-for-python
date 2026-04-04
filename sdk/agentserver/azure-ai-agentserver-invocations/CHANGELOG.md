# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver-invocations`.
- `InvocationAgentServerHost` — a Starlette-based host subclass for the invocations protocol.
- Decorator-based handler registration (`@app.invoke_handler`, `@app.get_invocation_handler`, `@app.cancel_invocation_handler`).
- Optional `GET /invocations/{id}` and `POST /invocations/{id}/cancel` endpoints.
- `GET /invocations/docs/openapi.json` for OpenAPI spec serving.
- Invocation ID tracking and session correlation via `agent_session_id` query parameter.
- Distributed tracing with GenAI semantic convention span attributes.
- Streaming response support with span lifecycle management.
- Cooperative mixin inheritance for multi-protocol composition.
