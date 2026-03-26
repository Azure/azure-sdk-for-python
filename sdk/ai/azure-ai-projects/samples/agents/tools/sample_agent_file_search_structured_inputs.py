# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations using the File Search Tool.

    It is intentionally very similar to `sample_agent_file_search.py`, but shows
    how to use structured inputs to pass an uploaded file id at runtime.

    The key idea is that structured input acts as a placeholder and is later bound to actual data in the response call.

USAGE:
    python sample_agent_file_search_structured_inputs.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT (preferred) or AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.

NOTES:
    This sample is intentionally kept very close to `sample_agent_file_search.py`.
    It does not include fallback logic.
"""

import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, StructuredInputDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # Create vector store for file search
    vector_store = openai_client.vector_stores.create(name="ProductInfoStore")
    print(f"Vector store created (id: {vector_store.id})")

    # Load the file to be indexed for search
    asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info.md"))

    # Upload file to vector store
    with open(asset_file_path, "rb") as f:
        file = openai_client.vector_stores.files.upload_and_poll(vector_store_id=vector_store.id, file=f)
    print(f"File uploaded to vector store (id: {file.id})")

    # Tool resources are templated and resolved at runtime via structured inputs.
    tool = FileSearchTool(vector_store_ids=["{{vector_store_id}}"])

    agent_definition = PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_NAME"],
        instructions=(
            "You are a helpful assistant that can search through product information. "
            "The indexed source file id is {{vector_store_file_id}}."
        ),
        tools=[tool],
        structured_inputs={
            "vector_store_id": StructuredInputDefinition(
                description="Vector store id used by the file_search tool",
                required=True,
                schema={"type": "string"},
            ),
            "vector_store_file_id": StructuredInputDefinition(
                description="File id uploaded into the vector store",
                required=True,
                schema={"type": "string"},
            ),
        },
    )

    # Create agent with file search tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=agent_definition,
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
        extra_body={
            "agent_reference": {"name": agent.name, "type": "agent_reference"},
            "structured_inputs": {"vector_store_id": vector_store.id, "vector_store_file_id": file.id},
        },
    )
    print(f"Agent response: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
