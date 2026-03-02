# Design: `azure-ai-agentserver` — Generic Agent Server Package

## Overview

A new standalone package `azure-ai-agentserver` providing a **protocol-agnostic agent server base**. The server supports multiple protocol heads (/invoke, /responses, and future protocols) through a pluggable handler architecture. Initially ships with `/invoke` support.

---

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
              │  • /invoke (Phase 1)          │
              │  • /responses (Phase 2)       │
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

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package name | `azure-ai-agentserver` | The canonical agentserver package going forward |
| Core dependency | Standalone | No dependency on `azure-ai-agentserver-core`. Own Starlette server, tracing, logging. |
| Web server | Starlette + uvicorn | Same tech as core, independent copy |
| Base class pattern | Abstract base class | Customer implements handler methods per protocol head |
| Invoke validation | Included in initial scope | Spec-based validation, no protocol type imports |
| Framework adapters | Customer-managed | No Layer 3 adapter packages. We provide samples showing how customers integrate their own frameworks. |

## Namespace

The Python import path is `azure.ai.agentserver`. All intermediate `__init__.py` files use `pkgutil.extend_path` for namespace compatibility with existing packages during the transition period.

```python
from azure.ai.agentserver import AgentServer, InvokeRequest
```

## Scope (Phase 1)

- [x] New package scaffolding (pyproject.toml, __init__.py, etc.)
- [x] Generic `AgentServer` base class with pluggable protocol heads
- [x] `/invoke` protocol head with all 4 operations from invoke.tsp
- [x] OpenAPI spec-based validation for /invoke
- [x] Sample: simple invoke agent (custom agent from scratch)
- [x] Sample: LangGraph invoke agent (customer-managed adapter pattern)
- [x] Sample: Agent Framework invoke agent (customer-managed adapter pattern)

---

## Step 1: Scaffold Package Directory

Create `sdk/agentserver/azure-ai-agentserver/` with this structure:

```
azure-ai-agentserver/
├── azure/
│   ├── __init__.py                       # pkgutil.extend_path
│   └── ai/
│       ├── __init__.py                   # pkgutil.extend_path
│       └── agentserver/
│           ├── __init__.py               # exports AgentServer, InvokeRequest
│           ├── _version.py               # VERSION = "1.0.0b1"
│           ├── py.typed
│           ├── _constants.py
│           ├── _logger.py
│           ├── _types.py                 # InvokeRequest dataclass
│           ├── server/
│           │   ├── __init__.py
│           │   └── _base.py              # AgentServer class
│           └── validation/
│               ├── __init__.py
│               └── _openapi_validator.py
├── samples/
│   ├── simple_invoke_agent/
│   │   ├── simple_invoke_agent.py        # Minimal from-scratch agent
│   │   └── requirements.txt
│   ├── langgraph_invoke_agent/
│   │   ├── langgraph_invoke_agent.py     # Customer-managed LangGraph adapter
│   │   └── requirements.txt
│   └── agentframework_invoke_agent/
│       ├── agentframework_invoke_agent.py # Customer-managed AF adapter
│       └── requirements.txt
│   └── async_invoke_agent/
│       ├── async_invoke_agent.py          # Get & cancel invocation support
│       └── requirements.txt
├── tests/
│   ├── conftest.py
│   ├── test_server_routes.py
│   ├── test_invoke.py
│   ├── test_get_cancel.py
│   ├── test_openapi_validation.py
│   ├── test_types.py
│   └── test_health.py
├── pyproject.toml
├── CHANGELOG.md
├── README.md
├── LICENSE
├── MANIFEST.in
├── dev_requirements.txt
├── cspell.json
└── pyrightconfig.json
```

## Step 2: `pyproject.toml`

Model after `azure-ai-agentserver-core/pyproject.toml`. Key differences:

