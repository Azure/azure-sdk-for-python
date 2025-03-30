# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_execute_run.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) AGENT_ENDPOINT - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
"""

import os
from azure.ai.projects.dp1.models import AzureAgentModel, UserMessage, DeveloperMessage, TextContent, ChatMessage
from azure.ai.projects.dp1 import AIProjectClient
from azure.identity import DefaultAzureCredential
from typing import List

project_client = AIProjectClient(
    endpoint=os.environ["AGENT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    text_content = TextContent(text="You are helpful assistant")
    developer_message = DeveloperMessage(content=[text_content])
    instructions: List[ChatMessage] = [developer_message]

    agent = project_client.agents.create_agent(
        agent_model=AzureAgentModel(id="gpt-4o"), name="SampleAgent", instructions=instructions
    )

    content = TextContent(text="Tell me a joke")
    chat_message = ChatMessage(content=[content])
    run = project_client.runs.create_and_execute_run(agent=agent, input=[chat_message])

    messages = run.run_outputs.messages
    for chat_message in messages:
        for content in chat_message.content:
            if isinstance(content, TextContent):
                print("AGENT: " + content.text)
