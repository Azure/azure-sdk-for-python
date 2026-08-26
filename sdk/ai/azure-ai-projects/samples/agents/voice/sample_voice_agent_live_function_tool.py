# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates handling a client-executed `function` tool during
    a live voice-agent session:

    1) Create a voice agent configured with a `get_weather` function tool.
    2) Open a realtime session and send a text turn that should trigger the tool.
    3) Listen for `response.function_call_arguments.done`, execute the function
       locally, and send the result back with `conversation.item.create` +
       `response.create` so the agent can finish its reply using the tool output.

USAGE:
    python sample_voice_agent_live_function_tool.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME - Optional. Name for the sample voice agent
       created and deleted by this script. Defaults to
       "sample-voice-agent-function-tool".
"""

import json
import os
from typing import Any, Final, cast

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeFunctionTool,
    RealtimeServerEventError,
    VoiceAgentDefinition,
    VoiceAgentServerEventResponseDone,
    VoiceAgentServerEventResponseFunctionCallArgumentsDone,
    VoiceAgentServerEventResponseTextDone,
    VoiceFunctionCallOutputItem,
    VoiceModelType,
    VoiceOutputModality,
    VoiceUserMessageItem,
)

load_dotenv()

# Seconds to wait for the agent to finish a response.
_RESPONSE_TIMEOUT: Final = 45


def get_weather(city: str) -> str:
    """A trivial local "tool" implementation the agent can call.

    :param city: The city to look up.
    :type city: str
    :return: A canned weather report for the city.
    :rtype: str
    """
    return json.dumps({"city": city, "condition": "sunny", "temperature_f": 72})


def _run_turn_with_tool_support(client: AIProjectClient, agent_name: str, prompt: str) -> None:
    """Send one turn and resolve any function-call the agent makes before printing its reply.

    :param client: The Foundry project client.
    :param agent_name: The voice agent name.
    :param prompt: The user's message for this turn.
    :type client: ~azure.ai.projects.AIProjectClient
    :type agent_name: str
    :type prompt: str
    """
    with client.realtime.connect(agent_name=agent_name) as conn:
        conn.conversation.item.create(item=VoiceUserMessageItem(content=[{"type": "input_text", "text": prompt}]))
        conn.response.create()

        for event in conn:
            if isinstance(event, VoiceAgentServerEventResponseFunctionCallArgumentsDone):
                # The service forwards the call to us; execute it locally and
                # send the result back so the agent can use it in its reply.
                args = json.loads(event.arguments)
                print(f"Tool call: {event.name}({args})")
                if event.name == "get_weather":
                    result = get_weather(**args)
                else:
                    result = json.dumps({"error": f"Unknown tool: {event.name}"})

                conn.conversation.item.create(item=VoiceFunctionCallOutputItem(call_id=event.call_id, output=result))
                conn.response.create()
            elif isinstance(event, VoiceAgentServerEventResponseTextDone):
                # The sample agent uses a text-only output modality, so the
                # reply arrives as output text rather than an audio transcript.
                print(f"Agent: {event.text}")
            elif isinstance(event, VoiceAgentServerEventResponseDone):
                # A response.done that isn't a function call is the final answer for this turn.
                # Output items surface as plain mappings (open union), so use dict-style access.
                if not any(
                    (item.get("type") if isinstance(item, dict) else getattr(item, "type", None)) == "function_call"
                    for item in (event.response.output or [])
                ):
                    return
            elif isinstance(event, RealtimeServerEventError):
                print(f"Session error: {event.error.message}")
                return


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-voice-agent-function-tool"

    get_weather_tool = RealtimeFunctionTool(
        type="function",
        name="get_weather",
        description="Get the current weather for a city.",
        parameters=cast(
            Any,
            {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name, e.g. Seattle."}},
                "required": ["city"],
            },
        ),
    )

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        try:
            project_client.agents.create_version(
                agent_name=agent_name,
                definition=VoiceAgentDefinition(
                    model_type=VoiceModelType.MANAGED,
                    model="gpt-realtime",
                    instructions=(
                        "You are a helpful voice assistant. Use the get_weather tool when the "
                        "caller asks about the weather, then answer using its result."
                    ),
                    output_modalities=[VoiceOutputModality.TEXT],
                    tools=[get_weather_tool],  # type: ignore[list-item]
                ),
            )
            print(f"Created voice agent: {agent_name}")

            _run_turn_with_tool_support(project_client, agent_name, "What's the weather like in Seattle right now?")
        finally:
            project_client.agents.delete(agent_name=agent_name)
            print(f"Deleted voice agent: {agent_name}")


if __name__ == "__main__":
    main()
