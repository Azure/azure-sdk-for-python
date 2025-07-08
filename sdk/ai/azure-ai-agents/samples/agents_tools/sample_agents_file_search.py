# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with file searching from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_file_search.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    FilePurpose,
    FileSearchTool,
    ListSortOrder,
    RunAdditionalFieldList,
    RunStepFileSearchToolCall,
    RunStepToolCallDetails,
)
from azure.identity import DefaultAzureCredential

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info_1.md"))

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

    # Upload file and create vector store
    # [START upload_file_create_vector_store_and_agent_with_file_search_tool]
    file = agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")

    vector_store = agents_client.vector_stores.create_and_poll(file_ids=[file.id], name="my_vectorstore")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Create file search tool with resources followed by creating agent
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="Hello, you are helpful agent and can search information from uploaded files",
        tools=file_search.definitions,
        tool_resources=file_search.resources,
    )
    # [END upload_file_create_vector_store_and_agent_with_file_search_tool]

    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id, role="user", content="Hello, what Contoso products do you know?"
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    # [START teardown]
    # Delete the file when done
    agents_client.vector_stores.delete(vector_store.id)
    print("Deleted vector store")

    agents_client.files.delete(file_id=file.id)
    print("Deleted file")

    # Delete the agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")
    # [END teardown]

    for run_step in agents_client.run_steps.list(
        thread_id=thread.id, run_id=run.id, include=[RunAdditionalFieldList.FILE_SEARCH_CONTENTS]
    ):
        if isinstance(run_step.step_details, RunStepToolCallDetails):
            for tool_call in run_step.step_details.tool_calls:
                if (
                    isinstance(tool_call, RunStepFileSearchToolCall)
                    and tool_call.file_search
                    and tool_call.file_search.results
                    and tool_call.file_search.results[0].content
                    and tool_call.file_search.results[0].content[0].text
                ):
                    print(
                        "The search tool has found the next relevant content in "
                        f"the file {tool_call.file_search.results[0].file_name}:"
                    )
                    # Note: technically we may have several search results, however in our example
                    # we only have one file, so we are taking the only result.
                    print(tool_call.file_search.results[0].content[0].text)
                    print("===============================================================")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

    # Print last messages from the thread
    file_name = os.path.split(asset_file_path)[-1]
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1].text.value
            for annotation in msg.text_messages[-1].text.annotations:
                citation = (
                    file_name if annotation.file_citation.file_id == file.id else annotation.file_citation.file_id
                )
                last_text = last_text.replace(annotation.text, f" [{citation}]")
            print(f"{msg.role}: {last_text}")
