# Resilient Research Agent — Demo

> **▶ Deploy it (hosted, recommended):** `azd deploy` this sample, then drive it
> with **[`demo-client.sh`](demo-client.sh)** (it auto-resolves the endpoint from
> your azd env). Validated end-to-end on a hosted Foundry deployment — run,
> stream, reconnect, and steer all work against the hosted task API. Prefer an
> offline run? The verified local kit in **[`local/`](local/README.md)**
> exercises the same run → crash → recover → verify flow file-backed
> (`cd local && ./setup.sh && ./run.sh`).

A `@multi_turn_task`-decorated long-running research agent that demonstrates two
platform capabilities of the Azure AI Hosted Agent + resilient-task primitive:

1. **Long-running tasks run uninterrupted past the platform's sandbox-eviction window.**
   The framework's `PATCH .../tasks/<id>` lease-renewal cycle (every ~30s,
   half of the 60s lease) signals activity through the task-storage API,
   which refreshes the platform's sandbox idle-reclaim timer. The demo
   runs for ~33 min with **zero client-side keepalive ingress** and the
   sandbox stays warm the whole time. Validated end-to-end against a
   hosted Foundry deployment.

2. **Recovery from container crashes.** When the agent container dies
   (intentional crash or OOM), the platform's nanny worker brings it
   back within ~1 min (43s measured) **without any new client ingress**.
   The resilient task automatically resumes from its last checkpoint
   (`ctx.entry_mode == "recovered"` + a `recovered` SSE event with
   `completed_phases`). User-visible: any reconnect attempt — whenever
   the user gets around to it — seamlessly continues the run.

3. **Steering.** Sending a new turn on a running steerable task queues
   the input and signals cooperative cancel. The agent winds down the
   current turn at the next checkpoint boundary and re-enters with the
   queued input as a fresh turn (with the prior topic surfaced for the
   viewer to see).

What the agent actually does: 15 logical research phases on whatever
topic the caller supplies. Each phase runs a small agent loop
(research → critique → refine → synthesize) against `gpt-4o`,
streaming every token to the consumer. The handler checkpoints to
`ctx.metadata` and flushes **after each subcall** — so a crash
mid-phase recovers at the next un-finished subcall (worst case: the
one that was actively streaming is replayed). A steerer that arrives
mid-phase causes the handler to wind down at the next phase boundary,
not abruptly. Hosted defaults target a ~33-min wall-time run (spanning
2x the sandbox-eviction window so every demo run exercises the lease
keep-alive path); local `agent.py` defaults are shorter for dev
iteration.

Between subcalls and between phases the agent sleeps for
`INTRA_PHASE_COOLDOWN_SEC` / `INTER_PHASE_COOLDOWN_SEC` (30s each in
the hosted defaults). A `cooldown` SSE event is emitted at the start
of each pause so the terminal shows a low-key
`...cooling down 30s (between subcalls) — next: subcall 3/4 in phase 2/15`
line instead of going silent.

## Run locally (offline alternative)

For an offline run with no hosted dependency, the resilient crash-recovery flow
can also be exercised **locally** — file-backed task store. A
ready-to-run, verified kit lives in [`local/`](local/README.md):

```bash
cd local
./setup.sh        # builds a venv from ../../../../wheels + deps

az login
export FOUNDRY_PROJECT_ENDPOINT="https://<account>.services.ai.azure.com/api/projects/<project>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"

./run.sh          # automated: run -> crash -> restart -> recover -> verify
./serve.sh        # or drive it yourself (curl http://localhost:8088/invocations)
```

See [`local/README.md`](local/README.md) for the manual curl recipe and how the
local resilient backend works (`AGENTSERVER_TASKS_BACKEND=local` +
`FOUNDRY_AGENT_SESSION_ID`).

## Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- `azd` AI agents extension: `azd extension install azure.ai.agents`

## Deploy

```bash
# 1. Stage the checked-in resilient-task preview wheels into the docker
#    build context (build.sh just copies sdk/agentserver/wheels/*.whl
#    into a per-sample gitignored staging dir — no compilation, no PyPI
#    fetch)
./build.sh

# 2. Login + deploy
azd auth login
azd up
```

