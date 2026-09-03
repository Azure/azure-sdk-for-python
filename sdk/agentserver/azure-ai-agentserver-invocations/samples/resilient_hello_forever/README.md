# Minimal *indefinite* resilient long-running agent

A durable background worker that **never finishes on its own** — it ticks
forever until cancelled, surviving crashes and redeploys. It is the companion to
`resilient_hello_world` (which runs a fixed number of steps and completes), and
depends on **only** the two agentserver packages — no LLM, no `azure-ai-projects`,
no `langgraph`.

## What makes an infinite loop a well-behaved LRA

The body is a `while True` loop, plus the three things such a loop needs:

1. **Checkpoint every iteration** — a monotonically increasing `iterations`
   cursor is written to a durable state store, so recovery resumes from where it
   was.
2. **Graceful shutdown** — on redeploy / SIGTERM the framework sets
   `ctx.shutdown`; the loop does `return await ctx.exit_for_recovery()` to release
   the lease cleanly so the next instance re-enters and continues.
3. **A stop path** — an explicit cancel sets `ctx.cancel` with
   `ctx.cancel_requested`; the loop returns terminally so it can actually be
   stopped.

It also sets `timeout=timedelta(days=7)` (the maximum per-turn budget), because
each *turn* is watchdog-bounded (default 1 day). When any interruption occurs —
crash, redeploy, or turn-budget expiry — the task is re-entered with
`ctx.entry_mode == "recovered"` and resumes from its checkpointed iteration.

## Files

| File | Purpose |
|------|---------|
| `agent.py` | The durable `@task` (`hello_forever`): the infinite, checkpointed loop. |
| `app.py`   | `InvocationAgentServerHost`: start / poll / cancel. |
| `requirements.txt` | Just `azure-ai-agentserver-core` + `azure-ai-agentserver-invocations`. |

## Run it

```bash
pip install -r requirements.txt
python app.py
```

```bash
# start the forever worker (note the invocation_id in the response)
curl -s -XPOST -H "Content-Type: application/json" \
    -d '{"name": "Ada"}' http://localhost:8088/invocations
# -> {"status": "started", "invocation_id": "<inv>"}

# poll — iterations keep climbing, status stays "running"
curl -s "http://localhost:8088/invocations/<inv>"
# -> {"status": "running", "iterations": 12}

# stop it
curl -s -XPOST "http://localhost:8088/invocations/<inv>/cancel"
# -> {"status": "cancelling", "invocation_id": "<inv>"}
```

## The key line: enable resilient tasks

As of `azure-ai-agentserver-core` **2.2.0b1** the durable-task subsystem is
**strictly opt-in**. Before host startup:

```python
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
set_resilient_tasks_enabled(True)
```

Without it, `hello_forever.start()` raises `TaskManagerNotInitialized` and there
is no crash recovery.

## See the recovery

1. Start the worker and poll until `iterations` is a few in.
2. **Kill the process** (Ctrl-C).
3. Restart `python app.py`. The recovery scan re-enters `hello_forever` with
   `ctx.entry_mode == "recovered"` (see the `Recovered '<name>' at iteration N`
   log) and the loop continues climbing from `N` — it does **not** reset to 0.

## Environment

| Var | Default | Meaning |
|-----|---------|---------|
| `TICK_SECONDS` | `2` | Seconds between iterations. |
