# Streaming guide — `azure.ai.agentserver.core.streaming`

This package gives you one way to **emit events from one coroutine
and receive them from one or more other coroutines** — typically:
your `@task` handler produces events, and your HTTP layer fans them
out to a Server-Sent-Events / WebSocket / long-poll endpoint.

You pick a backing once at app startup, then everywhere else you
look streams up by id and call `emit` / `subscribe`.

---

## 5-minute getting started

```python
from azure.ai.agentserver.core.streaming import streams

# 1. At app startup — pick a backing.
streams.use_in_memory_replay(cursor_fn=lambda ev: ev["n"], ttl_seconds=600)

# 2. The producer (e.g. your @task handler):
async def produce(stream_id: str) -> None:
    stream = await streams.get_or_create(stream_id)
    try:
        for n in range(5):
            await stream.emit({"n": n, "msg": f"hello {n}"})
    finally:
        await stream.close()

# 3. The subscriber (e.g. your HTTP handler) — attach BEFORE the
# producer starts (see §Subscribing for why):
async def consume(stream_id: str) -> None:
    stream = await streams.get_or_create(stream_id)
    async for event in stream.subscribe():
        print(event)
    # Loop terminates cleanly when the producer calls close().
```

`streams.get_or_create(id)` is idempotent: the producer and the
subscriber both call it with the same id and get the **same**
`EventStream` instance back.

---

## Public surface

Six exports, total:

```python
from azure.ai.agentserver.core.streaming import (
    streams,                    # the process-level registry singleton
    EventStream,                # @runtime_checkable Protocol
    EventStreamError,           # base exception (catch-all)
    EventStreamClosedError,     # emit on a closed stream
    EventStreamGoneError,       # any op on a destroyed stream
    EventStreamNotFoundError,   # streams.get(id) for an unknown id
)
```

That's it. The concrete classes behind the three configurators are
not part of the public API — you obtain instances via the registry
and program against the `EventStream` Protocol.

---

## Choosing a backing

| Backing | Use when | Reconnect / replay? | Survives process restart? | Notes |
|---|---|---|---|---|
| `use_in_memory_live()` (default) | Single subscriber that attaches before the producer; lowest memory; you don't need late subscribers to catch up. | No — late subscribers miss earlier events. | No. | Constant memory: only the subscriber list, no event buffer. |
| `use_in_memory_replay(...)` | Multiple subscribers that may attach at different times; client may reconnect within `ttl_seconds`. | Yes (within the per-event TTL window). | No. | Each event is retained until its TTL elapses (or `delete` runs). |
| `use_file_backed_replay(...)` | Long-running turns where you need to survive a process crash and a fresh worker resuming the same turn. | Yes. | Yes — events are persisted to `storage_dir / f"{id}.jsonl"` and rehydrated on the next `get_or_create(id)`. | Single-writer-per-file enforced. |

**Call a configurator before you create any streams** (typically
once at app startup). Later calls only affect streams created
after the call — streams already in the registry keep their original
backing. Switching mid-process is supported but discouraged.

### Configurator signatures

```python
streams.use_in_memory_live() -> None

streams.use_in_memory_replay(
    *,
    cursor_fn:    Callable[[Any], int] | None = None,
    ttl_seconds:  float | None             = None,
) -> None

streams.use_file_backed_replay(
    *,
    storage_dir:  Path,
    cursor_fn:    Callable[[Any], int] | None       = None,
    ttl_seconds:  float | None                      = None,
    serializer:   Callable[[Any], bytes] | None     = None,
    deserializer: Callable[[bytes], Any] | None     = None,
) -> None
```

- **`cursor_fn`** — pass this if you want cursored re-subscription
  (`subscribe(after=N)`) and a usable `last_cursor()`. It receives
  each payload and returns an `int` you choose as its cursor (a
  monotonically increasing sequence number is typical). Without it,
  `subscribe(after=...)` is silently ignored and `last_cursor()`
  always returns `None`.
- **`ttl_seconds`** — per-event retention. Each emitted event becomes
  evictable `ttl_seconds` after its emit time, regardless of whether
  the stream is still active. Use this to bound memory / disk usage.
  Once the stream is closed AND its last retained event has expired
  AND at least one event was ever emitted, the stream itself
  transitions to "destroyed" (see §Lifecycle). A stream that was
  created and closed without ever emitting stays in CLOSED forever
  (or until `streams.delete(id)`).
