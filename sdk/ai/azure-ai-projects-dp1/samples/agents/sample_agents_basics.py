# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_basics.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) AGENT_ENDPOINT - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
"""

import os, time
from azure.ai.projects.dp1.models import AzureAgentModel, UserMessage, DeveloperMessage, TextContent, CreateRunRequest
from azure.ai.projects.dp1 import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["AGENT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    instruction = TextContent(text="You are helpful assistant")
    instructions = [DeveloperMessage(content=instruction)]

    agent = project_client.agents.create_agent(
        agent_model=AzureAgentModel,
        name="SampleAgent",
        instructions=instructions)

    thread = project_client.threads.create_thread()
    content = TextContent(text="Tell me a joke")
    chat_messages = [UserMessage(content=content)]
    run_request = CreateRunRequest(agent=agent, input=chat_messages, thread_id=thread.thread_id)
    run = project_client.runs.create_run(run_request=run_request)

    # Poll the run as long as run status is queued or in progress
    while run.status in ["incomplete", "inProgress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = project_client.runs.get_run(run_id=run.run_id)
        # [END create_run]
        print(f"Run status: {run.status}")

    outputs = run.output
    for chat_message in outputs:
        for ai_content in chat_message.content:
            if isinstance(ai_content, TextContent):
                print("AGENT: " + ai_content.text)

