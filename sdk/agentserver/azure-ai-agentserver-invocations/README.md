# Azure AI Agent Server Invocations client library for Python

The `azure-ai-agentserver-invocations` package provides the invocation protocol endpoints for Azure AI Hosted Agent containers. It plugs into the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) host framework and supports two transports on the same host:

- **HTTP** (`invocations` protocol) — `POST /invocations`, `GET /invocations/{id}`, `POST /invocations/{id}/cancel`, `GET /invocations/docs/openapi.json`.
- **WebSocket** (`invocations_ws` protocol) — full-duplex streaming at `/invocations_ws`, registered with `@app.ws_handler`.

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
- `@app.ws_handler` — Optional. Handles WebSocket connections at `/invocations_ws`.

### Protocol endpoints

| Method | Route | Required | Description |
|---|---|---|---|
| `POST` | `/invocations` | Yes | Execute the agent |
| `GET` | `/invocations/{invocation_id}` | No | Retrieve invocation status or result |
| `POST` | `/invocations/{invocation_id}/cancel` | No | Cancel a running invocation |
| `GET` | `/invocations/docs/openapi.json` | No | Serve the agent's OpenAPI 3.x spec |
| `WS`   | `/invocations_ws` | No | Full-duplex WebSocket transport (`invocations_ws` protocol) |

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

## WebSocket protocol (`invocations_ws`)

The same `InvocationAgentServerHost` object also exposes a WebSocket transport at `/invocations_ws`. Container authors do not install or import a second package — registering an `@app.ws_handler` is the only step. A multi-protocol agent shares one host, one session, and one process.

### Quick start

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.websockets import WebSocket

app = InvocationAgentServerHost()


@app.invoke_handler                 # POST /invocations (HTTP)
async def invoke(request: Request) -> Response:
    payload = await request.json()
    return JSONResponse({"echo": payload})


@app.ws_handler                     # /invocations_ws (WebSocket)
async def ws(websocket: WebSocket) -> None:
    async for message in websocket.iter_text():
        await websocket.send_text(message)


app.run()
```

### What the SDK does for `@app.ws_handler`

- Registers `/invocations_ws` on the same Starlette host as `/invocations` and `/readiness`.
- Calls `await websocket.accept()` before invoking your handler.
- Runs WebSocket Ping/Pong keep-alive in the background — disabled by default; enable by setting the `WS_KEEPALIVE_INTERVAL` environment variable (auto-injected by AgentService into hosted-agent containers) or by passing `InvocationAgentServerHost(ws_ping_interval=...)`. Set the value to `0` (in any source) to disable. Frames are sent at the WebSocket protocol layer (RFC 6455 opcode `0x9`/`0xA`) by the underlying Hypercorn server, which keeps the connection alive across Azure APIM and Azure Load Balancer's ~4 minute idle timeout without any extra application traffic.
- Closes the connection cleanly on handler return (close code `1000`) or maps an uncaught handler exception to close code `1011`.
- Emits a structured close-event log line carrying `azure.ai.agentserver.invocations_ws.session_id`, `azure.ai.agentserver.invocations_ws.close_code`, and `azure.ai.agentserver.invocations_ws.duration_ms`. The same fields are recorded as OpenTelemetry span attributes so the connection lifetime is visible end-to-end.
- Inherits `/readiness`, OpenTelemetry export, graceful shutdown, and the `x-platform-server` identity header from `azure-ai-agentserver-core`.

### Handler signature

The handler receives a Starlette [`WebSocket`][starlette-ws] and returns `None`. The full WebSocket API — `iter_text`, `iter_bytes`, `iter_json`, `send_text`, `send_bytes`, `send_json`, `close`, `headers`, `query_params`, `client`, `state` — is available, so application protocols on top of `invocations_ws` are entirely under your control.

[starlette-ws]: https://www.starlette.io/websockets/

### Reference: configuration

| Constructor argument | Default | Description |
|---|---|---|
| `ws_ping_interval` | `0` (disabled) | WebSocket protocol Ping interval in seconds. `0` disables keep-alive. Negative or non-finite values are rejected. When `None`, the SDK reads the `WS_KEEPALIVE_INTERVAL` env var before falling back to disabled. |

| Environment variable | Default | Description |
|---|---|---|
| `WS_KEEPALIVE_INTERVAL` | unset (disabled) | Platform-injected override for the WebSocket Ping interval (seconds). `0` disables keep-alive. Ignored when `ws_ping_interval=` is set explicitly. |

### Reference: close codes

| Close code | Meaning |
|---|---|
| `1000` | Handler returned cleanly (normal close). |
| `1011` | Handler raised an unhandled exception (mapped by the SDK). |
| `4000`-`4999` | Application-defined codes (set by the handler via `await websocket.close(code=...)` — surfaced unchanged to the client). |

## Troubleshooting

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples) folder for complete working examples:

| Sample | Description |
|---|---|
| [simple_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/simple_invoke_agent/) | Minimal synchronous request-response |
| [async_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/async_invoke_agent/) | Long-running operations with polling and cancellation |
| [ws_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/ws_invoke_agent/) | Combined `POST /invocations` (HTTP) and `/invocations_ws` (WebSocket) host |
| [ws_bidirectional_streaming_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/ws_bidirectional_streaming_agent/) | Full-duplex `/invocations_ws` agent: concurrent token streams + mid-flight cancel (relies on the SDK's WS protocol Ping/Pong keep-alive, not application-level heartbeats) |

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
