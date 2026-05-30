# Durable Multi-Turn Session

A durable multi-turn conversation that survives process crashes and
shows how to use the **named-namespace metadata** facility on the
primitive.

## What this sample shows

- One `@task(name="session_workflow")` per session — invoked once per
  user turn; the function runs from the top each time.
- `ctx.entry_mode` distinguishes `"fresh"` / `"resumed"` / `"recovered"`
  lifetimes.
- **Two metadata namespaces** demonstrating the
  `ctx.metadata(name)` callable facility:
  - `ctx.metadata` (default) — per-invocation state (the most-recent
    reply + the `invocation_id` for this turn).
  - `ctx.metadata("session")` — session-level state (full
    conversation history + turn count) that survives across many
    invocations of the same session.
- No external file-store for session state — the durable primitive
  owns persistence.

## Prerequisites

- Python 3.11+
- `azure-ai-agentserver-invocations`

## Quick start

```bash
pip install -r requirements.txt
python -m durable_multiturn.app
```

## Invocation example

```bash
# Turn 1
curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
     -H "Content-Type: application/json" \
     -d '{"message": "I want to plan a vacation to Japan"}'
# → 202   (x-agent-invocation-id: <inv-1>)

# Poll
curl "http://localhost:8088/invocations/<inv-1>?agent_session_id=trip-001"
# → {"invocation_id": "<inv-1>", "status": "completed", "output": {...}}

# Turn 2
curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
     -H "Content-Type: application/json" \
     -d '{"message": "Budget is $5000, 2 weeks"}'

# End session
curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
     -H "Content-Type: application/json" \
     -d '{"message": "done"}'
```

## Inducing a crash

1. Start the host: `python -m durable_multiturn.app`.
2. Send a turn.
3. **Before** polling for the result, `SIGKILL` the host:
   `kill -9 <pid>`.
4. Restart: `python -m durable_multiturn.app`.

## Observing recovery

- The task re-enters with `ctx.entry_mode == "recovered"`.
- The session's `history` and `turn_count` are read out of
  `ctx.metadata("session")` — the prior turn is intact.
- The recovered turn is correctly attributed (no duplicate
  user-message, no skipped reply).

## Troubleshooting

- **Session history empty after restart** — confirm
  `await session.flush()` is called after every state mutation; only
  flushed mutations are durable.
- **Mixed-up state between two session IDs** — sessions are isolated
  by `task_id = f"session-{session_id}"`; verify your client sends a
  distinct `agent_session_id` per conversation.
- **`KeyError: 'invocation_id'`** — the poll handler matches the
  current `invocation_id` against `ctx.metadata["invocation_id"]`;
  if you call `/invocations/{id}` with a stale ID after a newer
  invocation has overwritten the default-namespace state, you'll get
  a `404`. Use the invocation ID returned from the *most recent*
  POST.
