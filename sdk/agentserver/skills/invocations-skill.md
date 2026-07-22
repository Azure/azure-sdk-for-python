---
name: agentserver-invocations
description: 'Build agent HTTP / WebSocket endpoints that speak the Azure AI Hosted Agents invocations protocol, using `InvocationAgentServerHost` from `azure-ai-agentserver-invocations`. WHEN: "expose my agent as a Foundry Hosted Agent invocations endpoint", "free-form POST /invocations + GET /invocations/{id} status + POST /invocations/{id}/cancel", "stream agent output as SSE", "bidirectional WebSocket streaming via /invocations_ws", "long-running invocations with polling", "publish an OpenAPI spec at /invocations/docs/openapi.json", "multi-turn conversations via agent_session_id grouping", "Foundry-hosted agent that needs platform-injected invocation/session IDs". DO NOT USE FOR: building OpenAI Responses API agents (use the `agentserver-responses` skill — the responses host adds the OpenAI wire protocol on top); OpenAI Chat Completions (different protocol, different host); raw `@task` resilient computation with no HTTP surface (use the `@task` primitive from `agentserver-resilient-tasks` skill directly); pure RPC microservices without per-invocation lifecycle (just use Starlette / FastAPI directly).'
---

# Agentserver Invocations (`InvocationAgentServerHost`) — Standalone Skill

> **Standalone document.** Copy this file into your project to give your
> AI coding agent (GitHub Copilot, etc.) the context it needs to build
> agents on the Azure AI Hosted Agents *invocations* protocol using
> `azure-ai-agentserver-invocations`. Pair it with the checked-in
> pre-release wheels (see *Packaging* below) — that's all your project
> needs to start.

The `InvocationAgentServerHost` class in
`azure.ai.agentserver.invocations` exposes the **invocations protocol**:
a free-form HTTP API
(`POST /invocations`, `GET /invocations/{id}`,
`POST /invocations/{id}/cancel`,
`GET /invocations/docs/openapi.json`) plus an optional
full-duplex WebSocket transport (`/invocations_ws`). You bring the
request / response wire format; the host owns the per-invocation
identity, the session-id resolution, the response headers, distributed
tracing, and the WebSocket lifecycle.

## When to use

Use `InvocationAgentServerHost` when **any** of these apply:

- You're shipping an agent as a **Foundry Hosted Agent container** that
  speaks the invocations protocol (the platform routes to
  `/invocations*` and expects the platform-injected
  `x-agent-invocation-id` header echoed back, the resolved
  `x-agent-session-id` returned, etc.).
- Your request / response shape is **free-form** (your own JSON, your
  own SSE event taxonomy) — not bound by the OpenAI Responses API
  contract.
- You need **WebSocket bidirectional streaming** for tool calling,
  back-pressure-sensitive flows, or full-duplex chat — registering
  `@app.ws_handler` adds `/invocations_ws` on the same host.
- You need **long-running invocations with polling**: POST returns
  immediately with an `invocation_id`, GET retrieves status or result,
  cancel terminates.
- You want to **publish an OpenAPI spec** at
  `/invocations/docs/openapi.json` for client discovery.
- You need **multi-turn conversations** grouped by
  `agent_session_id` (query param on POST, env var fallback, UUID
  default) — the resolved session ID is on
  `request.state.session_id` for handler-side state lookups.

## When NOT to use

`InvocationAgentServerHost` is intentionally narrow. Do **not** use it for:

- **OpenAI Responses API agents.** Use the `agentserver-responses`
  skill — `ResponsesAgentServerHost` adds the Responses-API wire
  protocol (`POST /responses`, builder events,
  `response.output_text.delta`, etc.) on top of the same core
  framework. Don't try to hand-roll Responses API on top of
  `InvocationAgentServerHost` — let the responses package own that
  contract.
- **OpenAI Chat Completions API agents.** Different protocol
  (`/chat/completions`); neither host implements it.
- **Raw `@task` resilient computation** with no HTTP surface. Use the
  `@task` decorator from `azure-ai-agentserver-core.tasks` directly.
  See the `agentserver-resilient-tasks` skill.
- **Pure RPC microservices** without per-invocation lifecycle
  (no invocation_id, no session_id, no platform header echoing).
  Use Starlette or FastAPI directly — the host's value is the
  per-invocation lifecycle it owns for you.

## Minimal pattern

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

app = InvocationAgentServerHost()


@app.invoke_handler  # POST /invocations  (required)
async def handle(request: Request) -> Response:
    data = await request.json()
    return JSONResponse({"greeting": f"Hello, {data['name']}!"})


