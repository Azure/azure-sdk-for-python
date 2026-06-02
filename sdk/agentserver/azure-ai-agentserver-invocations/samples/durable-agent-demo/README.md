# Durable Research Agent — Demo

A `@task`-decorated long-running research agent that demonstrates three
platform capabilities of the Azure AI Hosted Agent + durable-task primitive:

1. **Long-running tasks (>15 min)** — the sandbox stays alive without
   client ingress because the durable-task framework's lease-renewal cycle
   internally exercises the readiness probe. As long as a `@task` handler
   is executing, the platform keeps the container alive.
2. **Crash recovery via the platform nanny** — when the agent process
   exits unexpectedly the platform nanny worker restarts the container
   within ~5-10 minutes. On restart the durable task resumes from its
   last checkpoint via `ctx.entry_mode == "recovered"`.
3. **Steering** — sending a new turn on a running steerable task queues
   the input and signals cooperative cancel. The agent winds down the
   current turn at the next checkpoint boundary and re-enters with the
   queued input as a fresh turn.

## What the agent does

12-to-15 logical research phases on a topic the caller supplies. Each phase
runs a small agent loop (research → critique → refine → synthesize) against
`gpt-4.1-mini`, streaming every token to the consumer as it arrives.

After each phase the handler checkpoints to `ctx.metadata` and flushes — so a
crash mid-run picks up at the next un-completed phase, and a steerer that
arrives mid-phase causes the handler to wind down at the *next* phase
boundary, not abruptly.

Defaults are tuned for a ~45-minute run (15 phases × ~3 minutes each); env
vars can shorten this for fast development iteration.

## Server-wall-clock timestamps in every stream event

Every `phase_start`, `phase_end`, `recovered`, `winding_down`, and
`run_complete` event carries two fields:

- `server_time_utc` — the wall clock on the agent container at the moment the
  event was emitted.
- `server_uptime_sec` — seconds since the Python process started. **Resets
  to ~0 after the platform nanny restarts the container** — making crash
  recovery unambiguously observable.

These let a viewer prove the server kept executing during a window when no
client ingress was happening: disconnect, wait 15+ minutes, reconnect, and
look at the timestamps on phases that finished while you were dead.

## Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- `azd` AI agents extension: `azd extension install azure.ai.agents`

## Quick start (deploy)

```bash
# 1. Build local wheels (so the Docker image carries pre-release SDK bits)
./build.sh

# 2. Login + deploy
azd auth login
azd up
```

The deploy outputs the invocations endpoint. `demo-client.sh` already points
at the canonical e2e-tests-westus2 deployment; edit `ENDPOINT=` in
`demo-client.sh` if you deployed elsewhere.

## Demo workflows

### A. Long-running run + no-ingress verification (~45 min)

Proves capability #1 — the sandbox stays alive without our HTTP traffic
because the durable-task lease renewal extends its lifetime.

```bash
# t = 0:00   Start a fresh run.
./demo-client.sh start "the future of quantum computing"
# Watch phase 1 and phase 2 stream.
# Note the server_time_utc on each event.

# t = 5:00   Disconnect — close the terminal entirely.
#            Zero ingress from this machine for the next 15-20 minutes.

# t = 20:00  Open a new terminal:
./demo-client.sh stream
# Scroll back. You should see phase headers timestamped at every ~3 min
# during the window you were disconnected — proof that the server kept
# running the task without your traffic to extend the sandbox lifetime.
```

### B. Crash + recovery (~10 min downtime)

Proves capability #2 — the platform nanny restarts the container and the
durable task resumes.

```bash
# Terminal 1: start a fresh run, leave it streaming.
./demo-client.sh start "fusion energy research priorities"
# Wait until 3-4 phases have completed.

# Terminal 2: force a crash.
./demo-client.sh crash
# Server returns 202 then exits. Your stream in Terminal 1 will disconnect.

# Wait ~5-10 minutes for the platform nanny to restart the container.

# Terminal 1 (or new terminal):
./demo-client.sh stream
# You should see:
#   🔁 Recovered from crash   resuming from phase 4/15
#   server_uptime_sec=2.4    ← fresh container; uptime started over
# ...and the stream picks up at phase 4, NOT phase 1.
```

