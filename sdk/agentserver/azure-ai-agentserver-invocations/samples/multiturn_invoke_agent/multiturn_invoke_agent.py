"""Multi-turn session invoke agent example.

Demonstrates session-based conversations where context accumulates
across multiple invocations via the ``agent_session_id`` query parameter.

.. warning::

    **In-memory demo only.**  Session history is stored in process memory
    and is lost on restart.  For production use, persist history to
    durable storage (Redis, Cosmos DB, etc.).

Usage::

    # Start the agent
    python multiturn_invoke_agent.py

    # Turn 1 — start planning
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "I want to plan a vacation"}'
    # -> {"reply": "Welcome! Where would you like to go, and for how long?", ...}

    # Turn 2 — provide details
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "Japan for 2 weeks, interested in culture and food"}'
    # -> {"reply": "Great choice! What is your budget ...?", ...}

    # Turn 3 — add constraints
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "Budget is $5000, prefer direct flights"}'
    # -> {"reply": "Here is a suggested itinerary ...", ...}
"""
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost


app = InvocationAgentServerHost()

# In-memory session store — keyed by session ID.
_sessions: dict[str, list[dict[str, str]]] = {}


def _build_reply(history: list[dict[str, str]]) -> str:
    """Generate a contextual reply based on conversation history.

    In production this would call a language model with the full history.

    :param history: List of message dicts with ``role`` and ``content`` keys.
    :type history: list[dict[str, str]]
    :return: The assistant reply text.
    :rtype: str
    """
    turn = len([m for m in history if m["role"] == "user"])
    if turn == 1:
        return "Welcome! Where would you like to go, and for how long?"
    if turn == 2:
        return (
            "Great choice! Could you share your budget range "
            "and any travel preferences (direct flights, accommodation type)?"
        )
    return (
        f"Thanks for all the details! Based on our {turn}-turn conversation, "
        "here is a suggested itinerary. Let me know if you'd like to adjust anything."
    )


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Process a conversational turn, accumulating session context.

    The session ID comes from the ``agent_session_id`` query parameter
    (set automatically on ``request.state.session_id`` by the framework).

    :param request: The raw Starlette request.
    :type request: starlette.requests.Request
    :return: JSON reply with session metadata.
    :rtype: starlette.responses.JSONResponse
    """
    data = await request.json()
    session_id = request.state.session_id
    user_message = data.get("message", "")

    # Retrieve or create session history
    history = _sessions.setdefault(session_id, [])
    history.append({"role": "user", "content": user_message})

    reply = _build_reply(history)
    history.append({"role": "assistant", "content": reply})

    return JSONResponse({
        "reply": reply,
        "session_id": session_id,
        "turn": len([m for m in history if m["role"] == "user"]),
    })


if __name__ == "__main__":
    app.run()
