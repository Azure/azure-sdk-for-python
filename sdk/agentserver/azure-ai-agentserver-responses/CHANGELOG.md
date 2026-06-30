# Release History

## 1.0.0b8 (Unreleased)

### Features Added

- **Resilient background responses.** `ResponsesServerOptions(resilient_background=True)`
  makes `store=true`, `background=true` responses survive process crashes:
  the framework persists handler progress and re-invokes the registered
  handler on the next process start when a prior attempt did not reach a
  terminal event. Defaults to `False`.

- **Steerable conversations.** `ResponsesServerOptions(steerable_conversations=True)`
  lets clients post a new turn on an in-flight conversation; the running
  handler is woken (via the cancellation signal, distinguished by
  `context.pending_input_count > 0`), drains the queued input on a fresh
  invocation, and the turns are linked in a stable conversation chain.
  Defaults to `False`.

- **`ResponseContext` resilience + steering surface.** Flat fields stamped on
  each invocation: `context.is_recovery`, `context.is_steered_turn`,
  `context.pending_input_count`, and `context.conversation_chain_id` (a stable
  identifier shared by every turn of a conversation chain, usable as a key into
  application-side session state).

- **Developer checkpoints.** `yield stream.checkpoint()` persists the
  current response snapshot at a developer-chosen boundary (gated to resilient
  background responses; a no-op otherwise; backpressured and idempotent). On a
  recovered entry, `context.persisted_response` exposes the last persisted
  snapshot so the handler can seed its stream and resume — the basis of the
  one-`OutputItem`-per-phase recovery pattern.

- **`internal_metadata`.** A single-turn, platform-internal `MutableMapping[str, Any]`
  on output items (`item.internal_metadata`) and on the response
  (`stream.internal_metadata`). It is persisted with the response (so it is
  available on recovery) and is always stripped before any client-facing
  HTTP/SSE payload, and on ingress. Distinct from the public
  `ResponseObject.metadata`.

- **`context.conversation_chain_metadata`.** Cross-turn, named-scope,
  explicit-`flush()` resilient metadata over a conversation chain, typed by the
  public `ConversationChainMetadataNamespace` Protocol.

- **`await context.exit_for_recovery()`.** A single uniform graceful-shutdown
  recovery primitive that works in every handler shape (coroutine, async
  generator, sync) — it raises `ResponseExitForRecovery` internally to leave
  the response `in_progress` for next-lifetime recovery.

- **Stream recovery.** SSE events are persisted incrementally; clients reconnect
  with `GET /responses/{id}?stream=true&starting_after=<event_id>` and resume
  from their last received event.

- **Response acceptor hook.** Register `@app.response_acceptor` to customize the
  response shape returned when a turn is queued behind an active steerable
  conversation.

- **Storage.** `FileResponseStore` is exported from
  `azure.ai.agentserver.responses` and is the default local-development store
  (under `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/responses/`) when no `store=`
  is supplied in a non-hosted environment; pass
  `store=InMemoryResponseProvider()` to opt out. The `AGENTSERVER_STATE_ROOT`
  environment variable sets the local state storage root. A typed
  `ResponseAlreadyExistsError` is raised by the response-store providers on a
  duplicate `create_response` (the idempotent-create signal on recovery).

- **Error source classification headers.** HTTP error responses carry
  `x-platform-error-source` (`user` / `platform` / `upstream`); platform errors
  also include `x-platform-error-detail` with truncated diagnostics.

- **Handlers are `async def`.** `@app.response_handler` requires an async
  handler with the `(request, context, cancellation_signal)` signature so it can
  observe the `asyncio.Event` cancellation signal.

- Added resilient samples demonstrating real SDK integrations (Claude Agent SDK,
  Copilot SDK, LangGraph) and resilient streaming / steering / multi-turn
  patterns.

### Bugs Fixed

- **`context.conversation_chain_id` is now stable across every turn of a
  conversation.** Previously it returned the raw `previous_response_id` (the
  immediate predecessor), so it shifted on every turn after the second — breaking
  its use as a stable per-conversation key (e.g. an upstream SDK session id). It
  is now derived from the partition key embedded in the chain's response IDs
  (which every turn shares), so all turns of a chain — and the resilient task
  that backs them — resolve to the same identity. The value is now an opaque,
  agent/session-scoped hash rather than a raw id. (Known limitation: a client
  that supplies its own `response_id` with a mismatched embedded partition can
  shift the chain identity for later turns.)

