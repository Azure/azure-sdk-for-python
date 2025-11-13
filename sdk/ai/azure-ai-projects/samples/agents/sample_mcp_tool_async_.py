# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to interact with the Foundry Project MCP tool.

USAGE:
    python sample_mcp_tool_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv mcp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) IMAGE_GEN_DEPLOYMENT_NAME - The deployment name of the image generation model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()


async def main():
    credential = DefaultAzureCredential()
    try:
        # Fetch the Entra ID token with audience as https://ai.azure.com
        access_token = await credential.get_token("https://ai.azure.com")
        endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
        async with streamablehttp_client(
            url=f"{endpoint}/mcp_tools?api-version=2025-05-15-preview",
            headers={"Authorization": f"Bearer {access_token.token}"},
        ) as (read_stream, write_stream, _):
            # Create a session using the client streams
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()
                # List available tools
                tools = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools.tools]}")

                # For each tool, print its details
                for tool in tools.tools:
                    print(f"\n\nTool Name: {tool.name}, Input Schema: {tool.inputSchema}")

                # Run the code interpreter tool
                code_interpreter_result = await session.call_tool(
                    name="code_interpreter",
                    arguments={"code": "print('Hello from Microsoft Foundry MCP Code Interpreter tool!')"},
                )
                print(f"\n\nCode Interpreter Output: {code_interpreter_result.content}")

                # Run the image_generation tool
                image_generation_result = await session.call_tool(
                    name="image_generation",
                    arguments={"prompt": "Draw a cute puppy riding a skateboard"},
                    meta={"imagegen_model_deployment_name": os.getenv("IMAGE_GEN_DEPLOYMENT_NAME", "")},
                )
                print(f"\n\nImage Generation Output: {image_generation_result.content}")

                # Run the file_search tool
                # Create a project client
                project_client = AIProjectClient(
                    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
                    credential=credential,
                    api_version="2025-05-15-preview",
                )
                async with project_client:
                    # Create a vector store
                    openai_client = await project_client.get_openai_client()
                    vector_store = await openai_client.vector_stores.create(
                        name="sample_vector_store",
                    )

                    vector_store_file = await openai_client.vector_stores.files.upload_and_poll(
                        vector_store_id=vector_store.id,
                        file=open(
                            os.path.abspath(os.path.join(os.path.dirname(__file__), "./assets/product_info.md")),
                            "rb",
                        ),
                    )

                    print(f"\n\nUploaded file, file ID: {vector_store_file.id} to vector store ID: {vector_store.id}")

                    # Call the file_search tool
                    file_search_result = await session.call_tool(
                        name="file_search",
                        arguments={"queries": ["What feature does Smart Eyewear offer?"]},
                        meta={"vector_store_ids": [vector_store.id]},
                    )
                    print(f"\n\nFile Search Output: {file_search_result.content}")
    finally:
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
