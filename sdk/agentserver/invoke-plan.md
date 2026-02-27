# Implementation Plan: Agent Invocation API (`invoke.tsp`)

## TL;DR

Implement the 4 operations defined in `invoke.tsp` by evolving the **container-side** server
(`azure-ai-agentserver-core`) to support the new invocation routes the platform will proxy to,
and adding new **container-side endpoints** that align with the public API's raw-bytes proxy model.
The platform (Foundry data plane) maps the public `POST /agents/{name}/versions/{version}/invocations`
→ container `POST /invoke`, extracting path params and headers, and proxying the opaque body through.

**One workstream** — all changes are in `azure-ai-agentserver-core`:
- Add `/invoke` and `/invoke/docs/openapi.json` routes alongside existing `/runs` + `/responses`.
- Container developers override `agent_invoke()` directly with their own input/output logic.

No adapter changes needed — the invoke body is **opaque bytes**, so there's no framework-specific
conversion to do. Adapters (`agentserver-agentframework`, `agentserver-langgraph`) are irrelevant
for invoke; they only apply to the existing `/runs` + `/responses` routes which use the typed
OpenAI Responses API format.

No new packages are needed. No client SDK changes — the client side will come from TypeSpec
codegen into `azure-ai-projects` as a separate workstream.

---

## Architecture: Public API ↔ Container

```
Caller → POST /agents/{name}/versions/{ver}/invocations?agent_session_id=X
         [body: opaque bytes, Content-Type: caller-chosen]
                │
                ▼
         ┌──────────────────────────────────────┐
         │      Foundry Data Plane              │
         │  (raw-bytes proxy per invoke.tsp)     │
         │  • extracts path params               │
         │  • uses agent_session_id for routing  │
         │  • manages invocation ID & state      │
         │  • forwards body as-is                │
         │  • relays response bytes              │
         │  • sets x-agent-invocation-id         │
         │  • sets x-agent-session-id            │
         │  • handles GET /{id} and /{id}:cancel │
         └──────────────┬───────────────────────┘
                        │  (session_id, invocation_id
                        │   stripped — container
                        │   doesn't see them)
                        ▼
         POST /invoke
         [same body bytes, same Content-Type]
                        │
                        ▼
         ┌─────────────────────────────────┐
         │   Agent Container               │
         │  (FoundryCBAgent)               │
         │  • /invoke  (create invocation) │
         │  • /invoke/docs/openapi.json    │
         │  • /liveness, /readiness        │
         └─────────────────────────────────┘
```

> **Note:** Both `agent_session_id` and `invocation_id` are **platform-level** concepts.
> `agent_session_id` controls request routing to backend compute (sticky sessions).
> `invocation_id` identifies and tracks each invocation's lifecycle (state, get, cancel).
> The container server never sees either — both are managed by the Foundry data plane.
> The container processes one request at a time: body in → body out.

---

## Steps

### Step 1 — Define `InvocationContext` (new request context)

**File:** `azure-ai-agentserver-core/azure/ai/agentserver/core/server/common/invocation_context.py` (new)

Unlike `AgentRunContext` (which deserializes JSON into `CreateResponse`), `InvocationContext` wraps the
**raw request** without parsing the body:

- `body: bytes` — request body as-is
- `headers: dict` — all request headers (use `headers.get("content-type")` when needed)


This context is framework-agnostic; the container developer's `agent_invoke()` receives it
and returns raw bytes.

### Step 2 — Add `/invoke` route to `FoundryCBAgent`

**File:** `azure-ai-agentserver-core/azure/ai/agentserver/core/server/base.py`

Add 2 new Starlette routes to the existing `routes` list:

| Method | Path | Handler | Maps to TSP operation |
|--------|------|---------|-----------------------|
| POST | `/invoke` | `invoke_endpoint` | `createAgentInvocation` |
| GET | `/invoke/docs/openapi.json` | `openapi_spec_endpoint` | `getAgentInvocationOpenApiSpec` |

> `getAgentInvocation` and `cancelAgentInvocation` are handled entirely by the platform —
> no container routes needed.

**`invoke_endpoint` handler logic:**
1. Read raw body: `body = await request.body()`
2. Copy request headers into a dict
3. Build `InvocationContext(body=body, headers=headers)`
4. Call `self.agent_invoke(context)` (developer overrides this method)
5. Return `Response` with:
   - Body bytes from agent
   - Content-Type from agent's return

**Streaming support:** If `agent_invoke()` returns an async generator of bytes,
wrap in `StreamingResponse` with the content-type from the agent. No SSE framing
at this layer — the agent's bytes are the SSE stream.

