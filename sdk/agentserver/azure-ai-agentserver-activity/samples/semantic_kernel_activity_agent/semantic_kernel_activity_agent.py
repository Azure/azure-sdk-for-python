# Copyright (c) Microsoft. All rights reserved.

"""Semantic Kernel Agent — Activity Protocol with multi-turn tool use.

Demonstrates a multi-turn weather agent built with Semantic Kernel,
streaming responses token-by-token to Teams.

Features:
- Semantic Kernel ChatCompletionAgent with function calling
- Custom weather and datetime plugins
- Multi-turn conversation with session state
- Streaming response via ``context.streaming_response``

Architecture::

    ActivityAgentServerHost (Foundry contract)
        └── M365 bridge (auto-init)
            └── TurnContext with streaming_response
                └── Semantic Kernel agent.invoke() → streamed tokens

Required environment variables:

    # M365 Agents SDK (auto-injected by Foundry)
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT    # e.g. https://myresource.openai.azure.com/
    AZURE_OPENAI_API_KEY     # API key
    AZURE_OPENAI_MODEL       # e.g. gpt-4o

Usage::

    python semantic_kernel_activity_agent.py
"""

import logging
import sys
import traceback
from datetime import datetime, timezone
from os import environ
from typing import Annotated

from azure.ai.agentserver.activity import ActivityAgentServerHost

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = ActivityAgentServerHost()


# ── Semantic Kernel plugins ──────────────────────────────────────
# These are simple example plugins. In production, you'd call real APIs.

try:
    from semantic_kernel.functions import kernel_function
except ImportError:
    raise ImportError(
        "This sample requires semantic-kernel. "
        "Install: pip install semantic-kernel"
    )


class DateTimePlugin:
    """Plugin providing current date and time."""

    @kernel_function(name="get_date", description="Get the current date and time.")
    def get_date(self) -> Annotated[str, "The current date and time in ISO format."]:
        return datetime.now(timezone.utc).isoformat()


class WeatherPlugin:
    """Plugin providing simulated weather data."""

    @kernel_function(
        name="get_current_weather",
        description="Get the current weather for a given location.",
    )
    def get_current_weather(
        self,
        location: Annotated[str, "The city name, e.g. 'Seattle'"],
    ) -> Annotated[str, "Current weather information as a JSON string."]:
        import json

        # Simulated weather data — replace with real API in production
        data = {
            "location": location,
            "temperature": "72°F / 22°C",
            "high": "78°F / 26°C",
            "low": "65°F / 18°C",
            "humidity": "55%",
            "wind": "10 mph NW",
            "description": "Partly cloudy",
        }
        return json.dumps(data)

    @kernel_function(
        name="get_weather_forecast",
        description="Get a 5-day weather forecast for a given location.",
    )
    def get_weather_forecast(
        self,
        location: Annotated[str, "The city name, e.g. 'Seattle'"],
    ) -> Annotated[str, "5-day weather forecast as a JSON string."]:
        import json

        # Simulated forecast — replace with real API in production
        forecast = [
            {"day": "Monday", "high": "78°F", "low": "65°F", "description": "Partly cloudy"},
            {"day": "Tuesday", "high": "80°F", "low": "67°F", "description": "Sunny"},
            {"day": "Wednesday", "high": "75°F", "low": "62°F", "description": "Light rain"},
            {"day": "Thursday", "high": "72°F", "low": "60°F", "description": "Cloudy"},
            {"day": "Friday", "high": "76°F", "low": "63°F", "description": "Sunny"},
        ]
        return json.dumps({"location": location, "forecast": forecast})


# ── Semantic Kernel agent (lazy init) ────────────────────────────

_sk_agent = None
_sessions: dict[str, dict] = {}  # conversation_id → {"history": [...], "last_access": float}
_MAX_SESSIONS = 100  # Evict oldest sessions when this limit is reached


