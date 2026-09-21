# Copyright (c) Microsoft. All rights reserved.

"""Self-Hosted Activity Agent - build the M365 AgentApplication yourself.

The developer constructs the full M365 Agents SDK stack (``MsalConnectionManager``,
``HttpAdapterBase``, ``AgentApplication``) and hands the pre-built app to the host
via ``ActivityAgentServerHost(agent_app=...)``. The host drives it
through the Foundry activity turn pipeline (claims, parsing, delivery) for you.

Use this pattern when you need full control over how the ``AgentApplication`` is
built (custom storage / connection manager / authorization) but still want the
Activity-protocol host to run it.
"""

from azure.ai.agentserver.activity import ActivityAgentServerHost, get_hosted_agent_env

from microsoft_agents.activity import Activity, load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    HttpAdapterBase,
    MemoryStorage,
    RestChannelServiceClientFactory,
    TurnContext,
    TurnState,
)

# Resolve the config the M365 connection manager needs. get_hosted_agent_env()
# returns a mapping (os.environ overlaid with the derived CONNECTIONS__* settings)
# WITHOUT mutating the process environment — pass it straight to the SDK loader.
config = load_configuration_from_env(get_hosted_agent_env())
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


# ── Business logic ───────────────────────────────────────────────


@agent_app.activity("message")
async def on_message(context: TurnContext, state: TurnState):
    """Echo the user's message back."""
    user_text = context.activity.text or ""
    await context.send_activity(Activity(type="typing"))
    reply = f"[Self-Hosted] Echo: {user_text}"
    await context.send_activity(reply)


@agent_app.activity("conversationUpdate")
async def on_members_added(context: TurnContext, state: TurnState):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            await context.send_activity(f"Welcome, {member.name}!")


@agent_app.error
async def on_error(context: TurnContext, error: Exception):
    """Handle unhandled errors."""
    await context.send_activity("The agent encountered an error.")


# ── Foundry host with the pre-built AgentApplication ─────────────

app = ActivityAgentServerHost(agent_app=agent_app)

if __name__ == "__main__":
    app.run()