The deploy provisions infra + ships the container image and prints the
invocations endpoint. Point `demo-client.sh` at your deployment by
setting the `ENDPOINT=` env var (or editing the default near the top of
`demo-client.sh`).

> The resilient-task primitive (`@task` / `@multi_turn_task`) is in
> **private preview** and is not on PyPI. It ships only as the
> pre-release wheels checked into
> [`sdk/agentserver/wheels/`](../../../../wheels). See
> [`sdk/agentserver/wheels/README.md`](../../../../wheels/README.md)
> for the consumption workflow in your own project.

## demo-client.sh — command reference

The client is a bash CLI. Each command operates on a single session
tracked locally in `.demo-session`. Run from this directory:

| Command | What it does |
|---|---|
| `./demo-client.sh start "<topic>"` | **Allocates a new session id** (UUID), writes it to `.demo-session`, dispatches `POST /invocations` with the topic, then attaches to the SSE stream. |
| `./demo-client.sh stream` | Reuses the session + invocation from `.demo-session` and (re)attaches to the SSE stream. Passes `?last_event_id=N` so the server skips events you've already seen. |
| `./demo-client.sh steer "<topic>"` | Reuses the current session and sends a new `POST /invocations` with the new topic. If the run is still active the framework queues this as a steering input; the agent winds down at the next checkpoint boundary and re-enters on the new topic. |
| `./demo-client.sh cancel` | `POST /invocations/{id}/cancel` on the current invocation. The handler observes `ctx.cancel.is_set()` and winds down cooperatively. |
| `./demo-client.sh crash` | Sends `POST /invocations` with `{"message": "crash"}`. The agent (gated by `DEMO_MODE=1`) calls `os._exit(137)`. The platform's nanny worker brings the container back within ~1 min on its own — `./demo-client.sh stream` any time after will pick up the recovered run (no need to wait for or trigger anything). |
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
  resilient recovery picked up where the previous lifetime left off.
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

### A. Long-running run with no client-side keepalive (~33 min wall time)

This run intentionally outlasts the platform's 15-min sandbox-eviction
window — the framework's lease-renewal cycle keeps the sandbox warm.

```bash
# t = 0:00
./demo-client.sh start "the future of nuclear fusion"
# Stream events. Note server_time_utc + server_uptime_sec on each event.

# t = 5:00
# Detach (Ctrl-C). Make zero ingress for the next 20-25 min.

# t = 25:00 — open a new terminal:
./demo-client.sh stream
# The container is the SAME instance (no reclaim happened) because the
# framework's PATCH .../tasks/<id> lease renewals kept the platform's
# idle timer fresh. Your reconnect resumes the live SSE stream;
# server_uptime_sec is now ~25 min, not reset to 0.
```

### B. Explicit crash + nanny restoration (no ingress required)

