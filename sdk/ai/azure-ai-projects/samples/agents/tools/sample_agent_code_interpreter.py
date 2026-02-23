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

    pip install "azure-ai-projects>=2.0.0b4" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # [START tool_declaration]
    tool = CodeInterpreterTool()
    # [END tool_declaration]

    # Create agent with code interpreter tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant.",
            tools=[tool],
        ),
        description="Code interpreter agent for data analysis and visualization.",
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create a conversation for the agent interaction
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Send request for the agent to generate a multiplication chart.
    response = openai_client.responses.create(
        conversation=conversation.id,
        input="Could you please generate a multiplication chart showing the products for 1-10 multiplied by 1-10 (a 10x10 times table)?",
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        tool_choice="required",
    )
    print(f"Response completed (id: {response.id})")

    # Print code executed by the code interpreter tool.
    # [START code_output_extraction]
    code = next((output.code for output in response.output if output.type == "code_interpreter_call"), "")
    print(f"Code Interpreter code:")
    print(code)
    # [END code_output_extraction]

    # Print final assistant text output.
    print(f"Agent response: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
