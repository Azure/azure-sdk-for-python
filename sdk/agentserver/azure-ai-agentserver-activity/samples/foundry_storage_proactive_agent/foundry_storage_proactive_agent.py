# Copyright (c) Microsoft. All rights reserved.

"""Foundry Storage Proactive Agent — durable proactive conversation references.

Demonstrates the handler pattern with M365 ``ProactiveOptions``. Users send
``/subscribe`` to store the current conversation reference in ``FoundryStorage``.
An external caller can then POST ``/notify/{conversation_id}`` to resume that
stored conversation and send a proactive notification.

Usage::

    python foundry_storage_proactive_agent.py
"""

import logging
import sys
import traceback
from os import environ

from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from azure.ai.agentserver.activity import ActivityAgentServerHost, FoundryStorage, apply_msal_patches
from microsoft_agents.activity import Activity, load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    ClaimsIdentity,
    HttpAdapterBase,
    RestChannelServiceClientFactory,
    TurnContext,
    TurnState,
)
from microsoft_agents.hosting.core.app.proactive.proactive_options import ProactiveOptions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)

apply_msal_patches()

config = load_configuration_from_env(environ)
STORAGE = FoundryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**config)
CLIENT_FACTORY = RestChannelServiceClientFactory(CONNECTION_MANAGER)
ADAPTER = HttpAdapterBase(channel_service_client_factory=CLIENT_FACTORY)
AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **config)

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE,
    adapter=ADAPTER,
    authorization=AUTHORIZATION,
    proactive=ProactiveOptions(storage=STORAGE),
    **config,
)


@AGENT_APP.message("/subscribe")
async def on_subscribe(context: TurnContext, _state: TurnState):
    """Persist the current conversation reference for future proactive sends."""
    await AGENT_APP.proactive.store_conversation(context)
    conversation_id = context.activity.conversation.id
    await context.send_activity(
        "Stored this conversation in FoundryStorage.\n\n"
        f"POST `/notify/{conversation_id}` to send a proactive notification."
    )


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    """Default message handler."""
    await context.send_activity("Send **/subscribe** to store this conversation for proactive notifications.")


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


async def handle_activity(request) -> Response:
    """Bridge Activity Protocol requests to the M365 Agents SDK."""
    activity = Activity.model_validate(request.state.activity)
    if not activity.type or not activity.conversation or not activity.conversation.id:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "invalid_request", "message": "Missing type or conversation.id"}},
        )

    claims = ClaimsIdentity({}, is_authenticated=False, authentication_type="Anonymous")
    invoke_response = await ADAPTER.process_activity(claims, activity, AGENT_APP.on_turn)

    if activity.type == "invoke" or activity.delivery_mode == "expectReplies":
        if invoke_response is not None:
            return JSONResponse(content=invoke_response.body, status_code=invoke_response.status)
        return JSONResponse(content={}, status_code=200)
    return Response(status_code=202)


async def notify(request) -> Response:
    """Resume a stored conversation reference and send a proactive message."""
    conversation_id = request.path_params["conversation_id"]

    async def send_notification(context: TurnContext, _state: TurnState):
        await context.send_activity("Proactive notification sent from a conversation reference in FoundryStorage.")

    try:
        await AGENT_APP.proactive.continue_conversation(ADAPTER, conversation_id, send_notification)
    except KeyError:
        return JSONResponse(status_code=404, content={"error": "Conversation reference not found."})
    return JSONResponse({"sent": True, "conversation_id": conversation_id})


app = ActivityAgentServerHost(
    handler=handle_activity,
    routes=[Route("/notify/{conversation_id}", notify, methods=["POST"])],
)

if __name__ == "__main__":
    app.run()
