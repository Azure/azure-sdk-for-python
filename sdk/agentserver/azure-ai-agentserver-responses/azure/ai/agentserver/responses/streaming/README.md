# `azure.ai.agentserver.responses.streaming`

This sub-package wires the Responses host's SSE event pipeline to the
process-wide streams registry that ships with `azure-ai-agentserver-core`.
End users do not interact with the modules here directly — the helpers
are consumed by the responses orchestrator on every create-response
request — but operators and developers extending the host benefit from
knowing how the wiring works.

## Startup configuration

`ResponsesAgentServerHost.__init__` configures the process-wide
`streams` registry exactly once at compose time:

```python
from azure.ai.agentserver.core.streaming import streams

# Inside the host:
streams.use_file_backed_replay(           # if durable_background=True
    storage_dir=stream_dir,
    cursor_fn=lambda event: int(event["sequence_number"]),
    ttl_seconds=options.replay_event_ttl_seconds,
    serializer=_serialize_event_payload,  # ResponseStreamEvent.as_dict()
    deserializer=_deserialize_event_payload,
)
# OR
streams.use_in_memory_replay(             # if durable_background=False
    cursor_fn=lambda event: int(event["sequence_number"]),
    ttl_seconds=options.replay_event_ttl_seconds,
)
```

Why these choices:

| Setting | Value | Why |
|---|---|---|
| `cursor_fn` | `lambda e: e["sequence_number"]` | Every SSE event already carries a monotonically-increasing `sequence_number`. Reusing it as the registry cursor means clients reconnecting with `Last-Event-ID: N` (or the `?starting_after=N` query alias) can resume exactly where they left off without any extra bookkeeping. |
| `ttl_seconds` | `options.replay_event_ttl_seconds` (default `600`) | Caps both memory and on-disk footprint. Each emit becomes evictable 10 minutes after its emit time, regardless of whether the stream is still active; the SDK's auto-transition rules then destroy the stream once it has closed AND its last retained event has expired. |
| `serializer` / `deserializer` (file-backed only) | JSON via `as_dict()` | `ResponseStreamEvent` is a generated model — not directly JSON-serializable. The serializer converts via `.as_dict()`, so the on-disk records are plain JSON dicts that any reader (including a future shell script or recovery scanner) can parse. |

## Persistence file layout

When the host is configured with `durable_background=True`, the
file-backed backing writes one JSONL file per response under the
configured `storage_dir`:

```text
<storage_dir>/<response_id>.jsonl
```

Each line is a single JSON object of the form
`{"emit_time": <unix-float>, "payload": <event-dict>}`, ending with
a terminator record `{"emit_time": <float>, "__terminal__": true}` once
the stream is closed. The directory is created on first use.

Operators select the directory via `AGENTSERVER_STREAM_STORE_PATH`; the
host falls back to a per-process temp directory when unset.

## Recovery on restart

A fresh process that calls `await streams.get_or_create(response_id)`
for a `response_id` whose `.jsonl` file already exists on disk
rehydrates the stream from the persisted events automatically:

- Buffered events become available to new subscribers immediately.
- `await stream.last_cursor()` returns the highest `sequence_number`
  that made it to disk before the crash.
- The recovered handler reads that cursor to learn what sequence
  number to assign to its next emit, keeping the assembled stream
  monotonically increasing across the crash boundary.

If the previous run finished cleanly (terminator on disk) AND every
persisted event has since expired, the rehydrated stream is in the
`GONE` state. Calling `streams.delete(id)` + `streams.get_or_create(id)`
mints a fresh stream.

## HTTP / SSE wire mapping

The responses host exposes events through Server-Sent-Events on:

- `POST /responses` with `stream=true` — the **live wire**. The endpoint
  layer subscribes to the per-response stream and yields each emit as
  an SSE event.
- `GET /responses/{id}?stream=true` — **replay**. The endpoint looks up
  the per-response stream from the registry and iterates its buffered
  history.
  - Cursored reconnect: the SSE `Last-Event-ID: N` header (or the
    `?starting_after=N` query alias retained for backward compatibility)
    is forwarded as `stream.subscribe(after=N)`.
  - When no stream exists for `id` (never registered, or destroyed via
    `DELETE /responses/{id}`), the endpoint returns HTTP `404`. The
    underlying registry exceptions
    (`EventStreamNotFoundError` / `EventStreamGoneError`) both map to
    `404` on this endpoint.

## Other modules in this sub-package

| Module | Purpose |
|---|---|
| `_event_stream.py` | `ResponseEventStream` builder API for handler authors — typed event factory methods. |
| `_sse.py` | SSE wire-format encoders. |
| `_state_machine.py` | `EventStreamValidator` for first-event / lifecycle contract enforcement. |
| `_helpers.py` | `_coerce_handler_event`, `_apply_stream_event_defaults`, `_build_events` — coerce handler outputs into normalised events. |
| `_internals.py` | Low-level event construction. |
| `_text_response.py` | `TextResponse` helper. |
| `_builders/` | Per-output-item builders (message, function call, etc.). |