- **A resilient task that fails to start now fails the request instead of
  silently running without durability.** Previously, when `resilient_background`
  was in effect but the resilient task could not be started (e.g. the task store
  rejected the write), the server fell back to running the handler on a
  non-durable, connection-scoped task while still returning a healthy-looking
  response — so the response had no crash recovery and the failure was hidden.
  Such a failure is now surfaced immediately: non-streaming requests return
  `HTTP 500` with `x-platform-error-source: platform` (the same classification
  used for storage failures), and streaming requests emit a standalone `error`
  event. In a hosted environment a missing task subsystem is likewise treated as
  a platform failure. Local and test deployments without the task subsystem
  installed are unaffected and continue to run the handler in-process.

- **Resilient background streaming responses now engage resilience even when SSE
  keep-alive is enabled.** Previously the resilient task was created only on the
  no-keep-alive streaming path, so when SSE keep-alive was enabled (e.g. the
  hosted platform sets `SSE_KEEPALIVE_INTERVAL`), a `store=true`,
  `background=true`, `stream=true` response ran the handler inline on the
  request connection and never created a resilient task. Such responses could
  hang `in_progress` on a client/proxy disconnect and were not recoverable.
  Stored responses now always run via the resilient task; keep-alive comments are
  interleaved into the wire stream while the resilient body runs independently of
  the client connection.

## 1.0.0b5 (2026-04-22)

### Features Added

- All HTTP responses now include an `x-request-id` header for request correlation. Value is resolved in priority order: OTEL trace ID → incoming `x-request-id` header → new UUID.
- Error responses (4xx/5xx) with a JSON `error` body are automatically enriched with `error.additionalInfo.request_id` matching the `x-request-id` response header, enabling client-side error correlation.
- Persistence failure resilience — when storage operations fail, responses now complete gracefully with `status: "failed"` and `error.code: "storage_error"` instead of crashing or leaving responses permanently stuck at `in_progress`. Covers all execution modes (streaming, background+streaming, background+non-streaming, synchronous). For streaming responses, terminal SSE events are buffered, persistence is attempted, and on failure the terminal event is replaced with `response.failed` carrying `error_code="storage_error"`. Synchronous persistence failures return HTTP 500 with the storage error details.
- Foundry storage logging now includes the `traceparent` header (W3C distributed trace ID) in all log messages, enabling correlation between SDK log entries and backend distributed traces.

### Bugs Fixed

- Fixed crash in `FoundryStorageLoggingPolicy` when a transport-level failure (DNS resolution, connection refused, timeout) occurs before any HTTP response is received. The policy previously attempted to access `response.headers` unconditionally, raising an unrelated exception that masked the real transport error. Transport failures are now logged at ERROR level and the original exception propagates cleanly.
- Fixed `ResponseContext.get_input_text()` and `ResponseContext.get_input_items()` silently dropping text when `ItemMessage.content` is a plain string. String content is now correctly expanded into `MessageContentInputTextContent`.

### Other Changes

- Removed `x-ms-request-id` from Foundry storage response logging (unused service header).

## 1.0.0b4 (2026-04-19)

### Bugs Fixed

- `DELETE /responses/{id}` no longer returns intermittent 404 when the background task's eager eviction races with the delete handler. Previously, `try_evict` could remove the record from in-memory state between the handler's `get()` and `delete()` calls, causing `delete()` to return `False` and producing a spurious 404. The handler now falls through to the resilient provider when the in-memory delete fails due to a concurrent eviction.
- `POST /responses` with `background=true, stream=false` now correctly returns `status: "in_progress"` instead of `"completed"`. Handlers that yield events synchronously (no `await` between yields — the normal pattern with `ResponseEventStream`) would cause the background task to run to completion before `run_background` captured the initial snapshot. A cooperative yield after `response_created_signal.set()` now ensures the POST handler resumes promptly.
- Conversation history IDs (`previous_response_id`, `conversation_id`) are now validated eagerly before the handler is invoked. A nonexistent reference now returns a 404 error to the client immediately, instead of being silently ignored or surfacing as an opaque error deep inside the handler. The prefetched IDs are reused by `ResponseContext.get_history()`, eliminating a redundant provider call.

