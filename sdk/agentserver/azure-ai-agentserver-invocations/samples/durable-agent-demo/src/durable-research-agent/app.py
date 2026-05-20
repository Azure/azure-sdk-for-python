# Copyright (c) Microsoft. All rights reserved.

"""HTTP host for the durable research agent.

This file is minimal plumbing — the durability logic is in ``agent.py``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core.durable import TaskCancelled, TaskConflictError, TaskFailed, TaskTerminated
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from agent import deep_research

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── HTTP handlers ─────────────────────────────────────────────────────────────

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Dispatch a research task (fire-and-forget).

    Returns immediately with 202 + invocation/session IDs.
    The client then calls GET /invocations/{id} to stream results.
    Send ``{"message": "crash"}`` to trigger a deliberate crash for demo.
    """
    body = await request.body()
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {"message": body.decode("utf-8", errors="replace").strip()}

    topic = data.get("message") or ""
    # Foundry sends input as a list of messages
    if not topic and isinstance(data.get("input"), list):
        messages = data["input"]
        if messages and isinstance(messages[-1], dict):
            topic = messages[-1].get("content", "")
    elif not topic and isinstance(data.get("input"), str):
        topic = data["input"]

    if not topic.strip():
        return JSONResponse({"error": "Provide a 'message' field"}, status_code=400)

    # Deliberate crash trigger for demo — return 202, then crash asynchronously
    if topic.strip().lower() in ("crash", "💥", "kill"):
        logger.critical("💥 CRASH triggered via API — will exit shortly")

        async def _crash():
            await asyncio.sleep(0.3)  # give time for response to flush
            os._exit(137)

        asyncio.get_event_loop().create_task(_crash())
        return JSONResponse(
            {"status": "crashing", "message": "💥 Process will crash now"},
            status_code=202,
        )

    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    task_id = f"research-{session_id}"
    logger.info(f"POST handler: session_id={session_id!r}, task_id={task_id!r}")

    status = "started"
    try:
        await deep_research.start(
            task_id=task_id,
            input={"topic": topic, "invocation_id": invocation_id},
            session_id=session_id,
        )
    except TaskConflictError:
        # Task already running (recovered after crash)
        status = "in_progress"
        logger.info(f"POST handler: TaskConflictError — task already running")

    # Return immediately — platform sees 202 and preserves invocation mapping
    return JSONResponse(
        {
            "status": status,
            "invocation_id": invocation_id,
            "session_id": session_id,
            "task_id": task_id,
        },
        status_code=202,
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Stream SSE from the active task or replay from persisted file.

    The platform routes GET /invocations/{id} to this container based on
    the invocation→session mapping preserved from the fire-and-forget POST.
    Session ID is derived from the framework config (FOUNDRY_AGENT_SESSION_ID).

    Supports ``last_event_id`` query param to skip already-received events
    on reconnect (platform strips non x-client- headers, so we use a param).
    """
    session_id = request.state.session_id if hasattr(request.state, "session_id") and request.state.session_id else app.config.session_id
    task_id = f"research-{session_id}"

    # Skip already-seen events: client passes last_event_id query param on reconnect
    last_event_id = request.query_params.get("last_event_id", "")
    skip_count = int(last_event_id) if last_event_id.isdigit() else 0
    logger.info(f"GET handler: session_id={session_id!r}, task_id={task_id!r}, skip={skip_count}")

    run = deep_research.get_active_run(task_id)
    logger.info(f"GET handler: get_active_run({task_id!r}) -> {run}")

    if run is not None:
        # Live task — stream from it, skipping already-seen events
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
                yield f"id: {event_id}\ndata: {json.dumps({'type': 'done', 'full_text': result.output.get('report', '')})}\n\n"
            except (TaskCancelled, TaskTerminated):
                event_id += 1
                yield f"id: {event_id}\ndata: {json.dumps({'type': 'done', 'full_text': '[Task was cancelled]'})}\n\n"
            except TaskFailed as exc:
                event_id += 1
                yield f"id: {event_id}\ndata: {json.dumps({'type': 'done', 'full_text': f'[Error: {exc}]'})}\n\n"

        return StreamingResponse(
            live_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    # Fallback: replay from persisted stream file
    from pathlib import Path

    stream_file = Path.home() / ".durable-tasks" / "_streams" / task_id / "stream.jsonl"
    if not stream_file.exists():
        return JSONResponse({"status": "not_found", "message": "No active task or stream history for this session."})

    logger.info(f"GET handler: falling back to stream file {stream_file}")

    async def file_stream():
        event_id = 0
        for line in stream_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if "__done__" in data:
                event_id += 1
                yield f"id: {event_id}\ndata: {json.dumps({'type': 'done', 'full_text': ''})}\n\n"
                return
            event_id += 1
            if event_id <= skip_count:
                continue
            yield f"id: {event_id}\ndata: {json.dumps(data)}\n\n"
        # File exists but no __done__ sentinel — task may still be running
        event_id += 1
        yield f"id: {event_id}\ndata: {json.dumps({'type': 'done', 'full_text': '[Stream replay complete — task may still be recovering]'})}\n\n"

    return StreamingResponse(
        file_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Cancel the running research task."""
    session_id = request.state.session_id if hasattr(request.state, "session_id") and request.state.session_id else app.config.session_id
    task_id = f"research-{session_id}"
    logger.info(f"CANCEL handler: session_id={session_id!r}, task_id={task_id!r}")

    run = deep_research.get_active_run(task_id)
    if run is None:
        return JSONResponse({"status": "not_found", "message": "No active task to cancel."})

    await run.cancel()
    return JSONResponse({"status": "cancelled", "message": "Task cancellation requested."})


if __name__ == "__main__":
    app.run()