### Step 3 — Add `agent_invoke()` to `FoundryCBAgent`

**File:** `azure-ai-agentserver-core/azure/ai/agentserver/core/server/base.py`

```python
async def agent_invoke(self, context: InvocationContext) -> InvocationResponse:
    # Default: 404 Not Implemented
    raise NotImplementedError("Override agent_invoke() to handle /invoke requests")

def agent_openapi_spec(self) -> Optional[dict]:
    # Default: None (returns 404)
    return None
```

`agent_invoke()` is **not abstract** — it has a default 404 response. Container developers
override it when they want to support the invoke route. This is orthogonal to `agent_run()` —
the two methods serve different protocols:

| Method | Route | Input | Output | Used by |
|--------|-------|-------|--------|---------|
| `agent_run()` | `/runs`, `/responses` | Typed `AgentRunContext` (OpenAI Responses API) | `Response` / `ResponseStreamEvent` generator | Adapters (AgentFramework, LangGraph) |
| `agent_invoke()` | `/invoke` | Raw `InvocationContext` (body + headers) | `InvocationResponse` (opaque bytes) | Developer implements directly |

`InvocationResponse` is a simple dataclass:
- `body: Union[bytes, AsyncGenerator[bytes, None]]`
- `content_type: str`
- `status_code: int = 200`

### Step 4 — Add `InvocationResponse` model

**File:** `azure-ai-agentserver-core/azure/ai/agentserver/core/server/common/invocation_response.py` (new)

Dataclass holding the container's response to be sent back through the platform:
- `body` — raw bytes or async byte generator (for streaming)
- `content_type` — e.g., `application/json` or `text/event-stream`
- `status_code` — HTTP status (default 200)

> The platform adds `x-agent-invocation-id` and `x-agent-session-id` response headers —
> the container doesn't set either.

### Step 5 — OpenAPI spec endpoint

**File:** `azure-ai-agentserver-core/azure/ai/agentserver/core/server/base.py`

The `openapi_spec_endpoint` handler:
1. Call `self.agent_openapi_spec()`
2. If `None`, return `404 {"error": {"code": "NotFound", ...}}`
3. Otherwise, return `200` with `Content-Type: application/json` and the spec dict

Allow container developers to override `agent_openapi_spec()` to return a generated spec
based on their agent's capabilities.

### Step 6 — Update exports and `__init__.py`

**Files:**
- `azure-ai-agentserver-core/azure/ai/agentserver/core/__init__.py` — export `InvocationContext`, `InvocationResponse`
- `azure-ai-agentserver-core/azure/ai/agentserver/core/server/__init__.py` — export new classes
- `azure-ai-agentserver-core/azure/ai/agentserver/core/server/common/__init__.py` — export new modules

### Step 7 — Tests

**File:** `azure-ai-agentserver-core/tests/test_invoke_routes.py` (new)

Test cases using Starlette's `TestClient`:

| # | Test | Validates |
|---|------|-----------|
| 1 | `POST /invoke` with JSON body → 200 + JSON response | Basic invocation |
| 2 | `POST /invoke` with `text/plain` body → proxied correctly | Non-JSON content type |
| 3 | `POST /invoke` streaming → `text/event-stream` response | SSE passthrough |
| 4 | `POST /invoke` without override → 501 | Default not-implemented |
| 5 | `GET /invoke/docs/openapi.json` → spec or 404 | OpenAPI discovery |

### Step 8 — Documentation

- Update `FoundryCBAgent` docstrings with new routes
- Update `base.py` `run()` docstring to list all routes
- Add a "Migration Guide" section to README explaining the `/invoke` routes

---

## Decisions

- **Routes use `/invoke` prefix** (not `/invocations`) — container routes are shorter; the platform maps `/agents/{n}/versions/{v}/invocations` → `/invoke`
- **No bridge to `agent_run()`** — the invoke body is opaque bytes; it cannot be translated into the typed `AgentRunContext` that `agent_run()` requires. The two protocols (`/runs` vs `/invoke`) are independent.
- **No adapter layer for invoke** — adapters (AgentFramework, LangGraph) only apply to the `/runs` + `/responses` routes. For `/invoke`, the container developer implements `agent_invoke()` directly because only they understand their input/output format.
- **No state management in container** — the platform owns invocation IDs, state tracking, get, and cancel. The container is stateless: body in → body out.
- **No body parsing at server layer** — raw bytes in, raw bytes out. Adapters parse if needed.
- **Two container routes only** — `POST /invoke` (required) and `GET /invoke/docs/openapi.json` (optional, 404 by default)