- `name = "azure-ai-agentserver"`
- **Minimal dependencies** — no `azure-ai-projects`, no `azure-ai-agents`, no `openai`, no framework libs
- Dependencies:
  - `starlette>=0.45.0`
  - `uvicorn>=0.31.0`
  - `azure-core>=1.35.0`
  - `azure-identity`
  - `azure-monitor-opentelemetry>=1.5.0`
  - `opentelemetry-api>=1.35`
  - `opentelemetry-exporter-otlp-proto-http`
  - `jsonschema` (for OpenAPI validation)
- `requires-python = ">=3.10"`
- Version from `azure.ai.agentserver._version.VERSION`
- `[tool.azure-sdk-build] breaking = false`, `pyright = false`, `verifytypes = false`

## Step 3: `AgentServer` Base Class

A generic Starlette-based agent server in `server/_base.py`. The class is **not invoke-specific** — it provides shared server infrastructure and registers protocol-specific routes.

### Constructor

```python
class AgentServer:
    def __init__(
        self,
        openapi_spec: Optional[dict] = None,
    ):
        """
        Generic agent server base. Subclass and implement protocol handler methods.

        :param openapi_spec: Optional OpenAPI spec for /invoke request/response validation.
        """
```

### Routes (Phase 1: /invoke + health)

| Route | Method | Handler | Maps to TSP operation |
|-------|--------|---------|----------------------|
| `/invocations/docs/openapi.json` | GET | `_get_openapi_spec_endpoint` | `getAgentInvocationOpenApiSpec` |
| `/invocations` | POST | `_create_invocation_endpoint` | `createAgentInvocation` |
| `/invocations/{invocation_id}` | GET | `_get_invocation_endpoint` | `getAgentInvocation` |
| `/invocations/{invocation_id}/cancel` | POST | `_cancel_invocation_endpoint` | `cancelAgentInvocation` |
| `/liveness` | GET | `_liveness_endpoint` | Health check |
| `/readiness` | GET | `_readiness_endpoint` | Readiness check |

In Phase 2, `/responses` routes would be added to the same server class.

### Abstract Methods (Invoke Protocol)

```python
@abstractmethod
async def invoke(
    self,
    request: InvokeRequest,
) -> Union[bytes, AsyncGenerator[bytes, None]]:
    """
    Process an invocation.

    Return either:
    - bytes (non-streaming): complete response body
    - AsyncGenerator[bytes, None] (streaming): yields chunks of response bytes

    :param request: The invoke request containing body, headers, and invocation_id.
    """

async def get_invocation(
    self,
    invocation_id: str,
) -> bytes:
    """
    Retrieve a previous invocation result.
    Default implementation returns 404. Override to support retrieval.
    """
    raise NotImplementedError

async def cancel_invocation(
    self,
    invocation_id: str,
    body: Optional[bytes] = None,
    headers: Optional[dict[str, str]] = None,
) -> bytes:
    """
    Cancel an invocation.
    Default implementation returns 404. Override to support cancellation.
    """
    raise NotImplementedError
```

