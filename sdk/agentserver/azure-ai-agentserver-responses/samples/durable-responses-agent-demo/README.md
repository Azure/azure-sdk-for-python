# Durable Responses Research Agent — Demo

A `ResponsesAgentServerHost`-decorated long-running research agent
that demonstrates four platform capabilities of the Azure AI Hosted
Agent + the `azure-ai-agentserver-responses` package:

1. **Long-running responses run uninterrupted past the platform's
   sandbox-eviction window.** The underlying `@multi_turn_task`
   primitive's PATCH lease-renewal cycle (every ~30s, half of the 60s
   lease) refreshes the platform's sandbox idle-reclaim timer. The
   demo runs for several minutes with **zero client-side keepalive
   ingress** and the sandbox stays warm the whole time.

2. **Recovery from container crashes.** When the agent container
   dies (intentional crash or OOM), the platform's nanny worker
   brings it back within ~1 min **without any new client ingress**.
   The durable response automatically resumes with
   `context.is_recovery is True`, reads the last completed phase from
   `context.durable_metadata`, and re-emits the snapshot reset on
   `response.in_progress`. User-visible: any reconnect attempt picks
   up the recovered run.

3. **Steering.** POSTing a follow-up turn (with `previous_response_id`
   pointing at the still-running response) queues the input as a
   steering input. The agent observes
   `cancellation_signal.is_set() and context.pending_input_count > 0`,
   winds down at the next phase boundary, and re-enters with
   `context.is_steered_turn is True` carrying the new input.

4. **Operator cancel.** `POST /responses/{id}/cancel` fires
   `cancellation_signal` + stamps `context.client_cancelled`; the
   framework forces the response to `status="cancelled"` regardless
   of what the handler emits (B11 contract).

## Compared to the invocations demo

This demo is intentionally **much thinner** than its sibling
`durable-agent-demo` (which is built on the invocations protocol).
The reason: the responses package wraps the OpenAI Responses API
wire protocol, so the framework owns everything the invocations demo
had to wire by hand:

| Concern | Invocations demo | Responses demo |
|---|---|---|
| Wire protocol | Custom JSON shape; handler writes the SSE format | OpenAI Responses API SSE event taxonomy; emitted via `ResponseEventStream` builders |
| Cancellation route | Custom `@app.cancel_invocation_handler` that looks up the task and calls `run.cancel()` | Built-in `POST /responses/{id}/cancel` route handled by the framework |
| Stream replay route | Custom `@app.get_invocation_handler` that subscribes to the per-invocation stream | Built-in `GET /responses/{id}?stream=true&starting_after=N` |
| Durability + steering | Compose `@multi_turn_task(steerable=True)` directly; map `task_id`/`input_id` to session/invocation | Opt-in via `ResponsesServerOptions(durable_background=True, steerable_conversations=True)` — framework handles the rest |
| Recovery surface | Read `ctx.entry_mode == "recovered"` + `ctx.metadata` | Read `context.is_recovery` + `context.durable_metadata`; same recovery primitive underneath |

`main.py` here is ~300 lines (mostly the phase-streaming logic);
`agent.py` + `app.py` for the invocations demo is ~700 lines.

What the agent actually does: 5 logical research phases on whatever
topic the caller supplies. Each phase produces ~200 tokens via a real
`gpt-4.1-mini` call (streamed token-by-token through
`response.output_text.delta` events). The handler checkpoints to
`context.durable_metadata` after each phase completes — a crash
mid-phase recovers at the next un-finished phase (worst case: the
one that was actively streaming is replayed).

Between phases the agent sleeps for `INTER_PHASE_COOLDOWN_SEC` (30s
default in the hosted defaults) so a single demo run spans the
sandbox-eviction window and exercises the lease keep-alive path.

## Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- `azd` AI agents extension: `azd extension install azure.ai.agents`

## Deploy

```bash
# 1. Stage the checked-in agentserver preview wheels into the docker
#    build context (build.sh copies sdk/agentserver/wheels/*.whl into
#    a per-sample gitignored staging dir — no compilation, no PyPI fetch).
./build.sh

# 2. Login + deploy.
azd auth login
azd up
```

The deploy provisions infra + ships the container image and prints
the responses endpoint. `demo-client.sh` points at the canonical
`e2e-tests-westus2` deployment by default — set the `ENDPOINT=` env
var when invoking, or edit the script, if you deployed elsewhere.

> The `azure-ai-agentserver-responses` package's durable + steerable
> surface is in **private preview** and is not on PyPI yet. It ships
> as the pre-release wheels checked into
> [`sdk/agentserver/wheels/`](../../../../wheels). See
> [`sdk/agentserver/wheels/README.md`](../../../../wheels/README.md)
> for the consumption workflow in your own project.

