# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Let a GPT Live session call a local get_weather function through a Responses
    backend model. Return the function result and print the model's final reply.
    The weather is fixed sample data for Seattle (72 F), not a live forecast.
    The sample deletes its temporary agent version when finished.

USAGE:
    python sample_voice_agent_live_function_tool.py

    pip install "azure-ai-projects[voice]" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_MODEL (required) - Your GPT Live deployment name.
    3) FOUNDRY_MODEL_NAME (required) - A tool-capable Responses model deployment
       available to your Live resource.
    4) FOUNDRY_VOICE_AGENT_NAME (optional) - Prefix for the temporary agent name.

    Uses DefaultAzureCredential. No audio devices are needed.
    Tool results use call_id from response.output_item.done, not the item_id
    in response.function_call_arguments.done.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Mapping

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient, models

from live_sample_utils import (
    audio_settings,
    close_session,
    receive_response,
    remaining_time,
    safe_print,
    sample_agent_name,
    wait_for_event,
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


def _run_tool_turn(project_client: AIProjectClient, agent_name: str, agent_version: str) -> str:
    with project_client.beta.voice_agents.live.connect(
        agent_name=agent_name, agent_version=agent_version, store=False
    ) as connection:
        try:
            wait_for_event(connection, "session.started")
            connection.response.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Use get_weather for Seattle, then report the sample result."}
                    ],
                }
            )
            connection.response.create()
            deadline = time.monotonic() + 120
            handled_calls: set[str] = set()
            for _ in range(6):
                text, calls = receive_response(connection, timeout=remaining_time(deadline, "the tool-backed answer"))
                if not calls:
                    if not handled_calls:
                        raise RuntimeError("The backend answered without calling get_weather.")
                    if "72" not in text or "seattle" not in text.casefold():
                        raise RuntimeError("The backend answer did not include Seattle and the tool's 72 F result.")
                    return text
                # Wait for this cycle's response.completed before continuing, avoiding concurrent responses.
                for call in calls:
                    call_id = call["call_id"]
                    if not call_id or call_id in handled_calls:
                        raise RuntimeError("The backend returned a missing or repeated function call ID.")
                    result = _execute_tool(call)
                    connection.response.item.create(
                        item={"type": "function_call_output", "call_id": call_id, "output": result}
                    )
                    handled_calls.add(call_id)
                    print("get_weather returned sample data: Seattle, sunny, 72 F.")
                connection.response.create()
            raise RuntimeError("The backend exceeded this sample's six-response tool-call limit.")
        finally:
            close_session(connection)


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_VOICE_AGENT_MODEL"]
    backend_model = os.environ["FOUNDRY_MODEL_NAME"]
    agent_name = sample_agent_name("function-tool")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        created_version = None
        try:
            created_version = project_client.agents.create_version(
                agent_name=agent_name,
                definition=models.VoiceAgentLiveDefinition(
                    model=model,
                    instructions="Delegate weather questions to the Responses backend.",
                    audio=audio_settings(),
                    delegation=models.LiveResponsesDelegationParam(
                        responses=models.LiveResponsesDelegationSettingsInputParam(
                            model=backend_model,
                            instructions=(
                                "Call get_weather for Seattle. After its result, answer once without calling it again. "
                                "Explicitly include Seattle and the numeric temperature in F. Label it sample weather."
                            ),
                            tools=[
                                models.LiveFunctionToolInputParam(
                                    name="get_weather",
                                    description="Return deterministic sample weather for Seattle, not a live observation.",
                                    parameters={
                                        "type": "object",
                                        "properties": {"city": {"type": "string", "enum": ["Seattle"]}},
                                        "required": ["city"],
                                        "additionalProperties": False,
                                    },
                                    strict=True,
                                )
                            ],
                            parallel_tool_calls=False,
                        )
                    ),
                    store=False,
                ),
            )
            answer = _run_tool_turn(project_client, agent_name, created_version.version)
            safe_print(f"Responses backend: {answer}")
        finally:
            if created_version is not None:
                project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
                print(f"Deleted sample agent version: {created_version.version}")


if __name__ == "__main__":
    main()
