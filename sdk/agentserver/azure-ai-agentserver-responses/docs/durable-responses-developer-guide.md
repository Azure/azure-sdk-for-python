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

### What is `durability.metadata` for?

`durability.metadata` is a **small key-value store of references and
watermarks** — it is NOT a place to keep your application's checkpoint
data.

Use it for things like:

- An upstream session UUID (Claude `session_id`, Copilot session id, a
  LangGraph thread id).
- A small pointer to your most recently processed input or output (e.g.
  `last_processed_input_item_id`).
- A short workflow step counter (`step: 3`) so the recovered handler
  knows where to resume.

The actual checkpoint *data* — graph state, conversation history,
generated content, intermediate work — lives in the upstream framework
or in your own external storage (Redis, Cosmos DB, files on disk). The
metadata pointer is what lets the recovered handler find that data.

```python
@app.response_handler
async def handler(request, context, cancel):
    durability = context.durability

    # Small watermark: which workflow step is next?
    step = int(durability.metadata.get("workflow_step", 0))

    for i in range(step, total_steps):
        # Do work — write any bulk data to your upstream store directly,
        # NOT to durability.metadata.
        await upstream_store.write_step_result(i, result)
        durability.metadata["workflow_step"] = i + 1  # auto-flushed
```

Why this distinction matters: metadata is persisted alongside the
durable task — small writes are cheap and fast, but bulk writes will
hit task-store payload limits and slow down recovery. Treating metadata
as a checkpoint *index* (not a checkpoint *store*) keeps it fast and
keeps your actual durable data in the storage system best suited to it.

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
| `replay_event_ttl_seconds` | `600` | How long stream events remain replayable (seconds) |

## Configuration Matrix

Recovery semantics depend on three request flags and one server option. The
table below is a quick orientation. For the **normative** specification — the
exact behaviour you can rely on per row, per termination path, and per
stream/poll mode — see
[`responses-durability-spec.md`](responses-durability-spec.md). That document
is the source of truth; this section summarises it for developer ergonomics.

