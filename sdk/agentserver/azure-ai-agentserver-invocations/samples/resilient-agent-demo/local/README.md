# Run the resilient research agent locally (crash → recover)

This kit runs the invocations `resilient-research-agent` **entirely on your
machine** and demonstrates resilient crash-recovery — **without** the hosted
Foundry task API.

> **Why local?** Resilient recovery normally relies on the hosted task-store
> `/tasks` API. That API is currently returning **403** for hosted agents, which
> blocks deployed recovery. Off-platform, the framework auto-selects a
> **file-backed** task store, and the agent persists its per-turn event streams +
> checkpoints to disk — so the *exact same* recovery code path runs locally with
> no hosted dependency. Only the LLM sub-calls go to your Foundry project.

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
2. **`POST /invocations {"message": "<topic>"}`** starts a 3-phase research run
   (one checkpoint per phase) and returns an `invocation_id`; the SSE
   from `GET /invocations/{id}` streams to `out/sse_initial.txt`.
3. **Crash** it after the first phase checkpoint (`POST {"message": "crash"}`
   forces `os._exit(137)`).
4. **Restart** → the startup recovery scan reclaims the in-progress task and
   re-invokes the handler (`ctx.entry_mode == "recovered"`), reading the
   persisted phase watermark and resuming at the next un-finished phase.
5. **Reconnect** with `GET …?last_event_id=<seq>` → `out/sse_resumed.txt` (skips
   already-seen events), and assert the run emits `recovered` and reaches
   `run_complete` with all phases done.

Example tail:

```
[4/4] Reconnecting to the same invocation and verifying the run completes across the crash
  » recovery confirmed: handler re-invoked, 1 phase(s) already done
  » resumed checkpoint: phase 2/3 done
  » resumed checkpoint: phase 3/3 done
  » terminal event: run_complete (3 phases)

RESULT
{
  "pre_crash_checkpoints": 1,
  "recovered_event_completed_phases": 1,
  "terminal_event": "run_complete",
  "phases_completed": 3,
  "expected_phases": 3,
  "RECOVERED_FULL_PLAN": true
}

✓ Resilient recovery succeeded — the run completed all phases across a crash.
```

Tunables (env): `NUM_PHASES` (default 3), `CRASH_AFTER` (default 1 phase
checkpoint), `PORT` (default 8088), `TARGET_OUTPUT_TOKENS` (default 80).

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

**Terminal 2 — start, stream, crash, reconnect:**

```bash
# 1) Start a run. Capture the invocation_id from the response.
INV=$(curl -s http://localhost:8088/invocations \
  -H 'content-type: application/json' \
  -d '{"message":"renewable energy supply chains"}' | python -c 'import sys,json;print(json.load(sys.stdin)["invocation_id"])')
echo "invocation_id=$INV"

# 2) Stream it. Note the highest "sequence_number" before you crash it,
#    and watch for "type":"phase_end" checkpoints.
curl -N -s "http://localhost:8088/invocations/$INV"

# 3) In a THIRD terminal, after a phase_end, crash the process:
curl -s http://localhost:8088/invocations \
  -H 'content-type: application/json' -d '{"message":"crash"}'

# The server exits (137). Restart it in Terminal 1 (./serve.sh again — SAME
# session id; serve.sh pins FOUNDRY_AGENT_SESSION_ID). On startup it logs
# "Reclaimed stale task ... Recovered task ... is now active".

# 4) Reconnect, skipping events you already saw (use the last seq from step 2):
curl -N -s "http://localhost:8088/invocations/$INV?last_event_id=<last_seq>"
# First you'll see a {"type":"recovered","completed_phases":N} event, then the
# remaining phases stream, ending with {"type":"run_complete"}.
```

> No auth is needed locally. The session is pinned by `FOUNDRY_AGENT_SESSION_ID`
> (set by `serve.sh`) — both the original run and the restarted process must
> agree on it for the recovery scan to find the in-progress task.

## How it works locally

`serve.sh` / `run.sh` set the env vars that flip the framework into local mode:

| Env var | Effect |
|---------|--------|
| `AGENTSERVER_TASKS_BACKEND=local` | Use the file-backed task store instead of the hosted `/tasks` API. |
| `AGENTSERVER_STATE_ROOT=<dir>` | Where the resilient task store lives (`<dir>/tasks`). |
| `FOUNDRY_AGENT_SESSION_ID=<id>` | The session = the resilient task id. Must be identical across restarts. |
| `DEMO_MODE=1` | Enables the `"crash"` message sentinel. |

The agent additionally persists its per-turn **event streams** and **phase
checkpoints** under `~/.agentserver-tasks/` (file-backed replay), so a reconnecting
client can replay from `last_event_id` after the restart. Recovery works by
restarting the process against the same task store + session id.

## Files

| File | Purpose |
|------|---------|
| `setup.sh` | Create a venv and install the preview wheels + demo deps. |
| `run.sh` | One-command automated crash → recover → verify demo. |
| `serve.sh` | Start the agent locally for manual exploration. |
| `recovery_demo.py` | The orchestrator `run.sh` invokes. |

The agent itself is `../src/resilient-research-agent/` (`app.py` = HTTP host,
`agent.py` = the resilient task).

## Troubleshooting

**`Address already in use` / `OSError: [Errno 98]`** — a server is still running
on the port. `run.sh` auto-picks the next free port; for `serve.sh`, stop the
old server (`Ctrl-C` in its terminal) or pick another port: `PORT=8090 ./serve.sh`.
