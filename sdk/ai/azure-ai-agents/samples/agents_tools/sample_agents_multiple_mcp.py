# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with multiple
    Model Context Protocol (MCP) servers from the Azure Agents service using a synchronous client.
    To learn more about Model Context Protocol, visit https://modelcontextprotocol.io/

USAGE:
    python sample_agents_multiple_mcp.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents>=1.2.0b3 azure-identity --pre

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) MCP_SERVER_URL_1 - The URL of your first MCP server endpoint.
    4) MCP_SERVER_LABEL_1 - A label for your first MCP server.
    5) MCP_SERVER_URL_2 - The URL of your second MCP server endpoint.
    6) MCP_SERVER_LABEL_2 - A label for your second MCP server.
"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    Tool,
    ToolApproval,
    get_tool_resources,
    get_tool_definitions,
)

# Get MCP server configuration from environment variables
mcp_server_url_1 = os.environ.get("MCP_SERVER_URL_1", "https://gitmcp.io/Azure/azure-rest-api-specs")
mcp_server_label_1 = os.environ.get("MCP_SERVER_LABEL_1", "github")
mcp_server_url_2 = os.environ.get("MCP_SERVER_URL_2", "https://learn.microsoft.com/api/mcp")
mcp_server_label_2 = os.environ.get("MCP_SERVER_LABEL_2", "microsoft_learn")


project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Initialize agent MCP tool
mcp_tool1 = McpTool(
    server_label=mcp_server_label_1,
    server_url=mcp_server_url_1,
    allowed_tools=[],  # Optional: specify allowed tools
)

# You can also add or remove allowed tools dynamically
search_api_code = "search_azure_rest_api_code"
mcp_tool1.allow_tool(search_api_code)
print(f"Allowed tools: {mcp_tool1.allowed_tools}")

mcp_tool2 = McpTool(
    server_label=mcp_server_label_2,
    server_url=mcp_server_url_2,
    allowed_tools=["microsoft_docs_search"],  # Optional: specify allowed tools
)

tools: list[Tool] = [mcp_tool1, mcp_tool2]

# Create agent with MCP tool and process agent run
with project_client:
    agents_client = project_client.agents

    # Create a new agent.
    # NOTE: To reuse existing agent, fetch it with get_agent(agent_id)
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-mcp-agent",
        instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
        tools=get_tool_definitions(tools),
    )

    print(f"Created agent, ID: {agent.id}")
    print(f"MCP Server 1: {mcp_tool1.server_label} at {mcp_tool1.server_url}")
    print(f"MCP Server 2: {mcp_tool2.server_label} at {mcp_tool2.server_url}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please summarize the Azure REST API specifications Readme and Give me the Azure CLI commands to create an Azure Container App with a managed identity",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with MCP tools
    mcp_tool1.update_headers("SuperSecret", "123456")
    mcp_tool2.set_approval_mode("never")  # Disable approval for MS Learn MCP tool
    tool_resources = get_tool_resources(tools)
    print(tool_resources)
    run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id, tool_resources=tool_resources)
    print(f"Created run, ID: {run.id}")

    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
            tool_calls = run.required_action.submit_tool_approval.tool_calls
            if not tool_calls:
                print("No tool calls provided - cancelling run")
                agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                break

            tool_approvals = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredMcpToolCall):
                    try:
                        print(f"Approving tool call: {tool_call}")
                        tool_approvals.append(
                            ToolApproval(
                                tool_call_id=tool_call.id,
                                approve=True,
                                headers=mcp_tool1.headers,
                            )
                        )
                    except Exception as e:
                        print(f"Error approving tool_call {tool_call.id}: {e}")

            print(f"tool_approvals: {tool_approvals}")
            if tool_approvals:
                agents_client.runs.submit_tool_outputs(
                    thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                )

        print(f"Current run status: {run.status}")

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
    print(f"Current allowed tools: {mcp_tool1.allowed_tools}")

    # Remove a tool
    try:
        mcp_tool1.disallow_tool(search_api_code)
        print(f"After removing {search_api_code}: {mcp_tool1.allowed_tools}")
    except ValueError as e:
        print(f"Error removing tool: {e}")

    # Clean-up and delete the agent once the run is finished.
    # NOTE: Comment out this line if you plan to reuse the agent later.
    agents_client.delete_agent(agent.id)
    print("Deleted agent")
