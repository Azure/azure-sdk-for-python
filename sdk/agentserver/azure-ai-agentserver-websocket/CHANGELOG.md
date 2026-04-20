# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver-conversations`.
- `ConversationHandler` for wiring conversation protocol endpoints to an `AgentHost`.
- Decorator-based handler registration (`@conversations.invoke_handler`).
- Optional `GET /conversations/{id}` and `POST /conversations/{id}/cancel` endpoints.
- `GET /conversations/docs/openapi.json` for OpenAPI spec serving.
- Conversation ID tracking and session correlation via `agent_session_id` query parameter.
- Distributed tracing with GenAI semantic convention span attributes.
- W3C Baggage propagation for cross-service correlation.
- Streaming response support with span lifecycle management.
