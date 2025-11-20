# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to directly interact with MCP (Model Context Protocol) tools
    using the low-level MCP client library to connect to the Foundry Project's MCP tools API:
        {AZURE_AI_PROJECT_ENDPOINT}/mcp_tools?api-version=2025-05-15-preview

    For agent-based MCP tool usage, see samples in samples/agents/tools/sample_agent_mcp.py
    and related files in that directory.

    WORKFLOW:
    This sample demonstrates a typical MCP client workflow:
    1. Establish connection to the Foundry Project MCP endpoint using ClientSession
    2. Initialize the session and discover available tools
    3. Invoke tools programmatically with specific arguments and metadata
    4. Process and save tool outputs (e.g., writing image generation results to a file)
    5. Chain multiple tool calls together (code interpreter → image generation → file search)

USAGE:
    python sample_mcp_tool_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv mcp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) IMAGE_GEN_DEPLOYMENT_NAME - The deployment name of the image generation model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) (Optional) LOG_LEVEL - Logging level for HTTP client debugging. Valid values:
       - CRITICAL or 50 - Suppresses all logs except critical errors
       - FATAL - same as CRITICAL
       - ERROR or 40 - Shows errors only
       - WARNING or WARN or 30 - Shows warnings and errors
       - INFO or 20 - Shows informational messages, warnings, and errors
       - DEBUG or 10 - Shows detailed HTTP requests/responses and all other logs
       - NOTSET or 0 - Uses parent logger configuration
"""

import asyncio
import base64
import os
import logging
from dotenv import load_dotenv
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from mcp import ClientSession
from mcp.types import ImageContent
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()

# Configure logging level from environment variable
# Set LOG_LEVEL=DEBUG to see detailed HTTP requests and responses
log_level = os.getenv("LOG_LEVEL", "").upper()
if log_level:
    logging.basicConfig(level=getattr(logging, log_level, logging.CRITICAL))
    # Enable httpx logging to see HTTP requests at the same level
    logging.getLogger("httpx").setLevel(getattr(logging, log_level, logging.CRITICAL))

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


async def main():

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
        streamablehttp_client(
            url=f"{endpoint}/mcp_tools?api-version=2025-05-15-preview",
            headers={"Authorization": f"Bearer {(await credential.get_token('https://ai.azure.com')).token}"},
        ) as (read_stream, write_stream, _),
        ClientSession(read_stream, write_stream) as session,
    ):

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

        # Save the image generation output to a file
        if image_generation_result.content and isinstance(image_generation_result.content[0], ImageContent):
            print("\nDownloading generated image...")
            filename = "puppy.png"
            file_path = os.path.abspath(filename)

            with open(file_path, "wb") as f:
                f.write(base64.b64decode(image_generation_result.content[0].data))

        # Create a vector store
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


if __name__ == "__main__":
    asyncio.run(main())
