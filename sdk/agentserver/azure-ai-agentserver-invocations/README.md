# Azure AI Agent Server Invocations client library for Python

The `azure-ai-agentserver-invocations` package provides the invocation protocol endpoints for Azure AI Hosted Agent containers. It plugs into the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) host framework and supports two transport modes:

- **HTTP** (`invocations` protocol) — `POST /invocations`, `GET /invocations/{id}`, `POST /invocations/{id}/cancel`, `GET /invocations/docs/openapi.json`
- **WebSocket** (`invocations_ws` protocol) — persistent WebSocket at `/invocations_ws/ws` with invoke, get, cancel, and streaming over a single connection

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-invocations
```

This automatically installs `azure-ai-agentserver-core` as a dependency.

### Prerequisites

- Python 3.10 or later

## Key concepts

### InvocationAgentServerHost

`InvocationAgentServerHost` is an `AgentServerHost` subclass that adds invocation protocol endpoints. It provides decorator methods for registering handler functions:

- `@app.invoke_handler` — **Required.** Handles `POST /invocations`.
- `@app.get_invocation_handler` — Optional. Handles `GET /invocations/{id}`.
- `@app.cancel_invocation_handler` — Optional. Handles `POST /invocations/{id}/cancel`.

### Protocol endpoints

| Method | Route | Required | Description |
|---|---|---|---|
| `POST` | `/invocations` | Yes | Execute the agent |
| `GET` | `/invocations/{invocation_id}` | No | Retrieve invocation status or result |
| `POST` | `/invocations/{invocation_id}/cancel` | No | Cancel a running invocation |
| `GET` | `/invocations/docs/openapi.json` | No | Serve the agent's OpenAPI 3.x spec |

### Request and response headers

The SDK automatically manages these headers on every invocation:

| Header | Direction | Description |
|---|---|---|
| `x-agent-invocation-id` | Request & Response | Echoed if provided, otherwise a UUID is generated |
| `x-agent-session-id` | Response (POST only) | Resolved from `agent_session_id` query param, `FOUNDRY_AGENT_SESSION_ID` env var, or generated UUID |

### Session ID resolution

Session IDs group related invocations into a conversation. The SDK resolves the session ID in order:

1. `agent_session_id` query parameter on `POST /invocations`
2. `FOUNDRY_AGENT_SESSION_ID` environment variable
3. Auto-generated UUID

The resolved session ID is available in handler functions via `request.state.session_id`.

### Handler access to SDK state

Inside handler functions, the SDK sets these attributes on `request.state`:

- `request.state.invocation_id` — The invocation ID (echoed or generated).
- `request.state.session_id` — The resolved session ID (POST /invocations only).

### Distributed tracing

When tracing is enabled on the `AgentServerHost`, invocation spans are automatically created with GenAI semantic conventions:

- **Span name**: `invoke_agent {FOUNDRY_AGENT_NAME}:{FOUNDRY_AGENT_VERSION}`
- **Span attributes**: `gen_ai.system`, `gen_ai.operation.name`, `gen_ai.response.id`, `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.version`, `microsoft.session.id`
- **Error tags**: `azure.ai.agentserver.invocations.error.code`, `.error.message`
- **Baggage keys**: `azure.ai.agentserver.invocation_id`, `.session_id`

## Examples

### Simple synchronous agent

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle(request: Request) -> Response:
    data = await request.json()
    return JSONResponse({"greeting": f"Hello, {data['name']}!"})

app.run()
```

### Long-running operations with polling

```python
import asyncio
import json

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_tasks: dict[str, asyncio.Task] = {}
_results: dict[str, bytes] = {}

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle(request: Request) -> Response:
    data = await request.json()
    invocation_id = request.state.invocation_id
    task = asyncio.create_task(do_work(invocation_id, data))
    _tasks[invocation_id] = task
    return JSONResponse({"invocation_id": invocation_id, "status": "running"})

@app.get_invocation_handler
async def get_invocation(request: Request) -> Response:
    invocation_id = request.state.invocation_id
    if invocation_id in _results:
        return Response(content=_results[invocation_id], media_type="application/json")
    return JSONResponse({"invocation_id": invocation_id, "status": "running"})

@app.cancel_invocation_handler
async def cancel_invocation(request: Request) -> Response:
    invocation_id = request.state.invocation_id
    if invocation_id in _tasks:
        _tasks[invocation_id].cancel()
        del _tasks[invocation_id]
        return JSONResponse({"invocation_id": invocation_id, "status": "cancelled"})
    return JSONResponse({"error": "not found"}, status_code=404)
```

### Streaming (Server-Sent Events)

