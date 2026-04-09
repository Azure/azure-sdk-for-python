# Azure AI AgentServerHost Invocations for Python (WebSocket)

The `azure-ai-agentserver-invocations` package provides the invocation protocol over **WebSocket long connections** for Azure AI Hosted Agent containers. It plugs into the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) host framework and exposes a single WebSocket endpoint at `/invocations/ws` that supports invoke, get, cancel, and streaming operations.

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

`InvocationAgentServerHost` is an `AgentServerHost` subclass that adds a WebSocket endpoint for the invocation protocol. It provides decorator methods for registering handler functions:

- `@app.invoke_handler` — **Required.** Handles `invoke` actions. Supports both async functions (non-streaming) and async generators (streaming).
- `@app.get_invocation_handler` — Optional. Handles `get_invocation` actions.
- `@app.cancel_invocation_handler` — Optional. Handles `cancel_invocation` actions.

### InvocationContext

Handler functions receive an `InvocationContext` object containing:

- `context.invocation_id` — The invocation ID (echoed from client or auto-generated UUID).
- `context.session_id` — The resolved session ID.

### InvocationError

Handlers can raise `InvocationError(code, message)` to return a domain-specific error to the client without exposing internal details.

### WebSocket endpoint

All invocation operations use a single persistent WebSocket connection:

| Route | Description |
|---|---|
| `ws://host:port/invocations/ws` | WebSocket endpoint for all invocation operations |
| `GET /invocations/docs/openapi.json` | Serve the agent's OpenAPI 3.x spec (HTTP) |
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

Azure APIM and Azure Load Balancer silently drop idle WebSocket connections after approximately 4 minutes, even though the backend supports 60-minute connections. To prevent this, the server sends periodic `{"type": "ping"}` messages to each connected client.

- **Default interval**: 30 seconds (well within the ~4-minute idle timeout).
- **Disable**: Pass `ws_ping_interval=0` to `InvocationAgentServerHost()`.
- **Custom interval**: Pass any positive integer, e.g. `ws_ping_interval=15`.

Clients should respond with `{"action": "pong"}` when they receive a `{"type": "ping"}` message. Clients may also send `{"action": "ping"}` at any time; the server replies with `{"type": "pong"}`.

```python
app = InvocationAgentServerHost(ws_ping_interval=20)  # ping every 20 seconds
```

### Session ID resolution

Session IDs group related invocations into a conversation. The SDK resolves the session ID in order:

1. `session_id` field in the WebSocket message
2. `FOUNDRY_AGENT_SESSION_ID` environment variable
3. Auto-generated UUID

### Distributed tracing

When tracing is enabled on the `AgentServerHost`, invocation spans are automatically created with GenAI semantic conventions:

- **Span name**: `invoke_agent {FOUNDRY_AGENT_NAME}:{FOUNDRY_AGENT_VERSION}`
- **Span attributes**: `gen_ai.system`, `gen_ai.operation.name`, `gen_ai.response.id`, `gen_ai.conversation.id`, `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.version`
- **Error tags**: `azure.ai.agentserver.invocations.error.code`, `.error.message`

## Examples

### Simple agent

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost, InvocationContext

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle(payload: dict, context: InvocationContext) -> dict:
    return {"greeting": f"Hello, {payload['name']}!"}

app.run()
```

**Client** (using the `websockets` library):

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/invocations/ws") as ws:
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

from azure.ai.agentserver.invocations import (
    InvocationAgentServerHost,
    InvocationContext,
    InvocationError,
)

_tasks: dict[str, asyncio.Task] = {}
_results: dict[str, dict] = {}

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle(payload: dict, context: InvocationContext) -> dict:
    task = asyncio.create_task(do_work(context.invocation_id, payload))
    _tasks[context.invocation_id] = task
    return {"invocation_id": context.invocation_id, "status": "running"}


@app.get_invocation_handler
async def get_invocation(context: InvocationContext) -> dict:
    if context.invocation_id in _results:
        return _results[context.invocation_id]
    if context.invocation_id in _tasks:
        return {"invocation_id": context.invocation_id, "status": "running"}
    raise InvocationError("not_found", "Invocation not found")


@app.cancel_invocation_handler
async def cancel_invocation(context: InvocationContext) -> dict:
    if context.invocation_id in _tasks:
        _tasks[context.invocation_id].cancel()
        del _tasks[context.invocation_id]
        return {"invocation_id": context.invocation_id, "status": "cancelled"}
    raise InvocationError("not_found", "Invocation not found")
```

### Streaming

Use an async generator to stream chunks back to the client. Each yielded dict is sent as a `stream_chunk` message, followed by a `stream_end` when the generator completes.

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost, InvocationContext

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle(payload: dict, context: InvocationContext):
    for word in ["Hello", " ", "world", "!"]:
        yield {"delta": word}
```

**Client**:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/invocations/ws") as ws:
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

Use the `session_id` field to group invocations into a conversation over the same WebSocket connection:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/invocations/ws") as ws:
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

Pass an OpenAPI spec dict to enable the discovery endpoint at `GET /invocations/docs/openapi.json`:

```python
app = InvocationAgentServerHost(openapi_spec={
    "openapi": "3.0.3",
    "info": {"title": "My Agent", "version": "1.0.0"},
    "paths": { ... },
})
```

## Troubleshooting

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples) folder for complete working examples:

| Sample | Description |
|---|---|
| [streaming_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/streaming_invoke_agent/) | Streaming code-generation tokens via WebSocket |

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
