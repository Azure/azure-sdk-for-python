# Handler Implementation Guide

> Developer guidance for implementing response handlers — the single integration point for building Azure AI Responses API servers with this library.

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [TextResponse](#textresponse)
- [Server Registration](#server-registration)
- [Handler Signature](#handler-signature)
- [ResponseEventStream](#responseeventstream)
  - [Method Naming Conventions](#method-naming-conventions)
  - [Setting Custom Metadata](#setting-custom-metadata)
  - [Builder Pattern](#builder-pattern)
- [ResponseContext](#responsecontext)
- [Emitting Output](#emitting-output)
  - [Text Messages](#text-messages)
  - [Function Calls (Tool Use)](#function-calls-tool-use)
  - [Function Call Output](#function-call-output)
  - [Reasoning Items](#reasoning-items)
  - [Multiple Output Items](#multiple-output-items)
  - [Other Tool Call Types](#other-tool-call-types)
- [Handling Input](#handling-input)
- [Cancellation](#cancellation)
- [Error Handling](#error-handling)
  - [Validation Pipeline](#validation-pipeline)
- [Response Lifecycle](#response-lifecycle)
  - [Terminal Event Requirement](#terminal-event-requirement)
  - [Signalling Incomplete](#signalling-incomplete)
  - [Token Usage Reporting](#token-usage-reporting)
- [Configuration](#configuration)
  - [Distributed Tracing](#distributed-tracing)
  - [SSE Keep-Alive](#sse-keep-alive)
- [Resilience](#resilience)
  - [Mental Model](#mental-model)
  - [The Recovery Loop](#the-recovery-loop)
  - [Stream Checkpoints](#stream-checkpoints)
  - [Item and Response `internal_metadata`](#item-and-response-internal_metadata)
  - [Which metadata facility?](#which-metadata-facility)
  - [Default Pattern (recovery-aware)](#default-pattern-recovery-aware)
  - [Fallback Pattern (no opt-in)](#fallback-pattern-no-opt-in)
  - [Upstream History Pattern](#upstream-history-pattern)
  - [Watermark Pattern](#watermark-pattern)
  - [Resumption Response Construction](#resumption-response-construction)
  - [Composing an External Durable Engine (e.g. LangGraph)](#composing-an-external-durable-engine-eg-langgraph)
- [Best Practices](#best-practices)
- [Common Mistakes](#common-mistakes)

---

## Overview

The library handles all protocol concerns — routing, serialization, SSE framing,
`stream`/`background` mode negotiation, status lifecycle, and error shapes. You
register one handler function via the `@app.response_handler` decorator. Your handler
receives a `CreateResponse` request and produces response events. The library wraps
these events into the correct HTTP response format based on the client's requested
mode.

You do **not** need to think about:

- Whether the client requested JSON or SSE streaming
- Whether the response is running in the foreground or background
- HTTP status codes, content types, or error envelopes
- Sequence numbers or response IDs

The library manages all of this. Your handler just provides text or yields events.

For most handlers, `TextResponse` eliminates even the event plumbing — you provide
text (or a stream of tokens) and the library does the rest. For full control over
every SSE event, use `ResponseEventStream`.

---

## Getting Started

### Minimal Handler

The simplest handler uses `TextResponse` — a convenience class that handles the
full SSE event lifecycle for text-only responses:

```python
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

app = ResponsesAgentServerHost()


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    text = await context.get_input_text()
    return TextResponse(context, request, text=f"Echo: {text}")
```

### Running the Server

```python
app.run()
```

That's it. One call starts a Hypercorn host with OpenTelemetry, health checks,
identity headers, and all Responses protocol endpoints (`POST /responses`,
`GET /responses/{id}`, `POST /responses/{id}/cancel`, and more).

**Next steps:** See [TextResponse](#textresponse) for streaming text and more
patterns. For full SSE control (function calls, reasoning items, multiple outputs),
see [ResponseEventStream](#responseeventstream). For hosting options beyond the
default, see [Server Registration](#server-registration).

---

## TextResponse

A standalone convenience class for the most common case — returning a single text
message. `TextResponse` handles the full event lifecycle internally
(`response.created` → `response.in_progress` → message/content events →
`response.completed`).

### Complete Text

When you have the full text available at once:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    text = await context.get_input_text()
    return TextResponse(context, request, text=f"Echo: {text}")
```

`text` can also be a sync or async callable — useful when the answer requires I/O:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    async def _build():
        text = await context.get_input_text()
        answer = await model.generate(text)
        return answer

    return TextResponse(context, request, text=_build)
```

### Streaming Text

When an LLM produces tokens incrementally, pass an `AsyncIterable[str]` to
`text`. Each chunk becomes a separate `response.output_text.delta` SSE event:

```python
import asyncio

@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    async def generate_tokens():
        tokens = ["Hello", ", ", "world", "!"]
        for token in tokens:
            await asyncio.sleep(0.05)
            yield token

    return TextResponse(context, request, text=generate_tokens())
```

### Setting Response Properties

Use the optional `configure` callback to set properties like `temperature` or
`metadata` before the `response.created` event:

```python
return TextResponse(
    context,
    request,
    configure=lambda response: setattr(response, "temperature", 0.7),
    text="Hello!",
)
```

### When to Use TextResponse vs ResponseEventStream

| Use `TextResponse` when... | Use `ResponseEventStream` when... |
|---|---|
| Your handler returns a single text message | You need multiple output types (reasoning + message, function calls) |
| You want minimal boilerplate | You need fine-grained delta control |
| The focus of your handler is business logic, not event plumbing | You need to emit function calls, reasoning items, or tool calls |

> **Note:** `TextResponse` handles all lifecycle events internally — the contract
> described in [ResponseEventStream](#responseeventstream) (emit_created → output →
> terminal event) applies only when you use `ResponseEventStream` directly.

---

## Server Registration

### Default: Decorator Pattern

The primary way to register a handler is the `@app.response_handler` decorator:

```python
app = ResponsesAgentServerHost()

@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    return TextResponse(context, request, text="Hello!")

app.run()
```

### With Options

Pass `ResponsesServerOptions` to configure runtime behaviour:

```python
from azure.ai.agentserver.responses import ResponsesServerOptions

app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(
        default_model="gpt-4o",
        default_fetch_history_count=50,
    ),
)
```

### Multi-Protocol Composition

For agents that serve both Invocations and Responses protocols, use cooperative
(mixin) inheritance:

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.responses import ResponsesAgentServerHost

class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
    pass

app = MyHost()
```

### Self-Hosting (Mount into existing app)

Because `ResponsesAgentServerHost` **is** a Starlette ASGI application, it can be
mounted as a sub-application:

```python
from starlette.applications import Starlette
from starlette.routing import Mount

responses_app = ResponsesAgentServerHost()

@responses_app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    return TextResponse(context, request, text="Hello!")

app = Starlette(routes=[
    Mount("/api", app=responses_app),
])
# Now responses are at POST /api/responses
```

### Route Mapping

The host automatically maps five endpoints:

- `POST /responses` — Create a response
- `GET /responses/{response_id}` — Retrieve a response (JSON or SSE replay)
- `POST /responses/{response_id}/cancel` — Cancel a response
- `DELETE /responses/{response_id}` — Delete a response
- `GET /responses/{response_id}/input_items` — List input items (paginated)

### Custom Response Provider

The server delegates state persistence and event streaming to a pluggable
provider. The default in-memory implementation works for single-instance
deployments.

```python
from azure.ai.agentserver.responses import ResponsesAgentServerHost

# Use default in-memory provider (no configuration needed)
app = ResponsesAgentServerHost()

# Or provide a custom store
app = ResponsesAgentServerHost(store=MyCustomProvider())
```

When deployed to Azure AI Foundry, persistence is enabled automatically —
no custom provider registration is needed.

---

## Handler Signature

```python
@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    ...
```

| Parameter | Description |
|-----------|-------------|
| `request` | The deserialized `CreateResponse` body from the client (model, input, tools, instructions, etc.) |
| `context` | The handler-facing `ResponseContext` — request-scoped state, async input/history helpers, the shutdown signal (`context.shutdown`), cancellation cause flags (`context.client_cancelled`), and recovery + steering fields (`context.is_recovery`, `context.is_steered_turn`, `context.pending_input_count`, `context.conversation_chain_metadata`, `context.exit_for_recovery()`) |
| `cancellation_signal` | An `asyncio.Event` set on client cancel (`/cancel` API or non-bg POST disconnect) or steering pressure. Distinct from `context.shutdown` — shutdown does NOT fire this signal; handlers that care about both must observe each independently. |

Handlers MUST be `async def` and take exactly three positional
parameters `(request, context, cancellation_signal)`. Sync handlers and
the 2-arg signature `(request, context)` are hard-rejected at
decoration time with `TypeError`. Observe cancellation via
`cancellation_signal.is_set()`; observe shutdown via
`context.shutdown.is_set()`; see the [Cancellation](#cancellation)
section for the cause-boolean shape and the
[Shutdown](#shutdown-and-recovery) section for the recovery primitive.

Your handler can either:

1. **Return a `TextResponse`** — the simplest approach for text-only responses.
2. **Be an async generator** — `yield` events one at a time for full control.

The library consumes the events, assigns sequence numbers, manages the response
lifecycle, and delivers them to the client.

### TextResponse handlers

Use `return` — no generator yield needed:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    return TextResponse(context, request, text="Hello!")
```

### Generator handlers (ResponseEventStream)

Use `yield` for full control. Handlers are always `async def`; they
can be plain async functions that return an iterable, or async
generators that `yield` events directly:

```python
# Async generator — yields events one at a time
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    for event in stream.output_item_message("Hello!"):
        yield event
    yield stream.emit_completed()

# Async generator with an async builder (token streaming)
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    async for event in stream.aoutput_item_message(token_stream()):
        yield event
    yield stream.emit_completed()
```

---

## ResponseEventStream

For full control over every SSE event — multiple output types, custom Response
properties, streaming deltas — use `ResponseEventStream`. This is the lower-level
counterpart to `TextResponse`:

```python
stream = ResponseEventStream(response_id=context.response_id, request=request)

# 1. Signal response creation
yield stream.emit_created()
yield stream.emit_in_progress()

# 2. Build and emit output
message = stream.add_output_item_message()
yield message.emit_added()

text = message.add_text_content()
yield text.emit_added()
yield text.emit_delta("Hello, world!")
yield text.emit_text_done("Hello, world!")

yield text.emit_done()
yield message.emit_done()

# 3. Signal completion
yield stream.emit_completed()
```

Create a `ResponseEventStream` at the start of your handler:

```python
stream = ResponseEventStream(response_id=context.response_id, request=request)
```

It provides:

| Category | Methods |
|----------|---------|
| Response | `stream.response` — the underlying Response object. Set custom metadata or instructions before `emit_created()` |
| Lifecycle | `emit_created()`, `emit_in_progress()`, `emit_completed()`, `emit_failed()`, `emit_incomplete()` |
| Output factories | `add_output_item_message()`, `add_output_item_function_call()`, `add_output_item_reasoning_item()`, and more |
| Convenience generators | `output_item_message()`, `output_item_function_call()`, `output_item_reasoning_item()`, and async variants |

### Method Naming Conventions

`ResponseEventStream` and its builders use a consistent naming scheme. Knowing the
prefixes tells you what any method does at a glance:

#### Stream-level methods

| Prefix | Example | Returns | Purpose |
|--------|---------|---------|----------|
| `emit_*` | `emit_created()`, `emit_completed()` | A specific event subtype | Produce one response-lifecycle event |
| `add_*` | `add_output_item_message()` | A builder object | Create a builder for step-by-step event emission |
| `output_item_*` | `output_item_message(text)` | Generator of events | Convenience — yields the complete output-item lifecycle |
| `aoutput_item_*` | `aoutput_item_message(stream)` | Async generator | Async convenience for streaming `AsyncIterable[str]` |

#### Builder-level methods

| Prefix | Example | Returns | Purpose |
|--------|---------|---------|----------|
| `emit_*` | `emit_added()`, `emit_done()`, `emit_delta(chunk)` | A specific event subtype | Produce one event in the builder's lifecycle |
| `add_*` | `add_text_content()`, `add_summary_part()` | A child builder | Create a nested content builder |

> **Typed returns:** Every `emit_*` method returns its specific event model
> subtype — for example, `emit_created()` returns `ResponseCreatedEvent` and
> `emit_delta(chunk)` returns `ResponseTextDeltaEvent`. This enables type-safe
> downstream processing and IDE autocompletion without manual casts.

**Rule of thumb:** If a method returns a single event, it starts with `emit_`. If
it returns a builder, it starts with `add_`. If it returns a generator of events,
it's named after the content it produces (`output_item_message`, etc.).

Every convenience generator has two variants:

| Variant | Signature | When to use |
|---------|-----------|-------------|
| **Sync** | `output_item_message(text: str)` → `Iterable` | You have the full value up-front |
| **Async** | `aoutput_item_message(stream: AsyncIterable[str])` → `AsyncIterable` | You're receiving chunks from a model |

> **Tip:** Start with `TextResponse`. If you need convenience generators
> (`output_item_message`), use those. Drop down to `add_*` builders only when you
> need fine-grained control.

### Setting Custom Metadata

Use the `response` property to set custom metadata or instructions before emitting
the created event:

```python
stream = ResponseEventStream(response_id=context.response_id, request=request)

# Set custom metadata (overrides what was copied from the request) (preserved in all response.* events)
stream.response.metadata = {"handler_version": "2.0", "region": "us-west-2"}

# Set custom instructions
stream.response.instructions = "You are a helpful assistant."

yield stream.emit_created()
```

If the handler does not set metadata or instructions, the library automatically
copies them from the original `CreateResponse` request.

The library also auto-populates `conversation` and `previous_response_id` on the
response from the original request.

**Important:** Do not add output items directly to `stream.response.output`. Use
the output builder factories instead — the library tracks output items through
`output_item.added` events and will detect direct manipulation as a handler error.

Every `ResponseEventStream` handler must:

1. Call `stream.emit_created()` first — this creates the `response.created` SSE
   event. Mandatory and must be the first event yielded.
2. Call `stream.emit_in_progress()` — this creates the `response.in_progress` SSE
   event.
3. Emit output items using the builder factories.
4. End with exactly one terminal event: `stream.emit_completed()`,
   `stream.emit_failed()`, or `stream.emit_incomplete()`.

**Bad handler consequences:**

| Violation | Result |
|-----------|--------|
| First event is not `response.created` | HTTP 500 error, no persistence |
| Direct `response.output` manipulation detected | `response.failed` (post-created) or HTTP 500 (pre-created) |
| Empty generator (no events) | HTTP 500 error, no persistence |
| Throws before `response.created` | HTTP 500 error, no persistence |
| Ends without terminal event or error | The library emits `response.failed` automatically |
| Throws after `response.created` | The library emits `response.failed`, persists failed state |

> **Note:** `TextResponse` handles all lifecycle events internally — the contract
> above applies only when you use `ResponseEventStream` directly.

### Builder Pattern

Output is constructed through a builder hierarchy that enforces correct event
ordering:

```
ResponseEventStream
  └── OutputItemBuilder (message, function call, reasoning, etc.)
        └── Content builders (text, refusal, summary, etc.)
```

Each builder tracks its lifecycle state and will raise if you emit events out of
order. This prevents protocol violations at development time.

**Key rule:** Every builder that you start (`emit_added`) must be finished
(`emit_done`). Unfinished builders result in malformed responses.

---

## ResponseContext

```python
class ResponseContext:
    response_id: str                                # Library-generated response ID
    conversation_chain_id: str                      # Stable identity for the multi-turn chain (see Resilience)
    request: CreateResponse | None                  # Parsed request model
    client_headers: dict[str, str]                  # x-client-* headers from request (keys lowercase)
    query_parameters: dict[str, str]                # Query parameters from the HTTP request
    platform_context: PlatformContext               # Platform identity: user_id_key (x-agent-user-id) + call_id (x-agent-foundry-call-id)

    # Shutdown surface (distinct from per-request cancellation_signal — see Cancellation)
    shutdown: asyncio.Event                         # Set on graceful server shutdown
    client_cancelled: bool                          # True for explicit /cancel call OR non-bg POST disconnect

    async def exit_for_recovery() -> NoReturn
        # Unified graceful-shutdown recovery primitive — call as a bare
        # `await context.exit_for_recovery()` in any handler shape. Raises
        # internally to leave the response in_progress for next-lifetime recovery.

    # Recovery + steering classifiers (see Resilience)
    is_recovery: bool                               # True on a crash-recovered re-entry
    persisted_response: ResponseObject | None       # Entry-only: last resiliently-persisted snapshot
                                                    # (last stream.checkpoint(), else created snapshot,
                                                    # else None). See Resilience → persisted_response.
    is_steered_turn: bool                           # True on the drain re-entry that follows a steering input
    pending_input_count: int                        # Live count of queued steering inputs
    conversation_chain_metadata: ConversationChainMetadataNamespace      # Persistent checkpoint store (Mapping + Callable facade)

    # Async helpers
    async def get_input_items() -> Sequence[Item]   # Resolved input items as Item subtypes
    async def get_input_text() -> str               # Extract all text content from input items
    async def get_history() -> Sequence[OutputItem]  # Conversation history items
```

### Input Items — `get_input_items()`

Returns the caller's input items as `Item` subtypes, fully resolved:

```python
input_items = await context.get_input_items()
```

- Inline items are returned as-is — the same `Item` subtypes from the original
  request (e.g. `ItemMessage`, `FunctionCallOutputItemParam`)
- `ItemReferenceParam` entries are batch-resolved via the provider and converted
  to concrete `Item` subtypes
- Unresolvable references (provider returns ``None``) are silently dropped
- Input order is preserved
- Lazy — computed once and cached

Pass `resolve_references=False` to skip reference resolution (item references are
left as `ItemReferenceParam` in the returned sequence):

```python
input_items = await context.get_input_items(resolve_references=False)
```

### Input Text — `get_input_text()`

Convenience method that resolves input items, filters for `ItemMessage` items,
and joins all `MessageContentInputTextContent` text values:

```python
text = await context.get_input_text()
```

Returns `""` if no text content is found. Accepts `resolve_references=False` to
skip reference resolution.

### Conversation History — `get_history()`

Returns resolved output items from previous responses in the conversation chain:

```python
history = await context.get_history()
```

- Two-step resolution: resolves history item IDs, then fetches actual items
- Ascending order — oldest-first
- Configurable limit via `ResponsesServerOptions.default_fetch_history_count`
  (default: 100)
- Lazy singleton — computed once and cached

### Client Headers

Returns `x-client-*` prefixed headers forwarded from the original HTTP request:

```python
client_headers = context.client_headers
request_id = client_headers.get("x-client-request-id")
```

---

## Emitting Output

Each output type can be emitted using either **convenience generators**
(recommended — less code, correct by construction) or **builders** (when you need
fine-grained control). The examples below show both, starting with the simpler
approach.

> **Tip:** For simple text-only responses, [`TextResponse`](#textresponse) is even
> simpler than `ResponseEventStream` — it handles the entire event lifecycle in a
> single call.

### Text Messages

#### Using TextResponse (simplest)

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    return TextResponse(context, request, text="Hello, world!")
```

#### Using convenience generators

```python
stream = ResponseEventStream(response_id=context.response_id, request=request)
yield stream.emit_created()
yield stream.emit_in_progress()

# Complete text — full value up-front
for evt in stream.output_item_message("Hello, world!"):
    yield evt

yield stream.emit_completed()
```

Streaming from an LLM:

```python
async for evt in stream.aoutput_item_message(get_token_stream()):
    yield evt
```

#### Using builders (fine-grained control)

When you need multiple content parts in one message, emit refusal content, set
custom properties on the output item, or interleave non-event work between builder
calls:

```python
message = stream.add_output_item_message()
yield message.emit_added()

text = message.add_text_content()
yield text.emit_added()

# Stream text incrementally
yield text.emit_delta("First chunk of text. ")
yield text.emit_delta("Second chunk. ")

# Finalize the text content
yield text.emit_text_done("First chunk of text. Second chunk. ")

yield text.emit_done()
yield message.emit_done()
```

### Function Calls (Tool Use)

When your handler needs the client to execute a function (tool) and return the
result. Function calls require `ResponseEventStream` — `TextResponse` cannot emit
them.

#### Using convenience generators

```python
yield stream.emit_created()
yield stream.emit_in_progress()

args = json.dumps({"location": "Seattle"})
for evt in stream.output_item_function_call("get_weather", "call_1", args):
    yield evt

yield stream.emit_completed()
```

#### Using builders (fine-grained control)

```python
func_call = stream.add_output_item_function_call("get_weather", "call_weather_1")
yield func_call.emit_added()

arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
yield func_call.emit_arguments_delta(arguments)
yield func_call.emit_arguments_done(arguments)
yield func_call.emit_done()
```

The client receives the function call, executes it locally, and sends a new request
with the function output as input. Your handler then processes the result on the
next turn.

#### Multi-Turn Function Calling

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    tool_output = await _find_function_call_output(context)

    if tool_output is not None:
        # Turn 2+: Process the function result and respond
        yield stream.emit_created()
        yield stream.emit_in_progress()
        async for event in stream.aoutput_item_message(f"The result is: {tool_output}"):
            yield event
        yield stream.emit_completed()
    else:
        # Turn 1: Request a function call
        yield stream.emit_created()
        yield stream.emit_in_progress()
        args = json.dumps({"location": "Seattle"})
        async for event in stream.aoutput_item_function_call("get_weather", "call_weather_1", args):
            yield event
        yield stream.emit_completed()
```

### Function Call Output

When your handler itself executes a tool and includes the output in the response
(no client round-trip):

```python
for evt in stream.output_item_function_call_output("call_weather_1", weather_json):
    yield evt
```

Function call outputs have no deltas — only `output_item.added` and
`output_item.done`.

### Reasoning Items

Emit reasoning (chain-of-thought) before the main response. Reasoning items
require `ResponseEventStream`.

#### Using convenience generators

```python
yield stream.emit_created()
yield stream.emit_in_progress()

# Output 0: Reasoning
for evt in stream.output_item_reasoning_item("Let me think about this..."):
    yield evt

# Output 1: Message with the answer
for evt in stream.output_item_message("The answer is 42."):
    yield evt

yield stream.emit_completed()
```

#### Using builders (fine-grained control)

```python
reasoning = stream.add_output_item_reasoning_item()
yield reasoning.emit_added()

summary = reasoning.add_summary_part()
yield summary.emit_added()
yield summary.emit_text_delta("Let me think about this...")
yield summary.emit_text_done("Let me think about this...")
yield summary.emit_done()
yield reasoning.emit_done()
```

### Multiple Output Items

A single response can contain multiple output items. Each gets an auto-incrementing
output index:

```python
yield stream.emit_created()
yield stream.emit_in_progress()

# Output 0
for evt in stream.output_item_message("First message."):
    yield evt

# Output 1
for evt in stream.output_item_message("Second message."):
    yield evt

yield stream.emit_completed()
```

### Other Tool Call Types

The library provides specialised builders for each tool call type:

| Builder | Factory method | Sub-item convenience |
|---------|---------------|---------------------|
| `OutputItemCodeInterpreterCallBuilder` | `add_output_item_code_interpreter_call()` | `code()` |
| `OutputItemFileSearchCallBuilder` | `add_output_item_file_search_call()` | — |
| `OutputItemWebSearchCallBuilder` | `add_output_item_web_search_call()` | — |
| `OutputItemImageGenCallBuilder` | `add_output_item_image_gen_call()` | — |
| `OutputItemMcpCallBuilder` | `add_output_item_mcp_call(server_label, name)` | `arguments()` |
| `OutputItemCustomToolCallBuilder` | `add_output_item_custom_tool_call(call_id, name)` | `input_data()` |
| `OutputItemBuilder` | `add_output_item_structured_outputs()` | — |
| `OutputItemBuilder` | `add_output_item_computer_call()` | — |
| `OutputItemBuilder` | `add_output_item_computer_call_output()` | — |
| `OutputItemBuilder` | `add_output_item_local_shell_call()` | — |
| `OutputItemBuilder` | `add_output_item_local_shell_call_output()` | — |
| `OutputItemBuilder` | `add_output_item_function_shell_call()` | — |
| `OutputItemBuilder` | `add_output_item_function_shell_call_output()` | — |
| `OutputItemBuilder` | `add_output_item_apply_patch_call()` | — |
| `OutputItemBuilder` | `add_output_item_apply_patch_call_output()` | — |
| `OutputItemBuilder` | `add_output_item_custom_tool_call_output()` | — |
| `OutputItemBuilder` | `add_output_item_mcp_approval_request()` | — |
| `OutputItemBuilder` | `add_output_item_mcp_approval_response()` | — |
| `OutputItemBuilder` | `add_output_item_compaction()` | — |

Each builder enforces its own lifecycle ordering.

#### Convenience generators

For simple output items that only need an added→done pair, convenience generators
avoid the builder ceremony entirely:

```python
# Image generation — emits full lifecycle automatically
for evt in stream.output_item_image_gen_call(result_base64):
    yield evt

# Structured outputs
for evt in stream.output_item_structured_outputs({"sentiment": "positive", "confidence": 0.95}):
    yield evt

# Message with annotations
from azure.ai.agentserver.responses.models import FilePath, UrlCitationBody
for evt in stream.output_item_message(
    "Here are your sources.",
    annotations=[
        FilePath(file_id="/reports/summary.pdf", index=0),
        UrlCitationBody(url="https://example.com", start_index=0, end_index=5, title="Link"),
    ],
):
    yield evt
```

All convenience generators have async variants (prefixed with `a`):
`aoutput_item_image_gen_call()`, `aoutput_item_structured_outputs()`, etc.

#### `data_url` utility

Parse RFC 2397 data URLs from image/file inputs:

```python
from azure.ai.agentserver.responses import data_url

if data_url.is_data_url(value):
    raw_bytes = data_url.decode_bytes(value)
    media_type = data_url.get_media_type(value)  # e.g. "image/png"
```

---

## Handling Input

Access the client's input via the `ResponseContext`:

```python
# All resolved input items as Item subtypes
input_items = await context.get_input_items()

# Convenience: extract all text content as a single string
text = await context.get_input_text()
```

The `CreateResponse` object also provides:

- `request.model` — the requested model name
- `request.instructions` — system instructions
- `request.tools` — registered tool definitions
- `request.metadata` — key-value metadata pairs
- `request.store` — whether to persist the response
- `request.stream` — whether SSE streaming was requested
- `request.background` — whether background mode was requested

---

## Cancellation

The handler observes cancellation via two **distinct** surfaces and a
cause-flag boolean:

- **`cancellation_signal`** (3rd positional handler arg, `asyncio.Event`)
  — set when the request itself is being cancelled. Three triggers fire
  this signal: an explicit `POST /v1/responses/{id}/cancel` API call, a
  non-background POST whose client disconnects mid-stream, or steering
  pressure (a new turn arriving on the same steerable chain). This is
  the wake-up signal handlers await / poll on inside their work loop.
- **`context.shutdown`** (`asyncio.Event`) — set when the server is
  shutting down (e.g. SIGTERM). Shutdown is a **separate** surface —
  it does NOT fire the cancellation signal. The handler expectation
  for shutdown is different from cancel: resilient handlers should call
  `await context.exit_for_recovery()` to leave the response
  `in_progress` for re-entry on restart; non-resilient handlers should
  emit `response.failed` quickly. Handlers that care about both must
  inspect each surface independently.
- **`context.client_cancelled`** (`bool`) — cause flag stamped at the
  HTTP boundary when the cancellation was an explicit client
  cancellation (the `/cancel` endpoint OR a non-bg POST disconnect).
  When `cancellation_signal` fires but `client_cancelled` is False
  and `context.shutdown` is not set, the cause is steering pressure.

| Cause | `cancellation_signal` | `context.shutdown` | `context.client_cancelled` | Framework Behaviour | What Handler Should Do |
|-------|:---:|:---:|:---:|---|---|
| **Steering** | set | not set | False | If no terminal emitted → auto-emit `response.failed`. If terminal emitted → honour it. | Break loop → close builders → `emit_completed()` |
| **Client Cancel** | set | not set | True | Framework forces `cancelled` regardless of handler output. Output items abandoned. | Return as soon as cleanup is done. |
| **Shutdown** | not set | set | False | Hard cutoff after `shutdown_grace_period_seconds`. Resilient+bg: `await context.exit_for_recovery()` leaves the response `in_progress` for re-entry. Others: mark failed. | Checkpoint progress → `await context.exit_for_recovery()`. Or complete quickly. |
| **Shutdown + Client Cancel race** | set | set | True | Each surface reflects its independent cause; framework prefers the cancel-status path. | Inspect each surface as needed; typically prefer shutdown's `exit_for_recovery()` for resilient bg. |

**Key status rules:**
- `cancelled` is ONLY produced by explicit client cancellation (`/cancel` or non-bg POST disconnect). Never by steering or shutdown.
- `incomplete` is NEVER set by the framework — it's exclusively developer-controlled.
- `context.exit_for_recovery()` is the single, uniform graceful-shutdown recovery primitive — **it works in every handler shape** (coroutine, async generator, sync). Call it as a bare statement: `await context.exit_for_recovery()`. It raises internally (never returns), so there is no `return <value>` form to trip the async-generator `SyntaxError`. (A bare `return` without a terminal while `context.shutdown` is set still works as an implicit fallback, but the explicit primitive is the recommended idiom.)

> **On shutdown for resilient handlers**: leaving the response `in_progress` makes the framework re-invoke your handler on restart (when `resilient_background=True`). Every handler shape uses the same line — `await context.exit_for_recovery()`. See [Resilience](#resilience) for the recovery contract — what the recovered handler must do, what the library guarantees on re-entry, and how clients reconcile the multi-attempt stream.

### Default Pattern (handles cancel + shutdown)

Most handlers need to observe BOTH `cancellation_signal` and
`context.shutdown` in their work loop — cancel triggers graceful
finish, shutdown triggers `exit_for_recovery()`:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    async for token in model.stream(prompt):
        if context.shutdown.is_set():
            # Defer to next-lifetime recovery. The unified primitive
            # raises internally and works in this async-generator shape.
            await context.exit_for_recovery()
        if cancellation_signal.is_set():
            break
        yield text.emit_delta(token)

    yield text.emit_text_done()
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()
```

This works for all three causes:
- **Steering**: partial output is preserved, `completed` status is correct
- **Client cancel**: framework overrides status to `cancelled` regardless
- **Shutdown**: if you emit `completed` within the grace period, the response
  finishes successfully. If you can't finish in time, prefer the advanced pattern.

### Advanced Pattern (pre-entry steering, resilient shutdown recovery)

For steerable + resilient handlers, either surface may be pre-set when
the handler is (re)entered: `context.shutdown` if the server is
mid-shutdown, or `cancellation_signal` if a newer turn is already
queued (steering) or the client cancelled. **These are distinct,
(mostly) mutually-exclusive surfaces — shutdown does NOT fire
`cancellation_signal` (see the table above) — so check each one
independently, shutdown first.** Routing: for shutdown propagate the
recovery sentinel; for steering emit `completed` (the turn was
superseded); for explicit client cancel just return:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()

    # Pre-entry: shutdown and cancellation are SEPARATE surfaces. Check
    # shutdown first (it does not set cancellation_signal); this also
    # resolves the rare both-set race in favour of recovery.
    if context.shutdown.is_set():
        # Server is shutting down; defer to next-lifetime recovery.
        await context.exit_for_recovery()
    if cancellation_signal.is_set():
        if context.client_cancelled:
            # Explicit client cancel — framework forces "cancelled" status.
            return
        # Steering — emit completed so the superseded turn finishes cleanly.
        yield stream.emit_completed()
        return

    yield stream.emit_in_progress()

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    async for token in model.stream(prompt):
        if cancellation_signal.is_set():
            break
        yield text.emit_delta(token)

    # Shutdown mid-stream: defer to next-lifetime recovery — the framework
    # leaves the response in_progress and re-invokes on restart.
    if context.shutdown.is_set():
        await context.exit_for_recovery()

    yield text.emit_text_done()
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()
```

After the streaming loop breaks, check for `context.shutdown.is_set()`
BEFORE closing builders. If shutdown interrupted mid-stream, call
`await context.exit_for_recovery()` — the response stays `in_progress`
and the handler is re-entered on the next process lifetime to produce the
full output (requires
`resilient_background=True`).

For all other cases (steering, client cancel, normal completion), close
builders and emit `completed`:

- **Steering/Normal**: `completed` is the correct status.
- **Client cancel**: framework overrides to `cancelled` regardless.
- **Shutdown**: handler hasn't finished its work — propagate
  `await context.exit_for_recovery()` to defer re-entry.

### Metadata Usage in Cancellation

`context.conversation_chain_metadata` is appropriate for storing lightweight progress signals
that help on re-entry — for example `last_processed_item_id` so you can
take unprocessed items from response history after that point, or a step index
for multi-phase workflows.

**Acceptable**: step counters, message IDs, phase indicators, checkpoint
references for framework-native stores (e.g., a SqliteSaver checkpoint ID).

**Not acceptable**: full conversation history, LLM outputs, or framework
checkpoint data. These belong in framework-native stores (SqliteSaver for
LangGraph, Copilot SDK sessions, or your own backing store).

### TextResponse Handlers

`TextResponse` handlers handle cancellation automatically. For streaming
text with cancellation awareness:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    async def stream_tokens():
        async for token in model.stream(prompt):
            if cancellation_signal.is_set():
                return
            yield token

    return TextResponse(context, request, text=stream_tokens())
```

### Rules

1. **MUST emit `response.created` before any early return** — the framework
   cannot persist or track a response until `emit_created()` is yielded.

2. **MUST emit a terminal event** (`emit_completed()`, `emit_incomplete()`,
   or `emit_failed()`) in normal and cancellation paths. If the handler exits
   without a terminal event, the framework forces `failed` status.

3. **Do NOT emit `emit_cancelled()`** — the `cancelled` status is reserved
   for the framework when the client cancel API is used. Handlers should
   always emit `completed` (or `incomplete`/`failed` for errors).

4. **Steering and client cancel are fully cooperative** — the framework
   waits indefinitely for the handler to yield/return. Keep your cleanup fast
   but you're not racing a deadline.

5. **Shutdown has a hard cutoff** — after `shutdown_grace_period_seconds`
   the process exits. Keep post-signal work under a few seconds.

6. **`return` in an async generator is a bare statement** — you cannot
   `return value`. Use `yield` for events, then `return` to exit.

---

## Error Handling

### Handler Exceptions

Throwing an exception is a valid way to terminate your handler — you don't need to
emit a terminal event first. The library catches the exception and maps it to the
appropriate HTTP error response:

| Exception | HTTP Status | Response Status | Error Code |
|-----------|-------------|-----------------|------------|
| `RequestValidationError` | 400 | failed | from exception |
| `ValueError` | 400 | failed | `invalid_request` |
| Any other exception | 500 | failed | `server_error` |

For unknown exceptions, clients see a generic 500 — actual exception details are
logged but never exposed.

### Explicit Failure

To signal a specific failure with a custom error code and message:

```python
yield stream.emit_created()
yield stream.emit_in_progress()
# ... some work ...

# Something went wrong — signal failure explicitly
yield stream.emit_failed(code="server_error", message="Custom error message")
# Do NOT yield any more events after a terminal event
```

### Validation Pipeline

Bad client input returns HTTP 400 before your handler runs. Bad handler output
returns HTTP 500 or triggers `response.failed`. The library validates:

- Request payload structure
- Response ID format
- Agent reference structure
- Event ordering (created → in_progress → output → terminal)

---

## Response Lifecycle

### Terminal Event Requirement

Your handler must do one of two things before the generator completes:

1. **Emit a terminal event** — `emit_completed()`, `emit_failed()`, or
   `emit_incomplete()`
2. **Raise an exception** — the library maps it to `response.failed`

What is **not** valid is silently completing the generator without either — the
library treats this as a programming error and emits `response.failed`
automatically.

```python
# ✅ Emit a terminal event
yield stream.emit_completed()

# ✅ Also valid: raise an exception
raise ValueError("Unsupported model")

# ❌ Bad: stopping without a terminal event or exception
#    → library emits response.failed with a diagnostic log
```

> **Note:** This section applies to `ResponseEventStream` handlers. `TextResponse`
> handles terminal events automatically.

### Signalling Incomplete

If your handler cannot fully complete the request (e.g., output was truncated):

```python
yield stream.emit_created()
yield stream.emit_in_progress()

message = stream.add_output_item_message()
# ... partial output ...
yield message.emit_done()

yield stream.emit_incomplete(reason="max_output_tokens")
```

### Token Usage Reporting

Terminal methods accept an optional `usage` parameter for reporting token
consumption:

```python
from azure.ai.agentserver.responses.models import ResponseUsage

usage = ResponseUsage(input_tokens=150, output_tokens=42, total_tokens=192)

# Completed with usage
yield stream.emit_completed(usage=usage)

# Failed with usage
yield stream.emit_failed(code="server_error", message="Error message", usage=usage)

# Incomplete with usage
yield stream.emit_incomplete(reason="max_output_tokens", usage=usage)
```

Handlers that proxy to an LLM and receive token counts should pass them through.
Handlers that do not interact with an LLM typically omit usage.

---

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `default_model` | `None` | Default model when `model` is omitted from the request |
| `default_fetch_history_count` | `100` | Maximum history items resolved by `get_history()` |
| `sse_keep_alive_interval_seconds` | `None` (disabled) | Interval between SSE keep-alive comments |
| `shutdown_grace_period_seconds` | `10` | Seconds to wait for in-flight requests on shutdown |

Platform environment variables (read once at startup via `AgentConfig`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SSE_KEEPALIVE_INTERVAL` | Disabled | Interval (seconds) between SSE keep-alive comments |
| `PORT` | `8088` | HTTP listen port |
| `DEFAULT_FETCH_HISTORY_ITEM_COUNT` | `100` | Override for `default_fetch_history_count` |
| `FOUNDRY_PROJECT_ENDPOINT` | — | Foundry project endpoint (enables persistence) |
| `FOUNDRY_AGENT_SESSION_ID` | — | Platform-supplied session ID |
| `FOUNDRY_AGENT_NAME` | — | Agent name for tracing |
| `FOUNDRY_AGENT_VERSION` | — | Agent version for tracing |

### Distributed Tracing

The server emits OpenTelemetry-compatible spans for `POST /responses` requests.
Handler authors can create child spans — they are automatically parented under the
library's span.

The library sets baggage items on the span:

| Key | Description |
|-----|-------------|
| `response.id` | The library-generated response identifier |
| `conversation.id` | Conversation ID from the request (if present) |
| `streaming` | `"true"` or `"false"` |
| `agent.name` | Agent name from `agent_reference` (if provided) |
| `agent.id` | Composite `{name}:{version}` (if provided) |
| `provider.name` | Fixed: `"azure.ai.responses"` |
| `request.id` | From the `X-Request-Id` HTTP header (if present) |

### SSE Keep-Alive

The server can send periodic keep-alive comments during SSE streaming to prevent
reverse proxies from closing idle connections. Disabled by default.

Enable via environment variable:

```bash
export SSE_KEEPALIVE_INTERVAL=15
```

Or via the options constructor:

```python
app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(sse_keep_alive_interval_seconds=15),
)
```

The `X-Accel-Buffering: no` response header is automatically set on SSE streams
to disable nginx buffering.

---

## Resilience

The framework re-invokes your handler when the server crashes mid-response
(if `resilient_background=True` and the request had `store=true, background=true`).
What that re-invocation gives you, what you have to do to take advantage of it,
and how clients reconcile a multi-attempt stream is the **recovery contract**.

The deeper "how does this all fit together" view — the four-row dispatch matrix,
the three termination paths (handler completes within grace, grace exhausted,
crash), the exact persistence guarantees the framework makes, and the full
conformance items — is in
[`responses-resilience-spec.md`](responses-resilience-spec.md). That document is
language-agnostic and intentionally exhaustive; this section is the developer
how-to with worked Python examples. The conformance suite at
`tests/e2e/resilience_contract/` exercises every cell of the matrix.

You can opt out of all of this and your response will still be correct (just
duplicative). You opt in when you want the recovered attempt to pick up where
the crashed one left off instead of re-running the whole turn.

### Mental Model

Three layers, each owning a specific slice of state:

| Layer | Owns | On crash recovery, surfaces / provides |
|---|---|---|
| **Library** (this SDK) | Persisted SSE event stream (every event you emitted, in order) — used for client replay via `starting_after=`. The library persists the response *object* at the first attempt's `response.created`, at **each successful `yield stream.checkpoint()`**, and at the terminal event; the `response.created` and terminal writes are deduplicated across recovery attempts (idempotent persistence keyed on `response_id`). The last persisted snapshot is exposed on re-entry as `context.persisted_response`. It does NOT keep a *running* snapshot of in-flight state between those persistence points. | Re-invokes the handler. Surfaces `context.is_recovery == True`, `context.persisted_response`, `context.is_steered_turn`, `context.pending_input_count`, and `context.conversation_chain_metadata`. Replays persisted events to reconnecting clients. Rebuilds your `ResponseContext` transparently — the handler sees the same `response_id` it had on the first attempt. |
| **Handler** (your code) | The "what was safely committed" decision, plus side-effect watermarks in `context.conversation_chain_metadata`. | Decides the resumption point. Constructs the **resumption response**. Emits a fresh `response.in_progress` carrying it. Continues producing new output items. |
| **Upstream framework** (Copilot SDK, LangGraph, your own LLM client) | The conversational / graph / agent state that has to outlive a process death. | Has its own resume facility (session ID, checkpoint store) that you call from the handler. |

You do NOT own response event resilience — that's the library. The library
does NOT own conversational resilience — that's upstream. You glue them
together.

### The Recovery Loop

When the server restarts after a crash and your handler is re-invoked:

1. The library calls your handler with `context.is_recovery == True`.
2. You query upstream (and your own `context.conversation_chain_metadata` watermarks) to determine the **resumption point** — the most recent state you are confident is persisted.
3. You build a **resumption response**: a `ResponseObject` reflecting only the output items you trust at the resumption point. **In-flight items from the crashed attempt are excluded.** Construct this from upstream framework state + your own metadata watermarks — the library does NOT give you a snapshot of the prior attempt's in-flight state, because none exists in a useful form.
4. You construct `ResponseEventStream(response=resumption_response, ...)` instead of the usual `request=request` form.
5. You emit `response.created` exactly as you would on a fresh attempt — the framework dedups the response-store write so it happens exactly once across all recovery attempts. You do not need to branch on `is_recovery` to decide whether to emit `response.created`.
6. You emit `response.in_progress`. This event's `response` payload IS the resumption response — and the library treats it as a **client-visible snapshot reset**. Reconnecting clients discard any partial in-progress state they had and adopt this payload as authoritative.
7. You continue producing new output items, potentially at the same `output_index` values you used before the crash. Content does NOT have to match the pre-crash content (LLMs are non-deterministic; that's fine).
8. You emit your terminal event.

The library guarantees that step 6's `in_progress` is treated as a reset:
- The persisted response state is REPLACED with the event payload.
- Subsequent `output_item.added` at indexes already present in the resumption response REPLACE the prior item (don't append a duplicate).

The library does NOT deduplicate handler-emitted events. If you don't emit a
reset `in_progress`, the persisted state grows by whatever you emit, which
is the naive fallback (see below).

### What the Library Does

- Persists every SSE event in order. No reordering, no deduplication of stream events — **except** that a recovered handler's re-emitted `response.created` is not re-appended to an already-non-empty resilient stream (so a replaying client sees `response.created` exactly once; spec 026).
- Persists the response *object* at the first attempt's `response.created`, at **each successful `yield stream.checkpoint()`**, and at the terminal event. The `response.created` and terminal writes are deduplicated across recovery attempts (idempotent persistence keyed on `response_id`); the handler does not branch for them. The last persisted snapshot is exposed on re-entry as `context.persisted_response`.
- Rebuilds your `ResponseContext` transparently on any cross-process recovery — the recovered handler sees the same `response_id`, the same `request`, the same `conversation_chain_id`, and the same cancellation surface (`cancellation_signal` (3rd positional handler arg), `context.shutdown`, `context.client_cancelled`) it had on the first attempt. Id generation is a fresh-entry-only concern.
- Surfaces flat recovery + steering classifiers on `ResponseContext`: `context.is_recovery`, `context.persisted_response`, `context.is_steered_turn`, `context.pending_input_count`, `context.conversation_chain_metadata`. For the framework-checkpoint model, `context.persisted_response` is the last resiliently-checkpointed snapshot; for upstream-owned recovery, the library holds no useful in-flight snapshot and you consult your upstream framework for resumption state.
- Treats any `response.in_progress` event after the first one as a snapshot reset.
- Replays persisted events to reconnecting clients on `starting_after=`. The reset `in_progress` is part of the replay; clients use it as the reconciliation signal.
- **Surfaces graceful-shutdown recovery via one uniform signal in every handler shape.** The framework leaves the response `in_progress` so the next process lifetime re-invokes your handler with `context.is_recovery=True` when, on `context.shutdown`, the handler calls `await context.exit_for_recovery()`. This single idiom works identically in coroutine/`TextResponse` and streaming async-generator handlers — it raises internally (never returns), so there is no `return <value>` form to trip the async-generator `SyntaxError`. (An implicit fallback also applies: a streaming handler that simply `return`s without a terminal **while `context.shutdown` is set** still recovers — but `await context.exit_for_recovery()` is the recommended explicit idiom. A bare `return` during normal execution still yields the default terminal.)
- For `background=false` responses (or `resilient_background=False` background responses): marks the response `failed` on crash and does NOT re-invoke the handler.
- For `store=false` responses: best-effort `failed` marker during shutdown grace period; no recovery.

### What the Handler Does

- Branches on `context.is_recovery` to choose fresh-entry vs recovered-entry code paths.
- Builds the resumption response from upstream-framework state + own metadata watermarks. **Excludes in-flight items.**
- Constructs `ResponseEventStream(response=resumption_response)` on recovered entry.
- Emits `response.in_progress` early in the recovered path (this is the reset).
- Uses upstream framework's native resume facility (e.g. session resume, checkpoint replay) — never re-runs a side-effecting upstream call without checking a watermark first.
- Watermarks any upstream side-effecting call by writing a small marker to `context.conversation_chain_metadata` **before** the call and clearing it **after** the call has been persisted upstream. Call `await context.conversation_chain_metadata.flush()` between the watermark write and the side effect to ensure the marker survives a crash.
- For upstream-session-id needs: `context.conversation_chain_id` is a derived, stable chain identifier — the framework computes it so every turn of the same conversation resolves to the same value (anchored to the conversation's root: a `conversation_id`, or the head of a `previous_response_id` chain, falling back to a first turn's own `response_id`), stable across all attempts of a turn. It's a convenient session id to pass to upstream frameworks (Copilot `session_id`, LangGraph `thread_id`) — using it avoids allocating and persisting your own UUID, though you may use your own identifier if you prefer.

### Stream Checkpoints

For resilient background responses you can persist a snapshot of the response at
explicit, developer-chosen boundaries with `yield stream.checkpoint()`. A
checkpoint resiliently writes the current `stream.response` (every output item you
have finished emitting) via the storage provider, so a crashed attempt can
resume from the last checkpoint instead of re-running the whole turn.

```python
@app.response_handler
async def handler(request, context, cancellation_signal):
    # On recovery, seed the stream from the last resiliently-checkpointed
    # snapshot — the completed phases' items are already in
    # stream.response.output, so resume from their count.
    if context.is_recovery and context.persisted_response is not None:
        stream = ResponseEventStream(
            response_id=context.response_id, response=context.persisted_response,
        )
        start_phase = len(stream.response.output)
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        start_phase = 0

    yield stream.emit_created()      # recovery: framework suppresses the resilient-stream
                                     # write (stream already has the pre-crash created);
                                     # this seeds the in-memory stream + first-event validator
    yield stream.emit_in_progress()  # client-visible reset point on recovery (carries seeded items)

    for phase in range(start_phase, NUM_PHASES):
        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()
        yield text.emit_delta(await run_phase(phase))   # the expensive work
        yield text.emit_done()
        yield message.emit_done()
        yield stream.checkpoint()        # phase N is now resilient

    yield stream.emit_completed()
```

Semantics (the full normative list is in
[`responses-resilience-spec.md`](responses-resilience-spec.md) and
[`resilience-contract.md`](resilience-contract.md) Row 11):

- **Deterministic + developer-driven.** Checkpoints happen ONLY where you yield
  one. There are no periodic, timer, or implicit checkpoints.
- **Backpressured.** The handler is suspended at the `yield` until the provider
  write completes — "I checkpointed" means "it is resilient now". The handler
  cannot race ahead while a slow write is in flight.
- **No-op unless resilient background.** The write happens ONLY when the
  deployment has `resilient_background=True` and the request is `background=true`
  (which implies `store=true`). In every other configuration the checkpoint
  event is dropped (no provider write), so you may yield it unconditionally.
- **Idempotent.** A snapshot byte-identical to the last persisted one is
  skipped.
- **Failures swallowed.** A provider error is logged and ignored; recovery
  falls back to the previously-persisted snapshot.
- **After terminal.** A checkpoint yielded after a terminal event is dropped
  (the terminal write is authoritative); no exception.

#### `context.persisted_response`

On a recovered entry, `context.persisted_response` is the last resiliently-persisted
`ResponseObject` snapshot (the last checkpoint, or the `response.created`
snapshot if no checkpoint ran), or `None` if nothing was persisted before the
crash. It is an **entry-only** cache — read it at the start of a recovered
invocation to decide where to resume; it is not refreshed mid-execution.

The **one-OutputItem-per-phase** pattern composes naturally with it: emit one
output item per phase and checkpoint at each boundary, then on recovery **seed
the stream** with `context.persisted_response` and resume from
`len(stream.response.output)`. A phase whose `output_item.done` + checkpoint
completed survives (it is already in the seeded output, carrying its original
content); a phase interrupted before its checkpoint is re-run — correct by
construction, with no extra watermark bookkeeping.

> On recovery you seed `ResponseEventStream(response=context.persisted_response)`
> so the already-checkpointed items are present in `stream.response.output` and
> the builder's output-index continues past them. You then `yield
> stream.emit_created()` exactly as on a fresh attempt — the framework
> recognises the recovered entry and accepts the seeded output (it dedups the
> response-store write). You emit ONLY the remaining phases via builder events;
> the persisted response is the watermark, so there is no replay or breadcrumb
> reconstruction.

### Item and Response `internal_metadata`

`internal_metadata` is a **single-turn**, platform-internal key/value bag that
rides on output items and on the response, is persisted with the response (so
it survives crash recovery), and is **always stripped before any client-facing
HTTP or SSE payload** — clients never see it.

```python
# Item-level — a live MutableMapping[str, Any], lazily created, never None.
message = stream.add_output_item_message()
message.internal_metadata["upstream_msg_id"] = "abc-123"
message.internal_metadata["attempt"] = 2

# Response-level — read/write/delete via the stream proxy.
stream.internal_metadata["resume_phase"] = 3
del stream.internal_metadata["scratch"]
```

Use it for lightweight per-turn watermarks, id mappings (e.g. an upstream
framework's message id ↔ the emitted item), or stale-message / crash-recovery
detection within the turn. It is persisted whenever the response is persisted —
at `response.created`, at each `yield stream.checkpoint()`, and at terminal — so
on recovery you read it back from `context.persisted_response`. It is distinct
from the *public* `ResponseObject.metadata` dict (the client's own metadata,
which is NOT stripped).

### Which metadata facility?

The context exposes **two** internal-metadata facilities at **different scopes**
— do not confuse them:

| Aspect | `context.conversation_chain_metadata` | `internal_metadata` (item + response) |
|---|---|---|
| **Scope** | **Cross-turn** — persists across turns/responses on the same conversation chain (steerable multi-turn, recovery re-entries). | **Single turn** — lives on this response (or its items) only. |
| **Best for** | Cross-turn watermarks; state a later turn needs from an earlier one; coordination between layers/nodes spanning the chain. | Lightweight per-turn watermarks; id mappings; in-turn crash-recovery / stale-message detection. |
| **Structure** | **Named scopes** — `conversation_chain_metadata(name)` returns an isolated sibling namespace, so parallel nodes/layers track + `flush()` independently. | Flat per-object map (use key prefixes if you need grouping). |
| **Resilience trigger** | Explicit `await …flush()` (+ resilient-task lifecycle). | Persisted when the owning response is persisted (`created`, each `checkpoint()`, terminal). No separate flush. |
| **Visibility** | Task/resilience state — never on the wire. | Rides on the response/items but **stripped on egress/ingress** — clients never see it. |
| **Lifetime** | The conversation chain / resilient-task lifetime. | This response's persisted record; readable on recovery via `context.persisted_response`. |

**Rule of thumb:** need it in a *later turn* → `conversation_chain_metadata`;
need it only to reconstruct *this* response on crash recovery →
`internal_metadata` (+ `stream.checkpoint()`).

### Default Pattern (recovery-aware)

A framework-agnostic recovery-aware handler. The upstream-specific reconciliation
(how to query upstream for its state, how to resume a session) is in your
sample's docstring; the pattern below stays uniform.

```python
from azure.ai.agentserver.responses import (
    CreateResponse, ResponseContext, ResponseEventStream,
)
from azure.ai.agentserver.responses.models._generated import ResponseObject


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    # ── Choose between fresh and recovered entry ────────────────────
    if context.is_recovery:
        # Ask upstream (or read context.conversation_chain_metadata) for what was
        # safely committed.
        resumption = _build_resumption_response(context, request)
        stream = ResponseEventStream(
            response_id=context.response_id, response=resumption,
        )
    else:
        stream = ResponseEventStream(
            response_id=context.response_id, request=request,
        )

    yield stream.emit_created()  # same call on fresh and recovered; framework dedups

    # The cancellation contract still applies on recovered entry. Shutdown
    # and cancellation are DISTINCT, (mostly) mutually-exclusive surfaces —
    # shutdown does NOT fire cancellation_signal — so check each one
    # independently, shutdown first. Defer to recovery for shutdown; emit
    # `completed` for steering pressure; return for explicit client cancel.
    if context.shutdown.is_set():
        await context.exit_for_recovery()  # defer to next-lifetime recovery
    if cancellation_signal.is_set():
        if context.client_cancelled:
            return  # framework forces "cancelled" status
        # Steering pressure — emit completed so the superseded turn
        # finishes cleanly.
        yield stream.emit_completed()
        return

    # ── This is the client-visible reset point on recovery ──────────
    yield stream.emit_in_progress()

    # Now produce new content. Use upstream's resume facility before any
    # side-effecting call. Watermark before; clear after upstream commit.
    async for event in _produce_new_output(stream, request, context):
        yield event

    # On graceful shutdown mid-work, defer to next-lifetime recovery —
    # the framework leaves the response `in_progress` and re-invokes on
    # the next process restart (requires resilient_background=True).
    if context.shutdown.is_set():
        await context.exit_for_recovery()

    yield stream.emit_completed()
```

### Fallback Pattern (no opt-in)

A handler that does nothing recovery-specific still produces a correct response.
The library:
- accepts the duplicate `created` from re-entry,
- accepts a fresh `in_progress` with empty output as the reset,
- accumulates the re-streamed content as the new authoritative view.

The cost: clients that reconnected with `starting_after=` see a reset to empty
and a full re-stream. The final response is correct; the UX is jarring.
Upstream side-effecting calls (LLM queries, agent session writes) may be
issued twice — this corrupts upstream session history. If your upstream has
resilient history that matters, you MUST adopt the recovery-aware pattern. If
your handler has no upstream side effects (e.g. it streams from an
idempotent source), the fallback is fine.

### Upstream History Pattern (preferred when available)

Many stateful upstream SDKs expose their persisted conversation log directly —
e.g. `claude_agent_sdk.get_session_messages(session_id)` returns the list of
messages the SDK has persisted, and Copilot's `session.get_messages()`
does the same for its event log. When that API is available, use it as the
source of truth for "did my prior attempt already send this turn?" — no handler
metadata, no watermark, no flush ordering.

```python
async def _send_input_if_not_in_session(session, session_id, user_input):
    history = await session.get_messages()
    # If the most recent user message in upstream history matches the current
    # input, the prior attempt already sent it — skip the upstream call.
    last_user = next(
        (evt for evt in reversed(history) if _is_user_message(evt)),
        None,
    )
    if last_user is not None and _extract_user_text(last_user) == user_input:
        return
    await session.send(user_input)
```

Why this beats a handler-managed watermark:

- The detection input is the upstream's own resilient log — there is no window
  between "we sent the call" and "we wrote our watermark" where a crash leaves
  the handler and the upstream out of sync.
- No `context.conversation_chain_metadata` write, no `metadata.flush()`, no decision about
  flush-before vs flush-after.
- On any attempt (fresh, recovered, multiply-recovered) the same one-liner
  works: query history, compare, send only if needed.

Edge case to document in your sample: if a prior turn's input was byte-equal to
the current turn's input AND that prior turn completed normally, the
"last user message in history equals current input" heuristic incorrectly
skips. Rare in practice for human-driven conversations; if your domain has
machine-generated identical-input replays, fall back to the watermark pattern
below.

### Watermark Pattern (fallback when upstream exposes no persisted history)

When the upstream SDK does **not** expose its committed log — or does not
distinguish "queued but unacked" from "persisted" — the framework
cannot know which of your calls have side effects, so you stamp a marker in
`context.conversation_chain_metadata` before the call and clear it after the upstream commit.

The strict at-most-once pattern is **write → flush → side effect → write →
flush**. The explicit `await metadata.flush()` ensures the watermark hits
persistent storage before the side effect runs; without it, the framework only
snapshots metadata at resilient-task lifecycle boundaries
(start/suspend/complete/fail/cancel), so a crash between "side effect issued"
and the next lifecycle boundary would leave the watermark in memory only and
re-issue the side effect on recovery. The explicit `flush()` is the fence.

```python
#flat context surface — no nested resilience object
# Stamp BEFORE the side-effecting call, and FLUSH to make the marker resilient.
context.conversation_chain_metadata["upstream_query_in_flight"] = True
await context.conversation_chain_metadata.flush()

await upstream.send_message(prompt)

# Stream the response back…
async for chunk in upstream.receive_response():
    if cancellation_signal.is_set():
        break
    yield ...emit_delta(chunk)

# Clear AFTER the upstream persisted the result
# (e.g. assistant message landed in the upstream's session log), and
# FLUSH so the cleared marker survives a subsequent crash.
context.conversation_chain_metadata["upstream_query_in_flight"] = False
await context.conversation_chain_metadata.flush()
```

On recovery you check the marker:

- Marker `True`: prior attempt called the upstream API. Use upstream's resume
  facility (and, if available, fork primitive) to avoid duplicating the
  message in upstream history. **Do NOT call `upstream.send_message(prompt)` again.**
- Marker `False` (or missing): no prior side effect. Treat as fresh entry from
  the upstream's perspective.

The two flushes are the cost of at-most-once. If your side effect is naturally
idempotent (e.g. it carries a client-supplied request id and the upstream
dedupes), you can skip both flushes and rely on the upstream's dedup. The
upstream-history pattern above is preferred whenever it's available because
it removes the watermark window entirely.

Watermark naming convention (recommended): `<upstream>_<operation>_in_flight: bool`.
SDK-specific names belong in your sample's docstring.

### Resumption Response Construction

The resumption response is the `ResponseObject` you hand to
`ResponseEventStream(response=…)` on a recovered entry; its `output` is the
client-visible reset point. How much you build depends on your resume model.

**Simplest case — return the persisted snapshot as-is.** If you used framework
checkpoints (`stream.checkpoint()`), `context.persisted_response` already holds
exactly the items that were persisted at the last checkpoint. You can
seed straight from it, no construction needed:

```python
if context.is_recovery and context.persisted_response is not None:
    stream = ResponseEventStream(
        response=context.persisted_response, response_id=context.response_id,
    )
    start_phase = len(stream.response.output)   # resume past committed items
```

**Involved case — trim items you can't trust.** If the snapshot (or your
upstream's view) may contain items emitted by work that did NOT resiliently commit,
you trim `output` down to only the items you trust, then resume. *What* to trim
is your decision, and you can drive it from any resilient signal you stamped:

- **An upstream framework's checkpoint state** (which steps it actually saved).
- **Item-level `internal_metadata`** — tag each emitted item with, say, the step
  that produced it (`message.internal_metadata["step"] = step_id`); it rides on
  the persisted item and is stripped before the client ever sees it.
- **Response-level `internal_metadata`** (`stream.internal_metadata[...]`).
- **`context.conversation_chain_metadata`** watermarks.

For example: tag each message with the step that emitted it, then on recovery
keep only items whose step is in your checkpoint store and drop the rest:

```python
def _build_resumption_response(context, request) -> ResponseObject:
    snapshot = context.persisted_response
    committed_steps = upstream.checkpointed_step_ids(context.conversation_chain_id)

    kept = [
        item for item in (snapshot.output if snapshot else [])
        # the step tag we stamped on each item when we first emitted it
        if (item.get("internal_metadata") or {}).get("step") in committed_steps
    ]
    return ResponseObject({
        "id": context.response_id,
        "object": "response",
        "status": "in_progress",
        "output": kept,          # only items from steps we know were checkpointed
        "model": request.model,
    })
```

The library persists the response object at `response.created`, at **each
successful `stream.checkpoint()`**, and at the terminal event (the
`response.created` and terminal writes are deduped across attempts keyed on
`response_id`). It does not keep a *running* snapshot between those points — so
for any item whose commit status falls between persistence points, you are the
source of truth for whether to keep it, via the watermarks above.

### Composing an External Durable Engine (e.g. LangGraph)

The patterns above assume *your handler* is the only thing tracking progress. But
many agent frameworks — LangGraph, LlamaIndex workflows, custom state machines —
bring **their own durable checkpointer**. Now you have **two independent durable
stores**: the framework's response record (`persisted_response`, advanced by
`stream.checkpoint()`) and the engine's checkpoint (its saver). Composing them
correctly is the source of the subtlest recovery bugs, so this section is
explicit about the trap and the fix.

**The trap — dual-store divergence.** Two independent stores can never be written
atomically. Suppose the engine streams a reply token-by-token inside one node and
commits that node to *its* checkpoint. There is always a window between "the
engine committed the node" and "your `stream.checkpoint()` captured the reply".
If you crash in that window and, on recovery, resume the engine **from its own
latest checkpoint**, the engine sees that node as already done and will **not**
re-emit its tokens — yet `persisted_response` never captured the reply. Result: a
`completed` response with a missing reply (or, if you naively re-feed the input, a
duplicated turn). Resuming from the engine's latest tip is the bug.

**The fix — make the framework checkpoint the single source of truth, and record
the engine's resume point inside it.** Two rules:

1. **Checkpoint 1:1 with the engine.** Every time the engine commits a step, take
   a framework `stream.checkpoint()` too — and in the *same* checkpoint, store the
   engine's checkpoint id for that step in `internal_metadata`. Because the reply
   items and the resume pointer land in one atomic framework write, they can never
   disagree: if `persisted_response` has the reply, its recorded pointer is
   *after* the reply's node; if it doesn't, the pointer is *before* it.

2. **On recovery, rewind the engine to the recorded pointer — never its latest
   tip.** Resume from the checkpoint id you read back from
   `persisted_response.internal_metadata`. The engine re-runs exactly the steps
   after that point (re-streaming the reply *iff* it wasn't persisted) and forks
   away any orphaned work its own store had raced ahead to. `persisted_response`
   drives everything; the engine's store is subordinate.

```python
_GRAPH_CP_KEY = "graph_checkpoint_id"  # engine checkpoint id, kept in internal_metadata

# Forward + recovery share ONE streaming loop; only the resume config differs.
if context.is_recovery:
    # Rewind to the checkpoint that MATCHES the persisted items (not the
    # engine's latest tip), and resume with no new input — the input was already
    # applied at/before that checkpoint.
    graph_cp = (context.persisted_response.internal_metadata or {}).get(_GRAPH_CP_KEY)
    run_config = {"configurable": {"thread_id": chain_id, "checkpoint_id": graph_cp}} if graph_cp else base_config
    graph_input = None
else:
    run_config = base_config
    graph_input = {"messages": [HumanMessage(user_input)]}

async for mode, chunk in graph.astream(
    graph_input, run_config, stream_mode=["custom", "checkpoints"], durability="sync"
):
    if mode == "custom":                     # a token from the streaming node
        # Guard against re-emitting a reply that recovery already seeded.
        if not reply_open and not _reply_already_persisted(stream):
            message = stream.add_output_item_message(); yield message.emit_added()
            text = message.add_text_content(); yield text.emit_added()
            reply_open = True
        if reply_open:
            yield text.emit_delta(chunk["token"])
    elif mode == "checkpoints":              # the engine just committed a step
        if reply_open and not reply_closed:  # close the reply on its node's commit
            yield text.emit_text_done(); yield text.emit_done(); yield message.emit_done()
            reply_closed = True
        checkpoint_id = chunk.get("config", {}).get("configurable", {}).get("checkpoint_id")
        if checkpoint_id:
            # Persist items + resume pointer atomically (1:1 with the engine).
            stream.internal_metadata[_GRAPH_CP_KEY] = checkpoint_id
            yield stream.checkpoint()
```

Why this closes the window: the framework checkpoint on step *N-1* (before the
reply node) records the pre-reply engine checkpoint. If you crash any time during
or after the reply node but before the *next* framework checkpoint,
`persisted_response` still points at step *N-1* with no reply — so recovery
rewinds to *N-1*, re-runs the reply node, and re-streams. If you crash after the
post-reply framework checkpoint, the pointer is at step *N* and the reply is
persisted — so recovery rewinds to *N* (past the reply) and re-emits the seeded
item via the `in_progress` reset. Either way: exactly one reply, correct ids.

Practical notes, learned the hard way:

- **Get the engine's checkpoint id from its event stream, not by polling it
  mid-run.** With LangGraph, `graph.astream(..., stream_mode=[..., "checkpoints"])`
  yields the committed checkpoint id per step. Calling `graph.aget_state()`
  *during* an active `astream` on a single-connection saver (e.g.
  `AsyncSqliteSaver`) can return a stale/late id — do not rely on it for the
  resume pointer.
- **Resume with the engine's "no new input" signal** (LangGraph: `None`), never
  by re-feeding the user input, on a recovered turn — the input is already baked
  into the engine state at the rewind point. Re-feeding duplicates the turn.
- **Use the engine's fully-durable mode** (LangGraph: `durability="sync"`) so
  step commits are at node boundaries; a mid-step crash then cleanly re-runs the
  whole step.
- **`internal_metadata` is stripped on egress**, so the engine checkpoint id
  never leaks to the client — it is purely your recovery bookkeeping.

The end-to-end reference is `samples/sample_21_resilient_langgraph.py` (real-time
token streaming + steering + crash recovery), with subprocess crash tests in
`tests/e2e/test_sample_21_langgraph_e2e.py` that SIGKILL both *before* and *after*
the reply is emitted to exercise both sides of the window.

### Recovery × Cancellation Composition

The cancellation contract from the [Cancellation](#cancellation) section composes
with recovery cleanly:

- **Recovered entry + `cancellation_signal` (3rd positional handler arg) pre-set**: same as fresh entry — inspect the cause flags. Steering pressure (no cause flag) emits `completed`; explicit client cancel returns; shutdown propagates `await context.exit_for_recovery()`.
- **Recovered entry + `cancellation_signal` (3rd positional handler arg) fires mid-stream**: same as fresh entry — break the loop, then check `context.shutdown.is_set()` for the recovery-deferral path; otherwise close builders and `emit_completed`.
- **Crash during recovery itself**: same code path; each attempt queries upstream for its current state, computes a (possibly different) resumption response, emits a fresh reset `in_progress`. The loop is re-entrant.

### Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `resilient_background` | `False` | Opt INTO crash-recoverable background responses |
| `steerable_conversations` | `False` | Multi-turn conversation steering (see [Cancellation](#cancellation)) |

See the [Resilient Responses Developer Guide](resilient-responses-developer-guide.md)
for the configuration matrix (`store` × `background` × `resilient_background`),
the flat `ResponseContext` recovery + steering surface, and client-side
reconciliation rules.

---

## Steering API

Steering (`steerable_conversations=True`) lets a new turn arrive on an
already-active conversation: the framework cancels the in-progress turn via
`cancellation_signal` (see [Cancellation](#cancellation)), then re-invokes the
handler to drain the queued input. The handler-facing surface:

- **`context.is_steered_turn: bool`** — `True` on the drain re-entry that
  follows a steering input (not on the turn that was superseded).
- **`context.pending_input_count: int`** — live count of additional inputs
  queued behind the current turn; decreases as the framework drains them.
- **`@app.response_acceptor`** — the hook that produces the `"queued"`
  `ResponseObject` returned to the POST that was queued onto an
  **already-active** steerable conversation (never the first turn).

### `@app.response_acceptor`

When a new turn is queued onto an active steerable conversation, the framework
immediately returns a `status="queued"` response to that POST while the prior
turn finishes. By default this is a minimal queued envelope; register a hook to
customize it. The hook is **synchronous**, receives `(request, context)`, and
returns a strongly-typed `ResponseObject`:

```python
from azure.ai.agentserver.responses import (
    CreateResponse, ResponseContext, ResponseObject,
)

@app.response_acceptor
def acceptor(request: CreateResponse, context: ResponseContext) -> ResponseObject:
    return ResponseObject(
        {
            "id": context.response_id,
            "object": "response",
            "status": "queued",
        }
    )
```

- The framework ensures `status` defaults to `"queued"` if you omit it.
- If the hook raises, the framework logs a warning and falls back to the
  default queued envelope — a buggy hook never breaks queueing.
- The hook is optional; omit it to use the default envelope.

---

## Best Practices

### 1. Start with TextResponse

Use `TextResponse` for text-only responses — it handles all lifecycle events
automatically. Drop down to `ResponseEventStream` only when you need function
calls, reasoning items, multiple outputs, or fine-grained event control.

### 2. Always Emit Created First, Terminal Last

Every `ResponseEventStream` handler must yield `stream.emit_created()` followed by
`stream.emit_in_progress()` as its first two events, and exactly one terminal event
as its last. The library validates this ordering. `TextResponse` handles this
automatically.

### 3. Use Small, Frequent Deltas

For streaming mode, smaller deltas create a more responsive UX:

```python
# Good: Stream word-by-word
for word in words:
    yield text.emit_delta(word + " ")
```

### 4. Check Cancellation in Loops

Any long-running loop should check `cancellation_signal.is_set()`:

```python
for item in large_collection:
    if cancellation_signal.is_set():
        break
    # ... process item ...
```

### 5. Close Every Builder You Open

Every builder follows `emit_added()` → work → `emit_done()`. If you forget
`emit_done()`, the response will have incomplete output items.

### 6. Prefer Convenience Generators Over Builders

Start with `output_item_message()` / `aoutput_item_message()`. Drop down to
`add_output_item_message()` builders only when you need fine-grained control.

### 7. Let the Library Handle Mode Negotiation

You usually don't need to branch on `request.stream` or `request.background` —
the library negotiates the wire mode and replays the same event sequence for
streaming, non-streaming, and background callers. Emit one event sequence and
let the framework adapt it; reach for mode-specific behaviour only if your
application genuinely needs it.

```python
# ❌ Don't do this
if request.stream:
    # streaming path
else:
    # non-streaming path

# ✅ Same event sequence for all modes
yield stream.emit_created()
yield stream.emit_in_progress()
for evt in stream.output_item_message("Hello!"):
    yield evt
yield stream.emit_completed()
```

> **Tip:** `TextResponse` handlers that use `return TextResponse(...)` don't need
> generators at all — they produce the same events for all modes automatically.

---

## Common Mistakes

### Returning Without Emitting Events

```python
# ❌ Handler exits without producing anything — framework forces "failed"
@app.response_handler
async def handler(request, context, cancellation_signal):
    if cancellation_signal.is_set():
        return  # No events emitted! Response stuck in limbo.

# ✅ Always emit response.created and a terminal event
@app.response_handler
async def handler(request, context, cancellation_signal):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    if cancellation_signal.is_set():
        yield stream.emit_completed()
        return
    # ... normal processing
    yield stream.emit_completed()
```

### Not Emitting response.created Before Early Return

```python
# ❌ Skips emit_created — framework cannot persist or track this response
@app.response_handler
async def handler(request, context, cancellation_signal):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    if some_condition:
        yield stream.emit_completed()  # Created was never emitted!
        return

# ✅ Always emit_created first, regardless of path
@app.response_handler
async def handler(request, context, cancellation_signal):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()  # ALWAYS first
    if some_condition:
        yield stream.emit_completed()
        return
```

### Emitting cancelled Status on Steering

```python
# ❌ "cancelled" is reserved for client cancel API — don't emit it yourself
if cancellation_signal.is_set():
    yield stream.emit_cancelled()  # WRONG — only framework sets cancelled

# ✅ Emit completed — steering means "finish this turn, partial output is valid"
if cancellation_signal.is_set():
    yield text.emit_text_done()
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()
```

### Returning None from Handler

```python
# ❌ Returning None (implicit or explicit) produces no events
@app.response_handler
async def handler(request, context, cancellation_signal):
    result = await do_work()
    # Forgot to return/yield! Python returns None implicitly.

# ✅ Always return TextResponse or yield events from ResponseEventStream
@app.response_handler
async def handler(request, context, cancellation_signal):
    result = await do_work()
    return TextResponse(context, request, text=result)
```

### Using ResponseEventStream When TextResponse Suffices

```python
# ❌ Unnecessary boilerplate for a simple text response
stream = ResponseEventStream(response_id=context.response_id, request=request)
yield stream.emit_created()
yield stream.emit_in_progress()
for evt in stream.output_item_message("Hello!"):
    yield evt
yield stream.emit_completed()

# ✅ Use TextResponse — one line, same result
return TextResponse(context, request, text="Hello!")
```

### Emitting Events After a Terminal Event

```python
# ❌ Don't yield after emit_completed
yield stream.emit_completed()
yield message.emit_done()  # This will be ignored or cause errors

# ✅ Finish all output items before the terminal event
yield message.emit_done()
yield stream.emit_completed()
```

### Not Closing Content Builders

```python
# ❌ Missing emit_done on the content builder
text = message.add_text_content()
yield text.emit_added()
yield text.emit_text_done("text")
yield message.emit_done()  # Content wasn't properly closed

# ✅ Always call text.emit_done() before closing the message
text = message.add_text_content()
yield text.emit_added()
yield text.emit_text_done("text")
yield text.emit_done()  # Close the content part
yield message.emit_done()
```

### Swallowing Cancellation

```python
# ❌ Don't catch cancellation and convert to failure
try:
    ...
except asyncio.CancelledError:
    yield stream.emit_failed(code="server_error", message="Cancelled")

# ✅ Let it propagate — the library handles it
# Just check cancellation_signal.is_set() and exit cleanly
```

### Branching on Stream/Background Flags

```python
# ❌ Don't do this — the library handles mode negotiation
if request.stream:
    ...
else:
    ...

# ✅ Same event sequence regardless of mode
yield stream.emit_created()
yield stream.emit_in_progress()
for evt in stream.output_item_message("Hello!"):
    yield evt
yield stream.emit_completed()
```

### Expecting a Running Snapshot of the Prior Attempt's In-Flight State

```python
# ❌ There is no "running" snapshot of in-flight state, and no such attribute.
# The library persists the response object at created, at each checkpoint,
# and at terminal — not continuously.
stream = ResponseEventStream(
    response_id=context.response_id,
    response=context.prior_attempt_snapshot,  # AttributeError — no such field
)

# ✅ Use the snapshot that fits your resume model:
#  - framework-checkpoint: context.persisted_response is the LAST resiliently
#    checkpointed snapshot (or the created snapshot, or None).
if context.is_recovery and context.persisted_response is not None:
    stream = ResponseEventStream(
        response_id=context.response_id, response=context.persisted_response,
    )
#  - upstream-owned: build a resumption response from your upstream state.
else:
    resumption = _build_resumption_response(context, request)
    stream = ResponseEventStream(response_id=context.response_id, response=resumption)
```

The library does not keep a *running* snapshot between persistence points — but
`context.persisted_response` gives you the last checkpointed one. See
[Resilience](#resilience) for both resume models.

### Calling Upstream Side-Effecting APIs on Recovery Without a Watermark

```python
# ❌ Re-calls upstream.send_message() on every recovery → duplicate user
# messages in the upstream session history forever.
async def handler(request, context, cancellation_signal):
    if context.is_recovery:
        ... # rebuild stream
    await upstream.send_message(prompt)  # called on every attempt!

# ✅ Watermark before the side-effecting call; check before re-issuing.
async def handler(request, context, cancellation_signal):
    if not context.conversation_chain_metadata.get("upstream_query_in_flight"):
        context.conversation_chain_metadata["upstream_query_in_flight"] = True
        await upstream.send_message(prompt)
    # On recovery with watermark set, skip the send and just receive.
    async for chunk in upstream.receive_response():
        ...
    context.conversation_chain_metadata["upstream_query_in_flight"] = False
```

See [Resilience → Watermark Pattern](#resilience).

### Emitting `response.created` Without `response.in_progress` on Recovery

```python
# ❌ Recovery code path emits created and jumps to output items. No
# reset point — clients merge new items with pre-crash partial state.
async def handler(request, context, cancellation_signal):
    if context.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(...),
        )
        yield stream.emit_created()
        # Jumps straight to producing output → no reset signal for clients

# ✅ Emit response.in_progress before any output items on recovery.
# That event IS the snapshot reset point.
async def handler(request, context, cancellation_signal):
    if context.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(...),
        )
        yield stream.emit_created()
        yield stream.emit_in_progress()  # ← client reset point
        # ... then produce output
```

### Storing Conversation History in `context.conversation_chain_metadata`

```python
# ❌ Metadata isn't for bulk data. Hits payload limits, and the upstream
# framework should be the source of truth for conversation history.
context.conversation_chain_metadata["messages"] = [m.as_dict() for m in conversation]

# ✅ Stash a small reference (session ID, checkpoint ID) and ask upstream
# for the actual state when you need it.
context.conversation_chain_metadata["claude_session_id"] = session_id  # a UUID string
```

See [Resilience → Mental Model](#resilience) for why upstream owns
conversation state.