- **`storage_dir`** (file-backed only) — directory that holds one
  `<id>.jsonl` file per stream. Created if it doesn't exist.
- **`serializer` / `deserializer`** (file-backed only) — bring your
  own codec for non-JSON-serializable payloads. Defaults assume the
  payload is JSON-serializable.

---

## The stream id

A stream id is the identity of a single producer/consumer
conversation. Pick the per-turn identifier from your framework:

| Context | Use as id |
|---|---|
| Inside `azure-ai-agentserver-invocations` | `request.state.invocation_id` (HTTP layer); `ctx.input["invocation_id"]` (handler) |
| Inside `azure-ai-agentserver-responses` | `response_id` |
| Bare-Python / custom | Any per-turn `str` you control end-to-end |

**Do NOT use a durable `task_id` as the stream id.** A durable task
can span multiple turns (steering, recovery). Reusing the id across
turns means the second turn finds the previous turn's already-closed
stream and `emit` raises `EventStreamClosedError`. Always scope the
id to one logical request/turn/invocation.

**File-backed backing only:** because the file-backed backing maps
the id directly to `<storage_dir>/<id>.jsonl`, the id must be safe
for use as a single filename — no path separators, no characters
your filesystem rejects, ideally short. The framework-provided
`invocation_id` / `response_id` values already satisfy this; if you
mint your own id, sanitize it.

---

## The `EventStream` Protocol

Every stream — regardless of backing — exposes the same four
methods:

```python
class EventStream(Protocol):
    async def emit(self, payload: Any, *, close: bool = False) -> None: ...
    async def close(self) -> None: ...
    def     subscribe(self, *, after: int | None = None) -> AsyncIterator[Any]: ...
    async def last_cursor(self) -> int | None: ...
```

### `emit(payload, *, close=False)`

Publishes one event to every currently-attached subscriber.

- `payload` is opaque — the SDK never inspects, validates, or
  rewrites it. For file-backed replay it must be serializable by
  your chosen serializer (default: JSON).
- `close=True` is an **atomic emit-and-close**: the payload is
  delivered + the stream is closed in one step, with no opportunity
  to emit again in between. For replay backings, the payload is
  still retained in history and a late subscriber can see it; for
  the live backing, late subscribers see neither the payload nor any
  earlier events.
- Raises `EventStreamClosedError` if you call `emit` after `close`.
  This means a producer bug (you should not be emitting any more);
  HTTP layers should treat this as `5xx`, not a client error.
- Raises `EventStreamGoneError` if the stream has been destroyed.

### `close()`

Marks the stream done. Idempotent — calling it twice (or on a
destroyed stream) is a no-op, never raises. After `close()`:

- New `emit` calls raise `EventStreamClosedError`.
- Existing subscriber iterators drain any in-flight events, then
  exit cleanly with `StopAsyncIteration`.
- New `subscribe` calls still work as long as the stream hasn't yet
  been destroyed (for replay backings, they will see the retained
  history).

### `subscribe(*, after=None)`

Returns an **async iterator** over emitted payloads. **Not** a
coroutine — call it WITHOUT `await`, use directly in `async for`:

```python
async for event in stream.subscribe():
    handle(event)
```

The iterator terminates cleanly with `StopAsyncIteration` when the
stream is closed (after draining any in-flight events) **or** when
the stream is destroyed while you are iterating (whether by
`streams.delete(id)` or by the auto-transition described in
§Lifecycle). `subscribe()` itself raises `EventStreamGoneError`
synchronously only if the stream is already destroyed at the time
you call it.

`after=N` is the **reconnection primitive** — only yield events
whose cursor is strictly greater than `N`. Requires the active
backing to have a `cursor_fn`; silently ignored otherwise. See
§Recovery & resumption.

Multiple subscribers are supported; each gets its own independent
queue.

### `last_cursor()`

Returns the highest cursor value seen so far, or `None` if no
events were emitted, or `None` if the active backing has no
`cursor_fn`. After the stream is closed, this is the last cursor
the backing saw — even if that event has since expired from
replay. Raises `EventStreamGoneError` if the stream is destroyed.

