# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a multi-agent workflow using an asynchronous client
    with a student agent answering the question first and then a teacher agent checking the answer.

USAGE:
    python sample_workflow_multi_agent_async.py

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
from azure.ai.projects.models import (
    PromptAgentDefinition,
    ResponseStreamEventType,
    WorkflowAgentDefinition,
    ItemType,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


async def main():

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):

        teacher_agent = await project_client.agents.create_version(
            agent_name="teacher-agent-async",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="""You are a teacher that create pre-school math question for student and check answer. 
                              If the answer is correct, you stop the conversation by saying [COMPLETE]. 
                              If the answer is wrong, you ask student to fix it.""",
            ),
        )
        print(f"Agent created (id: {teacher_agent.id}, name: {teacher_agent.name}, version: {teacher_agent.version})")

        student_agent = await project_client.agents.create_version(
            agent_name="student-agent-async",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="""You are a student who answers questions from the teacher. 
                              When the teacher gives you a question, you answer it.""",
            ),
        )
        print(f"Agent created (id: {student_agent.id}, name: {student_agent.name}, version: {student_agent.version})")

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

        workflow = await project_client.agents.create_version(
            agent_name="student-teacher-workflow-async",
            definition=WorkflowAgentDefinition(workflow=workflow_yaml),
        )

        print(f"Agent created (id: {workflow.id}, name: {workflow.name}, version: {workflow.version})")

        conversation = await openai_client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        stream = await openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": workflow.name, "type": "agent_reference"}},
            input="1 + 1 = ?",
            stream=True,
            metadata={"x-ms-debug-mode-enabled": "1"},
        )

        async for event in stream:
            print(f"Event {event.sequence_number} type '{event.type}'", end="")
            if (
                event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED
                or event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE
            ) and event.item.type == ItemType.WORKFLOW_ACTION:
                print(
                    f": item action ID '{event.item.action_id}' is '{event.item.status}' (previous action ID: '{event.item.previous_action_id}')",
                    end="",
                )
            print("", flush=True)

        await openai_client.conversations.delete(conversation_id=conversation.id)
        print("Conversation deleted")

        await project_client.agents.delete_version(agent_name=workflow.name, agent_version=workflow.version)
        print("Workflow deleted")

        await project_client.agents.delete_version(agent_name=student_agent.name, agent_version=student_agent.version)
        print("Student Agent deleted")

        await project_client.agents.delete_version(agent_name=teacher_agent.name, agent_version=teacher_agent.version)
        print("Teacher Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
