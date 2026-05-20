# Durable Research Agent — Crash-Resilient Demo

This sample demonstrates a **long-running research agent** that survives process
crashes and automatically resumes from its last checkpoint. It uses the
`@durable_task` decorator from `azure-ai-agentserver-core` to provide built-in
crash resilience without any manual state management.

## What it showcases

1. **12-stage deep research pipeline** — each stage is a distinct LLM call with real-time token streaming
2. **Crash resilience** — send `{"message": "crash"}` to kill the process; the supervisor
   restarts it, and the task resumes from its last checkpoint
3. **Fire-and-forget POST** — `POST /invocations` dispatches the task and returns 202 immediately
4. **GET streaming with resume** — `GET /invocations/{id}?last_event_id=N` streams SSE, skipping already-seen events
5. **Cancel support** — `POST /invocations/{id}/cancel` stops the task gracefully
6. **File-backed streaming** — stream items persist to disk for replay after crashes

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│  Hosted Agent Sandbox (port 8088)                          │
│                                                            │
│  supervisor.py (PID 1 — always responds to /readiness)     │
│    └── python app.py (port 8089, restarted on crash)       │
│                                                            │
│  POST /invocations  (fire-and-forget)                      │
│    ├── {"message": "crash"} → 202, then exit 💥            │
│    └── {"message": "<topic>"} →                            │
│          deep_research.start() → 202 JSON response         │
│          { invocation_id, session_id, task_id, status }    │
│                                                            │
│  GET /invocations/{id}?last_event_id=N                     │
│    └── Streams SSE from active task (skips first N events) │
│        or replays from persisted file                      │
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

### Quick Demo (recommended)

Use the included `demo-client.sh` which handles token refresh, session sharing,
auto-reconnection, and event resumption:

```bash
# Terminal 1 — start research (auto-reconnects after crashes)
./demo-client.sh start "quantum computing"

# Terminal 2 — crash the agent while it's running
./demo-client.sh crash

# Watch Terminal 1 auto-reconnect and resume from where it left off!
# Crash again, as many times as you want:
./demo-client.sh crash

# Terminal 3 — stream container logs (optional)
./demo-client.sh logs

# Or cancel:
./demo-client.sh cancel

# Reset session to start fresh:
./demo-client.sh reset
```

### How it works (client flow)

1. **POST** `/invocations?agent_session_id=X` → returns 202 with `invocation_id`
2. **GET** `/invocations/{inv_id}` → streams SSE events (`id: N\ndata: {...}\n\n`)
3. Client tracks `last_event_id` (the `id:` field of the last received event)
4. On disconnect (crash): **POST** same session → new `invocation_id` → **GET** with `?last_event_id=N`
5. Server skips first N events → client sees only new content from the recovery point

### Manual Demo (curl)

```bash
# Get access token
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)

# Endpoint
ENDPOINT="https://e2e-tests-westus2-account.services.ai.azure.com/api/projects/e2e-tests-westus2/agents/durable-research-agent/endpoint/protocols"

# Generate a unique session ID (reuse across all calls in this demo)
SESSION_ID="demo-$(uuidgen | tr '[:upper:]' '[:lower:]')"
echo "Session: $SESSION_ID"
```

### Step 1: Start the research task (fire-and-forget)

```bash
# POST dispatches the task and returns immediately with IDs
curl -s -X POST "${ENDPOINT}/invocations?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Research the history and future of quantum computing"}'
```

Response (202):
```json
{"status": "started", "invocation_id": "inv_abc123...", "session_id": "demo-..."}
```

Save the invocation ID:
```bash
INV_ID="inv_abc123..."  # from response above
```

### Step 2: Stream results via GET

```bash
curl -N -X GET "${ENDPOINT}/invocations/${INV_ID}?api-version=2025-11-15-preview" \
  -H "Authorization: Bearer $TOKEN"
```

You'll see SSE events with sequential IDs:
```
id: 1
data: {"type": "token", "content": "\n\n**[Stage 1/12]** Decomposing topic...\n"}

id: 2
data: {"type": "token", "content": "Quantum"}

id: 3
data: {"type": "token", "content": " computing"}
...
```

### Step 3: Crash the agent! 💥

While the research is running, send a crash trigger (same session):

```bash
curl -s -X POST "${ENDPOINT}/invocations?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "crash"}'
```

Response (202):
```json
{"status": "crashing", "message": "💥 Process will crash now"}
```

The process exits. The supervisor immediately restarts it and recovers the task.

### Step 4: Reconnect with resume

Wait ~10 seconds, then POST again to get a new invocation ID, and GET with `last_event_id`:

```bash
# Get new invocation ID (task is already in progress)
NEW_RESPONSE=$(curl -s -X POST "${ENDPOINT}/invocations?api-version=2025-11-15-preview&agent_session_id=${SESSION_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "quantum computing"}')
NEW_INV_ID=$(echo "$NEW_RESPONSE" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['invocation_id'])")

# Resume from where we left off (e.g., last_event_id=370)
curl -N -X GET "${ENDPOINT}/invocations/${NEW_INV_ID}?api-version=2025-11-15-preview&last_event_id=370" \
  -H "Authorization: Bearer $TOKEN"
```

You'll see only NEW events (stages after the crash):
```
id: 371
data: {"type": "token", "content": "\n\n⚡ **Recovered from crash!** Resuming from stage 5/12...\n\n"}

id: 372
data: {"type": "token", "content": "\n\n**[Stage 5/12]** Examining competing theories...\n"}
...
```

### Step 5: Cancel the task (optional)

```bash
curl -X POST "${ENDPOINT}/invocations/${NEW_INV_ID}/cancel?api-version=2025-11-15-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{"status": "cancelled", "message": "Task cancellation requested."}
```

## Container Logs

Stream real-time container logs (stdout/stderr) in a separate terminal:

```bash
# Via demo-client.sh (uses session from .demo-session file)
./demo-client.sh logs

# Or directly via azd:
azd ai agent monitor --session <session-id> --follow

# Recent logs (last 20 lines):
azd ai agent monitor --tail 20

# System events (container start/stop):
azd ai agent monitor --type system
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
- **Event IDs** — each SSE event has a sequential `id:` field; clients use
  `last_event_id` query param to skip already-seen events on reconnect

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
├── demo-client.sh          # ⭐ Demo client (handles sessions, reconnect, crash)
├── azure.yaml              # azd service config
├── build.sh                # Build local wheels for Docker
├── infra/                  # Bicep templates
├── src/durable-research-agent/
│   ├── agent.py            # ⭐ The durable task (12-stage research pipeline)
│   ├── app.py              # HTTP handlers (POST fire-and-forget, GET stream, cancel)
│   ├── supervisor.py       # PID 1 reverse proxy (keeps /readiness alive)
│   ├── agent.yaml          # Agent definition for Foundry
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wheels/             # Local package wheels (built by build.sh)
└── README.md
```