if __name__ == "__main__":
    app.run()  # binds :8088 by default
```

## Long-running + polling

```python
import asyncio
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_tasks: dict[str, asyncio.Task] = {}
_results: dict[str, dict] = {}

app = InvocationAgentServerHost()


@app.invoke_handler
async def start(request: Request) -> Response:
    invocation_id = request.state.invocation_id   # framework-stamped
    payload = await request.json()
    _tasks[invocation_id] = asyncio.create_task(do_work(invocation_id, payload))
    return JSONResponse({"invocation_id": invocation_id, "status": "running"}, status_code=202)


@app.get_invocation_handler                       # GET /invocations/{id}
async def get_status(request: Request) -> Response:
    invocation_id = request.state.invocation_id
    if invocation_id in _results:
        return JSONResponse(_results[invocation_id])
    return JSONResponse({"invocation_id": invocation_id, "status": "running"})


@app.cancel_invocation_handler                    # POST /invocations/{id}/cancel
async def cancel(request: Request) -> Response:
    invocation_id = request.state.invocation_id
    task = _tasks.pop(invocation_id, None)
    if task is None:
        return JSONResponse({"error": "not_found"}, status_code=404)
    task.cancel()
    return JSONResponse({"invocation_id": invocation_id, "status": "cancelled"})
```

## SSE streaming

```python
import json
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

app = InvocationAgentServerHost()


@app.invoke_handler
async def stream(request: Request) -> Response:
    async def generate():
        for word in ("Hello", " ", "world", "!"):
            yield f"data: {json.dumps({'delta': word})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

For resilient-streaming patterns where the producer (inside `@task`)
fans out to N HTTP subscribers via SSE, with replay + reconnect, see
the [`agentserver-streaming` skill](streaming-skill.md).

## WebSocket bidirectional

```python
from starlette.websockets import WebSocket

@app.ws_handler  # /invocations_ws (full-duplex; protocol = invocations_ws)
async def ws(websocket: WebSocket) -> None:
    async for message in websocket.iter_text():
        await websocket.send_text(f"echo: {message}")
```

## Handler state (set by the framework)

The host populates these on `request.state` before dispatching:

| Attribute | Endpoints | Source |
|---|---|---|
| `request.state.invocation_id` | invoke / get / cancel | `x-agent-invocation-id` header (platform-injected when hosted) → generated UUID |
| `request.state.session_id` | invoke / get / cancel | `agent_session_id` query param (invoke only, per spec) → `FOUNDRY_AGENT_SESSION_ID` env var → generated UUID (invoke only) |
| `request.state.user_isolation_key` | invoke | `x-agent-user-isolation-key` header |
| `request.state.chat_isolation_key` | invoke | `x-agent-chat-isolation-key` header |

Per the [invocation protocol spec](https://github.com/Azure/foundrysdk_specs/blob/main/specs/hosted-agents/container-spec/docs/invocation-protocol-spec.md),
GET and cancel have **no platform-defined query parameters** — the
session is implicit (env-var sourced). The framework resolves it from
`FOUNDRY_AGENT_SESSION_ID` and stamps it on
`request.state.session_id` for your handler regardless.

## Composing with the resilient primitive

Pairing `InvocationAgentServerHost` with the `@task` primitive (see
the [`agentserver-resilient-tasks`](tasks-skill.md) skill) is the
canonical pattern for crash-resilient hosted agents:

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.core.tasks import multi_turn_task, TaskContext

app = InvocationAgentServerHost()


@multi_turn_task(steerable=True)  # crash-resilient + steerable resilient primitive
async def research(ctx: TaskContext[dict]) -> dict:
    # ctx.input is one turn's payload; ctx.entry_mode tells you whether
    # this is a fresh turn, a resumed turn, or a crash-recovered re-entry.
    ...
    return result


@app.invoke_handler
async def handle(request: Request) -> Response:
    payload = await request.json()
    task_id = request.state.session_id   # one resilient task per session
    input_id = request.state.invocation_id  # per-turn id
    await research.start(task_id=task_id, input=payload, input_id=input_id)
    return JSONResponse({"status": "started", "invocation_id": input_id}, status_code=202)


@app.cancel_invocation_handler
async def cancel(request: Request) -> Response:
    task_id = request.state.session_id
    input_id = request.state.invocation_id
    run = await research.get_active_run(task_id, input_id)
    if run is None:
        return JSONResponse({"status": "not_found"}, status_code=404)
    await run.cancel()
    return JSONResponse({"status": "cancelled"})
```

The [`resilient-agent-demo`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient-agent-demo)
sample wires this end-to-end with SSE streaming, file-backed task
storage, and crash recovery.

## Hosted vs local

Auto-detected via `FOUNDRY_HOSTING_ENVIRONMENT`:

- **Hosted** (Foundry Hosted Agent platform): platform injects
  `x-agent-invocation-id`, `x-agent-user-isolation-key`,
  `x-agent-chat-isolation-key`, `FOUNDRY_AGENT_SESSION_ID` env var,
  routes `/invocations*` to your container, terminates `/invocations_ws`
  WebSockets, exposes the OpenAPI spec from
  `/invocations/docs/openapi.json` for client discovery.
- **Local dev**: framework generates IDs as UUIDs when not supplied;
  isolation keys are empty; session id falls through to UUID; the host
  binds `:8088` by default.

## Packaging — private preview wheels

The current invocations host with the cancel/get session-id propagation
fix (per the invocation protocol spec) and the resilient-task integration
ships only via the pre-release wheels checked into this branch. The
regular PyPI version of `azure-ai-agentserver-invocations` predates
these.

Consume the checked-in wheels per:

- Wheel directory + README: [`sdk/agentserver/wheels/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/wheels)

