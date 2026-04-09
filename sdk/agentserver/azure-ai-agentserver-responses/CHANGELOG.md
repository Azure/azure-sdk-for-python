# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver-responses`.
- `ResponsesAgentServerHost` — Starlette-based host with Responses protocol endpoints (`POST /responses`, `GET /responses/{id}`, `POST /responses/{id}/cancel`, `DELETE /responses/{id}`, `GET /responses/{id}/input_items`).
- `TextResponse` — high-level convenience for text-only responses with automatic SSE lifecycle (`create_text` and `create_text_stream` modes).
- `ResponseEventStream` — low-level builder API for emitting SSE events with full control over output items (message, function call, reasoning, file search, web search, code interpreter, image gen, MCP, custom tool).
- Convenience generators (`output_item_message()`, `output_item_function_call()`, `output_item_reasoning_item()`) and async streaming variants (`aoutput_item_message()`, etc.) for common patterns.
- `ResponseContext` providing `response_id`, conversation history loading, input item access, isolation context, and client headers.
- `ResponsesServerOptions` for configuring default model, SSE keep-alive, shutdown grace period, and other runtime options.
- Support for all execution modes: default (synchronous), streaming (SSE), background, and streaming + background.
- Automatic SSE event replay for previously streamed responses via `?stream=true`.
- Cooperative cancellation via `asyncio.Event` and graceful shutdown integration.
- `InMemoryResponseProvider` as the default in-process state store.
- `ResponseProviderProtocol` and `ResponseStreamProviderProtocol` for custom storage implementations.
- Built-in distributed tracing with OpenTelemetry integration.
