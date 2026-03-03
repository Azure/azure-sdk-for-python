# azure-ai-agentserver

A standalone, **protocol-agnostic agent server** package for Azure AI. Provides a
Starlette-based `AgentServer` base class with pluggable protocol heads, OpenAPI-based
request/response validation, tracing, logging, and health endpoints — with **zero
framework coupling**.

## Overview

`azure-ai-agentserver` is the canonical agent-server package going forward. It supports
multiple protocol heads (`/invoke`, `/responses`, and future protocols) through a pluggable
handler architecture. Phase 1 ships with `/invoke` support; `/responses` and other
protocols will be added in subsequent phases.

**Key properties:**

- **Standalone** — no dependency on `azure-ai-agentserver-core`, `openai`, or any AI
  framework library.
- **Starlette + uvicorn** — lightweight ASGI server, same technology used by other Azure
  AI packages.
- **Abstract base class** — subclass `AgentServer` and implement handler methods for the
  protocol heads you need.
- **Customer-managed adapters** — integration with LangGraph, Agent Framework, Semantic
  Kernel, etc. is done in your own code. We provide samples, not separate adapter packages.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 1: Agent Service (Cloud Infrastructure)                       │
│  Supports: /invoke, /responses, /mcp, /a2a, /activity               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
              ┌───────────────────────────────┐
              │ azure-ai-agentserver          │
              │ AgentServer                   │
              │                               │
              │ Protocol heads:               │
              │  • /invoke                    │
              │  • /responses                 │
              │                               │
              │ OpenAPI spec validation (all) │
              │ Tracing, logging, health      │
              └───────────────────────────────┘
                             │
                   Customer owns adapters:
                   ┌─────────┼─────────┐
                   ▼         ▼         ▼
              LangGraph   Agent     Semantic
              adapter   Framework    Kernel
              (sample)   adapter    adapter
                        (sample)   (sample)
```

**Single package, multiple protocol heads, no framework coupling.**

## Installation

```bash
pip install azure-ai-agentserver
```

**Requires Python >= 3.10.**

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

### Routes (Phase 1)

| Route | Method | Description |
|-------|--------|-------------|
| `/invocations` | POST | Create and process an invocation |
| `/invocations/{id}` | GET | Retrieve a previous invocation result |
| `/invocations/{id}/cancel` | POST | Cancel a running invocation |
| `/invocations/docs/openapi.json` | GET | Return the registered OpenAPI spec |
| `/liveness` | GET | Health check |
| `/readiness` | GET | Readiness check |

## OpenAPI Validation

Register a spec to validate request and response bodies at runtime:

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

- Non-conforming **requests** return 400 with details.
- Non-conforming **responses** log warnings but are not blocked.
- `GET /invocations/docs/openapi.json` serves the registered spec (or 404 if none).

## Samples

| Sample | Description |
|--------|-------------|
| `samples/simple_invoke_agent/` | Minimal from-scratch agent |
| `samples/openapi_validated_agent/` | OpenAPI spec with request/response validation |
| `samples/async_invoke_agent/` | Long-running tasks with get & cancel support |
| `samples/human_in_the_loop_agent/` | Synchronous human-in-the-loop interaction |
| `samples/langgraph_invoke_agent/` | Customer-managed LangGraph adapter |
| `samples/agentframework_invoke_agent/` | Customer-managed Agent Framework adapter |

## Vision & Migration Path

### Phase 1 (Current): `/invoke` only

- Ship `azure-ai-agentserver` with the `/invoke` protocol head.
- Existing `agentserver-core` + Layer 3 adapter packages remain as-is for `/responses`
  customers.
- Samples show customer-managed framework integration (LangGraph, Agent Framework, Semantic
  Kernel, etc.).

### Phase 2 (Future): Add `/responses`

- Add a `/responses` protocol head to `azure-ai-agentserver` as a built-in handler.
- Validation for `/responses` uses the same OpenAPI-based approach (not
  `openai.types.responses.*` imports).
- Sample adapters show how to port existing LangGraph / Agent Framework patterns.

### Phase 3 (Future): Deprecate old packages

- Deprecate `azure-ai-agentserver-core` (replaced by this package's `/responses` handler).
- Deprecate `azure-ai-agentserver-agentframework` and `azure-ai-agentserver-langgraph`
  (replaced by customer-managed adapter code provided as samples).
- Customers who depend on Layer 3 adapters copy the adapter code into their own projects.

## License

MIT
