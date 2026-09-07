# Minimal resilient long-running agent — **cancellation**

A durable, **finite** job that would finish on its own but can be **cancelled
mid-run**. It is the smallest end-to-end illustration of the cancel flow for a
long-running agent (LRA), and depends on **only** the two agentserver packages —
no LLM, no `azure-ai-projects`, no `langgraph`.

It complements the other minimal samples:

| Sample | Shape | Cancel |
|--------|-------|--------|
| `resilient_hello_world` | finite, runs to completion | — |
| `resilient_cancellable` | **finite, can be stopped early** | **yes** |
| `resilient_hello_forever` | indefinite, must be stopped | yes |

## How cancel works

The job counts through `steps` steps, checkpointing after each. The cancel
endpoint writes a durable **cancel marker** to a separate state-store key; the
job reads that marker **before every step** and, if present, records
`status: "cancelled"` and returns without finishing the remaining steps.

Using a durable marker rather than the in-process `ctx.cancel` event matters:

1. **Cross-replica** — the cancel request may land on a different replica than
   the one running the job; a durable marker is visible to both.
2. **Crash-durable** — a job recovered after a cancel was requested still sees
   the marker and stops.
3. **No ETag race** — the marker lives in its own key, so the cancel write never
   collides with the checkpoint's ETag.

## Run it

```bash
pip install -r requirements.txt
python app.py            # listens on http://localhost:8088
```

Pass the same `?agent_session_id=` on every call so poll/cancel hit the same
session-scoped store:

```bash
# start a 30-step job (STEP_DELAY defaults to 2s, so ~60s of work)
curl -s -XPOST -H "Content-Type: application/json" \
    -d '{"name": "Ada", "steps": 30}' \
    "http://localhost:8088/invocations?agent_session_id=demo"
# -> {"status": "started", "invocation_id": "<inv>", "total_steps": 30}

# poll — completed_steps climbs while status is "in_progress"
curl -s "http://localhost:8088/invocations/<inv>?agent_session_id=demo"
# -> {"status": "in_progress", "completed_steps": 4, "total_steps": 30}

# cancel mid-run
curl -s -XPOST "http://localhost:8088/invocations/<inv>/cancel?agent_session_id=demo"
# -> {"status": "cancelling", "invocation_id": "<inv>"}

# poll again — the job stopped early
curl -s "http://localhost:8088/invocations/<inv>?agent_session_id=demo"
# -> {"status": "cancelled", "completed_steps": 4, "total_steps": 30}
```

`status` is one of `in_progress` / `cancelling` / `cancelled` / `completed` /
`failed`. `cancelling` is the brief window after a cancel is requested but before
the job reaches its next step and finalizes.

## The key line: enable resilient tasks

As of `azure-ai-agentserver-core` **2.1.0b1** the durable-task subsystem is
**strictly opt-in**. Before host startup:

```python
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
set_resilient_tasks_enabled(True)
```

Without it, `cancellable_job.start()` raises `TaskManagerNotInitialized` and
there is no crash recovery.

## Cancel survives a crash

1. Start a 30-step job and request cancel while it is a few steps in.
2. Before the job observes the marker, **hard-kill the process** — an *ungraceful*
   termination such as `kill -9 <pid>` (SIGKILL). Do **not** use Ctrl-C: that
   triggers the host's graceful shutdown, which gives the running task up to ~25s
   to finish, during which it observes the marker and exits terminally on its own
   — leaving nothing to recover.
3. Restart `python app.py`. The recovery scan re-enters the job with
   `ctx.entry_mode == "recovered"`; it reads the still-present cancel marker on
   its next step and stops with `status: "cancelled"` — the cancel is not lost.
