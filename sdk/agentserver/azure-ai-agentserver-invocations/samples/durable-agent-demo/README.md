# Durable Research Agent — Demo

A `@task`-decorated long-running research agent that demonstrates two
platform capabilities of the Azure AI Hosted Agent + durable-task primitive:

1. **Recovery from container reclaims / crashes.** When the agent container
   dies (intentional crash, OOM, or the platform's ~15-min idle reclaim),
   the platform brings it back on the next inbound request (~10 sec
   measured) and the durable task automatically resumes from its last
   checkpoint (`ctx.entry_mode == "recovered"`). The user-visible
   experience: any reconnect attempt seamlessly continues the run, no
   matter how long the container was down.

2. **Steering.** Sending a new turn on a running steerable task queues
   the input and signals cooperative cancel. The agent winds down the
   current turn at the next checkpoint boundary and re-enters with the
   queued input as a fresh turn (with the prior topic surfaced for the
   viewer to see).

What the agent actually does: 15 logical research phases on whatever
topic the caller supplies. Each phase runs a small agent loop
(research → critique → refine → synthesize) against `gpt-4.1-mini`,
streaming every token to the consumer. After each phase the handler
checkpoints to `ctx.metadata` and flushes — so a crash mid-run picks up
at the next un-completed phase, and a steerer that arrives mid-phase
causes the handler to wind down at the *next* phase boundary, not
abruptly. Defaults target a ~45-min wall-time run; env vars dial it
shorter for development.

> **Note on long-running tasks.** Empirically on the current platform
> deployment, the sandbox is reclaimed ~15 min after the *last
> user-facing ingress* — even when a `@task` handler is still executing.
> The framework's internal lease-renewal cycle goes to the platform's
> task-store API, not to the agent container's `/readiness`, so it does
> not currently extend the idle window. A 45-min run therefore reaches
> completion by being **reclaimed and recovered repeatedly** rather than
> running uninterrupted — which is exactly what `@task` is for.

## Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- `azd` AI agents extension: `azd extension install azure.ai.agents`

## Deploy

```bash
# 1. Build local wheels (so the Docker image carries the pre-release SDK)
./build.sh

# 2. Login + deploy
azd auth login
azd up
```

The deploy provisions infra + ships the container image and prints the
invocations endpoint. `demo-client.sh` already points at the canonical
`e2e-tests-westus2` deployment — edit `ENDPOINT=` near the top of
`demo-client.sh` if you deployed elsewhere.

## demo-client.sh — command reference

The client is a bash CLI. Each command operates on a single session
tracked locally in `.demo-session`. Run from this directory:

| Command | What it does |
|---|---|
| `./demo-client.sh start "<topic>"` | **Allocates a new session id** (UUID), writes it to `.demo-session`, dispatches `POST /invocations` with the topic, then attaches to the SSE stream. |
| `./demo-client.sh stream` | Reuses the session + invocation from `.demo-session` and (re)attaches to the SSE stream. Passes `?last_event_id=N` so the server skips events you've already seen. |
| `./demo-client.sh steer "<topic>"` | Reuses the current session and sends a new `POST /invocations` with the new topic. If the run is still active the framework queues this as a steering input; the agent winds down at the next checkpoint boundary and re-enters on the new topic. |
| `./demo-client.sh cancel` | `POST /invocations/{id}/cancel` on the current invocation. The handler observes `ctx.cancel.is_set()` and winds down cooperatively. |
| `./demo-client.sh crash` | Sends `POST /invocations` with `{"message": "crash"}`. The agent (gated by `DEMO_MODE=1`) calls `os._exit(137)`. The container stays down until the next ingress; `./demo-client.sh stream` is the easiest way to bring it back. |
| `./demo-client.sh status` | Prints the local `SESSION_ID`, `INV_ID`, and `LAST_EVENT_ID` from `.demo-session`. Useful when you forget which session you're on. |
| `./demo-client.sh logs` | Tails the agent container's stdout/stderr via `azd ai agent monitor --session-id <current> --follow`. |
| `./demo-client.sh reset` | Deletes `.demo-session`. The next `start` will allocate a fresh session id. |

### Session-id lifecycle

There is exactly **one active session per `.demo-session` file**:

```
./demo-client.sh start "<topic>"
        │
        ├─ SESSION_ID = demo-<uuid>     ← newly allocated by the client
        ├─ INV_ID    = inv_<...>        ← assigned by the platform on POST
        └─ written to .demo-session
                │
                ▼  these commands REUSE the same session id:
        ./demo-client.sh stream
        ./demo-client.sh steer "<new topic>"
        ./demo-client.sh crash
        ./demo-client.sh cancel
        ./demo-client.sh logs
        ./demo-client.sh status

To switch to a NEW session id:
        ./demo-client.sh reset            # clears .demo-session
        ./demo-client.sh start "<topic>"  # allocates a fresh demo-<uuid>
```

### Inspecting container logs

`./demo-client.sh logs` opens a follow tail on the agent container's
stdout/stderr for the current session. Useful framework log lines:

- `TaskManager starting (owner=..., instance=worker-N-..., hosted=True)` —
  a fresh container booted.
- `Reclaimed stale task <task_id>` / `Recovered task <task_id> is now active` —
  durable recovery picked up where the previous lifetime left off.
- `Inbound GET /readiness completed with status 200` — the platform's
  container health probe (a good signal that the container just came up).
- `HTTP Request: POST .../openai/v1/responses "HTTP/1.1 200 OK"` — each
  LLM call the agent makes.
- `Task <task_id> suspended` / `Steering drain: task <task_id> drained next input` —
  cooperative wind-down + steering re-entry.

For one-shot queries, invoke `azd ai agent monitor` directly:

```bash
SESSION_ID=$(grep SESSION_ID .demo-session | cut -d'"' -f2)
azd ai agent monitor --session-id "$SESSION_ID" --tail 100
azd ai agent monitor --session-id "$SESSION_ID" --type system   # container start/stop events
```

## Three demo workflows

### A. Long-running run + reclaim-and-recover (~45 min wall time)

```bash
# t = 0:00
./demo-client.sh start "the future of nuclear fusion"
# A few phases stream. Note server_time_utc + server_uptime_sec on each event.

# t = 5:00
# Close the terminal. Make zero ingress for the next 15-20 min.

# t = 20:00 — open a new terminal:
./demo-client.sh stream
# The container was reclaimed during your dead window. Your reconnect
# triggers the platform to bring it back (~10 sec). You'll see:
#   🔁 Recovered from crash   resuming from phase N/15
#   server_uptime_sec=1.3    ← fresh container; uptime started over
# Stream continues from phase N. Repeat as many times as needed; each
# reconnect brings the container back and resumes from the latest
# checkpoint.
```

### B. Explicit crash + recovery (same story, faster to demonstrate)

```bash
# Terminal 1: start a run and leave it streaming.
./demo-client.sh start "fusion energy research priorities"
# Wait until 3-4 phases have completed.

# Terminal 2: force a crash.
./demo-client.sh crash
# Server returns 202 then exits. Terminal 1's stream disconnects.

# Wait as long as you like — the container stays down with NO ingress.
# When you want to reconnect:
./demo-client.sh stream
# Container brought back in ~10 sec:
#   🔁 Recovered from crash   resuming from phase 4/15
#   server_uptime_sec=2.4    ← fresh container
# Stream picks up at phase 4, NOT phase 1.
```

### C. Steering (mid-run topic switch)

```bash
# Terminal 1:
./demo-client.sh start "deep learning interpretability"
# Wait until phase 2 starts streaming.

# Terminal 2:
./demo-client.sh steer "alignment of frontier models"
# Server queues the new input; the running turn keeps going until the
# next phase boundary.

# Terminal 1 (within ~3 min, at the next phase boundary):
#   ↓ Winding down   cause=steering   completed=2/15
#   ▶ Run start    topic=alignment of frontier models
#                  (steered from prior topic: deep learning interpretability)
#   ▶ Phase 1/15 — Decomposing topic into focused research questions
#   ...
```

## Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Foundry Hosted-Agent Sandbox (platform-managed lifecycle)                │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  python app.py        (InvocationAgentServerHost on :8088)          │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │  POST /invocations                                            │  │  │
│  │  │     └─ {"message": "<topic>"} →                               │  │  │
│  │  │           deep_research.start(task_id=session_id, input=...)  │  │  │
│  │  │        on an active steerable task: queued as a steering input│  │  │
│  │  │     └─ {"message": "crash"} (DEMO_MODE=1 only) → os._exit     │  │  │
│  │  │                                                               │  │  │
│  │  │  GET /invocations/{id}?last_event_id=N                        │  │  │
│  │  │     └─ live SSE from get_active_run(task_id), else file replay│  │  │
│  │  │                                                               │  │  │
│  │  │  POST /invocations/{id}/cancel                                │  │  │
│  │  │     └─ run.cancel()                                           │  │  │
│  │  │                                                               │  │  │
│  │  │  GET  /readiness  (called by platform health probe at startup)│  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                     │  │
│  │  deep_research  (agent.py)                                          │  │
│  │     @task(steerable=True, stream_handler_factory=file_stream_factory)│ │
│  │     loop 1..NUM_PHASES:                                             │  │
│  │        emit phase_start with server_time_utc + server_uptime_sec    │  │
│  │        run CALLS_PER_PHASE LLM sub-calls (research → critique → …)  │  │
│  │        ctx.metadata["completed_phases"] = i+1                       │  │
│  │        await ctx.metadata.flush()       ← crash-recovery boundary   │  │
│  │        emit phase_end                                               │  │
│  │        if ctx.cancel.is_set():                                      │  │
│  │           wind down → return await ctx.suspend(...)                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                              ▲          │
                              │          │  PATCH /api/projects/.../tasks/{id}
                              │          │  (framework lease renewal + checkpoint flush)
                              │          ▼
                ┌─────────────────────────────────────────┐
                │  Foundry control plane                  │
                │  ─ Task-storage API (lease, payload,    │
                │    metadata, checkpoint persistence)    │
                │  ─ Endpoint proxy: routes /invocations* │
                │    to the sandbox; brings the container │
                │    back up on next ingress when reclaimed│
                │  ─ Idle-reclaim timer (~15 min since    │
                │    last user-facing ingress)            │
                └─────────────────────────────────────────┘
```

Notable points:

- The container runs `python app.py` directly. There is **no
  application-level supervisor or auto-restart wrapper** — the previous
  versions of this demo needed one because the platform did not yet
  guarantee restart-on-ingress.
- `task_id == session_id`: one durable task per session. This is what
  routes a steering POST to the active task instead of starting a new one.
- The framework's lease-renewal loop talks to the **task-storage API**,
  not the agent's `/readiness`. The `/readiness` endpoint is hit only by
  the platform's startup health probe.
- When the platform reclaims (or the agent crashes) and ingress arrives
  later, the platform spins up a fresh container; the framework's
  recovery scan finds the stranded task and re-enters the handler with
  `ctx.entry_mode == "recovered"` and `ctx.metadata` populated from the
  last checkpoint.

## Environment variables

These are set in the Dockerfile and travel with the image. Override by
editing the Dockerfile and redeploying, or by setting them in
`azure.yaml` per-deployment.

| Variable | Default | Description |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | (required, set by platform) | Foundry project endpoint. |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | `gpt-4.1-mini` | Responses-API model deployment name. |
| `DEMO_MODE` | `1` (in the demo image) | Enables the `{"message": "crash"}` sentinel on `POST /invocations`. A production image would leave this off. |
| `NUM_PHASES` | `15` | Number of research phases. |
| `CALLS_PER_PHASE` | `4` | Sub-calls per phase (research, critique, refine, synthesize). |
| `TARGET_OUTPUT_TOKENS` | `1500` | Max tokens per LLM sub-call. |
| `INTRA_PHASE_COOLDOWN_SEC` | `10` | Seconds between sub-calls within a phase. |
| `INTER_PHASE_COOLDOWN_SEC` | `20` | Seconds between phases. |

For a **fast** development loop (~2 min total instead of ~45 min), add
to the Dockerfile and redeploy:

```dockerfile
ENV NUM_PHASES=3
ENV CALLS_PER_PHASE=1
ENV INTRA_PHASE_COOLDOWN_SEC=2
ENV INTER_PHASE_COOLDOWN_SEC=2
ENV TARGET_OUTPUT_TOKENS=200
```

## File structure

```
durable-agent-demo/
├── demo-client.sh          # bash CLI: start, stream, steer, crash, cancel, logs, status, reset
├── azure.yaml              # azd service config
├── build.sh                # builds local agentserver wheels for the Docker image
├── infra/                  # Bicep templates
├── src/durable-research-agent/
│   ├── agent.py            # @task deep_research — durability + steering logic
│   ├── app.py              # InvocationAgentServerHost — minimal HTTP plumbing
│   ├── agent.yaml          # Foundry agent definition
│   ├── Dockerfile          # python:3.12-slim → python app.py
│   ├── requirements.txt
│   └── wheels/             # built by build.sh; carries pre-release agentserver SDKs
└── README.md
```