Note: `get_invocation` and `cancel_invocation` have **default implementations** that return 404 (most agents won't support these). Only `invoke()` is abstract.

### Optional Override

```python
def get_openapi_spec(self) -> Optional[dict]:
    """Return OpenAPI spec dict for this agent, or None (returns 404)."""
    return self._openapi_spec
```

### Data Types

```python
@dataclass
class InvokeRequest:
    """Incoming invoke request."""
    body: bytes                  # Raw request body
    headers: dict[str, str]      # All HTTP request headers
    invocation_id: str           # Server-generated UUID for this invocation
```

- **`body`**: Raw request body bytes. The customer parses it themselves (e.g., `json.loads(request.body)`).
- **`headers`**: All HTTP request headers (Content-Type, Accept, Authorization, custom headers, etc.). Customers read `request.headers.get("content-type")` themselves.
- **`invocation_id`**: Server-generated UUID. Returned to the caller via `x-agent-invocation-id` response header. Store this if you need to support `get_invocation` / `cancel_invocation`.

Return type is plain `bytes` (non-streaming) or `AsyncGenerator[bytes, None]` (streaming).

The server auto-generates an `invocation_id` (UUID) for each `createAgentInvocation` call and:
- Packages it into `InvokeRequest` alongside `body` and `headers`
- Sets it as the `x-agent-invocation-id` response header
- The same ID is used by callers to `GET /invocations/{invocation_id}` or `POST /invocations/{invocation_id}/cancel`


```python
result = await self.invoke(request)
if isinstance(result, bytes):
    return Response(content=result, headers={"x-agent-invocation-id": request.invocation_id})
else:
    # result is an AsyncGenerator
    return StreamingResponse(result, headers={"x-agent-invocation-id": request.invocation_id})
```

### `_create_invocation_endpoint` Flow

1. Read request body as raw `bytes`, collect all HTTP headers into a `dict[str, str]`
2. Generate `invocation_id = str(uuid.uuid4())`
3. Build `InvokeRequest(body=body, headers=headers, invocation_id=invocation_id)`
4. If OpenAPI spec is registered, validate request body against spec's request schema
5. Call `self.invoke(request)`
6. If result is `bytes` (non-streaming):
   - If OpenAPI spec is registered, validate response body against spec's response schema (log warnings, don't block)
   - Return `Response(content=result, headers={"x-agent-invocation-id": invocation_id})`
