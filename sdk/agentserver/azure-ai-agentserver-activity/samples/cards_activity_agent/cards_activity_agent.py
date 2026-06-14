# Copyright (c) Microsoft. All rights reserved.

"""Cards Agent — Activity Protocol with rich card types.

Demonstrates using rich cards (Adaptive Cards, Hero Cards, etc.) to
enhance conversation design.

Available commands:
    1 — Adaptive Card (interactive form with input and submit)
    2 — Hero Card (title, subtitle, image, buttons)
    3 — Thumbnail Card (compact card with thumbnail image)
    4 — Receipt Card (receipt with items and totals)
    help — Show this menu

Architecture::

    ActivityAgentServerHost (Foundry contract)
        └── M365 bridge (auto-init)
            └── TurnContext → handlers below
                └── context.send_activity(MessageFactory.attachment(...))

Required environment variables (auto-injected in Foundry hosted containers):

    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID

Usage::

    python cards_activity_agent.py
"""

import json
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


# ── Card definitions ─────────────────────────────────────────────


ADAPTIVE_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.5",
    "body": [
        {
            "type": "TextBlock",
            "text": "Activity Protocol — Adaptive Card Sample",
            "weight": "Bolder",
            "size": "Medium",
        },
        {
            "type": "TextBlock",
            "text": "This is an interactive Adaptive Card. Fill in the form and submit!",
            "wrap": True,
        },
        {
            "type": "Input.Text",
            "id": "userInput",
            "placeholder": "Type something here...",
            "label": "Your message",
            "isRequired": True,
        },
        {
            "type": "Input.ChoiceSet",
            "id": "colorChoice",
            "label": "Pick a color",
            "choices": [
                {"title": "Red", "value": "red"},
                {"title": "Blue", "value": "blue"},
                {"title": "Green", "value": "green"},
            ],
        },
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Submit",
            "data": {"action": "adaptiveCardSubmit"},
        }
    ],
}


def _make_hero_card():
    """Create a Hero Card attachment."""
    return {
        "contentType": "application/vnd.microsoft.card.hero",
        "content": {
            "title": "Activity Protocol Hero Card",
            "subtitle": "A hero card with an image and action buttons",
            "text": (
                "Hero cards are great for presenting key information with "
                "a large image, title, and action buttons."
            ),
            "images": [
                {
                    "url": "https://learn.microsoft.com/en-us/azure/ai-services/media/azure-ai-services.png",
                    "alt": "Azure AI Services",
                }
            ],
            "buttons": [
                {
                    "type": "openUrl",
                    "title": "Azure AI Documentation",
                    "value": "https://learn.microsoft.com/azure/ai-services/",
                },
                {
                    "type": "imBack",
                    "title": "Say hello",
                    "value": "hello",
                },
            ],
        },
    }


def _make_thumbnail_card():
    """Create a Thumbnail Card attachment."""
    return {
        "contentType": "application/vnd.microsoft.card.thumbnail",
        "content": {
            "title": "Activity Protocol Thumbnail Card",
            "subtitle": "Compact card with thumbnail image",
            "text": (
                "Thumbnail cards are similar to hero cards but use "
                "a smaller image, good for list-style layouts."
            ),
            "images": [
                {
                    "url": "https://learn.microsoft.com/en-us/azure/ai-services/media/azure-ai-services.png",
                    "alt": "Azure AI",
                }
            ],
            "buttons": [
                {
                    "type": "openUrl",
                    "title": "Learn More",
                    "value": "https://learn.microsoft.com/azure/ai-services/",
                }
            ],
        },
    }


def _make_receipt_card():
    """Create a Receipt Card attachment."""
    return {
        "contentType": "application/vnd.microsoft.card.receipt",
        "content": {
            "title": "Activity Protocol Receipt",
            "facts": [
                {"key": "Order Number", "value": "AP-2026-001"},
                {"key": "Payment Method", "value": "Visa **** 1234"},
            ],
            "items": [
                {
                    "title": "Azure AI Agent Hosting",
                    "subtitle": "Foundry Hosted Agent",
                    "price": "$0.00",
                    "quantity": "1",
                },
                {
                    "title": "Activity Protocol SDK",
                    "subtitle": "azure-ai-agentserver-activity",
                    "price": "$0.00",
                    "quantity": "1",
                },
            ],
            "total": "$0.00",
            "tax": "$0.00",
            "buttons": [
                {
                    "type": "openUrl",
                    "title": "View in Azure Portal",
                    "value": "https://portal.azure.com",
                }
            ],
        },
    }


INTRO_TEXT = (
    "**Cards Sample — Activity Protocol**\n\n"
    "Type a number to see a card:\n\n"
    "- **1** — Adaptive Card (interactive form)\n"
    "- **2** — Hero Card (title, image, buttons)\n"
    "- **3** — Thumbnail Card (compact layout)\n"
    "- **4** — Receipt Card (items and totals)\n"
    "- **help** — Show this menu"
)


# ── Activity handlers ────────────────────────────────────────────


@app.activity("conversationUpdate")
async def on_members_added(context, state):
    """Welcome new members with the card menu."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            await context.send_activity(INTRO_TEXT)


@app.activity("message")
async def on_message(context, state):
    """Route commands to card builders."""
    from microsoft_agents.activity import Activity

    user_text = (context.activity.text or "").strip().lower()
    if not user_text:
        return

    if user_text == "1":
        # Adaptive Card — sent as an attachment on an Activity
        attachment = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": ADAPTIVE_CARD,
        }
        reply = Activity(
            type="message",
            text="",
            attachments=[attachment],
        )
        await context.send_activity(reply)

    elif user_text == "2":
        attachment = _make_hero_card()
        reply = Activity(type="message", text="", attachments=[attachment])
        await context.send_activity(reply)

    elif user_text == "3":
        attachment = _make_thumbnail_card()
        reply = Activity(type="message", text="", attachments=[attachment])
        await context.send_activity(reply)

    elif user_text == "4":
        attachment = _make_receipt_card()
        reply = Activity(type="message", text="", attachments=[attachment])
        await context.send_activity(reply)

    elif user_text in ("help", "menu", "?"):
        await context.send_activity(INTRO_TEXT)

    else:
        await context.send_activity(
            f"Unknown command: **{user_text}**. Type **help** to see available cards."
        )


@app.activity("invoke")
async def on_invoke(context, state):
    """Handle Adaptive Card submit actions.

    When a user submits an Adaptive Card form, Teams sends an invoke
    activity with the form data in ``context.activity.value``.
    """
    from microsoft_agents.activity import Activity, ActivityTypes

    value = context.activity.value or {}
    action = value.get("action", "")

    if action == "adaptiveCardSubmit":
        user_input = value.get("userInput", "(empty)")
        color = value.get("colorChoice", "(none)")
        await context.send_activity(
            f"**Adaptive Card submitted!**\n\n"
            f"- Your message: {user_input}\n"
            f"- Color choice: {color}"
        )

    # Always send invoke response
    invoke_response = Activity(
        type=ActivityTypes.invoke_response,
        value={"status": 200, "body": {"message": "ok"}},
    )
    await context.send_activity(invoke_response)


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    app.run()
