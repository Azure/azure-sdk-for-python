# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using the Code Interpreter Tool and a synchronous client.

USAGE:
    python sample_agent_code_interpreter.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
AGENT_NAME = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    with (
        create_version_with_endpoint(
            project_client=project_client,
            agent_name=AGENT_NAME,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions="You are a helpful assistant.",
                tools=[CodeInterpreterTool()],
            ),
            description="Code interpreter agent for data analysis and visualization.",
        ),
        project_client.get_openai_client(agent_name=AGENT_NAME) as openai_client,
    ):
        agent = project_client.agents.get(agent_name=AGENT_NAME)
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.versions.latest.version})")

        # Create a conversation for the agent interaction
        conversation = openai_client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        # Send request for the agent to generate a multiplication chart.
        response = openai_client.responses.create(
            conversation=conversation.id,
            input="Could you please generate a multiplication chart showing the products for 1-10 multiplied by 1-10 (a 10x10 times table)?",
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
