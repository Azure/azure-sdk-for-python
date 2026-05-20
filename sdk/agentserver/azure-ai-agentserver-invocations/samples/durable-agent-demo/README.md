# Durable Research Agent — Crash-Resilient Demo

This sample demonstrates a **long-running research agent** that survives crashes
and automatically resumes from its last checkpoint. It uses the
`@durable_task` decorator from `azure-ai-agentserver-core` to provide built-in
crash resilience without any manual state management.

## What it showcases

1. **Multi-stage long-running task** — 5 research stages that take ~1 minute total
2. **Real-time streaming** — SSE progress events as each stage completes
3. **Crash resilience** — send `{"message": "crash"}` to trigger a deliberate crash,
   the entrypoint auto-restarts the process, and the task resumes from checkpoint
4. **Hosted deployment** — deploys to Azure AI Foundry as a hosted agent via `azd`

## Architecture

```
┌────────────────────────────────────────────────────┐
│  Hosted Agent Sandbox                              │
│                                                    │
│  entrypoint.sh (auto-restarts on crash)            │
│    └── python main.py                              │
│                                                    │
│  POST /invocations                                 │
│    ├── {"message": "crash"} → os._exit(137) 💥     │
│    └── {"message": "<topic>"} →                    │
│          deep_research.start()                     │
│            └── @durable_task execution             │
│                  ├── Stage 1  → ctx.metadata.flush │
│                  ├── Stage 2  → ctx.metadata.flush │
│                  │       💥 CRASH (entrypoint       │
│                  │          restarts process)       │
│                  ├── Stage 3  (resumes here)       │
│                  ├── Stage 4  → ctx.metadata.flush │
│                  └── Stage 5  → final report       │
│                                                    │
│  Local disk: ~/.durable-sessions/ (persists in     │
│  the sandbox filesystem across restarts)           │
└────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- `azd` AI agents extension: `azd extension install azure.ai.agents`

## Quick Start (Local)

```bash
# 1. Build local wheel packages (packages aren't published yet)
./build.sh

# 2. Install dependencies
cd src/durable-research-agent
pip install wheels/*.whl
pip install -r requirements.txt

# 3. Set environment
export FOUNDRY_PROJECT_ENDPOINT="https://e2e-tests-westus2-account.services.ai.azure.com/api/projects/e2e-tests-westus2"
export STAGE_DURATION=10   # seconds per stage (default 15)

# 4. Run the agent (with auto-restart)
./entrypoint.sh
# — or directly without restart wrapper —
python app.py
```

## Quick Start (Hosted via azd)

```bash
# 1. Build wheels (included in Docker image)
./build.sh

# 2. Login and initialize (uses existing Foundry project)
azd auth login

# 3. Deploy
azd up
```

## Demo Walkthrough — Crash Recovery

### Terminal 1: Start the agent

```bash
./entrypoint.sh
# Output: [entrypoint] Starting agent (PID 12345)...
# Output: INFO Starting server on 0.0.0.0:8088
```

### Terminal 2: Send a research request (streaming)

```bash
curl -N -X POST "http://localhost:8088/invocations?agent_session_id=demo-1" \
    -H "Content-Type: application/json" \
    -d '{"message": "Research the history and future of quantum computing"}'
```

You'll see SSE events streaming:
```
data: {"type": "started", "invocation_id": "abc123"}
data: {"type": "progress", "stage": 1, "total": 5, "message": "[1/5] Analyzing topic..."}
data: {"type": "stage_done", "stage": 1, "total": 5, "preview": "Quantum computing originated..."}
data: {"type": "progress", "stage": 2, "total": 5, "message": "[2/5] Searching sources..."}
data: {"type": "stage_done", "stage": 2, "total": 5, "preview": "Key papers include..."}
```

### Terminal 2: Crash the agent! 💥

While stages are running, send the crash command from another terminal:

```bash
curl -X POST "http://localhost:8088/invocations?agent_session_id=crash-1" \
    -H "Content-Type: application/json" \
    -d '{"message": "crash"}'
```

### Terminal 1: Watch auto-restart

```
💥 DELIBERATE CRASH triggered via API — simulating OOM/failure
[entrypoint] 💥 Agent crashed with exit code 137. Restarting in 1s...
[entrypoint] Starting agent (PID 12346)...
INFO Starting server on 0.0.0.0:8088
WARNING Recovered stale task research-demo-1-abc123
```

The `entrypoint.sh` wrapper detects the crash and restarts automatically.
On startup, the durable task system detects the stale in-flight task and
recovers it from the last checkpoint.

### Terminal 2: Check status

```bash
# Poll the invocation to see resumed progress:
curl "http://localhost:8088/invocations/<invocation_id>"
```

Response:
```json
{
  "invocation_id": "abc123",
  "status": "running",
  "recovered": true,
  "completed_stages": 2
}
```

After recovery completes:
```json
{
  "invocation_id": "abc123",
  "status": "completed",
  "output": {
    "topic": "Research the history and future of quantum computing",
    "report": "Quantum computing has evolved from theoretical proposals...",
    "stages_completed": 5
  }
}
```

## How it works

The `@durable_task` decorator provides:

- **Automatic persistence** — task state is checkpointed after each stage via
  `ctx.metadata.flush()`
- **Crash recovery** — on startup, stale (in-flight) tasks are automatically
  detected and re-executed from the top, but `ctx.metadata` contains all
  previously saved progress
- **Entry mode awareness** — `ctx.entry_mode` tells the function why it was
  called: `"fresh"`, `"resumed"`, or `"recovered"`

Key code pattern:
```python
@durable_task(name="deep_research")
async def deep_research(ctx: TaskContext[dict]) -> dict:
    # Read progress from last checkpoint
    completed = ctx.metadata.get("completed_stages", 0)

    if ctx.entry_mode == "recovered":
        # We crashed! But metadata has our progress.
        await ctx.stream("⚡ Recovered! Resuming...")

    for i in range(completed, len(STAGES)):
        result = await do_stage(i)

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
| `STAGE_DURATION` | Seconds per research stage (for demo pacing) | `15` |
| `DURABLE_DATA_DIR` | Local persistence directory | `~/.durable-sessions` |

## File Structure

```
durable-agent-demo/
├── azure.yaml              # azd service config
├── build.sh                # Build local wheels for Docker
├── infra/                  # Bicep templates (shared with other demos)
├── .azure/demo-dev/.env    # Points at e2e-tests-westus2 project
├── src/durable-research-agent/
│   ├── agent.py            # ⭐ The durable task (this is the interesting part)
│   ├── app.py              # HTTP plumbing (just wires agent.py to the protocol)
│   ├── entrypoint.sh       # Auto-restarts on crash
│   ├── agent.yaml          # Agent definition for Foundry
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wheels/             # Local package wheels (built by build.sh)
└── README.md
```
