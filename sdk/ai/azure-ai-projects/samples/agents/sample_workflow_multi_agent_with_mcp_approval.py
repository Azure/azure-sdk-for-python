# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a multi-agent workflow using a synchronous client
    with a student agent (using MCP tools) answering questions and then a teacher
    agent checking the answer. The workflow handles MCP approval requests as always.

    The student agent can access external resources via MCP tools if needed to answer
    questions that require additional context or information.

USAGE:
    python sample_workflow_multi_agent_with_mcp_approval.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WorkflowAgentDefinition,
    MCPTool,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # Define MCP tool for accessing external resources (optional - can be removed for simpler demo)
    # Note: MCP tools in workflows may require special handling depending on the use case
    mcp_tool = MCPTool(
        server_label="api-specs",
        server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
        require_approval="always",
    )

    # Create Teacher Agent
    teacher_agent = project_client.agents.create_version(
        agent_name="teacher-agent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="""You are a teacher that create Foundry project question for student and check answer.
                            Verify student's answer from mcp tools.
                            If the answer is correct, you stop the conversation by saying [COMPLETE].
                            If the answer is wrong, you ask student to fix it.""",
            tools=[mcp_tool],
        ),
    )
    print(f"Agent created (id: {teacher_agent.id}, name: {teacher_agent.name}, version: {teacher_agent.version})")

    # Create Student Agent WITHOUT MCP tool initially to keep the sample simple
    # To demonstrate MCP approval in workflows, the tool would need to be triggered by appropriate queries
    student_agent = project_client.agents.create_version(
        agent_name="student-agent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="""You are a student who answers questions from the teacher.
                            When the teacher gives you a question, you answer it using mcp tool.""",
            tools=[mcp_tool],
        ),
    )
    print(f"Agent created (id: {student_agent.id}, name: {student_agent.name}, version: {student_agent.version})")

    # Create Multi-Agent Workflow
    workflow_yaml = f"""
kind: workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions:
    - kind: SetVariable
      id: set_variable_input_task
      variable: Local.LatestMessage
      value: "=UserMessage(System.LastMessageText)"

    - kind: CreateConversation
      id: create_student_conversation
      conversationId: Local.StudentConversationId

    - kind: CreateConversation
      id: create_teacher_conversation
      conversationId: Local.TeacherConversationId

    - kind: InvokeAzureAgent
      id: student_agent
      description: The student node
      conversationId: "=Local.StudentConversationId"
      agent:
        name: {student_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: InvokeAzureAgent
      id: teacher_agent
      description: The teacher node
      conversationId: "=Local.TeacherConversationId"
      agent:
        name: {teacher_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: SendActivity
      id: send_teacher_reply
      activity: "{{Last(Local.LatestMessage).Text}}"

    - kind: SetVariable
      id: set_variable_turncount
      variable: Local.TurnCount
      value: "=Local.TurnCount + 1"

    - kind: ConditionGroup
      id: completion_check
      conditions:
        - condition: '=!IsBlank(Find("[COMPLETE]", Upper(Last(Local.LatestMessage).Text)))'
          id: check_done
          actions:
            - kind: EndConversation
              id: end_workflow

        - condition: "=Local.TurnCount >= 4"
          id: check_turn_count_exceeded
          actions:
            - kind: SendActivity
              id: send_activity_tired
              activity: "Let's try again later...I am tired."

      elseActions:
        - kind: GotoAction
          id: goto_student_agent
          actionId: student_agent
"""

    workflow = project_client.agents.create_version(
        agent_name="student-teacher-workflow",
        definition=WorkflowAgentDefinition(workflow=workflow_yaml),
    )

    print(f"Agent created (id: {workflow.id}, name: {workflow.name}, version: {workflow.version})")

    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    stream = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": workflow.name, "type": "agent_reference"}},
        input="Please summarize the Azure REST API specifications Readme",
        stream=True,
    )

    # Track MCP approval requests during streaming
    mcp_approval_requests = []
    response = None

    for event in stream:
        print(f"Event {event.sequence_number} type '{event.type}'", end="")
        if (
            event.type in ("response.output_item.added", "response.output_item.done")
        ) and event.item.type == "workflow_action":  # pyright: ignore [reportAttributeAccessIssue]
            print(
                f": item action ID '{event.item.action_id}' is '{event.item.status}' (previous action ID: '{event.item.previous_action_id}')",  # pyright: ignore [reportAttributeAccessIssue]
                end="",
            )
        elif (
            event.type == "response.output_item.done" and event.item.type == "mcp_approval_request"
        ):  # pyright: ignore [reportAttributeAccessIssue]
            # Collect MCP approval requests during streaming
            print(
                f": MCP approval request for server '{event.item.server_label}'", end=""
            )  # pyright: ignore [reportAttributeAccessIssue]
            mcp_approval_requests.append(event.item)  # pyright: ignore [reportAttributeAccessIssue]
        elif event.type == "response.output_item.added" and hasattr(
            event, "item"
        ):  # pyright: ignore [reportAttributeAccessIssue]
            # Print other item types
            print(f": item type '{event.item.type}'", end="")  # pyright: ignore [reportAttributeAccessIssue]
        elif event.type == "response.completed":
            response = openai_client.responses.retrieve(event.response.id)
            print(f": Final Response: {response.output_text}", end="")
        elif event.type == "response.failed":
            response = openai_client.responses.retrieve(event.response.id)
            print(f": Response failed - Error: {response.error}", end="")
        print("", flush=True)

    print(f"\nStream completed. Response status: {response.status if response else 'No response'}")
    print(f"MCP approval requests collected: {len(mcp_approval_requests)}")

    # Process any MCP approval requests that were collected
    if mcp_approval_requests and response:
        print(f"\nProcessing {len(mcp_approval_requests)} MCP approval request(s)...")
        input_list: ResponseInputParam = []

        for item in mcp_approval_requests:
            if item.server_label == "api-specs" and item.id:
                # Automatically approve the MCP request to allow the agent to proceed
                print(f"Approving MCP request for server '{item.server_label}'")
                input_list.append(
                    McpApprovalResponse(
                        type="mcp_approval_response",
                        approve=True,
                        approval_request_id=item.id,
                    )
                )

        if input_list:
            # Send the approval response back to continue the agent's work
            print("\nContinuing workflow with MCP approvals...")
            response = openai_client.responses.create(
                input=input_list,
                previous_response_id=response.id,
                extra_body={"agent_reference": {"name": workflow.name, "type": "agent_reference"}},
            )
            print(f"Agent response after approval: {response.output_text}")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")

    project_client.agents.delete_version(agent_name=workflow.name, agent_version=workflow.version)
    print("Workflow deleted")

    project_client.agents.delete_version(agent_name=student_agent.name, agent_version=student_agent.version)
    print("Student Agent deleted")

    project_client.agents.delete_version(agent_name=teacher_agent.name, agent_version=teacher_agent.version)
    print("Teacher Agent deleted")
