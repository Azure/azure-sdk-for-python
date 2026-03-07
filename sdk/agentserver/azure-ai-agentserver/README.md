# Azure AI Agent Server client library for Python

A standalone, **protocol-agnostic agent server** package for Azure AI. Provides a
Starlette-based `AgentServer` base class with pluggable protocol heads, OpenAPI spec
serving, optional request validation, production middleware, optional tracing, and health
endpoints — with **zero framework coupling**.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver
```

**Requires Python >= 3.10.**

### Quick start

```python
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer


class GreetingAgent(AgentServer):
    async def invoke(self, request: Request) -> Response:
        data = await request.json()
        greeting = f"Hello, {data['name']}!"
        return JSONResponse({"greeting": greeting})


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

## Key concepts

`AgentServer` is a base class for building agent endpoints that plug into the
Azure Agent Service. It supports multiple protocol heads (`/invoke` today,
`/responses` and others in the future) through a pluggable handler architecture.

The Azure Agent Service expects specific route paths (`/invocations`, `/liveness`,
`/readiness`, etc.) for deployment. `AgentServer` wires these automatically so
your agent is compatible with the hosting platform — no manual route setup required.

**Key properties:**

- **Platform-compatible routes** — automatically registers the exact endpoints the Azure
  Agent Service expects, so your agent deploys without configuration changes.
- **Starlette + Hypercorn** — lightweight ASGI server with native HTTP/1.1 and HTTP/2
  support.
- **Raw protocol access** — subclass `AgentServer` and receive raw Starlette `Request`
  objects, return raw Starlette `Response` objects. Full control over content types,
  streaming, headers, SSE, and status codes.
- **Automatic invocation ID tracking** — every request gets a unique ID injected into
  `request.state` and the `x-agent-invocation-id` response header.
- **OpenAPI spec serving** — pass a spec and it is served at
  `GET /invocations/docs/openapi.json` for documentation / tooling.
- **Optional request validation** — opt in to validate incoming request bodies
  against the OpenAPI spec before reaching your code.
- **Request limits** — configurable invoke timeouts (504) and graceful shutdown — all via
  constructor args or environment variables.
- **Optional OpenTelemetry tracing** — opt-in span instrumentation that covers the full
  request lifecycle, including streaming responses.
- **Health endpoints** — `/liveness` and `/readiness` out of the box.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Azure Agent Service (Cloud Infrastructure)                          │
│  Protocols: /invoke, /responses, /mcp, /a2a, /activity              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
              ┌───────────────────────────────┐
              │ azure-ai-agentserver          │
              │ AgentServer                   │
              │                               │
              │ Protocol heads:               │
              │  • /invoke                    │
              │  • /responses (planned)       │
              │                               │
              │ OpenAPI spec serving         │
              │ Optional request validation  │
              │ Invocation ID tracking        │
              │ Invoke timeout / graceful     │
              │   shutdown                    │
              │ Optional OTel tracing         │
              │ Health & readiness endpoints  │
              └───────────────────────────────┘
                             │
                   Your integration code:
                   ┌─────────┼─────────┐
                   ▼         ▼         ▼
              LangGraph   Agent     Semantic
                        Framework    Kernel