`last_cursor()` is the producer's recovery primitive: a recovering
handler reads it to learn "what cursor should I assign to my next
emit?".

---

## Lifecycle: ACTIVE → CLOSED → GONE

Each stream is in one of three states:

| State | What it means | How you reach it |
|---|---|---|
| **ACTIVE** | Open to `emit`. Subscribable. | Construction (first `get_or_create(id)`). |
| **CLOSED** | No new emits. Existing subscribers drain. New subscribers can still attach (replay backings) but no new events arrive. | `close()` from ACTIVE. |
| **GONE** (destroyed) | `emit`, `subscribe`, and `last_cursor` all raise `EventStreamGoneError`. `close()` remains idempotent (no-op). The id is preserved in the registry so `streams.get(id)` raises `Gone`, not `NotFound`. | `streams.delete(id)`, OR (replay backings with `ttl_seconds`) automatic eviction: when the stream is CLOSED, its last retained event has expired, and at least one event was ever emitted. |

A few practical implications:

- The live backing (`use_in_memory_live`) never auto-transitions to
  GONE — it has nothing to evict. Call `streams.delete(id)`
  explicitly if you need to release the id.
- The auto-transition for replay backings fires on the **next**
  `subscribe()` or `emit()` after the eviction window has passed.
  `last_cursor()` does not itself fire the transition — it remains
  readable across the eviction window so a recovering handler can
  still learn "what was my last cursor?".

---

## The registry

```python
streams.get(id)            -> EventStream      # raises NotFound, never returns a destroyed instance
streams.get_or_create(id)  -> EventStream      # idempotent, atomic
streams.delete(id)         -> None             # idempotent
```

- `get(id)` returns the registered stream, or raises:
  - `EventStreamNotFoundError` — the id was never registered AND
    `delete(id)` was never called for it.
  - `EventStreamGoneError` — `delete(id)` has been called for this
    id (whether or not it was ever registered). The registry
    remembers deleted ids specifically so this distinction holds.
  - **Note** — `get(id)` does NOT raise `Gone` for a stream that
    auto-evicted itself (replay backing reached the CLOSED + last
    event expired condition). It returns the instance; the caller
    sees `Gone` only when they next call `emit` / `subscribe` /
    `last_cursor` on it. If you need an HTTP 410 response for an
    auto-evicted stream, attempt one operation (e.g.
    `await stream.last_cursor()`) and map the exception.
- `get_or_create(id)` is the **only** way to mint a stream. It is
  atomic across concurrent callers — two coroutines racing on the
  same id both get the same instance back. It clears any prior
  `delete`-installed marker and creates a fresh stream. It does NOT
  replace a stream that auto-evicted in place: that instance is
  still in the slot and is returned as-is. To recover an id whose
  stream auto-evicted, call `delete(id)` explicitly first (see
  §Recovery & resumption for the file-backed pattern).
- `delete(id)` destroys the stream, cleans up its backing resources
  (e.g. closes file handles for file-backed replay and removes the
  on-disk log), and records the id so future `get(id)` calls see
  `Gone`. Idempotent — calling it on an unknown id or an
  already-deleted id is a no-op (but still ensures the id is
  recorded as deleted).

You typically do not need to call `delete(id)` — the auto-transition
in the replay backings cleans up for you once the TTL has elapsed.
Call `delete(id)` explicitly when you want immediate cleanup
(end-of-request hook, test teardown).

---

## Exceptions → wire mapping

```text
EventStreamError                  (base — catch-all)
├── EventStreamClosedError        producer bug — wire-map to HTTP 5xx
├── EventStreamGoneError          stream existed, now destroyed — HTTP 410
└── EventStreamNotFoundError      stream never existed — HTTP 404
```

The 404 vs 410 distinction matters for clients: 410 tells a client
"this id was valid but is past its lifetime — don't retry"; 404
tells a client "this id was never valid — check your routing". The
registry preserves the distinction across the destroy boundary by
remembering ids that have been deleted or auto-evicted.

---

## Subscribing — the subscribe-before-start rule

For the **default live backing** (`use_in_memory_live`), subscribers
only see events emitted after they attach. With the live backing
"attach" means **`async for` over the iterator has begun (i.e.
`__aiter__` has run)** — not merely that you've called
`get_or_create` or `subscribe`. So just calling
`asyncio.create_task(_serve_sse(stream))` does not guarantee the SSE
task has actually begun iterating before your producer starts
emitting — there is a race.

