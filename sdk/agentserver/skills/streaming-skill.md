---
name: agentserver-streaming
description: 'Emit events from one coroutine and fan them out to one or more subscribers (typically: your `@task` handler produces, your HTTP layer fans out as SSE / WebSocket / long-poll) using the `streams` registry from `azure-ai-agentserver-core`. WHEN: "stream tokens / progress events from my agent", "SSE endpoint", "fan an agent stream out to N subscribers", "let a late subscriber catch up via replay", "reconnect from `Last-Event-ID` cursor", "stream survives container crash + recovery", "bridge a single-consumer LLM SDK stream to N HTTP subscribers", "subscribe before invoke pattern", "resilient streaming + checkpointed sequence numbers". DO NOT USE FOR: persisting business state (use `ctx.metadata` for tiny watermarks, your own store for content), cross-process pub/sub (one registry per process — use a real message bus), competing-consumer fan-out (every subscriber sees every event — not work-stealing), arbitrary back-pressure between producer and consumer (subscribers buffer per-subscriber; slow consumers grow their queue, not back-pressure the producer). PRIVATE PREVIEW: the `streaming` subpackage ships only via pre-release wheels checked into this branch (see references); the surrounding `azure-ai-agentserver-*` packages are on PyPI at stable versions.'
---

# Agentserver Streaming (`streams`) — Standalone Skill

> **Standalone document.** Copy this file into your project to give your
> AI coding agent (GitHub Copilot, etc.) the context it needs to use the
> `streams` registry correctly. Pair it with the checked-in pre-release
> wheels (see *Packaging* below) — that's all your project needs to start
> building streaming endpoints on top of `@task`.

The `streams` registry in `azure-ai-agentserver-core.streaming` is a
process-level rendezvous between one **producer** coroutine (your
agent handler) and one or more **subscriber** coroutines (typically your
HTTP layer rendering SSE). You pick a *backing* once at app startup —
live, in-memory replay, or file-backed replay — and from then on the
producer and every subscriber just look the stream up by id.

## When to use

Use `streams` when **any** of these apply:

- Your agent handler produces a stream of events (token deltas, phase
  progress markers, intermediate tool calls) and one or more clients
  want to see them as they happen.
- The HTTP layer needs to fan a single producer out to **N
  subscribers** (e.g., the originating client plus a tail / debug
  client) without the producer knowing about subscribers.
- Subscribers may **attach after the producer started** and need to
  catch up via replay (use one of the replay backings).
- Subscribers may **disconnect and reconnect** with a cursor
  (`Last-Event-ID` for SSE) and resume without losing events.
