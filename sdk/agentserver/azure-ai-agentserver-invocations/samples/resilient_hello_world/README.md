# Minimal resilient "hello world" long-running agent

The smallest possible **long-running agent (LRA)** on the invocations protocol —
**start-and-poll, no streaming**. It depends on **only** the two agentserver
packages (no LLM, no `azure-ai-projects`, no `langgraph`), so it runs with a
minimal dependency and memory footprint while still showing the one thing that
makes an agent an LRA: **it survives a crash and resumes from a checkpoint
instead of starting over.**

## Files

| File | Purpose |
|------|---------|
| `agent.py` | The durable `@task` (`hello_world`): counts N steps, checkpointing after each. |
| `app.py`   | `InvocationAgentServerHost`: `POST` to start, `GET` to poll status. |
| `requirements.txt` | Just `azure-ai-agentserver-core` + `azure-ai-agentserver-invocations`. |

## Run it

```bash
pip install -r requirements.txt
python app.py            # listens on http://localhost:8088
```

Start a run (returns immediately — the task keeps running in the background).
Pass `?agent_session_id=` to isolate this run's checkpoints; use the **same**
session id when you poll:

```bash
curl -s -XPOST -H "Content-Type: application/json" \
    -d '{"name": "Ada", "steps": 10}' \
    "http://localhost:8088/invocations?agent_session_id=demo"
# -> {"status": "started", "invocation_id": "<inv>", "total_steps": 10}
```

Poll it by that invocation id (repeat every couple of seconds, same session):

```bash
curl -s "http://localhost:8088/invocations/<inv>?agent_session_id=demo"
# -> {"status": "in_progress", "completed_steps": 3, "total_steps": 10}
# ... while running you see completed_steps climb.
# When it finishes:
# -> {"status": "completed", "completed_steps": 10, "total_steps": 10}
```

> The one-shot `@task` record is cleaned up on completion, but this sample's
> durable **checkpoint** persists, so the poll keeps reporting `completed`.

## How an *invocation* becomes *long-running*

1. `POST /invocations` derives a durable task id — `durable_task_id(session_id,
   invocation_id, user_id)`, a SHA-256 digest, **not** the raw invocation id —
   and calls `hello_world.start(task_id=<that digest>)`, which **schedules the
   task on the TaskManager and returns immediately**. The work is *not* tied to
   the HTTP request — the handler returns `202` while the task runs on. (The
   digest keeps the id within the provider's `[A-Za-z0-9_-]{1,128}` contract and
   isolates it per user + session; it is also the durable **checkpoint** key.)
2. The task loops, sleeping between steps and writing a durable **checkpoint**
   to the state store after each, keyed by that same derived task id.
3. `GET /invocations/{invocation_id}` re-derives the same task id from the
   request's identity and reads that durable state, so any client can poll
   progress long after the original call returned. When correlating logs or
   checkpoints, note they are keyed by the derived task id, not the invocation
   id.

## The key line: enable resilient tasks

As of `azure-ai-agentserver-core` **2.1.0b1** the durable-task subsystem is
**strictly opt-in**. `AgentServerHost` builds the `TaskManager` (and runs the
crash-recovery scan) **only** when you call, before host startup:

```python
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
set_resilient_tasks_enabled(True)
```

Without it, `hello_world.start()` raises `TaskManagerNotInitialized` and there is
no crash recovery. Declaring a `@task` alone does **not** turn it on.

## See the recovery

1. Start a longer run: `{"name": "Ada", "steps": 30}`.
2. Poll until `completed_steps` is a few in, then **kill the process** (Ctrl-C).
3. Restart `python app.py`. On startup the recovery scan re-enters `hello_world`
   with `ctx.entry_mode == "recovered"` (see the `Recovered — resuming …` log),
   reads `completed_steps` from the durable checkpoint, and continues from the
   next step — it does **not** restart from step 1. Poll again to watch
   `completed_steps` climb past where it crashed, ending at `completed`.

## Environment

| Var | Default | Meaning |
|-----|---------|---------|
| `STEP_DELAY` | `2` | Seconds between steps. Keep > 0 so a crash lands mid-run. |
