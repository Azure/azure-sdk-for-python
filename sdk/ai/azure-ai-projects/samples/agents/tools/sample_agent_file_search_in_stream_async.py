# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use the File Search Tool with streaming responses using the async client.
    It combines file search capabilities with response streaming to provide real-time
    search results from uploaded documents.

USAGE:
    python sample_agent_file_search_in_stream_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool

load_dotenv()

# Load the file to be indexed for search
asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info.md"))


async def main() -> None:

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        await project_client.get_openai_client() as openai_client,
    ):

        print("Setting up file search with streaming responses...")

        # Create vector store for file search
        vector_store = await openai_client.vector_stores.create(name="ProductInfoStreamStore")
        print(f"Vector store created (id: {vector_store.id})")

        # Upload file to vector store
        try:
            file = await openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id, file=open(asset_file_path, "rb")
            )
            print(f"File uploaded to vector store (id: {file.id})")
        except FileNotFoundError:
            print(f"Warning: Asset file not found at {asset_file_path}")
            print("Creating vector store without file for demonstration...")

        # Create agent with file search tool
        agent = await project_client.agents.create_version(
            agent_name="StreamingFileSearchAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="You are a helpful assistant that can search through product information and provide detailed responses. Use the file search tool to find relevant information before answering.",
                tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
            ),
            description="File search agent with streaming response capabilities.",
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        # Create a conversation for the agent interaction
        conversation = await openai_client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        print("\n" + "=" * 60)
        print("Starting file search with streaming response...")
        print("=" * 60)

        # Create a streaming response with file search capabilities
        stream_response = await openai_client.responses.create(
            stream=True,
            conversation=conversation.id,
            input=[
                {
                    "role": "user",
                    "content": "Tell me about Contoso products and their features in detail. Please search through the available documentation.",
                },
            ],
            tool_choice="required",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        print("Processing streaming file search results...\n")

        # Process streaming events as they arrive
        async for event in stream_response:
            if event.type == "response.created":
                print(f"Stream response created with ID: {event.response.id}")
            elif event.type == "response.output_text.delta":
                print(f"Delta: {event.delta}")
            elif event.type == "response.text.done":
                print(f"\nResponse done with full message: {event.text}")
            elif event.type == "response.completed":
                print(f"\nResponse completed!")
                print(f"Full response: {event.response.output_text}")

        print("\n" + "=" * 60)
        print("Demonstrating follow-up query with streaming...")
        print("=" * 60)

        # Demonstrate a follow-up query in the same conversation
        stream_response = await openai_client.responses.create(
            stream=True,
            conversation=conversation.id,
            input=[
                {
                    "role": "user",
                    "content": "Tell me about Smart Eyewear and its features.",
                },
            ],
            tool_choice="required",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        print("Processing follow-up streaming response...\n")

        # Process streaming events for the follow-up
        async for event in stream_response:
            if event.type == "response.created":
                print(f"Follow-up response created with ID: {event.response.id}")
            elif event.type == "response.output_text.delta":
                print(f"Delta: {event.delta}")
            elif event.type == "response.text.done":
                print(f"\nFollow-up response done!")
            elif event.type == "response.output_item.done":
                if event.item.type == "message":
                    item = event.item
                    if item.content[-1].type == "output_text":
                        text_content = item.content[-1]
                        for annotation in text_content.annotations:
                            if annotation.type == "file_citation":
                                print(
                                    f"File Citation - Filename: {annotation.filename}, File ID: {annotation.file_id}"
                                )
            elif event.type == "response.completed":
                print(f"\nFollow-up completed!")
                print(f"Full response: {event.response.output_text}")

        # Clean up resources
        print("\n" + "=" * 60)
        print("Cleaning up resources...")
        print("=" * 60)

        # Delete the agent
        await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")

        # Clean up vector store
        try:
            await openai_client.vector_stores.delete(vector_store.id)
            print("Vector store deleted")
        except Exception as e:
            print(f"Warning: Could not delete vector store: {e}")

    print("\nFile search streaming sample completed!")


if __name__ == "__main__":
    asyncio.run(main())
