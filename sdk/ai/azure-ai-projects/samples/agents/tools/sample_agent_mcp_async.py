# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using MCP (Model Context Protocol) tools and an asynchronous client.

USAGE:
    python sample_agent_mcp_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        mcp_tool = MCPTool(
            server_label="api-specs",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            require_approval="always",
        )

        # Create tools list with proper typing for the agent definition
        tools: list[Tool] = [mcp_tool]

        # Create a prompt agent with MCP tool capabilities
        agent = await project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                tools=tools,
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        # Create a conversation thread to maintain context across multiple interactions
        conversation = await openai_client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        # Send initial request that will trigger the MCP tool
        response = await openai_client.responses.create(
            conversation=conversation.id,
            input="Please summarize the Azure REST API specifications Readme",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        # Process any MCP approval requests that were generated
        input_list: ResponseInputParam = []
        for item in response.output:
            if item.type == "mcp_approval_request":
                if item.server_label == "api-specs" and item.id:
                    # Automatically approve the MCP request to allow the agent to proceed
                    # In production, you might want to implement more sophisticated approval logic
                    input_list.append(
                        McpApprovalResponse(
                            type="mcp_approval_response",
                            approve=True,
                            approval_request_id=item.id,
                        )
                    )

        print("Final input:")
        print(input_list)

        # Send the approval response back to continue the agent's work
        # This allows the MCP tool to access the GitHub repository and complete the original request
        response = await openai_client.responses.create(
            input=input_list,
            previous_response_id=response.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        # Print result (should contain "Azure")
        print(f"==> Result: {response.output_text}")

        # Clean up resources by deleting the agent version
        # This prevents accumulation of unused agent versions in your project
        await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
