# Durable Research Agent

A long-running 12-stage deep-research agent that survives process
crashes and supports consumer disconnect/reconnect with replay.

## What this sample shows

- One `@task(name="deep_research")` runs a 12-stage research pipeline
  — each stage is a real LLM call.
- **Checkpoint-and-resume**: after each completed stage, the watermark
  (`completed_stages` + accumulated `results`) is flushed to
  `ctx.metadata` and `await ctx.metadata.flush()`. On
  `ctx.entry_mode == "recovered"`, the loop picks up at the next
  un-completed stage.
- **Live SSE streaming** of incremental tokens via
  `ctx.stream({"type": "token", "content": "..."})`.
- **Consumer reconnect**: stage-by-stage checkpointed state lets a
  reconnected consumer get a coherent snapshot rather than starting
  from stage 1.

This sample is the peer-sample-shape distillation of the larger
`samples/durable-agent-demo/src/durable-research-agent/` reference
demo. The reference demo includes a supervisor / entrypoint
scaffolding for the foundry-hosted environment; this sample strips
all of that away and ships only the three files every invocations
sample ships: `agent.py`, `app.py`, and `requirements.txt`.

## Prerequisites

- Python 3.11+
- `azure-ai-agentserver-invocations`
- An Azure AI Foundry project endpoint
  (`FOUNDRY_PROJECT_ENDPOINT`) and Azure auth
  (`DefaultAzureCredential`).
- A model deployment (default: `gpt-4.1-mini`); override with
  `AZURE_AI_MODEL_DEPLOYMENT_NAME`.

## Quick start

```bash
export FOUNDRY_PROJECT_ENDPOINT='https://<your-project>.cognitiveservices.azure.com'
export AZURE_AI_MODEL_DEPLOYMENT_NAME='gpt-4.1-mini'

pip install -r requirements.txt
python -m durable_research.app
```

## Invocation example

```bash
# Streaming (live SSE)
curl -X POST "http://localhost:8088/invocations?agent_session_id=demo" \
     -H "Content-Type: application/json" \
     -H "Accept: text/event-stream" \
     -d '{"topic": "the future of nuclear fusion"}'

# Async-poll (no streaming)
curl -X POST "http://localhost:8088/invocations?agent_session_id=demo" \
     -H "Content-Type: application/json" \
     -d '{"topic": "the future of nuclear fusion"}'
# → 202  {"invocation_id": "...", "status": "queued", ...}

# Poll
curl "http://localhost:8088/invocations/<inv-id>?agent_session_id=demo"
```

## Inducing a crash

1. Start the host: `python -m durable_research.app`.
2. Begin a research run: `STAGE_DURATION=5` makes inter-stage delays
   visible, so a crash at stage 4–6 is easy to trigger.
3. `SIGKILL` the host: `kill -9 <pid>`.
4. Restart: `python -m durable_research.app`.

## Observing recovery

After restart, re-invoke with the **same** `agent_session_id` and the
same `topic`:

- The task re-enters with `ctx.entry_mode == "recovered"`.
- A recovery banner is streamed:
  `"⚡ Recovered from crash. Resuming from stage N/12."`
- The loop picks up at the next un-completed stage — earlier stages
  are not re-run.
- The final report includes content from both lifetimes.

## Troubleshooting

- **`EnvironmentError: FOUNDRY_PROJECT_ENDPOINT is required`** — set
  the environment variable before starting the host.
- **`DefaultAzureCredential` auth failure** — run `az login` or set
  service-principal env vars per the Azure Identity docs.
- **Stages re-run after restart** — confirm
  `await ctx.metadata.flush()` is awaited after every checkpoint
  write; unflushed writes do not survive a SIGKILL.
- **Streaming hangs** — the client must read the SSE response; the
  task pauses on backpressure if the consumer disconnects without
  reconnect.
- **Want zero-delay stages for tests** — set `STAGE_DURATION=0`.
