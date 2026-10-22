# pylint: disable=too-many-lines,line-too-long,useless-suppression
# # ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
from typing import Any

import json
import jsonref
import os
import re
import pytest
import io
import time

from azure.ai.agents.aio import AgentsClient
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.agents.models import (
    AzureAISearchTool,
    AzureFunctionTool,
    AzureFunctionStorageQueue,
    AgentStreamEvent,
    AgentThread,
    BingCustomSearchTool,
    BingGroundingTool,
    BrowserAutomationTool,
    CodeInterpreterTool,
    CodeInterpreterToolResource,
    ConnectedAgentTool,
    DeepResearchTool,
    FabricTool,
    FilePurpose,
    FileSearchTool,
    FileSearchToolCallContent,
    FileSearchToolResource,
    FunctionTool,
    McpTool,
    MessageAttachment,
    MessageRole,
    MessageDeltaChunk,
    MessageTextContent,
    MessageTextFileCitationAnnotation,
    MessageTextFileCitationDetails,
    MessageTextUrlCitationDetails,
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
    RequiredMcpToolCall,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
    RunStepActivityDetails,
    RunAdditionalFieldList,
    RunStepBingCustomSearchToolCall,
    RunStepBingGroundingToolCall,
    RunStepBrowserAutomationToolCall,
    RunStepCodeInterpreterToolCall,
    RunStepConnectedAgentToolCall,
    RunStepDeepResearchToolCall,
    RunStepAzureAISearchToolCall,
    RunStepAzureFunctionToolCall,
    RunStepDeltaAzureAISearchToolCall,
    RunStepDeltaAzureFunctionToolCall,
    RunStepDeltaBingGroundingToolCall,
    RunStepDeltaChunk,
    RunStepDeltaConnectedAgentToolCall,
    RunStepDeltaCodeInterpreterToolCall,
    RunStepDeltaCustomBingGroundingToolCall,
    RunStepDeltaFileSearchToolCall,
    RunStepDeltaMcpToolCall,
    RunStepDeltaMicrosoftFabricToolCall,
    RunStepDeltaOpenAPIToolCall,
    RunStepDeltaToolCallObject,
    RunStepDeltaSharepointToolCall,
    RunStepFileSearchToolCall,
    RunStepFileSearchToolCallResult,
    RunStepFileSearchToolCallResults,
    RunStepMcpToolCall,
    RunStepMicrosoftFabricToolCall,
    RunStepOpenAPIToolCall,
    RunStepSharepointToolCall,
    RunStepToolCallDetails,
    RunStatus,
    RunStep,
    SharepointTool,
    SubmitToolApprovalAction,
    ThreadMessage,
    ThreadMessageOptions,
    ThreadRun,
    ToolApproval,
    ToolResources,
    ToolSet,
    VectorStore,
    VectorStoreConfigurations,
    VectorStoreConfiguration,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)
from test_agents_client_base import (
    TestAgentClientBase,
    agentClientPreparer,
    fetch_current_datetime_recordings,
    fetch_current_datetime_live,
)

# TODO clean this up / get rid of anything not in use

"""
issues I've noticed with the code:
    delete_thread(thread.id) fails
    cancel_thread(thread.id) expires/times out occasionally
    added time.sleep() to the beginning of my last few tests to avoid limits
    when using the endpoint from Howie, delete_agent(agent.id) did not work but would not cause an error
"""

# Statically defined user functions for fast reference
user_functions_recording = {fetch_current_datetime_recordings}
user_functions_live = {fetch_current_datetime_live}


