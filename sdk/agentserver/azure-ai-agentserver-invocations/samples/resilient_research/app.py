"""HTTP host for the resilient deep-research agent.

Exposes the ``deep_research`` resilient task over the invocations
protocol with the FULL pattern matrix:

- ``POST /invocations`` with body ``{"topic": "..."}`` and an
  ``Accept: text/event-stream`` header — returns a live SSE stream of
  events as the research progresses.
- ``POST /invocations`` without the header — returns ``202`` with the
  ``invocation_id``; clients then connect to the GET endpoint to
  stream OR poll.
- ``GET /invocations/{id}`` with ``Accept: text/event-stream`` and an
  optional ``?last_event_id=N`` query — streams the per-turn events,
  skipping anything the client already saw (the cursor is the
  event's monotonic ``sequence_number``). Works for both freshly-
  started turns and turns that have been running for a while.
- ``GET /invocations/{id}`` without the SSE accept header — returns a
  JSON snapshot of the task's current status / payload.
- ``POST /invocations/{id}/cancel`` — operator cancel of the
  per-session task (steering is automatic via re-POSTing instead).

Streaming wiring ():

- ``streams.use_file_backed_replay(...)`` is called once at module
  import (app startup) per streaming.md §7.8. The file-backed
  backing persists events to disk so a subscriber reconnecting after
  a container crash + restart sees the pre-crash + post-crash
  events with no gap.
- ``cursor_fn`` reads the event's ``sequence_number`` (stamped by
  the agent's ``emit`` closure) so ``?last_event_id=N`` reconnects
  skip exactly the events the client already received.
- The HTTP layer extracts ``invocation_id`` from
  ``request.state.invocation_id`` (per-turn identifier per §7.8),
  reserves the stream id BEFORE starting the task, and propagates
  ``invocation_id`` to the handler via
  ``task.start(input={"invocation_id": inv_id, ...})``.
- The handler reads ``ctx.input["invocation_id"]`` and calls
  ``await streams.get_or_create(inv_id)`` — gets the SAME
  registry-cached instance.

Recovery: if the container crashes mid-research and is restarted,
the framework re-invokes ``deep_research`` with
``ctx.entry_mode == "recovered"`` and the same input. The same
``invocation_id`` is preserved; the file-backed stream is rehydrated
from disk so reconnecting subscribers (including the original POST-
SSE client if it reattaches via GET) see the pre-crash events plus
a fresh ``type: "recovered"`` marker plus the post-crash continuation.

Steering: a new POST while a turn is running enqueues the input as a
steering input — the agent winds down the current turn at the next
checkpoint via ``_finish_turn`` (which closes the per-turn stream
cleanly) and the framework re-enters with the new ``ctx.input``.
The new turn gets a new ``invocation_id`` from the platform; the
new ``invocation_id`` is the new stream id. The HTTP layer does not
need to distinguish steered turns from fresh turns — see
``agent.py`` for the discipline.

Usage::

    # From inside this sample directory:
    pip install -r requirements.txt
    python app.py
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core.streaming import (
    EventStream,
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from .agent import deep_research as _package_deep_research
except ImportError:  # allows `python app.py` from inside this directory
    from agent import deep_research as _script_deep_research

    deep_research = _script_deep_research
else:
    deep_research = _package_deep_research

logger = logging.getLogger(__name__)

# --- Streams bootstrap (run once at module import) -------------------------

# Per-turn streams persist to disk so they survive a container crash +
# restart. ``cursor_fn`` reads the agent's natural sequence number so
# ``?last_event_id=N`` reconnects skip already-delivered events.
#
# The registration uses the ergonomic defaults: ``storage_dir`` defaults to
# ``resolve_state_subdir("streams")`` (``<AGENTSERVER_STATE_ROOT>/streams``),
# ``ttl_seconds`` defaults to 600 (10 min, bounding disk usage once a stream is
# closed and its events age out), and serialization defaults to JSON — so the
# only thing this sample supplies is the ``cursor_fn``.
streams.use_file_backed_replay(cursor_fn=lambda ev: ev["sequence_number"])

app = InvocationAgentServerHost()


# --- SSE rendering ---------------------------------------------------------


async def _sse_from_stream(
    stream: EventStream,
    invocation_id: str,
    *,
    skip_after: int | None = None,
) -> AsyncGenerator[bytes, None]:
    """Render a stream's events as SSE-formatted bytes.

    Each event's ``sequence_number`` becomes the SSE ``id:`` field so
    a reconnecting client can pass it back as ``Last-Event-ID`` (or
    ``?last_event_id=N``) and pick up from there. The terminator
    payload is emitted on clean stream close; ``EventStreamNotFoundError``
    (the stream was destroyed under us) flushes a ``superseded``
    event so the consumer can tell stream-end from "you got cut off".
    """
    try:
        async for chunk in stream.subscribe(after=skip_after):
            seq = chunk.get("sequence_number", "")
            yield f"id: {seq}\ndata: {json.dumps(chunk)}\n\n".encode()
        done = {"type": "done", "invocation_id": invocation_id}
        yield f"event: done\ndata: {json.dumps(done)}\n\n".encode()
    except EventStreamNotFoundError:
        superseded = {"type": "superseded", "invocation_id": invocation_id}
        yield f"event: superseded\ndata: {json.dumps(superseded)}\n\n".encode()


# --- Invocation handlers ---------------------------------------------------


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Dispatch a research task with full pattern coverage.

    Body: ``{"topic": "<topic>"}``.

    If ``Accept: text/event-stream`` is set, returns a live SSE
    stream of the new turn's events (POST-SSE pattern). Otherwise
    returns ``202 Accepted`` with the ``invocation_id`` for clients
    that prefer to connect via GET (poll OR GET-SSE pattern).

    A POST while a steerable run is already in progress on this
    session enqueues the input as a steering input — the running
    turn winds down at the next checkpoint and the framework
    re-enters with the new topic. The new turn streams to the new
    ``invocation_id`` reserved here.
    """
    body = await request.body()
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {}
    topic = str(data.get("topic") or data.get("message") or "").strip()
    if not topic:
        return JSONResponse(
            {"error": "Provide a 'topic' field"},
            status_code=400,
        )

    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    # ONE resilient task per session so steering finds the active run.
    # invocation_id labels THIS turn; session_id labels the long-
    # lived task.
    task_id = f"research-{session_id}"

    # Reserve the per-turn stream id BEFORE starting the task. The
    # file-backed replay backing means even if no subscriber attaches
    # before the handler emits, the events go to disk and a later
    # subscriber catches up via ``?last_event_id=N``.
    stream = await streams.get_or_create(invocation_id)

    # Steering is transparent: for a ``steerable=True`` task,
    # ``task.start()`` queues the input on the in-progress task's
    # steering queue WITHOUT raising. See ``agent.py`` for the
    # ``_finish_turn`` discipline that makes this safe.
    await deep_research.start(
        task_id=task_id,
        input={"topic": topic, "invocation_id": invocation_id},
    )

    if "text/event-stream" in request.headers.get("accept", ""):
        return StreamingResponse(
            _sse_from_stream(stream, invocation_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    return JSONResponse(
        {
            "status": "started",
            "invocation_id": invocation_id,
            "session_id": session_id,
            "task_id": task_id,
        },
        status_code=202,
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Stream OR poll the per-invocation state.

    With ``Accept: text/event-stream``: SSE stream of the turn's
    events. ``?last_event_id=N`` (or the standard ``Last-Event-ID``
    header) skips events whose ``sequence_number`` <= N — the
    file-backed replay backing serves the gap from disk before
    live-tailing.

    Without the SSE accept header: returns the task's current
    snapshot from ``deep_research.get(task_id)``.

    HTTP mapping (from streaming.md §exceptions table):
      - 404 for ANY missing stream — never registered, explicitly
        deleted, or destroyed by TTL eviction. The registry exposes a
        single ``EventStreamNotFoundError`` for all "id is not a live
        stream" cases; treat it uniformly.
    """
    invocation_id: str = request.state.invocation_id

    wants_stream = "text/event-stream" in request.headers.get("accept", "")
    if wants_stream:
        last_event_id_q = request.query_params.get("last_event_id", "")
        last_event_id_h = request.headers.get("last-event-id", "")
        raw = last_event_id_q or last_event_id_h
        skip_after: int | None = int(raw) if raw.isdigit() else None

        try:
            stream = await streams.get(invocation_id)
        except EventStreamNotFoundError:
            return JSONResponse(
                {"status": "not_found", "message": "No live stream for this invocation id."},
                status_code=404,
            )

        return StreamingResponse(
            _sse_from_stream(stream, invocation_id, skip_after=skip_after),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    # JSON-snapshot path (polling clients).
    session_id: str = request.state.session_id
    task_id = f"research-{session_id}"
    # Task.get + TaskSnapshot removed. Use the
    # provider directly for read-only inspection (returns TaskInfo).
    from azure.ai.agentserver.core.tasks._manager import get_task_manager

    mgr = get_task_manager()
    info: Any = await mgr.provider.get(task_id)
    if info is None:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse(
        {
            "task_id": task_id,
            "invocation_id": invocation_id,
            "status": info.status,
            "payload": info.payload,
        }
    )


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Cancel the running research task.

    Cancel applies to the per-session resilient task (``task_id ==
    f"research-{session_id}"``). The handler observes
    ``ctx.cancel.is_set()`` and runs its cooperative wind-down at
    the next checkpoint, which closes the per-turn stream before
    suspending.
    """
    session_id: str = request.state.session_id
    task_id = f"research-{session_id}"

    # A multi-turn task's ``get_active_run`` requires the in-flight turn's
    # ``input_id``; a session-level cancel doesn't know it. Use the manager's
    # task_id-only accessor (what the one-shot ``Task.get_active_run``
    # delegates to) to grab whichever turn is currently active, then
    # cooperatively cancel it via ``run.cancel()``.
    from azure.ai.agentserver.core.tasks._manager import get_task_manager

    run = await get_task_manager().get_active_run(task_id)
    if run is None:
        return JSONResponse({"status": "not_found", "message": "No active task to cancel."})

    await run.cancel()
    return JSONResponse({"status": "cancelled", "message": "Task cancellation requested."})


if __name__ == "__main__":
    app.run()
