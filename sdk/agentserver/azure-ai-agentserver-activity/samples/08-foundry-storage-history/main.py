# Copyright (c) Microsoft. All rights reserved.

"""Foundry Storage History Agent — Activity Protocol with durable history.

The simplest durable-storage sample: it persists the full conversation
transcript with ``FoundryStorage`` so the history survives restarts and
scale-out. Each turn is appended to a list held in conversation state;
the agent echoes the running transcript back.

Commands:

    /history   show the stored transcript
    /clear     forget the stored transcript

Usage::

    python foundry_storage_history_agent.py
"""

import logging
import sys
import traceback

from azure.ai.agentserver.activity import ActivityAgentServerHost, FoundryStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)

# Platform-managed storage — no Cosmos account or connection string to manage.
storage = FoundryStorage()
app = ActivityAgentServerHost(storage=storage)


@app.activity("conversationUpdate")
async def on_members_added(context, _state):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            await context.send_activity(
                "Hello! I remember our conversation with FoundryStorage.\n\n"
                "Send any message and I'll append it to the durable transcript. "
                "Use `/history` to see it or `/clear` to forget it."
            )


@app.activity("message")
async def on_message(context, state):
    """Persist the turn in conversation history and echo the transcript back."""
    user_text = (context.activity.text or "").strip()
    if not user_text:
        return

    history = state.conversation.get_value("history", lambda: [])

    if user_text == "/clear":
        state.conversation.set_value("history", [])
        await context.send_activity("Transcript cleared.")
        return

    if user_text == "/history":
        if not history:
            await context.send_activity("No messages stored yet.")
        else:
            transcript = "\n".join(f"{i}. {line}" for i, line in enumerate(history, 1))
            await context.send_activity(f"**Stored transcript ({len(history)}):**\n\n{transcript}")
        return

    history.append(f"You: {user_text}")
    state.conversation.set_value("history", history)

    await context.send_activity(
        f"Saved. I've persisted **{len(history)}** message(s) this conversation. "
        "Send `/history` to see them all."
    )


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    app.run()