# The test class name needs to start with "Test" to get collected by pytest
class TestAgentClientAsync(TestAgentClientBase):

    # helper function: create client using environment variables
    def create_client(self, by_endpoint=False, **kwargs) -> AgentsClient:
        # fetch environment variables
        endpoint = kwargs.pop("azure_ai_agents_tests_project_connection_string")
        if by_endpoint:
            endpoint = kwargs.pop("azure_ai_agents_tests_project_endpoint")
        credential = self.get_credential(AgentsClient, is_async=False)

        # create and return client
        client = AgentsClient(
            endpoint=endpoint,
            credential=credential,
        )

        return client

    def _get_data_file(self) -> str:
        """Return the test file name."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data", "product_info_1.md")

    # for debugging purposes: if a test fails and its agent has not been deleted, it will continue to show up in the agents list
    """
    # NOTE: this test should not be run against a shared resource, as it will delete all agents
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_clear_client(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

        # clear agent list
        agents = await client.list_agents().data
        for agent in agents:
            await client.delete_agent(agent.id)
        assert client.list_agents().data.__len__() == 0

        # close client
        await client.close()
    """

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - agent APIs
    #
    # **********************************************************************************

    # test client creation
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_client(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AgentsClient)
        print("Created client")

        # close client
        await client.close()

    # test agent creation and deletion
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_delete_agent(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test agent creation with tools
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_agent_with_tools(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            print("Created client")

            # initialize agent functions
            functions = FunctionTool(functions=user_functions_recording)

            # create agent with tools
            agent = await client.create_agent(
                model="gpt-4o",
                name="my-agent",
                instructions="You are helpful agent",
                tools=functions.definitions,
            )
            assert agent.id
            print("Created agent, agent ID", agent.id)
            assert agent.tools
            assert agent.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
            print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test update agent without body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_agent(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            print("Created client")

            # create body for agent
            body = {"name": "my-agent", "model": "gpt-4o", "instructions": "You are helpful agent"}

            # create agent
            agent = await client.create_agent(body=body)
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # update agent and confirm changes went through
            agent = await client.update_agent(agent.id, name="my-agent2")
            assert agent.name
            assert agent.name == "my-agent2"

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test update agent with body: JSON
    @agentClientPreparer()
    @pytest.mark.skip("Overload performs inconsistently.")
    @recorded_by_proxy_async
    async def test_update_agent_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create body for agent
            body = {"name": "my-agent", "model": "gpt-4o", "instructions": "You are helpful agent"}

            # create agent
            agent = await client.create_agent(body=body)
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create body for agent
            body2 = {"name": "my-agent2", "instructions": "You are helpful agent"}

            # update agent and confirm changes went through
            agent = await client.update_agent(agent.id, body=body2)
            assert agent.name
            assert agent.name == "my-agent2"

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # NOTE update_agent with overloads isn't working
    # test update agent with body: IO[bytes]
    @agentClientPreparer()
    @pytest.mark.skip("Overload performs inconsistently.")
    @recorded_by_proxy_async
    async def test_update_agent_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id

            # create body for agent
            body = {"name": "my-agent2", "instructions": "You are helpful agent"}
            binary_body = json.dumps(body).encode("utf-8")

            # update agent and confirm changes went through
            agent = await client.update_agent(agent.id, body=io.BytesIO(binary_body))
            assert agent.name
            assert agent.name == "my-agent2"

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    """
    DISABLED: can't perform consistently on shared resource
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_agent_list(self, **kwargs):
        # create client and ensure there are no previous agents
        client = self.create_client(**kwargs)
        list_length = await client.list_agents().data.__len__()

        # create agent and check that it appears in the list
       agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent"
            )
        assert client.list_agents().data.__len__() == list_length + 1
        assert client.list_agents().data[0].id == agent.id

        # create second agent and check that it appears in the list
        agent2 = await client.create_agent(model="gpt-4o", name="my-agent2", instructions="You are helpful agent")
        assert client.list_agents().data.__len__() == list_length + 2
        assert client.list_agents().data[0].id == agent.id or client.list_agents().data[1].id == agent.id

        # delete agents and check list
        await client.delete_agent(agent.id)
        assert client.list_agents().data.__len__() == list_length + 1
        assert client.list_agents().data[0].id == agent2.id

        client.delete_agent(agent2.id)
        assert client.list_agents().data.__len__() == list_length
        print("Deleted agents")

        # close client
        await client.close()
        """

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - Thread APIs
    #
    # **********************************************************************************

    # test creating thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert isinstance(thread, AgentThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test creating thread with no body
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create metadata for thread
            metadata = {"key1": "value1", "key2": "value2"}

            # create thread
            thread = await client.threads.create(metadata=metadata)
            assert isinstance(thread, AgentThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # close client
            print("Deleted agent")
        await client.close()

    # test creating thread with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create body for thread
            body = {
                "metadata": {"key1": "value1", "key2": "value2"},
            }

            # create thread
            thread = await client.threads.create(body=body)
            assert isinstance(thread, AgentThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # close client
            print("Deleted agent")
        await client.close()

    # test creating thread with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create body for thread
            body = {
                "metadata": {"key1": "value1", "key2": "value2"},
            }
            binary_body = json.dumps(body).encode("utf-8")

            # create thread
            thread = await client.threads.create(body=io.BytesIO(binary_body))
            assert isinstance(thread, AgentThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # close client
            print("Deleted agent")
        await client.close()

    # test getting thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_get_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # get thread
            thread2 = await client.threads.get(thread.id)
            assert thread2.id
            assert thread.id == thread2.id
            print("Got thread, thread ID", thread2.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test updating thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # update thread
            thread = await client.threads.update(thread.id, metadata={"key1": "value1", "key2": "value2"})
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test updating thread without body
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # set metadata
            metadata = {"key1": "value1", "key2": "value2"}

            # create thread
            thread = await client.threads.create(metadata=metadata)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # set metadata
            metadata2 = {"key1": "value1", "key2": "newvalue2"}

            # update thread
            thread = await client.threads.update(thread.id, metadata=metadata2)
            assert thread.metadata == {"key1": "value1", "key2": "newvalue2"}

        # close client
        await client.close()

    # test updating thread with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # set metadata
            body = {"metadata": {"key1": "value1", "key2": "value2"}}

            # update thread
            thread = await client.threads.update(thread.id, body=body)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test updating thread with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # set metadata
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # update thread
            thread = await client.threads.update(thread.id, body=io.BytesIO(binary_body))
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test deleting thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_delete_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            # assert isinstance(thread, AgentThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # delete thread
            await client.threads.delete(thread.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Message APIs
    # #
    # # **********************************************************************************

    # test creating message in a thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_message(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test creating message in a thread with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_message_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for message
            body = {"role": "user", "content": "Hello, tell me a joke"}

            # create message
            message = await client.messages.create(thread_id=thread.id, body=body)
            assert message.id
            print("Created message, message ID", message.id)

        # close client
        await client.close()

    # test creating message in a thread with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_message_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for message
            body = {"role": "user", "content": "Hello, tell me a joke"}
            binary_body = json.dumps(body).encode("utf-8")

            # create message
            message = await client.messages.create(thread_id=thread.id, body=io.BytesIO(binary_body))
            assert message.id
            print("Created message, message ID", message.id)

        # close client
        await client.close()

    # test creating multiple messages in a thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_multiple_messages(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create messages
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)
            message2 = await client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me another joke"
            )
            assert message2.id
            print("Created message, message ID", message2.id)
            message3 = await client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me a third joke"
            )
            assert message3.id
            print("Created message, message ID", message3.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test listing messages in a thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_list_messages(self, **kwargs):
        # create client
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # check that initial message list is empty
            messages0 = [m async for m in client.messages.list(thread_id=thread.id)]
            print(messages0)
            assert len(messages0) == 0

            # create messages and check message list for each one
            message1 = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message1.id
            print("Created message, message ID", message1.id)
            messages1 = [m async for m in client.messages.list(thread_id=thread.id)]
            assert len(messages1) == 1
            assert messages1[0].id == message1.id

            message2 = await client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me another joke"
            )
            assert message2.id
            print("Created message, message ID", message2.id)
            messages2 = [m async for m in client.messages.list(thread_id=thread.id)]
            assert len(messages2) == 2
            assert any(msg.id == message2.id for msg in messages2)

            message3 = await client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me a third joke"
            )
            assert message3.id
            print("Created message, message ID", message3.id)
            messages3 = [message async for message in client.messages.list(thread_id=thread.id)]
            assert len(messages3) == 3
            assert any(msg.id == message3.id for msg in messages3)
            assert messages3[0].id == message3.id or messages3[1].id == message3.id or messages3[2].id == message3.id

            await client.messages.delete(thread_id=thread.id, message_id=message3.id)
            messages4 = [message async for message in client.messages.list(thread_id=thread.id)]
            assert len(messages4) == 2
            assert not any(msg.id == message3.id for msg in messages4)

            # Check that we can add messages after deletion
            message3 = await client.messages.create(thread_id=thread.id, role="user", content="Bar")
            assert message3.id
            messages5 = [message async for message in client.messages.list(thread_id=thread.id)]
            assert len(messages5) == 3
            assert any(msg.id == message3.id for msg in messages5)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test getting message in a thread
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_get_message(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # get message
            message2 = await client.messages.get(thread_id=thread.id, message_id=message.id)
            assert message2.id
            assert message.id == message2.id
            print("Got message, message ID", message.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test updating message in a thread without body
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_message(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # update message
            message = await client.messages.update(
                thread_id=thread.id, message_id=message.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test updating message in a thread with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_message_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # create body for message
            body = {"metadata": {"key1": "value1", "key2": "value2"}}

            # update message
            message = await client.messages.update(thread_id=thread.id, message_id=message.id, body=body)
            assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test updating message in a thread with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_message_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # create body for message
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # update message
            message = await client.messages.update(
                thread_id=thread.id, message_id=message.id, body=io.BytesIO(binary_body)
            )
            assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Run APIs
    # #
    # # **********************************************************************************

    # test creating run
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test creating run without body
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.runs.create(
                thread_id=thread.id, agent_id=agent.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test creating run with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for run
            body = {"assistant_id": agent.id, "metadata": {"key1": "value1", "key2": "value2"}}

            # create run
            run = await client.runs.create(thread_id=thread.id, body=body)
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test creating run with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for run
            body = {"assistant_id": agent.id, "metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # create run
            run = await client.runs.create(thread_id=thread.id, body=io.BytesIO(binary_body))
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test getting run
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_get_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # get run
            run2 = await client.runs.get(thread_id=thread.id, run_id=run.id)
            assert run2.id
            assert run.id == run2.id
            print("Got run, run ID", run2.id)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test sucessful run status
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_run_status(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # check status
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "cancelling",
                "cancelled",
                "failed",
                "completed",
                "expired",
            ]
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
                print("Run status:", run.status)

            assert run.status in ["cancelled", "failed", "completed", "expired"]
            print("Run completed with status:", run.status)

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    """
    # TODO another, but check that the number of runs decreases after cancelling runs
    # TODO can each thread only support one run?
    # test listing runs
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_list_runs(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

        # create agent
        agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent"
            )
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = await client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check list for current runs
        runs0 = await client.runs.list(thread_id=thread.id)
        assert runs0.data.__len__() == 0

        # create run and check list
        run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)
        runs1 = await client.runs.list(thread_id=thread.id)
        assert runs1.data.__len__() == 1
        assert runs1.data[0].id == run.id

        # create second run
        run2 = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
        assert run2.id
        print("Created run, run ID", run2.id)
        runs2 = await client.runs.list(thread_id=thread.id)
        assert runs2.data.__len__() == 2
        assert runs2.data[0].id == run2.id or runs2.data[1].id == run2.id

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        await client.close()
    """

    # test updating run
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(self._sleep_time(5))
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            run = await client.runs.update(
                thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.metadata == {"key1": "value1", "key2": "value2"}

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test updating run without body
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.runs.create(
                thread_id=thread.id, agent_id=agent.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(self._sleep_time(5))
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            run = await client.runs.update(
                thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "newvalue2"}
            )
            assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test updating run with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.runs.create(
                thread_id=thread.id, agent_id=agent.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # create body for run
            body = {"metadata": {"key1": "value1", "key2": "newvalue2"}}

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(self._sleep_time(5))
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            run = await client.runs.update(thread_id=thread.id, run_id=run.id, body=body)
            assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test updating run with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.runs.create(
                thread_id=thread.id, agent_id=agent.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # create body for run
            body = {"metadata": {"key1": "value1", "key2": "newvalue2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(self._sleep_time(5))
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            run = await client.runs.update(thread_id=thread.id, run_id=run.id, body=io.BytesIO(binary_body))
            assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test submitting tool outputs to run
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_submit_tool_outputs_to_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # Initialize agent tools
            functions = FunctionTool(user_functions_recording)
            # TODO add files for code interpreter tool
            # code_interpreter = CodeInterpreterTool()

            toolset = ToolSet()
            toolset.add(functions)
            # toolset.add(code_interpreter)

            # create agent
            agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
            )
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, what time is it?")
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # check that tools are uploaded
            assert run.tools
            assert run.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
            print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])

            # check status
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "cancelling",
                "cancelled",
                "failed",
                "completed",
                "expired",
            ]
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)

                # check if tools are needed
                if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                    print("Requires action: submit tool outputs")
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await client.runs.cancel(thread_id=thread.id, run_id=run.id)
                        break

                    # submit tool outputs to run
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                    print("Tool outputs:", tool_outputs)
                    if tool_outputs:
                        await client.runs.submit_tool_outputs(
                            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                        )

                print("Current run status:", run.status)

            print("Run completed with status:", run.status)

            # check that messages used the tool
            messages = [m async for m in client.messages.list(thread_id=thread.id, run_id=run.id)]
            tool_message = messages[0].content[0].text.value
            hour12 = time.strftime("%H")
            hour24 = time.strftime("%I")
            minute = time.strftime("%M")
            assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
            print("Used tool_outputs")

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test submitting tool outputs to run with body: JSON
    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_submit_tool_outputs_to_run_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # Initialize agent tools
            functions = FunctionTool(user_functions_recording)
            toolset = ToolSet()
            toolset.add(functions)

            # create agent
            agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
            )
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, what time is it?")
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # check that tools are uploaded
            assert run.tools
            assert run.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
            print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])

            # check status
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "cancelling",
                "cancelled",
                "failed",
                "completed",
                "expired",
            ]
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)

                # check if tools are needed
                if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                    print("Requires action: submit tool outputs")
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await client.runs.cancel(thread_id=thread.id, run_id=run.id)
                        break

                    # submit tool outputs to run
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                    print("Tool outputs:", tool_outputs)
                    if tool_outputs:
                        body = {"tool_outputs": tool_outputs}
                        await client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, body=body)

                print("Current run status:", run.status)

            print("Run completed with status:", run.status)

            # check that messages used the tool
            messages = [m async for m in client.messages.list(thread_id=thread.id, run_id=run.id)]
            tool_message = messages[0].content[0].text.value
            # hour12 = time.strftime("%H")
            # hour24 = time.strftime("%I")
            # minute = time.strftime("%M")
            # assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
            recorded_time = "12:30"
            assert recorded_time in tool_message
            print("Used tool_outputs")

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test submitting tool outputs to run with body: IO[bytes]
    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_submit_tool_outputs_to_run_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # Initialize agent tools
            functions = FunctionTool(user_functions_recording)
            toolset = ToolSet()
            toolset.add(functions)

            # create agent
            agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
            )
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, what time is it?")
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # check that tools are uploaded
            assert run.tools
            assert run.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
            print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])

            # check status
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "cancelling",
                "cancelled",
                "failed",
                "completed",
                "expired",
            ]
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)

                # check if tools are needed
                if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                    print("Requires action: submit tool outputs")
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        client.runs.cancel(thread_id=thread.id, run_id=run.id)
                        break

                    # submit tool outputs to run
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                    print("Tool outputs:", tool_outputs)
                    if tool_outputs:
                        body = {"tool_outputs": tool_outputs}
                        binary_body = json.dumps(body).encode("utf-8")
                        await client.runs.submit_tool_outputs(
                            thread_id=thread.id, run_id=run.id, body=io.BytesIO(binary_body)
                        )

                print("Current run status:", run.status)

            print("Run completed with status:", run.status)

            # check that messages used the tool
            messages = [m async for m in client.messages.list(thread_id=thread.id, run_id=run.id)]
            tool_message = messages[0].content[0].text.value
            # hour12 = time.strftime("%H")
            # hour24 = time.strftime("%I")
            # minute = time.strftime("%M")
            # assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
            recorded_time = "12:30"
            assert recorded_time in tool_message
            print("Used tool_outputs")

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    """
    # DISABLED: rewrite to ensure run is not complete when cancel_run is called
    # test cancelling run
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_cancel_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

        # create agent
        agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent"
            )
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = await client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check that tools are uploaded
        assert run.tools
        assert run.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
        print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])

        # check status
        assert run.status in [
            "queued",
            "in_progress",
            "requires_action",
            "cancelling",
            "cancelled",
            "failed",
            "completed",
            "expired",
        ]
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(self._sleep_time())
            run = await client.runs.get(thread_id=thread.id, run_id=run.id)

            # check if tools are needed
            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                print("Requires action: submit tool outputs")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print(
                        "No tool calls provided - cancelling run"
                    )  # TODO how can i make sure that it wants tools? should i have some kind of error message?
                    await client.runs.cancel(thread_id=thread.id, run_id=run.id)
                    break

                # submit tool outputs to run
                tool_outputs = toolset.execute_tool_calls(tool_calls)  # TODO issue somewhere here
                print("Tool outputs:", tool_outputs)
                if tool_outputs:
                    await client.runs.submit_tool_outputs(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        # check that messages used the tool
        messages = await client.messages.list(thread_id=thread.id, run_id=run.id)
        tool_message = messages["data"][0]["content"][0]["text"]["value"]
        hour12 = time.strftime("%H")
        hour24 = time.strftime("%I")
        minute = time.strftime("%M")
        assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
        print("Used tool_outputs")

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        await client.close()
        """

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_thread_true(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(True, True, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_thread_false(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(False, True, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_run_true(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(True, False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_run_false(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(False, False, **kwargs)

    async def _wait_for_run(self, client, run, timeout=1):
        """Wait while run will get to terminal state."""
        while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
            time.sleep(self._sleep_time(timeout))
            run = await client.runs.get(thread_id=run.thread_id, run_id=run.id)
        return run

    async def _do_test_create_parallel_thread_runs(self, use_parallel_runs, create_thread_run, **kwargs):
        """Test creation of parallel runs."""

        # create client
        client = self.create_client(
            **kwargs,
        )
        assert isinstance(client, AgentsClient)

        # Initialize agent tools
        functions = FunctionTool(functions=user_functions_recording)
        code_interpreter = CodeInterpreterTool()

        toolset = ToolSet()
        toolset.add(functions)
        toolset.add(code_interpreter)
        agent = await client.create_agent(
            model="gpt-4",
            name="my-agent",
            instructions="You are helpful agent",
            toolset=toolset,
        )
        assert agent.id

        message = ThreadMessageOptions(
            role="user",
            content="Hello, what time is it?",
        )

        if create_thread_run:
            run = await client.create_thread_and_run(
                agent_id=agent.id,
                parallel_tool_calls=use_parallel_runs,
            )
            run = await self._wait_for_run(client, run)
        else:
            thread = await client.threads.create(messages=[message])
            assert thread.id

            run = await client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
                parallel_tool_calls=use_parallel_runs,
                polling_interval=self._sleep_time(),
            )
        assert run.id
        assert run.status == RunStatus.COMPLETED, run.last_error.message
        assert run.parallel_tool_calls == use_parallel_runs

        await client.delete_agent(agent.id)
        messages = [m async for m in client.messages.list(thread_id=run.thread_id)]
        assert messages, "The data from the agent was not received."

    """
    # DISABLED: rewrite to ensure run is not complete when cancel_run is called
    # test cancelling run
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_cancel_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AgentsClient)

        # create agent
        agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.messages.create(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.runs.create(thread_id=thread.id, agent_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check status and cancel
        assert run.status in ["queued", "in_progress", "requires_action"]
        client.runs.cancel(thread_id=thread.id, run_id=run.id)

        while run.status in ["queued", "cancelling"]:
            time.sleep(self._sleep_time())
            run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            print("Current run status:", run.status)
        assert run.status == "cancelled"
        print("Run cancelled")

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        await client.close()
        """

    # test create thread and run
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_and_run(self, **kwargs):
        time.sleep(self._sleep_time(26))
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread and run
            run = await client.create_thread_and_run(agent_id=agent.id)
            assert run.id
            assert run.thread_id
            print("Created run, run ID", run.id)

            # get thread
            thread = await client.threads.get(run.thread_id)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # check status
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "cancelling",
                "cancelled",
                "failed",
                "completed",
                "expired",
            ]
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
                # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
                print("Run status:", run.status)

            assert run.status == "completed"
            print("Run completed")

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")

    # test create thread and run with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_and_run_with_body(self, **kwargs):
        # time.sleep(self._sleep_time(26))
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create body for thread
            body = {
                "assistant_id": agent.id,
                "metadata": {"key1": "value1", "key2": "value2"},
            }

            # create thread and run
            run = await client.create_thread_and_run(body=body)
            assert run.id
            assert run.thread_id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # get thread
            thread = await client.threads.get(run.thread_id)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # check status
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "cancelling",
                "cancelled",
                "failed",
                "completed",
                "expired",
            ]
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
                # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
                print("Run status:", run.status)

            assert run.status == "completed"
            print("Run completed")

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    # test create thread and run with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_and_run_with_iobytes(self, **kwargs):
        # time.sleep(self._sleep_time(26))
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create body for thread
            body = {
                "assistant_id": agent.id,
                "metadata": {"key1": "value1", "key2": "value2"},
            }
            binary_body = json.dumps(body).encode("utf-8")

            # create thread and run
            run = await client.create_thread_and_run(body=io.BytesIO(binary_body))
            assert run.id
            assert run.thread_id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # get thread
            thread = await client.threads.get(run.thread_id)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # check status
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "cancelling",
                "cancelled",
                "failed",
                "completed",
                "expired",
            ]
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
                # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
                print("Run status:", run.status)

            assert run.status == "completed"
            print("Run completed")

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    """
    # test listing run steps
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_list_run_step(self, **kwargs):

        time.sleep(self._sleep_time(50))
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent"
            )
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(
                thread_id=thread.id, role="user", content="Hello, what time is it?"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            steps = await client.run_steps.list(thread_id=thread.id, run_id=run.id)
            # commenting assertion out below, do we know exactly when run starts?
            # assert steps['data'].__len__() == 0

            # check status
            assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
                assert run.status in [
                    "queued",
                    "in_progress",
                    "requires_action",
                    "completed",
                ]
                print("Run status:", run.status)
                steps = await client.run_steps.list(
                    thread_id=thread.id, run_id=run.id
                )
            assert steps["data"].__len__() > 0

            assert run.status == "completed"
            print("Run completed")

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()
    """

    # test getting run step
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_get_run_step(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create agent
            agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = await client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.messages.create(
                thread_id=thread.id, role="user", content="Hello, can you tell me a joke?"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            if run.status == "failed":
                assert run.last_error
                print(run.last_error)
                print("FAILED HERE")

            # check status
            assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = await client.runs.get(thread_id=thread.id, run_id=run.id)
                if run.status == "failed":
                    assert run.last_error
                    print(run.last_error)
                    print("FAILED HERE")
                assert run.status in [
                    "queued",
                    "in_progress",
                    "requires_action",
                    "completed",
                ]
                print("Run status:", run.status)

            # list steps, check that get_run_step works with first step_id
            steps = [s async for s in client.run_steps.list(thread_id=thread.id, run_id=run.id)]

            assert steps, "No run steps returned."
            step = steps[0]
            get_step = await client.run_steps.get(thread_id=thread.id, run_id=run.id, step_id=step.id)
            assert step == get_step

            # delete agent and close client
            await client.delete_agent(agent.id)
            print("Deleted agent")
        await client.close()

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_azure(self, **kwargs):
        """Test the agent with vector store creation."""
        await self._do_test_create_vector_store(streaming=False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_file_id(self, **kwargs):
        """Test the agent with vector store creation."""
        await self._do_test_create_vector_store(streaming=False, file_path=self._get_data_file(), **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_azure_streaming(self, **kwargs):
        """Test the agent with vector store creation."""
        await self._do_test_create_vector_store(streaming=True, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_file_id_streaming(self, **kwargs):
        """Test the agent with vector store creation."""
        await self._do_test_create_vector_store(streaming=True, file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_vector_store(self, streaming, **kwargs):
        """Test the agent with vector store creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)
        file_ids = [file_id] if file_id else None
        if file_ids:
            ds = None
        else:
            ds = [
                VectorStoreDataSource(
                    asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                    asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
                )
            ]
        vector_store = await ai_client.vector_stores.create_and_poll(
            file_ids=file_ids, data_sources=ds, name="my_vectorstore", polling_interval=self._sleep_time()
        )
        assert vector_store.id
        await self._test_file_search(ai_client, vector_store, file_id, streaming)
        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_file_id(self, **kwargs):
        """Test adding single file to vector store withn file ID."""
        await self._do_test_create_vector_store_add_file(streaming=False, file_path=self._get_data_file(), **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_azure(self, **kwargs):
        """Test adding single file to vector store with azure asset ID."""
        await self._do_test_create_vector_store_add_file(streaming=False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_file_id_streaming(self, **kwargs):
        """Test adding single file to vector store withn file ID."""
        await self._do_test_create_vector_store_add_file(streaming=True, file_path=self._get_data_file(), **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_azure_streaming(self, **kwargs):
        """Test adding single file to vector store with azure asset ID."""
        await self._do_test_create_vector_store_add_file(streaming=True, **kwargs)

    async def _do_test_create_vector_store_add_file(self, streaming, **kwargs):
        """Test adding single file to vector store."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)
        if file_id:
            ds = None
        else:
            ds = VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
        vector_store = await ai_client.vector_stores.create_and_poll(
            file_ids=[], name="sample_vector_store", polling_interval=self._sleep_time()
        )
        assert vector_store.id
        vector_store_file = await ai_client.vector_store_files.create(
            vector_store_id=vector_store.id, data_source=ds, file_id=file_id
        )
        assert vector_store_file.id
        await self._test_file_search(ai_client, vector_store, file_id, streaming)
        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_file_ids(self, **kwargs):
        """Test adding multiple files to vector store with file IDs."""
        await self._do_test_create_vector_store_batch(streaming=False, file_path=self._get_data_file(), **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_azure(self, **kwargs):
        """Test adding multiple files to vector store with azure asset IDs."""
        await self._do_test_create_vector_store_batch(streaming=False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_file_ids_streaming(self, **kwargs):
        """Test adding multiple files to vector store with file IDs."""
        await self._do_test_create_vector_store_batch(streaming=True, file_path=self._get_data_file(), **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_azure_streaming(self, **kwargs):
        """Test adding multiple files to vector store with azure asset IDs."""
        await self._do_test_create_vector_store_batch(streaming=True, **kwargs)

    async def _do_test_create_vector_store_batch(self, streaming, **kwargs):
        """Test the agent with vector store creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)
        if file_id:
            file_ids = [file_id]
            ds = None
        else:
            file_ids = None
            ds = [
                VectorStoreDataSource(
                    asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                    asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
                )
            ]
        vector_store = await ai_client.vector_stores.create_and_poll(
            file_ids=[], name="sample_vector_store", polling_interval=self._sleep_time()
        )
        assert vector_store.id
        vector_store_file_batch = await ai_client.vector_store_file_batches.create_and_poll(
            vector_store_id=vector_store.id, data_sources=ds, file_ids=file_ids, polling_interval=self._sleep_time()
        )
        assert vector_store_file_batch.id
        await self._test_file_search(ai_client, vector_store, file_id, streaming)

    async def _test_file_search(
        self, ai_client: AgentsClient, vector_store: VectorStore, file_id: str, streaming: bool
    ) -> None:
        """Test the file search"""
        file_search = FileSearchTool(vector_store_ids=[vector_store.id])
        agent = await ai_client.create_agent(
            model="gpt-4",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        assert agent.id
        thread = await ai_client.threads.create()
        assert thread.id
        # create message
        message = await ai_client.messages.create(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        if streaming:
            thread_run = None
            async with await ai_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
                async for _, event_data, _ in stream:
                    if isinstance(event_data, ThreadRun):
                        thread_run = event_data
                    elif (
                        isinstance(event_data, RunStepDeltaChunk)
                        and isinstance(event_data.delta.step_details, RunStepDeltaToolCallObject)
                        and event_data.delta.step_details.tool_calls
                    ):
                        assert isinstance(
                            event_data.delta.step_details.tool_calls[0].file_search, RunStepFileSearchToolCallResults
                        )
            assert thread_run is not None
            run = await ai_client.runs.get(thread_id=thread_run.thread_id, run_id=thread_run.id)
            assert run is not None
        else:
            run = await ai_client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
            )
        await ai_client.vector_stores.delete(vector_store.id)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
        assert messages
        await self._remove_file_maybe(file_id, ai_client)
        # delete agent and close client
        await ai_client.delete_agent(agent.id)
        print("Deleted agent")
        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_message_attachement_azure(self, **kwargs):
        """Test message attachment with azure ID."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_message_attachment(data_sources=[ds], **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_message_attachement_file_ids(self, **kwargs):
        """Test message attachment with file ID."""
        await self._do_test_message_attachment(file_path=self._get_data_file(), **kwargs)

    async def _do_test_message_attachment(self, **kwargs):
        """Test agent with the message attachment."""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)

        # Create agent with file search tool
        agent = await ai_client.create_agent(
            model="gpt-4-1106-preview",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
        )
        assert agent.id, "Agent was not created"

        thread = await ai_client.threads.create()
        assert thread.id, "The thread was not created."

        # Create a message with the file search attachment
        # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
        attachment = MessageAttachment(
            file_id=file_id,
            data_sources=kwargs.get("data_sources"),
            tools=[
                FileSearchTool().definitions[0],
                CodeInterpreterTool().definitions[0],
            ],
        )
        message = await ai_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="What does the attachment say?",
            attachments=[attachment],
        )
        assert message.id, "The message was not created."

        run = await ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.id, "The run was not created."
        await self._remove_file_maybe(file_id, ai_client)
        await ai_client.delete_agent(agent.id)

        messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
        assert messages, "No messages were created"

        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("Failing with Http Response Errors.")
    @recorded_by_proxy_async
    async def test_vector_store_threads_file_search_azure(self, **kwargs):
        """Test file search when azure asset ids are supplied during thread creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        ds = [
            VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
        ]
        fs = FileSearchToolResource(
            vector_stores=[
                VectorStoreConfigurations(
                    store_name="my_vector_store",
                    store_configuration=VectorStoreConfiguration(data_sources=ds),
                )
            ]
        )
        file_search = FileSearchTool()
        agent = await ai_client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        assert agent.id

        thread = await ai_client.threads.create(tool_resources=ToolResources(file_search=fs))
        assert thread.id
        # create message
        message = await ai_client.messages.create(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
        assert messages
        await ai_client.delete_agent(agent.id)
        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy_async
    async def test_create_agent_with_interpreter_azure(self, **kwargs):
        """Test Create agent with code interpreter with azure asset ids."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_create_agent_with_interpreter(data_sources=[ds], **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_agent_with_interpreter_file_ids(self, **kwargs):
        """Test Create agent with code interpreter with file IDs."""
        await self._do_test_create_agent_with_interpreter(file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_agent_with_interpreter(self, **kwargs):
        """Test create agent with code interpreter and project asset id"""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        code_interpreter = CodeInterpreterTool()

        file_id = None
        if "file_path" in kwargs:
            file = await ai_client.files.upload_and_poll(file_path=kwargs["file_path"], purpose=FilePurpose.AGENTS)
            assert file.id, "The file was not uploaded."
            file_id = file.id

        cdr = CodeInterpreterToolResource(
            file_ids=[file_id] if file_id else None,
            data_sources=kwargs.get("data_sources"),
        )
        tr = ToolResources(code_interpreter=cdr)
        # notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
        agent = await ai_client.create_agent(
            model="gpt-4-1106-preview",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=code_interpreter.definitions,
            tool_resources=tr,
        )
        assert agent.id, "Agent was not created"

        thread = await ai_client.threads.create()
        assert thread.id, "The thread was not created."

        message = await ai_client.messages.create(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.id, "The run was not created."
        await self._remove_file_maybe(file_id, ai_client)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        await ai_client.delete_agent(agent.id)
        messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
        assert messages
        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy_async
    async def test_create_thread_with_interpreter_azure(self, **kwargs):
        """Test Create agent with code interpreter with azure asset ids."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_create_thread_with_interpreter(data_sources=[ds], **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_thread_with_interpreter_file_ids(self, **kwargs):
        """Test Create agent with code interpreter with file IDs."""
        await self._do_test_create_thread_with_interpreter(file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_thread_with_interpreter(self, **kwargs):
        """Test create agent with code interpreter and project asset id"""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        code_interpreter = CodeInterpreterTool()

        file_id = None
        if "file_path" in kwargs:
            file = await ai_client.files.upload_and_poll(file_path=kwargs["file_path"], purpose=FilePurpose.AGENTS)
            assert file.id, "The file was not uploaded."
            file_id = file.id

        cdr = CodeInterpreterToolResource(
            file_ids=[file_id] if file_id else None,
            data_sources=kwargs.get("data_sources"),
        )
        tr = ToolResources(code_interpreter=cdr)
        # notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
        agent = await ai_client.create_agent(
            model="gpt-4-1106-preview",
            name="my-agent",
            instructions="You are helpful agent",
            tools=code_interpreter.definitions,
        )
        assert agent.id, "Agent was not created"

        thread = await ai_client.threads.create(tool_resources=tr)
        assert thread.id, "The thread was not created."

        message = await ai_client.messages.create(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.id, "The run was not created."
        await self._remove_file_maybe(file_id, ai_client)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        await ai_client.delete_agent(agent.id)
        messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
        assert messages
        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("Failing with Http Response Errors.")
    @recorded_by_proxy_async
    async def test_create_agent_with_inline_vs_azure(self, **kwargs):
        """Test creation of asistant with vector store inline."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        ds = [
            VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
        ]
        fs = FileSearchToolResource(
            vector_stores=[
                VectorStoreConfigurations(
                    store_name="my_vector_store",
                    store_configuration=VectorStoreConfiguration(data_sources=ds),
                )
            ]
        )
        file_search = FileSearchTool()
        agent = await ai_client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=ToolResources(file_search=fs),
        )
        assert agent.id

        thread = await ai_client.threads.create()
        assert thread.id
        # create message
        message = await ai_client.messages.create(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
        assert messages
        await ai_client.delete_agent(agent.id)
        await ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy_async
    async def test_create_attachment_in_thread_azure(self, **kwargs):
        """Create thread with message attachment inline with azure asset IDs."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_create_attachment_in_thread_azure(data_sources=[ds], **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_attachment_in_thread_file_ids(self, **kwargs):
        """Create thread with message attachment inline with azure asset IDs."""
        await self._do_test_create_attachment_in_thread_azure(file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_attachment_in_thread_azure(self, **kwargs):
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)

        file_search = FileSearchTool()
        agent = await ai_client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
        )
        assert agent.id

        # create message
        attachment = MessageAttachment(
            file_id=file_id,
            data_sources=kwargs.get("data_sources"),
            tools=[
                FileSearchTool().definitions[0],
                CodeInterpreterTool().definitions[0],
            ],
        )
        message = ThreadMessageOptions(
            role="user",
            content="What does the attachment say?",
            attachments=[attachment],
        )
        thread = await ai_client.threads.create(messages=[message])
        assert thread.id

        run = await ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
        assert messages
        await ai_client.delete_agent(agent.id)
        await ai_client.close()

    def _get_azure_function_tool(self, storage_queue: str) -> AzureFunctionTool:
        """Helper method to get an AzureFunctionTool."""
        return AzureFunctionTool(
            name="foo",
            description="Get answers from the foo bot.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The question to ask."},
                    "outputqueueuri": {"type": "string", "description": "The full output queue uri."},
                },
            },
            input_queue=AzureFunctionStorageQueue(
                queue_name="azure-function-foo-input",
                storage_service_endpoint=storage_queue,
            ),
            output_queue=AzureFunctionStorageQueue(
                queue_name="azure-function-tool-output",
                storage_service_endpoint=storage_queue,
            ),
        )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_azure_function_call(self, **kwargs):
        """Test calling Azure functions."""
        storage_queue = kwargs["azure_ai_agents_tests_storage_queue"]
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            azure_function_tool = self._get_azure_function_tool(storage_queue)

            await self._do_test_tool(
                client=client,
                model_name="gpt-4o",
                tool_to_test=azure_function_tool,
                instructions=(
                    "You are a helpful support agent. Use the provided function any "
                    "time the prompt contains the string 'What would foo say?'. When "
                    "you invoke the function, ALWAYS specify the output queue uri parameter as "
                    f"'{storage_queue}/azure-function-tool-output'"
                    '. Always responds with "Foo says" and then the response from the tool.'
                ),
                prompt="What is the most prevalent element in the universe? What would foo say?",
                expected_class=RunStepAzureFunctionToolCall,
                agent_message_regex="bar",
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_azure_function_call_streaming(self, **kwargs):
        """Test calling Azure functions in streaming scenarios."""
        storage_queue = kwargs["azure_ai_agents_tests_storage_queue"]
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            azure_function_tool = self._get_azure_function_tool(storage_queue)

            await self._do_test_tool_streaming(
                client=client,
                model_name="gpt-4o",
                tool_to_test=azure_function_tool,
                instructions=(
                    "You are a helpful support agent. Use the provided function any "
                    "time the prompt contains the string 'What would foo say?'. When "
                    "you invoke the function, ALWAYS specify the output queue uri parameter as "
                    f"'{storage_queue}/azure-function-tool-output'"
                    '. Always responds with "Foo says" and then the response from the tool.'
                ),
                prompt="What is the most prevalent element in the universe? What would foo say?",
                expected_delta_class=RunStepDeltaAzureFunctionToolCall,
                agent_message_regex="bar",
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_client_with_thread_messages(self, **kwargs):
        """Test agent with thread messages."""
        async with self.create_client(**kwargs) as client:

            # [START create_agent]
            agent = await client.create_agent(
                model="gpt-4",
                name="my-agent",
                instructions="You are helpful agent",
            )
            assert agent.id, "The agent was not created."
            thread = await client.threads.create()
            assert thread.id, "Thread was not created"

            message = await client.messages.create(
                thread_id=thread.id, role="user", content="What is the equation of light energy?"
            )
            assert message.id, "The message was not created."

            additional_messages = [
                ThreadMessageOptions(role=MessageRole.AGENT, content="E=mc^2"),
                ThreadMessageOptions(role=MessageRole.USER, content="What is the impedance formula?"),
            ]
            run = await client.runs.create(
                thread_id=thread.id, agent_id=agent.id, additional_messages=additional_messages
            )

            # poll the run as long as run status is queued or in progress
            while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = await client.runs.get(
                    thread_id=thread.id,
                    run_id=run.id,
                )
            assert run.status in RunStatus.COMPLETED, run.last_error

            await client.delete_agent(agent.id)
            messages = [m async for m in client.messages.list(thread_id=thread.id)]
            assert messages, "The data from the agent was not received."

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_include_file_search_results_no_stream(self, **kwargs):
        """Test using include_file_search."""
        await self._do_test_include_file_search_results(use_stream=False, include_content=True, **kwargs)
        await self._do_test_include_file_search_results(use_stream=False, include_content=False, **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_include_file_search_results_stream(self, **kwargs):
        """Test using include_file_search with streaming."""
        await self._do_test_include_file_search_results(use_stream=True, include_content=True, **kwargs)
        await self._do_test_include_file_search_results(use_stream=True, include_content=False, **kwargs)

    async def _do_test_include_file_search_results(self, use_stream, include_content, **kwargs):
        """Run the test with file search results."""
        async with self.create_client(**kwargs) as ai_client:
            ds = [
                VectorStoreDataSource(
                    asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                    asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
                )
            ]
            vector_store = await ai_client.vector_stores.create_and_poll(
                file_ids=[], data_sources=ds, name="my_vectorstore", polling_interval=self._sleep_time()
            )
            # vector_store = await ai_client.vector_stores.get('vs_M9oxKG7JngORHcYNBGVZ6Iz3')
            assert vector_store.id

            file_search = FileSearchTool(vector_store_ids=[vector_store.id])
            agent = await ai_client.create_agent(
                model="gpt-4o",
                name="my-agent",
                instructions="Hello, you are helpful agent and can search information from uploaded files",
                tools=file_search.definitions,
                tool_resources=file_search.resources,
            )
            assert agent.id
            thread = await ai_client.threads.create()
            assert thread.id
            # create message
            message = await ai_client.messages.create(
                thread_id=thread.id,
                role="user",
                # content="What does the attachment say?"
                content="What Contoso Galaxy Innovations produces?",
            )
            assert message.id, "The message was not created."
            include = [RunAdditionalFieldList.FILE_SEARCH_CONTENTS] if include_content else None

            if use_stream:
                run = None
                async with await ai_client.runs.stream(
                    thread_id=thread.id, agent_id=agent.id, include=include
                ) as stream:
                    async for event_type, event_data, _ in stream:
                        if isinstance(event_data, ThreadRun):
                            run = event_data
                        elif event_type == AgentStreamEvent.THREAD_RUN_STEP_COMPLETED:
                            if isinstance(event_data.step_details, RunStepToolCallDetails):
                                self._assert_file_search_valid(event_data.step_details.tool_calls[0], include_content)
                        elif event_type == AgentStreamEvent.DONE:
                            print("Stream completed.")
                            break
            else:
                run = await ai_client.runs.create_and_process(
                    thread_id=thread.id, agent_id=agent.id, include=include, polling_interval=self._sleep_time()
                )
                assert run.status == RunStatus.COMPLETED
            assert run is not None
            steps = [s async for s in ai_client.run_steps.list(thread_id=thread.id, run_id=run.id, include=include)]
            # first (index-1) step is the tool call
            step_id = steps[1].id
            one_step = await ai_client.run_steps.get(
                thread_id=thread.id, run_id=run.id, step_id=step_id, include=include
            )
            self._assert_file_search_valid(one_step.step_details.tool_calls[0], include_content)
            self._assert_file_search_valid(steps[1].step_details.tool_calls[0], include_content)

            messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]
            assert len(messages) > 1, "No messages were returned."

            await ai_client.vector_stores.delete(vector_store.id)
            # delete agent and close client
            await ai_client.delete_agent(agent.id)
            print("Deleted agent")
            await ai_client.close()

    def _assert_file_search_valid(self, tool_call: Any, include_content: bool) -> None:
        """Test that file search result is properly populated."""
        assert isinstance(tool_call, RunStepFileSearchToolCall), f"Wrong type of tool call: {type(tool_call)}."
        assert isinstance(
            tool_call.file_search, RunStepFileSearchToolCallResults
        ), f"Wrong type of search results: {type(tool_call.file_search)}."
        assert isinstance(
            tool_call.file_search.results[0], RunStepFileSearchToolCallResult
        ), f"Wrong type of search result: {type(tool_call.file_search.results[0])}."
        assert tool_call.file_search.results
        if include_content:
            assert tool_call.file_search.results[0].content
            assert isinstance(tool_call.file_search.results[0].content[0], FileSearchToolCallContent)
            assert tool_call.file_search.results[0].content[0].type == "text"
            assert tool_call.file_search.results[0].content[0].text
        else:
            assert tool_call.file_search.results[0].content is None

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_agents_with_json_schema(self, **kwargs):
        """Test structured output from the agent."""
        async with self.create_client(**kwargs) as ai_client:
            agent = await ai_client.create_agent(
                # Note only gpt-4o-mini-2024-07-18 and
                # gpt-4o-2024-08-06 and later support structured output.
                model="gpt-4o-mini",
                name="my-agent",
                instructions="Extract the information about planets.",
                headers={"x-ms-enable-preview": "true"},
                response_format=ResponseFormatJsonSchemaType(
                    json_schema=ResponseFormatJsonSchema(
                        name="planet_mass",
                        description="Extract planet mass.",
                        schema={
                            "$defs": {
                                "Planets": {"enum": ["Earth", "Mars", "Jupyter"], "title": "Planets", "type": "string"}
                            },
                            "properties": {
                                "planet": {"$ref": "#/$defs/Planets"},
                                "mass": {"title": "Mass", "type": "number"},
                            },
                            "required": ["planet", "mass"],
                            "title": "Planet",
                            "type": "object",
                        },
                    )
                ),
            )
            assert agent.id

            thread = await ai_client.threads.create()
            assert thread.id

            message = await ai_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=("The mass of the Mars is 6.4171E23 kg"),
            )
            assert message.id

            run = await ai_client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
            )

            assert run.status == RunStatus.COMPLETED, run.last_error.message

            await ai_client.delete_agent(agent.id)

            messages = [m async for m in ai_client.messages.list(thread_id=thread.id)]

            planet_info = []
            # The messages are following in the reverse order,
            # we will iterate them and output only text contents.
            for msg in reversed(messages):
                last = msg.content[-1]
                # We will only list agent responses here.
                if isinstance(last, MessageTextContent) and msg.role == MessageRole.AGENT:
                    planet_info.append(json.loads(last.text.value))
            assert len(planet_info) == 1
            assert len(planet_info[0]) == 2
            assert planet_info[0]["mass"] == pytest.approx(6.4171e23, 1e22)
            assert planet_info[0]["planet"] == "Mars"

    async def _get_connected_agent_tool(self, client, model_name, connected_agent_name):
        """Get the connected agent tool."""
        stock_price_agent = await client.create_agent(
            model=model_name,
            name=connected_agent_name,
            instructions=(
                "Your job is to get the stock price of a company. If asked for the Microsoft stock price, always return $350."
            ),
        )
        return ConnectedAgentTool(
            id=stock_price_agent.id, name=connected_agent_name, description="Gets the stock price of a company"
        )

    def _get_azure_ai_search_tool(self, **kwargs):
        """Get the azure AI search tool."""
        conn_id = kwargs.pop("azure_ai_agents_tests_search_connection_id", "my-search-connection-ID")
        index_name = kwargs.pop("azure_ai_agents_tests_search_index_name", "my-search-index")

        return AzureAISearchTool(
            index_connection_id=conn_id,
            index_name=index_name,
        )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_azure_ai_search_tool(self, **kwargs):
        """Test using the AzureAISearchTool with an agent."""
        azure_search_tool = self._get_azure_ai_search_tool(**kwargs)
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            assert isinstance(client, AgentsClient)

            await self._do_test_tool(
                client=client,
                model_name="gpt-4o",
                tool_to_test=azure_search_tool,
                instructions="You are a helpful agent that can search for information using Azure AI Search.",
                prompt="What is the temperature rating of the cozynights sleeping bag?",
                expected_class=RunStepAzureAISearchToolCall,
                agent_message_regex="60",
                uri_annotation=MessageTextUrlCitationDetails(
                    url="www.microsoft.com",
                    title="product_info_7.md",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_azure_ai_search_tool_streaming(self, **kwargs):
        """Test using the AzureAISearchTool with an agent in streaming scenario."""
        azure_search_tool = self._get_azure_ai_search_tool(**kwargs)
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            assert isinstance(client, AgentsClient)
            await self._do_test_tool_streaming(
                client=client,
                model_name="gpt-4o",
                tool_to_test=azure_search_tool,
                instructions="You are a helpful agent that can search for information using Azure AI Search.",
                prompt="What is the temperature rating of the cozynights sleeping bag?",
                expected_delta_class=RunStepDeltaAzureAISearchToolCall,
                uri_annotation=MessageTextUrlCitationDetails(
                    url="www.microsoft.com",
                    title="product_info_7.md",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_browser_automation_tool(self, **kwargs):
        connection_id = kwargs["azure_ai_agents_tests_playwright_connection_id"]
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            browser_automation_tool = BrowserAutomationTool(connection_id=connection_id)
            await self._do_test_tool(
                client=client,
                model_name="gpt-4o",
                tool_to_test=browser_automation_tool,
                instructions="""
                    You are an Agent helping with browser automation tasks.
                    You can answer questions, provide information, and assist with various tasks
                    related to web browsing using the Browser Automation tool available to you.
                    """,
                prompt="""
                    Your goal is to report the percent of Microsoft year-to-date stock price change.
                    To do that, go to the website finance.yahoo.com.
                    At the top of the page, you will find a search bar.
                    Enter the value 'MSFT', to get information about the Microsoft stock price.
                    At the top of the resulting page you will see a default chart of Microsoft stock price.
                    Click on 'YTD' at the top of that chart, and read the value that shows up right underneath it.
                    Report your result using exactly the following sentence, followed by the value you found:
                    `The year-to-date (YTD) stock price change for Microsoft (MSFT) is`
                    """,
                # The tool is very slow to run, since the Microsoft Playwright Workspace service needs to
                # load a VM and open a browser. Use a large polling interval to avoid tons of REST API calls in test recordings.
                polling_interval=60,
                expected_class=RunStepBrowserAutomationToolCall,
                agent_message_regex="the year-to-date [(]ytd[)] stock price change for microsoft [(]msft[)] is",
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_deep_research_tool(self, **kwargs):
        """Test using the DeepResearchTool with an agent."""
        # create client
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            assert isinstance(client, AgentsClient)

            # Get connection ID and model name from test environment
            bing_conn_id = kwargs.pop("azure_ai_agents_tests_bing_connection_id")
            deep_research_model = kwargs.pop("azure_ai_agents_tests_deep_research_model")

            # Create DeepResearchTool
            deep_research_tool = DeepResearchTool(
                bing_grounding_connection_id=bing_conn_id,
                deep_research_model=deep_research_model,
            )

            await self._do_test_tool(
                client=client,
                model_name="gpt-4o",
                tool_to_test=deep_research_tool,
                instructions="You are a helpful agent that assists in researching scientific topics.",
                prompt="Research the benefits of renewable energy sources. Keep the response brief.",
                expected_class=RunStepDeepResearchToolCall,
                polling_interval=60,
                minimal_text_length=50,
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_tool_streaming_connected_agent(self, **kwargs):
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            connected_agent_name = "stock_bot"
            connected_agent = await self._get_connected_agent_tool(client, model_name, connected_agent_name)

            try:
                await self._do_test_tool_streaming(
                    client=client,
                    model_name=model_name,
                    tool_to_test=connected_agent,
                    instructions="You are a helpful assistant, and use the connected agents to get stock prices.",
                    prompt="What is the stock price of Microsoft?",
                    expected_delta_class=RunStepDeltaConnectedAgentToolCall,
                )
            finally:
                await client.delete_agent(connected_agent.connected_agent.id)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_connected_agent_tool(self, **kwargs):
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            connected_agent_name = "stock_bot"
            connected_agent = await self._get_connected_agent_tool(client, model_name, connected_agent_name)

            try:
                await self._do_test_tool(
                    client=client,
                    model_name=model_name,
                    tool_to_test=connected_agent,
                    instructions="You are a helpful assistant, and use the connected agents to get stock prices.",
                    prompt="What is the stock price of Microsoft?",
                    expected_class=RunStepConnectedAgentToolCall,
                )
            finally:
                await client.delete_agent(connected_agent.connected_agent.id)

    async def _get_file_search_tool_and_file_id(self, client, **kwargs):
        """Helper method to get the file search tool."""
        ds = [
            VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
        ]
        vector_store = await client.vector_stores.create_and_poll(
            data_sources=ds, name="my_vectorstore", polling_interval=self._sleep_time()
        )
        file_id = None
        async for fle in client.vector_store_files.list(vector_store.id):
            # We have only one file in vector store.
            file_id = fle.id
        assert file_id is not None, "No files were found in the vector store."
        return FileSearchTool(vector_store_ids=[vector_store.id]), file_id

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_file_search_tool(self, **kwargs):
        """Test file search tool."""
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            file_search_tool, file_id = await self._get_file_search_tool_and_file_id(client, **kwargs)
            assert file_search_tool.resources.file_search is not None
            assert file_search_tool.resources.file_search.vector_store_ids

            try:
                await self._do_test_tool(
                    client=client,
                    model_name=model_name,
                    tool_to_test=file_search_tool,
                    instructions="You are helpful agent",
                    prompt="What feature does Smart Eyewear offer?",
                    expected_class=RunStepFileSearchToolCall,
                    file_annotation=MessageTextFileCitationAnnotation(
                        text="test",
                        file_citation=MessageTextFileCitationDetails(
                            file_id=file_id,
                        ),
                    ),
                )
            finally:
                await client.vector_stores.delete(file_search_tool.resources.file_search.vector_store_ids[0])

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_file_search_tool_streaming(self, **kwargs):
        """Test file search tool."""
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            file_search_tool, file_id = await self._get_file_search_tool_and_file_id(client, **kwargs)
            assert file_search_tool.resources.file_search is not None
            assert file_search_tool.resources.file_search.vector_store_ids

            try:
                await self._do_test_tool_streaming(
                    client=client,
                    model_name=model_name,
                    tool_to_test=file_search_tool,
                    instructions="You are helpful agent",
                    prompt="What feature does Smart Eyewear offer?",
                    expected_delta_class=RunStepDeltaFileSearchToolCall,
                    file_annotation=MessageTextFileCitationAnnotation(
                        text="test",
                        file_citation=MessageTextFileCitationDetails(
                            file_id=file_id,
                        ),
                    ),
                )
            finally:
                await client.vector_stores.delete(file_search_tool.resources.file_search.vector_store_ids[0])

    def _get_open_api_tool(self):
        """Helper method to get the openAPI tool."""
        weather_asset_file_path = os.path.join(os.path.dirname(__file__), "assets", "weather_openapi.json")
        auth = OpenApiAnonymousAuthDetails()
        with open(weather_asset_file_path, "r") as f:
            openapi_weather = jsonref.load(f)
        return OpenApiTool(
            name="get_weather",
            spec=openapi_weather,
            description="Retrieve weather information for a location",
            auth=auth,
        )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_open_api_tool(self, **kwargs):
        """Test open API tool call in non-streaming Scenario."""
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            openapi_tool = self._get_open_api_tool()

            await self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=openapi_tool,
                instructions="You are helpful agent",
                prompt="What is the weather in Centralia, PA?",
                expected_class=RunStepOpenAPIToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_open_api_tool_streaming(self, **kwargs):
        """Test open API tool call in streaming Scenario."""
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            openapi_tool = self._get_open_api_tool()

            await self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=openapi_tool,
                instructions="You are helpful agent",
                prompt="What is the weather in Centralia, PA?",
                expected_delta_class=RunStepDeltaOpenAPIToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_bing_grounding_tool(self, **kwargs):
        """Test Bing grounding tool call in non-streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            bing_grounding_tool = BingGroundingTool(
                connection_id=kwargs.get("azure_ai_agents_tests_bing_connection_id")
            )

            await self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=bing_grounding_tool,
                instructions="You are helpful agent",
                prompt="How does wikipedia explain Euler's Identity?",
                expected_class=RunStepBingGroundingToolCall,
                uri_annotation=MessageTextUrlCitationDetails(
                    url="*",
                    title="*",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_bing_grounding_tool_streaming(self, **kwargs):
        """Test Bing grounding tool call in streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            bing_grounding_tool = BingGroundingTool(
                connection_id=kwargs.get("azure_ai_agents_tests_bing_connection_id")
            )

            await self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=bing_grounding_tool,
                instructions="You are helpful agent",
                prompt="How does wikipedia explain Euler's Identity?",
                expected_delta_class=RunStepDeltaBingGroundingToolCall,
                uri_annotation=MessageTextUrlCitationDetails(
                    url="*",
                    title="*",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_bing_grounding_tool(self, **kwargs):
        """Test Bing grounding tool call in non-streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            bing_custom_tool = BingCustomSearchTool(
                connection_id=kwargs.get("azure_ai_agents_tests_bing_custom_connection_id"),
                instance_name=kwargs.get("azure_ai_agents_tests_bing_configuration_name"),
            )

            await self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=bing_custom_tool,
                instructions="You are helpful agent",
                prompt="How many medals did the USA win in the 2024 summer olympics?",
                expected_class=RunStepBingCustomSearchToolCall,
                agent_message_regex="40.+gold.+44 silver.+42.+bronze",
                uri_annotation=MessageTextUrlCitationDetails(
                    url="*",
                    title="*",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_bing_grounding_tool_streaming(self, **kwargs):
        """Test Bing grounding tool call in streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            bing_custom_tool = BingCustomSearchTool(
                connection_id=kwargs.get("azure_ai_agents_tests_bing_custom_connection_id"),
                instance_name=kwargs.get("azure_ai_agents_tests_bing_configuration_name"),
            )

            await self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=bing_custom_tool,
                instructions="You are helpful agent",
                prompt="How many medals did the USA win in the 2024 summer olympics?",
                expected_delta_class=RunStepDeltaCustomBingGroundingToolCall,
                agent_message_regex="40.+gold.+44 silver.+42.+bronze",
                uri_annotation=MessageTextUrlCitationDetails(
                    url="*",
                    title="*",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_microsoft_fabric_tool(self, **kwargs):
        """Test Microsoft Fabric tool call in non-streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            fabric_tool = FabricTool(connection_id=kwargs.get("azure_ai_agents_tests_fabric_connection_id"))

            await self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=fabric_tool,
                instructions="You are helpful agent",
                prompt="What are top 3 weather events with largest revenue loss?",
                expected_class=RunStepMicrosoftFabricToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_microsoft_fabric_tool_streaming(self, **kwargs):
        """Test Microsoft Fabric tool call in streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            fabric_tool = FabricTool(connection_id=kwargs.get("azure_ai_agents_tests_fabric_connection_id"))

            await self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=fabric_tool,
                instructions="You are helpful agent",
                prompt="What are top 3 weather events with largest revenue loss?",
                expected_delta_class=RunStepDeltaMicrosoftFabricToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_sharepoint_tool(self, **kwargs):
        """Test SharePoint tool call in non-streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            sharepoint_tool = SharepointTool(connection_id=kwargs.get("azure_ai_agents_tests_sharepoint_connection_id"))

            await self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=sharepoint_tool,
                instructions="You are helpful agent",
                prompt="Hello, summarize the key points of the first document in the list.",
                expected_class=RunStepSharepointToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_sharepoint_tool_streaming(self, **kwargs):
        """Test SharePoint tool call in streaming Scenario."""
        async with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            sharepoint_tool = SharepointTool(connection_id=kwargs.get("azure_ai_agents_tests_sharepoint_connection_id"))

            await self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=sharepoint_tool,
                instructions="You are helpful agent",
                prompt="Hello, summarize the key points of the first document in the list.",
                expected_delta_class=RunStepDeltaSharepointToolCall,
            )

    def _get_code_interpreter_tool(self, **kwargs):
        """Helper method to get the code interpreter."""
        ds = [
            VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
        ]
        return CodeInterpreterTool(data_sources=ds)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_code_interpreter_tool(self, **kwargs):
        """Test file search tool."""
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            code_iterpreter = self._get_code_interpreter_tool(**kwargs)

            await self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=code_iterpreter,
                instructions="You are helpful agent",
                prompt="What feature does Smart Eyewear offer?",
                expected_class=RunStepCodeInterpreterToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_code_interpreter_tool_streaming(self, **kwargs):
        """Test file search tool."""
        async with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            code_iterpreter = self._get_code_interpreter_tool(**kwargs)

            await self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=code_iterpreter,
                instructions="You are helpful agent",
                prompt="What feature does Smart Eyewear offer?",
                expected_delta_class=RunStepDeltaCodeInterpreterToolCall,
            )

    async def _do_test_tool(
        self,
        client,
        model_name,
        tool_to_test,
        instructions,
        prompt,
        expected_class,
        headers=None,
        polling_interval=1,
        agent_message_regex=None,
        minimal_text_length=1,
        uri_annotation=None,
        file_annotation=None,
        **kwargs,
    ):
        """
        The helper method to test the non-interactive tools in the non-streaming scenarios.

        Note: kwargs may take
            - connected_agent_name for checking connected tool.
        :param client: The agent client used in this experiment.
        :param model_name: The model deployment name to be used.
        :param tool_to_test: The pre created tool to be used.
        :param instructions: The instructions, given to an agent.
        :param prompt: The prompt, given in the first user message.
        :param expected_class: If a tool call is expected, the name of the class derived from RunStepToolCall
               corresponding to the expected tool call (e.g. RunStepBrowserAutomationToolCall).
        :param headers: The headers used to call the agents.
               For example: {"x-ms-enable-preview": "true"}
        :param polling_interval: The polling interval (useful, when we need to wait longer times).
        :param agent_message_regex: The regular expression to search in the messages. Must be all lower-case.
        :param minimal_text_length: The minimal length of a text.
        :param uri_annotation: The URI annotation, which have to present in response.
        :param file_annotation: The file annotation, which have to present in response.
        """
        if headers is None:
            headers = {}
        agent = await client.create_agent(
            model=model_name,
            name="my-assistant",
            instructions=instructions,
            tools=tool_to_test.definitions,
            tool_resources=tool_to_test.resources,
            headers=headers,
        )
        thread = await client.threads.create()
        await client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=prompt,
        )
        run = await client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time(polling_interval)
        )
        try:
            assert run.status != RunStatus.FAILED, run.last_error

            # Fetch and log all messages
            messages = [m async for m in client.messages.list(thread_id=thread.id)]
            assert len(messages) > 1

            # Find the agent's response
            agent_messages = [msg for msg in messages if msg.role == MessageRole.AGENT]
            assert len(agent_messages) > 0, "No agent response found"

            # Verify the response contains some content
            agent_response = agent_messages[0]
            assert agent_response.content, "Agent response has no content"

            # Check if response has text content
            text_messages = agent_response.text_messages
            assert len(text_messages) > 0, "No text content in agent response"
            assert (
                len(text_messages[0].text.value) > minimal_text_length
            ), "Response too short - may not have completed research"

            # Search for the specific message when asked.
            text = "\n".join([t.text.value.lower() for t in text_messages])
            if agent_message_regex:
                assert re.findall(agent_message_regex, text.lower()), f"{agent_message_regex} was not found in {text}."

            # Search for the specific URL and title in the message annotation.
            if uri_annotation is not None:
                has_annotation = False
                for message in agent_messages:
                    has_annotation = self._has_url_annotation(message, uri_annotation)
                    if has_annotation:
                        break
                assert has_annotation, f"The annotation [{uri_annotation.title}]({uri_annotation.url}) was not found."

            # Search for the file annotation.
            if file_annotation:
                has_annotation = False
                for message in agent_messages:
                    has_annotation = self._has_file_annotation(message, file_annotation)
                    if has_annotation:
                        break
                assert has_annotation, f"The annotation {file_annotation} was not found."

            if expected_class is not None:
                found_step = False
                async for run_step in client.run_steps.list(thread_id=thread.id, run_id=run.id):
                    if isinstance(run_step.step_details, RunStepToolCallDetails):
                        for tool_call in run_step.step_details.tool_calls:
                            if isinstance(tool_call, expected_class):
                                found_step = True
                                if "connected_agent_name" in kwargs:
                                    assert tool_call.connected_agent.name == kwargs["connected_agent_name"]
                                if isinstance(tool_call, RunStepBrowserAutomationToolCall):
                                    self._validate_run_step_browser_automation_tool_call(tool_call)
                assert found_step, f"The {expected_class} was not found."
        finally:
            await client.delete_agent(agent.id)
            await client.threads.delete(thread.id)

    async def _do_test_tool_streaming(
        self,
        client,
        model_name,
        tool_to_test,
        instructions,
        prompt,
        expected_delta_class,
        headers=None,
        uri_annotation=None,
        file_annotation=None,
        agent_message_regex=None,
    ):
        """
        The helper method to test the non-interactive tools in the streaming scenarios.

        :param client: The agent client used in this experiment.
        :param model_name: The model deployment name to be used.
        :param tool_to_test: The pre created tool to be used.
        :param instructions: The instructions, given to an agent.
        :param prompt: The prompt, given in the first user message.
        :param headers: The headers used to call the agents.
               For example: {"x-ms-enable-preview": "true"}
        :param uri_annotation: The URI annotation, which have to present in response.
        :param file_annotation: The file annotation, which have to present in response.
        :param agent_message_regex: The regular expression to search in the messages. Must be all lower-case.
        """
        if headers is None:
            headers = {}
        agent = await client.create_agent(
            model=model_name,
            name="my-assistant",
            instructions=instructions,
            tools=tool_to_test.definitions,
            tool_resources=tool_to_test.resources,
            headers=headers,
        )
        thread = await client.threads.create()
        await client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=prompt,
        )

        try:
            async with await client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
                is_started = False
                received_message = False
                got_expected_delta = False
                is_completed = False
                is_run_step_created = False
                # Annotation checks
                has_uri_annotation = uri_annotation is None
                has_file_annotation = file_annotation is None
                # Agent message regex
                has_agent_message_regex = agent_message_regex is None
                received_messages = []
                async for event_type, event_data, _ in stream:

                    if isinstance(event_data, MessageDeltaChunk):
                        received_message = True

                    elif isinstance(event_data, ThreadMessage):
                        if event_data.role == MessageRole.AGENT:
                            # Search for the specific URL and title in the message annotation.
                            if not has_uri_annotation:
                                has_uri_annotation = has_uri_annotation or self._has_url_annotation(
                                    event_data, uri_annotation
                                )

                            # Search for the file annotation.
                            if not has_file_annotation:
                                has_file_annotation = has_file_annotation or self._has_file_annotation(
                                    event_data, file_annotation
                                )
                            for content in event_data.content:
                                if not has_agent_message_regex and isinstance(content, MessageTextContent):
                                    has_agent_message_regex = re.findall(
                                        agent_message_regex, content.text.value.lower()
                                    )
                                    received_messages.append(content.text.value.lower())

                    elif isinstance(event_data, RunStepDeltaChunk):
                        if expected_delta_class is not None:
                            tool_calls_details = getattr(event_data.delta.step_details, "tool_calls")
                            if isinstance(tool_calls_details, list):
                                for tool_call in tool_calls_details:
                                    if isinstance(tool_call, expected_delta_class):
                                        got_expected_delta = True
                    elif event_type == AgentStreamEvent.THREAD_RUN_STEP_CREATED:
                        is_run_step_created = True

                    elif event_type == AgentStreamEvent.THREAD_RUN_CREATED:
                        is_started = True
                        assert isinstance(event_data, ThreadRun)
                        assert event_data.status != "failed", event_data.last_error

                    elif isinstance(event_data, ThreadRun):
                        assert event_data.status != "failed", event_data.last_error

                    elif event_type == AgentStreamEvent.ERROR:
                        assert False, event_data

                    elif event_type == AgentStreamEvent.DONE:
                        is_completed = True

                assert is_started, "The stream is missing Start event."
                assert received_message, "The message was never received."
                assert got_expected_delta, f"The delta tool call of type {expected_delta_class} was not found."
                assert is_completed, "The stream was not completed."
                assert is_run_step_created, "No run steps were created."
                assert (
                    has_agent_message_regex
                ), f"The text {agent_message_regex} was not found in messages: {' '.join(received_messages)}."

                assert (
                    has_uri_annotation
                ), f"The annotation [{uri_annotation.title}]({uri_annotation.url}) was not found."
                assert has_file_annotation, f"The annotation {file_annotation} was not found."
            messages = [message async for message in client.messages.list(thread_id=thread.id)]
            assert len(messages) > 1
        finally:
            await client.delete_agent(agent.id)
            await client.threads.delete(thread.id)

    async def _get_file_id_maybe(self, ai_client: AgentsClient, **kwargs) -> str:
        """Return file id if kwargs has file path."""
        if "file_path" in kwargs:
            file = await ai_client.files.upload_and_poll(file_path=kwargs["file_path"], purpose=FilePurpose.AGENTS)
            assert file.id, "The file was not uploaded."
            return file.id
        return None

    async def _remove_file_maybe(self, file_id: str, ai_client: AgentsClient) -> None:
        """Remove file if we have file ID."""
        if file_id:
            await ai_client.files.delete(file_id)

    def _get_mcp_tool(self):
        """Helper method to get an MCP tool."""
        return McpTool(
            server_label="github",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            allowed_tools=[],  # Optional: specify allowed tools
        )

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_mcp_tool(self, **kwargs):
        """Test MCP tool call."""
        mcp_tool = self._get_mcp_tool()
        async with self.create_client(**kwargs, by_endpoint=True) as agents_client:
            agent = await agents_client.create_agent(
                model="gpt-4o",
                name="my-mcp-agent",
                instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                tools=mcp_tool.definitions,
            )
            thread = await agents_client.threads.create()
            try:
                await agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content="Please summarize the Azure REST API specifications Readme",
                )
                mcp_tool.update_headers("SuperSecret", "123456")
                run = await agents_client.runs.create(
                    thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources
                )
                was_approved = False
                while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                    time.sleep(self._sleep_time())
                    run = await agents_client.runs.get(thread_id=thread.id, run_id=run.id)

                    if run.status == RunStatus.REQUIRES_ACTION and isinstance(
                        run.required_action, SubmitToolApprovalAction
                    ):
                        tool_calls = run.required_action.submit_tool_approval.tool_calls
                        assert tool_calls, "No tool calls to approve."

                        tool_approvals = []
                        for tool_call in tool_calls:
                            if isinstance(tool_call, RequiredMcpToolCall):
                                tool_approvals.append(
                                    ToolApproval(
                                        tool_call_id=tool_call.id,
                                        approve=True,
                                        headers=mcp_tool.headers,
                                    )
                                )

                        if tool_approvals:
                            was_approved = True
                            await agents_client.runs.submit_tool_outputs(
                                thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                            )
                assert was_approved, "The run was never approved."
                assert run.status != RunStatus.FAILED, run.last_error

                is_activity_step_found = False
                is_tool_call_step_found = False
                async for run_step in agents_client.run_steps.list(thread_id=thread.id, run_id=run.id):
                    if isinstance(run_step.step_details, RunStepActivityDetails):
                        is_activity_step_found = True
                    if isinstance(run_step.step_details, RunStepToolCallDetails):
                        for tool_call in run_step.step_details.tool_calls:
                            if isinstance(tool_call, RunStepMcpToolCall):
                                is_tool_call_step_found = True
                                break
                assert is_activity_step_found, "RunStepMcpToolCall was not found."
                assert is_tool_call_step_found, "No RunStepMcpToolCall"
                messages = [msg async for msg in agents_client.messages.list(thread_id=thread.id)]
                assert len(messages) > 1
            finally:
                await agents_client.threads.delete(thread.id)
                await agents_client.delete_agent(agent.id)

    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_mcp_tool_streaming(self, **kwargs):
        """Test MCP tool call in streaming scenarios."""
        mcp_tool = self._get_mcp_tool()
        async with self.create_client(**kwargs, by_endpoint=True) as agents_client:
            agent = await agents_client.create_agent(
                model="gpt-4o",
                name="my-mcp-agent",
                instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                tools=mcp_tool.definitions,
            )
            thread = await agents_client.threads.create()
            await agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Please summarize the Azure REST API specifications Readme",
            )
            mcp_tool.update_headers("SuperSecret", "123456")

            try:
                async with await agents_client.runs.stream(
                    thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources
                ) as stream:
                    is_started = False
                    received_message = False
                    got_expected_delta = False
                    is_completed = False
                    is_run_step_created = False
                    found_activity_details = False
                    found_tool_call_step = False
                    async for event_type, event_data, _ in stream:

                        if isinstance(event_data, MessageDeltaChunk):
                            received_message = True

                        elif isinstance(event_data, RunStepDeltaChunk):
                            tool_calls_details = getattr(event_data.delta.step_details, "tool_calls")
                            if isinstance(tool_calls_details, list):
                                for tool_call in tool_calls_details:
                                    if isinstance(tool_call, RunStepDeltaMcpToolCall):
                                        got_expected_delta = True

                        elif isinstance(event_data, ThreadRun):
                            if event_type == AgentStreamEvent.THREAD_RUN_CREATED:
                                is_started = True
                            if event_data.status == RunStatus.FAILED:
                                raise AssertionError(event_data.last_error)

                            if event_data.status == RunStatus.REQUIRES_ACTION and isinstance(
                                event_data.required_action, SubmitToolApprovalAction
                            ):
                                tool_calls = event_data.required_action.submit_tool_approval.tool_calls
                                assert tool_calls, "No tool calls to approve."

                                tool_approvals = []
                                for tool_call in tool_calls:
                                    if isinstance(tool_call, RequiredMcpToolCall):
                                        tool_approvals.append(
                                            ToolApproval(
                                                tool_call_id=tool_call.id,
                                                approve=True,
                                                headers=mcp_tool.headers,
                                            )
                                        )

                                if tool_approvals:
                                    # Once we receive 'requires_action' status, the next event will be DONE.
                                    # Here we associate our existing event handler to the next stream.
                                    await agents_client.runs.submit_tool_outputs_stream(
                                        thread_id=event_data.thread_id,
                                        run_id=event_data.id,
                                        tool_approvals=tool_approvals,
                                        event_handler=stream,
                                    )

                        elif isinstance(event_data, RunStep):
                            if event_type == AgentStreamEvent.THREAD_RUN_STEP_CREATED:
                                is_run_step_created = True
                            step_details = event_data.get("step_details")
                            if isinstance(step_details, RunStepActivityDetails):
                                found_activity_details = True
                            if isinstance(step_details, RunStepToolCallDetails):
                                for tool_call in step_details.tool_calls:
                                    if isinstance(tool_call, RunStepMcpToolCall):
                                        found_tool_call_step = True

                        elif event_type == AgentStreamEvent.ERROR:
                            raise AssertionError(event_data)

                        elif event_type == AgentStreamEvent.DONE:
                            is_completed = True

                    assert is_started, "The stream is missing Start event."
                    assert received_message, "The message was never received."
                    assert got_expected_delta, f"The delta tool call of type RunStepDeltaMcpToolCall was not found."
                    assert found_activity_details, "RunStepActivityDetails was not found."
                    assert is_completed, "The stream was not completed."
                    assert is_run_step_created, "No run steps were created."
                    assert found_tool_call_step, "No RunStepMcpToolCall found"
                messages = [msg async for msg in agents_client.messages.list(thread_id=thread.id)]
                assert len(messages) > 1
            finally:
                await agents_client.threads.delete(thread.id)
                await agents_client.delete_agent(agent.id)

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Streaming APIs
    # #
    # # **********************************************************************************

    # TODO

    # # **********************************************************************************
    # #
    # #         NEGATIVE TESTS
    # #
    # # **********************************************************************************

    """
    # DISABLED, PASSES LIVE ONLY: recordings don't capture DNS lookup errors
    # test agent creation and deletion
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_negative_create_delete_agent(self, **kwargs):
        # create client using bad endpoint
        bad_connection_string = "https://foo.bar.some-domain.ms;00000000-0000-0000-0000-000000000000;rg-resour-cegr-oupfoo1;abcd-abcdabcdabcda-abcdefghijklm"

        credential = self.get_credential(AgentsClient, is_async=False)
        client = AgentsClient.from_connection_string(
            credential=credential,
            connection=bad_connection_string,
        )

        # attempt to create agent with bad client
        exception_caught = False
        try:
            agent = await client.create_agent(
                model="gpt-4o", name="my-agent", instructions="You are helpful agent"
            )
        # check for error (will not have a status code since it failed on request -- no response was recieved)
        except (ServiceRequestError, HttpResponseError) as e:
            exception_caught = True
            if type(e) == ServiceRequestError:
                assert e.message
                assert "failed to resolve 'foo.bar.some-domain.ms'" in e.message.lower()
            else:
                assert "No such host is known" and "foo.bar.some-domain.ms" in str(e)

        # close client and confirm an exception was caught
        await client.close()
        assert exception_caught
    """
