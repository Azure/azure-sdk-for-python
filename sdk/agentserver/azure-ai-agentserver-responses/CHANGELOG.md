# Release History

## 1.0.0b2 (Unreleased)

### Features Added

- `FoundryStorageLoggingPolicy` — Azure Core per-retry pipeline policy that logs Foundry storage HTTP calls (method, URI, status code, duration, correlation headers) at the `azure.ai.agentserver` logger. Replaces the built-in `HttpLoggingPolicy` in the Foundry pipeline to provide single-line summaries with duration timing and log-level escalation (WARNING for 4xx/5xx).

### Bugs Fixed

- Error `code` field now uses spec-compliant values: `"invalid_request_error"` for 400/404 errors (was `"invalid_request"`, `"not_found"`, or `"invalid_mode"`), `"server_error"` for 500 errors (was `"internal_error"`).
- `RequestValidationError` default code updated from `"invalid_request"` to `"invalid_request_error"`.
- Error responses for deleted resources now correctly return HTTP 404 (was 400). Affects `GET /responses/{id}`, `GET /responses/{id}/input_items`, and `DELETE /responses/{id}` (second delete) on previously deleted responses.
- Cancel on a response in terminal state now returns the spec-compliant message `"Cannot cancel a response in terminal state."` (was `"Cannot cancel an incomplete response."`).
- SSE replay rejection messages now use spec-compliant wording:
  - Non-background responses: `"This response cannot be streamed because it was not created with background=true."`
  - Background non-stream responses: `"This response cannot be streamed because it was not created with stream=true."`
- Foundry storage errors (`FoundryResourceNotFoundError`, `FoundryBadRequestError`, `FoundryApiError`) are now explicitly caught in endpoint handlers and mapped to appropriate HTTP status codes instead of being swallowed by broad exception handlers.

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
