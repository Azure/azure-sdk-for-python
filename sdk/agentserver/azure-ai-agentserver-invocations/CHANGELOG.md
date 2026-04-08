# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver-invocations`.
- `InvocationHandler` for wiring invocation protocol endpoints to an `AgentHost`.
- Decorator-based handler registration (`@invocations.invoke_handler`).
- Optional `GET /invocations/{id}` and `POST /invocations/{id}/cancel` endpoints.
- `GET /invocations/docs/openapi.json` for OpenAPI spec serving.
- Invocation ID tracking and session correlation via `agent_session_id` query parameter.
- Distributed tracing with GenAI semantic convention span attributes.
- W3C Baggage propagation for cross-service correlation.
- Streaming response support with span lifecycle management.
