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
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer


# Holds questions waiting for a human reply, keyed by invocation_id
_waiting: dict[str, dict[str, Any]] = {}

server = AgentServer()


@server.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Handle messages and replies.

    :param request: The raw Starlette request.
    :type request: starlette.requests.Request
    :return: JSON response indicating status.
    :rtype: starlette.responses.JSONResponse
    """
    data = await request.json()
    invocation_id = request.state.invocation_id

    # --- Reply to a previous question ---
    reply_to = data.get("reply_to")
    if reply_to:
        if reply_to not in _waiting:
            return JSONResponse({"error": f"No pending question for {reply_to}"})

        return JSONResponse({
            "invocation_id": reply_to,
            "status": "completed",
            "response": f"Flight to {data.get('message', '?')} booked.",
        })

    # --- New request: ask a clarifying question ---
    _waiting[invocation_id] = {
        "message": data.get("message", ""),
    }
    return JSONResponse({
        "invocation_id": invocation_id,
        "status": "needs_input",
        "question": "Where would you like to fly to?",
    })


if __name__ == "__main__":
    server.run()
