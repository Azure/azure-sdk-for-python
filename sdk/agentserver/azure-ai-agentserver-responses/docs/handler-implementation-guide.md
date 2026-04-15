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
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal):
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
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal):
    text = await context.get_input_text()
    return TextResponse(context, request, text=f"Echo: {text}")
```

`text` can also be a sync or async callable — useful when the answer requires I/O:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal):
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
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal):
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
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
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
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
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

When deployed to Azure AI Foundry, durable persistence is enabled automatically —
no custom provider registration is needed.

---

## Handler Signature

```python
@app.response_handler
def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    ...
```

| Parameter | Description |
|-----------|-------------|
| `request` | The deserialized `CreateResponse` body from the client (model, input, tools, instructions, etc.) |
| `context` | Provides the response ID, history resolution, and ID generation helpers |
| `cancellation_signal` | An `asyncio.Event` set on cancellation (explicit `/cancel` call or client disconnection for non-background) |

Your handler can either:

1. **Return a `TextResponse`** — the simplest approach for text-only responses.
2. **Be a Python generator** — `yield` events one at a time for full control.

The library consumes the events, assigns sequence numbers, manages the response
lifecycle, and delivers them to the client.

### TextResponse handlers

Use `return` — no generator yield needed:

```python
@app.response_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    return TextResponse(context, request, text="Hello!")
```

### Generator handlers (ResponseEventStream)

Use `yield` for full control. Can be **sync** or **async**:

```python
# Sync handler
@app.response_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    yield from stream.output_item_message("Hello!")
    yield stream.emit_completed()

# Async handler
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
    response_id: str                        # Library-generated response ID
    is_shutdown_requested: bool             # True when host is shutting down
    request: CreateResponse | None          # Parsed request model
    client_headers: dict[str, str]          # x-client-* headers from request (keys lowercase)
    query_parameters: dict[str, str]        # Query parameters from the HTTP request
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
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    return TextResponse(context, request, text="Hello, world!")
```

#### Using convenience generators

```python
stream = ResponseEventStream(response_id=context.response_id, request=request)
yield stream.emit_created()
yield stream.emit_in_progress()

# Complete text — full value up-front
yield from stream.output_item_message("Hello, world!")

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
yield from stream.output_item_function_call("get_weather", "call_1", args)

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
yield from stream.output_item_function_call_output("call_weather_1", weather_json)
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
yield from stream.output_item_reasoning_item("Let me think about this...")

# Output 1: Message with the answer
yield from stream.output_item_message("The answer is 42.")

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
yield from stream.output_item_message("First message.")

# Output 1
yield from stream.output_item_message("Second message.")

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
yield from stream.output_item_image_gen_call(result_base64)

# Structured outputs
yield from stream.output_item_structured_outputs({"sentiment": "positive", "confidence": 0.95})

# Message with annotations
from azure.ai.agentserver.responses.models import FilePath, UrlCitationBody
yield from stream.output_item_message(
    "Here are your sources.",
    annotations=[
        FilePath(file_id="/reports/summary.pdf", index=0),
        UrlCitationBody(url="https://example.com", start_index=0, end_index=5, title="Link"),
    ],
)
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

The `cancellation_signal` (`asyncio.Event`) is set when:

- A client calls `POST /responses/{id}/cancel` (background mode only)
- A client disconnects the HTTP connection (non-background mode)

### TextResponse Handlers

`TextResponse` handlers use `return TextResponse(...)`. Cancellation is propagated
automatically — if the signal fires while producing text, remaining events are
suppressed and the library handles the winddown.

For streaming, check cancellation between chunks:

```python
@app.response_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    async def stream_tokens():
        async for token in model.stream(prompt):
            if cancellation_signal.is_set():
                return
            yield token

    return TextResponse(context, request, text=stream_tokens())
```

### ResponseEventStream Handlers — Sync

Check the signal between iterations:

```python
@app.response_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(...)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    for chunk in get_chunks():
        if cancellation_signal.is_set():
            break
        yield text.emit_delta(chunk)

    yield stream.emit_completed()
```

### ResponseEventStream Handlers — Async

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(...)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    async for token in model.stream(prompt):
        if cancellation_signal.is_set():
            break
        yield text.emit_delta(token)

    yield stream.emit_completed()
```

### What the Library Does on Cancellation

Let the handler exit cleanly — the server handles the winddown automatically:

1. The library sets the `cancellation_signal` event.
2. It waits up to 10 seconds for the handler to wind down. If the handler doesn't
   cooperate, the cancel endpoint returns the response in its current state.
3. Once the handler finishes (within or beyond the grace period), the response
   transitions to `cancelled` status and a `response.failed` terminal event is
   emitted and persisted.

You don't need to emit any terminal event on cancellation — just check the signal
and exit your generator cleanly.

### Graceful Shutdown

When the host shuts down (e.g., SIGTERM), `context.is_shutdown_requested` is set to
`True` and the cancellation signal is triggered. Use this to distinguish shutdown
from explicit cancel:

```python
@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(...)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    try:
        result = await do_long_running_work()
    except asyncio.CancelledError:
        if context.is_shutdown_requested:
            yield stream.emit_incomplete()
            return
        raise

    async for event in stream.aoutput_item_message(result):
        yield event
    yield stream.emit_completed()
```

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
| `FOUNDRY_PROJECT_ENDPOINT` | — | Foundry project endpoint (enables durable persistence) |
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

Any long-running loop should check `cancellation_signal`:

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

Never branch on `request.stream` or `request.background` in your handler. The
library handles these — your handler always produces the same event sequence
regardless of mode.

```python
# ❌ Don't do this
if request.stream:
    # streaming path
else:
    # non-streaming path

# ✅ Same event sequence for all modes
yield stream.emit_created()
yield stream.emit_in_progress()
yield from stream.output_item_message("Hello!")
yield stream.emit_completed()
```

> **Tip:** `TextResponse` handlers that use `return TextResponse(...)` don't need
> generators at all — they produce the same events for all modes automatically.

---

## Common Mistakes

### Using ResponseEventStream When TextResponse Suffices

```python
# ❌ Unnecessary boilerplate for a simple text response
stream = ResponseEventStream(response_id=context.response_id, request=request)
yield stream.emit_created()
yield stream.emit_in_progress()
yield from stream.output_item_message("Hello!")
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
yield from stream.output_item_message("Hello!")
yield stream.emit_completed()
```
