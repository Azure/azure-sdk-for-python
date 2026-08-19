# Copyright (c) Microsoft. All rights reserved.

"""Multi-Protocol Agent - Activity + Invocations.

Composes the Activity and Invocations protocols on a single server using
Python mixin inheritance.

Both protocols share the same server on port 8088:
    POST /activity/messages  - Activity protocol (Teams/M365)
    POST /invocations        - Invocations protocol (HTTP API)
"""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.activity import ActivityAgentServerHost
from azure.ai.agentserver.invocations import InvocationAgentServerHost


class MultiProtocolHost(ActivityAgentServerHost, InvocationAgentServerHost):
    pass


host = MultiProtocolHost()
app = host.agent_app


@app.activity("message")
async def on_teams_message(context, state):
    """Handle messages from Teams via Activity protocol."""
    user_text = context.activity.text or ""
    if user_text.strip():
        await context.send_activity(f"[Multi-Protocol] Echo: {user_text}")


@host.invoke_handler
async def handle_invocation(request: Request) -> Response:
    """Handle HTTP invocations via Invocations protocol."""
    data = await request.json()
    message = data.get("message", "")
    return JSONResponse(
        {
            "reply": f"[Multi-Protocol] Echo: {message}",
            "protocol": "invocations",
        }
    )


if __name__ == "__main__":
    host.run()
