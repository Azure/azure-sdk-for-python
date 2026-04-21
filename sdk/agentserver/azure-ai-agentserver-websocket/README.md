# Azure AI AgentServerHost Websocket for Python (WebSocket)

The `azure-ai-agentserver-websocket` package provides the websocket protocol over **WebSocket long connections** for Azure AI Hosted Agent containers. It plugs into the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) host framework and exposes a single WebSocket endpoint at `/websocket/ws` that supports invoke, get, cancel, and streaming operations.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-websocket
```

This automatically installs `azure-ai-agentserver-core` as a dependency.

### Prerequisites

- Python 3.10 or later

## Key concepts

### WebsocketAgentServerHost

`WebsocketAgentServerHost` is an `AgentServerHost` subclass that adds a WebSocket endpoint for the websocket protocol. It provides decorator methods for registering handler functions:

- `@app.invoke_handler` — **Required.** Handles `invoke` actions. Supports both async functions (non-streaming) and async generators (streaming).
- `@app.get_websocket_handler` — Optional. Handles `get_websocket` actions.
- `@app.cancel_websocket_handler` — Optional. Handles `cancel_websocket` actions.

### WebsocketContext

Handler functions receive an `WebsocketContext` object containing:

- `context.websocket_id` — The websocket ID (echoed from client or auto-generated UUID).
- `context.session_id` — The resolved session ID.

### WebsocketError

Handlers can raise `WebsocketError(code, message)` to return a domain-specific error to the client without exposing internal details.

### WebSocket endpoint

All websocket operations use a single persistent WebSocket connection:

| Route | Description |
|---|---|
| `ws://host:port/websocket/ws` | WebSocket endpoint for all websocket operations |
| `GET /websocket/docs/openapi.json` | Serve the agent's OpenAPI 3.x spec (HTTP) |
| `GET /readiness` | Health check (HTTP) |

### Client → Server messages

All messages are JSON text frames with an `action` field:

```json
{"action": "invoke", "payload": {...}, "websocket_id": "optional", "session_id": "optional"}
{"action": "get_websocket", "websocket_id": "required"}
{"action": "cancel_websocket", "websocket_id": "required"}
{"action": "ping"}
{"action": "pong"}
```

### Server → Client messages

```json
{"type": "result", "websocket_id": "...", "session_id": "...", "payload": {...}}
{"type": "stream_chunk", "websocket_id": "...", "session_id": "...", "payload": {...}}
{"type": "stream_end", "websocket_id": "...", "session_id": "..."}
{"type": "error", "websocket_id": "...", "error": {"code": "...", "message": "..."}}
{"type": "ping"}
{"type": "pong"}
```

### WebSocket keep-alive (ping/pong)

Azure APIM and Azure Load Balancer silently drop idle WebSocket connections after approximately 4 minutes, even though the backend supports 60-minute connections. To prevent this, the server sends periodic `{"type": "ping"}` messages to each connected client.

- **Default interval**: 30 seconds (well within the ~4-minute idle timeout).
- **Disable**: Pass `ws_ping_interval=0` to `WebsocketAgentServerHost()`.
- **Custom interval**: Pass any positive integer, e.g. `ws_ping_interval=15`.

Clients should respond with `{"action": "pong"}` when they receive a `{"type": "ping"}` message. Clients may also send `{"action": "ping"}` at any time; the server replies with `{"type": "pong"}`.

```python
app = WebsocketAgentServerHost(ws_ping_interval=20)  # ping every 20 seconds
```

### Session ID resolution

Session IDs group related websocket sessions. The SDK resolves the session ID in order:

1. `session_id` field in the WebSocket message
2. `FOUNDRY_AGENT_SESSION_ID` environment variable
3. Auto-generated UUID

### Distributed tracing

When tracing is enabled on the `AgentServerHost`, websocket spans are automatically created with GenAI semantic conventions:

- **Span name**: `invoke_agent {FOUNDRY_AGENT_NAME}:{FOUNDRY_AGENT_VERSION}`
- **Span attributes**: `gen_ai.system`, `gen_ai.operation.name`, `gen_ai.response.id`, `gen_ai.conversation.id`, `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.version`
- **Error tags**: `azure.ai.agentserver.websocket.error.code`, `.error.message`

## Examples

### Simple agent

```python
from azure.ai.agentserver.websocket import WebsocketAgentServerHost, WebsocketContext

app = WebsocketAgentServerHost()


@app.invoke_handler
async def handle(payload: dict, context: WebsocketContext) -> dict:
    return {"greeting": f"Hello, {payload['name']}!"}

app.run()
```

**Client** (using the `websockets` library):

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/websocket/ws") as ws:
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

### Long-running operations with get/cancel

```python
import asyncio

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
    WebsocketError,
)

_tasks: dict[str, asyncio.Task] = {}
_results: dict[str, dict] = {}

app = WebsocketAgentServerHost()


@app.invoke_handler
async def handle(payload: dict, context: WebsocketContext) -> dict:
    task = asyncio.create_task(do_work(context.websocket_id, payload))
    _tasks[context.websocket_id] = task
    return {"websocket_id": context.websocket_id, "status": "running"}


@app.get_websocket_handler
async def get_websocket(context: WebsocketContext) -> dict:
    if context.websocket_id in _results:
        return _results[context.websocket_id]
    if context.websocket_id in _tasks:
        return {"websocket_id": context.websocket_id, "status": "running"}
    raise WebsocketError("not_found", "Websocket not found")


@app.cancel_websocket_handler
async def cancel_websocket(context: WebsocketContext) -> dict:
    if context.websocket_id in _tasks:
        _tasks[context.websocket_id].cancel()
        del _tasks[context.websocket_id]
        return {"websocket_id": context.websocket_id, "status": "cancelled"}
    raise WebsocketError("not_found", "Websocket not found")
```

### Streaming

Use an async generator to stream chunks back to the client. Each yielded dict is sent as a `stream_chunk` message, followed by a `stream_end` when the generator completes.

```python
from azure.ai.agentserver.websocket import WebsocketAgentServerHost, WebsocketContext

app = WebsocketAgentServerHost()


@app.invoke_handler
async def handle(payload: dict, context: WebsocketContext):
    for word in ["Hello", " ", "world", "!"]:
        yield {"delta": word}
```

**Client**:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/websocket/ws") as ws:
        await ws.send(json.dumps({"action": "invoke", "payload": {}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg["type"] == "stream_chunk":
                print(msg["payload"]["delta"], end="", flush=True)
            elif msg["type"] == "stream_end":
                print("\nDone!")
                break
            elif msg["type"] == "ping":
                await ws.send(json.dumps({"action": "pong"}))

asyncio.run(main())
```

### Multi-turn conversation

Use the `session_id` field to group websocket sessions over the same WebSocket connection:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/websocket/ws") as ws:
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

### Serving an OpenAPI spec

Pass an OpenAPI spec dict to enable the discovery endpoint at `GET /websocket/docs/openapi.json`:

```python
app = WebsocketAgentServerHost(openapi_spec={
    "openapi": "3.0.3",
    "info": {"title": "My Agent", "version": "1.0.0"},
    "paths": { ... },
})
```

## Troubleshooting

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-websocket/samples) folder for complete working examples:

| Sample | Description |
|---|---|
| [streaming_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-websocket/samples/streaming_invoke_agent/) | Streaming code-generation tokens via WebSocket |

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
