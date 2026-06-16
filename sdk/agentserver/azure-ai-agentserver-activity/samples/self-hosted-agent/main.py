# Copyright (c) Microsoft. All rights reserved.

"""Self-Hosted Activity Agent — Full M365 SDK Control.

Demonstrates the handler pattern (Tier 3) where the developer owns the
full M365 Agents SDK pipeline: MsalConnectionManager, HttpAdapterBase,
AgentApplication, and a custom bridge handler.

Use this pattern when you need:
- Direct access to M365 SDK features (auth_handlers, regex message matching)
- Custom error handling or response logic
- Full control over the activity processing pipeline
"""

import logging
import sys
import traceback
from os import environ

from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.activity import ActivityAgentServerHost, apply_msal_patches

from microsoft_agents.activity import Activity, load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    ClaimsIdentity,
    HttpAdapterBase,
    MemoryStorage,
    RestChannelServiceClientFactory,
    TurnContext,
    TurnState,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger("self-hosted-agent")

# ── M365 SDK setup ───────────────────────────────────────────────
# Apply MSAL patches before creating MsalConnectionManager.
apply_msal_patches()

logger.info("Initializing M365 SDK...")
config = load_configuration_from_env(environ)
storage = MemoryStorage()
connection_manager = MsalConnectionManager(**config)
client_factory = RestChannelServiceClientFactory(connection_manager)
adapter = HttpAdapterBase(channel_service_client_factory=client_factory)
authorization = Authorization(storage, connection_manager, **config)
agent_app = AgentApplication[TurnState](
    storage=storage,
    adapter=adapter,
    authorization=authorization,
    **config,
)
logger.info("M365 SDK initialized successfully.")


# ── Business logic ───────────────────────────────────────────────

@agent_app.activity("message")
async def on_message(context: TurnContext, state: TurnState):
    """Echo the user's message back."""
    user_text = context.activity.text or ""
    logger.info("Message received | text=%s", user_text[:100])
    await context.send_activity(Activity(type="typing"))
    reply = f"[Self-Hosted] Echo: {user_text}"
    await context.send_activity(reply)
    logger.info("Reply sent | text=%s", reply)


@agent_app.activity("conversationUpdate")
async def on_members_added(context: TurnContext, state: TurnState):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            try:
                await context.send_activity(f"Welcome, {member.name}!")
            except Exception as exc:
                logger.warning("Could not send welcome: %s", exc)


@agent_app.error
async def on_error(context: TurnContext, error: Exception):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error.")


# ── Foundry host with custom handler ─────────────────────────────

async def handle(request) -> Response:
    """Bridge to M365 SDK — parses activity and delegates to agent_app."""
    activity_dict = request.state.activity
    activity_type = activity_dict.get("type", "unknown")
    session_id = request.state.session_id

    logger.info("Activity received | type=%s | session=%s", activity_type, session_id)

    activity = Activity.model_validate(activity_dict)

    if not activity.type or not activity.conversation or not activity.conversation.id:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "invalid_request", "message": "Missing type or conversation.id"}},
        )

    claims = ClaimsIdentity({}, is_authenticated=False, authentication_type="Anonymous")

    try:
        invoke_response = await adapter.process_activity(claims, activity, agent_app.on_turn)
    except PermissionError:
        return Response(status_code=401)
    except TypeError as exc:
        logger.warning("TypeError (likely missing serviceUrl) | error=%s", exc)
        return Response(status_code=202)
    except Exception as exc:
        logger.exception("Error processing activity | error=%s", exc)
        return Response(status_code=202)

    if activity.type == "invoke" or activity.delivery_mode == "expectReplies":
        if invoke_response is not None:
            return JSONResponse(content=invoke_response.body, status_code=invoke_response.status)
        return JSONResponse(content={}, status_code=200)

    return Response(status_code=202)


app = ActivityAgentServerHost(handler=handle)

if __name__ == "__main__":
    app.run()