- The handler runs under `@task`, can **crash mid-stream**, and you
  want a fresh subscriber after the recovery boundary to see the full
  pre-crash + post-crash history (use the file-backed replay backing
  plus the [Resilient streaming primer](#resilient-streaming-primer-task--streams)
  below).

## When NOT to use

`streams` is intentionally narrow. Do **not** use it for:

- **Cross-process or cross-machine pub/sub.** The registry lives in
  one Python process. Multi-worker deployments need a real message
  bus (Redis, NATS, Kafka). Each worker's registry is independent.
- **Work-stealing / competing-consumer queues.** Every subscriber
  receives every event. There is no acknowledge / nack protocol.
  If you want N workers to share work, use a queue.
- **Producer-side back-pressure.** Each subscriber has its own
  per-subscriber buffer. A slow subscriber grows its own queue; the
  producer never blocks on `emit()`. If a subscriber falls badly
  behind it's the subscriber's problem — design for short-lived
  HTTP streams.
- **Business-state persistence.** The replay backings hold events for
  *reconnect catch-up*, not as your system of record. Persist
  business state through your agent framework's store and through
  `@task` metadata watermarks.
- **Stream resilience across the registry's TTL / process boundary.**
  `use_in_memory_replay(ttl_seconds=...)` evicts on TTL.
  `use_file_backed_replay(...)` survives a process restart only for
  the same stream id within the same on-disk directory.

## Minimal pattern

```python
from azure.ai.agentserver.core.streaming import streams

# 1. At app startup — pick a backing ONCE.
streams.use_in_memory_replay(cursor_fn=lambda ev: ev["n"], ttl_seconds=600)

# 2. The producer — typically your @task handler:
async def produce(stream_id: str) -> None:
    stream = await streams.get_or_create(stream_id)
    try:
        for n in range(5):
            await stream.emit({"n": n, "msg": f"hello {n}"})
    finally:
        await stream.close()

# 3. The subscriber — typically your HTTP handler.
# Attach BEFORE the producer starts whenever you can.
async def consume(stream_id: str) -> None:
    stream = await streams.get_or_create(stream_id)
    async for event in stream.subscribe():
        print(event)
    # Loop terminates cleanly when the producer calls close().
```

`streams.get_or_create(id)` is idempotent: the producer and the
subscriber both call it with the same id and get the **same**
`EventStream` instance back.

## Pick the right backing

| Backing | Use when | Reconnect / replay? | Survives process restart? |
|---|---|---|---|
| `use_in_memory_live()` *(default)* | Single subscriber attaches before the producer; lowest memory. | No — late subscribers miss earlier events. | No. |
| `use_in_memory_replay(cursor_fn=..., ttl_seconds=...)` | Late subscribers / disconnect+reconnect within the same process; cursor-based catch-up. | Yes, up to TTL. | No. |
| `use_file_backed_replay(storage_dir=..., cursor_fn=...)` | `@task` handler that can crash and recover; subscribers need monotonic event continuity across the crash boundary. | Yes, across process restarts for the same stream id + on-disk dir. | Yes. |

Call exactly **one** configurator at app startup. Don't switch
backings mid-process.

## Pick the right stream id

The stream id is the **per-turn natural identifier** — never the
resilient task id, because a `task_id` outlives a single turn:

| Framework | Stream id | Source |
|---|---|---|
| `azure-ai-agentserver-invocations` (hosted agents) | `invocation_id` | HTTP layer's `request.state.invocation_id`; propagated to the `@task` handler via `ctx.input["invocation_id"]`. |
| `azure-ai-agentserver-responses` (OpenAI-shaped) | `response_id` | The orchestrator knows it at every call site. |
| Bare Python (no framework) | caller's choice (`str`) | Pick a natural per-turn id from your domain. |

## Subscribe BEFORE you start the producer

```python
# 1. Resolve / create the stream first.
stream = await streams.get_or_create(invocation_id)
# 2. Start subscribing.
async def pump():
    async for ev in stream.subscribe():
        yield render_sse(ev)
# 3. NOW kick off the producer (e.g., the @task run).
asyncio.create_task(run_task(invocation_id))
```

This guarantees the subscriber's queue exists by the time the very
first `emit()` lands, so the live backing doesn't drop the early
events. The replay backings can also catch you up after the fact via
the cursor, but subscribe-before-start is the cheaper, simpler
pattern when the HTTP layer owns both sides.

## HTTP / SSE bridging shape

```python
from azure.ai.agentserver.core.streaming import (
    streams,
    EventStreamNotFoundError,
)

async def sse_endpoint(request):
    invocation_id = request.path_params["id"]
    # streams.get(id) raises NotFound for any id that isn't currently
    # a live stream (never registered, deleted, or close-clock elapsed).
    # streams.get_or_create cannot raise NotFound — it clears any
    # tombstone and synthesises a fresh stream.
    try:
        stream = await streams.get(invocation_id)
    except EventStreamNotFoundError:
        return Response(404, "stream not found")

    last_event_id = request.headers.get("last-event-id")
    after = int(last_event_id) if last_event_id else None

    async def body():
        try:
            async for ev in stream.subscribe(after=after):
                yield f"id: {ev['n']}\ndata: {json.dumps(ev)}\n\n"
        except EventStreamNotFoundError:
            return  # stream was tombstoned mid-iteration; cleanly close
    return StreamingResponse(body(), media_type="text/event-stream")
```

The streaming contract collapsed the prior `EventStreamGoneError`
(`410 Gone`) and `EventStreamNotFoundError` (`404 Not Found`) into
a single error type wire-mapped to `404`. Every "this id is not
currently a live stream" condition raises `EventStreamNotFoundError`.

The replay backings honor `after=<cursor>` for catch-up. The cursor
itself comes from `cursor_fn(event)` you pass to the configurator —
typically a monotonically increasing `sequence_number` you put on
every event in your producer.

## Resilient streaming primer (`@task` + `streams`)

The streaming registry is the natural pair for `@task`. The recipe:

1. At app startup, call `streams.use_file_backed_replay(storage_dir=...,
   cursor_fn=lambda ev: ev["sequence_number"])`.
2. Producer (inside your `@task` handler) stamps every event with a
   monotonically increasing `sequence_number`. After a crash, the
   recovery boundary reads `stream.last_cursor()` to know where to
   resume from.
3. Subscribers reconnect with `Last-Event-ID: <sequence_number>` and
   the file-backed replay backing replays the gap, then live-tails
   from there.

The `samples/resilient-agent-demo/` end-to-end run demonstrates the full
flow: subscriber connects mid-run, witnesses pre-crash events, sees
the recovery boundary (`type=recovered`), then continues monotonically
through the post-crash events with no gaps.

## Bring your own `EventStream` implementation

The bundled registry is the SDK-provided one. If you need different
semantics (Redis-backed, pubsub-replicated, etc.) you implement the
`EventStream` Protocol on your own class and ship your own peer
registry — the SDK explicitly does not let third-party concrete
classes plug into the bundled registry. The Protocol is small:
`emit`, `close`, `subscribe`, `last_cursor`, plus three exception types.

## Packaging — private preview wheels

The surrounding `azure-ai-agentserver-core` and
`azure-ai-agentserver-invocations` packages are published on PyPI at
stable versions. **The `streaming` subpackage is in private preview**
and ships *only* via the pre-release wheels checked into this branch.
There is no PyPI release for `azure.ai.agentserver.core.streaming`
until it goes GA — installing the regular PyPI version of
`azure-ai-agentserver-core` will not give you the `streams` registry.

Consume the checked-in wheels per:

- Wheel directory + README: [`sdk/agentserver/wheels/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/wheels)

## Authoritative references

| Topic | Link |
|---|---|
| **Full streaming developer guide** (configurators, EventStream Protocol, lifecycle, registry API, exception/wire mapping, recovery patterns, BYO impl) | [`docs/streaming-guide.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/streaming-guide.md) |
| **Resilient task developer guide** (the natural pair: `@task` produces, `streams` fans out) | [`docs/tasks-guide.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/tasks-guide.md) |
| Bare-Python streaming sample | [`samples/resilient_streaming/resilient_streaming.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/samples/resilient_streaming/resilient_streaming.py) |
| End-to-end **long-running + crash + steer + SSE** demo (Foundry hosted) | [`samples/resilient-agent-demo/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient-agent-demo) |
| Invocations streaming sample (research agent — SSE on POST + GET + `?last_event_id` reconnect) | [`samples/resilient_research/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient_research) |
| Invocations streaming sample (copilot agent — optional SSE on POST, polling fallback) | [`samples/resilient_copilot/`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/resilient_copilot) |

Read the streaming developer guide first — it covers the full
`EventStream` Protocol, the ACTIVE → CLOSED → GONE lifecycle, the
`last_cursor()` rule-25 exemption for file-backed recovery,
subscribe-before-start mechanics, the HTTP/SSE bridging shape, and
the BYO peer-registry pattern.

## Decision shortcuts

| Need | Use `streams`? | Why |
|---|---|---|
| SSE endpoint that tails a `@task` handler's output | ✅ | The natural producer/subscriber rendezvous |
| Late subscriber needs to catch up via cursor | ✅ | `use_in_memory_replay` or `use_file_backed_replay` |
| Subscriber reconnects after a container crash | ✅ | `use_file_backed_replay` + monotonic `sequence_number` |
| Fan one producer to N HTTP subscribers in the same process | ✅ | Every subscriber sees every event |
| Multi-worker / cross-process pubsub | ❌ | Each worker has its own registry — use a real bus |
| Work-stealing across N consumers | ❌ | Wrong primitive — use a queue |
| Persist business state across turns | ❌ | Use `ctx.metadata` (small) + your own store (big) |
| Producer needs back-pressure when subscriber is slow | ⚠️ | Per-subscriber queues grow; producer never blocks — design for short-lived HTTP streams |