The wheels bundle all three preview packages (`core`,
`invocations`, `responses`) so a single
`pip install /path/to/wheels/*.whl` gives you the full surface.

## Authoritative references

| Topic | Link |
|---|---|
| **Package README** (decorator catalog, request/response headers, distributed tracing, WebSocket lifecycle) | [`README.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-invocations/README.md) |
| **Invocation protocol spec** (the wire contract — POST/GET/cancel routes, headers, query params, session-id resolution, response headers, OpenAPI spec endpoint, error format) | [`invocation-protocol-spec.md`](https://github.com/Azure/foundrysdk_specs/blob/main/specs/hosted-agents/container-spec/docs/invocation-protocol-spec.md) |
| Minimal echo agent | [`samples/simple_invoke_agent/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/simple_invoke_agent) |
| Long-running + polling | [`samples/async_invoke_agent/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/async_invoke_agent) |
| SSE streaming | [`samples/streaming_invoke_agent/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/streaming_invoke_agent) |
| WebSocket (echo + bidirectional) | [`samples/ws_invoke_agent/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/ws_invoke_agent), [`samples/ws_bidirectional_streaming_agent/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/ws_bidirectional_streaming_agent) |
| Multi-turn (suspend / resume on top of `@multi_turn_task`) | [`samples/multiturn_invoke_agent/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/multiturn_invoke_agent), [`samples/resilient_multiturn/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient_multiturn) |
| End-to-end **long-running + crash + steer** demo (Foundry hosted) | [`samples/resilient-agent-demo/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient-agent-demo) |
| Companion: resilient-task primitive skill (the `@task` underneath) | [`tasks-skill.md`](tasks-skill.md) |
| Companion: streaming registry skill (producer/subscriber fan-out + replay) | [`streaming-skill.md`](streaming-skill.md) |
| Companion: responses-API host skill (when you need OpenAI Responses API wire format instead) | [`responses-skill.md`](responses-skill.md) |

Read the package README first — it covers every decorator, the full
request/response header table, distributed tracing semantics, and the
WebSocket lifecycle (subprotocol negotiation, ping/pong, close codes).
The protocol spec is the canonical wire contract. The samples ground
the API in working code.

## Decision shortcuts

| Need | Use `InvocationAgentServerHost`? | Why |
|---|---|---|
| Free-form HTTP agent on Foundry Hosted Agents | ✅ | This is the host. |
| WebSocket bidirectional streaming | ✅ | Register `@app.ws_handler`; no second package needed. |
| Long-running invocation with polling + cancel | ✅ | Register `@app.invoke_handler` + `@app.get_invocation_handler` + `@app.cancel_invocation_handler`. |
| Publish OpenAPI spec for client discovery | ✅ | Pass `openapi_spec={...}` to the constructor. |
| OpenAI Responses API endpoint | ❌ | Use the `agentserver-responses` skill. |
| OpenAI Chat Completions endpoint | ❌ | Different protocol — different host. |
| Server-to-server background job, no HTTP | ❌ | Use the `@task` primitive directly. |
| Pure RPC, no invocation_id / session_id / platform headers | ❌ | Use Starlette / FastAPI directly. |
| Crash-resilient long-running agent | ⚠️ | Compose with `@task` / `@multi_turn_task` — see the "Composing with the resilient primitive" section. |
