# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_openai_assistants_basics.py

DESCRIPTION:
    This sample demonstrates how to create an assistant, thread, and message using the AzureOpenAI client.

USAGE:
    python sample_openai_assistants_basics.py

    Before running the sample:

    pip install openai azure-identity

"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI


with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Explicit type hinting for IntelliSense
    client: AzureOpenAI = project_client.inference.get_azure_openai_client()

    with client:
        agent = client.beta.assistants.create(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = client.beta.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        print(f"Created message, message ID: {message.id}")

        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=agent.id)

        # Poll the run while run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)  # Wait for a second
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Run status: {run.status}")

        client.beta.assistants.delete(agent.id)
        print("Deleted agent")

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(f"Messages: {messages}")