```

**Single package, multiple protocol heads, no framework coupling.**

### Subclassing `AgentServer`

| Method | Required | Description |
|--------|----------|-------------|
| `invoke(request: Request) -> Response` | **Yes** | Process an invocation. Return any Starlette `Response`. |
| `get_invocation(request: Request) -> Response` | No | Retrieve a stored invocation result. Default returns 404. |
| `cancel_invocation(request: Request) -> Response` | No | Cancel a running invocation. Default returns 404. |
| `on_shutdown() -> None` | No | Called during graceful shutdown after in-flight requests drain. Use to flush buffers, close connections, or release resources. Default is a no-op. |

The invocation ID is available via `request.state.invocation_id` (auto-generated for
`invoke`, extracted from the URL path for `get_invocation` / `cancel_invocation`).
The server auto-injects the `x-agent-invocation-id` response header if not already set.

### Routes (Phase 1)

| Route | Method | Description |
|-------|--------|-------------|
| `/invocations` | POST | Create and process an invocation |
| `/invocations/{id}` | GET | Retrieve a previous invocation result |
| `/invocations/{id}/cancel` | POST | Cancel a running invocation |
| `/invocations/docs/openapi.json` | GET | Return the registered OpenAPI spec |
| `/liveness` | GET | Health check |
| `/readiness` | GET | Readiness check |

### Configuration

All settings follow the same resolution order: **constructor argument > environment
variable > default**. Set a value to `0` to disable the corresponding feature.

| Constructor param | Environment variable | Default | Description |
|---|---|---|---|
| `port` (on `run()`) | `AGENT_SERVER_PORT` | `8088` | Port to bind |
| `graceful_shutdown_timeout` | `AGENT_GRACEFUL_SHUTDOWN_TIMEOUT` | `30` (seconds) | Drain period after SIGTERM before forced exit |
| `request_timeout` | `AGENT_REQUEST_TIMEOUT` | `300` (seconds) | Max time for `invoke()` before 504 |
| `enable_tracing` | `AGENT_ENABLE_TRACING` | `false` | Enable OpenTelemetry tracing |
| `enable_request_validation` | `AGENT_ENABLE_REQUEST_VALIDATION` | `false` | Validate request bodies against `openapi_spec` |
| `log_level` | `AGENT_LOG_LEVEL` | `WARNING` | Library log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `debug_errors` | `AGENT_DEBUG_ERRORS` | `false` | Include exception details in error responses |

```python
agent = MyAgent(
    request_timeout=60,                       # 1 minute
    graceful_shutdown_timeout=15,             # 15 s drain
)
agent.run()
```

Or configure entirely via environment variables — no code changes needed for deployment
tuning.

## Examples

### OpenAPI spec & validation

Pass an OpenAPI spec to serve it at `/invocations/docs/openapi.json`.
Opt in to runtime request validation with `enable_request_validation=True`:

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

# Spec served for documentation; validation off (default)
agent = GreetingAgent(openapi_spec=spec)

# Spec served AND requests validated at runtime
agent = GreetingAgent(openapi_spec=spec, enable_request_validation=True)
agent.run()
```

- `GET /invocations/docs/openapi.json` serves the registered spec (or 404 if none).
- When validation is enabled, non-conforming **requests** return 400 with details.

### Tracing

Tracing is **disabled by default**. Enable it via constructor or environment variable:

```python
agent = MyAgent(enable_tracing=True)
```

or:

```bash
export AGENT_ENABLE_TRACING=true
```

Install the tracing extras (includes OpenTelemetry and the Azure Monitor exporter):

```bash
pip install azure-ai-agentserver[tracing]
```

When enabled, spans are created for `invoke`, `get_invocation`, and `cancel_invocation`
endpoints. For streaming responses, the span stays open until the last chunk is sent,
accurately capturing the full transfer duration. Errors during streaming are recorded on
the span. Incoming `traceparent` / `tracestate` headers are propagated via W3C
TraceContext.

#### Application Insights integration

When tracing is enabled **and** an Application Insights connection string is available,
traces and logs are automatically exported to Azure Monitor. The connection string is
resolved in the following order:

1. The `application_insights_connection_string` constructor parameter.
2. The `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable.

```python
# Explicit connection string
agent = MyAgent(
    enable_tracing=True,
    application_insights_connection_string="InstrumentationKey=...",
)

# Or via environment variable (connection string auto-discovered)
# export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
agent = MyAgent(enable_tracing=True)
```

If no connection string is found, tracing still works — spans are created but not exported
to Azure Monitor (you can bring your own `TracerProvider`).

### More samples

| Sample | Description |
|--------|-------------|
| `samples/simple_invoke_agent/` | Minimal from-scratch agent |
| `samples/openapi_validated_agent/` | OpenAPI spec with request/response validation |
| `samples/async_invoke_agent/` | Long-running tasks with get & cancel support |
| `samples/human_in_the_loop_agent/` | Synchronous human-in-the-loop interaction |
| `samples/langgraph_invoke_agent/` | Customer-managed LangGraph adapter |
| `samples/agentframework_invoke_agent/` | Customer-managed Agent Framework adapter |

## Troubleshooting

### Reporting issues

To report an issue with the client library, or request additional features, please open a
GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

Please visit [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver/samples)
for more usage examples.

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
