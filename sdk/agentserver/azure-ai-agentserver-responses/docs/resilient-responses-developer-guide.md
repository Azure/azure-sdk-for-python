# Resilient Responses Developer Guide

This guide explains how to build crash-recoverable response handlers using the
resilient background responses feature. It covers what the framework provides
automatically, what developers need to implement, and best practices.

## Overview

When `resilient_background=True` (opt-in — the default is `False`), the
framework automatically wraps your response handler in a **resilient
task**. If the server crashes mid-response:

- Background responses are automatically re-invoked on restart
- Stream events are preserved for client reconnection
- Conversation state is maintained across crashes

**Opting in (`resilient_background=True`) gets you the framework half for
free**: re-invocation on restart, event replay for reconnecting clients, and
conversation continuity — with no handler changes. A naive handler re-invoked
this way still produces a correct response (it just re-runs the whole turn).
The *handler* half — making the recovered attempt resume *where it left off*
and not repeat non-idempotent side effects — is optional work you take on when
you want it; see [Choosing a resume strategy](#choosing-a-resume-strategy).

> **Default**: `resilient_background` defaults to `False`. Without the
> opt-in, a crash mid-handler leaves the response in the
> "crash-failed" state: the next-lifetime recovery scanner marks it
> `failed` (`error.code="server_error"`) instead
> of re-invoking the handler. Set `resilient_background=True` on
> `ResponsesServerOptions` to engage the re-invoke recovery path.

## What the Framework Provides (Zero Code)

| Feature | Behavior |
|---------|----------|
| Crash recovery | Handler re-invoked on server restart (requires `resilient_background=True`) |
| Stream replay | Events persisted incrementally; clients reconnect seamlessly |
| Conversation lock | Prevents conflicting concurrent writes |
| Non-bg cleanup | Foreground responses marked `failed` on crash (no ghost re-invocation) |
| TTL-based cleanup | Stream events auto-expire after 10 minutes (framework-internal) |

## Decision Tree

### What is `context.conversation_chain_metadata` for?

`context.conversation_chain_metadata` is a **small key-value store of references
and watermarks** — it is NOT a place to keep your application's
checkpoint data.

Use it for things like:

- An upstream session UUID (Copilot session id, a
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
async def handler(request, context, cancellation_signal):
    # Small watermark: which workflow step is next?
    step = int(context.conversation_chain_metadata.get("workflow_step", 0))

    for i in range(step, total_steps):
        # Do work — write any bulk data to your upstream store directly,
        # NOT to context.conversation_chain_metadata.
        await upstream_store.write_step_result(i, result)
        # Advance the watermark, then explicitly flush so the next
        # process lifetime (after a crash) skips the already-committed
        # step. Persistence is not implicit — flush before any side
        # effect whose effect must survive a crash.
        context.conversation_chain_metadata["workflow_step"] = i + 1
        await context.conversation_chain_metadata.flush()
```

Why this distinction matters: metadata is persisted alongside the
resilient task — small writes are cheap and fast, but bulk writes will
hit task-store payload limits and slow down recovery. Treating metadata
as a checkpoint *index* (not a checkpoint *store*) keeps it fast and
keeps your actual resilient data in the storage system best suited to it.

### Do you need multi-turn conversations?

Enable steerable conversations for agents that maintain context across turns:

```python
options = ResponsesServerOptions(
    resilient_background=True,
    steerable_conversations=True,
)
```

With steering enabled:
- Each turn shares the same resilient task (conversation continuity)
- New turns can cancel the current in-progress turn
- The `pending_input_count` field tells you how many turns are queued

### Do you need a custom acceptance hook?

When a new turn is queued onto an **already-active steerable conversation**
(steering pressure — never the first turn of a conversation), the framework
returns a "queued" response to that POST. By default it's a minimal
`status="queued"` envelope. Register `@app.response_acceptor` to customize it
— the hook returns a strongly-typed `ResponseObject`:

```python
from azure.ai.agentserver.responses import (
    CreateResponse, ResponseContext, ResponseObject,
)

@app.response_acceptor
def my_acceptor(request: CreateResponse, context: ResponseContext) -> ResponseObject:
    return ResponseObject(
        {
            "id": context.response_id,
            "object": "response",
            "status": "queued",
        }
    )
```

This is optional — the default queued envelope is fine for most agents. See
the handler guide's
[steering API](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#steering-api) for the hook
mechanics.

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `resilient_background` | `False` | Opt INTO crash-recoverable background responses |
| `steerable_conversations` | `False` | Enable multi-turn steering with cooperative cancel |

## Configuration Matrix

Recovery semantics depend on three request flags and one server option. The
table below is a quick orientation. For the **normative** specification — the
exact behaviour you can rely on per row, per termination path, and per
stream/poll mode — see
[`responses-resilience-spec.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/responses-resilience-spec.md). That document
is the source of truth; this section summarises it for developer ergonomics.

| `store` | `background` | `resilient_background` | Summary |
|---|---|---|---|
| `true` | `true` | `True` | **Full recovery.** Handler is re-invoked with `context.is_recovery == True`. Persisted events replay to reconnecting clients. See [Crash Recovery](#crash-recovery). |
| `true` | `true` | `False` (default) | **Failed marker.** Response is marked `failed` on restart. Handler is NOT re-invoked. Pre-crash persisted events remain replayable until TTL expires. |
| `true` | `false` (foreground) | any | **Failed marker.** Response is marked `failed` with `code=server_error`. Handler is NOT re-invoked (the client's HTTP connection is already dead). Persisted events remain queryable. |
| `false` | any | any | **Best-effort failed marker** during shutdown grace period only. No persistence. Recovery does not apply. |

Each row × termination-path cell — Path A (handler completes within grace),
Path B (grace exhausted, in-process marker fires), Path C (crash or Path-B
failure, next-lifetime recovery fires) — is covered by a dedicated
conformance test in `tests/e2e/resilience_contract/`. If something behaves
differently from what the spec says, that's a bug in either the implementation
or the spec — open an issue.

`steerable_conversations=True` composes orthogonally: it enables multi-turn
steering on top of any row above. Recovery composes with steering — see the
[handler guide's Recovery × Cancellation Composition](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#recovery--cancellation-composition).

> **`conversation_id` chains**: when a request supplies
> `conversation_id`, sequential turns extend the chain even when
> `steerable_conversations=False`. Only **concurrent overlap** (a new
> turn arriving while a prior turn's handler is still in progress)
> returns 409 `conversation_locked`. This is independent of the
> `steerable_conversations` option — that option only controls whether
> mid-turn inputs are queued (steerable) or rejected (non-steerable).

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

The check is enforced by the core resilient layer's input-precondition primitive
under the hood — see the core `tasks-guide.md` §4 (Concepts → "Input-acceptance
preconditions") for the underlying mechanism. From a
responses-API consumer's perspective: keep `previous_response_id` pointing at
the latest `response_id` you have seen for this conversation.

### Provider configuration for local-dev recovery testing

Real cross-process recovery requires persistent storage that survives subprocess
restarts. The framework defaults provide this automatically; the
sections below describe what they do and how to override them for
specific scenarios.

- **Resilient task store**: in a hosted environment the framework uses
  the Foundry task storage API; in local development it auto-selects
  a file-backed task store under
  `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/tasks/`. Either way, tasks
  survive process restarts so a recovered handler re-enters its prior
  task body. Operators can override the auto-selection by setting
  `AGENTSERVER_TASKS_BACKEND=local` (to force file-backed in hosted)
  or `AGENTSERVER_TASKS_BACKEND=hosted` (to force the hosted API in
  local).
- **Response store**: in a hosted environment the framework uses the
  Foundry hosted responses storage API; in local development the
  default is `FileResponseStore` under
  `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/responses/`. No explicit
  construction needed in either case. `InMemoryResponseProvider`
  remains importable for in-memory-specific unit tests. To target a
  different directory in local development, pass
  `store=FileResponseStore(storage_dir=…)` to `ResponsesAgentServerHost`.
- **Stream event store**: configured automatically — file-backed when
  `resilient_background=True`, in-memory otherwise. Files land under
  `${AGENTSERVER_STATE_ROOT:-~/.agentserver}/streams/`. No per-store env
  var to set; the unified `AGENTSERVER_STATE_ROOT` covers all three
  local subdirs (`tasks/`, `streams/`, `responses/`).

For production, your deployment hosts the response store externally —
typically via the Foundry response provider, which is auto-configured
when `FOUNDRY_PROJECT_ENDPOINT` is set. The stream event store
continues to use the framework's file-backed registry under
`${AGENTSERVER_STATE_ROOT}/streams/` (the resilient-task primitive
owns the equivalent migration for its task store).

## Recovery + steering surface on `ResponseContext`

When `resilient_background=True`, the framework populates flat fields
on the response context for every handler invocation. The fields
mirror the underlying task primitive's classifiers and are safe to
read regardless of `is_recovery`:

> **Recovered inputs are identical to fresh entry.** On a recovered
> re-invocation the handler observes the *same* `request`, `client_headers`,
> `query_parameters`, and `await context.get_input_items()` it saw on fresh
> entry — nothing is dropped or altered. The only differences are
> `context.is_recovery == True` and the entry-only `context.persisted_response`
> snapshot. So recovery-aware code only needs to branch on `is_recovery`; it
> never has to re-fetch or reconstruct the request itself.

```python
@app.response_handler
async def handler(request, context, cancellation_signal):
    # True if this invocation is a re-entry after a crash.
    if context.is_recovery:
        # Recovery code path — build a resumption response, emit a
        # reset response.in_progress event, continue from the last
        # checkpoint your handler's metadata watermark recorded.
        ...

    # True only on the drain re-entry that follows a steering input
    # (steerable_conversations=True). NOT set on the cancelled
    # current turn that produced the steering pressure.
    if context.is_steered_turn:
        ...

    # Number of additional steering inputs queued behind this turn.
    # Live count — decreases as the framework drains the queue.
    print(f"{context.pending_input_count} turns waiting")

    # Persistent metadata namespace. Safe across crashes and turns.
    # The default namespace is `context.conversation_chain_metadata["key"]`;
    # named namespaces are `context.conversation_chain_metadata("name")["key"]`.
    # Call `await context.conversation_chain_metadata.flush()` before any side
    # effect that depends on the write surviving a crash. Snapshots
    # also happen at lifecycle boundaries automatically.
    context.conversation_chain_metadata["my_checkpoint_id"] = "abc-123"
```

These fields are always present on the context (even for `store=false`
Row 4 responses, where the metadata facade is backed by an in-memory
mapping that evaporates on restart).

### Conversation chain identity

`ResponseContext.conversation_chain_id: str` is a **derived, stable chain
identifier**: the framework computes it so that **every turn of the same
conversation resolves to the same value**, and so it stays constant across all
attempts of a turn (fresh, recovered, multiply-recovered). It is the same value
the framework uses internally to partition resilient tasks. Think of it as "the
stable name of this conversation", not as any single request field.

It's derived by anchoring to the conversation's root rather than to the current
turn: a `conversation_id` (explicit conversation scope) or the head of a
`previous_response_id` chain pins every turn to one identifier; a first turn that
has neither falls back to its own `response_id` as the chain root. The point of
the derivation is that pinning — so you get **one resilient key per conversation**,
not a new one per turn.

Handlers that wrap a stateful upstream framework (Copilot SDK, LangGraph, …) can
use it as their upstream session id — a convenient way to avoid allocating (and
persisting) your own UUID, though you're free to use your own identifier:

```python
session = await upstream_client.create_or_resume_session(
    session_id=context.conversation_chain_id,
)
```

What snapshot does the library hand you on recovery? It depends on your resume
model (see [Choosing a resume strategy](#choosing-a-resume-strategy)):

- If you use **framework checkpoints** (`stream.checkpoint()`), the library
  persists the response snapshot at `response.created`, at each checkpoint, and
  at the terminal event — and exposes the **last** such snapshot on a recovered
  entry as `context.persisted_response`. That snapshot is your watermark.
- If your resilient state lives in an **upstream framework/store**, the library
  does not hold a useful in-flight snapshot of the crashed attempt — you build
  the resumption response from the upstream's state.

Either way, the library never keeps a *running* snapshot of in-flight items
between persistence points; what it persists is the SSE event stream (for
client replay) plus the snapshot at each of the points above.

### Notes on `context.conversation_chain_metadata`

- The metadata API is a **callable namespace facade**. Use
  `context.conversation_chain_metadata["key"] = value` for the default namespace;
  use `context.conversation_chain_metadata("name")["key"] = value` for a sibling
  namespace (each namespace tracks dirty state independently and can be
  `await context.conversation_chain_metadata("name").flush()`-ed in isolation).
- Persistence is **explicit**, not auto-flushed. Call
  `await context.conversation_chain_metadata.flush()` (or
  `await context.conversation_chain_metadata("name").flush()`) before any side
  effect that depends on a metadata write surviving a crash. The
  framework also snapshots all touched namespaces at lifecycle
  boundaries (start/suspend/complete/fail/cancel/terminate), so values
  written and forgotten will still be visible on a clean recovery — but
  the fence for at-most-once side-effect patterns is your explicit
  `flush()`.
- Keys and namespace names **starting with `_` are rejected** (raise `ValueError`). Those prefixes are reserved for framework-internal use — pick your own prefix-free names.
- Metadata survives crashes — use it for small watermarks (session IDs, checkpoint references, "side effect issued" flags).
- Keep values JSON-serializable (strings, numbers, lists, dicts).
- **DO NOT** store conversation history, LLM outputs, or any bulk data in metadata. Use the upstream framework's own storage (session JSONL, checkpoint DB, etc.) for that.

## Choosing a resume strategy

When the framework re-invokes your handler after a crash
(`context.is_recovery == True`), how the recovered attempt resumes coherently is
**your choice**, driven by one question: **where does your resilient progress
state live?**

| Where state lives | Strategy | On recovery |
|---|---|---|
| Nowhere (cheap to re-run) | **Naive re-run** | Do nothing recovery-specific; the whole turn re-runs. Correct, just duplicative — only unsafe if it repeats non-idempotent side effects. |
| In the response snapshot | **Framework checkpoint** | Emit one `OutputItem` per phase + `yield stream.checkpoint()`. `context.persisted_response` is the last snapshot — seed the stream from it and resume past the items already there. |
| In an upstream framework/store | **Upstream-owned** | Rebuild a resumption `ResponseObject` from the upstream's state (Copilot session, LangGraph checkpoint, your DB) and emit it as the reset. |

Minimal skeletons (full templates are in the handler guide's
[Resilience section](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#resilience)):

```python
# Framework checkpoint — state lives in the response snapshot
if context.is_recovery and context.persisted_response is not None:
    stream = ResponseEventStream(response=context.persisted_response,
                                 response_id=context.response_id)
    start = len(stream.response.output)          # resume past checkpointed phases
else:
    stream = ResponseEventStream(request=request, response_id=context.response_id)
    start = 0

# Upstream-owned — state lives in your framework/store
resumption = build_response_from(upstream.load(context.conversation_chain_id))
stream = ResponseEventStream(response=resumption, response_id=context.response_id)
```

**Watermark overlay (composable — not a fourth strategy).** Independently of the
strategy you pick: if your handler makes a **non-idempotent side effect** (sending
a user message upstream, charging a card) that the upstream can't dedup for you,
fence it with a metadata watermark so a recovered attempt doesn't repeat it:

```python
context.conversation_chain_metadata["sent_msg"] = True
await context.conversation_chain_metadata.flush()   # resilient BEFORE the side effect
await upstream.send_message(...)                    # the non-idempotent call
del context.conversation_chain_metadata["sent_msg"]
await context.conversation_chain_metadata.flush()   # clear AFTER it persisted
```

These compose: a handler may checkpoint its response output **and** watermark a
non-response side effect in the same turn.

## Crash recovery — what you get, what you owe

Re-entry is governed by the recovery contract in the
[handler guide's Resilience section](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#resilience)
(the canonical mental model and worked templates). This section is the
configuration / decision context.

### What you get on recovered entry

- `context.is_recovery == True`, plus `context.persisted_response` — the last
  resiliently-persisted snapshot (last `stream.checkpoint()`, else the
  `response.created` snapshot, else `None`).
- `context.conversation_chain_metadata` carrying whatever watermarks you stamped.
- The cancellation contract from the [Cancellation guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#cancellation) continues to apply. If the prior attempt was cancelled (steering, client cancel, shutdown), the cancel surface is pre-set with the appropriate cause-boolean (`context.client_cancelled` for explicit cancel / non-bg disconnect; `context.shutdown.is_set()` for graceful shutdown; neither for steering pressure) on re-entry.
- The framework persists the response object at `response.created`, at **each
  successful `stream.checkpoint()`**, and at the terminal event; the
  `response.created` and terminal writes are **deduplicated** across recovery
  attempts keyed on `response_id`, so you never branch for them. The SSE event
  stream is persisted as you emit it (no dedup) — except that a recovered
  handler's re-emitted `response.created` is **not** re-appended to the
  already-non-empty resilient stream, so a replaying client sees `response.created`
  exactly once.

### What you owe on recovered entry (only if you chose a non-naive strategy)

- Seed or build your resumption response (framework-checkpoint: from
  `context.persisted_response`; upstream-owned: from upstream state).
- Emit `response.in_progress` early — it is the client-visible reset point.
- For non-idempotent side effects without upstream idempotency, honour your
  watermarks: don't re-issue a call whose watermark is still set from the prior
  attempt.

### Naive opt-out

A handler that does nothing recovery-specific still produces a correct response:
it re-runs from scratch, the recovered stream's first client-visible event is a
fresh `response.in_progress` (the duplicate `response.created` is suppressed at
the resilient stream), and everything re-streams. The one real risk is **repeating
non-idempotent side effects** (a second upstream user message, a double charge) —
if your handler has any, reach for the watermark overlay or a strategy that
resumes past them.

## Checkpoint-driven recovery — one item per phase

When your work decomposes into phases, the simplest correct recovery shape
is **one `OutputItem` per phase + `yield stream.checkpoint()` at each phase
boundary**. The persisted response *is* the watermark: on recovery you seed
the stream from `context.persisted_response` and resume from
`len(stream.response.output)`. A phase that finished (`output_item.done` +
`checkpoint()`) is already in the seeded output; a phase interrupted before
its checkpoint never entered the snapshot, so it re-runs cleanly — no
hand-rolled breadcrumb reconstruction.

```python
from azure.ai.agentserver.responses import (
    CreateResponse, ResponseContext, ResponseEventStream,
)

PHASES = ("gather", "analyze", "synthesize", "review", "publish")


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal):
    # Recovery branch: seed from the persisted snapshot. The completed
    # phases' items are already in stream.response.output; count them to
    # know where to resume.
    if context.is_recovery and context.persisted_response is not None:
        stream = ResponseEventStream(
            response_id=context.response_id, response=context.persisted_response,
        )
        done_phases = len(stream.response.output)
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        done_phases = 0

    yield stream.emit_created()      # framework dedups the duplicate on recovery
    if context.shutdown.is_set():
        await context.exit_for_recovery()
    yield stream.emit_in_progress()  # client-visible reset point on recovery

    prompt = await context.get_input_text()
    for phase_idx in range(done_phases, len(PHASES)):
        message = stream.add_output_item_message()
        message.internal_metadata["phase"] = PHASES[phase_idx]  # stripped on egress
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()
        async for token in run_phase(PHASES[phase_idx], prompt):
            if context.shutdown.is_set():
                await context.exit_for_recovery()  # item not closed → phase re-runs
            yield text.emit_delta(token)
        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()        # item now in stream.response.output
        yield stream.checkpoint()        # phase resilient; on to the next

    yield stream.emit_completed()
```

`yield stream.checkpoint()` persists the current `stream.response`
snapshot (gated to resilient background responses; a no-op otherwise) and is
backpressured — control does not return from the `yield` until the write
completes. See the handler guide's
[Stream Checkpoints](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#stream-checkpoints) for
the full semantics and `resilience-contract.md` Row 11 for the conformance
contract.

### Which metadata facility?

There are **two** internal-metadata facilities at **different scopes**:

- **`context.conversation_chain_metadata`** — **cross-turn**, named-scope,
  explicit-`flush()` resilient state over the whole conversation chain. Use it
  for state a *later turn* needs from an earlier one, or for coordination
  between layers/parallel nodes spanning the chain.
- **`internal_metadata`** (on items via `item.internal_metadata`, and on the
  response via `stream.internal_metadata`) — a **single-turn** live
  `MutableMapping[str, Any]` that rides on the response/items, is persisted
  with the response (so it survives recovery, read back via
  `context.persisted_response`), and is **stripped before every client-facing
  payload** (egress and ingress). Use it for lightweight per-turn watermarks,
  id mappings, or in-turn stale-message detection.

**Rule of thumb:** need it in a *later turn* → `conversation_chain_metadata`;
need it only to reconstruct *this* response on crash →
`internal_metadata` + `stream.checkpoint()`. Both are distinct from the
*public* `ResponseObject.metadata` (the client's own metadata — never
stripped).

## Stream Recovery (client-side reconciliation)

The library persists every SSE event in order — including events emitted
across multiple recovery attempts. Reconnecting clients use the standard
`starting_after=` query parameter to resume:

```
GET /responses/{id}?stream=true&starting_after=42
```

This returns only events with `sequence_number > 42`.

A resilient stream has **exactly one** `response.created` — it is the first
event of the stream. On a recovered entry the framework does **not** append a
second `response.created` (it is suppressed at the resilient-stream write because
the stream is non-empty), so the full replayed sequence a reconnecting client
sees end-to-end is:

```
response.created
response.in_progress
<events emitted before the crash>
response.in_progress        ← recovery reset: carries the stable
                              (already-persisted) output items at the
                              resumption point
<events emitted after recovery>
response.completed
```

The post-recovery part of this guarantee is normative per
[`responses-resilience-spec.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/responses-resilience-spec.md): for
`(store=true, background=true, resilient_background=True, stream=true)` —
the row that supports handler re-invoke — a client reconnecting AFTER a
crash receives the events the recovered handler emits, framed by the
reset-on-`in_progress` rule below. The conformance suite covers this
under Row 1 Path C.

### The reset-on-`in_progress` rule

Clients that want to support resilient+background recovery MUST observe the
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
- If the server crashes: response is marked `failed` with `code=server_error`.
- The handler is NOT re-invoked (client is already disconnected).
- Conversation lock still applies (prevents concurrent modifications).

## Layered Concerns

This guide and the handler guide together describe three layered concerns
that compose to give you resilient response handlers:

- **The resilient background runtime** provides the runtime primitives
  (flat recovery + steering fields on `ResponseContext` —
  `is_recovery`, `is_steered_turn`, `pending_input_count`,
  `conversation_chain_metadata` — task store wiring, steerable conversation
  orchestration).
- **The cancellation contract** provides two distinct surfaces — the
  3rd positional handler arg `cancellation_signal: asyncio.Event`
  (set on client cancel, `/cancel` API, or steering pressure) and
  `context.shutdown: asyncio.Event` (set on server shutdown), plus
  the cause flag `context.client_cancelled: bool` and the recovery
  primitive `await context.exit_for_recovery()`. Pre-entry /
  mid-stream / post-stream rules: no `cancelled` from steering or
  shutdown, no `incomplete` from framework, framework-set `failed`
  for naive-not-handled cancellation.
- **The recovery contract** provides the multi-attempt
  reconciliation pattern: resumption response, snapshot reset on
  `response.in_progress`, watermark-guarded side effects, naive
  fallback.

The three compose cleanly: the runtime surfaces the recovery hooks, the
cancellation contract is what recovered handlers must honour, and the
recovery contract prescribes how the recovered attempt produces coherent
output.

## Best Practices

These are recommendations, not framework requirements — adapt them to your
handler. (The genuine hard rules are few: a `ResponseEventStream` handler emits
`response.created` then `response.in_progress` first and exactly one terminal
event; a recovered streaming entry emits `response.in_progress` as the reset
point; and clients supporting resilient streams treat any later
`response.in_progress` as a snapshot reset.)

1. **Keep the recovery branch easy to find.** A recovery-aware handler usually
   diverges from a fresh handler near the top (`if context.is_recovery:`).
   Branching early keeps the two paths readable — a readability tip, not a rule.

2. **Prefer your upstream framework's own resume facility** when you have one.
   Copilot SDK has `create_session(session_id=...)` / `resume_session(...)`;
   LangGraph has `AsyncSqliteSaver` checkpoints. Reconstructing upstream state from
   your own metadata is usually more work and more fragile. **When the upstream
   is a durable engine with its own checkpointer, follow the
   [Composing an External Durable Engine](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#composing-an-external-durable-engine-eg-langgraph)
   pattern**: checkpoint 1:1 with the engine, store the engine's resume checkpoint
   id in `internal_metadata`, and rewind to *that* point on recovery — resuming
   from the engine's latest tip instead opens a reply-loss window.

3. **Watermark non-idempotent side effects — when the upstream can't dedup them.**
   If a recovered attempt could repeat an observable side effect (sending a user
   message, charging a card) and the upstream offers no idempotency key or
   "already done?" query, fence it: stamp + `flush()` `context.conversation_chain_metadata`
   BEFORE the call, clear + `flush()` AFTER it resiliently commits. If the upstream is
   already idempotent, or you use the framework-checkpoint model where the snapshot
   is your side-effect boundary, you may not need this.

4. **Keep metadata small.** Watermarks, session IDs, checkpoint references —
   never bulk data (it hits task-store payload limits and slows recovery).

5. **Honour the cancellation contract on recovery.** Recovery doesn't change the
   cancellation contract from the [Cancellation guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#cancellation):
   the same pre-entry / mid-stream / shutdown rules apply on recovered entries.

6. **Don't store secrets in metadata.** The task store persists it.

## Examples

See the `samples/` directory for canonical resilient handler shapes:

- `sample_19_resilient_streaming.py` — Canonical **framework-checkpoint**
  handler (`stream.checkpoint()` + `context.persisted_response`, no upstream
  framework).
- `sample_20_resilient_steering.py` — Steering surface (`is_steered_turn` /
  `pending_input_count`) with **naive re-run** recovery; cancellation ×
  recovery composition.
- `sample_21_resilient_langgraph.py` — **Real-time streaming** LangGraph agent
  (tokens relayed as deltas the instant nodes produce them) that **composes an
  external durable engine**: LangGraph's `AsyncSqliteSaver` (graph-execution
  resume) with framework `stream.checkpoint()` / `context.persisted_response`
  (client-visible items + ids). Checkpoints 1:1 with the graph and records the
  graph checkpoint id in `internal_metadata`, so recovery rewinds the graph to
  the point matching the persisted items — no dual-store divergence window. See
  [Composing an External Durable Engine](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/docs/handler-implementation-guide.md#composing-an-external-durable-engine-eg-langgraph).
- `sample_22_resilient_multiturn.py` — Multi-turn conversation with
  `resilient_background=True, steerable_conversations=False`.
