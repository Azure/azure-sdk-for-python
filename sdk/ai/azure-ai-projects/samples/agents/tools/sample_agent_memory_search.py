# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to integrate memory into a prompt agent,
    by using the Memory Search Tool to retrieve relevant past user messages.
    This sample uses the synchronous AIProjectClient and OpenAI clients.

    For memory management, see also samples in the folder "samples/memories"
    folder.

USAGE:
    python sample_agent_memory_search.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Deploy a chat model (e.g. gpt-4.1) and an embedding model (e.g. text-embedding-3-small).
    Once you have deployed models, set the deployment name in the variables below.

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the Agent's AI model,
       as found under the "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
    3) MEMORY_STORE_CHAT_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model for memory,
       as found under the "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
    4) MEMORY_STORE_EMBEDDING_MODEL_DEPLOYMENT_NAME - The deployment name of the embedding model for memory,
       as found under the "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MemoryStoreDefaultDefinition,
    MemorySearchTool,
    PromptAgentDefinition,
    MemoryStoreDefaultOptions,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Delete memory store, if it already exists
    memory_store_name = "my_memory_store"
    try:
        project_client.memory_stores.delete(memory_store_name)
        print(f"Memory store `{memory_store_name}` deleted")
    except ResourceNotFoundError:
        pass

    # Create a memory store
    definition = MemoryStoreDefaultDefinition(
        chat_model=os.environ["MEMORY_STORE_CHAT_MODEL_DEPLOYMENT_NAME"],
        embedding_model=os.environ["MEMORY_STORE_EMBEDDING_MODEL_DEPLOYMENT_NAME"],
        options=MemoryStoreDefaultOptions(
            user_profile_enabled=True, chat_summary_enabled=True
        ),  # Note: This line will not be needed once the service is fixed to use correct defaults
    )
    memory_store = project_client.memory_stores.create(
        name=memory_store_name,
        description="Example memory store for conversations",
        definition=definition,
    )
    print(f"Created memory store: {memory_store.name} ({memory_store.id}): {memory_store.description}")

    # [START memory_search_tool_declaration]
    # Set scope to associate the memories with
    # You can also use "{{$userId}}" to take the oid of the request authentication header
    scope = "user_123"

    tool = MemorySearchTool(
        memory_store_name=memory_store.name,
        scope=scope,
        update_delay=1,  # Wait 1 second of inactivity before updating memories
        # In a real application, set this to a higher value like 300 (5 minutes, default)
    )
    # [END memory_search_tool_declaration]

    # Create a prompt agent with memory search tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
            tools=[tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create a conversation with the agent with memory tool enabled
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Create an agent response to initial user message
    response = openai_client.responses.create(
        input="I prefer dark roast coffee",
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response output: {response.output_text}")

    # After an inactivity in the conversation, memories will be extracted from the conversation and stored
    print("Waiting for memories to be stored...")
    time.sleep(60)

    # Create a new conversation
    new_conversation = openai_client.conversations.create()
    print(f"Created new conversation (id: {new_conversation.id})")

    # Create an agent response with stored memories
    new_response = openai_client.responses.create(
        input="Please order my usual coffee",
        conversation=new_conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response output: {new_response.output_text}")

    # Clean up
    openai_client.conversations.delete(conversation.id)
    openai_client.conversations.delete(new_conversation.id)
    print("Conversations deleted")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")

    project_client.memory_stores.delete(memory_store.name)
    print("Memory store deleted")
