# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver-websocket`.
- `WebsocketHandler` for wiring websocket protocol endpoints to an `AgentHost`.
- Decorator-based handler registration (`@websocket.invoke_handler`).
- Optional `GET /websocket/{id}` and `POST /websocket/{id}/cancel` endpoints.
- `GET /websocket/docs/openapi.json` for OpenAPI spec serving.
- Websocket ID tracking and session correlation via `agent_session_id` query parameter.
- Distributed tracing with GenAI semantic convention span attributes.
- W3C Baggage propagation for cross-service correlation.
- Streaming response support with span lifecycle management.