```bash
# Terminal 1: start a run and leave it streaming.
./demo-client.sh start "fusion energy research priorities"
# Wait until 3-4 phases have completed.

# Terminal 2: force a crash.
./demo-client.sh crash
# Server returns 202 then os._exit(137). Terminal 1's stream disconnects.

# Wait — DO NOT send any new ingress. The platform's nanny brings the
# container back within ~1 min entirely on its own (validated: 43 sec
# from crash to new worker_instance_id in a hosted Foundry
# deployment). The resilient task auto-resumes from the last checkpoint
# inside the new process — you don't need to do anything.

# When you want to verify recovery:
./demo-client.sh stream
# You'll see:
#   🔁 Recovered from crash   completed_phases=3
#   server_uptime_sec=<some-value-much-larger-than-1>
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
│  │  │     └─ (await streams.get(id)).subscribe(after=N) → SSE       │  │  │
│  │  │     └─ 404 if id never seen; 410 if stream destroyed (TTL)    │  │  │
│  │  │                                                               │  │  │
│  │  │  POST /invocations/{id}/cancel                                │  │  │
│  │  │     └─ run.cancel()                                           │  │  │
│  │  │                                                               │  │  │
│  │  │  GET  /readiness  (called by platform health probe at startup)│  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                     │  │
│  │  At module import: streams.use_file_backed_replay(                  │  │
│  │     storage_dir=~/.agentserver-tasks/_streams,                          │  │
│  │     cursor_fn=lambda ev: ev["sequence_number"],                     │  │
│  │     ttl_seconds=600)                                                │  │
│  │                                                                     │  │
│  │  deep_research  (agent.py)                                          │  │
│  │     @multi_turn_task(steerable=True)   ← no streaming kwarg         │  │
│  │     stream = await streams.get_or_create(ctx.input["invocation_id"])│  │
│  │     seq    = await stream.last_cursor() or 0   ← resume after crash │  │
│  │     loop 1..NUM_PHASES:                                             │  │
│  │        emit phase_start with server_time_utc + server_uptime_sec    │  │
│  │        run CALLS_PER_PHASE LLM sub-calls (research → critique → …)  │  │
│  │        ctx.metadata["completed_phases"] = i+1                       │  │
│  │        await ctx.metadata.flush()       ← crash-recovery boundary   │  │
│  │        emit phase_end                                               │  │
│  │        if ctx.cancel.is_set():                                      │  │
│  │           emit winding_down → stream.close() → return None          │  │
│  │           (bare return X is the implicit-suspend signal for chains) │  │
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
                │    back up via nanny worker after a     │
                │    crash (no client ingress needed)     │
                │  ─ Idle-reclaim timer: kept fresh by    │
                │    framework lease-renewal traffic so   │
                │    long-running tasks survive past 15min│
                └─────────────────────────────────────────┘
```

Notable points:

- The container runs `python app.py` directly. There is **no
  application-level supervisor or auto-restart wrapper** — the platform's
  nanny worker handles container restoration on crash.
- `task_id == session_id`: one resilient chain (`@multi_turn_task`) per
  session. This is what routes a steering POST to the active chain
  instead of starting a new one.
- The framework's lease-renewal loop talks to the **task-storage API**
  every ~30s (half of the 60s lease). This traffic both (a) refreshes
  the lease so a successor instance won't reclaim the task, and (b)
  signals activity to the platform's routing layer so the sandbox's
  idle-reclaim timer stays fresh — letting the run outlive the 15-min
  eviction window without any client ingress. The `/readiness`
  endpoint is hit only by the platform's startup health probe;
  `/liveness` is hit continuously (~every 2s) by the platform.
- When the platform's nanny restores the container after a crash, the
  framework's recovery scan finds the stranded task and re-enters the
  handler with `ctx.entry_mode == "recovered"` and `ctx.metadata`
  populated from the last checkpoint. A `recovered` SSE event is
  emitted to any (re)connecting clients.

## Streaming

The agent emits to the SDK's `streams` registry
(`azure.ai.agentserver.core.streaming`); the HTTP layer subscribes by
the same id. There is no streaming kwarg on `@multi_turn_task` —
streaming is explicitly initiated by the handler.

**Public surface used here (5 exports):** `streams`, `EventStream`,
`EventStreamError`, `EventStreamClosedError`, `EventStreamNotFoundError`.
The SDK ships three backings (live, in-memory replay, file-backed
replay) which you pick via the registry's configurators; concrete
backing classes are not in the public API.

**Backing.** `app.py` calls `streams.use_file_backed_replay(...)`
once at module import. This persists every event to
`~/.agentserver-tasks/_streams/<invocation_id>.jsonl` so the stream
survives a container crash + restart and a late `GET` can replay the
full transcript.

**Stream id = per-turn `invocation_id`** (per the streaming guide).
The HTTP layer reads `request.state.invocation_id` and propagates it
to the handler via `task.start(input={"invocation_id": inv_id, ...})`.
The handler reads it from `ctx.input["invocation_id"]`. **Not**
`ctx.task_id` — `task_id` is the per-session resilient-task identity
that spans multiple turns (steering, recovery), and conflating
logically separate per-turn streams under one id would break
`emit`-after-close on the second turn. Each turn — including a steered
re-entry — gets its own fresh `invocation_id` and its own stream.

