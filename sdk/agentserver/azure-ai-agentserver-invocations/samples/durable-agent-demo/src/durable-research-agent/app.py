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
    """Start a research task. Send ``{"message": "crash"}`` to trigger a crash."""
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

    # Deliberate crash trigger for demo — respond first, then crash
    if topic.strip().lower() in ("crash", "💥", "kill"):
        logger.critical("💥 CRASH triggered via API — will exit after response")

        async def crash_after_response():
            yield f"data: {json.dumps({'type': 'done', 'full_text': '💥 Process crashing now...'})}\n\n"
            await asyncio.sleep(0.1)  # ensure response is flushed
            os._exit(137)

        return StreamingResponse(
            crash_after_response(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    task_id = f"research-{session_id}"
    logger.info(f"POST handler: session_id={session_id!r}, task_id={task_id!r}")

    try:
        run = await deep_research.start(
            task_id=task_id,
            input={"topic": topic, "invocation_id": invocation_id},
            session_id=session_id,
        )
    except TaskConflictError:
        # Task still in_progress (recovered after crash and still running)
        return JSONResponse(
            {"status": "in_progress", "message": "Research task is still running (recovered after crash). Use GET to reconnect."},
            status_code=200,
        )

    # Stream SSE events in Foundry-compatible format
    async def event_stream():
        try:
            async for chunk in run:
                # Each chunk from ctx.stream() is already a JSON string
                yield f"data: {chunk}\n\n"
            result = await run.result()
            yield f"data: {json.dumps({'type': 'done', 'full_text': result.output.get('report', '')})}\n\n"
        except (TaskCancelled, TaskTerminated):
            yield f"data: {json.dumps({'type': 'done', 'full_text': '[Task was cancelled]'})}\n\n"
        except TaskFailed as exc:
            yield f"data: {json.dumps({'type': 'done', 'full_text': f'[Error: {exc}]'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Reconnect to an existing invocation — stream from the active task.

    After a crash, the client calls GET /invocations/{id} to resume receiving
    the SSE stream. First tries the in-memory task handle; if unavailable
    (task completed or not yet recovered), falls back to replaying from the
    persisted stream file.
    """
    session_id = (
        request.query_params.get("agent_session_id")
        or os.environ.get("FOUNDRY_AGENT_SESSION_ID", "")
    )
    task_id = f"research-{session_id}"
    logger.info(f"GET handler: session_id={session_id!r}, task_id={task_id!r}")

    run = deep_research.get_active_run(task_id)
    logger.info(f"GET handler: get_active_run({task_id!r}) -> {run}")

    if run is not None:
        # Live task — stream from it
        async def live_stream():
            try:
                async for chunk in run:
                    yield f"data: {chunk}\n\n"
                result = await run.result()
                yield f"data: {json.dumps({'type': 'done', 'full_text': result.output.get('report', '')})}\n\n"
            except (TaskCancelled, TaskTerminated):
                yield f"data: {json.dumps({'type': 'done', 'full_text': '[Task was cancelled]'})}\n\n"
            except TaskFailed as exc:
                yield f"data: {json.dumps({'type': 'done', 'full_text': f'[Error: {exc}]'})}\n\n"

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
        for line in stream_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if "__done__" in data:
                yield f"data: {json.dumps({'type': 'done', 'full_text': ''})}\n\n"
                return
            yield f"data: {json.dumps(data)}\n\n"
        # File exists but no __done__ sentinel — task may still be running
        yield f"data: {json.dumps({'type': 'done', 'full_text': '[Stream replay complete — task may still be recovering]'})}\n\n"

    return StreamingResponse(
        file_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Cancel the running research task."""
    session_id = (
        request.query_params.get("agent_session_id")
        or os.environ.get("FOUNDRY_AGENT_SESSION_ID", "")
    )
    task_id = f"research-{session_id}"
    logger.info(f"CANCEL handler: session_id={session_id!r}, task_id={task_id!r}")

    run = deep_research.get_active_run(task_id)
    if run is None:
        return JSONResponse({"status": "not_found", "message": "No active task to cancel."})

    await run.cancel()
    return JSONResponse({"status": "cancelled", "message": "Task cancellation requested."})


if __name__ == "__main__":
    app.run()
