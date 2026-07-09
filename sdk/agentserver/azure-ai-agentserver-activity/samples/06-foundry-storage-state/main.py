# Copyright (c) Microsoft. All rights reserved.

"""Foundry Storage State Agent — Activity Protocol with durable state.

Demonstrates the zero-config decorator pattern with platform-managed durable
storage. Conversation and user counters are persisted by the M365 Agents SDK
through ``FoundryStorage`` after each turn.

Usage::

    python foundry_storage_state_agent.py
"""

import logging
import sys
import traceback

from azure.ai.agentserver.activity import ActivityAgentServerHost, FoundryStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)

storage = FoundryStorage()
app = ActivityAgentServerHost(storage=storage)


@app.activity("conversationUpdate")
async def on_members_added(context, _state):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            await context.send_activity(
                "Hello! I persist conversation and user state with FoundryStorage.\n\n"
                "Send any message to increment the durable counters."
            )


@app.activity("message")
async def on_message(context, state):
    """Increment durable conversation and user counters."""
    conversation_count = state.conversation.get_value("message_count", lambda: 0)
    user_count = state.user.get_value("message_count", lambda: 0)

    conversation_count += 1
    user_count += 1
    state.conversation.set_value("message_count", conversation_count)
    state.user.set_value("message_count", user_count)

    await context.send_activity(
        "FoundryStorage persisted this turn.\n\n"
        f"- Conversation messages: **{conversation_count}**\n"
        f"- Messages from you: **{user_count}**"
    )


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    app.run()
