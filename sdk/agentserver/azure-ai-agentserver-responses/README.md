# Azure AI Agent Server Responses client library for Python

The `azure-ai-agentserver-responses` package provides the Responses protocol endpoints for Azure AI Hosted Agent containers. It plugs into the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) host framework and adds the full response lifecycle: create, stream (SSE), cancel, delete, replay, and input-item listing.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-responses
```

This automatically installs `azure-ai-agentserver-core` as a dependency.

### Prerequisites

- Python 3.10 or later

## Key concepts

### ResponsesAgentServerHost

`ResponsesAgentServerHost` is an `AgentServerHost` subclass that adds Responses protocol endpoints. Register your handler with the `@app.response_handler` decorator:

```python
@app.response_handler
def my_handler(
    request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
):
    ...
```

### Protocol endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/responses` | Create a new response |
| `GET` | `/responses/{response_id}` | Get response state (JSON or SSE replay via `?stream=true`) |
| `POST` | `/responses/{response_id}/cancel` | Cancel an in-flight response |
| `DELETE` | `/responses/{response_id}` | Delete a stored response |
| `GET` | `/responses/{response_id}/input_items` | List input items (paginated) |

### TextResponse

The simplest way to return text. Handles the full SSE lifecycle automatically (`response.created` → `response.in_progress` → message/content events → `response.completed`):

```python
return TextResponse(context, request, text="Hello!")
```

For streaming, pass an async iterable to `text`:

```python
async def tokens():
    for t in ["Hello", ", ", "world!"]:
        yield t

return TextResponse(context, request, text=tokens())
```

### ResponseEventStream

Use `ResponseEventStream` when you need function calls, reasoning items, multiple output types, or fine-grained event control. Each `yield` maps 1:1 to an SSE event with zero bookkeeping:

```python
stream = ResponseEventStream(response_id=context.response_id, request=request)
yield stream.emit_created()
yield stream.emit_in_progress()
yield from stream.output_item_message("Hello, world!")
yield stream.emit_completed()
```

Drop down to the builder API for full control over individual events:

```python
message = stream.add_output_item_message()
yield message.emit_added()
text = message.add_text_content()
yield text.emit_added()
yield text.emit_delta("Hello!")
yield text.emit_text_done()
yield text.emit_done()
yield message.emit_done()
```

### ResponseContext

The `ResponseContext` provides request-scoped state:

| Property / Method | Description |
|---|---|
| `response_id` | Unique ID for this response |
| `is_shutdown_requested` | Whether the server is draining |
| `isolation` | `IsolationContext` with `user_key` and `chat_key` for multi-tenant state partitioning |
| `client_headers` | Dictionary of `x-client-*` headers forwarded from the platform (keys normalized to lowercase) |
| `query_parameters` | Dictionary of query string parameters |
| `get_input_items()` | Load resolved input items as `Item` subtypes |
| `get_input_text()` | Extract all text content from input items as a single string |
| `get_history()` | Load conversation history items |

### Streaming and background modes

The SDK automatically handles all combinations of `stream` and `background` flags:

- **Default** — Run to completion, return final JSON response
- **Streaming** — Pipe events as SSE in real-time, cancel on client disconnect
- **Background** — Return immediately, handler runs in the background
- **Streaming + Background** — SSE while connected, handler continues after disconnect

### Response lifecycle

The library orchestrates the complete response lifecycle: `created` → `in_progress` → `completed` (or `failed` / `cancelled`). Cancellation, error handling, and terminal event guarantees are all managed automatically.

For detailed handler implementation guidance, see [docs/handler-implementation-guide.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md).

## Examples

### Echo handler

```python
import asyncio

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


app.run()
```

### Function calling

```python
import json

from azure.ai.agentserver.responses import ResponseEventStream

stream = ResponseEventStream(response_id=context.response_id, request=request)
yield stream.emit_created()
yield stream.emit_in_progress()

arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
yield from stream.output_item_function_call("get_weather", "call_001", arguments)

yield stream.emit_completed()
```

### Reasoning + text message

```python
stream = ResponseEventStream(response_id=context.response_id, request=request)
yield stream.emit_created()
yield stream.emit_in_progress()

yield from stream.output_item_reasoning_item("Let me think about this...")
yield from stream.output_item_message("Here is my answer.")

yield stream.emit_completed()
```

### Configuration

```python
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions

options = ResponsesServerOptions(
    default_model="gpt-4o",
    sse_keep_alive_interval_seconds=15,
    shutdown_grace_period_seconds=10,
)

app = ResponsesAgentServerHost(options=options)
```

## Troubleshooting

### Common errors

- **400 Bad Request**: The request body failed validation. Check that optional fields such as `model` (when provided) are valid and that `input` items are well-formed.
- **404 Not Found**: The response ID does not exist or has expired past the configured TTL.
- **400 Bad Request** (cancel): The response was not created with `background=true`, or it has already reached a terminal state.

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/refs/heads/feature/agentserver-durable-preview-share/sdk/agentserver/azure-ai-agentserver-responses/samples) folder for the **durable** examples, and the [`durable-responses-agent-demo/local/`](https://github.com/Azure/azure-sdk-for-python/tree/refs/heads/feature/agentserver-durable-preview-share/sdk/agentserver/azure-ai-agentserver-responses/samples/durable-responses-agent-demo/local) kit to run a crash → recover demo locally:

| Sample | Description |
|---|---|
| [Durable Copilot](https://github.com/Azure/azure-sdk-for-python/tree/refs/heads/feature/agentserver-durable-preview-share/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_18_durable_copilot.py) | Copilot SDK durable + steerable session flow |
| [Durable Streaming](https://github.com/Azure/azure-sdk-for-python/tree/refs/heads/feature/agentserver-durable-preview-share/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_19_durable_streaming.py) | Phase watermarks; skip completed phases on recovery |
| [Durable Steering](https://github.com/Azure/azure-sdk-for-python/tree/refs/heads/feature/agentserver-durable-preview-share/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_20_durable_steering.py) | `context.is_steered_turn` mid-turn steering drain |
| [Durable LangGraph](https://github.com/Azure/azure-sdk-for-python/tree/refs/heads/feature/agentserver-durable-preview-share/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_21_durable_langgraph.py) | LangGraph thread id = `context.conversation_chain_id` |
| [Durable Multiturn](https://github.com/Azure/azure-sdk-for-python/tree/refs/heads/feature/agentserver-durable-preview-share/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_22_durable_multiturn.py) | Per-turn counters in `context.conversation_chain_metadata` |

- [Handler implementation guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md) — Detailed reference for building handlers

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
