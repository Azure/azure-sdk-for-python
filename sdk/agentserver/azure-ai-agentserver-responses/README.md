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
async def my_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    ...
```

Handlers MUST be `async def` and take exactly three positional parameters
(`request`, `context`, `cancellation_signal`). Sync handlers and the 2-arg
signature `(request, context)` are hard-rejected at decoration time.
Cancellation is observed via the `cancellation_signal` event (set on
client cancel, `/cancel` API, or steering pressure). Server shutdown is
a **distinct** signal observed via `context.shutdown` — shutdown does
NOT fire the cancellation signal; handlers that care about both must
inspect each independently. See the handler implementation guide for
the full surface.

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
| `conversation_id` / `conversation_chain_id` | Conversation identifiers; `conversation_chain_id` is the framework-computed stable id shared by every turn in a chain |
| `is_shutdown_requested` | Whether the server is draining |
| `platform_context` | `PlatformContext` with `user_id_key` (from `x-agent-user-id`) and `call_id` (from `x-agent-foundry-call-id`) for multi-tenant state partitioning and per-request caller-context forwarding |
| `client_headers` | Dictionary of `x-client-*` headers forwarded from the platform (keys normalized to lowercase) |
| `query_parameters` | Dictionary of query string parameters |
| `shutdown` | `asyncio.Event` set on graceful server shutdown — distinct from the per-request cancellation signal |
| `client_cancelled` | `bool` set when the cancel cause is `/cancel` endpoint or non-bg POST disconnect |
| `is_recovery` | `bool` set on a crash-recovered re-entry |
| `is_steered_turn` | `bool` set on the drain re-entry that follows a steering input |
| `pending_input_count` | `int` count of queued steering inputs |
| `exit_for_recovery()` | `await` to opt into the graceful-shutdown recovery path |
| `get_input_items()` | Load resolved input items as `Item` subtypes |
| `get_input_text()` | Extract all text content from input items as a single string |
| `get_history()` | Load conversation history items |

Persist cross-turn application state explicitly with
`azure.ai.agentserver.core.storage.FoundryStateStore`, using
`conversation_chain_id` as part of the store name.

The per-request cancellation signal is delivered as the **3rd
positional handler argument** (`cancellation_signal: asyncio.Event`),
not via a `ResponseContext` attribute. It fires on client cancel
(`/cancel` API or non-bg POST disconnect) or steering pressure; it
does NOT fire on server shutdown — `context.shutdown` is the
independent surface for that case.

### Streaming and background modes

The SDK automatically handles all combinations of `stream` and `background` flags:

- **Default** — Run to completion, return final JSON response
- **Streaming** — Pipe events as SSE in real-time, cancel on client disconnect
- **Background** — Return immediately, handler runs in the background
- **Streaming + Background** — SSE while connected, handler continues after disconnect

### Response lifecycle

The library orchestrates the complete response lifecycle: `created` → `in_progress` → `completed` (or `failed` / `cancelled`). Cancellation, error handling, and terminal event guarantees are all managed automatically.

For detailed handler implementation guidance, see [docs/handler-implementation-guide.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md).

### Resilience

Crash recovery is **opt-in** via `ResponsesServerOptions(resilient_background=True)`. When opted in, background responses with `store=True` are crash-recoverable: the handler is re-invoked on restart and the recovered context exposes `context.is_recovery == True`. Stream events are persisted incrementally so clients can reconnect and resume from where they left off. Without the opt-in (the default), a crash mid-handler marks the response `failed` instead of re-invoking the handler. For advanced scenarios (metadata checkpointing, multi-turn steering), see the [Resilient Responses Developer Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/resilient-responses-developer-guide.md).

## Examples

### Echo handler

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


app.run()
```

### Multi-user session (per-request call ID)

On container protocol `2.0.0` a single agent session can serve **multiple users**. Forwarding the per-request `x-agent-foundry-call-id` on outbound toolbox calls lets the tool server resolve *which* user made this request and act on their behalf — so user A's and user B's requests to the same session each get a user-scoped result. (`x-agent-user-id` is never forwarded; the tool resolves the user from the call ID server-side. Use `context.platform_context.user_id_key` only for the container's own per-user state.)

```python
import asyncio
import os

import httpx
from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

app = ResponsesAgentServerHost()


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    # platform_headers() echoes x-agent-foundry-call-id only (never x-agent-user-id).
    headers = get_request_context().platform_headers()

    # Toolbox / MCP — attach the call ID PER CALL. The MCP session is long-lived and
    # shared across users/turns, so never bake one call's ID into static client headers.
    async with httpx.AsyncClient() as mcp:
        resp = await mcp.post(
            f"{os.environ['FOUNDRY_PROJECT_ENDPOINT']}/toolboxes/github/mcp",
            headers={"Authorization": f"Bearer {get_agent_token()}", **headers},  # get_agent_token(): the agent's managed-identity token
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "list_my_assigned_issues", "arguments": {}}},
        )
        # The toolbox resolved the caller from the call ID and returned THIS user's issues.

    return TextResponse(context, request, text=resp.text)


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
- **404 Not Found**: The response ID does not exist. In hosted deployments persisted responses live in the Foundry hosted responses store; in local development they live under `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/responses/` by default. A missing record may indicate the response was never persisted or was deleted via `DELETE /responses/{id}`.
- **400 Bad Request** (cancel): The response was not created with `background=true`, or it has already reached a terminal state.

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples) folder for complete working examples:

| Sample | Description |
|---|---|
| [Getting Started](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_01_getting_started.py) | Minimal echo handler using `TextResponse` |
| [Streaming Text Deltas](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_02_streaming_text_deltas.py) | Token-by-token streaming with `configure` callback |
| [Full Control](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_03_full_control.py) | Convenience, streaming, and builder — three ways to emit output |
| [Function Calling](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_04_function_calling.py) | Two-turn function calling with convenience and builder variants |
| [Conversation History](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_05_conversation_history.py) | Multi-turn study tutor with `context.get_history()` |
| [Multi-Output](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_06_multi_output.py) | Reasoning + message in a single response |
| [Streaming Upstream](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_10_streaming_upstream.py) | Forward to upstream streaming LLM via `openai` SDK |
| [Non-Streaming Upstream](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_11_non_streaming_upstream.py) | Forward to upstream non-streaming LLM, emit items via builders |
| [Image Generation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_12_image_generation.py) | Image gen convenience, streaming partials, and full-control builder |
| [Image Input](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_13_image_input.py) | Receive images via URL, base64 data URL, or file ID |
| [File Inputs](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_14_file_inputs.py) | Receive files via base64 data URL, URL, or file ID |
| [Annotations](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_15_annotations.py) | Attach file_path, file_citation, and url_citation annotations |
| [Structured Outputs](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_16_structured_outputs.py) | Return structured JSON as a `structured_outputs` item |
| [Resilient Streaming](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_19_resilient_streaming.py) | Framework-checkpoint handler — one item per phase + `stream.checkpoint()`, recovery via `context.persisted_response` |
| [Resilient Steering](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_20_resilient_steering.py) | `context.is_steered_turn` on the drain re-entry with `resilient_background=True, steerable_conversations=True`; naive re-run recovery |
| [Resilient LangGraph](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_21_resilient_langgraph.py) | Real-time streaming LangGraph agent composing `AsyncSqliteSaver` with framework `stream.checkpoint()` / `context.persisted_response`; graph checkpoint id stored in `internal_metadata` so recovery rewinds to the persisted point (no divergence window) |
| [Resilient Multi-turn](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_22_resilient_multiturn.py) | Multi-turn conversation with `resilient_background=True, steerable_conversations=False` |

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
