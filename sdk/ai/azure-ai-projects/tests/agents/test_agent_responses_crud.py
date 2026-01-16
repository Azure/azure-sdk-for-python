# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from pydantic import BaseModel, Field
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    ResponseTextFormatConfigurationJsonSchema,
    PromptAgentDefinitionText,
)


class TestAgentResponsesCrud(TestBase):

    # To run this test:
    # pytest tests/agents/test_agent_responses_crud.py::TestAgentResponsesCrud::test_agent_responses_crud -s
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_responses_crud(self, **kwargs):
        """
        Test two-turn Responses with Agent reference and Conversation.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------

        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        POST   /openai/conversations                         openai_client.conversations.create()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create()
        GET    /openai/responses/{response_id}               openai_client.responses.retrieve() # SERVICE BUG? returns 500 Internal Server Error
        DELETE /openai/responses/{response_id}               openai_client.responses.delete() # SERVICE BUG? returns 500 Internal Server Error
        GET    /openai/responses/{response_id}/input_items   openai_client.responses.list_input_items() # SERVICE BUG? returns 500 Internal Server Error
        GET    /openai/responses                             openai_client.responses.list()
        POST   /openai/responses/{response_id}/cancel        openai_client.responses.cancel() # SERVICE BUG? returns 500 Internal Server Error

        # Teardown:
        DELETE /conversations/{conversation_id}              openai_client.conversations.delete()
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = kwargs.get("azure_ai_model_deployment_name")

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        agent = project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant that answers general questions",
            ),
        )
        print(f"\nAgent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": "How many feet in a mile?"}]
        )
        print(f"Created conversation with initial user message (id: {conversation.id})")

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",  # TODO: Remove 'input' once service is fixed
        )
        print(f"Response id: {response.id}, output text: {response.output_text}")
        assert "5280" in response.output_text or "5,280" in response.output_text

        items = openai_client.conversations.items.create(
            conversation.id,
            items=[{"type": "message", "role": "user", "content": "And how many meters?"}],
        )

        # Test retrieving a response
        # TODO: Service bug? Is this supposed to work? returns 500 Internal Server Error
        # retrieved_response = openai_client.responses.retrieve(response_id=response.id)
        # print(f"Retrieved response output: {retrieved_response.output_text}")
        # assert retrieved_response.id == response.id
        # assert retrieved_response.output_text == response.output_text

        # Test deleting a response
        # TODO: Service bug? Is this supposed to work? returns 500 Internal Server Error
        # deleted_response = openai_client.responses.delete(response_id=response.id)
        # assert deleted_response.id == response.id
        # assert deleted_response.deleted is True
        # print(f"Deleted response: {deleted_response}")

        # Re-add original user message to the conversation
        # conversation = openai_client.conversations.create(
        #     items=[ResponsesUserMessageItemParam(content="What is the size of France in square miles?")]
        # )
        # print(f"Created conversation with initial user message (id: {conversation.id})")

        # openai_client.conversations.items.create(
        #     conversation_id=conversation.id,
        #     # items=[ResponsesUserMessageItemParam(content="And what is the capital city?")],
        #     items=[{"type": "message", "role": "user", "content": "And what is the capital city?"}],
        # )
        # print(f"Added a second user message to the conversation")

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",  # TODO: Remove 'input' once service is fixed
        )
        print(f"Response id: {response.id}, output text: {response.output_text}")
        assert "1609" in response.output_text or "1,609" in response.output_text

        # TODO: Service bug? Is this supposed to work? returns 500 Internal Server Error
        # print(f"List all input items in the response:")
        # for listed_item in openai_client.responses.list_input_items(response_id=response.id):
        #     print(f" - response item type {listed_item.type}, id {listed_item.id}")

        # OpenAI SDK does not support "list" responses. Even though the Azure endpoint does.
        # print(f"List all responses:")
        # count = 0
        # for listed_response in openai_client.responses.list(conversation_id=conversation.id):
        #     count += 1
        #     # TODO: Note of these responses match the above created responses
        #     print(f" - Response id: {listed_response.id}, output text: {listed_response.output_text}")
        # assert count >= 2

        # openai_client.conversations.items.create(
        #     conversation_id=conversation.id,
        #     items=[ResponsesUserMessageItemParam(content="List all prime numbers between 1 and 1000.")],
        # )
        # print(f"Added a third user message to the conversation")

        # response = openai_client.responses.create(
        #     conversation=conversation.id,
        #     extra_body={"agent": AgentReference(name=agent.name).as_dict()}
        # )
        # print(f"Response id: {response.id}, output text: {response.output_text}")

        # TODO: Why do we have a cancel operation, when there are no long-running-operations?
        # TODO: Service bug? Is this supposed to work? returns 500 Internal Server Error
        # If the have the response ID, it means the "response.create" call is already completed...
        # canceled_response = openai_client.responses.cancel(response_id=response.id)
        # print(f"Canceled response id: {canceled_response.id}")

        # Teardown
        openai_client.conversations.delete(conversation_id=conversation.id)
        print("Conversation deleted")

        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")

    # To run this test:
    # pytest tests\agents\test_agent_responses_crud.py::TestAgentResponsesCrud::test_agent_responses_with_structured_output -s
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_responses_with_structured_output(self, **kwargs):
        model = kwargs.get("azure_ai_model_deployment_name")

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        class CalendarEvent(BaseModel):
            model_config = {"extra": "forbid"}
            name: str
            date: str = Field(description="Date in YYYY-MM-DD format")
            participants: list[str]

        agent = project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=model,
                text=PromptAgentDefinitionText(
                    format=ResponseTextFormatConfigurationJsonSchema(
                        name="CalendarEvent", schema=CalendarEvent.model_json_schema()
                    )
                ),
                instructions="""
                    You are a helpful assistant that extracts calendar event information from the input user messages,
                    and returns it in the desired structured output format.
                """,
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        conversation = openai_client.conversations.create(
            items=[
                {
                    "type": "message",
                    "role": "user",
                    "content": "Alice and Bob are going to a science fair this Friday, November 7, 2025.",
                }
            ]
        )
        print(f"Created conversation with initial user message (id: {conversation.id})")

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",  # TODO: Remove 'input' once service is fixed
        )
        print(f"Response id: {response.id}, output text: {response.output_text}")
        assert response.output_text == '{"name":"Science Fair","date":"2025-11-07","participants":["Alice","Bob"]}'

        openai_client.conversations.delete(conversation_id=conversation.id)
        print("Conversation deleted")

        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")
