# Durable LangGraph — Steerable Multi-Turn Graph

A durable, **steerable** [LangGraph](https://github.com/langchain-ai/langgraph)
conversation that survives process crashes and supports
fork-on-steer: roll back to the last stable checkpoint and replay the
new user message instead of the old one.

## What this sample shows

- One `@task(name="langgraph_session", steerable=True)` wrapping a
  LangGraph `StateGraph`.
- **LangGraph owns the conversation flow**; the durable primitive
  owns crash resilience and steering. There is no `DurabilityContext`
  — LangGraph already persists graph state via its own
  `SqliteSaver` keyed on `thread_id`.
- **Checkpoint-and-fork cancel** — three patterns layered:
  1. Pre-entry cancel — short-circuit if `ctx.cancel` is pre-set.
  2. Inter-node cancel — `graph.stream()` checks `ctx.cancel` between
     nodes (~2s granularity).
  3. Fork-on-steer — when a steering input arrives, `update_state`
     against the last stable checkpoint creates a new branch with the
     new user message and the graph re-runs from that point.

## Prerequisites

- Python 3.11+
- `azure-ai-agentserver-invocations`
- `langgraph`, `langchain-core`, `langgraph-checkpoint-sqlite`

## Quick start

```bash
pip install -r requirements.txt
python -m durable_langgraph.app
```

## Invocation example

```bash
# Turn 1
curl -X POST "http://localhost:8088/invocations?agent_session_id=trip" \
     -H "Content-Type: application/json" \
     -d '{"message": "Plan a 2-week Japan vacation"}'

# Turn 2
curl -X POST "http://localhost:8088/invocations?agent_session_id=trip" \
     -H "Content-Type: application/json" \
     -d '{"message": "Budget is $5000"}'

# Steer mid-turn (before turn 2 finishes) → graph forks
curl -X POST "http://localhost:8088/invocations?agent_session_id=trip" \
     -H "Content-Type: application/json" \
     -d '{"message": "Actually, plan a Tokyo-only trip instead"}'

# End session
curl -X POST "http://localhost:8088/invocations?agent_session_id=trip" \
     -H "Content-Type: application/json" \
     -d '{"message": "done"}'
```

## Inducing a crash

1. Start the host: `python -m durable_langgraph.app`.
2. Send a turn that triggers multi-node processing.
3. `SIGKILL` the host between nodes: `kill -9 <pid>`.
4. Restart: `python -m durable_langgraph.app`.

## Observing recovery

After restart, send any new turn on the same `agent_session_id`:

- The LangGraph `SqliteSaver` checkpoint is read from
  `~/.durable-sessions/langgraph_checkpoints.db`.
- The task re-enters with `ctx.entry_mode == "recovered"` and resumes
  from the last completed graph node.
- No node is double-executed (no double LLM call, no double tool
  call).

## Troubleshooting

- **"sqlite3.OperationalError: database is locked"** — only one host
  process at a time may write the LangGraph checkpoint DB. Stop any
  duplicate processes.
- **Graph re-runs from the beginning after restart** — confirm the
  checkpointer is configured with a stable `thread_id` keyed on the
  session ID.
- **Steering doesn't fork** — fork uses `graph.update_state` against a
  specific checkpoint config; verify your graph nodes update state
  (`return {...}`) rather than mutating in place.