Safe options:

1. **Use a replay backing** (`use_in_memory_replay` or
   `use_file_backed_replay`). Late subscribers catch up via the
   retained history, so the race doesn't matter. This is the
   recommended default for HTTP layers.
2. **Drive iteration before starting the producer.** Spawn the SSE
   task, then `await asyncio.sleep(0)` (or any explicit signal from
   the SSE task that it has started its `async for`) before calling
   `task.start(...)`. This is harder to get right than option 1; we
   recommend option 1 unless you have a strong reason to avoid
   buffering.

Once you've picked your strategy, the canonical pattern is:

1. HTTP layer reads the per-turn id from the request.
2. HTTP layer calls `await streams.get_or_create(id)` and arranges
   for a subscriber to be attached (per the strategy above).
3. HTTP layer starts the producer (e.g. `await task.start(...)`)
   with the id propagated via input.
4. Producer also calls `await streams.get_or_create(id)` and gets
   the same instance.

```python
# At startup (option 1 — recommended):
streams.use_in_memory_replay(cursor_fn=lambda ev: ev["n"], ttl_seconds=600)

# HTTP layer
async def handle_request(request):
    inv_id = request.state.invocation_id

    stream = await streams.get_or_create(inv_id)          # 1 + 2
    sse = asyncio.create_task(_serve_sse(stream))         # safe: replay backing

    await my_task.start(
        task_id=...,
        input={"invocation_id": inv_id, ...},             # 3
    )
    return StreamingResponse(...)

# Handler
@task
async def my_task(ctx):
    inv_id = ctx.input["invocation_id"]
    stream = await streams.get_or_create(inv_id)          # 4 — same instance
    await stream.emit({"event": "hello"})
```

---

## Recovery & resumption

### Cursored reconnect (client side)

If your subscriber drops (network blip, client refresh) and your
backing has a `cursor_fn`, the client reconnects with the last
cursor it saw and the SDK only re-delivers later events:

```python
# Client reconnects with Last-Event-ID: 42
stream = await streams.get_or_create(stream_id)
async for event in stream.subscribe(after=42):
    push_to_client(event)
```

Events with cursor ≤ 42 are skipped from the retained history;
delivery resumes at 43.

### Crash-recoverable producer (file-backed)

With `use_file_backed_replay`, a fresh process resuming the same
turn rehydrates the stream automatically:

```python
from azure.ai.agentserver.core.streaming import (
    streams, EventStreamGoneError,
)

streams.use_file_backed_replay(
    storage_dir=Path("/var/lib/myapp/streams"),
    cursor_fn=lambda ev: ev["n"],
    ttl_seconds=3600,
)

@task
async def producer(ctx):
    inv_id = ctx.input["invocation_id"]
    stream = await streams.get_or_create(inv_id)
    try:
        # On crash recovery this is the highest n that made it to disk.
        last = await stream.last_cursor()
    except EventStreamGoneError:
        # The previous run closed the stream AND every persisted event
        # has since expired. The on-disk log is stale; drop it and start
        # fresh. delete() removes the file and records the deletion;
        # the next get_or_create() then mints a brand-new stream.
        await streams.delete(inv_id)
        stream = await streams.get_or_create(inv_id)
        last = None

    next_n = (last + 1) if last is not None else 0
    for n in range(next_n, total):
        await stream.emit({"n": n, "msg": ...})
    await stream.close()
```

The typical recovery scenario — process crashed mid-stream, no
terminal marker on disk — is handled by the first branch:
rehydration loads the persisted events, `last_cursor()` returns the
highest cursor, and the handler resumes emitting from the next
cursor.

The `EventStreamGoneError` branch handles the edge case where the
previous run completed cleanly (wrote a close marker to disk) AND
every persisted event has since expired AND your application policy
is "start over with a fresh stream". Without the explicit
`delete(id)`, the registry would keep handing back the same dead
instance.

### Don't double-track in `@task` metadata

Anti-pattern:

```python
# Don't do this.
await stream.emit({"n": n, ...})
ctx.metadata.set("last_event_n", n)
await ctx.metadata.flush()
```