## demo-client.sh — command reference

| Command | What it does |
|---|---|
| `./demo-client.sh start "<topic>"` | Dispatches `POST /responses` with `{stream: true, store: true, background: true}` and the topic, then attaches to the SSE stream via `GET /responses/{id}?stream=true`. Writes the new `response_id` to `.demo-session`. |
| `./demo-client.sh stream` | Reuses the `response_id` + `last_sequence_number` from `.demo-session` and reattaches via `GET /responses/{id}?stream=true&starting_after=N`. The server skips events you've already seen. |
| `./demo-client.sh steer "<topic>"` | POSTs a new response with `previous_response_id` pointing at the active one. With `steerable_conversations=True` the framework queues it as a steering input on the active conversation; the agent winds down the current turn at its next phase boundary and re-enters with the new topic. |
| `./demo-client.sh cancel` | `POST /responses/{id}/cancel` on the active response. The framework fires `cancellation_signal` + stamps `context.client_cancelled`; the response transitions to `status=cancelled`. |
| `./demo-client.sh crash` | POSTs `{"input": "crash"}`. The agent (gated by `DEMO_MODE=1`) calls `os._exit(137)`. The platform's nanny worker brings the container back within ~1 min; `./demo-client.sh stream` after will pick up the recovered run. |
| `./demo-client.sh delete` | `DELETE /responses/{id}`. Cleans up the persisted snapshot + per-response stream. |
| `./demo-client.sh status` | Prints the local session state (`RESPONSE_ID`, `LAST_SEQUENCE_NUMBER`) + the server's current snapshot of the response. |
| `./demo-client.sh logs` | Tails the agent container's stdout/stderr via `azd ai agent monitor --follow`. |
| `./demo-client.sh reset` | Deletes `.demo-session`. The next `start` allocates a fresh response. |

### Session-state lifecycle

The client tracks one active response per `.demo-session` file:

```
./demo-client.sh start "<topic>"
        │
        ├─ RESPONSE_ID          = caresp_...   ← assigned by the platform
        ├─ LAST_SEQUENCE_NUMBER = 0            ← bumps as events stream
        └─ written to .demo-session
                │
                ▼  these commands REUSE the same response_id:
        ./demo-client.sh stream     (resumes from LAST_SEQUENCE_NUMBER)
        ./demo-client.sh steer "<new topic>"  (creates a new response steered on the prior)
        ./demo-client.sh crash
        ./demo-client.sh cancel
        ./demo-client.sh delete
        ./demo-client.sh logs
        ./demo-client.sh status

To start over with a brand-new response:
        ./demo-client.sh reset            # clears .demo-session
        ./demo-client.sh start "<topic>"
```

`steer` is the only command that bumps `RESPONSE_ID` — the steered
turn is technically a new response (with a new `response_id`) whose
`previous_response_id` points at the prior one. The client tracks the
prior id in `PREV_RESPONSE_ID` for convenience.

## Local iteration

You can run the agent locally without `azd`:

```bash
export FOUNDRY_PROJECT_ENDPOINT="https://<account>.services.ai.azure.com/api/projects/<project>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1-mini"
export DEMO_MODE=1
export NUM_PHASES=3                # smaller for local iteration
export INTER_PHASE_COOLDOWN_SEC=2

# Install the local wheels (or pip install -e the responses package).
pip install ../../../wheels/*.whl
pip install -r src/durable-responses-agent-demo/requirements.txt

# Run.
python src/durable-responses-agent-demo/main.py
```

Then drive it with curl against `http://localhost:8088/responses`
(no auth needed locally; `demo-client.sh` is hosted-aware and expects
the `Authorization: Bearer ...` header).

## Configuration

All knobs are env vars read at startup. Hosted defaults are tuned for
the demo's "span the eviction window" narrative; override for local
iteration.

| Var | Default | Description |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | (required) | Foundry project endpoint for the upstream `gpt-4.1-mini` calls. Platform-injected in hosted; set manually locally. |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | `gpt-4.1-mini` | Responses-API model deployment name. |
| `NUM_PHASES` | `5` | Logical research phases per run. |
| `TARGET_OUTPUT_TOKENS` | `200` | `max_output_tokens` per phase's upstream call. |
| `INTER_PHASE_COOLDOWN_SEC` | `30` | Sleep between phases. Set to `0` for local iteration. |
| `DEMO_MODE` | unset | When `1`, the input `"crash"` triggers `os._exit(137)`. Production deployments should leave this off. |
