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

    pip install "azure-ai-projects[realtime]>=2.0.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_MODEL - Optional. The realtime model deployment name.
       Defaults to "gpt-realtime".
    3) FOUNDRY_VOICE_AGENT_NAME - Optional. Name for the sample voice agent
       created and deleted by this script. Defaults to
       "sample-voice-agent-function-tool".
"""

import json
import os
import sys
from typing import Any, Final, cast

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeConversationItemFunctionCall,
    RealtimeConversationItemFunctionCallOutput,
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventError,
    VoiceAgentDefinition,
    VoiceAgentFunctionTool,
    RealtimeServerEventResponseDone,
    RealtimeServerEventResponseFunctionCallArgumentsDone,
    RealtimeServerEventResponseTextDone,
    VoiceModelType,
    VoiceOutputModality,
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


def _safe_print(text: str) -> None:
    """Print text that may contain characters the current console can't display.

    The agent's reply below is model-generated and can contain characters (curly
    quotes, em-dashes, etc.) outside some legacy, non-Unicode console encodings
    (for example when stdout is piped/redirected on Windows). Rather than crashing
    with UnicodeEncodeError, fall back to replacing just the unsupported characters;
    a real interactive UTF-8 console prints unaffected.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding))


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
        conn.conversation.item.create(
            item=RealtimeConversationItemMessageUser(
                type=RealtimeConversationItemType.MESSAGE,
                content=[RealtimeConversationItemMessageUserContent(type="input_text", text=prompt)],
            )
        )
        conn.response.create()

        while True:
            try:
                event = conn.recv(timeout=_RESPONSE_TIMEOUT)
            except TimeoutError:
                print("Timed out waiting for the agent's reply.")
                conn.response.cancel()
                return
            if isinstance(event, RealtimeServerEventResponseFunctionCallArgumentsDone):
                # The service forwards the call to us; execute it locally and
                # send the result back so the agent can use it in its reply.
                args = json.loads(event.arguments)
                print(f"Tool call: {event.name}({args})")
                if event.name == "get_weather":
                    result = get_weather(**args)
                else:
                    result = json.dumps({"error": f"Unknown tool: {event.name}"})

                conn.conversation.item.create(
                    item=RealtimeConversationItemFunctionCallOutput(call_id=event.call_id, output=result)
                )
                conn.response.create()
            elif isinstance(event, RealtimeServerEventResponseTextDone):
                # The sample agent uses a text-only output modality, so the
                # reply arrives as output text rather than an audio transcript.
                _safe_print(f"Agent: {event.text}")
            elif isinstance(event, RealtimeServerEventResponseDone):
                # A response.done that isn't a function call is the final answer for this turn.
                if not any(
                    isinstance(item, RealtimeConversationItemFunctionCall) for item in (event.response.output or [])
                ):
                    return
            elif isinstance(event, RealtimeServerEventError):
                print(f"Session error: {event.error.message}")
                return


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME") or "sample-voice-agent-function-tool"

    get_weather_tool = VoiceAgentFunctionTool(
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
                    model=model,
                    instructions=(
                        "You are a helpful voice assistant. Use the get_weather tool when the "
                        "caller asks about the weather, then answer using its result."
                    ),
                    output_modalities=[VoiceOutputModality.TEXT],
                    tools=[get_weather_tool],
                ),
            )
            print(f"Created voice agent: {agent_name}")

            _run_turn_with_tool_support(project_client, agent_name, "What's the weather like in Seattle right now?")
        finally:
            project_client.agents.delete(agent_name=agent_name)
            print(f"Deleted voice agent: {agent_name}")


if __name__ == "__main__":
    main()