## 1.0.0b3 (2026-04-19)

### Bugs Fixed

- Background non-stream finalization now passes isolation keys to `update_response` — previously the `isolation=` kwarg was missing, causing Foundry storage to return 404 when isolation headers were present (the response was created in a scoped partition but the update targeted the unscoped partition). This left responses permanently stuck at `in_progress`.

## 1.0.0b2 (2026-04-17)

### Features Added

- Startup configuration logging — `ResponsesAgentServerHost` logs storage provider type, default model, default fetch history count, and shutdown grace period at INFO level during construction.
- `InboundRequestLoggingMiddleware` moved to `azure-ai-agentserver-core` — pure-ASGI middleware that logs every inbound HTTP request at INFO level (start) and at INFO or WARNING level (completion). Now wired automatically by `AgentServerHost` so all protocol hosts get consistent inbound logging. Includes method, path (no query string), status code, duration in milliseconds, and correlation headers (`x-request-id`, `x-ms-client-request-id`). Status codes >= 400 are logged at WARNING; unhandled exceptions are logged as status 500 at WARNING. OpenTelemetry trace ID is included when an active trace exists.
- Handler-level diagnostic logging — all five endpoint handlers (`POST /responses`, `GET /responses/{id}`, `DELETE /responses/{id}`, `POST /responses/{id}/cancel`, `GET /responses/{id}/input_items`) now emit INFO-level logs at entry and on success, including response ID, status, and output count where applicable.
- Orchestrator handler invocation logging — logs the handler function name and response ID at INFO level before each handler invocation.
- Chat isolation key enforcement — when a response is created with an `x-agent-chat-isolation-key` header, subsequent GET, DELETE, Cancel, and InputItems requests must include the same key. Mismatched or missing keys return an indistinguishable 404 to prevent cross-chat information leakage. Backward-compatible: no enforcement when the response was created without a key.
- Malformed response ID validation — all endpoints that accept a `response_id` path parameter now reject malformed IDs (wrong prefix, too short) with HTTP 400 (`error.type: "invalid_request_error"`, `error.code: "invalid_parameters"`, `param: "responseId{<value>}"`) before touching storage. The `previous_response_id` field in POST body is also validated.
- `FoundryStorageLoggingPolicy` — Azure Core per-retry pipeline policy that logs Foundry storage HTTP calls (method, URI, status code, duration, correlation headers) at the `azure.ai.agentserver` logger. Replaces the built-in `HttpLoggingPolicy` in the Foundry pipeline to provide single-line summaries with duration timing and log-level escalation (WARNING for 4xx/5xx).
- `FoundryStorageLoggingPolicy` now logs `x-request-id` and `apim-request-id` response headers from Foundry in addition to `x-ms-client-request-id` and `x-ms-request-id`, matching the .NET SDK's diagnostic detail. This enables verifying that the inbound trace-id round-trips through Foundry storage calls.
- Foundry storage User-Agent — outbound HTTP requests to Foundry storage now carry a `User-Agent` header reflecting the exact `x-platform-server` value (lazy callback via `_ServerVersionUserAgentPolicy`) so upstream logs can correlate inbound and outbound traffic.

### Bugs Fixed

- SSE stream replay now works when the response provider does not implement `ResponseStreamProviderProtocol` (e.g. `FoundryStorageProvider`). Previously, `GET /responses/{id}?stream=true` returned HTTP 400 after eager eviction because no stream provider was configured. The host now auto-provisions an in-memory stream provider as a fallback.
- `item_reference` inputs are now resolved at persistence time — when a `POST /responses` request includes `item_reference` entries in its input, they are batch-resolved via the provider before being stored. Previously, `item_reference` entries were silently dropped during input expansion, so `GET /responses/{id}/input_items` would only return inline items. This matches the .NET SDK behavior (`GetInputItemsForPersistenceAsync`).
- Post-eviction chat isolation — after eager eviction, GET, DELETE, Cancel, and InputItems requests with missing or mismatched `x-agent-chat-isolation-key` headers now correctly fall through to Foundry storage (which returns HTTP 400) instead of being blocked locally with HTTP 404. In-flight isolation enforcement is unchanged.
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