def _get_or_create_session(conversation_id: str) -> list:
    """Get or create a session, with TTL-based eviction to prevent memory leaks."""
    import time

    now = time.time()

    # Evict stale sessions (older than 1 hour) or when over limit
    if len(_sessions) > _MAX_SESSIONS:
        stale = [k for k, v in _sessions.items() if now - v["last_access"] > 3600]
        for k in stale:
            del _sessions[k]
        # If still over limit, remove oldest
        if len(_sessions) > _MAX_SESSIONS:
            oldest = min(_sessions, key=lambda k: _sessions[k]["last_access"])
            del _sessions[oldest]

    if conversation_id not in _sessions:
        _sessions[conversation_id] = {"history": [], "last_access": now}
    else:
        _sessions[conversation_id]["last_access"] = now

    return _sessions[conversation_id]["history"]


def _get_sk_agent():
    """Lazily initialize the Semantic Kernel agent."""
    global _sk_agent
    if _sk_agent is not None:
        return _sk_agent

    from semantic_kernel import Kernel
    from semantic_kernel.agents import ChatCompletionAgent
    from semantic_kernel.connectors.ai.open_ai import (
        AzureChatCompletion,
        OpenAIPromptExecutionSettings,
    )
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

    kernel = Kernel()
    kernel.add_plugin(plugin=DateTimePlugin(), plugin_name="datetime")
    kernel.add_plugin(plugin=WeatherPlugin(), plugin_name="weather")

    service = AzureChatCompletion(
        deployment_name=environ.get("AZURE_OPENAI_MODEL", "gpt-4o"),
        endpoint=environ["AZURE_OPENAI_ENDPOINT"],
        api_key=environ["AZURE_OPENAI_API_KEY"],
    )

    execution_settings = OpenAIPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    execution_settings.temperature = 0

    _sk_agent = ChatCompletionAgent(
        service=service,
        name="WeatherAgent",
        instructions=(
            "You are a friendly weather assistant. "
            "Help users find the current weather or a weather forecast for any city. "
            "Use the weather plugin tools to get data. "
            "Use the datetime plugin to get the current date. "
            "Format responses nicely in Markdown. Use emojis where appropriate!"
        ),
        kernel=kernel,
    )
    return _sk_agent


# ── Activity handlers ────────────────────────────────────────────


@app.activity("conversationUpdate")
async def on_members_added(context, state):
    """Welcome new members."""
    for member in context.activity.members_added or []:
        if member.id != context.activity.recipient.id:
            await context.send_activity(
                "Hello! I'm your weather assistant. 🌤️\n\n"
                "Ask me about the weather in any city! For example:\n"
                "- *What's the weather in Seattle?*\n"
                "- *Give me a forecast for Tokyo*\n"
                "- *What's the temperature in London?*"
            )


@app.activity("message")
async def on_message(context, state):
    """Process user message through Semantic Kernel agent with streaming."""
    from semantic_kernel.agents import ChatHistoryAgentThread
    from semantic_kernel.contents import ChatHistory

    user_text = (context.activity.text or "").strip()
    if not user_text:
        return

    logger.info("SK message: %s", user_text[:100])

    # Configure streaming metadata
    context.streaming_response.set_generated_by_ai_label(True)
    context.streaming_response.set_feedback_loop(True)
    context.streaming_response.queue_informative_update("Checking the weather...")

    agent = _get_sk_agent()

    # Multi-turn: maintain chat history per conversation
    conversation_id = context.activity.conversation.id if context.activity.conversation else "default"
    session_history = _get_or_create_session(conversation_id)

    history = ChatHistory()
    for msg in session_history:
        if msg["role"] == "user":
            history.add_user_message(msg["content"])
        else:
            history.add_assistant_message(msg["content"])
    history.add_user_message(user_text)

    try:
        thread = ChatHistoryAgentThread()
        response_text = ""

        async for chat in agent.invoke(history, thread=thread):
            content = chat.content.content if hasattr(chat, "content") and hasattr(chat.content, "content") else str(chat)
            if content:
                context.streaming_response.queue_text_chunk(content)
                response_text += content

        # Save to history (keep last 20 turns to avoid unbounded growth)
        session_history.append({"role": "user", "content": user_text})
        session_history.append({"role": "assistant", "content": response_text})
        if len(session_history) > 40:
            del session_history[:-20]

    except Exception as e:
        logger.error("SK agent error: %s", e)
        context.streaming_response.queue_text_chunk(
            "Sorry, I encountered an error while checking the weather. Please try again."
        )
    finally:
        await context.streaming_response.end_stream()


@app.error
async def on_error(context, error):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    app.run()
