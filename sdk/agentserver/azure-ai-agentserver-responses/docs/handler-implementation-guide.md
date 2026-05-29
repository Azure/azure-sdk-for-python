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
- [Durability](#durability)
  - [Mental Model](#mental-model)
  - [The Recovery Loop](#the-recovery-loop)
  - [Default Pattern (recovery-aware)](#default-pattern-recovery-aware)
  - [Fallback Pattern (no opt-in)](#fallback-pattern-no-opt-in)
  - [Upstream History Pattern](#upstream-history-pattern)
  - [Watermark Pattern](#watermark-pattern)
  - [Resumption Response Construction](#resumption-response-construction)
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

The `cancellation_signal` (`asyncio.Event`) fires when the framework needs
the handler to stop. Three scenarios trigger it, each with different
semantics:

| Reason | Trigger | Framework Behaviour | What Handler Should Do |
|--------|---------|---------------------|----------------------|
| **Steering** | New turn queued (steerable conversations) | If no terminal emitted → auto-emit `response.failed`. If terminal emitted → honour it. | Break loop → close builders → `emit_completed()` |
| **Client Cancel** | `POST /responses/{id}/cancel` or disconnect on non-bg | Framework forces `cancelled` regardless of handler output. Output items abandoned. | Return as soon as cleanup is done. |
| **Shutdown** | SIGTERM/SIGINT | Hard cutoff after `shutdown_grace_period_seconds`. Durable+bg: leave in_progress for re-entry. Others: mark failed. | Checkpoint progress → return without terminal event (durable+bg). Or complete quickly. |

**Key status rules:**
- `cancelled` is ONLY produced by explicit client cancellation (`/cancel` or foreground disconnect). Never by steering or shutdown.
- `incomplete` is NEVER set by the framework — it's exclusively developer-controlled.

> **On shutdown for durable handlers**: returning without a terminal event leaves the response `in_progress` and the framework re-invokes your handler on restart. See [Durability](#durability) for the recovery contract — what the recovered handler must do, what the library guarantees on re-entry, and how clients reconcile the multi-attempt stream.

### Default Pattern (handles all cases)

Most handlers don't need to distinguish the reason — just break and complete:

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
        if cancellation_signal.is_set():
            break
        yield text.emit_delta(token)

    yield text.emit_text_done()
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()
```

This works for all three reasons:
- **Steering**: partial output is preserved, `completed` status is correct
- **Client cancel**: framework overrides status to `cancelled` regardless
- **Shutdown**: if you emit `completed` within the grace period, the response
  finishes successfully. If you can't finish in time, prefer the advanced pattern.

### Advanced Pattern (pre-entry steering)

For steerable handlers, the signal may be pre-set when a newer turn is
already queued. Check at the top — only emit `completed` for steering
(the response was superseded). For other cancellations, just return and
let the framework handle terminal status:

```python
from azure.ai.agentserver.responses import CancellationReason

@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()

    # Pre-entry: signal pre-set could be steering, shutdown, or client cancel.
    # Only emit completed for steering. Others: just return.
    if cancellation_signal.is_set():
        if context.cancellation_reason == CancellationReason.STEERED:
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

    # Shutdown mid-stream: return without terminal → re-entered on restart.
    if context.cancellation_reason == CancellationReason.SHUTTING_DOWN:
        return

    yield text.emit_text_done()
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()
```

After the streaming loop breaks, check for shutdown BEFORE closing builders.
If shutdown interrupted mid-stream, return without terminal — the response
stays `in_progress` and the handler is re-entered on restart to produce the
full output.

For all other cases (steering, client cancel, normal completion), close
builders and emit `completed`:

- **Steering/Normal**: `completed` is the correct status.
- **Client cancel**: framework overrides to `cancelled` regardless.
- **Shutdown**: handler hasn't finished its work — leave in_progress for re-entry.

### Metadata Usage in Cancellation

`durability.metadata` is appropriate for storing lightweight progress signals
that help on re-entry — for example `last_processed_item_id` so you can
take unprocessed items from response history after that point, or a step index
for multi-phase workflows.

**Acceptable**: step counters, message IDs, phase indicators, checkpoint
references for framework-native stores (e.g., a SqliteSaver checkpoint ID).

**Not acceptable**: full conversation history, LLM outputs, or framework
checkpoint data. These belong in framework-native stores (SqliteSaver for
LangGraph, Copilot SDK sessions, external stores for Claude, etc.).

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

### Backward Compatibility

The `context.is_shutdown_requested` property still works:

```python
if cancellation_signal.is_set() and context.is_shutdown_requested:
    # Same as: context.cancellation_reason == CancellationReason.SHUTTING_DOWN
    ...
```

Prefer `context.cancellation_reason` for new code — it covers all three cases.

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

## Durability

The framework re-invokes your handler when the server crashes mid-response
(if `durable_background=True` and the request had `store=true, background=true`).
What that re-invocation gives you, what you have to do to take advantage of it,
and how clients reconcile a multi-attempt stream is the **Recovery Contract**.

The normative version of the Recovery Contract — every row × cancellation-path
cell, the exact handler-visible signals on recovery, and the framework's
persistence guarantees — lives in
[`sdk/agentserver/specs/durability-contract.md`](../../specs/durability-contract.md).
That document is the source of truth; this section is the developer-facing
how-to plus worked examples. The conformance suite at
`tests/e2e/durability_contract/` exercises every cell.

You can opt out of all of this and your response will still be correct (just
duplicative). You opt in when you want the recovered attempt to pick up where
the crashed one left off instead of re-running the whole turn.

### Mental Model

Three layers, each owning a specific slice of state:

| Layer | Owns | On crash recovery, surfaces / provides |
|---|---|---|
| **Library** (this SDK) | Persisted SSE event stream (every event you emitted, in order) — used for client replay via `starting_after=`. The library writes the persisted response *object* exactly twice per response across the entire recovery lifecycle: once at the first attempt's `response.created` and once at the first attempt that reaches a terminal event. Subsequent attempts emit `response.created` again but the framework dedups the write (idempotent persistence keyed on `response_id`). It does NOT keep a running snapshot of in-flight state. | Re-invokes the handler. Surfaces `entry_mode = "recovered"`, `is_recovery`, `run_attempt`. Replays persisted events to reconnecting clients. Reconstructs the in-memory handler context (`record`, `parsed`, `context`, cancellation signal) from the durable task input — the handler sees the same `response_id` it had on the first attempt. |
| **Handler** (your code) | The "what was safely committed" decision, plus side-effect watermarks in `durability.metadata`. | Decides the resumption point. Constructs the **resumption response**. Emits a fresh `response.in_progress` carrying it. Continues producing new output items. |
| **Upstream framework** (Claude SDK, Copilot SDK, LangGraph, your own LLM client) | The conversational / graph / agent state that has to outlive a process death. | Has its own resume facility (session ID, checkpoint store) that you call from the handler. |

You do NOT own response event durability — that's the library. The library
does NOT own conversational durability — that's upstream. You glue them
together.

### The Recovery Loop

When the server restarts after a crash and your handler is re-invoked:

1. The library calls your handler with `context.durability.entry_mode == "recovered"` and `run_attempt > 0`.
2. You query upstream (and your own `metadata` watermarks) to determine the **resumption point** — the most recent state you are confident is durably committed.
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

- Persists every SSE event in order. No reordering, no deduplication of stream events.
- Persists the response *object* exactly twice per response_id across the entire recovery lifecycle: once at the first attempt's `response.created` and once at the first attempt that reaches a terminal event. Subsequent attempts' `response.created` and terminal writes are deduplicated by the framework (idempotent persistence keyed on `response_id`); the handler does not need to branch.
- Reconstructs the in-memory handler context (`record`, `parsed`, `context`, cancellation signal, runtime-state registration) from the durable task input on any cross-process recovery. The recovered handler sees the same `response_id` it had on the first attempt — id generation is a fresh-entry-only concern.
- Surfaces `entry_mode`, `run_attempt`, `is_recovery` via `context.durability` (see [DurabilityContext API](durable-responses-developer-guide.md#durabilitycontext-api)). The library does NOT expose a snapshot of the prior attempt — handler must consult its upstream framework for resumption state.
- Treats any `response.in_progress` event after the first one as a snapshot reset.
- Replays persisted events to reconnecting clients on `starting_after=`. The reset `in_progress` is part of the replay; clients use it as the reconciliation signal.
- **Translates the "return on shutdown" handler pattern into the right durable-task recovery behavior.** When your handler returns without emitting a terminal event AND the framework is in graceful shutdown (`cancellation_signal` is set due to SHUTTING_DOWN), the responses package detects this and signals the underlying durable-task primitive to leave the task `in_progress` so the next process lifetime re-invokes your handler with `entry_mode="recovered"`. You simply write `return` in your handler on shutdown — the framework handles the convention; you do not need to raise `CancelledError` yourself or know the durable-task primitive's internals.
- For `background=false` responses: marks the response `failed` on crash and does NOT re-invoke the handler.
- For `store=false` responses: best-effort `failed` marker during shutdown grace period; no recovery.

### What the Handler Does

- Branches on `context.durability.is_recovery` (or `entry_mode == "recovered"`) to choose fresh-entry vs recovered-entry code paths.
- Builds the resumption response from upstream-framework state + own metadata watermarks. **Excludes in-flight items.**
- Constructs `ResponseEventStream(response=resumption_response)` on recovered entry.
- Emits `response.in_progress` early in the recovered path (this is the reset).
- Uses upstream framework's native resume facility (e.g. session resume, checkpoint replay) — never re-runs a side-effecting upstream call without checking a watermark first.
- Watermarks any upstream side-effecting call by writing a small marker to `durability.metadata` **before** the call and clearing it **after** the call has been durably committed upstream.
- For upstream-session-id needs: reads `context.conversation_chain_id` — the framework-computed stable identifier for the current conversation chain. Use this as the session id passed to upstream frameworks (Claude `session_id`, Copilot `session_id`, LangGraph `thread_id`) instead of allocating your own UUID. The value is derived from `conversation_id` if present, else `previous_response_id` in steerable mode, else `response_id` — stable across all attempts of a given task. See the [DurabilityContext API](durable-responses-developer-guide.md#durabilitycontext-api) section of the developer guide for the full derivation rule.

### Default Pattern (recovery-aware)

A framework-agnostic recovery-aware handler. The upstream-specific reconciliation
(how to query upstream for its state, how to resume a session) is in your
sample's docstring; the pattern below stays uniform.

```python
from azure.ai.agentserver.responses import (
    CancellationReason, CreateResponse, ResponseContext, ResponseEventStream,
)
from azure.ai.agentserver.responses.models._generated import ResponseObject


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal):
    durability = context.durability

    # ── Choose between fresh and recovered entry ────────────────────
    if durability.is_recovery:
        # Ask upstream (or read metadata) for what was safely committed.
        resumption = _build_resumption_response(durability, context, request)
        stream = ResponseEventStream(
            response_id=context.response_id, response=resumption,
        )
    else:
        stream = ResponseEventStream(
            response_id=context.response_id, request=request,
        )

    yield stream.emit_created()  # same call on fresh and recovered; framework dedups

    # Cancellation policy composes with recovery:
    # Phase 1 pre-entry cancel still applies — only emit completed on STEERED.
    if cancellation_signal.is_set():
        if context.cancellation_reason == CancellationReason.STEERED:
            yield stream.emit_completed()
        return

    # ── This is the client-visible reset point on recovery ──────────
    yield stream.emit_in_progress()

    # Now produce new content. Use upstream's resume facility before any
    # side-effecting call. Watermark before; clear after upstream commit.
    async for event in _produce_new_output(stream, durability, request, cancellation_signal):
        yield event

    # Phase 3 cancellation: on shutdown mid-work, return without terminal
    # so the framework re-invokes us again on the next restart.
    if context.cancellation_reason == CancellationReason.SHUTTING_DOWN:
        return

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
durable history that matters, you MUST adopt the recovery-aware pattern. If
your handler has no upstream side effects (e.g. it streams from an
idempotent source), the fallback is fine.

### Upstream History Pattern (preferred when available)

Many stateful upstream SDKs expose their persisted conversation log directly —
e.g. `claude_agent_sdk.get_session_messages(session_id)` returns the list of
messages the SDK has durably committed, and Copilot's `session.get_messages()`
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

- The detection input is the upstream's own durable log — there is no window
  between "we sent the call" and "we wrote our watermark" where a crash leaves
  the handler and the upstream out of sync.
- No `durability.metadata` write, no `metadata.flush()`, no decision about
  flush-before vs flush-after.
- On any attempt (fresh, recovered, multiply-recovered) the same one-liner
  works: query history, compare, send only if needed.

Edge case to document in your sample: if a prior turn's input was byte-equal to
the current turn's input AND that prior turn completed normally, the
"last user message in history equals current input" heuristic incorrectly
skips. Rare in practice for human-driven conversations; if your domain has
machine-generated identical-input replays, fall back to the watermark pattern
below, or have the framework provide stable per-turn identity (see the
`conversation_chain_id` follow-up in spec 013).

### Watermark Pattern (fallback when upstream exposes no persisted history)

When the upstream SDK does **not** expose its committed log — or does not
distinguish "queued but unacked" from "durably committed" — the framework
cannot know which of your calls have side effects, so you stamp a marker in
`durability.metadata` before the call and clear it after the upstream commit.

The strict at-most-once pattern is **write → flush → side effect → write →
flush**. The explicit `await metadata.flush()` ensures the watermark hits
durable storage before the side effect runs; otherwise the framework's 5s
auto-flush could leave the watermark in memory only and a crash between
"side effect issued" and "auto-flush fires" would re-issue the side effect
on recovery.

```python
durability = context.durability

# Stamp BEFORE the side-effecting call, and FLUSH to make the marker durable.
durability.metadata["upstream_query_in_flight"] = True
await durability.metadata.flush()

await upstream.send_message(prompt)

# Stream the response back…
async for chunk in upstream.receive_response():
    if cancellation_signal.is_set():
        break
    yield ...emit_delta(chunk)

# Clear AFTER the upstream durably committed the result
# (e.g. assistant message landed in the upstream's session log), and
# FLUSH so the cleared marker survives a subsequent crash.
durability.metadata["upstream_query_in_flight"] = False
await durability.metadata.flush()
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

The resumption response is a small `ResponseObject` containing only the output
items you are confident were durably committed. A minimal example for a handler
whose only safe state is "the user message was committed; nothing else":

```python
from azure.ai.agentserver.responses.models._generated import ResponseObject


def _build_resumption_response(durability, context, request) -> ResponseObject:
    return ResponseObject({
        "id": context.response_id,
        "object": "response",
        "status": "in_progress",
        "output": [],   # exclude in-flight items from the crashed attempt
        "model": request.model,
    })
```

A handler whose upstream framework checkpoints intermediate state (e.g.
LangGraph's SqliteSaver) can include the completed output items it can
reconstruct from that checkpoint:

```python
def _build_resumption_response(durability, context, request) -> ResponseObject:
    durable_items = _reconstruct_output_from_upstream_checkpoint(durability)
    return ResponseObject({
        "id": context.response_id,
        "object": "response",
        "status": "in_progress",
        "output": durable_items,
        "model": request.model,
    })
```

There is no library-managed snapshot of the prior attempt's in-flight state.
The library persists the response object exactly once at start (the first
attempt's `response.created`) and exactly once at end (the first attempt
that reaches a terminal event). Subsequent attempts re-emit these events
naturally; the framework dedups the writes keyed on `response_id`. Trust your
upstream framework (or your own metadata watermarks) as the source of truth
for what's safely committed.

### Recovery × Cancellation Composition

The cancellation policy from the [Cancellation](#cancellation) section composes
with recovery cleanly:

- **Recovered entry + cancellation_signal pre-set**: same as fresh entry —
  only `STEERED` emits `completed`; others return.
- **Recovered entry + cancellation_signal fires mid-stream**: same as fresh
  entry's Phase 2 — break the loop, then check `SHUTTING_DOWN` for
  return-without-terminal; otherwise close builders and `emit_completed`.
- **Crash during recovery itself** (`run_attempt > 1`): same code path; each
  attempt queries upstream for its current state, computes a (possibly
  different) resumption response, emits a fresh reset `in_progress`. The
  loop is re-entrant.

### Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `durable_background` | `True` | Enable crash-recoverable background responses |
| `steerable_conversations` | `False` | Multi-turn conversation steering (see [Cancellation](#cancellation)) |
| `max_pending` | `10` | Max queued turns for steerable mode |
| `replay_event_ttl_seconds` | `600` | Stream event replay window |

See the [Durable Responses Developer Guide](durable-responses-developer-guide.md)
for the configuration matrix (`store` × `background` × `durable_background`),
the full `DurabilityContext` API surface, and client-side reconciliation rules.

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

### Expecting the Library to Hand You a Snapshot of the Prior Attempt

```python
# ❌ The library does NOT keep a running snapshot of in-flight state.
# It only persists the response object at created and at terminal.
# `durability.last_snapshot` does not exist.
stream = ResponseEventStream(
    response_id=context.response_id,
    response=durability.last_snapshot,  # AttributeError
)

# ✅ Build a resumption response from your upstream framework state.
# Only the upstream knows what was safely committed.
resumption = _build_resumption_response(durability, context, request)
stream = ResponseEventStream(
    response_id=context.response_id,
    response=resumption,
)
```

See [Durability → Resumption Response Construction](#durability) for what to
include and what to leave out.

### Calling Upstream Side-Effecting APIs on Recovery Without a Watermark

```python
# ❌ Re-calls upstream.send_message() on every recovery → duplicate user
# messages in the upstream session history forever.
async def handler(request, context, cancellation_signal):
    if durability.is_recovery:
        ... # rebuild stream
    await upstream.send_message(prompt)  # called on every attempt!

# ✅ Watermark before the side-effecting call; check before re-issuing.
async def handler(request, context, cancellation_signal):
    if not durability.metadata.get("upstream_query_in_flight"):
        durability.metadata["upstream_query_in_flight"] = True
        await upstream.send_message(prompt)
    # On recovery with watermark set, skip the send and just receive.
    async for chunk in upstream.receive_response():
        ...
    durability.metadata["upstream_query_in_flight"] = False
```

See [Durability → Watermark Pattern](#durability).

### Emitting `response.created` Without `response.in_progress` on Recovery

```python
# ❌ Recovery code path emits created and jumps to output items. No
# reset point — clients merge new items with pre-crash partial state.
async def handler(request, context, cancellation_signal):
    if durability.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(...),
        )
        yield stream.emit_created()
        # Jumps straight to producing output → no reset signal for clients

# ✅ Emit response.in_progress before any output items on recovery.
# That event IS the snapshot reset point.
async def handler(request, context, cancellation_signal):
    if durability.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(...),
        )
        yield stream.emit_created()
        yield stream.emit_in_progress()  # ← client reset point
        # ... then produce output
```

### Storing Conversation History in `durability.metadata`

```python
# ❌ Metadata isn't for bulk data. Hits payload limits, and the upstream
# framework should be the source of truth for conversation history.
durability.metadata["messages"] = [m.as_dict() for m in conversation]

# ✅ Stash a small reference (session ID, checkpoint ID) and ask upstream
# for the actual state when you need it.
durability.metadata["claude_session_id"] = session_id  # a UUID string
```

See [Durability → Mental Model](#durability) for why upstream owns
conversation state.