```python
import json

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle(request: Request) -> Response:
    async def generate():
        for word in ["Hello", " ", "world", "!"]:
            yield json.dumps({"delta": word}).encode() + b"\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Multi-turn conversation

Use the `agent_session_id` query parameter to group invocations into a conversation:

```bash
# First turn
curl -X POST "http://localhost:8088/invocations?agent_session_id=session-abc" \
    -H "Content-Type: application/json" \
    -d '{"message": "My name is Alice"}'

# Second turn (same session)
curl -X POST "http://localhost:8088/invocations?agent_session_id=session-abc" \
    -H "Content-Type: application/json" \
    -d '{"message": "What is my name?"}'
```

The session ID is available in the handler via `request.state.session_id`.

### Serving an OpenAPI spec

Pass an OpenAPI spec dict to enable the discovery endpoint at `GET /invocations/docs/openapi.json`:

```python
app = InvocationAgentServerHost(openapi_spec={
    "openapi": "3.0.3",
    "info": {"title": "My Agent", "version": "1.0.0"},
    "paths": { ... },
})
```

---

## WebSocket Protocol (`invocations_ws`)

The package also ships an alternative transport that runs the same invocation lifecycle over a single persistent **WebSocket** long connection. Use this when you want lower latency for streaming, full-duplex agent interactions, or to avoid HTTP request overhead per turn.

### InvocationWSAgentServerHost

`InvocationWSAgentServerHost` is an `AgentServerHost` subclass that adds a WebSocket endpoint for the `invocations_ws` protocol. It exposes decorator methods for registering handler functions:

- `@app.ws_invoke_handler` — **Required.** Handles `invoke` actions. Supports both async functions (non-streaming) and async generators (streaming).
- `@app.ws_get_invocation_handler` — Optional. Handles `get_invocation` actions.
- `@app.ws_cancel_invocation_handler` — Optional. Handles `cancel_invocation` actions.

### InvocationWSContext

WebSocket handler functions receive an `InvocationWSContext` object containing:

- `context.invocation_id` — The invocation ID (echoed from client or auto-generated UUID).
- `context.session_id` — The resolved session ID.

### InvocationWSError

Handlers can raise `InvocationWSError(code, message)` to return a domain-specific error to the client without exposing internal details.

### WebSocket endpoint

All operations use a single persistent WebSocket connection:

| Route | Description |
|---|---|
| `ws://host:port/invocations_ws/ws` | WebSocket endpoint for all `invocations_ws` operations |
| `GET /invocations_ws/docs/openapi.json` | Serve the agent's OpenAPI 3.x spec (HTTP) |
| `GET /readiness` | Health check (HTTP) |

### Client → Server messages

All messages are JSON text frames with an `action` field:

```json
{"action": "invoke", "payload": {...}, "invocation_id": "optional", "session_id": "optional"}
{"action": "get_invocation", "invocation_id": "required"}
{"action": "cancel_invocation", "invocation_id": "required"}
{"action": "ping"}
{"action": "pong"}
```

### Server → Client messages

```json
{"type": "result", "invocation_id": "...", "session_id": "...", "payload": {...}}
{"type": "stream_chunk", "invocation_id": "...", "session_id": "...", "payload": {...}}
{"type": "stream_end", "invocation_id": "...", "session_id": "..."}
{"type": "error", "invocation_id": "...", "error": {"code": "...", "message": "..."}}
{"type": "ping"}
{"type": "pong"}
```

### WebSocket keep-alive (ping/pong)

Azure APIM and Azure Load Balancer silently drop idle WebSocket connections after approximately 4 minutes. To prevent this, the server sends periodic `{"type": "ping"}` messages to each connected client.

- **Default interval**: 30 seconds.
- **Disable**: `ws_ping_interval=0`.
- **Custom**: any positive integer, e.g. `ws_ping_interval=15`.

```python
app = InvocationWSAgentServerHost(ws_ping_interval=20)  # ping every 20 seconds
```

Clients should respond with `{"action": "pong"}` when they receive a `{"type": "ping"}` message. Clients may also send `{"action": "ping"}` at any time; the server replies with `{"type": "pong"}`.

### Session ID resolution (WebSocket)

Session IDs group related invocations. Resolution order:

1. `session_id` field in the WebSocket message
2. `FOUNDRY_AGENT_SESSION_ID` environment variable
3. Auto-generated UUID

### Distributed tracing (WebSocket)

When tracing is enabled on the `AgentServerHost`, `invocations_ws` spans are automatically created with GenAI semantic conventions:

- **Span name**: `invoke_agent {FOUNDRY_AGENT_NAME}:{FOUNDRY_AGENT_VERSION}`
- **Span attributes**: `gen_ai.system`, `gen_ai.operation.name`, `gen_ai.response.id`, `gen_ai.conversation.id`, `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.version`
- **Error tags**: `azure.ai.agentserver.invocations_ws.error.code`, `.error.message`

