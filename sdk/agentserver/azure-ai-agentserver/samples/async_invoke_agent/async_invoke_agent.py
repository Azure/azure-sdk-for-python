"""Async invoke agent example.

Demonstrates get_invocation and cancel_invocation for long-running work.
Invocations run in background tasks; callers poll or cancel by ID.

.. warning::

    **In-memory demo only.**  This sample stores all invocation state
    (``self._tasks``, ``self._results``) in process memory.  Both in-flight
    ``asyncio.Task`` objects and completed results are lost on process restart
    — which *will* happen during platform rolling updates, health-check
    failures, and scaling events.

    For production long-running invocations:

    * Persist results to durable storage (Redis, Cosmos DB, etc.) inside
      ``_do_work`` **before** the method returns.
    * On startup, rehydrate any incomplete work or mark it as failed.
    * Consider an external task queue (Celery, Azure Queue, etc.) instead
      of ``asyncio.create_task`` for work that must survive restarts.

Usage::

    # Start the agent
    python async_invoke_agent.py

    # Start a long-running invocation
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"query": "analyze dataset"}'
    # -> x-agent-invocation-id: abc-123
    # -> {"invocation_id": "abc-123", "status": "running"}

    # Poll for result
    curl http://localhost:8088/invocations/abc-123
    # -> {"invocation_id": "abc-123", "status": "running"}   (still working)
    # -> {"invocation_id": "abc-123", "status": "completed"} (done)

    # Or cancel
    curl -X POST http://localhost:8088/invocations/abc-123/cancel
    # -> {"invocation_id": "abc-123", "status": "cancelled"}
"""
import asyncio
import json

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer


class AsyncAgent(AgentServer):
    """Agent that supports long-running invocations with get and cancel."""

    def __init__(self):
        super().__init__()
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: dict[str, bytes] = {}

    async def invoke(self, request: Request) -> Response:
        """Start a long-running invocation in a background task.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: JSON status indicating the task is running.
        :rtype: starlette.responses.JSONResponse
        """
        data = await request.json()
        invocation_id = request.state.invocation_id

        task = asyncio.create_task(self._do_work(invocation_id, data))
        self._tasks[invocation_id] = task

        return JSONResponse({
            "invocation_id": invocation_id,
            "status": "running",
        })

    async def get_invocation(self, request: Request) -> Response:
        """Retrieve a previous invocation result.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: JSON status or result.
        :rtype: starlette.responses.JSONResponse
        """
        invocation_id = request.state.invocation_id

        if invocation_id in self._results:
            return Response(content=self._results[invocation_id], media_type="application/json")

        if invocation_id in self._tasks:
            task = self._tasks[invocation_id]
            if not task.done():
                return JSONResponse({
                    "invocation_id": invocation_id,
                    "status": "running",
                })
            result = task.result()
            self._results[invocation_id] = result
            del self._tasks[invocation_id]
            return Response(content=result, media_type="application/json")

        return JSONResponse({"error": "not found"}, status_code=404)

    async def cancel_invocation(self, request: Request) -> Response:
        """Cancel a running invocation.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: JSON cancellation status.
        :rtype: starlette.responses.JSONResponse
        """
        invocation_id = request.state.invocation_id

        # Already completed — cannot cancel
        if invocation_id in self._results:
            return JSONResponse({
                "invocation_id": invocation_id,
                "status": "completed",
                "error": "invocation already completed",
            })

        if invocation_id in self._tasks:
            task = self._tasks[invocation_id]
            if task.done():
                # Task finished between check — treat as completed
                self._results[invocation_id] = task.result()
                del self._tasks[invocation_id]
                return JSONResponse({
                    "invocation_id": invocation_id,
                    "status": "completed",
                    "error": "invocation already completed",
                })
            task.cancel()
            del self._tasks[invocation_id]
            return JSONResponse({
                "invocation_id": invocation_id,
                "status": "cancelled",
            })

        return JSONResponse({"error": "not found"}, status_code=404)

    async def _do_work(self, invocation_id: str, data: dict) -> bytes:
        """Simulate long-running work.

        :param invocation_id: The invocation ID for this task.
        :type invocation_id: str
        :param data: The parsed request data.
        :type data: dict
        :return: JSON result bytes.
        :rtype: bytes
        """
        await asyncio.sleep(10)
        result = json.dumps({
            "invocation_id": invocation_id,
            "status": "completed",
            "output": f"Processed: {data}",
        }).encode()
        self._results[invocation_id] = result
        return result


if __name__ == "__main__":
    AsyncAgent().run()