| `store` | `background` | `durable_background` | Summary |
|---|---|---|---|
| `true` | `true` | `True` | **Full recovery.** Handler is re-invoked with `entry_mode="recovered"`. Persisted events replay to reconnecting clients. See [Crash Recovery](#crash-recovery). |
| `true` | `true` | `False` | **Failed marker.** Response is marked `failed` on restart. Handler is NOT re-invoked. Pre-crash persisted events remain replayable until TTL expires. |
| `true` | `false` (foreground) | any | **Failed marker.** Response is marked `failed` with `code=server_error`. Handler is NOT re-invoked (the client's HTTP connection is already dead). Persisted events remain queryable. |
| `false` | any | any | **Best-effort failed marker** during shutdown grace period only. No persistence. Recovery does not apply. |

Each row × termination-path cell — Path A (handler completes within grace),
Path B (grace exhausted, in-process marker fires), Path C (crash or Path-B
failure, next-lifetime recovery fires) — is covered by a dedicated
conformance test in `tests/e2e/durability_contract/`. If something behaves
differently from what the spec says, that's a bug in either the implementation
or the spec — open an issue.

`steerable_conversations=True` composes orthogonally: it enables multi-turn
steering on top of any row above. Recovery composes with steering — see the
[handler guide's Recovery × Cancellation Composition](handler-implementation-guide.md#recovery--cancellation-composition).

### Steerable conversations: no forking

When `steerable_conversations=True`, each turn after the first must reference
the previous turn's `response_id` via `previous_response_id`. The framework
rejects forks with HTTP 409:

```json
{
  "error": {
    "message": "Conversation forking is not supported — previous_response_id must reference the most recent turn.",
    "type": "conflict",
    "code": "conversation_fork_not_supported",
    "param": "previous_response_id"
  }
}
```

This includes both stale-predecessor cases (you sent a `previous_response_id`
that refers to a turn other than the most recent one) and concurrent races
(two POSTs arrive together with the same `previous_response_id` — exactly one
wins; the other gets the 409). There is no soft path through; a steerable
conversation cannot be branched.

The check is enforced by the core durable layer's input-precondition primitive
under the hood — see the core `durable-task-guide.md` §4 (Concepts → "Input-acceptance
preconditions") for the underlying mechanism. From a
responses-API consumer's perspective: keep `previous_response_id` pointing at
the latest `response_id` you have seen for this conversation.

### Provider configuration for local-dev recovery testing

Real cross-process recovery requires durable storage that survives subprocess
restarts. For local development:

- **Durable task store**: use `LocalDurableProvider` (writes JSON under a chosen
  filesystem path). The default in-memory provider does not survive a restart.
- **Response store**: use `FileResponseStore(storage_dir=…)`. The default
  in-memory provider does not survive a restart, so a recovered handler would
  always see an empty store and false-positive on the "fresh attempt" path.
  Use the file store when you want to exercise the idempotent
  `response.created` swallow on recovery.
- **Stream event store**: use `FileStreamProvider`. Same rationale.

All three providers accept a directory path. Wire them against the same root
for a consistent local crash-recovery setup. For production, your deployment
hosts these stores externally — typically via the Foundry providers, which are
auto-configured when `FOUNDRY_PROJECT_ENDPOINT` is set.

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
# Use namespaces to keep distinct concerns isolated:
#   durability.metadata["key"]            -- default namespace
#   durability.metadata("name")["key"]    -- named (sibling) namespace
# Call await durability.metadata.flush() before any side effect that depends
# on the write surviving a crash. Snapshots also happen at lifecycle
# boundaries automatically.
durability.metadata["my_checkpoint_id"] = "abc-123"

# Run attempt counter: 0 on first invocation, 1 on first recovery, etc.
print(f"Attempt #{durability.retry_attempt}")

# Pending inputs (steerable mode only): how many newer turns are queued.
print(f"{durability.pending_inputs} turns waiting")
```

### Conversation chain identity

`ResponseContext.conversation_chain_id: str` exposes the framework-computed
conversation chain identifier — the stable id every turn in a multi-turn
conversation shares (and the same value the framework uses internally to
partition durable tasks). Handlers that wrap a stateful upstream framework
(Claude SDK, Copilot SDK, LangGraph, …) can use this as their upstream session
id without allocating their own UUIDs:

```python
session = await upstream_client.create_or_resume_session(
    session_id=context.conversation_chain_id,
)
```

The value is derived as follows (same rule the framework uses internally):

1. If the request has a `conversation_id`, return it.
2. Else if `steerable_conversations=True` and the request has a
   `previous_response_id`, return it (so every turn in a steerable conversation
   returns the same value).
3. Else return a deterministic derivative of `response_id` (so first-turn
   handlers always get a non-None identity).

Stable across all attempts of a given task (fresh, recovered, multiply-recovered).

There is intentionally no `last_snapshot` property. The library only persists
the response object at `response.created` and at the terminal event — between
those points it persists the SSE event stream (for client replay), not a
running `ResponseObject`. So there is no useful "what did the prior attempt
look like" snapshot for the library to hand you. The resumption response is
your responsibility to compose from upstream state.

### Notes on Metadata

- The metadata API is a **callable namespace facade**. Use `durability.metadata["key"] = value` for the default namespace; use `durability.metadata("name")["key"] = value` for a sibling namespace (each namespace tracks dirty state independently and can be `await durability.metadata("name").flush()`-ed in isolation).
- Persistence is **explicit**, not auto-flushed. Call `await durability.metadata.flush()` (or `await durability.metadata("name").flush()`) before any side effect that depends on a metadata write surviving a crash. The framework also snapshots all touched namespaces at lifecycle boundaries (start/suspend/complete/fail/cancel/terminate), so values written and forgotten will still be visible on a clean recovery — but the fence for at-most-once side-effect patterns is your explicit `flush()`.
- Keys and namespace names **starting with `_` are rejected** (raise `ValueError`). Those prefixes are reserved for framework-internal namespaces (e.g. `_responses` for the responses orchestrator) — pick your own prefix-free names.
- Metadata survives crashes — use it for small watermarks (session IDs, checkpoint references, "side effect issued" flags).
- Keep values JSON-serializable (strings, numbers, lists, dicts).
- **DO NOT** store conversation history, LLM outputs, or any bulk data in metadata. Use the upstream framework's own storage (session JSONL, checkpoint DB, etc.) for that.

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
- `context.durability.retry_attempt > 0`
- `context.durability.metadata` carrying whatever watermarks you stamped
- The cancellation contract from the [Cancellation guide](handler-implementation-guide.md#cancellation) continues to apply. If the prior attempt was cancelled (steering, client cancel, shutdown), the signal is pre-set with the appropriate `cancellation_reason` on re-entry.
- The framework guarantees the response object is persisted **exactly once** at the first attempt's `response.created` and **exactly once** at the first attempt that reaches a terminal event. Subsequent attempts' `response.created` and terminal events are deduplicated by the framework keyed on `response_id`; you don't need to do anything special. The SSE event stream is persisted as you emit it (no dedup).

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

The library persists every SSE event in order — including events emitted
across multiple recovery attempts. Reconnecting clients use the standard
`starting_after=` query parameter to resume:

```
GET /responses/{id}?stream=true&starting_after=42
```

This returns only events with `sequence_number > 42`.

The post-recovery part of this guarantee is normative per
[`responses-durability-spec.md`](responses-durability-spec.md): for
`(store=true, background=true, durable_background=True, stream=true)` —
the row that supports handler re-invoke — a client reconnecting AFTER a
crash receives the events the recovered handler emits, framed by the
reset-on-`in_progress` rule below. The conformance suite covers this
under Row 1 Path C.

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

## Layered Concerns

This guide and the handler guide together describe three layered concerns
that compose to give you durable response handlers:

- **The durable background runtime** provides the runtime primitives
  (`DurabilityContext`, task store wiring, `entry_mode`, steerable
  conversation orchestration).
- **The cancellation contract** provides the `CancellationReason`
  enum and the pre-entry / mid-stream / post-stream rules
  (no `cancelled` from steering or shutdown, no `incomplete` from
  framework, framework-set `failed` for naive-not-handled cancellation).
- **The recovery contract** provides the multi-attempt
  reconciliation pattern: resumption response, snapshot reset on
  `response.in_progress`, watermark-guarded side effects, naive
  fallback.

The three compose cleanly: the runtime surfaces the recovery hooks, the
cancellation contract is what recovered handlers must honour, and the
recovery contract prescribes how the recovered attempt produces coherent
output.

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

5. **Honour the cancellation contract.** Recovery doesn't change the
   cancellation contract from the [Cancellation guide](handler-implementation-guide.md#cancellation):
   the same pre-entry / mid-stream / shutdown rules apply on recovered
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
