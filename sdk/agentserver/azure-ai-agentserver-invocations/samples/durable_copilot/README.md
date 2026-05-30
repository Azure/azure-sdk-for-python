# Durable Copilot — Steerable GitHub Copilot Sessions

A durable, **steerable** Copilot conversation that survives process
crashes and lets the user replace an in-flight reply by sending a new
turn before the old one finishes.

## What this sample shows

- One `@task(name="copilot_session", steerable=True)` per session.
- **Live streaming** of `AssistantMessageDeltaData` to the consumer
  via `ctx.stream({"type": "text_delta", ...})`.
- `SessionIdleData` → `ctx.stream({"type": "session_idle"})` so the
  consumer can detect end-of-turn deterministically.
- **Upstream-history dedup** — the upstream Copilot session is the
  source of truth for "did I already send this user turn this
  lifetime?" — read via `session.get_messages()`, no separate
  watermark, no flush-ordering race.
- **Recovery replay** — on `ctx.entry_mode == "recovered"`, replays
  whatever assistant text the previous lifetime had already emitted
  before continuing the stream.
- **3-phase steering cancel**:
  1. Pre-entry cancel — queued steering input that arrived before this
     entry; persist the message into the upstream session, abort.
  2. Mid-stream cancel — `ctx.cancel` fires while the assistant is
     generating; abort the upstream session.
  3. Post-completion cancel — cancel arrived after the assistant
     message landed; record as superseded.

## Prerequisites

- Python 3.11+
- `azure-ai-agentserver-invocations`
- A working `gh copilot` install — the Copilot SDK auth flows are
  required.

## Quick start

```bash
pip install -r requirements.txt
python -m durable_copilot.app
```

## Invocation example

```bash
# Turn 1
curl -X POST "http://localhost:8088/invocations?agent_session_id=demo" \
     -H "Content-Type: application/json" \
     -H "Accept: text/event-stream" \
     -d '{"message": "Tell me about durable agent loops"}'

# Steer mid-stream (send another message before turn 1 finishes)
curl -X POST "http://localhost:8088/invocations?agent_session_id=demo" \
     -H "Content-Type: application/json" \
     -H "Accept: text/event-stream" \
     -d '{"message": "Actually, focus on the cancel semantics"}'
```

Stream chunks are JSON SSE: `{"type": "text_delta", "delta": "..."}`
during streaming, `{"type": "session_idle"}` on turn complete.

## Inducing a crash

1. Start the host: `python -m durable_copilot.app`.
2. Send a turn that takes ≥10s to complete (e.g., a multi-paragraph
   research request).
3. While streaming, `SIGKILL` the host process: `kill -9 <pid>`.
4. Restart the host: `python -m durable_copilot.app`.

## Observing recovery

After restart, send a new request on the **same** `agent_session_id`
and you will see:

- `ctx.entry_mode == "recovered"` on the recovered task lifetime.
- A `{"type": "text_delta", "delta": "<text from prior lifetime>",
   "recovered": true}` chunk emitted before the live stream continues.
- The upstream Copilot session is **not** double-fed the user turn
  (dedup via `session.get_messages()`).

## Troubleshooting

- **"Module 'copilot' not found"** — install the GitHub Copilot SDK
  per its install guide; this sample depends on it.
- **No delta chunks emitted** — check that the Copilot SDK is emitting
  `AssistantMessageDeltaData` (older builds may only emit
  `AssistantMessageData` at end of turn; the handler falls back to a
  single chunk in that case).
- **Recovered turn replays nothing** — older Copilot SDK builds
  without `session.get_messages()` will skip the replay safely (no
  crash). Verify your SDK build supports the API.
- **Same user message sent twice** — confirm
  `session.get_messages()` is reachable; without it the handler
  cannot dedup and will re-send on every recovery lifetime.
