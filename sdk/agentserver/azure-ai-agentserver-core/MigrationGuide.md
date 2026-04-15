# Guide for migrating to the new azure-ai-agentserver package architecture

This guide helps you migrate from `azure-ai-agentserver-core` 1.x to the new three-package
architecture introduced in `azure-ai-agentserver-core` 2.0.0b1.

## Table of contents

- [Migration benefits](#migration-benefits)
- [Package changes](#package-changes)
- [API changes](#api-changes)
  - [Handler registration](#handler-registration)
  - [Streaming handler](#streaming-handler)
  - [Server startup](#server-startup)
  - [Tracing](#tracing)
  - [Logging](#logging)
  - [Error responses](#error-responses)
- [Import changes](#import-changes)
- [Multi-protocol composition](#multi-protocol-composition)
- [Additional information](#additional-information)

## Migration benefits

The new package architecture provides:

- **Separation of concerns** — protocol implementations (Responses API, Invocations) are in
  dedicated packages rather than bundled into a monolithic Core package.
- **Dramatically simpler API** — the old approach required manually constructing SSE events,
  tracking sequence numbers, and building response objects. The new API provides decorator-based
  handler registration with builder methods that handle all of this automatically.
- **Type-safe event builders** — `ResponseEventStream` and its convenience generators manage
  event sequencing, output indices, and content indices. You cannot accidentally emit events in
  the wrong order.
- **Built-in convenience methods** — common patterns like "emit a text message" or "stream
  tokens" are one-liners via `ResponseEventStream` generators or `TextResponse`.
- **Zero-config startup** — `app.run()` replaces manual server configuration with sensible
  defaults including OpenTelemetry, health endpoints, and user-agent headers.
- **Multi-protocol support** — a single server can host both Responses and Invocations endpoints
  via cooperative mixin inheritance.

## Package changes

| Before | After | Notes |
|--------|-------|-------|
| `azure-ai-agentserver-core` 1.x | `azure-ai-agentserver-core` 2.x | Stripped to hosting foundation only |
| _(bundled in core)_ | `azure-ai-agentserver-responses` 1.x | New — Responses API protocol |
| _(bundled in core)_ | `azure-ai-agentserver-invocations` 1.x | New — Invocations protocol |

Update your dependencies:

```bash
# Install the protocol package you need (transitively brings in core 2.x)
pip install azure-ai-agentserver-responses

# If you also need the Invocations protocol:
pip install azure-ai-agentserver-invocations
```

> **Note:** Both `azure-ai-agentserver-responses` and `azure-ai-agentserver-invocations`
> depend on `azure-ai-agentserver-core`, so you do not need to install Core separately.

## API changes

### Handler registration

**Before (1.x):**

```python
from azure.ai.agentserver.core import FoundryCBAgent, AgentRunContext

class MyAgent(FoundryCBAgent):
    def register_routes(self):
        self.app.add_route("/responses", self.handle_create, methods=["POST"])

    async def handle_create(self, request):
        # Manually parse request, build SSE events, track sequence numbers
        ...
```

**After (2.x) — Responses protocol:**

```python
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

app = ResponsesAgentServerHost()

@app.response_handler
async def handle_create(request: CreateResponse, context: ResponseContext, cancellation_signal):
    input_text = await context.get_input_text()
    return TextResponse(context, request, text=f"Echo: {input_text}")

app.run()
```

**After (2.x) — Invocations protocol:**

```python
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from azure.ai.agentserver.invocations import InvocationAgentServerHost

app = InvocationAgentServerHost()

@app.invoke_handler
async def handle(request: Request) -> Response:
    data = await request.json()
    return JSONResponse({"greeting": f"Hello, {data['name']}!"})

app.run()
```

### Streaming handler

**Before (1.x):**

```python
# Manually construct every SSE event, track sequence numbers and indices
seq = 0
yield {"type": "response.created", "sequence_number": seq, "response": {...}}
seq += 1
yield {"type": "response.output_item.added", "sequence_number": seq, ...}
seq += 1
# ... many more events with manual index tracking
```

**After (2.x):**

```python
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)

app = ResponsesAgentServerHost()

@app.response_handler
async def handle_create(request: CreateResponse, context: ResponseContext, cancellation_signal):
    stream = ResponseEventStream(context, request)
    stream.emit_created()

    # All inner events (output_item.added, content_part.added, deltas, done events)
    # are emitted automatically with correct sequence numbers and indices
    async for token in get_tokens():
        yield from stream.output_item_message(token)

    stream.emit_completed()
```

Or, for the simplest case:

```python
return TextResponse(context, request, text="Hello!")
```

### Server startup

**Before (1.x):**

```python
agent = MyAgent()
agent.run()  # or manual uvicorn/hypercorn setup
```

**After (2.x):**

```python
# Responses protocol
app = ResponsesAgentServerHost()

@app.response_handler
async def handle(request, context, cancellation_signal):
    ...

app.run()  # Built-in Hypercorn server with OpenTelemetry, health endpoint, graceful shutdown
```

Configuration is via constructor parameters:

```python
app = ResponsesAgentServerHost(
    log_level="DEBUG",                                      # Console log level
    graceful_shutdown_timeout=60,                           # Drain period in seconds
    applicationinsights_connection_string="InstrumentationKey=...",  # Azure Monitor
    configure_observability=None,                           # Disable SDK logging/tracing setup
)
```

## Import changes

| Before (1.x) | After (2.x) |
|---------------|-------------|
| `from azure.ai.agentserver.core import FoundryCBAgent` | `from azure.ai.agentserver.core import AgentServerHost` |
| `from azure.ai.agentserver.core import AgentRunContext` | `from azure.ai.agentserver.responses import ResponseContext` |
| _(n/a)_ | `from azure.ai.agentserver.responses import ResponsesAgentServerHost` |
| _(n/a)_ | `from azure.ai.agentserver.responses import TextResponse` |
| _(n/a)_ | `from azure.ai.agentserver.responses import ResponseEventStream` |
| _(n/a)_ | `from azure.ai.agentserver.invocations import InvocationAgentServerHost` |

## Multi-protocol composition

A single server can host both Responses and Invocations endpoints using cooperative
mixin inheritance:

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.responses import ResponsesAgentServerHost

class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
    pass

app = MyHost()

@app.response_handler
async def handle_responses(request, context, cancellation_signal):
    return TextResponse(context, request, text="Hello from Responses!")

@app.invoke_handler
async def handle_invocations(request):
    return JSONResponse({"hello": "from Invocations!"})

app.run()
# Serves both POST /responses and POST /invocations
```

## Additional information

- [azure-ai-agentserver-core README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/README.md)
- [azure-ai-agentserver-responses README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/README.md)
- [azure-ai-agentserver-invocations README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-invocations/README.md)
- [Responses samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples)
- [Invocations samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-invocations/samples)
