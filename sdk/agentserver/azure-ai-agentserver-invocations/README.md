# Azure AI Agent Server Invocations client library for Python

The `azure-ai-agentserver-invocations` package provides the invocation protocol endpoints for Azure AI Hosted Agent containers. It plugs into the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) host framework and adds the full invocation lifecycle: `POST /invocations`, `GET /invocations/{id}`, `POST /invocations/{id}/cancel`, and `GET /invocations/docs/openapi.json`.

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

## Troubleshooting

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Visit the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples) folder for complete working examples:

| Sample | Description |
|---|---|
| [simple_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/simple_invoke_agent/) | Minimal synchronous request-response |
| [async_invoke_agent](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/async_invoke_agent/) | Long-running operations with polling and cancellation |

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
