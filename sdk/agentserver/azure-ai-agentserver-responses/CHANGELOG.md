# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- `ResponseHandler` for Starlette-based routing of the Azure AI Responses API protocol.
- `ResponseEventStream` and scoped builder API for emitting SSE events (`message`, `function_call`, `reasoning`, `file_search`, `web_search`, `code_interpreter`, `image_gen`, `mcp`, `custom_tool`).
- `ResponseContext` providing `response_id`, history loading, and input item access.
- `ResponsesServerOptions` for configuring SSE keep-alive, history count, and other runtime options.
- `InMemoryResponseProvider` as the default in-process state store.
- `FoundryStorageProvider` for Azure AI Foundry-backed persistence.
- `ResponseProviderProtocol` and `ResponseStreamProviderProtocol` for custom storage implementations.
- Support for all execution modes: default (synchronous), streaming (SSE), background, and streaming-background.
- Automatic SSE event replay for previously streamed responses via `?stream=true`.
- Cooperative cancellation via `asyncio.Event` and graceful shutdown integration.
- S-047: Response ID override via `x-agent-response-id` HTTP header.
- S-048: Automatic `agent_session_id` resolution (payload → env var → generated UUID) and stamping on all `response.*` events.
