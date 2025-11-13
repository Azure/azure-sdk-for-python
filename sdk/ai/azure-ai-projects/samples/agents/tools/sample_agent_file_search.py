# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using the File Search Tool and a synchronous client.

USAGE:
    python sample_agent_file_search.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv

# Azure AI imports
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

# [START tool_declaration]
# Create vector store for file search
vector_store = openai_client.vector_stores.create(name="ProductInfoStore")
print(f"Vector store created (id: {vector_store.id})")

# Load the file to be indexed for search
asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info.md"))

# Upload file to vector store
file = openai_client.vector_stores.files.upload_and_poll(
    vector_store_id=vector_store.id, file=open(asset_file_path, "rb")
)
print(f"File uploaded to vector store (id: {file.id})")

tool = FileSearchTool(vector_store_ids=[vector_store.id])
# [END tool_declaration]

with project_client:
    # Create agent with file search tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that can search through product information.",
            tools=[tool],
        ),
        description="File search agent for product information queries.",
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create a conversation for the agent interaction
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Send a query to search through the uploaded file
    response = openai_client.responses.create(
        conversation=conversation.id,
        input="Tell me about Contoso products",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
