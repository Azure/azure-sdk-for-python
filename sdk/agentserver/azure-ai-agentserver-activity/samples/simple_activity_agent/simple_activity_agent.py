# Copyright (c) Microsoft. All rights reserved.

"""Simple Echo Agent — Activity Protocol.

The simplest activity protocol agent. Echoes messages back, welcomes
new members, handles installation events, and processes invoke activities.

The package auto-initializes the M365 Agents SDK from environment variables.
You write only handler logic — no SDK wiring needed.

Architecture::

    ActivityAgentServerHost (Foundry contract: headers, tracing, errors)
        └── M365 bridge (auto-init AgentApplication from env vars)
            └── adapter.process_activity(activity, agent_app.on_turn)
                └── TurnContext → handler functions below
                    └── context.send_activity() → POST to channel serviceUrl

Required environment variables (auto-injected in Foundry hosted containers):

    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID

Usage::

    python simple_activity_agent.py

    # Deployed to Foundry as a hosted agent, messages arrive via
    # POST /activity/messages or POST /api/messages
"""

import logging
import sys
import traceback

from azure.ai.agentserver.activity import ActivityAgentServerHost

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = ActivityAgentServerHost()


# ── Activity handlers ────────────────────────────────────────────


@app.activity("conversationUpdate")
async def on_members_added(context, state):
    """Welcome new members when they join the conversation."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            name = getattr(member, "name", None) or "there"
            await context.send_activity(
                f"Welcome, {name}! I'm an echo agent powered by the Activity Protocol. "
                "Type anything and I'll repeat it back."
            )


@app.activity("message")
async def on_message(context, state):
    """Echo the user's message back."""
    user_text = context.activity.text or ""
    if not user_text.strip():
        return
    logger.info("Message received: %s", user_text[:100])
    await context.send_activity(f"You said: {user_text}")


@app.activity("invoke")
async def on_invoke(context, state):
    """Handle invoke activities (adaptive card actions, task modules, etc.).

    Invoke activities require a synchronous response with a status code.
    """
    from microsoft_agents.activity import Activity, ActivityTypes

    logger.info("Invoke received: %s", getattr(context.activity, "name", ""))
    invoke_response = Activity(
        type=ActivityTypes.invoke_response,
        value={"status": 200},
    )
    await context.send_activity(invoke_response)


@app.activity("installationUpdate")
async def on_installation_update(context, state):
    """Handle agent installation/uninstallation events."""
    action = getattr(context.activity, "action", None)
    if action == "add":
        await context.send_activity("Thank you for adding me! Type anything to get started.")
    elif action == "remove":
        await context.send_activity("Goodbye!")


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    app.run()
