"""Weather agent built with the Activity protocol.

Uses ``microsoft_agents.activity`` types (Activity, ChannelAccount, etc.)
for activity handling and the OpenAI Agents SDK for LLM orchestration.

This module has **no dependency** on ``azure-ai-agentserver-server`` — it
is a standalone agent that can be hosted by any server that speaks the
Activity protocol.  See ``server.py`` for the AgentServer hosting layer.

The agent mirrors the
`weather-agent-open-ai <https://github.com/microsoft/Agents-for-python/tree/main/test_samples/weather-agent-open-ai>`_
reference sample from Agents-for-python, using the same ``ActivityHandler``
dispatch pattern (``on_turn`` → ``on_message_activity`` /
``on_members_added_activity``).
"""

import logging
import os
import random
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from openai import AsyncAzureOpenAI
from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    function_tool,
)

from microsoft_agents.activity import Activity, ActivityTypes

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tools — registered with the OpenAI Agents SDK
# ---------------------------------------------------------------------------


@function_tool
def get_weather(city: str, date: str) -> dict:
    """Get the weather forecast for a city on a given date.

    :param city: City name (e.g. "Seattle").
    :param date: Date string (e.g. "2026-03-14").
    :return: Weather data with temperature and conditions.
    """
    logger.info("Tool get_weather called: city=%s, date=%s", city, date)
    temperature = random.randint(8, 21)
    conditions = random.choice(
        ["Sunny with light breeze", "Partly cloudy", "Overcast with rain"]
    )
    result = {
        "city": city,
        "temperature": f"{temperature}C",
        "conditions": conditions,
        "date": date,
    }
    logger.info("Tool get_weather result: %s", result)
    return result


@function_tool
def get_date() -> str:
    """Get the current date and time.

    :return: ISO-formatted current datetime string.
    """
    now = datetime.now().isoformat()
    logger.info("Tool get_date called: %s", now)
    return now


# ---------------------------------------------------------------------------
# WeatherAgent — Activity protocol agent
# ---------------------------------------------------------------------------


class WeatherAgent:
    """A weather-forecast agent that speaks the Activity protocol.

    Accepts an :class:`~microsoft_agents.activity.Activity`, dispatches by
    ``activity.type``, and returns a list of reply
    :class:`~microsoft_agents.activity.Activity` objects.

    :param client: An ``AsyncAzureOpenAI`` client for LLM calls.
    :type client: openai.AsyncAzureOpenAI
    """

    def __init__(self, client: AsyncAzureOpenAI) -> None:
        self._agent = Agent(
            name="WeatherAgent",
            instructions=(
                "You are a friendly assistant that helps people find weather "
                "forecasts.  Use the get_weather and get_date tools to look up "
                "the forecast.  Always respond with plain text.  If you need "
                "more information (city or date), ask the user a follow-up "
                "question."
            ),
            tools=[get_weather, get_date],
        )

        class _AzureModelProvider(ModelProvider):
            """Routes model requests to the Azure OpenAI client."""

            def get_model(self, model_name: Optional[str] = None) -> Model:
                return OpenAIChatCompletionsModel(
                    model=model_name
                    or os.environ.get("AZURE_OPENAI_MODEL", "gpt-4o"),
                    openai_client=client,
                )

        self._model_provider = _AzureModelProvider()
        logger.info("WeatherAgent initialised with tools: get_weather, get_date")

    # -- Dispatch ------------------------------------------------------------

    async def on_turn(self, activity: Activity) -> list[Activity]:
        """Process an incoming activity and return reply activities.

        Routes by ``activity.type`` to the appropriate handler, mirroring the
        ``ActivityHandler.on_turn()`` pattern from the Microsoft Agents SDK.

        :param activity: The incoming activity.
        :type activity: microsoft_agents.activity.Activity
        :return: Zero or more reply activities.
        :rtype: list[Activity]
        """
        sender = activity.from_property.name if activity.from_property else "unknown"
        conv_id = activity.conversation.id if activity.conversation else "unknown"
        logger.info(
            "on_turn: type=%s, from=%s, conversation=%s",
            activity.type, sender, conv_id,
        )

        if activity.type == ActivityTypes.message:
            return await self._on_message_activity(activity)
        if activity.type == ActivityTypes.conversation_update:
            return await self._on_conversation_update_activity(activity)

        logger.debug("on_turn: unhandled activity type %r, returning empty", activity.type)
        return []

    # -- Handlers ------------------------------------------------------------

    async def _on_message_activity(self, activity: Activity) -> list[Activity]:
        """Handle a ``message`` activity via the OpenAI Agents SDK.

        :param activity: The incoming message activity.
        :type activity: Activity
        :return: A single-element list with the reply activity.
        :rtype: list[Activity]
        """
        user_text = activity.text or ""
        logger.info("Message received: %r", user_text)

        logger.debug("Running OpenAI Agents SDK Runner.run() ...")
        response = await Runner.run(
            self._agent,
            user_text,
            run_config=RunConfig(
                model_provider=self._model_provider,
                tracing_disabled=True,
            ),
        )

        reply = activity.create_reply(text=response.final_output)
        logger.info("Reply: %r", reply.text)
        return [reply]

    async def _on_conversation_update_activity(
        self, activity: Activity
    ) -> list[Activity]:
        """Handle a ``conversationUpdate`` activity.

        Sends a welcome message when new members are added (excluding the
        agent itself).

        :param activity: The incoming conversationUpdate activity.
        :type activity: Activity
        :return: A list with one welcome reply, or empty.
        :rtype: list[Activity]
        """
        members_added = activity.members_added or []
        recipient_id = activity.recipient.id if activity.recipient else None
        logger.info(
            "conversationUpdate: %d member(s) added, recipient_id=%s",
            len(members_added), recipient_id,
        )

        for member in members_added:
            if member.id != recipient_id:
                logger.info(
                    "New member joined: id=%s, name=%s — sending welcome",
                    member.id, member.name,
                )
                reply = activity.create_reply(
                    text=(
                        "Hello and welcome! I can help you with weather "
                        "forecasts. Just tell me a city and date, and I'll "
                        "look up the forecast for you."
                    ),
                )
                return [reply]

        logger.debug("conversationUpdate: no new external members, no welcome sent")
        return []


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_weather_agent() -> WeatherAgent:
    """Create a :class:`WeatherAgent` from environment variables.

    Reads ``AZURE_OPENAI_ENDPOINT`` and ``AZURE_OPENAI_API_VERSION`` from
    the environment (or ``.env`` file via ``python-dotenv``).

    :return: A configured WeatherAgent instance.
    :rtype: WeatherAgent
    """
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    logger.info(
        "Creating WeatherAgent: endpoint=%s, api_version=%s",
        endpoint, api_version,
    )
    client = AsyncAzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
    )
    return WeatherAgent(client=client)
