# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the
    Model Context Protocol (MCP) tool from the Azure Agents service using a synchronous client.
    To learn more about Model Context Protocol, visit https://modelcontextprotocol.io/

USAGE:
    python sample_agents_mcp.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents>=1.2.0b3 azure-identity --pre

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) MCP_SERVER_URL - The URL of your MCP server endpoint.
    4) MCP_SERVER_LABEL - A label for your MCP server.
"""

import os
from typing import Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    ToolApproval,
    RunHandler,
    ThreadRun,
    ToolSet,
)

# Get MCP server configuration from environment variables
mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://gitmcp.io/Azure/azure-rest-api-specs")
mcp_server_label = os.environ.get("MCP_SERVER_LABEL", "github")

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START create_agent_with_mcp_tool]
# Initialize agent MCP tool
mcp_tool = McpTool(
    server_label=mcp_server_label,
    server_url=mcp_server_url,
    allowed_tools=[],  # Optional: specify allowed tools
)
toolset = ToolSet()
toolset.add(mcp_tool)

# You can also add or remove allowed tools dynamically
search_api_code = "search_azure_rest_api_code"
mcp_tool.allow_tool(search_api_code)
print(f"Allowed tools: {mcp_tool.allowed_tools}")


class MyRunHandler(RunHandler):
    def submit_mcp_tool_approval(
        self, run: ThreadRun, tool_call: RequiredMcpToolCall, **kwargs
    ) -> Optional[ToolApproval]:
        return ToolApproval(
            tool_call_id=tool_call.id,
            approve=True,
            headers=mcp_tool.headers,
        )


# Create agent with MCP tool and process agent run
with project_client:
    agents_client = project_client.agents

    # Create a new agent.
    # NOTE: To reuse existing agent, fetch it with get_agent(agent_id)
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-mcp-agent",
        instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
        toolset=toolset,
    )
    # [END create_agent_with_mcp_tool]

    print(f"Created agent, ID: {agent.id}")
    print(f"MCP Server: {mcp_tool.server_label} at {mcp_tool.server_url}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please summarize the Azure REST API specifications Readme",
    )
    print(f"Created message, ID: {message.id}")

    # [START handle_tool_approvals]
    # Create and process agent run in thread with MCP tools
    mcp_tool.update_headers("SuperSecret", "123456")

    run_handler = MyRunHandler()
    # mcp_tool.set_approval_mode("never")  # Uncomment to disable approval requirement
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id, run_handler=run_handler)
    print(f"Created run, ID: {run.id}")

    print(f"Run completed with status: {run.status}")
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Display run steps and tool calls
    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)

    # Loop through each step
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")

        # Check if there are tool calls in the step details
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  MCP Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

        if isinstance(step_details, RunStepActivityDetails):
            for activity in step_details.activities:
                for function_name, function_definition in activity.tools.items():
                    print(
                        f'  The function {function_name} with description "{function_definition.description}" will be called.:'
                    )
                    if len(function_definition.parameters) > 0:
                        print("  Function parameters:")
                        for argument, func_argument in function_definition.parameters.properties.items():
                            print(f"      {argument}")
                            print(f"      Type: {func_argument.type}")
                            print(f"      Description: {func_argument.description}")
                    else:
                        print("This function has no parameters")

        print()  # add an extra newline between steps

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    print("\nConversation:")
    print("-" * 50)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role.upper()}: {last_text.text.value}")
            print("-" * 50)

    # Example of dynamic tool management
    print(f"\nDemonstrating dynamic tool management:")
    print(f"Current allowed tools: {mcp_tool.allowed_tools}")

    # Remove a tool
    try:
        mcp_tool.disallow_tool(search_api_code)
        print(f"After removing {search_api_code}: {mcp_tool.allowed_tools}")
    except ValueError as e:
        print(f"Error removing tool: {e}")

    # Clean-up and delete the agent once the run is finished.
    # NOTE: Comment out this line if you plan to reuse the agent later.
    agents_client.delete_agent(agent.id)
    print("Deleted agent")
