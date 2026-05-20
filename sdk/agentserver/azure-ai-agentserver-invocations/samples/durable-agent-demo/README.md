# Durable Research Agent — Crash-Resilient Demo (LangGraph)

This sample demonstrates a **long-running research agent** that survives process
crashes and automatically resumes from its last checkpoint. It uses **LangGraph**
with an **SQLite checkpointer** for built-in crash resilience — no manual state
management needed.

## What it showcases

1. **12-stage deep research pipeline** — each stage is a distinct LLM call with real-time token streaming
2. **Crash resilience** — send `{"message": "crash"}` to kill the process; the supervisor
   restarts it, and the graph resumes from its last checkpointed node
3. **GET reconnection** — after a crash, `GET /invocations/{id}` replays completed stages
   from the checkpoint state
4. **Cancel support** — `POST /invocations/{id}/cancel` stops the task gracefully
5. **Zero manual checkpointing** — LangGraph's `SqliteSaver` handles all state persistence

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│  Hosted Agent Sandbox (port 8088)                          │
│                                                            │
│  supervisor.py (PID 1 — always responds to /readiness)     │
│    └── python app.py (port 8089, restarted on crash)       │
│                                                            │
│  POST /invocations                                         │
│    ├── {"message": "crash"} → responds 200, then exit 💥   │
│    └── {"message": "<topic>"} →                            │
│          run_research(thread_id, topic)                    │
│            └── LangGraph StateGraph execution              │
│                  ├── research_stage node (Stage 1) → ckpt  │
│                  ├── research_stage node (Stage 2) → ckpt  │
│                  │       💥 CRASH (supervisor restarts)     │
│                  ├── research_stage node (Stage 3) resumes │
│                  ├── ...                                   │
│                  └── research_stage node (Stage 12) → done │
│                                                            │
│  GET /invocations/{id}                                     │
│    ├── Live stream queue (if graph is running)             │
│    └── Replay from SQLite checkpoint (if not running)      │
│                                                            │
│  POST /invocations/{id}/cancel                             │
│    └── Sets asyncio.Event checked between nodes            │
│                                                            │
│  Local disk: ~/.durable-research/checkpoints.db            │
└────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- `azd` AI agents extension: `azd extension install azure.ai.agents`

## Quick Start (Deploy to Foundry)

```bash
# 1. Build wheels (included in Docker image)
./build.sh

# 2. Login and deploy
azd auth login
azd up
```

## Demo Script — Crash Recovery & Reconnection

This walkthrough demonstrates the full durability story. Total time: ~3 minutes.

### Setup

```bash
# Get access token
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)

# Endpoint
ENDPOINT="https://<account>.services.ai.azure.com/api/projects/<project>/agents/durable-research-agent/endpoint/protocols"

# Generate a unique session ID (reuse across all calls in this demo)
SESSION_ID="demo-$(uuidgen | tr '[:upper:]' '[:lower:]')"
echo "Session: $SESSION_ID"
```

### Step 1: Start the research task

```bash
curl -N -X POST "${ENDPOINT}/invocations?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Research the history and future of quantum computing"}'
```

You'll see SSE token events streaming in real-time:
```
data: {"type": "token", "content": "\n\n**[Stage 1/12]** Decomposing topic into focused research questions...\n"}
data: {"type": "token", "content": "Quantum"}
data: {"type": "token", "content": " computing"}
...
data: {"type": "token", "content": "\n✅ Stage 1/12 complete.\n"}
data: {"type": "token", "content": "\n\n**[Stage 2/12]** Surveying foundational literature...\n"}
```

> **Note:** Press Ctrl+C to stop watching the stream. The task continues running on the server.

### Step 2: Crash the agent! 💥

While the research is running, send a crash trigger (same session):

```bash
curl -X POST "${ENDPOINT}/invocations?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "crash"}'
```

Response (the app sends this back BEFORE dying):
```
data: {"type": "done", "full_text": "💥 Process crashing now..."}
```

The process exits. The supervisor immediately restarts it.

### Step 3: Reconnect via GET

Wait ~10 seconds for the process to restart, then reconnect:

```bash
INV_ID="reconnect"

curl -N -X GET "${ENDPOINT}/invocations/${INV_ID}?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN"
```

If the graph has resumed running, you'll see live token streaming.
If not yet running, you'll get a replay of completed stages from the checkpoint:
```
data: {"type": "token", "content": "\n\n**[Stage 1/12]** Decomposing topic...\n"}
data: {"type": "token", "content": "Quantum computing..."}
...
data: {"type": "token", "content": "\n\n[Completed 2/12 stages — task may be recovering...]\n"}
```

### Step 4: Crash again (optional — repeat as many times as you want)

```bash
curl -X POST "${ENDPOINT}/invocations?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "crash"}'

# Wait, then reconnect again
sleep 10
curl -N -X GET "${ENDPOINT}/invocations/${INV_ID}?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN"
```

Each time the graph resumes from its last checkpoint — no work is lost.

### Step 5: Cancel the task (optional)

```bash
curl -X POST "${ENDPOINT}/invocations/${INV_ID}/cancel?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{"status": "cancelled", "message": "Task cancellation requested."}
```

## How it works

**LangGraph + SQLite checkpointer** provides everything:

- **Automatic persistence** — graph state is checkpointed by `AsyncSqliteSaver`
  after every node execution (every completed research stage)
- **Crash recovery** — on restart, `aget_state(config)` loads the last checkpoint;
  the graph is re-invoked from `current_stage` onward
- **No manual state management** — no `ctx.metadata.flush()`, no `FileStreamHandler`,
  no JSONL files. The checkpoint IS the state.
- **GET replay** — after crash, GET loads checkpoint and replays all completed
  stage results as SSE events

Key code pattern:
```python
# The graph state — persisted automatically after each node
class ResearchState(TypedDict):
    topic: str
    current_stage: int
    results: Annotated[list[dict], _append_results]
    is_cancelled: bool
    is_complete: bool

# Single node that loops via conditional edge
async def research_stage(state: ResearchState) -> dict:
    stage_idx = state["current_stage"]
    # ... LLM call with token streaming ...
    return {"current_stage": stage_idx + 1, "results": [new_result]}

# On crash recovery — just check existing checkpoint and resume
snapshot = await graph.aget_state(config)
if snapshot.values.get("current_stage", 0) > 0:
    # Resume from checkpoint — graph continues where it left off
    async for _ in graph.astream(snapshot.values, config):
        pass
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | AI Foundry project endpoint (set by platform) | Required |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Model deployment to use | `gpt-4.1-mini` |
| `STAGE_DURATION` | Seconds between stages (for demo pacing) | `5` |

## File Structure

```
durable-agent-demo/
├── azure.yaml              # azd service config
├── build.sh                # Build local wheels for Docker
├── infra/                  # Bicep templates
├── src/durable-research-agent/
│   ├── agent.py            # ⭐ LangGraph research pipeline (12 stages + SQLite checkpoint)
│   ├── app.py              # HTTP handlers (invoke, GET reconnect, cancel)
│   ├── supervisor.py       # PID 1 reverse proxy (keeps /readiness alive)
│   ├── agent.yaml          # Agent definition for Foundry
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wheels/             # Local package wheels (built by build.sh)
└── README.md
```
