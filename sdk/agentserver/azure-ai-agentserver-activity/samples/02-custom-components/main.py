# Copyright (c) Microsoft. All rights reserved.

"""Echo activity protocol agent that overrides an M365 component.

Same echo behavior as ``01-echo``, but overrides one of the M365 components the
host would otherwise build itself. Any of ``storage`` / ``connection_manager`` /
``adapter`` / ``authorization`` / ``connection_config`` can be passed; the host builds the
rest from the environment. This sample overrides ``storage`` as the concrete
example.

Because the host still builds the connection manager itself, it derives the
``CONNECTIONS__*`` settings internally — no ``get_hosted_agent_env()`` call is
needed here. (You only resolve those yourself when you build the connection
manager — see ``03-self-hosted-app``.)

Swap ``MemoryStorage`` for a durable M365 ``Storage`` implementation (e.g.
Cosmos DB / Blob) to persist ``TurnState`` across restarts.
"""

from microsoft_agents.hosting.core import MemoryStorage

from azure.ai.agentserver.activity import ActivityAgentServerHost

# Override one component (storage here); everything else is built from the environment.
storage = MemoryStorage()

host = ActivityAgentServerHost(storage=storage)
app = host.agent_app


@app.activity("message")
async def on_message(context, state):
    """Echo the user's message back."""
    user_text = context.activity.text or ""
    if user_text.strip():
        await context.send_activity(f"Echo (custom components): {user_text}")


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
    host.run()
