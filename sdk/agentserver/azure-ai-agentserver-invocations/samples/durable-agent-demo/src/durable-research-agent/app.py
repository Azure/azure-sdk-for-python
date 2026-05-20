# Copyright (c) Microsoft. All rights reserved.

"""HTTP host for the durable research agent.

This file is just plumbing — the interesting durability logic is in ``agent.py``.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncGenerator
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from azure.ai.agentserver.core.durable import TaskCancelled, TaskFailed, TaskTerminated
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from agent import deep_research

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Azure clients ─────────────────────────────────────────────────────────────

_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
if not _endpoint:
    raise EnvironmentError("FOUNDRY_PROJECT_ENDPOINT is required.")

_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
_credential = DefaultAzureCredential()
_project_client = AIProjectClient(endpoint=_endpoint, credential=_credential)
_openai_client = _project_client.get_openai_client()


def get_openai_client():
    return _openai_client


def get_model() -> str:
    return _model


# ── SSE streaming helper ──────────────────────────────────────────────────────

async def _sse_stream(run: Any, invocation_id: str) -> AsyncGenerator[bytes, None]:
    yield f"data: {json.dumps({'type': 'started', 'invocation_id': invocation_id})}\n\n".encode()
    try:
        async for chunk in run:
            yield f"data: {chunk}\n\n".encode()
        result = await run.result()
        yield f"event: done\ndata: {json.dumps({'type': 'done', 'output': result.output})}\n\n".encode()
    except (TaskCancelled, TaskTerminated):
        yield f"event: cancelled\ndata: {json.dumps({'type': 'cancelled'})}\n\n".encode()
    except TaskFailed as exc:
        yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n".encode()


# ── HTTP handlers ─────────────────────────────────────────────────────────────

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start a research task. Send ``{"message": "crash"}`` to trigger a crash."""
    data = json.loads(await request.body() or b"{}")
    topic = data.get("message") or data.get("topic") or ""

    if not topic.strip():
        return JSONResponse({"error": "Provide a 'message' field"}, status_code=400)

    # Deliberate crash trigger for demo
    if topic.strip().lower() in ("crash", "💥", "kill"):
        logger.critical("💥 CRASH triggered via API")
        os._exit(137)

    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    task_id = f"research-{session_id}"

    run = await deep_research.start(
        task_id=task_id,
        input={"topic": topic, "invocation_id": invocation_id},
        session_id=session_id,
    )

    return StreamingResponse(
        _sse_stream(run, invocation_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Invocation-Id": invocation_id},
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Poll status — works even after crash + restart."""
    # The durable task system handles this automatically
    return JSONResponse({"invocation_id": request.state.invocation_id, "status": "check_stream"})


if __name__ == "__main__":
    app.run()
