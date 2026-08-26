# Release History

## 2.2.0b1 (Unreleased)

### Bugs Fixed

- Scoped durable multi-turn task IDs with `FOUNDRY_AGENT_SESSION_GUID` when
  available, preventing recreated same-name sessions from colliding with task
  tombstones. Existing pre-rollout active chains remain resumable through a
  legacy-ID lookup.

## 2.1.0 (2026-08-24)

### Other Changes

- Constrained runtime, development, and sample dependencies to compatible release lines.
- Updated the minimum `azure-ai-agentserver-core` dependency to the stable `2.1.0` release.

## 2.1.0b2 (2026-08-21)

### Bugs Fixed

- Restored JSON-string encoding for response-level `internal_metadata` so resilient response checkpoints round-trip through Foundry storage.
- Restored `get_request_context()` identity values while stored Responses handlers run inside durable tasks.
- `get_history_item_ids` on `InMemoryResponseProvider` and `FileResponseStore` now keeps the newest item IDs when applying `limit`. (#48514)

## 2.1.0b1 (2026-08-11)

### Breaking Changes

- The durable-response subsystem is now **opt-in**. A `store=true` response is
  wrapped in a resilient task (with crash recovery) only when the resilient task
  subsystem is enabled — which `resilient_background=True` (or
  `set_resilient_tasks_enabled(True)`) now does automatically. On a host that
  enables neither, `store=true` responses run **non-durably in-process**: they
  execute and persist (GET works), but a response in-flight when the process is
  ungracefully killed stays `in_progress` on a later GET (no mark-failed/recovery)
  — matching a plain stateless server. A one-time startup log announces which
  mode is active. Previously every responses host implicitly used the task
  subsystem (and paid the boot recovery scan) regardless of these options.
- Removed `ResponseContext.conversation_chain_metadata` and the
  `ConversationChainMetadataNamespace` protocol. Resilient response
  applications now persist cross-turn state explicitly with
  `FoundryStateStore`.

### Other Changes

- Updated the resilient Responses samples to use conversation-scoped
  `FoundryStateStore` instances directly.
- Bumped the minimum `azure-ai-agentserver-core` dependency to `>=2.1.0b1`,
  which adds the local `FoundryStateStore` fallback used by the samples.

## 2.0.0 (2026-08-07)

### Features Added

- First stable release of the Azure AI Agent Server Responses client library.

### Breaking Changes

- Removed the duplicate `azure.ai.agentserver.responses.get_input_expanded`
  export. Import it from `azure.ai.agentserver.responses.models` instead.

### Other Changes

- Bumped the minimum `azure-ai-agentserver-core` dependency to the stable `2.0.0` release.

## 2.0.0b1 (2026-08-04)

### Other Changes

- Cleaned up the public API surface by moving validation-only error helpers to a private implementation module and renaming runtime terminal/replay helpers as private.
- Bumped the minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b10`, which adds an opt-in gate for resilient-task startup recovery. The resilient Responses samples now call `set_resilient_tasks_enabled(True)` to explicitly opt in, mirroring the invocations resilient samples.

## 2.0.0b0 (2026-07-29)

### Features Added

- Marked Foundry storage public APIs as experimental.
- Raised the minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b10` so the shared experimental decorator is always available.
- Added the `azure.ai.agentserver.responses.aio` namespace with async `ResponseEventStream` convenience generators that use the same method names as the sync stream, such as `output_item_message()` and `output_item_compaction()`.
- Added local `TypedDict` model contract generation for the Responses protocol, including generated type aliases, union aliases, and `py.typed` packaging support.
- Added dict-native wire payload helpers and request validators for validating protocol payloads without depending on generated model internals.

- `ResponseContext.conversation_chain_id` (and the resilient task id it backs) now follows the native id convention: `cchain_<partition><scope>` for conversation-scoped chains, `rchain_<partition><scope>` for steerable response-linkage chains, or the `response_id` verbatim for a non-steerable one-shot. The id embeds the chain's partition key for co-location and carries a deterministic `(agent, session)` scope; `task_id == conversation_chain_id` exactly. Replaces the previous opaque `resilient-resp-<32-hex>` form.

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

- **Handlers are `async def`.** `@app.response_handler` requires an async
  handler with the `(request, context, cancellation_signal)` signature so it can
  observe the `asyncio.Event` cancellation signal.

### Breaking Changes

- Removed a-prefixed async convenience generator methods from the sync `ResponseEventStream` and sync builder classes. Use `azure.ai.agentserver.responses.aio.ResponseEventStream` for async streaming convenience methods.
- Replaced generated model classes in `azure.ai.agentserver.responses.models` with dict-native `TypedDict` contracts. Model constructors such as `ItemMessage(...)` and `CreateResponse(...)` now produce plain dictionaries instead of generated model instances.
- Removed runtime model-class behavior from response protocol models. Code should no longer rely on attribute access, `isinstance(..., ModelType)`, `.as_dict()`, or generated model base-class behavior.
- Replaced most generated enum classes with string literal type aliases. Use string values directly for protocol fields, for example `"completed"`, `"message"`, or `"function_call_output"`.

- The resilient-task input persisted for a `store=true` background response now
  carries a single `user_id_key` (the durable per-user partition key) instead of
  the previous `user_isolation_key` / `chat_isolation_key` pair; conversation
  scoping continues to use `conversation_id`.

### Migration Guide

Async response event stream helpers now live under the `aio` namespace and no longer use the `a` prefix.

Before:

```python
from azure.ai.agentserver.responses import ResponseEventStream

stream = ResponseEventStream(response_id=context.response_id, request=request)
async for event in stream.aoutput_item_message(token_stream()):
    yield event
```

After:

```python
from azure.ai.agentserver.responses.aio import ResponseEventStream

stream = ResponseEventStream(response_id=context.response_id, request=request)
async for event in stream.output_item_message(token_stream()):
    yield event
```
Builder async helpers follow the same pattern: use builders from `azure.ai.agentserver.responses.aio.streaming` and drop the `a` prefix. For example, `atext_content(...)` becomes `text_content(...)`, `aarguments(...)` becomes `arguments(...)`, and `asummary_part(...)` becomes `summary_part(...)`.

Protocol models are now dict-native. Construction still works, but the result is a dictionary:

```python
from azure.ai.agentserver.responses.models import ItemMessage, MessageContentInputTextContent

message = ItemMessage(
    role="user",
    content=[MessageContentInputTextContent(type="input_text", text="hello")],
)
```

Before:

```python
if isinstance(item, ItemMessage):
    text = item.content[0].text
```

After:

```python
if item.get("type") == "message":
    text = item.get("content", [{}])[0].get("text")
```

Before:

```python
status = ResponseStatus.COMPLETED
```

After:

```python
status = "completed"
```

### Bugs Fixed

- **Steering now works on the first turn of a conversation.** In a
  `steerable_conversations=true` deployment, the first turn (a request with no
  `conversation_id` and no `previous_response_id`) is now hosted on the
  multi-turn chain primitive instead of a one-shot task. Because all turns of a
  chain share a stable `conversation_chain_id` — and therefore the same backing
  task — a steered turn posted onto an in-flight first turn previously queued
  onto a one-shot task that completed and auto-deleted before draining the
  queued input, leaving the steered turn stuck `in_progress`. The first turn now
  suspends between turns and drains queued steering inputs correctly.

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

### Other Changes

- Bumped the minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b9`.
- Reworked the resilient responses samples: `sample_21_resilient_langgraph` is now a real-time streaming LangGraph agent that composes LangGraph's checkpointer with the framework's response checkpoints (see the "Composing an External Durable Engine" section of the handler guide), added real crash-harness e2e coverage for samples 19–22, and removed the copilot sample.
- Updated response hosting, persistence, streaming, validation, samples, and tests to operate on JSON-compatible wire dictionaries.
- Updated model generation tooling to use TypeSpec Python `models-mode=typeddict` and removed generated model shim files.

## 1.0.0b9 (2026-07-22)

### Other Changes

- Raised the `azure-ai-agentserver-core` dependency floor to `>=2.0.0b8`.

## 1.0.0b8 (2026-06-28)

### Features Added

- Container protocol version `2.0.0` support: the per-request call ID (`x-agent-foundry-call-id`) and global user ID (`x-agent-user-id`) are read from inbound requests and exposed on `ResponseContext.platform_context`. The per-request call ID is forwarded on all outbound Foundry Storage calls and bound to the request-scoped platform context so handler/tool code making raw outbound calls can forward it; `x-agent-user-id` is used only for container-side partitioning and is not forwarded to 1P services.

### Breaking Changes

- Renamed the public `IsolationContext` type to `PlatformContext`. Its fields are now `user_id_key` (from `x-agent-user-id`) and `call_id` (from `x-agent-foundry-call-id`), replacing `user_key` / `chat_key`.
- `ResponseContext.isolation` is now `ResponseContext.platform_context`.
- Response provider protocol methods now accept a `context` keyword argument (previously `isolation`).
- In-process partition enforcement is now keyed on the user ID (`x-agent-user-id`) instead of the chat isolation key.

## 1.0.0b7 (2026-05-25)

### Features Added

- Added MCP output item builder enhancements for hosted MCP relay scenarios: `ResponseEventStream.add_output_item_mcp_call()` now supports caller-supplied item IDs, and MCP call `emit_done()` supports optional `output` and `error` payloads for canonical `mcp_call` persistence and replay.

## 1.0.0b6 (2026-05-21)

### Features Added

- Error source classification headers: All HTTP error responses now include `x-platform-error-source` with a value of `user`, `platform`, or `upstream` to indicate which component caused the error. Client validation errors (400/404) are classified as `user`, Foundry storage infrastructure errors (transport failures, 5xx) as `platform`, and developer handler exceptions as `upstream`. Platform errors additionally include `x-platform-error-detail` with truncated exception details (max 2048 characters) for diagnostics. Matches the container image specification §8 error source classification.

### Breaking Changes

- Removed the automatic `invoke_agent` server span that was created on each response creation request. Trace context propagation is now handled by the core `TraceContextMiddleware`, and user-created spans inside handlers are correctly parented without framework-generated spans.
- Removed `_safe_set_attrs`, `_wrap_streaming_response`, and `_classify_error_code` internal helpers (no longer needed without framework-level span management).
- Removed OTel error tagging attributes (`azure.ai.agentserver.responses.error.code`, `azure.ai.agentserver.responses.error.message`) that were set on the framework span.

### Bugs Fixed

- Removed `ContentDecodePolicy` from the `FoundryStorageProvider` HTTP pipeline.  The policy eagerly decoded every response body as JSON and crashed with `UnicodeDecodeError` when the storage backend (or an intermediary gateway/load-balancer) returned a non-UTF-8 body — for example a gzip-compressed payload, an HTML error page, or a transport-corrupted response.  The crash propagated up before our error-classification code could see the response, masking the underlying status with a generic decode error.  Our serializers and error-extraction helpers already call `http_resp.text()` lazily with defensive error handling, so the eager decode policy was never needed.

### Other Changes

- Platform header name constants (e.g. `x-platform-error-source`, `x-platform-error-detail`) are now imported from `azure-ai-agentserver-core` (`_platform_headers` module). Error source classification helpers remain internal to this package.
- Simplified request handling: baggage entries (`response_id`, `conversation_id`, `streaming`, `x-request-id`) are still set on each request, but span creation and lifecycle management are left to downstream frameworks.

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
