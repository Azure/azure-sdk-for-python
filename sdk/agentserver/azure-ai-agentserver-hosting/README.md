# Azure AI AgentServer Hosting for Python

The `azure-ai-agentserver-hosting` package provides the foundation host framework for building Azure AI Hosted Agent containers. It handles the protocol-agnostic infrastructure — health probes, graceful shutdown, OpenTelemetry tracing, and ASGI serving — so that protocol packages can focus on their endpoint logic.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-hosting
```

To enable OpenTelemetry tracing with Azure Monitor and OTLP exporters:

```bash
pip install azure-ai-agentserver-hosting[tracing]
```

### Prerequisites

- Python 3.10 or later

## Key concepts

### AgentServer

`AgentServer` is the host process for Azure AI Hosted Agent containers. It provides:

- **Health probe** — `GET /healthy` returns `200 OK` when the server is ready.
- **Graceful shutdown** — On `SIGTERM` the server drains in-flight requests (default 30 s timeout) before exiting.
- **OpenTelemetry tracing** — Automatic span creation with Azure Monitor and OTLP export when configured.
- **Hypercorn ASGI server** — Serves on `0.0.0.0:${PORT:-8088}` with HTTP/1.1.

Protocol packages (e.g. `azure-ai-agentserver-invocations`) plug into `AgentServer` by calling `register_routes()` to add their endpoints.

### Environment variables

| Variable | Description | Default |
|---|---|---|
| `PORT` | Listen port | `8088` |
| `FOUNDRY_AGENT_NAME` | Agent name (used in tracing) | `""` |
| `FOUNDRY_AGENT_VERSION` | Agent version (used in tracing) | `""` |
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint | `""` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Azure Monitor connection string | — |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | — |
| `AGENT_GRACEFUL_SHUTDOWN_TIMEOUT` | Shutdown drain timeout (seconds) | `30` |
| `AGENT_LOG_LEVEL` | Log level (`DEBUG`, `INFO`, etc.) | `INFO` |

## Examples

`AgentServer` is typically used with a protocol package. The simplest setup with the invocations protocol:

```python
from azure.ai.agentserver.hosting import AgentServer
from azure.ai.agentserver.invocations import InvocationHandler
from starlette.responses import JSONResponse

server = AgentServer()
invocations = InvocationHandler(server)

@invocations.invoke_handler
async def handle(request):
    body = await request.json()
    return JSONResponse({"greeting": f"Hello, {body['name']}!"})

server.run()
```

### Using AgentServer standalone

For custom protocol implementations, use `AgentServer` directly and register your own routes:

```python
from azure.ai.agentserver.hosting import AgentServer
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

async def my_endpoint(request: Request):
    return JSONResponse({"status": "ok"})

server = AgentServer()
server.register_routes([Route("/my-endpoint", my_endpoint, methods=["POST"])])
server.run()
```

### Shutdown handler

Register a cleanup function that runs during graceful shutdown:

```python
server = AgentServer()

@server.shutdown_handler
async def on_shutdown():
    # Close database connections, flush buffers, etc.
    pass
```

### Configuring tracing

Tracing is enabled automatically when an Application Insights connection string is available:

```python
server = AgentServer(
    application_insights_connection_string="InstrumentationKey=...",
)
```

Or via environment variable:

```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
python my_agent.py
```

## Troubleshooting

### Logging

Set the log level to `DEBUG` for detailed diagnostics:

```python
server = AgentServer(log_level="DEBUG")
```

Or via environment variable:

```bash
export AGENT_LOG_LEVEL=DEBUG
```

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

- Install [`azure-ai-agentserver-invocations`](https://pypi.org/project/azure-ai-agentserver-invocations/) to add the invocation protocol endpoints.
- See the [container image spec](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver) for the full hosted agent contract.

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
