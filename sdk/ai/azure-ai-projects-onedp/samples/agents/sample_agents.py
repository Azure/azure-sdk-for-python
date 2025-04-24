# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    TODO: Update me
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AgentsClient from the azure.ai.agents package. For more information on 
    the azure.ai.agents package see https://pypi.org/project/azure-ai-agents/.

USAGE:
    python sample_agents.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

# TODO: Remove console logging
import sys
import logging
azure_logger = logging.getLogger("azure")
azure_logger.setLevel(logging.DEBUG)
azure_logger.addHandler(logging.StreamHandler(stream=sys.stdout))
identity_logger = logging.getLogger("azure.identity")
identity_logger.setLevel(logging.ERROR)
# End logging

import os, time
from azure.identity import DefaultAzureCredential
from azure.ai.projects.onedp import AIProjectClient
from azure.ai.agents.models import ListSortOrder, MessageTextContent

endpoint = os.environ["PROJECT_ENDPOINT"]

with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
    logging_enable=True
) as project_client:

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent",
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID: {message.id}")

    run = project_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)

    # Poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {run.status}")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id, order=ListSortOrder.ASCENDING)

    # The messages are following in the reverse order,
    # we will iterate them and output only text contents.
    for data_point in messages.data:
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent):
            print(f"{data_point.role}: {last_message_content.text.value}")

