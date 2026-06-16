# Copyright (c) Microsoft. All rights reserved.

"""Tier 1 ΓÇö Zero-Config Activity Protocol Agent (with debug logging).

The simplest possible activity protocol agent. The package auto-initializes
the M365 Agents SDK from environment variables, applies MSAL auth patches,
and bridges activities to the AgentApplication turn pipeline.

You write only handler logic ΓÇö no SDK wiring needed.
"""

import logging
from os import environ

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
logger = logging.getLogger("tier1-echo")

# Enable verbose logging for all relevant namespaces
for ns in ["azure.ai.agentserver", "microsoft_agents", "hypercorn"]:
    logging.getLogger(ns).setLevel(logging.DEBUG)

logger.info("========== TIER1-ECHO STARTING (debug build Jun 16 2026) ==========")
logger.info("Agent name: %s", environ.get("FOUNDRY_AGENT_NAME", "(not set)"))
logger.info("Agent version: %s", environ.get("FOUNDRY_AGENT_VERSION", "(not set)"))
logger.info("Session ID: %s", environ.get("FOUNDRY_AGENT_SESSION_ID", "(not set)"))
logger.info("Port: %s", environ.get("PORT", "8088"))
logger.info("Auth type: %s", environ.get("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE", "(not set)"))
logger.info("Client ID: %s", environ.get("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID", "(not set)"))
logger.info("Tenant ID: %s", environ.get("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID", "(not set)"))

from azure.ai.agentserver.activity import ActivityAgentServerHost

app = ActivityAgentServerHost()


@app.activity("message")
async def on_message(context, state):
    """Echo the user's message back with environment variables."""
    user_text = context.activity.text or ""
    logger.info("MESSAGE RECEIVED | text=%s | from=%s | conv=%s",
                user_text[:100],
                getattr(context.activity.from_property, "id", "?") if context.activity.from_property else "?",
                context.activity.conversation.id if context.activity.conversation else "?")
    if user_text.strip():
        # Build response with user message and env vars
        env_lines = ["=== tier1echo16jun313pm ENVIRONMENT VARIABLES ==="]
        for k, v in sorted(environ.items()):
            env_lines.append(f"{k}={v}")
        
        reply = f"[Echo agent Jun 16 2026 tier1echo16jun313pm PM ]\n\nYour message: {user_text}\n\n" + "\n".join(env_lines)
        await context.send_activity(reply)
        logger.info("REPLY SENT | text=%s", reply)


@app.activity("conversationUpdate")
async def on_members_added(context, state):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            logger.info("MEMBER ADDED | name=%s | id=%s", member.name, member.id)
            try:
                await context.send_activity(f"Welcome, {member.name}!")
            except Exception as exc:
                logger.warning("Could not send welcome: %s", exc)


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    logger.error("HANDLER ERROR | error=%s", error, exc_info=True)
    await context.send_activity(f"Sorry, something went wrong: {error}")


if __name__ == "__main__":
    app.run()