"""Async invoke agent example.

Demonstrates get_invocation and cancel_invocation for long-running work.
Invocations run in background tasks; callers poll or cancel by ID.

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
from typing import Optional

from azure.ai.agentserver import AgentServer, InvokeRequest


class AsyncAgent(AgentServer):
    """Agent that supports long-running invocations with get and cancel."""

    def __init__(self):
        super().__init__()
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: dict[str, bytes] = {}

    async def invoke(self, request: InvokeRequest) -> bytes:
        """Start a long-running invocation in a background task.

        :param request: The invocation request.
        :type request: InvokeRequest
        :return: JSON status indicating the task is running.
        :rtype: bytes
        """
        data = json.loads(request.body)

        task = asyncio.create_task(self._do_work(request.invocation_id, data))
        self._tasks[request.invocation_id] = task

        return json.dumps({
            "invocation_id": request.invocation_id,
            "status": "running",
        }).encode()

    async def get_invocation(self, invocation_id: str) -> bytes:
        """Retrieve a previous invocation result.

        :param invocation_id: The invocation ID to look up.
        :type invocation_id: str
        :return: JSON status or result bytes.
        :rtype: bytes
        """
        if invocation_id in self._results:
            return self._results[invocation_id]

        if invocation_id in self._tasks:
            task = self._tasks[invocation_id]
            if not task.done():
                return json.dumps({
                    "invocation_id": invocation_id,
                    "status": "running",
                }).encode()
            result = task.result()
            self._results[invocation_id] = result
            del self._tasks[invocation_id]
            return result

        return json.dumps({"error": "not found"}).encode()

    async def cancel_invocation(
        self,
        invocation_id: str,
        body: Optional[bytes] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> bytes:
        """Cancel a running invocation.

        :param invocation_id: The invocation ID to cancel.
        :type invocation_id: str
        :param body: Optional request body bytes.
        :type body: Optional[bytes]
        :param headers: Optional request headers.
        :type headers: Optional[dict[str, str]]
        :return: JSON cancellation status.
        :rtype: bytes
        """
        # Already completed — cannot cancel
        if invocation_id in self._results:
            return json.dumps({
                "invocation_id": invocation_id,
                "status": "completed",
                "error": "invocation already completed",
            }).encode()

        if invocation_id in self._tasks:
            task = self._tasks[invocation_id]
            if task.done():
                # Task finished between check — treat as completed
                self._results[invocation_id] = task.result()
                del self._tasks[invocation_id]
                return json.dumps({
                    "invocation_id": invocation_id,
                    "status": "completed",
                    "error": "invocation already completed",
                }).encode()
            task.cancel()
            del self._tasks[invocation_id]
            return json.dumps({
                "invocation_id": invocation_id,
                "status": "cancelled",
            }).encode()

        return json.dumps({"error": "not found"}).encode()

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
