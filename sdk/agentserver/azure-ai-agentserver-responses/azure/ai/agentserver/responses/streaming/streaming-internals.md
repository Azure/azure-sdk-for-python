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
streams.use_file_backed_replay(           # if resilient_background=True
    storage_dir=stream_dir,
    cursor_fn=lambda event: int(event["sequence_number"]),
    ttl_seconds=_REPLAY_EVENT_TTL_SECONDS,  # hardcoded 600.0
    serializer=_serialize_event_payload,  # ResponseStreamEvent.as_dict()
    deserializer=_deserialize_event_payload,
)
# OR
streams.use_in_memory_replay(             # if resilient_background=False
    cursor_fn=lambda event: int(event["sequence_number"]),
    ttl_seconds=_REPLAY_EVENT_TTL_SECONDS,  # hardcoded 600.0
)
```

Why these choices:

| Setting | Value | Why |
|---|---|---|
| `cursor_fn` | `lambda e: e["sequence_number"]` | Every SSE event already carries a monotonically-increasing `sequence_number`. Reusing it as the registry cursor means clients reconnecting with `Last-Event-ID: N` (or the `?starting_after=N` query alias) can resume exactly where they left off without any extra bookkeeping. |
| `ttl_seconds` | `_REPLAY_EVENT_TTL_SECONDS = 600.0` (hardcoded framework constant) | Caps both memory and on-disk footprint. Each emit becomes evictable 10 minutes after its emit time, regardless of whether the stream is still active; the SDK's auto-transition rules then destroy the stream once it has closed AND its last retained event has expired. 600s gives clients a 10-minute reconnection window before persisted events are eligible for cleanup. |
| `serializer` / `deserializer` (file-backed only) | JSON via `as_dict()` | `ResponseStreamEvent` is a generated model — not directly JSON-serializable. The serializer converts via `.as_dict()`, so the on-disk records are plain JSON dicts that any reader (including a future shell script or recovery scanner) can parse. |

## Persistence file layout

When the host is configured with `resilient_background=True`, the
file-backed backing writes one JSONL file per caller-scoped lifecycle ID under the
configured `storage_dir`:

```text
<storage_dir>/<lifecycle_id>.jsonl
```

The host derives `lifecycle_id` using
`derive_lifecycle_id(response_id, user_id_key)`. For identified users this is
`lifecycle-` followed by the SHA-256 digest of the user key and public response
ID, so different users' replay logs cannot collide. The public response ID in
HTTP paths and SSE payloads does not change. Anonymous requests (`user_id_key`
is `None`) retain the original response ID as their lifecycle key and keep the
previous file naming convention. Identified users never adopt those shared
legacy replay logs.

Each line is a single JSON object of the form
`{"emit_time": <unix-float>, "payload": <event-dict>}`, ending with
a terminator record `{"emit_time": <float>, "__terminal__": true}` once
the stream is closed. The directory is created on first use.

Operators select the resilient root directory via
`AGENTSERVER_STATE_ROOT` (defaults to `~/.agentserver`); the responses
host derives the streams subdirectory as
`${AGENTSERVER_STATE_ROOT:-~/.agentserver}/streams/`. There is no
per-stream directory override — the unified `AGENTSERVER_STATE_ROOT`
is the single environment variable that controls all resilient
subdirectories (`tasks/`, `streams/`, `responses/`).

## Recovery on restart

A fresh process looks up replay using the same caller-scoped lifecycle ID:

```python
lifecycle_id = derive_lifecycle_id(response_id, user_id_key)
stream = await streams.get(lifecycle_id)
```

`get` rehydrates an existing `.jsonl` file from persisted events, but never
creates a file for an absent ID. Missing or expired replay raises
`EventStreamNotFoundError`. `get_or_create(lifecycle_id)` is reserved for
admitted execution that owns the producer lifecycle, not GET replay lookup.

- Buffered events become available to new subscribers immediately.
- `await stream.last_cursor()` returns the highest `sequence_number`
  that made it to disk before the crash.
- The recovered handler reads that cursor to learn what sequence
  number to assign to its next emit, keeping the assembled stream
  monotonically increasing across the crash boundary.

If the previous run finished cleanly (terminator on disk) AND every
persisted event has since expired, the rehydrated stream is in the
`GONE` state; `streams.get(lifecycle_id)` cleans up and reports it as missing.
Only a newly admitted producer may use `streams.get_or_create(lifecycle_id)`
to mint a fresh stream.

An empty ACTIVE file can remain after a crash before durable admission. Under
the caller-scoped create reservation, the host removes it only after confirming
that no live or pending execution, stored response, or resumable durable input
owns it. Storage failures or unavailable durable ownership lookup fail closed;
an empty cursor alone does not authorize reclamation.

DELETE retains exact caller-scoped ownership until replay and response-provider
cleanup succeed, including across cleanup errors and cancellation. Before
removing backing state, it conditionally fences that response's lifecycle input
in the durable task payload. Other turns and queued inputs are retained.
Recovery observes the fence before writes or admission and participates in the
same scoped reservations, so deleting a response cannot resurrect it on restart.

Each newly admitted durable input carries a server-generated private
`response_incarnation_id`. DELETE retains fences for old incarnations rather
than clearing a response-wide fence on reuse. The task primitive's conditional
resume writes the new incarnation with its input, and recovery validates that
exact persisted incarnation under scoped admission before it writes or runs.
This permits DELETE followed by a same-ID POST in the same conversation without
allowing an old recovered turn to reuse the new execution's references or
reservation. Legacy inputs without an incarnation retain fail-closed deletion
checks. Public HTTP/SSE IDs, task-chain input IDs, and replay filenames do not
change.

## HTTP / SSE wire mapping

The responses host exposes events through Server-Sent-Events on:

- `POST /responses` with `stream=true` — the **live wire**. The endpoint
  layer subscribes to the per-response stream and yields each emit as
  an SSE event.
- `GET /responses/{id}?stream=true` — **replay**. The endpoint looks up
  the persisted response using the caller's user partition before calling
  `streams.get(lifecycle_id)` and iterating buffered history. Storage errors
  fail closed rather than falling through to cached replay.
  - Cursored reconnect: the SSE `Last-Event-ID: N` header (or the
    `?starting_after=N` query alias retained for backward compatibility)
    is forwarded as `stream.subscribe(after=N)`.
  - A missing or unauthorized response returns HTTP `404`. If an authorized
    background response exists but its replay is absent or expired, the
    endpoint returns HTTP `400` with an invalid-mode error. The registry's
    `EventStreamNotFoundError` never causes a lookup to create a new replay log.

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
