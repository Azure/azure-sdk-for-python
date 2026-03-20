# azure-ai-agentserver-responses

A Python SDK for building [Starlette](https://www.starlette.io/) servers that implement the [Azure AI Responses API](https://learn.microsoft.com/azure/ai-services). Install the package, implement one handler, and the SDK handles routing, streaming (SSE), background execution, cancellation, state management, and response lifecycle.

## Quick Start

### 1. Install the package

```bash
pip install azure-ai-agentserver-responses
```

### 2. Implement a `ResponseHandler`

```python
from azure.ai.agentserver.responses import ResponseEventStream

class EchoHandler:
    """Simple handler yielding a deterministic response lifecycle."""

    async def create_async(self, request, context, cancellation_signal):
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )

        yield stream.emit_created()
        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()

        text = message.add_text_content()
        yield text.emit_added()

        yield text.emit_delta("Hello, ")
        yield text.emit_delta("world!")

        yield text.emit_done("Hello, world!")
        yield message.emit_content_done(text)
        yield message.emit_done()

        yield stream.emit_completed()
```

`ResponseEventStream` manages `sequence_number`, `output_index`, `content_index`, `item_id`, and the full `Response` lifecycle automatically — each `yield` maps 1:1 to an SSE event with zero bookkeeping. The handler interacts only through `context.response_id` and the builder API.

### 3. Register routes on a Starlette app

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from azure.ai.agentserver.responses.hosting import map_responses_server

app = Starlette()
app.add_route("/ready", lambda r: JSONResponse({"status": "ready"}), methods=["GET"])
map_responses_server(app, EchoHandler())
```

Run with [uvicorn](https://www.uvicorn.org/):

```bash
uvicorn app:app --host 0.0.0.0 --port 5100
```

This gives you five endpoints:

| Method | Route                                    | Description                             |
|--------|------------------------------------------|-----------------------------------------|
| POST   | `/responses`                             | Create a new response                   |
| GET    | `/responses/{response_id}`               | Get response state (JSON or SSE replay) |
| POST   | `/responses/{response_id}/cancel`        | Cancel an in-flight response            |
| DELETE | `/responses/{response_id}`               | Delete a stored response                |
| GET    | `/responses/{response_id}/input_items`   | List input items (paginated)            |

## Features

- **Streaming event builders** — Scoped builders eliminate SSE bookkeeping (see below)
- **Four execution modes** — The SDK automatically handles all combinations of `stream` and `background` flags:
  - **Default** — Run to completion, return final JSON response
  - **Streaming** — Pipe events as SSE in real-time, cancel on client disconnect
  - **Background** — Return immediately, handler runs in the background
  - **Streaming + Background** — SSE while connected, handler continues after disconnect
- **SSE keep-alive** — Automatic keep-alive comments to prevent proxy/load-balancer timeouts
- **Event stream replay** — SSE replay for previously streamed responses via `?stream=true`
- **Pluggable state provider** — `ResponseProviderProtocol` abstracts state persistence; default `InMemoryResponseProvider` included, override for multi-instance deployments
- **Cancellation** — Cancel endpoint triggers cooperative cancellation via `asyncio.Event`
- **Graceful shutdown** — Handlers distinguish shutdown from cancel via `context.is_shutdown_requested`. Shutdown-terminated responses are marked `failed` for client retry
- **Content negotiation** — GET endpoint returns JSON snapshot by default, or SSE replay when `?stream=true` query parameter is specified
- **Distributed tracing** — Built-in observability hooks for OpenTelemetry integration
- **Error handling** — Global exception handling maps errors to appropriate HTTP responses

## Streaming Event Builder

`ResponseEventStream` provides a scoped, hierarchical builder that mirrors the SSE event nesting. Each scope manages its own bookkeeping — you never touch `sequence_number`, `output_index`, `content_index`, or `item_id`.

```
ResponseEventStream                          → response.created / in_progress / completed / failed / incomplete
  ├─ OutputItemMessageBuilder                → output_item.added / done
  │    ├─ TextContentBuilder                 → content_part.added / text.delta / text.done / content_part.done
  │    │    └─ emit_annotation_added         → output_text.annotation.added
  │    └─ RefusalContentBuilder              → content_part.added / refusal.delta / refusal.done / content_part.done
  ├─ OutputItemFunctionCallBuilder           → output_item.added / function_call_arguments.delta / done / output_item.done
  ├─ OutputItemReasoningItemBuilder          → output_item.added / done
  │    └─ ReasoningSummaryPartBuilder        → summary_part.added / text.delta / text.done / summary_part.done
  ├─ OutputItemFileSearchCallBuilder         → output_item.added / in_progress / searching / completed / done
  ├─ OutputItemWebSearchCallBuilder          → output_item.added / in_progress / searching / completed / done
  ├─ OutputItemCodeInterpreterCallBuilder    → output_item.added / in_progress / code.delta / code.done / completed / done
  ├─ OutputItemImageGenCallBuilder           → output_item.added / in_progress / partial_image / completed / done
  ├─ OutputItemMcpCallBuilder                → output_item.added / in_progress / args.delta / args.done / completed|failed / done
  ├─ OutputItemMcpListToolsBuilder           → output_item.added / in_progress / completed|failed / done
  └─ OutputItemCustomToolCallBuilder         → output_item.added / input.delta / input.done / done
```

**Naming convention:** `add_output_item_*()` methods create child scopes (return builders). `emit_*()` methods produce SSE events (return event dicts).

### Function call response

```python
stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
yield stream.emit_created()
yield stream.emit_in_progress()

fn_call = stream.add_output_item_function_call("get_weather", "call_abc123")
yield fn_call.emit_added()
yield fn_call.emit_arguments_delta('{"location":')
yield fn_call.emit_arguments_delta('"San Francisco"}')
yield fn_call.emit_arguments_done('{"location":"San Francisco"}')
yield fn_call.emit_done()

yield stream.emit_completed()
```

### Reasoning + text message (multiple output items)

Output indices auto-increment across `add_output_item_*()` calls:

```python
stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
yield stream.emit_created()
yield stream.emit_in_progress()

# output_index=0: reasoning item
reasoning = stream.add_output_item_reasoning_item()
yield reasoning.emit_added()
summary = reasoning.add_summary_part()
yield summary.emit_added()
yield summary.emit_text_delta("Let me think about this...")
yield summary.emit_text_done("Let me think about this...")
yield summary.emit_done()
yield reasoning.emit_summary_part_done(summary)
yield reasoning.emit_done()

# output_index=1: message item (auto-incremented)
message = stream.add_output_item_message()
yield message.emit_added()
text = message.add_text_content()
yield text.emit_added()
yield text.emit_delta("Here is my answer.")
yield text.emit_done("Here is my answer.")
yield message.emit_content_done(text)
yield message.emit_done()

yield stream.emit_completed()
```

### Conversation history (multi-turn)

```python
class ConversationHandler:
    async def create_async(self, request, context, cancellation_signal):
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_in_progress()

        # Retrieve history and input from context
        history = await context.get_history_async()
        input_items = await context.get_input_items_async()
        current_input = extract_text(request)
        reply = build_reply(current_input, history, input_items)

        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()
        yield text.emit_delta(reply)
        yield text.emit_done(reply)
        yield message.emit_content_done(text)
        yield message.emit_done()

        yield stream.emit_completed()
```

## Handler Contract

Your handler must implement `create_async` with this signature:

```python
from typing import AsyncIterable
import asyncio

class ResponseHandler(Protocol):
    async def create_async(
        self,
        request: CreateResponse,
        context: ResponseContext,
        cancellation_signal: asyncio.Event,
    ) -> AsyncIterable[dict]: ...
```

The `ResponseContext` provides:

| Property / Method | Description |
|---|---|
| `response_id` | Unique ID for this response |
| `is_shutdown_requested` | Whether the server is draining |
| `raw_body` | Raw request body (if needed) |
| `get_input_items_async()` | Load input items for this request |
| `get_history_async()` | Load conversation history items |

## Configuration

```python
from azure.ai.agentserver.responses import ResponsesServerOptions

options = ResponsesServerOptions(
    default_model="gpt-4o",
    sse_keep_alive_interval_seconds=15,
    shutdown_grace_period_seconds=10,
    additional_server_identity="my-server/1.0",
)

map_responses_server(app, handler, options=options)
```

Options can also be loaded from environment variables:

```python
options = ResponsesServerOptions.from_env()
```

### Route prefix

```python
# Mount at a custom prefix
map_responses_server(app, handler, prefix="/openai/v1")
# Routes become: /openai/v1/responses, /openai/v1/responses/{response_id}, etc.
```

### Custom Response Provider

For multi-instance deployments, implement `ResponseProviderProtocol`:

```python
from azure.ai.agentserver.responses import ResponseProviderProtocol

class MyDurableProvider:
    """Implements ResponseProviderProtocol with database-backed storage."""

    async def create_response_async(self, response, input_items, history_item_ids):
        ...

    async def get_response_async(self, response_id):
        ...

    async def update_response_async(self, response):
        ...

    async def delete_response_async(self, response_id):
        ...

    async def get_input_items_async(self, response_id, limit=20, ascending=False, after=None, before=None):
        ...

    async def get_items_async(self, item_ids):
        ...

    async def get_history_item_ids_async(self, previous_response_id, conversation_id, limit):
        ...
```

## Project Structure

```
azure/ai/agentserver/responses/
  ├─ hosting/              Starlette routing, background execution, validation, observability
  ├─ models/               Domain models (runtime state, errors, generated contracts)
  │    └─ _generated/      TypeSpec-generated model classes
  ├─ store/                Persistence abstraction and in-memory provider
  ├─ streaming/            Event stream builders, SSE encoding, lifecycle state machine
  │    └─ _builders/       Scoped builder classes (message, function call, reasoning, etc.)
  ├─ _handlers.py          Handler protocol and runtime context
  ├─ _options.py           Server configuration (ResponsesServerOptions)
  └─ _id_generator.py      Deterministic ID generation
samples/                   Runnable Starlette sample servers
tests/                     Test suite (contract, unit, integration)
type_spec/                 TypeSpec definitions and pipeline
```

## Samples

The `samples/` directory contains runnable Starlette servers demonstrating the SDK:

| Sample | Description |
|--------|-------------|
| GettingStarted | Minimal echo handler — text message in default, streaming, and background modes |
| FunctionCalling | Two-turn conversation — server emits a function call, client submits output, server returns result |
| MultiOutput | Multiple output items — reasoning followed by a text message |
| ConversationHistory | Multi-turn with `previous_response_id` — demonstrates `get_history_async()` and conversation chaining |

Each sample includes:
- `app.py` — the sample Starlette server
- `test.py` — a `requests`-based client that exercises the scenario

## Development

### Prerequisites

- Python 3.10+
- Node.js (for TypeSpec model generation)

### Build & Test

```bash
make install    # pip install -e .[dev]
make test       # pytest
make lint       # ruff check + mypy
make format     # ruff format
make all        # install → test → lint
```

### Running tests

```bash
# All tests
pytest

# Contract tests only (full HTTP pipeline via Starlette TestClient)
pytest tests/contract/

# Unit tests only
pytest tests/unit/
```

## Requirements

- Python >= 3.10
- [azure-core](https://pypi.org/project/azure-core/) >= 1.30.0
- [starlette](https://pypi.org/project/starlette/) >= 1.0.0rc1, < 2.0.0
- [uvicorn](https://pypi.org/project/uvicorn/) >= 0.31.0

## License

MIT
