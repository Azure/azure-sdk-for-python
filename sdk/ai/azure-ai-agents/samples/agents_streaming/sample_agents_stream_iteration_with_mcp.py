# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the
    Model Context Protocol (MCP) tool from the Azure Agents service, and
    iteration in streaming. It uses a synchronous client.
    To learn more about Model Context Protocol, visit https://modelcontextprotocol.io/

USAGE:
    python sample_agents_stream_iteration_with_mcp.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents>=1.2.0b3 azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) MCP_SERVER_URL - The URL of your MCP server endpoint.
    4) MCP_SERVER_LABEL - A label for your MCP server.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AgentStreamEvent, RunStepDeltaChunk
from azure.ai.agents.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
    McpTool,
    MessageRole,
    MessageDeltaTextContent,
    MessageDeltaTextUrlCitationAnnotation,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
)
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

    # Get MCP server configuration from environment variables
    mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://gitmcp.io/Azure/azure-rest-api-specs")
    mcp_server_label = os.environ.get("MCP_SERVER_LABEL", "github")

    # Initialize agent MCP tool
    mcp_tool = McpTool(
        server_label=mcp_server_label,
        server_url=mcp_server_url,
        allowed_tools=[],  # Optional: specify allowed tools
    )

    # You can also add or remove allowed tools dynamically
    search_api_code = "search_azure_rest_api_code"
    mcp_tool.allow_tool(search_api_code)
    print(f"Allowed tools: {mcp_tool.allowed_tools}")

    # Create a new agent.
    # NOTE: To reuse existing agent, fetch it with get_agent(agent.id)
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
        tools=mcp_tool.definitions,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="Please summarize the Azure REST API specifications Readme",
    )
    print(f"Created message, message ID {message.id}")

    # Process Agent run and stream events back to the client. It may take a few minutes for the agent to complete the run.
    mcp_tool.update_headers("SuperSecret", "123456")
    # mcp_tool.set_approval_mode("never")  # Uncomment to disable approval requirement
    with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources) as stream:

        for event_type, event_data, _ in stream:

            if isinstance(event_data, MessageDeltaChunk):
                print(f"Text delta received: {event_data.text}")
                if event_data.delta.content and isinstance(event_data.delta.content[0], MessageDeltaTextContent):
                    delta_text_content = event_data.delta.content[0]
                    if delta_text_content.text and delta_text_content.text.annotations:
                        for delta_annotation in delta_text_content.text.annotations:
                            if isinstance(delta_annotation, MessageDeltaTextUrlCitationAnnotation):
                                print(
                                    f"URL citation delta received: [{delta_annotation.url_citation.title}]({delta_annotation.url_citation.url})"
                                )

            elif isinstance(event_data, RunStepDeltaChunk):
                print(f"RunStepDeltaChunk received. ID: {event_data.id}.")

            elif isinstance(event_data, ThreadMessage):
                print(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

            elif isinstance(event_data, ThreadRun):
                print(f"ThreadRun status: {event_data.status}")

                if event_data.status == "failed":
                    print(f"Run failed. Error: {event_data.last_error}")

                if event_data.status == "requires_action" and isinstance(
                    event_data.required_action, SubmitToolApprovalAction
                ):
                    tool_calls = event_data.required_action.submit_tool_approval.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        agents_client.runs.cancel(thread_id=event_data.thread_id, run_id=event_data.id)
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
                                        headers=mcp_tool.headers,
                                    )
                                )
                            except Exception as e:
                                print(f"Error approving tool_call {tool_call.id}: {e}")

                    print(f"tool_approvals: {tool_approvals}")
                    if tool_approvals:
                        # Once we receive 'requires_action' status, the next event will be DONE.
                        # Here we associate our existing event handler to the next stream.
                        agents_client.runs.submit_tool_outputs_stream(
                            thread_id=event_data.thread_id,
                            run_id=event_data.id,
                            tool_approvals=tool_approvals,
                            event_handler=stream,
                        )

            elif isinstance(event_data, RunStep):
                print(f"RunStep type: {event_data.type}, Status: {event_data.status}")

                # Check if there are tool calls in the step details
                step_details = event_data.get("step_details", {})
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

            elif event_type == AgentStreamEvent.ERROR:
                print(f"An error occurred. Data: {event_data}")

            elif event_type == AgentStreamEvent.DONE:
                print("Stream completed.")

            else:
                print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    # Clean-up and delete the agent once the run is finished.
    # NOTE: Comment out this line if you plan to reuse the agent later.
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    response_message = agents_client.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
