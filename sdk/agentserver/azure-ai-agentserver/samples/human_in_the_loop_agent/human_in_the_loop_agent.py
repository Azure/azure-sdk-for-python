"""Human-in-the-loop invoke agent example.

Demonstrates a synchronous human-in-the-loop pattern using only
POST /invocations. The agent asks a clarifying question, and the client
replies in a second request.

Flow:
  1. Client sends a message  -> agent returns a question + invocation_id
  2. Client sends a reply    -> agent returns the final result

Usage::

    # Start the agent
    python human_in_the_loop_agent.py

    # Step 1: Send a request — agent asks a clarifying question
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"message": "Book me a flight"}'
    # -> {"invocation_id": "<ID>", "status": "needs_input", "question": "Where would you like to fly to?"}

    # Step 2: Reply with the answer — agent completes
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"reply_to": "<ID>", "message": "Seattle"}'
    # -> {"invocation_id": "<ID>", "status": "completed", "response": "Flight to Seattle booked."}
"""
import json
from typing import Any

from azure.ai.agentserver import AgentServer, InvokeRequest


class HumanInTheLoopAgent(AgentServer):
    """Agent that asks one clarifying question before completing a request."""

    def __init__(self) -> None:
        super().__init__()
        # Holds questions waiting for a human reply, keyed by invocation_id
        self._waiting: dict[str, dict[str, Any]] = {}

    async def invoke(self, request: InvokeRequest) -> bytes:
        """Handle messages and replies.

        :param request: The invocation request.
        :type request: InvokeRequest
        :return: JSON response bytes.
        :rtype: bytes
        """
        data = json.loads(request.body)

        # --- Reply to a previous question ---
        reply_to = data.get("reply_to")
        if reply_to:
            if reply_to not in self._waiting:
                return json.dumps({"error": f"No pending question for {reply_to}"}).encode()

            return json.dumps({
                "invocation_id": reply_to,
                "status": "completed",
                "response": f"Flight to {data.get('message', '?')} booked.",
            }).encode()

        # --- New request: ask a clarifying question ---
        self._waiting[request.invocation_id] = {
            "message": data.get("message", ""),
        }
        return json.dumps({
            "invocation_id": request.invocation_id,
            "status": "needs_input",
            "question": "Where would you like to fly to?",
        }).encode()


if __name__ == "__main__":
    HumanInTheLoopAgent().run()
