# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use function tools with the Azure AI Projects client.
    It shows the complete workflow of defining a function tool, handling function calls
    from the model, executing the function, and providing results back to get a final response.

USAGE:
    python sample_agent_function_tool.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
import os
import json
from dotenv import load_dotenv
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool

load_dotenv()

agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


def get_horoscope(sign: str) -> str:
    """Generate a horoscope for the given astrological sign."""
    return f"{sign}: Next Tuesday you will befriend a baby otter."


endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


tool = FunctionTool(
    name="get_horoscope",
    parameters={
        "type": "object",
        "properties": {
            "sign": {
                "type": "string",
                "description": "An astrological sign like Taurus or Aquarius",
            },
        },
        "required": ["sign"],
        "additionalProperties": False,
    },
    description="Get today's horoscope for an astrological sign.",
    strict=True,
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_with_endpoint(
        project_client=project_client,
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="You are a helpful assistant that can use function tools.",
            tools=[tool],
        ),
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    # Prompt the model with tools defined
    response = openai_client.responses.create(
        input="What is my horoscope? I am an Aquarius.",
    )
    print(f"Response output: {response.output_text}")

    input_list: ResponseInputParam = []
    # Process function calls
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_horoscope":
                # Execute the function logic for get_horoscope
                horoscope = get_horoscope(**json.loads(item.arguments))

                # Provide function call results to the model
                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps({"horoscope": horoscope}),
                    )
                )

    print("Final input:")
    print(input_list)

    response = openai_client.responses.create(
        input=input_list,
        previous_response_id=response.id,
    )

    print(f"Agent response: {response.output_text}")
