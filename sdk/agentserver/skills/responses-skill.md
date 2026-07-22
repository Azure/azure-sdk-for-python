---
name: agentserver-responses
description: 'Build OpenAI Responses API-compatible agents using the `ResponsesAgentServerHost` from `azure-ai-agentserver-responses`. WHEN: "expose my agent as an OpenAI Responses API endpoint", "implement /responses POST + GET + cancel + delete", "stream agent output as Responses SSE events (response.created, response.in_progress, response.output_text.delta, response.completed, etc.)", "emit Responses output items (messages, function calls, reasoning, structured outputs)", "background responses with SSE replay", "resilient + crash-recoverable Responses API agent", "steerable Responses API multi-turn conversations (queue a new turn while one is running)", "Foundry-hosted Responses-API agent". DO NOT USE FOR: building agents on a different wire protocol (the invocations protocol — use `agentserver-resilient-tasks` + `agentserver-streaming` skills; the OpenAI Chat Completions API — different host; raw `@task` resilient computation that does NOT need a Responses-API HTTP surface). PRIVATE PREVIEW: ships only via pre-release wheels checked into this branch (see references); the regular PyPI version of `azure-ai-agentserver-responses` predates this surface and does not include `resilient_background` / `steerable_conversations` / the per-request primitive dispatch.'
---

# Agentserver Responses (`ResponsesAgentServerHost`) — Standalone Skill

> **Standalone document.** Copy this file into your project to give your
> AI coding agent (GitHub Copilot, etc.) the context it needs to build
> OpenAI Responses API-compatible agents on top of
> `azure-ai-agentserver-responses`. Pair it with the checked-in
> pre-release wheels (see *Packaging* below) — that's all your project
> needs to start.

The `ResponsesAgentServerHost` class in
`azure.ai.agentserver.responses` exposes the OpenAI Responses API as an
HTTP host. You register a single `@app.response_handler`-decorated
coroutine; the framework owns the wire protocol (SSE event ordering,
terminal-status invariants, background-mode lifecycle, GET-after-completion
snapshots, /cancel semantics, /delete cleanup, the resilient +
steerable lifecycle when opted in).

## When to use

Use `ResponsesAgentServerHost` when **any** of these apply:

- You need to expose an agent over the OpenAI Responses API wire format
  so existing Responses-API clients (the `openai` Python SDK's
  `responses.create`, raw HTTP callers reading `text/event-stream`,
  etc.) work without modification.
- You want background responses with SSE replay — POST returns
  immediately, the handler runs in the background, and a subsequent
  GET with `?stream=true` replays / live-streams the per-response
  event log including a `?starting_after=N` reconnect cursor (the
  Responses API's cursor convention — `N` is the
  `sequence_number` of the last event the client received).
- You need crash-recoverable agents (opt-in via
  `ResponsesServerOptions(resilient_background=True)`) — backed by the
  `@task` primitive under the covers, but you write a normal
  handler instead of touching the resilient primitive directly.
- You need steerable multi-turn conversations (opt-in via
  `ResponsesServerOptions(steerable_conversations=True)`) — a new turn
  posted on an in-flight conversation cooperatively winds down the
  current turn at its next checkpoint and re-enters with the new input
  on a fresh handler invocation, linked in a stable
  `conversation_chain_id`.

## When NOT to use

`ResponsesAgentServerHost` is intentionally narrow. Do **not** use it for:

- **Agents that speak a different wire protocol.** If you're building
  for the invocations protocol (free-form request/response shape, no
  OpenAI compatibility), use the `agentserver-resilient-tasks` +
  `agentserver-streaming` skills directly — that gives you the resilient
  primitive + HTTP wrapper without the Responses-API surface.
- **OpenAI Chat Completions API agents.** Different protocol; this
  host implements Responses (`/responses`), not Chat Completions
  (`/chat/completions`).
- **Raw `@task` resilient computation** with no HTTP surface. Use the
  `@task` decorator from `azure-ai-agentserver-core.tasks` directly.