### WebSocket examples

#### Simple agent

```python
from azure.ai.agentserver.invocations import InvocationWSAgentServerHost, InvocationWSContext

app = InvocationWSAgentServerHost()


@app.ws_invoke_handler
async def handle(payload: dict, context: InvocationWSContext) -> dict:
    return {"greeting": f"Hello, {payload['name']}!"}

app.run()
```

**Client** (using the `websockets` library):

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/invocations_ws/ws") as ws:
        await ws.send(json.dumps({
            "action": "invoke",
            "payload": {"name": "Alice"}
        }))
        while True:
            msg = json.loads(await ws.recv())
            if msg["type"] == "ping":
                await ws.send(json.dumps({"action": "pong"}))
            elif msg["type"] == "result":
                print(msg["payload"]["greeting"])  # Hello, Alice!
                break

asyncio.run(main())
```

#### Long-running operations with get/cancel

```python
import asyncio

from azure.ai.agentserver.invocations import (
    InvocationWSAgentServerHost,
    InvocationWSContext,
    InvocationWSError,
)

_tasks: dict[str, asyncio.Task] = {}
_results: dict[str, dict] = {}

app = InvocationWSAgentServerHost()


@app.ws_invoke_handler
async def handle(payload: dict, context: InvocationWSContext) -> dict:
    task = asyncio.create_task(do_work(context.invocation_id, payload))
    _tasks[context.invocation_id] = task
    return {"invocation_id": context.invocation_id, "status": "running"}


@app.ws_get_invocation_handler
async def get_invocation(context: InvocationWSContext) -> dict:
    if context.invocation_id in _results:
        return _results[context.invocation_id]
    if context.invocation_id in _tasks:
        return {"invocation_id": context.invocation_id, "status": "running"}
    raise InvocationWSError("not_found", "Invocation not found")


@app.ws_cancel_invocation_handler
async def cancel_invocation(context: InvocationWSContext) -> dict:
    if context.invocation_id in _tasks:
        _tasks[context.invocation_id].cancel()
        del _tasks[context.invocation_id]
        return {"invocation_id": context.invocation_id, "status": "cancelled"}
    raise InvocationWSError("not_found", "Invocation not found")
```

#### Streaming

Use an async generator to stream chunks back to the client. Each yielded dict is sent as a `stream_chunk` message, followed by a `stream_end` when the generator completes.

```python
from azure.ai.agentserver.invocations import InvocationWSAgentServerHost, InvocationWSContext

app = InvocationWSAgentServerHost()


@app.ws_invoke_handler
async def handle(payload: dict, context: InvocationWSContext):
    for word in ["Hello", " ", "world", "!"]:
        yield {"delta": word}
```

#### Multi-turn conversation

Use the `session_id` field to group invocations over the same WebSocket connection:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/invocations_ws/ws") as ws:
        # First turn
        await ws.send(json.dumps({
            "action": "invoke",
            "session_id": "session-abc",
            "payload": {"message": "My name is Alice"},
        }))
        print(json.loads(await ws.recv()))

        # Second turn (same session, same connection)
        await ws.send(json.dumps({
            "action": "invoke",
            "session_id": "session-abc",
            "payload": {"message": "What is my name?"},
        }))
        print(json.loads(await ws.recv()))

asyncio.run(main())
```

#### Combined HTTP + WebSocket host

Use cooperative multiple inheritance to serve both `invocations` (HTTP) and `invocations_ws` (WebSocket) protocols on the same server:

```python
from azure.ai.agentserver.invocations import (
    InvocationAgentServerHost,
    InvocationWSAgentServerHost,
    InvocationWSContext,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class MyAgentHost(InvocationWSAgentServerHost, InvocationAgentServerHost):
    pass


app = MyAgentHost()


@app.invoke_handler  # HTTP — POST /invocations
async def handle_http(request: Request) -> Response:
    data = await request.json()
    return JSONResponse({"greeting": f"Hello, {data['name']}!"})


@app.ws_invoke_handler  # WebSocket — /invocations_ws/ws
async def handle_ws(payload: dict, context: InvocationWSContext) -> dict:
    return {"greeting": f"Hello, {payload['name']}!"}

app.run()
```

## Troubleshooting

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples) folder for complete working examples:

| Sample | Description |
|---|---|
| [simple_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/simple_invoke_agent/) | Minimal synchronous request-response (HTTP) |
| [async_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/async_invoke_agent/) | Long-running operations with polling and cancellation (HTTP) |
| [streaming_ws_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/streaming_ws_invoke_agent/) | Streaming token-by-token echo over both WebSocket and HTTP (SSE) |

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
