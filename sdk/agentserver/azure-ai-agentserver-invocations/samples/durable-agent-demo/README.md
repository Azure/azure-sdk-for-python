# Durable Research Agent — Crash-Resilient Demo

This sample demonstrates a **long-running research agent** that survives process
crashes and automatically resumes from its last checkpoint. It uses the
`@durable_task` decorator from `azure-ai-agentserver-core` to provide built-in
crash resilience without any manual state management.

## What it showcases

1. **12-stage deep research pipeline** — each stage is a distinct LLM call with real-time token streaming
2. **Crash resilience** — send `{"message": "crash"}` to kill the process; the supervisor
   restarts it, and the task resumes from its last checkpoint
3. **GET reconnection** — after a crash, `GET /invocations/{id}` streams replayed + live tokens
4. **Cancel support** — `POST /invocations/{id}/cancel` stops the task gracefully
5. **File-backed streaming** — stream items persist to disk for replay after crashes

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
│          deep_research.start()                             │
│            └── @durable_task execution                     │
│                  ├── Stage 1/12 → LLM streaming + ckpt     │
│                  ├── Stage 2/12 → LLM streaming + ckpt     │
│                  │       💥 CRASH (supervisor restarts)     │
│                  ├── Stage 3/12 (resumes here)             │
│                  ├── ...                                   │
│                  └── Stage 12/12 → final report            │
│                                                            │
│  GET /invocations/{id}                                     │
│    └── Streams from active task or replays from file       │
│                                                            │
│  POST /invocations/{id}/cancel                             │
│    └── Signals cancellation to running task                │
│                                                            │
│  Local disk: ~/.durable-tasks/ (persists across restarts)  │
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
ENDPOINT="https://e2e-tests-westus2-account.services.ai.azure.com/api/projects/e2e-tests-westus2/agents/durable-research-agent/endpoint/protocols"

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

The process exits. The supervisor immediately restarts it and recovers the task.

### Step 3: Reconnect via GET

Wait ~10 seconds for the process to restart and recover, then reconnect:

```bash
# Use the invocation ID from Step 1's response headers (x-agent-invocation-id),
# or just use any ID — the GET handler finds the active task by session.
INV_ID="reconnect"

curl -N -X GET "${ENDPOINT}/invocations/${INV_ID}?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN"
```

You'll see replayed tokens from before the crash, followed by the recovery message
and continued live streaming:
```
data: {"type": "token", "content": "\n\n**[Stage 1/12]** Decomposing topic...\n"}
data: {"type": "token", "content": "Quantum computing..."}
...
data: {"type": "token", "content": "\n\n⚡ **Recovered from crash!** Resuming from stage 3/12...\n\n"}
data: {"type": "token", "content": "\n\n**[Stage 3/12]** Identifying leading researchers...\n"}
...
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

Each time the task resumes from its last checkpoint — no work is lost.

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

The `@durable_task` decorator provides:

- **Automatic persistence** — task state is checkpointed after each stage via
  `ctx.metadata.flush()`
- **Crash recovery** — on startup, stale (in-flight) tasks are automatically
  detected by lease owner and re-executed, with `ctx.metadata` containing all
  previously saved progress
- **Entry mode awareness** — `ctx.entry_mode` tells the function why it was
  called: `"fresh"`, `"resumed"`, or `"recovered"`
- **File-backed streaming** — stream items are persisted to disk via a custom
  `FileStreamHandler` so GET can replay them after a crash

Key code pattern:
```python
@durable_task(name="deep_research", stream_handler_factory=file_stream_factory)
async def deep_research(ctx: TaskContext[dict]) -> dict:
    completed = ctx.metadata.get("completed_stages", 0)

    if ctx.entry_mode == "recovered":
        await ctx.stream(json.dumps({"type": "token", "content": "⚡ Recovered!"}))

    for i in range(completed, len(STAGES)):
        # Stream LLM tokens in real-time
        async for event in llm_stream:
            await ctx.stream(json.dumps({"type": "token", "content": event.delta}))

        # CHECKPOINT — survives crashes
        ctx.metadata["completed_stages"] = i + 1
        await ctx.metadata.flush()

    return final_result
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | AI Foundry project endpoint (set by platform) | Required |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Model deployment to use | `gpt-4.1-mini` |
| `FOUNDRY_TASK_API_ENABLED` | Use platform Task Storage (vs local file) | `0` (local) |
| `STAGE_DURATION` | Seconds between stages (for demo pacing) | `5` |

## File Structure

```
durable-agent-demo/
├── azure.yaml              # azd service config
├── build.sh                # Build local wheels for Docker
├── infra/                  # Bicep templates
├── src/durable-research-agent/
│   ├── agent.py            # ⭐ The durable task (12-stage research pipeline)
│   ├── app.py              # HTTP handlers (invoke, GET reconnect, cancel)
│   ├── supervisor.py       # PID 1 reverse proxy (keeps /readiness alive)
│   ├── agent.yaml          # Agent definition for Foundry
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wheels/             # Local package wheels (built by build.sh)
└── README.md
```
