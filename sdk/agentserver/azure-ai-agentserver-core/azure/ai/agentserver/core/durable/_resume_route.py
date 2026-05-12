# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""POST /tasks/resume — Starlette route for external task resume triggers.

Returns an empty body with the appropriate status code:
- 202 Accepted: resume dispatched successfully
- 404 Not Found: task not found or not in a resumable state
- 409 Conflict: task is already in progress
"""

from __future__ import annotations

import json
import logging

from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

logger = logging.getLogger("azure.ai.agentserver.durable")


async def _handle_resume_request(request: Request) -> Response:
    """Handle POST /tasks/resume.

    Expects a JSON body with ``{"task_id": "..."}`` and dispatches the
    resume to the DurableTaskManager.

    :param request: The incoming HTTP request.
    :type request: Request
    :return: Empty-body response with status code.
    :rtype: Response
    """
    from ._manager import (  # pylint: disable=import-outside-toplevel
        get_task_manager,
    )

    try:
        body = await request.json()
    except (json.JSONDecodeError, ValueError):
        return Response(status_code=400)

    task_id = body.get("task_id")
    if not task_id or not isinstance(task_id, str):
        return Response(status_code=400)

    try:
        manager = get_task_manager()
    except RuntimeError:
        return Response(status_code=503)

    try:
        await manager.handle_resume(task_id)
        logger.info("Resume accepted for task %s", task_id)
        return Response(status_code=202)

    except Exception as exc:
        msg = str(exc).lower()
        if "not found" in msg:
            return Response(status_code=404)
        if "not 'suspended'" in msg or "already" in msg or "conflict" in msg:
            return Response(status_code=409)
        logger.error("Resume failed for task %s: %s", task_id, exc, exc_info=True)
        return Response(status_code=500)


def create_resume_route() -> Route:
    """Create the Starlette Route for POST /tasks/resume.

    :return: A Starlette Route to be added to the host.
    :rtype: Route
    """
    return Route("/tasks/resume", _handle_resume_request, methods=["POST"])