### C. Steering (mid-run topic switch)

Proves capability #3 — the steerable task winds down at the next checkpoint
boundary and re-enters with the new input.

```bash
# Terminal 1:
./demo-client.sh start "deep learning interpretability"
# Wait until phase 2 starts streaming.

# Terminal 2:
./demo-client.sh steer "alignment of frontier models"
# Server queues the new input.

# Terminal 1 will show (within ~3 min, at the next phase boundary):
#   ↓ Winding down   cause=steering   completed=2/15   pending_steers=1
#   ▶ Run start    topic=alignment of frontier models  (steered from prior topic: deep learning interpretability)
#   ▶ Phase 1/15 — Decomposing topic into focused research questions
#   ...
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Hosted-agent sandbox (port 8088)                                     │
│                                                                       │
│    python app.py            (InvocationAgentServerHost)               │
│      ├── POST /invocations                                            │
│      │     → deep_research.start(task_id, input={"topic": ...})       │
│      │     → on already-active steerable task: queues steering input  │
│      ├── GET  /invocations/{id}?last_event_id=N                       │
│      │     → SSE stream from get_active_run(task_id)                  │
│      ├── POST /invocations/{id}/cancel                                │
│      │     → run.cancel()                                             │
│      └── POST /demo/crash    (only when DEMO_MODE=1)                  │
│            → os._exit(137)                                            │
│                                                                       │
│    deep_research  (in agent.py)                                       │
│      @task(steerable=True, stream_handler_factory=file_stream_factory)│
│      Loop 1..NUM_PHASES:                                              │
│        for each phase:                                                │
│          emit phase_start with server_time_utc + server_uptime_sec    │
│          run CALLS_PER_PHASE LLM sub-calls (research → critique → …)  │
│          ctx.metadata["completed_phases"] = i+1                       │
│          await ctx.metadata.flush()                                   │
│          emit phase_end                                               │
│          if ctx.cancel.is_set():                                      │
│            wind down → return await ctx.suspend(...)                  │
└──────────────────────────────────────────────────────────────────────┘

Platform-managed:
  • nanny worker: restarts the container within ~5-10 min on crash
  • lease-renewal ingress: framework pings /readiness for each renewal,
    keeping the sandbox alive as long as a @task is executing
```

There is **no application-level supervisor or auto-restart wrapper** — those
were necessary in an older platform model and have been removed.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | (required) | Foundry project endpoint (set by platform). |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | `gpt-4.1-mini` | Responses-API model deployment. |
| `NUM_PHASES` | `15` | Number of research phases. |
| `CALLS_PER_PHASE` | `4` | Sub-calls per phase (research, critique, refine, synthesize). |
| `TARGET_OUTPUT_TOKENS` | `1500` | Max tokens per LLM sub-call. |
| `INTRA_PHASE_COOLDOWN_SEC` | `10` | Seconds between sub-calls within a phase. |
| `INTER_PHASE_COOLDOWN_SEC` | `20` | Seconds between phases. |
| `DEMO_MODE` | `0` | When `1`, enables `POST /demo/crash`. |

For a **fast** development loop (~2 min total instead of ~45 min):

```bash
NUM_PHASES=3 CALLS_PER_PHASE=1 INTRA_PHASE_COOLDOWN_SEC=2 \
  INTER_PHASE_COOLDOWN_SEC=2 TARGET_OUTPUT_TOKENS=200 \
  python app.py
```

## File structure

```
durable-agent-demo/
├── demo-client.sh          # bash CLI: start, stream, steer, crash, cancel, …
├── azure.yaml              # azd service config
├── build.sh                # builds local agentserver wheels for the Docker image
├── infra/                  # Bicep templates
├── src/durable-research-agent/
│   ├── agent.py            # @task deep_research — the durability + steering logic
│   ├── app.py              # InvocationAgentServerHost — minimal HTTP plumbing
│   ├── agent.yaml          # Foundry agent definition
│   ├── Dockerfile          # python:3.12-slim → python app.py
│   ├── requirements.txt
│   └── wheels/             # built by build.sh; carries pre-release agentserver SDKs
└── README.md
```