- **Custom HTTP paths.** `ResponsesAgentServerHost` owns
  `/responses*`. If you need additional endpoints, compose via
  Starlette mounting or co-host another `AgentServerHost` subclass
  via cooperative inheritance.

## Minimal pattern

```python
import asyncio
from azure.ai.agentserver.responses import (
    ResponsesAgentServerHost,
    ResponseContext,
    TextResponse,
    CreateResponse,
)

app = ResponsesAgentServerHost()


# Handlers are async with exactly 3 positional parameters.
# The 3rd arg `cancellation_signal` is an asyncio.Event the framework
# fires on /cancel, non-bg POST disconnect, or steering pressure.
# `context.shutdown` is a separate Event for server shutdown — observe
# each independently.
@app.response_handler
async def my_handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    # Simplest case — let the framework own the full SSE lifecycle:
    return TextResponse(context, request, text="Hello, world!")


if __name__ == "__main__":
    app.run()  # binds :8088 by default
```

For full event control (function calls, multiple output items,
streaming partials, structured outputs), use `ResponseEventStream` and
yield events directly:

```python
from azure.ai.agentserver.responses import ResponseEventStream

@app.response_handler
async def my_handler(request, context, cancellation_signal):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    msg = stream.add_output_item_message()
    yield msg.emit_added()
    text = msg.add_text_content()
    yield text.emit_added()
    async for tok in upstream_llm():
        if cancellation_signal.is_set():
            break
        yield text.emit_delta(tok)
    yield text.emit_text_done(accumulated_text)
    yield text.emit_done()
    yield msg.emit_done()
    yield stream.emit_completed()
```

## Cancel + shutdown observation

Two **distinct** surfaces, two **distinct** handler responses:

| Surface | Fires on | Handler should |
|---|---|---|
| `cancellation_signal` (3rd handler arg, `asyncio.Event`) | `/cancel` API call, non-bg POST disconnect, steering pressure | break work loop → close builders → emit `response.completed` (the framework overrides to `response.cancelled` if `context.client_cancelled is True`) |
| `context.shutdown` (`asyncio.Event`) | server shutdown (SIGTERM, graceful drain) | `return await context.exit_for_recovery()` (resilient + bg) or emit a quick terminal (others) |

Shutdown does NOT fire the cancellation signal. Handlers that care
about both must observe each independently.

To distinguish steering from a client cancel inside the cancel branch:
```python
if cancellation_signal.is_set() and context.pending_input_count > 0:
    # Steering pressure — a new turn is queued. Emit completed with
    # whatever output is persisted; the framework re-enters with
    # the new input as ctx.input.
    yield stream.emit_completed()
    return
```

## Resilient + steerable (opt-in)

```python
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions

app = ResponsesAgentServerHost(options=ResponsesServerOptions(
    resilient_background=True,        # background responses survive process crashes
    steerable_conversations=True,   # accept new turns on in-flight conversations
))
```

When opted in, the handler also sees:

| Field | Meaning |
|---|---|
| `context.is_recovery: bool` | `True` on a crash-recovered re-entry |
| `context.is_steered_turn: bool` | `True` on the drain re-entry that follows a steering input |
| `context.pending_input_count: int` | Live count of queued steering inputs |
| `context.conversation_chain_metadata: ConversationChainMetadataNamespace` | `MutableMapping` for handler-managed checkpoint state (small — watermarks, dedup tokens, NOT full conversation history). `await context.conversation_chain_metadata.flush()` for at-most-once side-effect fencing before an upstream call with observable side effects |
| `await context.exit_for_recovery()` | Recovery primitive — `return await context.exit_for_recovery()` to leave the response `in_progress` so the next-lifetime recovery scanner picks it up |

## Hosted vs local

Both modes are auto-detected via `FOUNDRY_HOSTING_ENVIRONMENT`:

- **Hosted** (Foundry Hosted Agent platform): response store auto-binds
  to the Foundry hosted responses storage API; stream replay uses
  file-backed storage under `${AGENTSERVER_STATE_ROOT}/streams/`;
  resilient task store uses the Foundry hosted task storage API; lease
  renewal extends the sandbox idle-reclaim timer past the eviction
  window.
- **Local dev**: response store defaults to file-backed under
  `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/responses/`; stream replay
  uses in-memory (resilient_background=False) or file-backed
  (resilient_background=True) under
  `${AGENTSERVER_STATE_ROOT}/streams/`; resilient task store is
  file-backed under `${AGENTSERVER_STATE_ROOT}/tasks/`.

Operator override: `AGENTSERVER_TASKS_BACKEND=local|hosted` forces
the task provider regardless of hosting detection. Useful for debugging
hosted-only scenarios on a local workstation.

## Packaging — private preview wheels

The PyPI version of `azure-ai-agentserver-responses` predates the
resilient + steerable surface. **The current Responses API host with
crash recovery, steering, and the per-request primitive dispatch
ships only via the pre-release wheels checked into this branch.**

Consume the checked-in wheels per:

- Wheel directory + README: [`sdk/agentserver/wheels/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/wheels)

The wheels bundle all three preview packages (`core`,
`invocations`, `responses`) so a single
`pip install /path/to/wheels/*.whl` gives you the full surface.

## Authoritative references

| Topic | Link |
|---|---|
| **Handler implementation guide** (full patterns, builder API, terminal-status rules, cancellation matrix) | [`docs/handler-implementation-guide.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md) |
| **Resilient responses developer guide** (recovery contract, watermark patterns, upstream-framework integration, the `is_recovery` / `is_steered_turn` / `pending_input_count` surface) | [`docs/resilient-responses-developer-guide.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/resilient-responses-developer-guide.md) |
| **Source-of-truth resilience spec** (language-agnostic protocol contract) | [`docs/responses-resilience-spec.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/responses-resilience-spec.md) |
| Minimal handler examples (TextResponse, ResponseEventStream, function calling, multi-output, streaming upstream) | [`samples/sample_01_getting_started.py`..`sample_16_structured_outputs.py`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples) |
| Resilient + steerable patterns (Copilot SDK, three-phase streaming with watermarks, steering drain, LangGraph integration, multi-turn) | [`samples/sample_18_resilient_copilot.py`..`sample_22_resilient_multiturn.py`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-responses/samples) |
| Companion: resilient-task primitive skill (the `@task` underneath) | [`tasks-skill.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/skills/tasks-skill.md) |
| Companion: streaming registry skill (the `streams` registry underneath) | [`streaming-skill.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/skills/streaming-skill.md) |

Read the handler implementation guide first — it covers the full
event taxonomy (every SSE event type the host accepts, the builder
methods for each, terminal-status invariants), the cancellation cause
matrix, and the recovery primitive shape. The samples ground the API
in working code.

## Decision shortcuts

| Need | Use `ResponsesAgentServerHost`? | Why |
|---|---|---|
| Expose agent as OpenAI Responses API endpoint | ✅ | This is the host. |
| Background response with SSE replay (POST + GET ?stream=true) | ✅ | Framework owns the per-response stream registry + cursor. |
| Multi-turn chat that survives container restart | ✅ | Opt into `resilient_background=True` + `steerable_conversations=True`. |
| Steerable long generation (user can change topic mid-run) | ✅ | Opt into `steerable_conversations=True`; observe `cancellation_signal` + `pending_input_count`. |
| OpenAI Chat Completions API endpoint | ❌ | Different protocol — use a different host. |
| Free-form invocations-protocol agent | ❌ | Use the `agentserver-resilient-tasks` + `agentserver-streaming` skills directly. |
| Server-to-server background job with no HTTP surface | ❌ | Use the `@task` primitive directly. |
| Persist conversation history in `context.conversation_chain_metadata` | ❌ | Wrong — `conversation_chain_metadata` is for small watermarks. Use your own DB or framework store (LangGraph SqliteSaver, etc.) for content. |
