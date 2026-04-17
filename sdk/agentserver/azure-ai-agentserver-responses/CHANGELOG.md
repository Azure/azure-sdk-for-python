# Release History

## 1.0.0b1 (2026-04-14)

### Features Added

- Initial release of `azure-ai-agentserver-responses`.
- `ResponsesAgentServerHost` — Starlette-based host with Responses protocol endpoints (`POST /responses`, `GET /responses/{id}`, `POST /responses/{id}/cancel`, `DELETE /responses/{id}`, `GET /responses/{id}/input_items`).
- `TextResponse` — high-level convenience for text-only responses with automatic SSE lifecycle. Accepts a plain string, sync/async callable, or async iterable via the `text` parameter.
- `ResponseEventStream` — low-level builder API for emitting SSE events with full control over output items (message, function call, reasoning, file search, web search, code interpreter, image gen, MCP, custom tool).
- Convenience generators (`output_item_message()`, `output_item_function_call()`, `output_item_reasoning_item()`) and async streaming variants (`aoutput_item_message()`, etc.) for common patterns.
- New convenience generators for all output item types: `output_item_image_gen_call()`, `output_item_structured_outputs()`, `output_item_computer_call()`, `output_item_computer_call_output()`, `output_item_local_shell_call()`, `output_item_local_shell_call_output()`, `output_item_function_shell_call()`, `output_item_function_shell_call_output()`, `output_item_apply_patch_call()`, `output_item_apply_patch_call_output()`, `output_item_custom_tool_call_output()`, `output_item_mcp_approval_request()`, `output_item_mcp_approval_response()`, `output_item_compaction()`, plus async variants for all.
- `output_item_message()` and `aoutput_item_message()` now accept an `annotations` keyword argument for attaching typed `Annotation` instances (file_path, file_citation, url_citation).
- New factory methods on `ResponseEventStream`: `add_output_item_structured_outputs()`, `add_output_item_computer_call()`, `add_output_item_computer_call_output()`, `add_output_item_local_shell_call()`, `add_output_item_local_shell_call_output()`, `add_output_item_function_shell_call()`, `add_output_item_function_shell_call_output()`, `add_output_item_apply_patch_call()`, `add_output_item_apply_patch_call_output()`, `add_output_item_custom_tool_call_output()`, `add_output_item_mcp_approval_request()`, `add_output_item_mcp_approval_response()`, `add_output_item_compaction()`.
- `data_url` utility module (`is_data_url()`, `decode_bytes()`, `try_decode_bytes()`, `get_media_type()`) for parsing RFC 2397 data URLs in image/file inputs.
- `IdGenerator.new_structured_output_item_id()` with `"fco"` partition prefix.
- Samples 12–16: image generation, image input, file inputs, annotations, structured outputs.
- `ResponseContext` providing `response_id`, conversation history loading, input item access via `get_input_items()` (returns `Item` subtypes), `get_input_text()` convenience for extracting text content, isolation context, and client headers.
- `ResponsesServerOptions` for configuring default model, SSE keep-alive, shutdown grace period, and other runtime options.
- Support for all execution modes: default (synchronous), streaming (SSE), background, and streaming + background.
- Automatic SSE event replay for previously streamed responses via `?stream=true`.
- Cooperative cancellation via `asyncio.Event` and graceful shutdown integration.
- `InMemoryResponseProvider` as the default in-process state store.
- `ResponseProviderProtocol` and `ResponseStreamProviderProtocol` for custom storage implementations.
- Built-in distributed tracing with OpenTelemetry integration.
