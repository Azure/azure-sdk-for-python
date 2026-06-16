---
page_type: sample
languages:
- python
products:
- azure
name: azure-ai-agentserver-responses durable samples for Python
description: Durable Responses-API agent samples for the azure-ai-agentserver-responses preview.
---

# azure-ai-agentserver-responses — durable samples

This preview drop ships the **durable** Responses-API samples. Each shows a
crash-resilient, optionally steerable handler built on the spec-025 durability
primitives (`durable_background=True`, one `OutputItem` + `stream.checkpoint()`
per unit of work, recovery via `context.persisted_response`).

## Run them locally (crash → recover)

The hosted task API is currently returning 403, so the durable samples are
exercised **locally** — the durable task store + response store are file-backed,
no hosted dependency. A ready-to-run, verified kit lives at:

> **[`durable-responses-agent-demo/local/`](durable-responses-agent-demo/local/README.md)** —
> `./setup.sh` then `./run.sh` for an automated stream → crash → recover → verify
> run, or `./serve.sh` to drive the agent yourself.

The same pattern (`AGENTSERVER_TASKS_BACKEND=local` +
`AGENTSERVER_DURABLE_ROOT=<dir>`, restart the process to recover) applies to
every sample below.

## Samples index

| # | Sample | Pattern | Description |
|---|--------|---------|-------------|
| 18 | [Durable Copilot](sample_18_durable_copilot.py) | Durable + steerable | GitHub Copilot SDK with `durable_background=True, steerable_conversations=True` — `create_session` / `resume_session` flow with live delta forwarding |
| 19 | [Durable Streaming](sample_19_durable_streaming.py) | Durable | Three-phase streaming handler with `durable_background=True` — uses `context.conversation_chain_metadata` watermarks to skip phases that already completed on recovery |
| 20 | [Durable Steering](sample_20_durable_steering.py) | Durable + steerable | Demonstrates `context.is_steered_turn` on the drain re-entry with `durable_background=True, steerable_conversations=True` |
| 21 | [Durable LangGraph](sample_21_durable_langgraph.py) | Durable + steerable | LangGraph upstream framework integration — `context.conversation_chain_id` as the LangGraph thread id |
| 22 | [Durable Multiturn](sample_22_durable_multiturn.py) | Durable | Multi-turn conversation with `durable_background=True, steerable_conversations=False` — `context.conversation_chain_metadata` tracks per-turn counters |

The flagship end-to-end demo (15-phase × 4-subcall research agent, one
checkpoint per sub-call, azd-deployable + locally runnable) is
[`durable-responses-agent-demo/`](durable-responses-agent-demo/).

## Key durable APIs

Use these from a durable handler (`ResponseContext`):

- `context.is_recovery` / `context.persisted_response` — seed the stream from the
  persisted snapshot and resume at the first un-checkpointed item.
- `context.is_steered_turn` / `context.pending_input_count` — observe and drain
  mid-turn steering inputs.
- `context.conversation_chain_metadata` / `context.conversation_chain_id` —
  per-conversation durable metadata and the stable chain id.
- `await context.exit_for_recovery()` — graceful-shutdown primitive that leaves
  the response `in_progress` for next-lifetime recovery (works in every handler
  shape).

## Enabling durability and steering

Durable + steerable behaviour is **opt-in** via `ResponsesServerOptions` — the
defaults are both `False`:

```python
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions

app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(
        durable_background=True,             # opt-in to crash recovery
        steerable_conversations=True,        # opt-in to mid-turn steering
    ),
)
```

Without `durable_background=True`, a crash mid-handler leaves the response in the
"crash-failed" state (the next process lifetime marks it `failed` instead of
re-invoking the handler). Without `steerable_conversations=True`, concurrent
multi-turn requests for the same conversation return `409 conversation_locked`
instead of queueing.
