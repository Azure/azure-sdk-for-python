# Copyright (c) Microsoft. All rights reserved.

"""Suggested Actions Agent — Activity Protocol with quick-reply buttons.

Demonstrates using suggested actions to present quick-reply buttons
that disappear after the user taps one. This provides a guided
conversation experience without cluttering the chat with stale buttons.

Suggested actions differ from card buttons:
- Card buttons remain visible after tapping
- Suggested actions disappear after the user makes a selection
- Best for quick choices, confirmations, or menu options

Architecture::

    ActivityAgentServerHost (Foundry contract)
        └── M365 bridge (auto-init)
            └── TurnContext → handlers below
                └── context.send_activity(Activity(suggested_actions=...))

Required environment variables (auto-injected in Foundry hosted containers):

    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID

Usage::

    python suggested_actions_activity_agent.py
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


# ── Helpers ──────────────────────────────────────────────────────


def _create_reply_with_suggestions(text, choices):
    """Create an Activity with suggested actions.

    Suggested actions appear as quick-reply buttons below the message.
    They disappear after the user taps one.

    :param text: The message text to display.
    :param choices: List of button labels (strings).
    :returns: An Activity dict with suggested_actions.
    """
    from microsoft_agents.activity import Activity, SuggestedActions, CardAction

    actions = [
        CardAction(type="imBack", title=choice, value=choice)
        for choice in choices
    ]

    return Activity(
        type="message",
        text=text,
        suggested_actions=SuggestedActions(actions=actions),
    )


# ── Color responses ──────────────────────────────────────────────

COLOR_RESPONSES = {
    "red": "Red is the color of passion and energy! 🔴",
    "blue": "Blue is the color of calm and trust! 🔵",
    "green": "Green is the color of nature and growth! 🟢",
    "yellow": "Yellow is the color of sunshine and happiness! 🟡",
}

COLOR_CHOICES = list(COLOR_RESPONSES.keys())


# ── Activity handlers ────────────────────────────────────────────


@app.activity("conversationUpdate")
async def on_members_added(context, state):
    """Welcome new members with suggested action buttons."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            reply = _create_reply_with_suggestions(
                "Welcome to the Suggested Actions sample! Pick a color:",
                COLOR_CHOICES,
            )
            await context.send_activity(reply)


@app.activity("message")
async def on_message(context, state):
    """Handle color selection and re-prompt with suggestions."""
    user_text = (context.activity.text or "").strip().lower()
    if not user_text:
        return

    if user_text in COLOR_RESPONSES:
        response_text = COLOR_RESPONSES[user_text]
    else:
        response_text = (
            f"**{user_text}** is not a recognized color. "
            "Please pick one of the suggested options below."
        )

    # Always re-prompt with suggested actions so the user can pick again
    reply = _create_reply_with_suggestions(
        f"{response_text}\n\nPick another color:",
        COLOR_CHOICES,
    )
    await context.send_activity(reply)


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    app.run()
