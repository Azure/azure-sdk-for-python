"""Host a WeatherAgent via AgentServer with the Activity protocol.

Bridges the Activity protocol to AgentServer's ``/invocations`` endpoint.
Incoming requests carry Bot Framework Activity JSON; the server
deserialises them into ``microsoft_agents.activity.Activity`` objects,
dispatches to the ``WeatherAgent``, and serialises the reply activities
back to JSON.

This demonstrates that AgentServer can host agents built with the
Activity protocol — without depending on ``microsoft_agents.hosting.core``
or ``CloudAdapter``.

Usage::

    # Start the server
    python server.py

    # Send a message activity
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{
        "type": "message",
        "text": "What is the weather in Seattle tomorrow?",
        "from": {"id": "user-1", "name": "User"},
        "recipient": {"id": "agent-1", "name": "WeatherAgent"},
        "conversation": {"id": "conv-1"},
        "channelId": "custom",
        "serviceUrl": "http://localhost:8088"
      }'

    # Send a conversationUpdate to trigger the welcome message
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{
        "type": "conversationUpdate",
        "membersAdded": [{"id": "user-1", "name": "User"}],
        "from": {"id": "user-1"},
        "recipient": {"id": "agent-1", "name": "WeatherAgent"},
        "conversation": {"id": "conv-1"},
        "channelId": "custom",
        "serviceUrl": "http://localhost:8088"
      }'
"""

import logging

# Configure logging for the sample so all loggers (including the agent's)
# output to the console.  This must run before any logger.info() calls.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from microsoft_agents.activity import Activity

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.server import AgentServer

from activity_weather_agent import create_weather_agent

logger = logging.getLogger(__name__)


# -- Create the agent and server ---------------------------------------------

agent = create_weather_agent()
server = AgentServer()
# AgentServer adds its own StreamHandler to the "azure.ai.agentserver" logger.
# Stop propagation to the root logger to avoid duplicate lines from basicConfig.
logging.getLogger("azure.ai.agentserver").propagate = False
logger.info("AgentServer created, WeatherAgent wired to /invocations")


# -- Wire the Activity protocol to /invocations ------------------------------


@server.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Bridge ``POST /invocations`` to the Activity protocol.

    Deserialises the JSON body into an
    :class:`~microsoft_agents.activity.Activity`, dispatches to the
    agent's ``on_turn``, and returns the first reply activity as JSON.

    :param request: The raw Starlette request.
    :type request: starlette.requests.Request
    :return: JSON response containing the reply activity, or 200 with
        an empty status if no reply is produced.
    :rtype: starlette.responses.Response
    """
    data = await request.json()
    activity = Activity.model_validate(data)
    logger.info(
        "Received activity: type=%s, conversation=%s",
        activity.type,
        activity.conversation.id if activity.conversation else "unknown",
    )

    replies = await agent.on_turn(activity)

    if replies:
        # Serialise back to camelCase JSON (matching Bot Framework wire format).
        body = replies[0].model_dump(
            by_alias=True, exclude_none=True, mode="json"
        )
        logger.info(
            "Returning reply: type=%s, text=%r",
            body.get("type"), body.get("text", "")[:80],
        )
        return JSONResponse(body)

    logger.info("No reply activities produced, returning status ok")
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    server.run()
