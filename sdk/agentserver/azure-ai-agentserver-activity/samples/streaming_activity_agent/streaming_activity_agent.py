# Copyright (c) Microsoft. All rights reserved.

"""Streaming Agent — Activity Protocol with Azure OpenAI.

Demonstrates the M365 SDK's streaming response support via
``context.streaming_response``. Streams Azure OpenAI completions
token-by-token to the user in Teams.

The agent uses ``streaming_response`` to send:
- Informative updates ("Thinking...")
- Streamed text chunks (real Azure OpenAI token-by-token output)
- AI label and feedback loop metadata
- Final stream end signal

Architecture::

    ActivityAgentServerHost (Foundry contract)
        └── M365 bridge (auto-init)
            └── TurnContext with streaming_response
                ├── set_generated_by_ai_label(True)
                ├── set_feedback_loop(True)
                ├── queue_informative_update("Thinking...")
                ├── queue_text_chunk(chunk) (per token from Azure OpenAI)
                └── end_stream() (signals completion)

Required environment variables:

    # M365 Agents SDK (auto-injected by Foundry)
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID

    # Azure OpenAI configuration
    AZURE_OPENAI_ENDPOINT       # e.g. https://myresource.openai.azure.com/
    AZURE_OPENAI_API_KEY        # API key for Azure OpenAI
    AZURE_OPENAI_API_VERSION    # e.g. 2025-01-01-preview
    AZURE_OPENAI_MODEL          # e.g. gpt-4o-mini

Usage::

    python streaming_activity_agent.py
"""

import logging
import sys
import traceback
from os import environ

from azure.ai.agentserver.activity import ActivityAgentServerHost

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = ActivityAgentServerHost()


# ── Azure OpenAI client ──────────────────────────────────────────
# Initialized lazily on first message to allow import-time decoration.

_client = None


def _get_openai_client():
    global _client
    if _client is None:
        from openai import AsyncAzureOpenAI

        _client = AsyncAzureOpenAI(
            api_version=environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
            azure_endpoint=environ["AZURE_OPENAI_ENDPOINT"],
            api_key=environ["AZURE_OPENAI_API_KEY"],
        )
    return _client


# ── Activity handlers ────────────────────────────────────────────


@app.activity("conversationUpdate")
async def on_members_added(context, state):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            await context.send_activity(
                "Welcome to the streaming sample! "
                "Type any question and I'll stream the response from Azure OpenAI."
            )


@app.activity("message")
async def on_message(context, state):
    """Stream Azure OpenAI response to the user.

    Uses ``context.streaming_response`` for progressive delivery:
    - ``set_generated_by_ai_label(True)`` — marks content as AI-generated
    - ``set_feedback_loop(True)`` — enables thumbs up/down in Teams
    - ``queue_informative_update(...)`` — shows status text in Teams
    - ``queue_text_chunk(...)`` — sends a streamed token
    - ``end_stream()`` — signals completion to the channel

    Based on: microsoft/Agents azureai-streaming/src/agent.py
    """
    user_text = context.activity.text or ""
    if not user_text.strip():
        return

    logger.info("Streaming message: %s", user_text[:100])

    # Configure streaming metadata
    context.streaming_response.set_generated_by_ai_label(True)
    context.streaming_response.set_feedback_loop(True)

    # Show informative update while waiting for first token
    context.streaming_response.queue_informative_update("Thinking...")

    client = _get_openai_client()
    model = environ.get("AZURE_OPENAI_MODEL", "gpt-4o-mini")

    try:
        streamed_response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Keep responses concise "
                        "and well-formatted using Markdown."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
            stream=True,
        )

        async for chunk in streamed_response:
            if chunk.choices and chunk.choices[0].delta.content:
                context.streaming_response.queue_text_chunk(
                    chunk.choices[0].delta.content
                )
    except Exception as e:
        logger.error("Error during streaming: %s", e)
        context.streaming_response.queue_text_chunk(
            "An error occurred while generating the response. Please try again."
        )
    finally:
        await context.streaming_response.end_stream()


@app.activity("invoke")
async def on_invoke(context, state):
    """Handle invoke activities."""
    from microsoft_agents.activity import Activity, ActivityTypes

    await context.send_activity(
        Activity(type=ActivityTypes.invoke_response, value={"status": 200})
    )


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    app.run()