7. If result is `AsyncGenerator` (streaming):
   - Return `StreamingResponse(result, headers={"x-agent-invocation-id": invocation_id})` — chunks are forwarded as-is
   - OpenAPI validation is skipped for streaming (can't validate partial chunks)

### Tracing

Reuse the same OpenTelemetry + Azure Monitor pattern from `FoundryCBAgent` in `azure-ai-agentserver-core/azure/ai/agentserver/core/server/base.py`:
- Span name: `AgentServer-invoke`
- Same `init_tracing()` / `setup_otlp_exporter()` / `setup_application_insights_exporter()` methods

### Logging

Replicate the `_logger.py` and `_constants.py` patterns from core:
- Logger namespace: `azure.ai.agentserver`
- Same env var conventions for debug, telemetry endpoints

### `run()` / `run_async()`

Same pattern as `FoundryCBAgent` (but on `AgentServer`):
- `run(port)` → `uvicorn.run()` for sync
- `run_async(port)` → `uvicorn.Server` for async (awaitable)
- Default port from `DEFAULT_AD_PORT` env var or 8088

## Step 4: OpenAPI Spec Validation

In `validation/_openapi_validator.py`:

### Registration

Customer registers a spec via constructor param or method:

```python
server = MyAgent(openapi_spec=spec_dict)
# or
server.set_openapi_spec(spec_dict)
```

### Behavior

- **`getAgentInvocationOpenApiSpec` endpoint**: Returns the registered spec as `application/json`, or 404 if not set
- **Request validation** (on `createAgentInvocation`): Extract request body schema from spec, validate incoming body with `jsonschema`. Return 400 with descriptive errors on failure.
- **Response validation** (on `createAgentInvocation`): Extract response body schema from spec, validate outgoing body. Log warnings on validation failure (don't block response — customer's agent already executed).
- **No protocol type imports**: Validation is purely schema-based per the constraint in problem.md. This pattern generalizes to /responses in Phase 2.

### `OpenApiValidator` Class

```python
class OpenApiValidator:
    def __init__(self, spec: dict):
        self._spec = spec
        self._request_schema = self._extract_request_schema(spec)
        self._response_schema = self._extract_response_schema(spec)

    def validate_request(self, body: bytes, content_type: str) -> list[str]:
        """Returns list of validation errors, empty if valid."""

    def validate_response(self, body: bytes, content_type: str) -> list[str]:
        """Returns list of validation errors, empty if valid."""
```

## Step 5: Samples

### Sample 1: Simple Invoke Agent (from scratch)

`samples/simple_invoke_agent/simple_invoke_agent.py` — minimal agent, no framework:

```python
"""
Simple invoke agent example.
Accepts JSON requests, echoes back with a greeting.
"""
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

### Sample 2: LangGraph Invoke Agent (customer-managed adapter)

`samples/langgraph_invoke_agent/langgraph_invoke_agent.py` — shows how a customer wraps their LangGraph agent:

```python
"""
LangGraph agent served via /invoke.
Customer owns the LangGraph ↔ invoke conversion logic.
This replaces the need for azure-ai-agentserver-langgraph.
"""
import json
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import AzureChatOpenAI

from azure.ai.agentserver import AgentServer, InvokeRequest


def build_graph() -> StateGraph:
    """Customer builds their LangGraph agent as usual."""
    llm = AzureChatOpenAI(model="gpt-4o")

    def chatbot(state: MessagesState):
        return {"messages": [llm.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("chatbot", chatbot)
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)
    return graph.compile()


class LangGraphInvokeAgent(AgentServer):
    """Customer-managed adapter: LangGraph ↔ /invoke protocol."""

    def __init__(self):
        super().__init__()
        self.graph = build_graph()

    async def invoke(self, request: InvokeRequest):
        data = json.loads(request.body)
        user_message = data["message"]
        stream = data.get("stream", False)

        if stream:
            # Streaming: return an async generator
            return self._stream_response(user_message)

        # Non-streaming: return bytes
        result = await self.graph.ainvoke(
            {"messages": [{"role": "user", "content": user_message}]}
        )
        last_message = result["messages"][-1]
        return json.dumps({"reply": last_message.content}).encode()

    async def _stream_response(self, user_message: str):
        """Async generator that yields response chunks."""
        async for event in self.graph.astream_events(
            {"messages": [{"role": "user", "content": user_message}]},
            version="v2",
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield json.dumps({"delta": chunk}).encode() + b"\n"

if __name__ == "__main__":
    LangGraphInvokeAgent().run()
```

### Sample 3: Agent Framework Invoke Agent (customer-managed adapter)

`samples/agentframework_invoke_agent/agentframework_invoke_agent.py` — shows the same pattern for Agent Framework:

```python
"""
Agent Framework agent served via /invoke.
Customer owns the AgentFramework ↔ invoke conversion logic.
This replaces the need for azure-ai-agentserver-agentframework.
"""
import json
from agent_framework import AgentProtocol

from azure.ai.agentserver import AgentServer, InvokeRequest


class AgentFrameworkInvokeAgent(AgentServer):
    """Customer-managed adapter: Agent Framework ↔ /invoke protocol."""

    def __init__(self, agent: AgentProtocol):
        super().__init__()
        self.agent = agent

    async def invoke(self, request: InvokeRequest) -> bytes:
        data = json.loads(request.body)

        # Customer converts /invoke request → Agent Framework input
        af_input = self._to_agent_framework_input(data)

        # Run the agent
        af_output = await self.agent.run(af_input)

        # Customer converts Agent Framework output → /invoke response
        response = self._to_invoke_response(af_output)
        return json.dumps(response).encode()

    def _to_agent_framework_input(self, data: dict):
        """Customer defines their own input conversion."""
        # ... framework-specific conversion
        pass

    def _to_invoke_response(self, af_output) -> dict:
        """Customer defines their own output conversion."""
        # ... framework-specific conversion
        pass
```

### Sample 4: Async Agent with Get & Cancel Support

`samples/async_invoke_agent/async_invoke_agent.py` — shows how to support `get_invocation` and `cancel_invocation` for long-running tasks:

```python
"""
Async invoke agent example.
Demonstrates get_invocation and cancel_invocation for long-running work.
Invocations run in background tasks; callers poll or cancel by ID.
"""
import asyncio
import json
from azure.ai.agentserver import AgentServer, InvokeRequest


class AsyncAgent(AgentServer):
    def __init__(self):
        super().__init__()
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: dict[str, bytes] = {}

    async def invoke(self, request: InvokeRequest) -> bytes:
        data = json.loads(request.body)

        # Start long-running work in a background task
        # Use server-generated invocation_id for tracking
        task = asyncio.create_task(self._do_work(request.invocation_id, data))
        self._tasks[request.invocation_id] = task

        # Return immediately — caller uses x-agent-invocation-id header to poll/cancel
        return json.dumps({
            "invocation_id": request.invocation_id,
            "status": "running",
        }).encode()

    async def get_invocation(self, invocation_id: str) -> bytes:
        # Completed — return stored result
        if invocation_id in self._results:
            return self._results[invocation_id]

        # Still running
        if invocation_id in self._tasks:
            task = self._tasks[invocation_id]
            if not task.done():
                return json.dumps({
                    "invocation_id": invocation_id,
                    "status": "running",
                }).encode()
            # Just finished — collect result
            result = task.result()
            self._results[invocation_id] = result
            del self._tasks[invocation_id]
            return result

        # Unknown ID
        return json.dumps({"error": "not found"}).encode()

    async def cancel_invocation(
        self,
        invocation_id: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        if invocation_id in self._tasks:
            self._tasks[invocation_id].cancel()
            del self._tasks[invocation_id]
            return json.dumps({
                "invocation_id": invocation_id,
                "status": "cancelled",
            }).encode()
        return json.dumps({"error": "not found"}).encode()

    async def _do_work(self, invocation_id: str, data: dict) -> bytes:
        """Simulate long-running work."""
        await asyncio.sleep(10)
        result = json.dumps({
            "invocation_id": invocation_id,
            "status": "completed",
            "output": f"Processed: {data}",
        }).encode()
        self._results[invocation_id] = result
        return result


if __name__ == "__main__":
    AsyncAgent().run()
```

**Usage:**
```bash
# Start an invocation
curl -X POST http://localhost:8088/invocations -d '{"query": "analyze dataset"}'
# → x-agent-invocation-id: abc-123
# → {"invocation_id": "abc-123", "status": "running"}

# Poll for result
curl http://localhost:8088/invocations/abc-123
# → {"invocation_id": "abc-123", "status": "running"}  (still working)
# → {"invocation_id": "abc-123", "status": "completed", "output": "..."}  (done)

# Or cancel
curl -X POST http://localhost:8088/invocations/abc-123/cancel
# → {"invocation_id": "abc-123", "status": "cancelled"}
```

## Step 6: Update CI

Add the new artifact to `ci.yml` under `Artifacts:`:

```yaml
- name: azure-ai-agentserver
  safeName: azureaiagentserver
```

## Step 7: Boilerplate Files

| File | Content |
|------|---------|
| `CHANGELOG.md` | Initial `1.0.0b1 (Unreleased)` entry |
| `README.md` | Document the generic agentserver concept, /invoke protocol, how to subclass `AgentServer`, framework adapter samples, OpenAPI validation |
| `LICENSE` | MIT (same as other packages) |
| `MANIFEST.in` | Include `py.typed`, `LICENSE`, `README.md` |
| `dev_requirements.txt` | `pytest`, `httpx`, `pytest-asyncio` |
| `cspell.json` | Same pattern as other agentserver packages |
| `pyrightconfig.json` | Same pattern as other agentserver packages |

## Step 8: Tests

Test directory structure:

```
tests/
├── conftest.py                     # Shared fixtures (test app, async client)
├── test_server_routes.py           # All route/endpoint tests
├── test_invoke.py                  # invoke() dispatch (streaming, non-streaming)
├── test_get_cancel.py              # get_invocation / cancel_invocation
├── test_openapi_validation.py      # OpenAPI spec validation
├── test_types.py                   # InvokeRequest dataclass
└── test_health.py                  # Liveness / readiness endpoints
```

All tests use `httpx.AsyncClient` with Starlette's ASGI transport (no real uvicorn needed). Shared fixtures in `conftest.py` provide test agents: `EchoAgent` (echoes body), `StreamingAgent` (yields chunks), `AsyncAgent` (supports get/cancel), `ValidatedAgent` (has OpenAPI spec).

### Test Plan

#### `test_server_routes.py` — Route Registration (7 tests)

| # | Test | Description |
|---|------|-------------|
| 1 | `test_post_invocations_returns_200` | `POST /invocations` with valid body returns 200 |
| 2 | `test_post_invocations_returns_invocation_id_header` | Response includes `x-agent-invocation-id` header (UUID format) |
| 3 | `test_get_openapi_spec_returns_404_when_not_set` | `GET /invocations/docs/openapi.json` returns 404 if no spec registered |
| 4 | `test_get_openapi_spec_returns_spec` | `GET /invocations/docs/openapi.json` returns registered spec as JSON |
| 5 | `test_get_invocation_returns_404_default` | `GET /invocations/{id}` returns 404 when not overridden |
| 6 | `test_cancel_invocation_returns_404_default` | `POST /invocations/{id}/cancel` returns 404 when not overridden |
| 7 | `test_unknown_route_returns_404` | `GET /unknown` returns 404 |

#### `test_invoke.py` — Invoke Dispatch (8 tests)

| # | Test | Description |
|---|------|-------------|
| 1 | `test_invoke_echoes_body` | `POST /invocations` body is passed to `invoke()` and echoed back |
| 2 | `test_invoke_receives_headers` | `request.headers` contains sent HTTP headers (Content-Type, custom) |
| 3 | `test_invoke_receives_invocation_id` | `request.invocation_id` is a non-empty UUID string |
| 4 | `test_invoke_invocation_id_unique` | Two consecutive `POST /invocations` return different `x-agent-invocation-id` values |
| 5 | `test_invoke_streaming_returns_chunked` | Streaming agent returns `Transfer-Encoding: chunked` / `StreamingResponse` |
| 6 | `test_invoke_streaming_yields_all_chunks` | All chunks from the async generator are received by the client |
| 7 | `test_invoke_streaming_has_invocation_id_header` | Streaming response also includes `x-agent-invocation-id` header |
| 8 | `test_invoke_empty_body` | `POST /invocations` with empty body doesn't crash (passes `b""`) |

#### `test_get_cancel.py` — Get & Cancel Invocations (5 tests)

| # | Test | Description |
|---|------|-------------|
| 1 | `test_get_invocation_after_invoke` | Invoke, then `GET /invocations/{id}` returns stored result |
| 2 | `test_get_invocation_unknown_id_returns_404` | `GET /invocations/{unknown}` returns 404 |
| 3 | `test_cancel_invocation_after_invoke` | Invoke, then `POST /invocations/{id}/cancel` returns cancelled status |
| 4 | `test_cancel_invocation_unknown_id_returns_404` | `POST /invocations/{unknown}/cancel` returns 404 |
| 5 | `test_get_after_cancel_returns_404` | Cancel, then get same ID returns 404 |

#### `test_openapi_validation.py` — OpenAPI Spec Validation (7 tests)

| # | Test | Description |
|---|------|-------------|
| 1 | `test_valid_request_passes` | Request matching schema returns 200 |
| 2 | `test_invalid_request_returns_400` | Request missing required field returns 400 with error details |
| 3 | `test_invalid_request_wrong_type_returns_400` | Request with wrong field type returns 400 |
| 4 | `test_response_validation_logs_warning` | Invalid response body logs warning but still returns 200 (non-blocking) |
| 5 | `test_no_spec_skips_validation` | Agent with no spec accepts any request body |
| 6 | `test_spec_endpoint_returns_spec` | `GET /invocations/docs/openapi.json` returns the registered spec |
| 7 | `test_non_json_body_skips_validation` | Non-JSON content type bypasses JSON schema validation |

#### `test_types.py` — InvokeRequest Dataclass (4 tests)

| # | Test | Description |
|---|------|-------------|
| 1 | `test_invoke_request_fields` | `InvokeRequest` has `body`, `headers`, `invocation_id` fields |
| 2 | `test_invoke_request_body_is_bytes` | `body` field accepts and stores `bytes` |
| 3 | `test_invoke_request_headers_is_dict` | `headers` field is `dict[str, str]` |
| 4 | `test_invoke_request_invocation_id_is_str` | `invocation_id` is a string |

#### `test_health.py` — Health Check Endpoints (2 tests)

| # | Test | Description |
|---|------|-------------|
| 1 | `test_liveness_returns_200` | `GET /liveness` returns 200 |
| 2 | `test_readiness_returns_200` | `GET /readiness` returns 200 |

**Total: 33 tests across 6 files.**

---

## Phase 2 Sketch: Adding `/responses`

When /responses is added, `AgentServer` gains new routes and an abstract method:

```python
class AgentServer:
    # Phase 1 (exists)
    @abstractmethod
    async def invoke(self, request: InvokeRequest) -> Union[bytes, AsyncGenerator[bytes, None]]: ...

    # Phase 2 (added)
    async def responses(self, request: RespondRequest) -> Union[RespondResult, AsyncGenerator[RespondEvent]]:
        """Handle a /responses request. Override to support /responses protocol."""
        raise NotImplementedError  # returns 404 if not overridden
```

A customer who wants both protocols overrides both methods. A customer who only cares about /invoke keeps `responses()` as-is (returns 404). This is strictly additive — no breaking changes.

Validation for /responses would use the same OpenAPI-based approach: customer provides a spec describing their response format, and `jsonschema` validates it at runtime. No imports from `openai.types.responses.*`.

---

## Vision & Migration Path

### Phase 1 (Now): `/invoke` only
- Ship `azure-ai-agentserver` with `/invoke` protocol head
- `agentserver-core` + Layer 3 adapters remain as-is for /responses customers
- Provide samples showing customer-managed framework integration (LangGraph, Agent Framework, Semantic Kernel, etc.)

### Phase 2 (Future): Add `/responses`
- Add `/responses` protocol head to `azure-ai-agentserver` as a built-in handler
- Validation for /responses done via OpenAPI spec (same as /invoke), NOT by importing `openai.types.responses.*`
- Provide sample adapters showing customers how to port LangGraph/AgentFramework patterns into their own code

### Phase 3 (Future): Deprecate old packages
- Deprecate `azure-ai-agentserver-core` (replaced by this package's /responses handler)
- Deprecate `azure-ai-agentserver-agentframework` (replaced by customer-managed adapter code)
- Deprecate `azure-ai-agentserver-langgraph` (replaced by customer-managed adapter code)
- Customers who currently depend on Layer 3 adapters copy the adapter code into their own projects (we provide that code as samples)


## Verification Checklist

1. **Package installs cleanly**: `pip install -e sdk/agentserver/azure-ai-agentserver/` succeeds without conflicts with existing packages
2. **Namespace works**: `from azure.ai.agentserver import AgentServer` works when `azure-ai-agentserver-core` is also installed
3. **Simple sample runs**: `simple_invoke_agent.py` starts and responds to curl on `/invocations` endpoints
4. **LangGraph sample runs**: `langgraph_invoke_agent.py` starts and handles requests (with customer's own langchain/langgraph installed)
5. **OpenAPI validation**: Non-conforming payload returns 400; spec endpoint returns registered spec or 404
6. **CI builds**: `ci.yml` change causes the new package to build as an artifact
7. **No framework deps**: `pip show azure-ai-agentserver` shows no langchain/langgraph/openai/agent-framework in dependencies
