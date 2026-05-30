# Durable Invocation Samples — Cross-Sample Guide

This guide is the entry point for the four durable invocation samples
shipped in this package. Read it first to pick the right starting
point, then dive into a sample's own `README.md`.

## When to use which sample

| Need                                                                      | Start here                                |
|---------------------------------------------------------------------------|-------------------------------------------|
| A simple multi-turn session with crash resilience                         | [`durable_multiturn`](durable_multiturn/) |
| A LangGraph-backed conversation that supports steering + fork-on-steer    | [`durable_langgraph`](durable_langgraph/) |
| A steerable, live-streaming GitHub Copilot session                        | [`durable_copilot`](durable_copilot/)     |
| A long-running pipeline that checkpoints and resumes after crashes        | [`durable_research`](durable_research/)   |

## Concepts (read once, then refer back)

### Entry mode (`ctx.entry_mode`)

Every invocation runs the handler from the top. `ctx.entry_mode`
tells the handler *why* it was entered this time:

- `"fresh"` — first lifetime; no prior state.
- `"resumed"` — orderly resume after `ctx.suspend(...)` returned;
  prior state is intact.
- `"recovered"` — recovery after process crash; prior state is
  intact and was rebuilt from the durable checkpoint.

For more detail on entry mode semantics see the
[core developer guide §3](../../azure-ai-agentserver-core/docs/durable-task-guide.md#hello-world).

### Metadata namespaces (`ctx.metadata`)

`ctx.metadata` is a callable, durable key-value store scoped to a
single task. Two shapes:

- `ctx.metadata[k] = v` — default namespace, per-task.
- `ctx.metadata("session")[k] = v` — named namespace; sibling of the
  default namespace, also per-task.

Mutations are durable only after `await ctx.metadata.flush()`. The
named-namespace shape is used by `durable_multiturn` to separate
per-invocation state from session-level state.

### Recovery replay (consumer reconnect)

Two of the samples emit a recovery snapshot to the consumer before
continuing the live stream:

- `durable_copilot` reads the upstream Copilot session log via
  `session.get_messages()` and replays the prior lifetime's
  partial assistant text as a single `text_delta` chunk marked
  `recovered: true`.
- `durable_research` checkpoints per stage; on recovery, the
  consumer sees a recovery banner and then the next un-completed
  stage's stream — earlier stages are not re-run.

### Steering (cancel-and-replace)

`@task(..., steerable=True)` lets a new invocation arrive while the
previous one is still running; `ctx.cancel` fires inside the prior
lifetime, the handler aborts cleanly, and the new lifetime starts
with the new input. `durable_copilot` and `durable_langgraph`
demonstrate the pattern.

## Prereqs for every sample

- Python 3.11+
- `pip install -r samples/<sample>/requirements.txt` — each sample
  declares its own dependencies for install-independence (FR-014).
- Optional but recommended for the streaming samples:
  `Accept: text/event-stream` on the POST to receive live SSE.

## Production checklist

Before deploying a durable invocation sample to a hosted agent
sandbox:

1. Confirm the host writes durable state under a path that survives
   container restarts (e.g., `~/.durable-sessions` is fine for local
   demos; in production this should be a persistent volume).
2. Set `STAGE_DURATION=0` (research) and disable any other artificial
   delays.
3. Verify the upstream SDK (Copilot, LangGraph, AI Foundry) is
   pinned in `requirements.txt`.
4. Run the per-sample e2e suite at least once against the production
   storage path.

## See also

- [Core developer guide](../../azure-ai-agentserver-core/docs/durable-task-guide.md) — full API reference and conceptual deep-dive.
- [`SHIPPABLE.md`](SHIPPABLE.md) — the per-sample shippable bar
  manifest.
- [`durable-agent-demo/README.md`](durable-agent-demo/README.md) —
  the foundry-hosted reference demo (not part of the per-sample
  shippable surface).
