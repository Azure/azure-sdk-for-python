# Durable Responses Developer Guide

This guide explains how to build crash-recoverable response handlers using the
durable background responses feature. It covers what the framework provides
automatically, what developers need to implement, and best practices.

## Overview

When `durable_background=True` (the default), the framework automatically wraps
your response handler in a **durable task**. If the server crashes mid-response:
- Background responses are automatically re-invoked on restart
- Stream events are preserved for client reconnection
- Conversation state is maintained across crashes

**You get crash recovery with zero code changes to your handler.**

## What the Framework Provides (Zero Code)

| Feature | Behavior |
|---------|----------|
| Crash recovery | Handler re-invoked on server restart |
| Stream replay | Events persisted incrementally; clients reconnect seamlessly |
| Conversation lock | Prevents conflicting concurrent writes |
| Non-bg cleanup | Foreground responses marked `failed` on crash (no ghost re-invocation) |
| TTL-based cleanup | Stream events auto-expire after configurable window |

## Decision Tree

### Do you need metadata checkpointing?

If your handler does expensive work and you want to resume from where you left
off (rather than re-running from scratch), use **durability metadata**:

```python
@app.response_handler
async def handler(request, context, cancel):
    durability = context.durability
    
    # Resume from last checkpoint
    step = durability.metadata.get("last_step", 0) if durability else 0
    
    for i in range(step, total_steps):
        # Do work...
        durability.metadata["last_step"] = i + 1  # Auto-flushed by framework
```

### Do you need multi-turn conversations?

Enable steerable conversations for agents that maintain context across turns:

```python
options = ResponsesServerOptions(
    durable_background=True,
    steerable_conversations=True,
)
```

With steering enabled:
- Each turn shares the same durable task (conversation continuity)
- New turns can cancel the current in-progress turn
- The `pending_inputs` count tells you how many turns are queued

### Do you need a custom acceptance hook?

When a new turn arrives while another is in progress, the framework returns a
"queued" response. Customize this with `@app.response_acceptor`:

```python
@app.response_acceptor
def my_acceptor(request, context):
    return {
        "status": "queued",
        "id": context.response_id,
        "message": "Your request is queued behind the current response",
    }
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `durable_background` | `True` | Enable crash-recoverable background responses |
| `steerable_conversations` | `False` | Enable multi-turn steering with cooperative cancel |
| `store_disabled` | `False` | Disable response persistence |
| `max_pending` | `10` | Max queued turns for steerable conversations |
| `replay_event_ttl_seconds` | `600` | How long stream events remain replayable (seconds) |

## Configuration Matrix

Recovery semantics depend on three request flags and one server option. This
matrix is the authoritative reference for "what guarantee applies in my case."

| `store` | `background` | `durable_background` | Guarantee on crash |
|---|---|---|---|
| `true` | `true` | `True` | **Full recovery contract** applies. Handler is re-invoked with `entry_mode="recovered"`. Persisted events replay to reconnecting clients. See [Crash Recovery](#crash-recovery). |
| `true` | `true` | `False` | Response is marked `failed` on restart. Handler is NOT re-invoked. Events that were persisted before the crash remain replayable until TTL expires. |
| `true` | `false` (foreground) | any | Response is marked `failed` with `code=server_crashed`. Handler is NOT re-invoked (the client's HTTP connection is already dead). Persisted events remain queryable. |
| `false` | any | any | Best-effort `failed` marker during shutdown grace period. No persistence. Recovery does not apply. |

`steerable_conversations=True` composes orthogonally: it enables multi-turn
steering on top of any row above. Recovery composes with steering — see the
[handler guide's Recovery × Cancellation Composition](handler-implementation-guide.md#recovery--cancellation-composition).

## DurabilityContext API

When `durable_background=True`, `context.durability` provides:

```python
durability = context.durability

# Convenience: True if this is a re-invocation after crash.
if durability.is_recovery:
    # Recovery code path — build a resumption response, emit reset in_progress.
    ...

