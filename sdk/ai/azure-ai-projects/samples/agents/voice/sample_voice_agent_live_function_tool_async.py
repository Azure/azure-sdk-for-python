# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Let GPT-Live (preview) call a local weather function, return its result, and print
    the final reply. Weather is fixed sample data, not a live forecast.
    The sample deletes its temporary agent version when finished.

USAGE:
    python sample_voice_agent_live_function_tool_async.py

    pip install "azure-ai-projects[voice]>=2.11.0" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT-Live deployment name.
    3) FOUNDRY_MODEL_NAME (required) - A tool-capable Responses deployment available to Live.
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for the temporary agent name.

    Uses DefaultAzureCredential. No audio devices are needed.
    Printed text does not mean voice playback has finished.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Mapping

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects import models

from live_sample_utils import (
    audio_settings,
    close_session_async,
    receive_response_async,
    remaining_time,
    safe_print,
    sample_agent_name,
    wait_for_event_async,
)


def get_weather(city: str) -> str:
    """Return deterministic sample weather, rather than calling an external service."""
    if city.strip().casefold() != "seattle":
        raise ValueError("This sample only provides weather data for Seattle.")
    return json.dumps({"city": "Seattle", "condition": "sunny", "temperature_f": 72})


def _execute_tool(call: Mapping[str, Any]) -> str:
    if call.get("name") != "get_weather":
        raise RuntimeError(f"Unexpected backend function: {call.get('name')}")
    arguments = json.loads(call["arguments"])
    if not isinstance(arguments, dict) or set(arguments) != {"city"} or not isinstance(arguments["city"], str):
        raise ValueError("get_weather requires exactly one string argument named city.")
    return get_weather(arguments["city"])


async def _run_tool_turn(project_client: AIProjectClient, agent_name: str, agent_version: str) -> str:
    async with project_client.beta.voice_agents.live.connect(
        agent_name=agent_name, agent_version=agent_version, store=False
    ) as connection:
        try:
            await wait_for_event_async(connection, "session.started")
            await connection.response.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Use get_weather for Seattle, then report the sample result."}
                    ],
                }
            )
            await connection.response.create()
            deadline = time.monotonic() + 120
            handled_calls: set[str] = set()
            for _ in range(6):
                text, calls = await receive_response_async(
                    connection, timeout=remaining_time(deadline, "the tool-backed answer")
                )
                if not calls:
                    if not handled_calls:
                        raise RuntimeError("The backend answered without calling get_weather.")
                    if not text:
                        raise RuntimeError("The backend completed without returning an answer.")
                    return text
                # Complete the backend cycle before submitting results or starting another response.
                for call in calls:
                    call_id = call["call_id"]
                    if not call_id or call_id in handled_calls:
                        raise RuntimeError("The backend returned a missing or repeated function call ID.")
                    result = _execute_tool(call)
                    await connection.response.item.create(
                        item={"type": "function_call_output", "call_id": call_id, "output": result}
                    )
                    handled_calls.add(call_id)
                    print("get_weather returned sample data: Seattle, sunny, 72 F.")
                await connection.response.create()
            raise RuntimeError("The backend exceeded this sample's six-response tool-call limit.")
        finally:
            await close_session_async(connection)


async def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    backend_model = os.environ["FOUNDRY_MODEL_NAME"]
    agent_name = sample_agent_name("function-tool")

    weather_tool = models.LiveFunctionToolInputParam(
        name="get_weather",
        description="Return sample weather for Seattle, not a live forecast.",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string", "enum": ["Seattle"]}},
            "required": ["city"],
            "additionalProperties": False,
        },
        strict=True,
    )
    definition = models.VoiceAgentLiveDefinition(
        model=model,
        model_type=models.VoiceModelType.SELF_DEPLOYED,
        instructions="Delegate weather questions to the Responses backend.",
        audio=audio_settings(),
        delegation=models.VoiceAgentLiveResponsesDelegation(
            responses=models.LiveResponsesDelegationSettingsInputParam(
                model=backend_model,
                instructions=(
                    "Call get_weather for Seattle, then answer once using its result. "
                    "Do not call it again. Label the result as sample weather."
                ),
                tools=[weather_tool],
                parallel_tool_calls=False,
            )
        ),
        store=False,
    )
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        agent = await project_client.agents.create_version(agent_name=agent_name, definition=definition)
        try:
            answer = await _run_tool_turn(project_client, agent_name, agent.version)
            safe_print(f"Responses backend: {answer}")
        finally:
            await project_client.agents.delete_version(agent_name=agent_name, agent_version=agent.version)
            print(f"Deleted sample agent version: {agent.version}")


if __name__ == "__main__":
    asyncio.run(main())
