# Copyright (c) Microsoft. All rights reserved.

"""HTTP host for the durable research agent.

This file is minimal plumbing. The durability + steering logic is in ``agent.py``.

Routes (all of them are platform-managed — only ``/invocations*`` is reachable
through the Foundry endpoint proxy):
  * ``POST /invocations``                       — fire-and-forget dispatch (or
                                                   steering input on an in-progress run);
                                                   special: ``{"message": "crash"}``
                                                   when ``DEMO_MODE=1`` forces a process
                                                   exit so the platform nanny restarts us
  * ``GET  /invocations/{id}?last_event_id=N``  — SSE stream of the active run
  * ``POST /invocations/{id}/cancel``           — operator cancel
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core.durable import TaskCancelled, TaskConflictError, TaskFailed
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from agent import deep_research

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = InvocationAgentServerHost()


# --- Invocation handlers ---------------------------------------------------

@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Dispatch a research task (fire-and-forget).

    Input shape: ``{"message": "<topic>"}``.

    Two special behaviors driven by the request body:

    * ``{"message": "crash"}`` (when the container has ``DEMO_MODE=1``) forces
      ``os._exit(137)`` shortly after returning ``202``. The platform nanny
      worker restarts the container within ~5-10 minutes; the durable task
      auto-resumes from its last checkpoint. This is gated by ``DEMO_MODE``
      so a stray request can't accidentally kill a production agent.

    * Any other ``{"message": "<topic>"}`` dispatches a normal research run.
      If a steerable run is already in progress on this session, the input is
      queued as a steering input — the agent winds down the current turn at
      the next checkpoint and re-enters with the new topic.
    """
    body = await request.body()
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {}
    topic = str(data.get("message") or "").strip()
    if not topic:
        return JSONResponse({"error": "Provide a 'message' field"}, status_code=400)

    # Demo-only crash trigger.
    if topic.lower() in ("crash", "kill", "💥") and os.environ.get("DEMO_MODE") == "1":
        logger.critical("CRASH triggered via /invocations message=%r — exiting in 300ms", topic)

        async def _crash() -> None:
            await asyncio.sleep(0.3)
            os._exit(137)

        asyncio.get_event_loop().create_task(_crash())
        return JSONResponse(
            {
                "status": "crashing",
                "message": (
                    "Process will exit. The platform nanny worker will restart "
                    "the container within ~5-10 minutes; the durable task will "
                    "automatically resume from its last checkpoint."
                ),
            },
            status_code=202,
        )

    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    # ONE durable task per session so steering finds the active run.
    # invocation_id labels the call; session_id labels the long-lived task.
    task_id = session_id
    logger.info("POST handler: session_id=%r task_id=%r topic=%r", session_id, task_id, topic)

    status = "started"
    try:
        await deep_research.start(
            task_id=task_id,
            input={"topic": topic, "invocation_id": invocation_id},
        )
    except TaskConflictError as exc:
        # Steerable task already running. The framework queued our input and
        # signalled cancel; the agent will wind down at the next checkpoint
        # and re-enter with our input.
        status = "steered"
        logger.info("POST handler: queued steering input (current_status=%s)",
                    getattr(exc, "current_status", None))

    return JSONResponse(
        {
            "status": status,
            "invocation_id": invocation_id,
            "session_id": session_id,
        },
        status_code=202,
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Stream SSE from the active task, or replay from disk if finished.

    The platform routes ``GET /invocations/{id}`` to this container based on
    the invocation-to-session mapping set up by the original POST. Clients
    can pass ``?last_event_id=N`` to skip events they've already seen on a
    reconnect.

    If the durable task is still active we stream live events from the
    in-memory run. If the task has already finished (or this container
    doesn't currently hold the run) we replay from the persisted
    ``stream.jsonl`` file — so a reconnect after completion still shows the
    full transcript.
    """
    invocation_id = request.state.invocation_id
    session_id = (
        getattr(request.state, "session_id", None) or app.config.session_id
    )
    task_id = session_id  # one task per session — match POST handler

    last_event_id = request.query_params.get("last_event_id", "")
    skip_count = int(last_event_id) if last_event_id.isdigit() else 0
    logger.info("GET handler: invocation_id=%r task_id=%r skip=%d",
                invocation_id, task_id, skip_count)

    run = await deep_research.get_active_run(task_id)

    if run is not None:
        async def live_stream():
            event_id = 0
            try:
                async for chunk in run:
                    event_id += 1
                    if event_id <= skip_count:
                        continue
                    yield f"id: {event_id}\ndata: {chunk}\n\n"
                result = await run.result()
                event_id += 1
                yield (
                    f"id: {event_id}\ndata: "
                    + json.dumps({
                        "type": "done",
                        "phases_completed": result.output.get("phases_completed", 0),
                    })
                    + "\n\n"
                )
            except TaskCancelled:
                event_id += 1
                yield (
                    f"id: {event_id}\ndata: "
                    + json.dumps({"type": "done", "reason": "cancelled"})
                    + "\n\n"
                )
            except TaskFailed as exc:
                event_id += 1
                yield (
                    f"id: {event_id}\ndata: "
                    + json.dumps({"type": "done", "reason": "failed", "error": str(exc)})
                    + "\n\n"
                )

        return StreamingResponse(
            live_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    # No live run — replay from the persisted stream file.
    stream_file = (
        Path.home() / ".durable-tasks" / "_streams" / task_id / "stream.jsonl"
    )
    if not stream_file.exists():
        return JSONResponse(
            {"status": "not_found",
             "message": "No active or finished task for this session."},
            status_code=404,
        )

    async def file_replay():
        event_id = 0
        for line in stream_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if "__done__" in data:
                event_id += 1
                yield (
                    f"id: {event_id}\ndata: "
                    + json.dumps({"type": "done", "reason": "replayed"})
                    + "\n\n"
                )
                return
            event_id += 1
            if event_id <= skip_count:
                continue
            yield f"id: {event_id}\ndata: {json.dumps(data)}\n\n"
        # File present but no __done__ sentinel — task may still be recovering.
        event_id += 1
        yield (
            f"id: {event_id}\ndata: "
            + json.dumps({"type": "done", "reason": "replay_incomplete"})
            + "\n\n"
        )

    return StreamingResponse(
        file_replay(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Cancel the running research task."""
    invocation_id = request.state.invocation_id
    session_id = (
        getattr(request.state, "session_id", None) or app.config.session_id
    )
    task_id = session_id  # one task per session — match POST handler
    logger.info("CANCEL handler: invocation_id=%r task_id=%r", invocation_id, task_id)

    run = await deep_research.get_active_run(task_id)
    if run is None:
        return JSONResponse({"status": "not_found", "message": "No active task to cancel."})

    await run.cancel()
    return JSONResponse({"status": "cancelled", "message": "Task cancellation requested."})


if __name__ == "__main__":
    app.run()
