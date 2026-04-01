# Azure AI Agent Server Responses API for Python

A Python SDK for building [Starlette](https://www.starlette.io/) servers that implement the [Azure AI Responses API](https://learn.microsoft.com/azure/ai-services). Install the package, implement one handler, and the SDK handles routing, streaming (SSE), background execution, cancellation, state management, and response lifecycle.

## Getting started

### Prerequisites

- Python 3.10+

### Install the package

```bash
pip install azure-ai-agentserver-responses
```

### Implement a handler and register routes

```python
import asyncio
from collections.abc import AsyncIterable
from typing import Any

from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.responses import ResponseContext, CreateResponse, ResponseEventStream
from azure.ai.agentserver.responses.hosting import ResponseHandler


server = AgentHost()
responses = ResponseHandler(server)


@responses.create_handler
def my_handler(
    request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
) -> AsyncIterable[dict[str, Any]]:
    stream = ResponseEventStream(
        response_id=context.response_id,
        model=request.model,
    )

    yield stream.emit_created()
    yield stream.emit_in_progress()

    message = stream.add_output_item_message()
    yield message.emit_added()

    text = message.add_text_content()
    yield text.emit_added()
    yield text.emit_delta("Hello from the Python GettingStarted sample!")
    yield text.emit_done("Hello from the Python GettingStarted sample!")
    yield message.emit_content_done(text)

    yield message.emit_done()

    yield stream.emit_completed()



server.run(host="127.0.0.1", port=5100)
```

Run:

```bash
python app.py
```

This gives you five endpoints:

| Method | Route                                    | Description                             |
|--------|------------------------------------------|-----------------------------------------|
| POST   | `/responses`                             | Create a new response                   |
| GET    | `/responses/{response_id}`               | Get response state (JSON or SSE replay) |
| POST   | `/responses/{response_id}/cancel`        | Cancel an in-flight response            |
| DELETE | `/responses/{response_id}`               | Delete a stored response                |
| GET    | `/responses/{response_id}/input_items`   | List input items (paginated)            |

## Key concepts

### ResponseEventStream

`ResponseEventStream` manages `sequence_number`, `output_index`, `content_index`, `item_id`, and the full `Response` lifecycle automatically — each `yield` maps 1:1 to an SSE event with zero bookkeeping. The handler interacts only through `context.response_id` and the builder API.

It provides a scoped, hierarchical builder that mirrors the SSE event nesting. Each scope manages its own bookkeeping — you never touch `sequence_number`, `output_index`, `content_index`, or `item_id`.

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

### Handler contract

Your handler must implement with this signature:

```python
@responses.create_handler
def my_handler(
    request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
) -> AsyncIterable[dict[str, Any]]:
```

The `ResponseContext` provides:

| Property / Method | Description |
|---|---|
| `response_id` | Unique ID for this response |
| `is_shutdown_requested` | Whether the server is draining |
| `raw_body` | Raw request body (if needed) |
| `get_input_items_async()` | Load input items for this request |
| `get_history_async()` | Load conversation history items |

### Execution modes

The SDK automatically handles all combinations of `stream` and `background` flags:

- **Default** — Run to completion, return final JSON response
- **Streaming** — Pipe events as SSE in real-time, cancel on client disconnect
- **Background** — Return immediately, handler runs in the background
- **Streaming + Background** — SSE while connected, handler continues after disconnect

### Features

- **SSE keep-alive** — Automatic keep-alive comments to prevent proxy/load-balancer timeouts
- **Event stream replay** — SSE replay for previously streamed responses via `?stream=true`
- **Pluggable state provider** — `ResponseProviderProtocol` abstracts state persistence; default `InMemoryResponseProvider` included, override for multi-instance deployments
- **Cancellation** — Cancel endpoint triggers cooperative cancellation via `asyncio.Event`
- **Graceful shutdown** — Handlers distinguish shutdown from cancel via `context.is_shutdown_requested`. Shutdown-terminated responses are marked `failed` for client retry
- **Content negotiation** — GET endpoint returns JSON snapshot by default, or SSE replay when `?stream=true` query parameter is specified
- **Distributed tracing** — Built-in observability hooks for OpenTelemetry integration
- **Error handling** — Global exception handling maps errors to appropriate HTTP responses

### Configuration

```python
from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.responses import ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import ResponseHandler

options = ResponsesServerOptions(
    default_model="gpt-4o",
    sse_keep_alive_interval_seconds=15,
    shutdown_grace_period_seconds=10,
    additional_server_identity="my-server/1.0",
)

responses = ResponseHandler(server, options=options)

```

Options can also be loaded from environment variables:

```python
options = ResponsesServerOptions.from_env()
```

#### Route prefix

```python
# Mount at a custom prefix
responses = ResponseHandler(server, prefix="/openai/v1")
# Routes become: /openai/v1/responses, /openai/v1/responses/{response_id}, etc.
```

#### Custom Response Provider

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

## Examples

### Function call response

```python
stream = ResponseEventStream(response_id=context.response_id, model=request.model)
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
stream = ResponseEventStream(response_id=context.response_id, model=request.model)
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


### More samples

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

## Troubleshooting

### General

Run your server locally first to verify handler behaviour before deploying.

If the server works locally but fails in the cloud, check your logs in the Application Insights instance connected to your Azure AI Foundry Project.


### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues). Mention the package name "azure-ai-agentserver-responses" in the title or content.

## Next steps

Please visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples) folder for runnable examples covering common scenarios.

### Project structure

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

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com/).

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information, see the [Code of Conduct FAQ][code_of_conduct_faq] or contact [opencode@microsoft.com][email_opencode] with any additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[email_opencode]: mailto:opencode@microsoft.com
