# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_openai_assistants_file_search.py

DESCRIPTION:
    This sample demonstrates how to use file search tool with assistant using the AzureOpenAI client

USAGE:
    python sample_openai_assistants_file_search.py

    Before running the sample:

    pip install openai azure-identity

"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from azure.ai.projects.models import FileSearchTool


with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Explicit type hinting for IntelliSense
    client: AzureOpenAI = project_client.inference.get_azure_openai_client()

    openai_file = client.files.create(file=open("product_info_1.md", "rb"), purpose="assistants")
    print(f"Uploaded file, file ID: {openai_file.id}")

    # Create vector store with file, note: there is no poll method to check the status of vector store is ready
    openai_vectorstore = client.beta.vector_stores.create(file_ids=[openai_file.id], name="my_vectorstore")

    # poll the vector store status, the vector store status can be "in_progress", "completed", "expired"
    # status can be get from client.beta.vector_stores.retrieve(openai_vectorstore.id)
    while openai_vectorstore.status == "in_progress":
        time.sleep(1)
        openai_vectorstore = client.beta.vector_stores.retrieve(openai_vectorstore.id)

    print(f"Created vector store, vector store ID: {openai_vectorstore.id}")

    # Create file search tool with resources
    file_search = FileSearchTool(vector_store_ids=[openai_vectorstore.id])

    with client:
        agent = client.beta.assistants.create(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", tools=file_search.definitions, tool_resources=file_search.resources
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = client.beta.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content="Hello, what Contoso products do you know?")
        print(f"Created message, message ID: {message.id}")

        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=agent.id)

        # Poll the run while run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)  # Wait for a second
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Run status: {run.status}")

        if run.status == "failed":
            # Check if you got "Rate limit is exceeded.", then you want to get more quota
            print(f"Run failed: {run.last_error}")

        client.beta.vector_stores.delete(openai_vectorstore.id)
        print("Deleted vector store")

        client.beta.assistants.delete(agent.id)
        print("Deleted agent")

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(f"Messages: {messages}")
