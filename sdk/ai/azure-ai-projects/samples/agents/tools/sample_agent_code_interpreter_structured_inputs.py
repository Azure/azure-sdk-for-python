# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using the Code Interpreter Tool and a synchronous client.

    It is intentionally very similar to `sample_agent_code_interpreter.py`, but shows
    how to use structured inputs to pass an uploaded file id at runtime.

    The key idea is that structured input acts as a placeholder and is later bound to actual data in the response call.


USAGE:
    python sample_agent_code_interpreter_structured_inputs.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from io import BytesIO
from typing import Any, cast

from dotenv import load_dotenv

from azure.ai.projects.models._models import AutoCodeInterpreterToolParam
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool, StructuredInputDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Upload a tiny CSV so the code interpreter has a file to work with.
    csv_bytes = b"x\n1\n2\n3\n"
    csv_file = BytesIO(csv_bytes)
    csv_file.name = "numbers.csv"  # type: ignore[attr-defined]
    uploaded = openai_client.files.create(purpose="assistants", file=csv_file)
    print(f"File uploaded (id: {uploaded.id})")

    tool = CodeInterpreterTool(container=AutoCodeInterpreterToolParam(file_ids=["{{analysis_file_id}}"]))

    agent_definition = PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        instructions="You are a helpful assistant.",
        tools=[tool],
        structured_inputs={
            "analysis_file_id": StructuredInputDefinition(
                description="File id available to the code interpreter",
                required=True,
                schema={"type": "string"},
            ),
        },
    )

    # Create agent with code interpreter tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=agent_definition,
        description="Code interpreter agent for data analysis and visualization.",
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create a conversation for the agent interaction
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Send request for the agent to generate a multiplication chart.
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=(
            "Could you please generate a multiplication chart showing the products for 1-10 multiplied by 1-10 "
            "(a 10x10 times table)? Also, using the code interpreter, read numbers.csv and return the sum of x."
        ),
        extra_body={
            "agent_reference": {"name": agent.name, "type": "agent_reference"},
            "structured_inputs": {"analysis_file_id": uploaded.id},
        },
        tool_choice="required",
    )
    print(f"Response completed (id: {response.id})")

    # Print code executed by the code interpreter tool.
    code = next((output.code for output in response.output if output.type == "code_interpreter_call"), "")
    print("Code Interpreter code:")
    print(code)

    # Print final assistant text output.
    print(f"Agent response: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