**Cursor field.** `cursor_fn=lambda ev: ev["sequence_number"]`.
The handler maintains an in-memory `seq` counter and tags every emit
with the next value. On crash recovery the handler calls
`stream.last_cursor()` first to learn the highest sequence number
that made it to disk, then resumes numbering from there. The HTTP
layer surfaces `sequence_number` as the SSE `id:` field so a client
reconnect with `?last_event_id=N` maps cleanly to
`stream.subscribe(after=N)` — events the client already saw are
skipped without duplicates.

**Retention.** `ttl_seconds=600`. Per-event TTL bounds disk usage:
once a stream is closed and all its events have aged out, the
registry destroys the stream and removes the file. The 410 Gone
wire mapping in the GET handler covers the "client tried to reconnect
to an expired stream" case.

**Close-before-suspend / close-before-return.** Every exit path in
the handler (`run_complete`, `winding_down → suspend`,
`finally` safety net) explicitly closes the stream before the
framework reports the turn as terminal. This guarantees SSE
subscribers see a clean stream terminator before any next-turn
plumbing kicks in.

## Environment variables

These are set in `agent.yaml` (`environment_variables`) and travel with
the deploy. Override by editing `agent.yaml` and re-deploying.

| Variable | Default (hosted) | Default (`agent.py`) | Description |
|---|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | (required, set by platform) | — | Foundry project endpoint. |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | `gpt-4o` | `gpt-4o` | Responses-API model deployment name. |
| `DEMO_MODE` | `1` (in the demo image) | unset | Enables the `{"message": "crash"}` sentinel on `POST /invocations`. A production image would leave this off. |
| `NUM_PHASES` | `15` | `15` | Number of research phases. |
| `CALLS_PER_PHASE` | `4` | `4` | Sub-calls per phase (research, critique, refine, synthesize). |
| `TARGET_OUTPUT_TOKENS` | `1500` | `1500` | Max tokens per LLM sub-call. |
| `INTRA_PHASE_COOLDOWN_SEC` | `30` | `10` | Seconds between sub-calls within a phase. Hosted default is bumped to push total wall-time past 30 min. |
| `INTER_PHASE_COOLDOWN_SEC` | `30` | `20` | Seconds between phases. Hosted default is bumped to push total wall-time past 30 min. |

Note: `azure-ai-agentserver-core` automatically uses `HostedTaskProvider`
in hosted environments (i.e. when the platform sets
`FOUNDRY_HOSTING_ENVIRONMENT`) and `LocalFileTaskProvider` otherwise —
no opt-in env var required.

For a **fast** development loop (~2 min total instead of ~33 min), edit
`agent.yaml`'s `environment_variables` block:

```yaml
- name: NUM_PHASES
  value: "3"
- name: CALLS_PER_PHASE
  value: "1"
- name: INTRA_PHASE_COOLDOWN_SEC
  value: "2"
- name: INTER_PHASE_COOLDOWN_SEC
  value: "2"
- name: TARGET_OUTPUT_TOKENS
  value: "200"
```

## File structure

```
resilient-agent-demo/
├── demo-client.sh          # bash CLI: start, stream, steer, crash, cancel, logs, status, reset
├── azure.yaml              # azd service config
├── build.sh                # copies sdk/agentserver/wheels/*.whl into src/.../wheels/ for docker
├── infra/                  # Bicep templates
├── src/resilient-research-agent/
│   ├── agent.py            # @multi_turn_task deep_research — resilience + steering logic
│   ├── app.py              # InvocationAgentServerHost — minimal HTTP plumbing
│   ├── agent.yaml          # Foundry agent definition
│   ├── Dockerfile          # python:3.12-slim → python app.py
│   ├── requirements.txt
│   └── wheels/             # GITIGNORED — docker-build staging dir populated by build.sh
└── README.md
```

The resilient-task primitive private-preview wheels are checked in at
[`sdk/agentserver/wheels/`](../../../../wheels) — `./build.sh` just
copies them into this sample's `wheels/` so the Dockerfile can `COPY`
them at image-build time. See
[`sdk/agentserver/wheels/README.md`](../../../../wheels/README.md)
for the consumer workflow.
