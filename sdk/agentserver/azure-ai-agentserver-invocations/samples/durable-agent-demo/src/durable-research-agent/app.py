# Copyright (c) Microsoft. All rights reserved.

"""HTTP host for the LangGraph-based durable research agent.

Durability is provided by LangGraph's SQLite checkpointer — no @durable_task
decorator needed. The graph automatically resumes from its last checkpoint
when invoked with the same thread_id after a crash.

Streaming: Live token events via asyncio.Queue during execution.
GET reconnect: Replays completed stage results from checkpoint state.
Cancel: Sets an asyncio.Event checked between graph nodes.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from agent import get_checkpoint_state, get_stream_queue, init_checkpointer, run_research, STAGES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── HTTP handlers ─────────────────────────────────────────────────────────────

app = InvocationAgentServerHost()

# Track cancel events per session
_cancel_events: dict[str, asyncio.Event] = {}


@app.on_event("startup")
async def startup():
    """Initialize checkpointer on app startup."""
    await init_checkpointer()
    logger.info("LangGraph research agent ready")


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
            await asyncio.sleep(0.1)
            os._exit(137)

        return StreamingResponse(
            crash_after_response(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    session_id: str = request.state.session_id
    thread_id = f"research-{session_id}"
    logger.info(f"POST handler: session_id={session_id!r}, thread_id={thread_id!r}")

    # Create cancel event for this session
    cancel_event = asyncio.Event()
    _cancel_events[session_id] = cancel_event

    # Start or resume the graph — returns a live stream queue
    queue = await run_research(thread_id, topic, cancel_event=cancel_event)

    # Stream SSE events from the queue
    async def event_stream():
        try:
            while True:
                item = await queue.get()
                if item is None:  # sentinel — done
                    yield f"data: {json.dumps({'type': 'done', 'full_text': ''})}\n\n"
                    break
                yield f"data: {json.dumps(item)}\n\n"
        finally:
            _cancel_events.pop(session_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Reconnect to an existing research session.

    1. If a live stream queue exists (graph still running), attach to it.
    2. Otherwise, replay completed stage results from the LangGraph checkpoint.
    """
    session_id = (
        request.query_params.get("agent_session_id")
        or os.environ.get("FOUNDRY_AGENT_SESSION_ID", "")
    )
    thread_id = f"research-{session_id}"
    logger.info(f"GET handler: session_id={session_id!r}, thread_id={thread_id!r}")

    # Try live stream first
    queue = get_stream_queue(thread_id)
    if queue is not None:
        logger.info("GET handler: attaching to live stream")

        async def live_stream():
            while True:
                item = await queue.get()
                if item is None:
                    yield f"data: {json.dumps({'type': 'done', 'full_text': ''})}\n\n"
                    break
                yield f"data: {json.dumps(item)}\n\n"

        return StreamingResponse(
            live_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    # Fallback: replay from checkpoint state
    state = await get_checkpoint_state(thread_id)
    if state is None:
        return JSONResponse({"status": "not_found", "message": "No research session found."})

    logger.info(f"GET handler: replaying from checkpoint (stage {state.get('current_stage', 0)}/{len(STAGES)})")

    async def replay_stream():
        results = state.get("results", [])
        total = len(STAGES)

        for i, r in enumerate(results):
            stage_name = r["stage"]
            header = f"\n\n**[Stage {i+1}/{total}]** {stage_name}...\n"
            yield f"data: {json.dumps({'type': 'token', 'content': header})}\n\n"
            yield f"data: {json.dumps({'type': 'token', 'content': r['result']})}\n\n"
            footer = f"\n\u2705 Stage {i+1}/{total} complete.\n"
            yield f"data: {json.dumps({'type': 'token', 'content': footer})}\n\n"

        current = state.get("current_stage", 0)
        if current >= total:
            done_msg = "\n\n---\n\u2705 **Research complete!**\n"
            yield f"data: {json.dumps({'type': 'token', 'content': done_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'full_text': ''})}\n\n"
        else:
            partial_msg = f"\n\n[Completed {current}/{total} stages \u2014 task may be recovering...]\n"
            yield f"data: {json.dumps({'type': 'token', 'content': partial_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'full_text': ''})}\n\n"

    return StreamingResponse(
        replay_stream(),
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
    logger.info(f"CANCEL handler: session_id={session_id!r}")

    cancel_event = _cancel_events.get(session_id)
    if cancel_event is None:
        return JSONResponse({"status": "not_found", "message": "No active task to cancel."})

    cancel_event.set()
    return JSONResponse({"status": "cancelled", "message": "Task cancellation requested."})


if __name__ == "__main__":
    app.run()