# Raw entry mode literal: "fresh" or "recovered". Use is_recovery for the
# common case; use entry_mode for the rare "I need to distinguish from a
# resumed steerable turn" case.
print(durability.entry_mode)

# Metadata: small JSON-serializable dict, persisted across crashes and turns.
# Auto-flushed by the framework — no manual save needed.
durability.metadata["my_checkpoint_id"] = "abc-123"

# Run attempt counter: 0 on first invocation, 1 on first recovery, etc.
print(f"Attempt #{durability.run_attempt}")

# Pending inputs (steerable mode only): how many newer turns are queued.
print(f"{durability.pending_inputs} turns waiting")
```

There is intentionally no `last_snapshot` property. The library only persists
the response object at `response.created` and at the terminal event — between
those points it persists the SSE event stream (for client replay), not a
running `ResponseObject`. So there is no useful "what did the prior attempt
look like" snapshot for the library to hand you. The resumption response is
your responsibility to compose from upstream state.

### Notes on Metadata

- Keys are auto-flushed by the framework. No manual save needed.
- Keys prefixed with `_framework.` are reserved (hidden from your view).
- Metadata survives crashes — use it for small watermarks (session IDs,
  checkpoint references, "side effect issued" flags).
- Keep values JSON-serializable (strings, numbers, lists, dicts).
- **DO NOT** store conversation history, LLM outputs, or any bulk data in
  metadata. Use the upstream framework's own storage (session JSONL,
  checkpoint DB, etc.) for that.

## Building a Resumption Response

The resumption response is a `ResponseObject` you build on a recovered entry,
reflecting only what is durably committed at your resumption point. It's
constructed from:

- The upstream framework's persisted state (Claude session JSONL, Copilot
  session events, LangGraph SqliteSaver checkpoints, etc.).
- Your own metadata watermarks that disambiguate "we did this" from "we
  didn't".

You pass it to `ResponseEventStream(response=resumption_response)`. The
handler's `response.in_progress` event then carries it as the client-visible
reset point.

The library cannot compose this for you — only you know which prior-attempt
items your upstream framework actually committed. See the handler guide's
[Resumption Response Construction](handler-implementation-guide.md#resumption-response-construction)
for a worked example.

## Crash Recovery

Re-entry is governed by the recovery contract documented in the
[handler guide's Durability section](handler-implementation-guide.md#durability).
That document is the canonical mental model and the prescribed patterns.
This section adds the configuration / API context.

### What you get on recovered entry

- `context.durability.is_recovery == True`
- `context.durability.run_attempt > 0`
- `context.durability.metadata` carrying whatever watermarks you stamped
- The cancellation contract from [Spec 011](handler-implementation-guide.md#cancellation) continues to apply. If the prior attempt was cancelled (steering, client cancel, shutdown), the signal is pre-set with the appropriate `cancellation_reason` on re-entry.

### What you owe on recovered entry

- Build a resumption response from upstream framework state + your metadata.
- Construct `ResponseEventStream(response=resumption_response)`.
- Emit `response.in_progress` (this is the client-visible reset point).
- Use the upstream framework's native resume / fork facility before any
  side-effecting call.
- Honour your watermarks: don't re-issue a side-effecting upstream call
  whose watermark is still set from the prior attempt.

### Naive opt-out

A handler that does nothing recovery-specific still produces a correct
response. The library accepts duplicate `response.created` events, treats
the first non-empty `response.in_progress` after a duplicate as the reset
point, and re-streams everything fresh. The only real risk is duplicating
side effects against the upstream framework (LLM calls, session writes)
— if you have any of those, you MUST adopt the recovery-aware pattern.

## Stream Recovery (client-side reconciliation)

The library persists every SSE event in order. Reconnecting clients use
the standard `starting_after=` query parameter to resume:

```
GET /responses/{id}?stream=true&starting_after=42
```

This returns only events with `sequence_number > 42`.

### The reset-on-`in_progress` rule

Clients that want to support durable+background recovery MUST observe the
following rule:

> **Any `response.in_progress` event received after the first one in a
> stream is a snapshot reset.** Replace the local `response.output` with
> the event's `response.output`. Discard any partial in-flight item
> content you had been accumulating. Treat subsequent events as additive
> on top of the new snapshot.

This rule applies whether the client is reading the live stream or
replaying via `starting_after=`. The reset event is in-band — no
separate signal is needed.

### Output indexes are slot IDs, not monotonic counters

After a snapshot reset, the handler MAY re-use `output_index` values that
appeared before the reset. Clients MUST treat indexes as authoritative
slot identifiers:

- `output_item.added` at an index already present in the snapshot →
  replace the slot.
- `output_item.added` at a new index → append a slot.
- Subsequent `output_item.delta` / `output_item.done` apply to the slot
  identified by `output_index`.

Clients that assume indexes are strictly monotonic will see a coherent
final response but may render intermediate states incorrectly.

## Non-Background Response Behavior

When `background=false` (foreground streaming):

- Response is tied to the HTTP connection lifetime.
- If the server crashes: response is marked `failed` with `code=server_crashed`.
- The handler is NOT re-invoked (client is already disconnected).
- Conversation lock still applies (prevents concurrent modifications).

## Composition with Specs 010 and 011

This guide and the handler guide together implement three layered specs:

- **Spec 010 — Responses Durable Background** provides the runtime
  primitives (`DurabilityContext`, task store wiring, `entry_mode`,
  steerable conversation orchestration).
- **Spec 011 — Cancellation Redesign** provides the `CancellationReason`
  enum and the Phase 1 / 2 / 3 cancellation policy (no `cancelled` from
  steering or shutdown, no `incomplete` from framework, framework-set
  `failed` for naive-not-handled cancellation).
- **Spec 012 — Durable Response Recovery Contract** (this work) provides
  the multi-attempt reconciliation pattern: resumption response, snapshot
  reset on `response.in_progress`, watermark-guarded side effects, naive
  fallback.

The three compose cleanly: Spec 010 surfaces the recovery hooks, Spec 011
provides the cancellation policy that recovered handlers must honour, and
Spec 012 prescribes how the recovered attempt produces coherent output.

## Best Practices

1. **Make `is_recovery` the first check.** A recovery-aware handler diverges
   from a fresh handler at this branch — keep the divergence at the top of
   the function so the two paths are easy to read in isolation.

2. **Use upstream framework's resume facility.** Claude SDK has `resume=` and
   `fork_session=True`; Copilot SDK has `create_session(session_id=...)`;
   LangGraph has `SqliteSaver` checkpoints. Use them. Don't try to recreate
   upstream state from your own metadata.

3. **Watermark before side effects.** Stamp `durability.metadata` with a
   "this side effect is in flight" flag BEFORE calling an upstream API that
   has observable side effects (sending a user message, writing a checkpoint).
   Clear it AFTER the upstream durably committed the result.

4. **Keep metadata small.** Watermarks, session IDs, checkpoint references.
   Never bulk data.

5. **Honour the cancellation policy.** Recovery doesn't change the
   cancellation contract from [Spec 011](handler-implementation-guide.md#cancellation).
   Phase 1 / Phase 2 / Phase 3 cancellation logic still applies to recovered
   entries.

6. **Don't store secrets in metadata.** The task store persists it.

## Examples

See the `samples/` directory for canonical durable handler shapes:

- `sample_17_durable_claude.py` — Stateful Claude Agent SDK conversation
  (session resume + `fork_session` on recovery).
- `sample_18_durable_copilot.py` — Stateful GitHub Copilot SDK conversation
  (session resume on recovery).
- `sample_19_durable_streaming.py` — Handler-managed checkpointing
  (no upstream framework).
- `sample_20_durable_steering.py` — Steerable variant of 19, demonstrating
  cancellation × recovery composition.
- `sample_21_durable_langgraph.py` — LangGraph with `SqliteSaver`
  checkpointer (upstream-framework-owned durability).
