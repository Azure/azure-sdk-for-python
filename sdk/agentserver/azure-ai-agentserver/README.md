# azure-ai-agentserver

A **protocol-agnostic agent server** package for Azure AI. Provides a Starlette-based
`AgentServer` base class with pluggable protocol heads. Phase 1 ships with the `/invoke`
protocol head; future phases will add `/responses` and other protocols.

## Features

- **Generic `AgentServer` base class** — subclass and implement `invoke()` to serve any agent.
- **`/invoke` protocol** — four operations: `POST /invocations`, `GET /invocations/{id}`,
  `POST /invocations/{id}/cancel`, `GET /invocations/docs/openapi.json`.
- **OpenAPI validation** — register a spec to validate request/response bodies at runtime.
- **Streaming support** — return `bytes` for non-streaming or an `AsyncGenerator[bytes, None]` for streaming.
- **Health endpoints** — `/liveness` and `/readiness` out of the box.
- **No framework coupling** — LangGraph, Agent Framework, Semantic Kernel, etc. are integrated
  via customer-managed adapter code (see samples).

## Installation

```bash
pip install azure-ai-agentserver
```

## Quick Start

```python
import json
from azure.ai.agentserver import AgentServer, InvokeRequest


class GreetingAgent(AgentServer):
    async def invoke(self, request: InvokeRequest) -> bytes:
        data = json.loads(request.body)
        greeting = f"Hello, {data['name']}!"
        return json.dumps({"greeting": greeting}).encode()


if __name__ == "__main__":
    GreetingAgent().run()
```

```bash
# Start the agent
python my_agent.py

# Call it
curl -X POST http://localhost:8088/invocations \
  -H "Content-Type: application/json" \
  -d '{"name": "World"}'
# → {"greeting": "Hello, World!"}
```

## Subclassing `AgentServer`

| Method | Required | Description |
|--------|----------|-------------|
| `invoke(request)` | **Yes** | Process an invocation. Return `bytes` or `AsyncGenerator[bytes, None]`. |
| `get_invocation(invocation_id)` | No | Retrieve a stored invocation result. Default returns 404. |
| `cancel_invocation(invocation_id, ...)` | No | Cancel a running invocation. Default returns 404. |

## OpenAPI Validation

```python
spec = {
    "openapi": "3.0.0",
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                                "required": ["name"],
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"greeting": {"type": "string"}},
                                }
                            }
                        }
                    }
                },
            }
        }
    },
}

agent = GreetingAgent(openapi_spec=spec)
agent.run()
```

Non-conforming requests will return 400. Non-conforming responses log warnings but are not blocked.

## Samples

- `samples/simple_invoke_agent/` — Minimal from-scratch agent
- `samples/langgraph_invoke_agent/` — Customer-managed LangGraph adapter
- `samples/agentframework_invoke_agent/` — Customer-managed Agent Framework adapter
- `samples/async_invoke_agent/` — Long-running tasks with get & cancel support

## License

MIT
