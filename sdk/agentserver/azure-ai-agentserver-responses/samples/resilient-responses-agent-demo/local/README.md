# Run the resilient Responses agent locally (crash → recover)

This kit runs the `resilient-responses-agent-demo` **entirely on your machine** and
demonstrates resilient crash-recovery — **without** the hosted Foundry task API.

> **Why local?** Resilient recovery normally relies on the hosted task-store
> `/tasks` API. That API is currently returning **403** for hosted agents, which
> blocks deployed recovery. Off-platform, the framework auto-selects a
> **file-backed** task store + response store, so the *exact same* recovery code
> path runs locally with no hosted dependency. Only the LLM sub-calls go to your
> Foundry project.

## Prerequisites

- Python 3.10+
- `az login` (the LLM sub-calls use `DefaultAzureCredential`)
- A Foundry **project endpoint** and a **model deployment** in it

## Quick start (automated demo)

```bash
cd local
./setup.sh                          # builds a venv from ../../../../wheels + deps

az login
export FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o     # a deployment in that project

./run.sh
```

`run.sh` drives the whole thing and prints a narrated, verified result:

1. **Start** the agent as a local server (file-backed state store).
2. **Stream** a 3-phase research response (one resilient `OutputItem` +
   `checkpoint()` per sub-call) → `out/sse_initial.txt`.
3. **Crash** it after 5 checkpoints (the demo's `"crash"` input forces
   `os._exit(137)`), pinned to the same session so the right replica dies.
4. **Restart** → the startup recovery scan reclaims the in-progress task and
   re-invokes the handler (`context.is_recovery`), seeding from the persisted
   response and resuming at the first un-checkpointed sub-call.
5. **Reconnect** with `GET …?stream=true&starting_after=<seq>` →
   `out/sse_resumed.txt`, and assert the response completes the full plan.

Example tail:

```
[4/4] Reconnecting to the same response and verifying it completes across the crash
  » first resumed event: response.created (carries 5 checkpointed item(s))
  » terminal event: response.completed with 12 total output item(s)

RESULT
{
  "pre_crash_checkpoints": 5,
  "first_resumed_event": "response.created",
  "items_seeded_on_resume": 5,
  "terminal_event": "response.completed",
  "final_item_count": 12,
  "expected_item_count": 12,
  "RECOVERED_FULL_PLAN": true
}

✓ Resilient recovery succeeded — the response completed the full plan across a crash.
```

Tunables (env): `NUM_PHASES` (default 3 → 12 sub-calls), `CRASH_AFTER` (default
5 checkpoints), `PORT` (default 8088), `TARGET_OUTPUT_TOKENS` (default 80).

## Manual exploration

Drive the agent yourself in two terminals.

**Terminal 1 — start the agent:**

```bash
cd local
az login
export FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
./serve.sh
```

**Terminal 2 — stream, crash, reconnect** (`SID` pins everything to one session):

```bash
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
SID=$(openssl rand -hex 16)

# 1) Start a streaming, background, stored response. Note the "id" (caresp_...)
#    and the highest "sequence_number" you see before you crash it.
curl -N -s http://localhost:8088/responses \
  -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d "{\"model\":\"gpt-4o\",\"input\":\"renewable energy supply chains\",
       \"stream\":true,\"store\":true,\"background\":true,\"agent_session_id\":\"$SID\"}"

# 2) In a THIRD terminal, after a few `response.output_item.done` events, crash it:
curl -s http://localhost:8088/responses \
  -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d "{\"model\":\"gpt-4o\",\"input\":\"crash\",\"stream\":false,\"store\":true,
       \"background\":true,\"agent_session_id\":\"$SID\"}"

# The server process exits (137). Restart it in Terminal 1 (./serve.sh again,
# SAME resilient root). On startup it logs "Reclaimed stale task ... Recovered
# task ... is now active".

# 3) Reconnect to the SAME response (use the id + last seq from step 1):
curl -N -s "http://localhost:8088/responses/<caresp_id>?stream=true&starting_after=<last_seq>" \
  -H "authorization: Bearer $TOKEN"
# First event is response.in_progress/created carrying the already-checkpointed
# items; the next sub-call resumes; the stream ends with response.completed.
```

> GET routes by `response_id` — you don't pass a session id on reconnect. For
> `POST /responses`, the session id goes in the **body** (`agent_session_id`),
> not the query string.

## How it works locally

`serve.sh` / `run.sh` set two env vars that flip the framework into local mode:

| Env var | Effect |
|---------|--------|
| `AGENTSERVER_TASKS_BACKEND=local` | Use the file-backed task store instead of the hosted `/tasks` API. |
| `AGENTSERVER_STATE_ROOT=<dir>` | Where the resilient task store **and** response store live (`<dir>/tasks`, `<dir>/responses`, `<dir>/streams`). |

Recovery works by restarting the process against the **same** `AGENTSERVER_STATE_ROOT`:
the startup scan finds the stale in-progress task, reclaims its lease, and
re-invokes the handler. `DEMO_MODE=1` enables the `"crash"` input sentinel.

## Files

| File | Purpose |
|------|---------|
| `setup.sh` | Create a venv and install the preview wheels + demo deps. |
| `run.sh` | One-command automated crash → recover → verify demo. |
| `serve.sh` | Start the agent locally for manual exploration. |
| `recovery_demo.py` | The orchestrator `run.sh` invokes. |

The agent handler itself is `../src/resilient-responses-agent-demo/main.py`.

## Other resilient samples

The same local pattern (`AGENTSERVER_TASKS_BACKEND=local` +
`AGENTSERVER_STATE_ROOT`, restart to recover) applies to the other resilient
samples in this drop — see `../../sample_19_resilient_streaming.py`,
`sample_20_resilient_steering.py`, `sample_21_resilient_langgraph.py`,
`sample_22_resilient_multiturn.py`, and the invocations
`resilient_research` / `resilient_multiturn` / `resilient_langgraph` / `resilient_copilot`
samples.

## Troubleshooting

**`Address already in use` / `OSError: [Errno 98]`** — a server is still running
on the port. `run.sh` auto-picks the next free port; for `serve.sh`, stop the
old server (`Ctrl-C` in its terminal) or pick another port: `PORT=8090 ./serve.sh`.
