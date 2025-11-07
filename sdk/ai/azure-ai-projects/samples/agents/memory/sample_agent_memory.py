# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to integrate memory into a prompt agent.

USAGE:
    python sample_agent_memory.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Deploy a chat model (e.g. gpt-4.1) and an embedding model (e.g. text-embedding-3-small).
    Once you have deployed models, set the deployment name in the variables below.

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model for the agent, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model for memory, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    4) AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME - The deployment name of the embedding model for memory, as found under the
       "Name" column in the "Models + endpoints" tab in your Azure AI Foundry project.
"""

# import os
# from dotenv import load_dotenv
# from azure.identity import DefaultAzureCredential
# from azure.ai.projects import AIProjectClient
# from azure.ai.projects.models import (
#     MemoryStoreDefaultDefinition,
#     MemoryStoreDefaultOptions,
#     MemorySearchOptions,
#     ResponsesUserMessageItemParam,
#     MemorySearchTool,
#     PromptAgentDefinition,
# )

# load_dotenv()

# project_client = AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=DefaultAzureCredential())

# with project_client:

#     openai_client = project_client.get_openai_client()

#     # Create a memory store
#     definition = MemoryStoreDefaultDefinition(
#         chat_model=os.environ["AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME"],
#         embedding_model=os.environ["AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME"],
#     )
#     memory_store = project_client.memory_stores.create(
#         name="my_memory_store",
#         description="Example memory store for conversations",
#         definition=definition,
#     )
#     print(f"Created memory store: {memory_store.name} ({memory_store.id}): {memory_store.description}")

#     # Create a prompt agent with memory search tool
#     agent = project_client.agents.create_version(
#         agent_name="MyAgent",
#         definition=PromptAgentDefinition(
#             model=os.environ["AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"],
#             instructions="You are a helpful assistant that answers general questions",
#         ),
#         tools=[
#             MemorySearchTool(
#                 memory_store_name=memory_store.name,
#                 scope="{{$userId}}",
#                 update_delay=10,  # Wait 5 seconds of inactivity before updating memories
#                 # In a real application, set this to a higher value like 300 (5 minutes, default)
#             )
#         ],
#     )
#     print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

#     # Create a conversation with the agent with memory tool enabled
#     conversation = openai_client.conversations.create()
#     print(f"Created conversation (id: {conversation.id})")

#     # Create an agent response to initial user message
#     response = openai_client.responses.create(
#         conversation=conversation.id,
#         extra_body={"agent": AgentReference(name=agent.name).as_dict()},
#         input=[ResponsesUserMessageItemParam(content="I prefer dark roast coffee")],
#     )
#     print(f"Response output: {response.output_text}")

#     # After an inactivity in the conversation, memories will be extracted from the conversation and stored
#     sleep(60)

#     # Create a new conversation
#     new_conversation = openai_client.conversations.create()
#     print(f"Created new conversation (id: {new_conversation.id})")

#     # Create an agent response with stored memories
#     new_response = openai_client.responses.create(
#         conversation=new_conversation.id,
#         extra_body={"agent": AgentReference(name=agent.name).as_dict()},
#         input=[ResponsesUserMessageItemParam(content="Please order my usual coffee")],
#     )
#     print(f"Response output: {new_response.output_text}")

#     # Clean up
#     openai_client.conversations.delete(conversation.id)
#     openai_client.conversations.delete(new_conversation.id)
#     print("Conversations deleted")

#     project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
#     print("Agent deleted")

#     project_client.memory_stores.delete(memory_store.name)
#     print("Memory store deleted")
