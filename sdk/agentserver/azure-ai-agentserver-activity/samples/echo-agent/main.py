# Copyright (c) Microsoft. All rights reserved.

"""Tier 1 - Zero-Config Activity Protocol Agent.

The simplest possible activity protocol agent. The package auto-initializes
the M365 Agents SDK from environment variables, applies MSAL auth patches,
and bridges activities to the AgentApplication turn pipeline.

You write only handler logic - no SDK wiring needed.
"""

from azure.ai.agentserver.activity import ActivityAgentServerHost

app = ActivityAgentServerHost()


@app.activity("message")
async def on_message(context, state):
    """Echo the user's message back."""
    user_text = context.activity.text or ""
    if user_text.strip():
        reply = f"Echo: {user_text}"
        await context.send_activity(reply)


@app.activity("conversationUpdate")
async def on_members_added(context, state):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            await context.send_activity(f"Welcome, {member.name}!")


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    await context.send_activity(f"Sorry, something went wrong: {error}")


if __name__ == "__main__":
    app.run()