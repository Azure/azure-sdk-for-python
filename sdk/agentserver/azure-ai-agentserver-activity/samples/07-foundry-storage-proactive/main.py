# Copyright (c) Microsoft. All rights reserved.

"""Foundry Storage Proactive Agent — durable proactive conversation references.

Builds the M365 ``AgentApplication`` with ``ProactiveOptions`` (self-hosted-app
pattern) and injects it into the host via ``agent_app=``. Users send
``/subscribe`` to store the current conversation reference in ``FoundryStorage``.
An external caller can then POST ``/notify/{conversation_id}`` (registered via
the host's ``routes=`` override) to resume that stored conversation and send a
proactive notification.

Usage::

    python main.py
"""

import sys
import traceback

from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from azure.ai.agentserver.activity import ActivityAgentServerHost, FoundryStorage, get_hosted_agent_env
from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    HttpAdapterBase,
    RestChannelServiceClientFactory,
    TurnContext,
    TurnState,
)
from microsoft_agents.hosting.core.app.proactive.proactive_options import ProactiveOptions

# get_hosted_agent_env() resolves the CONNECTIONS__* settings WITHOUT mutating
# the process environment (see 03-self-hosted-app).
config = load_configuration_from_env(get_hosted_agent_env())
storage = FoundryStorage()
connection_manager = MsalConnectionManager(**config)
client_factory = RestChannelServiceClientFactory(connection_manager)
adapter = HttpAdapterBase(channel_service_client_factory=client_factory)
authorization = Authorization(storage, connection_manager, **config)
agent_app = AgentApplication[TurnState](
    storage=storage,
    adapter=adapter,
    authorization=authorization,
    proactive=ProactiveOptions(storage=storage),
    **config,
)


@agent_app.message("/subscribe")
async def on_subscribe(context: TurnContext, _state: TurnState):
    """Persist the current conversation reference for future proactive sends."""
    await agent_app.proactive.store_conversation(context)
    conversation_id = context.activity.conversation.id
    await context.send_activity(
        "Stored this conversation in FoundryStorage.\n\n"
        f"POST `/notify/{conversation_id}` to send a proactive notification."
    )


@agent_app.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    """Default message handler."""
    await context.send_activity("Send **/subscribe** to store this conversation for proactive notifications.")


@agent_app.error
async def on_error(context: TurnContext, error: Exception):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


async def notify(request) -> Response:
    """Resume a stored conversation reference and send a proactive message."""
    conversation_id = request.path_params["conversation_id"]

    async def send_notification(context: TurnContext, _state: TurnState):
        await context.send_activity("Proactive notification sent from a conversation reference in FoundryStorage.")

    try:
        await agent_app.proactive.continue_conversation(adapter, conversation_id, send_notification)
    except KeyError:
        return JSONResponse(status_code=404, content={"error": "Conversation reference not found."})
    return JSONResponse({"sent": True, "conversation_id": conversation_id})


# routes= extends the Foundry activity routes with the custom /notify endpoint;
# agent_app= hosts the pre-built AgentApplication (adapter taken from agent_app.adapter).
app = ActivityAgentServerHost(
    agent_app=agent_app,
    routes=[Route("/notify/{conversation_id}", notify, methods=["POST"])],
)

if __name__ == "__main__":
    app.run()
