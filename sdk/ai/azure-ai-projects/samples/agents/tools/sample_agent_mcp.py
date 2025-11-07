# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using MCP (Model Context Protocol) tools and a synchronous client.

USAGE:
    python sample_agent_mcp.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam


load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Get the OpenAI client for responses and conversations
openai_client = project_client.get_openai_client()

mcp_tool = MCPTool(
    server_label="api-specs",
    server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
    require_approval="always",
)

# Create tools list with proper typing for the agent definition
tools: list[Tool] = [mcp_tool]

with project_client:
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
            tools=tools,
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create a conversation thread to maintain context across multiple interactions
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Send initial request that will trigger the MCP tool
    response = openai_client.responses.create(
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
    response = openai_client.responses.create(
        input=input_list,
        previous_response_id=response.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Response: {response.output_text}")

    # Clean up resources by deleting the agent version
    # This prevents accumulation of unused agent versions in your project
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