The stream already persisted the event; `last_cursor()` will return
`n` for you. `ctx.metadata` is for **workflow** watermarks — which
units of side-effecting work (LLM calls, tool invocations) you've
already completed — not for mirroring stream state.

---

## HTTP / SSE bridging pattern

Typical helper for serving a stream over Server-Sent-Events:

```python
import json

from azure.ai.agentserver.core.streaming import EventStreamGoneError

async def _serve_sse(stream):
    """Bridge an EventStream to an SSE wire format."""
    last_seen: int | None = None
    try:
        async for event in stream.subscribe():
            cursor = event.get("n")
            yield f"id: {cursor}\ndata: {json.dumps(event)}\n\n".encode()
            last_seen = cursor
    except EventStreamGoneError:
        # Server-side cleanup ran while we were attached; tell the
        # client we're done.
        yield b"event: gone\ndata: {}\n\n"
```

If your client sends `Last-Event-ID`, pass it through to
`stream.subscribe(after=int(last_event_id))` to skip already-delivered
events.

---

## Bringing your own `EventStream` implementation

You can write your own `EventStream` Protocol impl (e.g. a Redis-
backed stream). It will be accepted anywhere the Protocol is — the
`@runtime_checkable` decorator on the Protocol means
`isinstance(s, EventStream)` works.

**But** you must NOT plug it into the SDK `streams` registry —
`streams` is the lifecycle owner for SDK-bundled backings only, and
its cleanup assumes those backings' semantics. Ship your own peer
registry instead:

```python
class _MyRedisStreams:
    """Peer namespace to the SDK ``streams`` registry."""
    def __init__(self, *, redis_url, **opts): ...
    async def get(self, id: str) -> EventStream: ...
    async def get_or_create(self, id: str) -> EventStream: ...
    async def delete(self, id: str) -> None: ...

my_redis_streams = _MyRedisStreams(redis_url="...")
```

Consumers explicitly choose which registry they want:
`await my_redis_streams.get_or_create(id)` vs
`await streams.get_or_create(id)`. The shared interface is the
`EventStream` Protocol; lifecycle is each registry's own concern.

---

## Migrating from the legacy `StreamHandler` surface

If you have existing code that uses the now-removed `StreamHandler`
/ `QueueStreamHandler` / `ctx.stream(item)` / `async for chunk in
run` API, here is the crosswalk:

```python
# OLD — removed.
@task(stream_handler_factory=lambda task_id: QueueStreamHandler())
async def my_handler(ctx):
    await ctx.stream({"n": 1})
# Consumer:
async for chunk in run:
    print(chunk)
```

```python
# NEW.
# At app startup:
streams.use_in_memory_replay(ttl_seconds=600)

# HTTP layer (subscribe-before-start):
inv_id = request.state.invocation_id
stream = await streams.get_or_create(inv_id)
sse = asyncio.create_task(_serve_sse(stream))
await my_task.start(task_id=..., input={"invocation_id": inv_id, ...})

# Handler:
@task
async def my_handler(ctx):
    inv_id = ctx.input["invocation_id"]
    stream = await streams.get_or_create(inv_id)
    await stream.emit({"n": 1})

# Consumer:
async for chunk in stream.subscribe():
    print(chunk)
```

Migration checklist:

1. Pick a backing in your app startup (one of the three `use_*`).
2. Pass the per-turn id (e.g. `invocation_id`) through to the handler
   via `task.start(input=...)`.
3. Replace `ctx.stream(item)` with
   `await stream.emit(item)` where `stream = await
   streams.get_or_create(ctx.input["invocation_id"])`.
4. Replace `async for chunk in run` (where `run` is a `TaskRun`)
   with `async for chunk in stream.subscribe()` — in the HTTP layer,
   attach the subscriber BEFORE calling `task.start(...)`.
5. Remove any `stream_handler_factory=` kwarg from `@task(...)`.

---

## See also

- [`durable-task-guide.md`](./durable-task-guide.md) — `@task` developer
  guide; Pattern E shows the streaming integration end-to-end.
- `samples/durable_streaming/durable_streaming.py` (in this package)
  — minimal standalone sample.
- `azure-ai-agentserver-invocations/samples/durable_research/`,
  `durable_langgraph/`, `durable_copilot/` — HTTP-server samples
  exercising the registry + per-turn `invocation_id` +
  subscribe-before-start pattern end-to-end.
