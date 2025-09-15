# pylint: disable=too-many-lines,line-too-long,useless-suppression
# # ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
from typing import Any, Dict, Optional, Type

import os
import re
import json
import jsonref
import tempfile
import time
import pytest
import io
import user_functions

from typing import List

from azure.ai.agents import AgentsClient
from azure.core.exceptions import HttpResponseError
from devtools_testutils import (
    recorded_by_proxy,
)
from azure.ai.agents.models import (
    AgentEventHandler,
    AgentStreamEvent,
    AgentThread,
    AzureAISearchTool,
    AzureFunctionStorageQueue,
    AzureFunctionTool,
    BingCustomSearchTool,
    BingGroundingTool,
    BrowserAutomationTool,
    CodeInterpreterTool,
    CodeInterpreterToolResource,
    ConnectedAgentTool,
    DeepResearchTool,
    ComputerUseTool,
    FabricTool,
    FilePurpose,
    FileSearchTool,
    FileSearchToolCallContent,
    FileSearchToolResource,
    FunctionTool,
    McpTool,
    ComputerToolOutput,
    ComputerScreenshot,
    MessageAttachment,
    MessageDeltaChunk,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
    MessageTextContent,
    MessageTextFileCitationDetails,
    MessageTextFileCitationAnnotation,
    MessageTextUrlCitationDetails,
    MessageRole,
    FileInfo,
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
    RequiredMcpToolCall,
    RequiredComputerUseToolCall,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
    RunStepActivityDetails,
    RunAdditionalFieldList,
    RunStepAzureFunctionToolCall,
    RunStepAzureAISearchToolCall,
    RunStepBingCustomSearchToolCall,
    RunStepBingGroundingToolCall,
    RunStepBrowserAutomationToolCall,
    RunStepCodeInterpreterToolCall,
    RunStepComputerUseToolCall,
    RunStepConnectedAgentToolCall,
    RunStepDeepResearchToolCall,
    RunStepDeltaAzureFunctionToolCall,
    RunStepDeltaAzureAISearchToolCall,
    RunStepDeltaChunk,
    RunStepDeltaCodeInterpreterToolCall,
    RunStepDeltaCustomBingGroundingToolCall,
    RunStepDeltaBingGroundingToolCall,
    RunStepDeltaFileSearchToolCall,
    RunStepDeltaMcpToolCall,
    RunStepDeltaMicrosoftFabricToolCall,
    RunStepDeltaOpenAPIToolCall,
    RunStepDeltaSharepointToolCall,
    RunStepDeltaToolCallObject,
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
    SubmitToolOutputsAction,
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
from azure.ai.agents.models._models import RunStepDeltaConnectedAgentToolCall
from test_agents_client_base import (
    TestAgentClientBase,
    agentClientPreparer,
    fetch_current_datetime_recordings,
    fetch_current_datetime_live,
    image_to_base64,
)

# Statically defined user functions for fast reference
user_functions_recording = {fetch_current_datetime_recordings}
user_functions_live = {fetch_current_datetime_live}


# The test class name needs to start with "Test" to get collected by pytest
class TestAgentClient(TestAgentClientBase):

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

    def _get_screenshot_file(self) -> str:
        """Return the test file name."""
        return os.path.join(os.path.dirname(__file__), "test_data", "cua_screenshot.jpg")

    def _get_screenshot_next_file(self) -> str:
        """Return the test file name."""
        return os.path.join(os.path.dirname(__file__), "test_data", "cua_screenshot_next.jpg")

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - agent APIs
    #
    # **********************************************************************************

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_client(self, **kwargs):
        """test client creation"""

        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AgentsClient)

        # close client
        client.close()

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_delete_agent(self, **kwargs):
        """test agent creation and deletion"""
        # create client
        # client = self.create_client(**kwargs)
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            print("Created client")
            self._do_test_create_agent(client=client, body=None, functions=None)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_body(self, **kwargs):
        """test agent creation with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            print("Created client")

            # create body for agent and call helper function
            body = {"name": "my-agent", "model": "gpt-4o", "instructions": "You are helpful agent"}
            self._do_test_create_agent(client=client, body=body, functions=None)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_iobytes(self, **kwargs):
        """test agent creation with body: IO[bytes]"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            print("Created client")

            # create body for agent and call helper function
            body = {"name": "my-agent", "model": "gpt-4o", "instructions": "You are helpful agent"}
            binary_body = json.dumps(body).encode("utf-8")
            self._do_test_create_agent(client=client, body=io.BytesIO(binary_body), functions=None)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_tools(self, **kwargs):
        """test agent creation with tools"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # initialize agent functions
            functions = FunctionTool(functions=user_functions_recording)
            self._do_test_create_agent(client=client, body=None, functions=functions)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_tools_and_resources(self, **kwargs):
        """test agent creation with tools and resources"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # initialize agent functions
            functions = FunctionTool(functions=user_functions_recording)
            self._do_test_create_agent(client=client, body=None, functions=functions)

    def _do_test_create_agent(self, client, body, functions):
        """helper function for creating agent with different body inputs"""

        # create agent
        if body:
            agent = client.create_agent(body=body)
        elif functions:
            agent = client.create_agent(
                model="gpt-4o",
                name="my-agent",
                instructions="You are helpful agent",
                tools=functions.definitions,
            )
            assert agent.tools
            assert agent.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
            print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])
        else:
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)
        assert agent.name == "my-agent"
        assert agent.model == "gpt-4o"

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_agent(self, **kwargs):
        """test agent update without body"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_update_agent(client=client, use_body=False, use_io=False)

    @agentClientPreparer()
    @pytest.mark.skip("Update agent with body is failing")
    @recorded_by_proxy
    def test_update_agent_with_body(self, **kwargs):
        """test agent update with body: JSON"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_update_agent(client=client, use_body=True, use_io=False)

    @agentClientPreparer()
    @pytest.mark.skip("Update agent with body is failing")
    @recorded_by_proxy
    def test_update_agent_with_iobytes(self, **kwargs):
        """test agent update with body: IO[bytes]"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_update_agent(client=client, use_body=True, use_io=True)

    def _do_test_update_agent(self, client: AgentsClient, use_body, use_io):
        """helper function for updating agent with different body inputs"""

        # create agent
        agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id

        # update agent
        if use_body:
            body = {"agent_id": agent.id, "name": "my-agent2"}
            if use_io:
                binary_body = json.dumps(body).encode("utf-8")
                body = io.BytesIO(binary_body)
            agent = client.update_agent(agent_id=agent.id, body=body)
        else:
            agent = client.update_agent(agent_id=agent.id, name="my-agent2")
        assert agent.name
        assert agent.name == "my-agent2"

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")

    @agentClientPreparer()
    @pytest.mark.skip("Does not perform consistently on a shared resource")
    @recorded_by_proxy
    def test_agent_list(self, **kwargs):
        """test list agents"""
        # create client and ensure there are no previous agents
        with self.create_client(**kwargs) as client:
            agents = list(client.list_agents())
            list_length = len(agents)

            # create agent and verify it is listed
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")

            agents = list(client.list_agents())
            assert len(agents) == list_length + 1
            assert agent.id in {a.id for a in agents}

            # create second agent and verify it is listed
            agent2 = client.create_agent(model="gpt-4o", name="my-agent2", instructions="You are helpful agent")

            agents = list(client.list_agents())
            assert len(agents) == list_length + 2
            assert {agent.id, agent2.id}.issubset({a.id for a in agents})

            # delete first agent and verify list shrinks
            client.delete_agent(agent.id)
            agents = list(client.list_agents())
            assert len(agents) == list_length + 1
            assert agent2.id in {a.id for a in agents}

            # delete second agent and verify list is back to original size
            client.delete_agent(agent2.id)
            assert len(list(client.list_agents())) == list_length

            print("Deleted agents")

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - Thread APIs
    #
    # **********************************************************************************

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread(self, **kwargs):
        """test creating thread"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert isinstance(thread, AgentThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_with_metadata(self, **kwargs):
        """test creating thread with no body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            self._do_test_create_thread(client=client, body=None)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_with_body(self, **kwargs):
        """test creating thread with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for thread and call helper function
            body = {
                "metadata": {"key1": "value1", "key2": "value2"},
            }
            self._do_test_create_thread(client=client, body=body)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_with_iobytes(self, **kwargs):
        """test creating thread with body: IO[bytes]"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for thread and call helper function
            body = {
                "metadata": {"key1": "value1", "key2": "value2"},
            }
            binary_body = json.dumps(body).encode("utf-8")
            self._do_test_create_thread(client=client, body=io.BytesIO(binary_body))

    def _do_test_create_thread(self, client, body):
        """helper function for creating thread with different body inputs"""
        # create thread
        if body:
            thread = client.threads.create(body=body)
        else:
            thread = client.threads.create(metadata={"key1": "value1", "key2": "value2"})
        assert isinstance(thread, AgentThread)
        assert thread.id
        print("Created thread, thread ID", thread.id)
        assert thread.metadata == {"key1": "value1", "key2": "value2"}

    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_thread(self, **kwargs):
        """test getting thread"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # get thread
            thread2 = client.threads.get(thread.id)
            assert thread2.id
            assert thread.id == thread2.id
            print("Got thread, thread ID", thread2.id)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread(self, **kwargs):
        """test updating thread without body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # update thread
            thread = client.threads.update(thread.id, metadata={"key1": "value1", "key2": "value2"})
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread_with_metadata(self, **kwargs):
        """test updating thread without body"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # set metadata
            metadata = {"key1": "value1", "key2": "value2"}

            # create thread
            thread = client.threads.create(metadata=metadata)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # set metadata
            metadata2 = {"key1": "value1", "key2": "newvalue2"}

            # update thread
            thread = client.threads.update(thread.id, metadata=metadata2)
            assert thread.metadata == {"key1": "value1", "key2": "newvalue2"}

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread_with_body(self, **kwargs):
        """test updating thread with body: JSON"""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # set body and run test
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            self._do_test_update_thread(client=client, body=body)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread_with_iobytes(self, **kwargs):
        """test updating thread with body: IO[bytes]"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # set body and run test
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")
            io_body = io.BytesIO(binary_body)
            self._do_test_update_thread(client=client, body=io_body)

    def _do_test_update_thread(self, client, body):
        """helper function for updating thread with different body inputs"""
        # create thread
        thread = client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # update thread
        if body:
            thread = client.threads.update(thread.id, body=body)
        else:
            metadata = {"key1": "value1", "key2": "value2"}
            thread = client.threads.update(thread.id, metadata=metadata)
        assert thread.metadata == {"key1": "value1", "key2": "value2"}

    @agentClientPreparer()
    @recorded_by_proxy
    def test_delete_thread(self, **kwargs):
        """test deleting thread"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert isinstance(thread, AgentThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # delete thread
            client.threads.delete(thread.id)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Message APIs
    # #
    # # **********************************************************************************

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_message(self, **kwargs):
        """test creating message in a thread without body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_create_message(client=client, body=None)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_message_with_body(self, **kwargs):
        """test creating message in a thread with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for message and call helper function
            body = {"role": "user", "content": "Hello, tell me a joke"}
            self._do_test_create_message(client=client, body=body)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_message_with_iobytes(self, **kwargs):
        """test creating message in a thread with body: IO[bytes]"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for message and call helper function
            body = {"role": "user", "content": "Hello, tell me a joke"}
            binary_body = json.dumps(body).encode("utf-8")
            self._do_test_create_message(client=client, body=io.BytesIO(binary_body))

    def _do_test_create_message(self, client, body):
        """helper function for creating message with different body inputs"""

        # create thread
        thread = client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        if body:
            message = client.messages.create(thread_id=thread.id, body=body)
        else:
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_multiple_messages(self, **kwargs):
        """test creating multiple messages in a thread"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create messages
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)
            message2 = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me another joke")
            assert message2.id
            print("Created message, message ID", message2.id)
            message3 = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a third joke")
            assert message3.id
            print("Created message, message ID", message3.id)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_list_messages(self, **kwargs):
        """test listing messages in a thread"""
        # create client
        with self.create_client(by_endpoint=True, **kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # check that initial message list is empty
            messages0 = list(client.messages.list(thread_id=thread.id))
            print(messages0)
            assert len(messages0) == 0

            # create messages and check message list for each one
            message1 = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message1.id
            print("Created message, message ID", message1.id)
            messages1 = list(client.messages.list(thread_id=thread.id))
            assert len(messages1) == 1
            assert messages1[0].id == message1.id

            message2 = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me another joke")
            assert message2.id
            print("Created message, message ID", message2.id)
            messages2 = list(client.messages.list(thread_id=thread.id))
            assert len(messages2) == 2
            assert any(msg.id == message2.id for msg in messages2)

            message3 = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a third joke")
            assert message3.id
            print("Created message, message ID", message3.id)
            messages3 = list(client.messages.list(thread_id=thread.id))
            assert len(messages3) == 3
            assert any(msg.id == message3.id for msg in messages3)

            client.messages.delete(thread_id=thread.id, message_id=message3.id)
            messages4 = list(client.messages.list(thread_id=thread.id))
            assert len(messages4) == 2
            assert not any(msg.id == message3.id for msg in messages4)

            # Check that we can add messages after deletion
            message3 = client.messages.create(thread_id=thread.id, role="user", content="Bar")
            assert message3.id
            messages5 = list(client.messages.list(thread_id=thread.id))
            assert len(messages5) == 3
            assert any(msg.id == message3.id for msg in messages5)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_message(self, **kwargs):
        """test getting message in a thread"""
        # create client
        with self.create_client(**kwargs) as client:
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
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # get message
            message2 = client.messages.get(thread_id=thread.id, message_id=message.id)
            assert message2.id
            assert message.id == message2.id
            print("Got message, message ID", message.id)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_message(self, **kwargs):
        """test updating message in a thread without body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_update_message(client=client, body=None)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_message_with_body(self, **kwargs):
        """test updating message in a thread with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for message and call helper function
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            self._do_test_update_message(client=client, body=body)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_message_with_iobytes(self, **kwargs):
        """test updating message in a thread with body: IO[bytes]"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for message and call helper function
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")
            self._do_test_update_message(client=client, body=io.BytesIO(binary_body))

    def _do_test_update_message(self, client, body):
        """helper function for updating message with different body inputs"""
        # create thread
        thread = client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # update message
        if body:
            message = client.messages.update(thread_id=thread.id, message_id=message.id, body=body)
        else:
            message = client.messages.update(
                thread_id=thread.id, message_id=message.id, metadata={"key1": "value1", "key2": "value2"}
            )
        assert message.metadata == {"key1": "value1", "key2": "value2"}

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Run APIs
    # #
    # # **********************************************************************************

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run(self, **kwargs):
        """test creating run"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run_with_metadata(self, **kwargs):
        """test creating run without body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_create_run(client=client, use_body=False, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run_with_body(self, **kwargs):
        """test creating run with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_create_run(client=client, use_body=True, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run_with_iobytes(self, **kwargs):
        """test creating run with body: IO[bytes]"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_create_run(client=client, use_body=True, use_io=True)

    def _do_test_create_run(self, client, use_body, use_io=False):
        """helper function for creating run with different body inputs"""

        # create agent
        agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        if use_body:
            body = {"assistant_id": agent.id, "metadata": {"key1": "value1", "key2": "value2"}}
            if use_io:
                binary_body = json.dumps(body).encode("utf-8")
                body = io.BytesIO(binary_body)
            run = client.runs.create(thread_id=thread.id, body=body)
        else:
            run = client.runs.create(
                thread_id=thread.id, agent_id=agent.id, metadata={"key1": "value1", "key2": "value2"}
            )
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_run(self, **kwargs):
        """test getting run"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # get run
            run2 = client.runs.get(thread_id=thread.id, run_id=run.id)
            assert run2.id
            assert run.id == run2.id
            print("Got run, run ID", run2.id)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_run_status(self, **kwargs):
        """test run status"""
        # create client
        with self.create_client(**kwargs) as client:
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
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = client.runs.create(thread_id=thread.id, agent_id=agent.id)
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
                run = client.runs.get(thread_id=thread.id, run_id=run.id)
                print("Run status:", run.status)

            assert run.status in ["cancelled", "failed", "completed", "expired"]
            print("Run completed with status:", run.status)

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run(self, **kwargs):
        """test updating run without body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create agent
            agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # create thread
            thread = client.threads.create()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = client.runs.create(thread_id=thread.id, agent_id=agent.id)
            assert run.id
            print("Created run, run ID", run.id)

            # update run
            while run.status in ["queued", "in_progress"]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = client.runs.get(thread_id=thread.id, run_id=run.id)
            run = client.runs.update(thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "value2"})
            assert run.metadata == {"key1": "value1", "key2": "value2"}

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run_with_metadata(self, **kwargs):
        """test updating run without body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_update_run(client=client, body=None)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run_with_body(self, **kwargs):
        """test updating run with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for run and call helper function
            body = {"metadata": {"key1": "value1", "key2": "newvalue2"}}
            self._do_test_update_run(client=client, body=body)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run_with_iobytes(self, **kwargs):
        """test updating run with body: IO[bytes]"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # create body for run and call helper function
            body = {"metadata": {"key1": "value1", "key2": "newvalue2"}}
            binary_body = json.dumps(body).encode("utf-8")
            self._do_test_update_run(client=client, body=io.BytesIO(binary_body))

    def _do_test_update_run(self, client, body):
        """helper function for updating run with different body inputs"""
        # create agent
        agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.runs.create(thread_id=thread.id, agent_id=agent.id, metadata={"key1": "value1", "key2": "value2"})
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # update run
        while run.status in ["queued", "in_progress"]:
            time.sleep(self._sleep_time(5))
            run = client.runs.get(thread_id=thread.id, run_id=run.id)
        if body:
            run = client.runs.update(thread_id=thread.id, run_id=run.id, body=body)
        else:
            run = client.runs.update(
                thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "newvalue2"}
            )
        assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

        # delete agent
        client.delete_agent(agent.id)
        print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_run(self, **kwargs):
        """test submitting tool outputs to run without body"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_submit_tool_outputs_to_run(client=client, use_body=False, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_run_with_body(self, **kwargs):
        """test submitting tool outputs to run with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_submit_tool_outputs_to_run(client=client, use_body=True, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_run_with_iobytes(self, **kwargs):
        """test submitting tool outputs to run with body: IO[bytes]"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_submit_tool_outputs_to_run(client=client, use_body=True, use_io=True)

    def _do_test_submit_tool_outputs_to_run(self, client, use_body, use_io):
        """helper function for submitting tool outputs to run with different body inputs"""

        # Initialize agent tools
        functions = FunctionTool(user_functions_recording)
        # code_interpreter = CodeInterpreterTool()

        toolset = ToolSet()
        toolset.add(functions)
        # toolset.add(code_interpreter)

        # create agent
        agent = client.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
        )
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
            run = client.runs.get(thread_id=thread.id, run_id=run.id)

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
                    if use_body:
                        body = {"tool_outputs": tool_outputs}
                        if use_io:
                            binary_body = json.dumps(body).encode("utf-8")
                            body = io.BytesIO(binary_body)
                        client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, body=body)
                    else:
                        client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        # check that messages used the tool
        print("Messages: ")
        messages = list(client.messages.list(thread_id=thread.id, run_id=run.id))
        tool_message = messages[0].content[0].text.value
        # if user_functions_live is used, the time will be the current time
        # since user_functions_recording is used, the time will be 12:30
        assert "12:30" in tool_message
        print("Used tool_outputs")

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy
    def test_create_parallel_tool_thread_true(self, **kwargs):
        """Test creation of parallel runs."""
        self._do_test_create_parallel_thread_runs(True, True, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy
    def test_create_parallel_tool_thread_false(self, **kwargs):
        """Test creation of parallel runs."""
        self._do_test_create_parallel_thread_runs(False, True, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy
    def test_create_parallel_tool_run_true(self, **kwargs):
        """Test creation of parallel runs."""
        self._do_test_create_parallel_thread_runs(True, False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy
    def test_create_parallel_tool_run_false(self, **kwargs):
        """Test creation of parallel runs."""
        self._do_test_create_parallel_thread_runs(False, False, **kwargs)

    def _wait_for_run(self, client, run, timeout=1):
        """Wait while run will get to terminal state."""
        while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
            time.sleep(self._sleep_time(timeout))
            run = client.runs.get(thread_id=run.thread_id, run_id=run.id)
        return run

    def _do_test_create_parallel_thread_runs(self, use_parallel_runs, create_thread_run, **kwargs):
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
        agent = client.create_agent(
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
            run = client.create_thread_and_run(
                agent_id=agent.id,
                parallel_tool_calls=use_parallel_runs,
            )
            run = self._wait_for_run(client, run)
        else:
            thread = client.threads.create(messages=[message])
            assert thread.id

            run = client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
                parallel_tool_calls=use_parallel_runs,
            )
        assert run.id
        assert run.status == RunStatus.COMPLETED, run.last_error.message
        assert run.parallel_tool_calls == use_parallel_runs

        client.delete_agent(agent.id)
        messages = list(client.messages.list(thread_id=run.thread_id))
        assert len(messages), "The data from the agent was not received."

    """
    # DISABLED: rewrite to ensure run is not complete when cancel_run is called
    @agentClientPreparer()
    @recorded_by_proxy
    def test_cancel_run(self, **kwargs):
        '''test cancelling run'''
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
            run = client.runs.get(thread_id=thread.id, run_id=run.id)
            print("Current run status:", run.status)
        assert run.status == "cancelled"
        print("Run cancelled")

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        client.close()
        """

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_and_run(self, **kwargs):
        """Test creating thread and run"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_create_thread_and_run(client=client, use_body=False, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_and_run_with_body(self, **kwargs):
        """Test creating thread and run with body: JSON"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_create_thread_and_run(client=client, use_body=True, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_and_run_with_iobytes(self, **kwargs):
        """Test creating thread and run with body: IO[bytes]"""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_create_thread_and_run(client=client, use_body=True, use_io=True)

    def _do_test_create_thread_and_run(self, client, use_body, use_io):
        """helper function for creating thread and run with different body inputs"""

        # create agent
        agent = client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create run
        if use_body:
            body = {
                "assistant_id": agent.id,
                "metadata": {"key1": "value1", "key2": "value2"},
            }
            if use_io:
                binary_body = json.dumps(body).encode("utf-8")
                body = io.BytesIO(binary_body)
            run = client.create_thread_and_run(body=body)
            assert run.metadata == {"key1": "value1", "key2": "value2"}
        else:
            run = client.create_thread_and_run(agent_id=agent.id)

        # create thread and run
        assert run.id
        assert run.thread_id
        print("Created run, run ID", run.id)

        # get thread
        thread = client.threads.get(run.thread_id)
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
            run = client.runs.get(thread_id=thread.id, run_id=run.id)
            # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)

        assert run.status == "completed"
        print("Run completed")

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")

    @agentClientPreparer()
    @pytest.mark.skip("Working on recordings")
    @recorded_by_proxy
    def test_list_run_step(self, **kwargs):
        """Test listing run steps."""

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

        steps = client.run_steps.list(thread_id=thread.id, run_id=run.id)
        # commenting assertion out below, do we know exactly when run starts?
        # assert steps['data'].__len__() == 0

        # check status
        assert run.status in ["queued", "in_progress", "requires_action", "completed"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(self._sleep_time())
            run = client.runs.get(thread_id=thread.id, run_id=run.id)
            assert run.status in [
                "queued",
                "in_progress",
                "requires_action",
                "completed",
            ]
            print("Run status:", run.status)
            if run.status != "queued":
                steps = list(client.run_steps.list(thread_id=thread.id, run_id=run.id))
                print("Steps:", steps)
                assert len(steps) > 0

        assert run.status == "completed"
        print("Run completed")

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_run_step(self, **kwargs):
        """Test getting run step."""

        # create client
        with self.create_client(**kwargs) as client:
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
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, can you tell me a joke?")
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = client.runs.create(thread_id=thread.id, agent_id=agent.id)
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
                run = client.runs.get(thread_id=thread.id, run_id=run.id)
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
            steps = list(client.run_steps.list(thread_id=thread.id, run_id=run.id))
            assert len(steps) > 0
            step = steps[0]
            get_step = client.run_steps.get(thread_id=thread.id, run_id=run.id, step_id=step.id)
            assert step == get_step

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Streaming APIs
    # #
    # # **********************************************************************************

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_stream(self, **kwargs):
        """Test creating stream."""

        # create client
        with self.create_client(**kwargs) as client:
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
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, can you tell me a joke?")
            assert message.id
            print("Created message, message ID", message.id)

            # create stream
            with client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
                for event_type, event_data, _ in stream:
                    assert (
                        isinstance(event_data, (MessageDeltaChunk, ThreadMessage, ThreadRun, RunStep))
                        or event_type == AgentStreamEvent.DONE
                    )

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    # TODO create_stream doesn't work with body -- fails on for event_type, event_data : TypeError: 'ThreadRun' object is not an iterator
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_stream_with_body(self, **kwargs):
        """Test creating stream with body."""

        # create client
        with self.create_client(**kwargs) as client:
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
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, can you tell me a joke?")
            assert message.id
            print("Created message, message ID", message.id)

            # create body for stream
            body = {"assistant_id": agent.id, "stream": True}

            # create stream
            with client.runs.stream(thread_id=thread.id, body=body, stream=True) as stream:

                for event_type, event_data, _ in stream:
                    print("event type: event data")
                    print(event_type, event_data)
                    assert (
                        isinstance(event_data, (MessageDeltaChunk, ThreadMessage, ThreadRun, RunStep))
                        or event_type == AgentStreamEvent.DONE
                    )

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_stream_with_iobytes(self, **kwargs):
        """Test creating stream with body: IO[bytes]."""

        # create client
        with self.create_client(**kwargs) as client:
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
            message = client.messages.create(thread_id=thread.id, role="user", content="Hello, can you tell me a joke?")
            assert message.id
            print("Created message, message ID", message.id)

            # create body for stream
            body = {"assistant_id": agent.id, "stream": True}
            binary_body = json.dumps(body).encode("utf-8")

            # create stream
            with client.runs.stream(thread_id=thread.id, body=io.BytesIO(binary_body), stream=True) as stream:
                for event_type, event_data, _ in stream:
                    assert (
                        isinstance(event_data, (MessageDeltaChunk, ThreadMessage, ThreadRun, RunStep))
                        or event_type == AgentStreamEvent.DONE
                    )

            # delete agent and close client
            client.delete_agent(agent.id)
            print("Deleted agent")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_stream(self, **kwargs):
        """Test submitting tool outputs to stream."""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_submit_tool_outputs_to_stream(client=client, use_body=False, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_stream_with_body(self, **kwargs):
        """Test submitting tool outputs to stream with body: JSON."""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_submit_tool_outputs_to_stream(client=client, use_body=True, use_io=False)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_stream_with_iobytes(self, **kwargs):
        """Test submitting tool outputs to stream with body: IO[bytes]."""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_submit_tool_outputs_to_stream(client=client, use_body=True, use_io=True)

    def _do_test_submit_tool_outputs_to_stream(self, client, use_body, use_io):
        """helper function for submitting tool outputs to stream with different body inputs"""

        # Initialize agent tools
        functions = FunctionTool(functions=user_functions_recording)

        toolset = ToolSet()
        toolset.add(functions)
        # toolset.add(code_interpreter)

        # create agent
        agent = client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="You are helpful agent",
            tools=functions.definitions,
            tool_resources=functions.resources,
        )
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

        # create stream
        with client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
            for event_type, event_data, _ in stream:

                # Check if tools are needed
                if (
                    event_type == AgentStreamEvent.THREAD_RUN_REQUIRES_ACTION
                    and event_data.required_action.submit_tool_outputs
                ):
                    print("Requires action: submit tool outputs")
                    tool_calls = event_data.required_action.submit_tool_outputs.tool_calls

                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        client.runs.cancel(thread_id=thread.id, run_id=event_data.id)
                        break

                    # submit tool outputs to stream
                    tool_outputs = toolset.execute_tool_calls(tool_calls)

                    tool_event_handler = AgentEventHandler()
                    if tool_outputs:
                        if use_body:
                            body = {"tool_outputs": tool_outputs, "stream": True}
                            if use_io:
                                binary_body = json.dumps(body).encode("utf-8")
                                body = io.BytesIO(binary_body)
                            client.runs.submit_tool_outputs_stream(
                                thread_id=thread.id,
                                run_id=event_data.id,
                                body=body,
                                event_handler=tool_event_handler,
                                stream=True,
                            )
                        else:
                            client.runs.submit_tool_outputs_stream(
                                thread_id=thread.id,
                                run_id=event_data.id,
                                tool_outputs=tool_outputs,
                                event_handler=tool_event_handler,
                            )
                        for tool_event_type, tool_event_data, _ in tool_event_handler:
                            assert (
                                isinstance(tool_event_data, (MessageDeltaChunk, ThreadMessage, ThreadRun, RunStep))
                                or tool_event_type == AgentStreamEvent.DONE
                            )

                        print("Submitted tool outputs to stream")

            print("Stream processing completed")

        # check that messages used the tool
        messages = list(client.messages.list(thread_id=thread.id))
        print("Messages:", messages)
        tool_message = messages[0].content[0].text.value
        # TODO if testing live, uncomment these
        # hour12 = time.strftime("%H")
        # hour24 = time.strftime("%I")
        # minute = time.strftime("%M")
        # hour12string = str(hour12)+":"+str(minute)
        # hour24string = str(hour24)+":"+str(minute)
        # assert hour12string in tool_message or hour24string in tool_message
        recorded_time = "12:30"
        assert recorded_time in tool_message
        print("Used tool_outputs")

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        # client.close()

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - User function APIs
    # #
    # # **********************************************************************************

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_string_input(self, **kwargs):
        """Test submitting tool outputs to run with function input being a single string."""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.fetch_weather},
                content="Hello, what is the weather in New York?",
                expected_values=["sunny", "25"],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_multiple_strings(self, **kwargs):
        """Test submitting tool outputs to run with function input being multiple strings."""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.send_email},
                content="Hello, can you send an email to my manager (manager@microsoft.com) with the subject 'thanksgiving' asking when he is OOF?",
                possible_values=["email has been sent", "email has been successfully sent"],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_integers(self, **kwargs):
        """Test submitting tool outputs to run with function input being multiple integers."""

        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.calculate_sum},
                content="Hello, what is 293 + 243?",
                expected_values=["536"],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_integer(self, **kwargs):
        """Test submitting tool outputs to run with function input being a single integer."""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.convert_temperature},
                content="Hello, what is 32 degrees Celsius in Fahrenheit?",
                expected_values=["89.6"],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_multiple_dicts(self, **kwargs):
        """Test submitting tool outputs to run with function input being multiple dictionaries."""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.merge_dicts},
                content="If I have a dictionary with the key 'name' and value 'John' and another dictionary with the key 'age' and value '25', what is the merged dictionary?",
                possible_values=[
                    "{'name': 'john', 'age': '25'}",
                    "{'age': '25', 'name': 'john'}",
                    '{"name": "john", "age": "25"}',
                    '{"age": "25", "name": "john"}',
                    "{'name': 'john', 'age': 25}",
                    "{'age': 25, 'name': 'john'}",
                    '"name": "john",\n  "age": 25',
                    '"name": "john",\n  "age": "25"',
                    '"name": "john",\n    "age": 25',
                ],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_input_string_output_dict(self, **kwargs):
        """Test submitting tool outputs to run with function input being one string and output being a dictionary."""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.get_user_info},
                content="What is the name and email of the first user in our database?",
                expected_values=["alice", "alice@example.com"],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_list(self, **kwargs):
        """Test submitting tool outputs to run with function input being a list."""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.longest_word_in_sentences},
                content="Hello, please give me the longest word in the following sentences: 'Hello, how are you?' and 'I am good.'",
                expected_values=["hello", "good"],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tools_with_multiple_dicts2(self, **kwargs):
        """Test submitting tool outputs to run with function input being multiple dictionaries."""
        # create client
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AgentsClient)

            # run test with function input, content, and expected/possible values
            self._test_tools_with_different_functions(
                client=client,
                function={user_functions.process_records},
                content="Hello, please process the following records: [{'a': 10, 'b': 20}, {'x': 5, 'y': 15, 'z': 25}, {'m': 35}]",
                expected_values=["30", "45", "35"],
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def _test_tools_with_different_functions(
        self, client, function, content, expected_values=None, possible_values=None
    ):
        """Helper function to test submitting tool outputs to run with different function inputs."""
        # Initialize agent tools
        functions = FunctionTool(functions=function)
        toolset = ToolSet()
        toolset.add(functions)

        # create agent
        agent = client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="You are helpful agent",
            toolset=toolset,
        )
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.threads.create()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.messages.create(thread_id=thread.id, role="user", content=content)
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.runs.create(thread_id=thread.id, agent_id=agent.id)
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
            run = client.runs.get(thread_id=thread.id, run_id=run.id)

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
                    client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        # check that messages used the tool
        messages = list(client.messages.list(thread_id=thread.id, run_id=run.id))
        print("Messages:", messages)
        tool_message = messages[0].content[0].text.value
        if expected_values:
            for value in expected_values:
                assert value in tool_message.lower()
        if possible_values:
            value_used = False
            for value in possible_values:
                if value in tool_message.lower():
                    value_used = True
            assert value_used
        # assert expected_value in tool_message
        print("Used tool_outputs")

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")

    # # **********************************************************************************
    # #
    # #         NEGATIVE TESTS
    # #
    # # **********************************************************************************

    '''
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_invalid_code_interpreter_tool_resource(self, **kwargs):
        """test agent creation with invalid code interpreter tool resource."""
        # create client
        with self.create_client(**kwargs) as client:

            # initialize resources
            tool_resources = ToolResources()
            tool_resources.code_interpreter = CodeInterpreterToolResource()

            exception_message = ""
            try:
                client.create_agent(
                    model="gpt-4o",
                    name="my-agent",
                    instructions="You are helpful agent",
                    tools=[],
                    tool_resources=tool_resources,
                )
            except:
                print("exception here")
                # except ValueError as e:
                #     exception_message = e.args[0]
            else: 
                print("no exception")

            assert (
                exception_message
                == "Tools must contain a CodeInterpreterToolDefinition when tool_resources.code_interpreter is provided"
            )
            

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_invalid_file_search_tool_resource(self, **kwargs):
        """test agent creation with invalid file search tool resource."""
        # create client
        with self.create_client(**kwargs) as client:

            # initialize resources
            tool_resources = ToolResources()
            tool_resources.file_search = FileSearchToolResource()

            exception_message = ""
            try:
                client.create_agent(
                    model="gpt-4o", name="my-agent", instructions="You are helpful agent", tools=[], tool_resources=tool_resources
                )
            except:
                print("exception here")
                # except ValueError as e:
                #     exception_message = e.args[0]
            else: 
                print("no exception")

            assert exception_message == "Tools must contain a FileSearchToolDefinition when tool_resources.file_search is provided"
    '''

    @agentClientPreparer()
    @pytest.mark.skip("PASSES LIVE ONLY: recordings don't capture DNS lookup errors")
    @recorded_by_proxy
    def test_create_agent_with_invalid_file_search_tool_resource(self, **kwargs):
        """test agent creation with invalid file search tool resource."""
        # create client
        with self.create_client(**kwargs) as client:

            # initialize resources
            tool_resources = ToolResources()
            tool_resources.file_search = FileSearchToolResource()

            exception_message = ""
            try:
                client.create_agent(
                    model="gpt-4o",
                    name="my-agent",
                    instructions="You are helpful agent",
                    tools=[],
                    tool_resources=tool_resources,
                )
            except ValueError as e:
                exception_message = e.args[0]

            assert (
                exception_message
                == "Tools must contain a FileSearchToolDefinition when tool_resources.file_search is provided"
            )

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_file_search_add_vector_store(self, **kwargs):
        """Test the agent with file search and vector store creation."""

        # Create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AgentsClient)
        print("Created client")

        # Create file search tool
        file_search = FileSearchTool()

        # Adjust the file path to be relative to the test file location
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data", "product_info_1.md")
        openai_file = client.files.upload_and_poll(file_path=file_path, purpose="assistants")
        print(f"Uploaded file, file ID: {openai_file.id}")

        openai_vectorstore = client.vector_stores.create_and_poll(
            file_ids=[openai_file.id], name="my_vectorstore", polling_interval=self._sleep_time()
        )
        print(f"Created vector store, vector store ID: {openai_vectorstore.id}")

        file_search.add_vector_store(openai_vectorstore.id)

        toolset = ToolSet()
        toolset.add(file_search)
        print("Created toolset and added file search")

        # create agent
        agent = client.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
        )
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # check agent tools and vector store resources
        assert agent.tools
        assert agent.tools[0]["type"] == "file_search"
        assert agent.tool_resources
        assert agent.tool_resources["file_search"]["vector_store_ids"][0] == openai_vectorstore.id

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_and_poll(self, **kwargs):
        """test create vector store and poll"""
        # Create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AgentsClient)
        print("Created client")

        # Create vector store
        body = {"name": "test_vector_store", "metadata": {"key1": "value1", "key2": "value2"}}
        try:
            vector_store = client.vector_stores.create_and_poll(body=body, polling_interval=self._sleep_time(2))
            # check correct creation
            assert isinstance(vector_store, VectorStore)
            assert vector_store.name == "test_vector_store"
            assert vector_store.id
            assert vector_store.metadata == {"key1": "value1", "key2": "value2"}
            assert vector_store.status == "completed"
            print(f"Vector store created and polled successfully: {vector_store.id}")

        # throw error if failed to create and poll vector store
        except HttpResponseError as e:
            print(f"Failed to create and poll vector store: {e}")
            raise

        # close client
        client.close()

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store(self, **kwargs):
        """Test the agent with vector store creation."""
        # Create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AgentsClient)
        print("Created client")

        # Create vector store
        body = {"name": "test_vector_store", "metadata": {"key1": "value1", "key2": "value2"}}
        try:
            vector_store = client.vector_stores.create(body=body)
            print("here")
            print(vector_store)
            # check correct creation
            assert isinstance(vector_store, VectorStore)
            assert vector_store.name == "test_vector_store"
            assert vector_store.id
            assert vector_store.metadata == {"key1": "value1", "key2": "value2"}
            assert vector_store.status == "completed"
            print(f"Vector store created and polled successfully: {vector_store.id}")

        # throw error if failed to create and poll vector store
        except HttpResponseError as e:
            print(f"Failed to create and poll vector store: {e}")
            raise

        # close client
        client.close()

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_azure(self, **kwargs):
        """Test the agent with vector store creation."""
        self._do_test_create_vector_store(streaming=False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_vector_store_file_id(self, **kwargs):
        """Test the agent with vector store creation."""
        self._do_test_create_vector_store(file_path=self._get_data_file(), streaming=False, **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_azure_streaming(self, **kwargs):
        """Test the agent with vector store creation."""
        self._do_test_create_vector_store(streaming=True, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_vector_store_file_id_streaming(self, **kwargs):
        """Test the agent with vector store creation."""
        self._do_test_create_vector_store(file_path=self._get_data_file(), streaming=True, **kwargs)

    def _do_test_create_vector_store(self, streaming, **kwargs):
        """Test the agent with vector store creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = self._get_file_id_maybe(ai_client, **kwargs)
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
        vector_store = ai_client.vector_stores.create_and_poll(
            file_ids=file_ids, data_sources=ds, name="my_vectorstore", polling_interval=self._sleep_time()
        )
        assert vector_store.id
        self._test_file_search(ai_client, vector_store, file_id, streaming)

    @agentClientPreparer()
    @pytest.mark.skip("Not deployed in all regions.")
    @recorded_by_proxy
    def test_vector_store_threads_file_search_azure(self, **kwargs):
        """Test file search when azure asset ids are sopplied during thread creation."""
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
        agent = ai_client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        assert agent.id

        thread = ai_client.threads.create(tool_resources=ToolResources(file_search=fs))
        assert thread.id
        # create message
        message = ai_client.messages.create(thread_id=thread.id, role="user", content="What does the attachment say?")
        assert message.id, "The message was not created."

        run = ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = list(ai_client.messages.list(thread_id=thread.id))
        assert len(messages)
        ai_client.delete_agent(agent.id)
        ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_vector_store_add_file_file_id(self, **kwargs):
        """Test adding single file to vector store withn file ID."""
        self._do_test_create_vector_store_add_file(file_path=self._get_data_file(), streaming=False, **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_add_file_azure(self, **kwargs):
        """Test adding single file to vector store with azure asset ID."""
        self._do_test_create_vector_store_add_file(streaming=False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_vector_store_add_file_file_id_streaming(self, **kwargs):
        """Test adding single file to vector store withn file ID."""
        self._do_test_create_vector_store_add_file(file_path=self._get_data_file(), streaming=True, **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_add_file_azure_streaming(self, **kwargs):
        """Test adding single file to vector store with azure asset ID."""
        self._do_test_create_vector_store_add_file(streaming=True, **kwargs)

    def _do_test_create_vector_store_add_file(self, streaming, **kwargs):
        """Test adding single file to vector store."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = self._get_file_id_maybe(ai_client, **kwargs)
        if file_id:
            ds = None
        else:
            ds = VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                asset_type="uri_asset",
            )
        vector_store = ai_client.vector_stores.create_and_poll(
            file_ids=[], name="sample_vector_store", polling_interval=self._sleep_time()
        )
        assert vector_store.id
        vector_store_file = ai_client.vector_store_files.create(
            vector_store_id=vector_store.id, data_source=ds, file_id=file_id
        )
        assert vector_store_file.id
        self._test_file_search(ai_client, vector_store, file_id, streaming)
        ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_vector_store_batch_file_ids(self, **kwargs):
        """Test adding multiple files to vector store with file IDs."""
        self._do_test_create_vector_store_batch(streaming=False, file_path=self._get_data_file(), **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_batch_azure(self, **kwargs):
        """Test adding multiple files to vector store with azure asset IDs."""
        self._do_test_create_vector_store_batch(streaming=False, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_vector_store_batch_file_ids_streaming(self, **kwargs):
        """Test adding multiple files to vector store with file IDs."""
        self._do_test_create_vector_store_batch(streaming=True, file_path=self._get_data_file(), **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_batch_azure_streaming(self, **kwargs):
        """Test adding multiple files to vector store with azure asset IDs."""
        self._do_test_create_vector_store_batch(streaming=True, **kwargs)

    def _do_test_create_vector_store_batch(self, streaming, **kwargs):
        """Test the agent with vector store creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = self._get_file_id_maybe(ai_client, **kwargs)
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
        vector_store = ai_client.vector_stores.create_and_poll(
            file_ids=[], name="sample_vector_store", polling_interval=self._sleep_time()
        )
        assert vector_store.id
        vector_store_file_batch = ai_client.vector_store_file_batches.create_and_poll(
            vector_store_id=vector_store.id, data_sources=ds, file_ids=file_ids, polling_interval=self._sleep_time()
        )
        assert vector_store_file_batch.id
        self._test_file_search(ai_client, vector_store, file_id, streaming)
        ai_client.close()

    def _test_file_search(
        self, ai_client: AgentsClient, vector_store: VectorStore, file_id: Optional[str], streaming: bool
    ) -> None:
        """Test the file search"""
        file_search = FileSearchTool(vector_store_ids=[vector_store.id])
        agent = ai_client.create_agent(
            model="gpt-4",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        assert agent.id

        thread = ai_client.threads.create()
        assert thread.id

        # create message
        message = ai_client.messages.create(thread_id=thread.id, role="user", content="What does the attachment say?")
        assert message.id, "The message was not created."

        if streaming:
            thread_run = None
            with ai_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
                for _, event_data, _ in stream:
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
            run = ai_client.runs.get(thread_id=thread_run.thread_id, run_id=thread_run.id)
            assert run is not None
        else:
            run = ai_client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
            )

        ai_client.vector_stores.delete(vector_store.id)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = list(ai_client.messages.list(thread_id=thread.id))
        assert len(messages)
        ai_client.delete_agent(agent.id)
        self._remove_file_maybe(file_id, ai_client)
        ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_message_attachement_azure(self, **kwargs):
        """Test message attachment with azure ID."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        self._do_test_message_attachment(data_source=ds, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_message_attachment_file_ids(self, **kwargs):
        """Test message attachment with file ID."""
        self._do_test_message_attachment(file_path=self._get_data_file(), **kwargs)

    def _do_test_message_attachment(self, **kwargs):
        """Test agent with the message attachment."""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = self._get_file_id_maybe(ai_client, **kwargs)

        # Create agent with file search tool
        agent = ai_client.create_agent(
            model="gpt-4-1106-preview",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
        )
        assert agent.id, "Agent was not created"

        thread = ai_client.threads.create()
        assert thread.id, "The thread was not created."

        # Create a message with the file search attachment
        # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
        attachment = MessageAttachment(
            file_id=file_id,
            data_source=kwargs.get("data_source"),
            tools=[
                FileSearchTool().definitions[0],
                CodeInterpreterTool().definitions[0],
            ],
        )
        message = ai_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="What does the attachment say?",
            attachments=[attachment],
        )
        assert message.id, "The message was not created."

        run = ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.id, "The run was not created."
        self._remove_file_maybe(file_id, ai_client)
        ai_client.delete_agent(agent.id)

        messages = list(ai_client.messages.list(thread_id=thread.id))
        assert len(messages), "No messages were created"
        ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy
    def test_create_agent_with_interpreter_azure(self, **kwargs):
        """Test Create agent with code interpreter with azure asset ids."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        self._do_test_create_agent_with_interpreter(data_sources=[ds], **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_agent_with_interpreter_file_ids(self, **kwargs):
        """Test Create agent with code interpreter with file IDs."""
        self._do_test_create_agent_with_interpreter(file_path=self._get_data_file(), **kwargs)

    def _do_test_create_agent_with_interpreter(self, **kwargs):
        """Test create agent with code interpreter and project asset id"""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        code_interpreter = CodeInterpreterTool()

        file_id = None
        if "file_path" in kwargs:
            file = ai_client.files.upload_and_poll(file_path=kwargs["file_path"], purpose=FilePurpose.AGENTS)
            assert file.id, "The file was not uploaded."
            file_id = file.id

        cdr = CodeInterpreterToolResource(
            file_ids=[file_id] if file_id else None,
            data_sources=kwargs.get("data_sources"),
        )
        tr = ToolResources(code_interpreter=cdr)
        # notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
        agent = ai_client.create_agent(
            model="gpt-4-1106-preview",
            name="my-agent",
            instructions="You are helpful agent",
            tools=code_interpreter.definitions,
            tool_resources=tr,
        )
        assert agent.id, "Agent was not created"

        thread = ai_client.threads.create()
        assert thread.id, "The thread was not created."

        message = ai_client.messages.create(thread_id=thread.id, role="user", content="What does the attachment say?")
        assert message.id, "The message was not created."

        run = ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.id, "The run was not created."
        self._remove_file_maybe(file_id, ai_client)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        ai_client.delete_agent(agent.id)
        messages = list(ai_client.messages.list(thread_id=thread.id))
        assert len(messages), "No messages were created"
        ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy
    def test_create_thread_with_interpreter_azure(self, **kwargs):
        """Test Create agent with code interpreter with azure asset ids."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        self._do_test_create_thread_with_interpreter(data_sources=[ds], **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_thread_with_interpreter_file_ids(self, **kwargs):
        """Test Create agent with code interpreter with file IDs."""
        self._do_test_create_thread_with_interpreter(file_path=self._get_data_file(), **kwargs)

    def _do_test_create_thread_with_interpreter(self, **kwargs):
        """Test create agent with code interpreter and project asset id"""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        code_interpreter = CodeInterpreterTool()

        file_id = None
        if "file_path" in kwargs:
            file = ai_client.files.upload_and_poll(file_path=kwargs["file_path"], purpose=FilePurpose.AGENTS)
            assert file.id, "The file was not uploaded."
            file_id = file.id

        cdr = CodeInterpreterToolResource(
            file_ids=[file_id] if file_id else None,
            data_sources=kwargs.get("data_sources"),
        )
        tr = ToolResources(code_interpreter=cdr)
        # notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
        agent = ai_client.create_agent(
            model="gpt-4-1106-preview",
            name="my-agent",
            instructions="You are helpful agent",
            tools=code_interpreter.definitions,
        )
        assert agent.id, "Agent was not created"

        thread = ai_client.threads.create(tool_resources=tr)
        assert thread.id, "The thread was not created."

        message = ai_client.messages.create(thread_id=thread.id, role="user", content="What does the attachment say?")
        assert message.id, "The message was not created."

        run = ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.id, "The run was not created."
        self._remove_file_maybe(file_id, ai_client)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        ai_client.delete_agent(agent.id)
        messages = list(ai_client.messages.list(thread_id=thread.id))
        assert len(messages)
        ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("Not deployed in all regions.")
    @recorded_by_proxy
    def test_create_agent_with_inline_vs_azure(self, **kwargs):
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
        agent = ai_client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=ToolResources(file_search=fs),
        )
        assert agent.id

        thread = ai_client.threads.create()
        assert thread.id
        # create message
        message = ai_client.messages.create(thread_id=thread.id, role="user", content="What does the attachment say?")
        assert message.id, "The message was not created."

        run = ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = list(ai_client.messages.list(thread_id=thread.id))
        assert len(messages)
        ai_client.delete_agent(agent.id)
        ai_client.close()

    @agentClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy
    def test_create_attachment_in_thread_azure(self, **kwargs):
        """Create thread with message attachment inline with azure asset IDs."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        self._do_test_create_attachment_in_thread_azure(data_source=ds, **kwargs)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_create_attachment_in_thread_file_ids(self, **kwargs):
        """Create thread with message attachment inline with azure asset IDs."""
        self._do_test_create_attachment_in_thread_azure(file_path=self._get_data_file(), **kwargs)

    def _do_test_create_attachment_in_thread_azure(self, **kwargs):
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AgentsClient)

        file_id = self._get_file_id_maybe(ai_client, **kwargs)

        file_search = FileSearchTool()
        agent = ai_client.create_agent(
            model="gpt-4-1106-preview",
            name="my-agent",
            instructions="Hello, you are helpful agent and can search information from uploaded files",
            tools=file_search.definitions,
        )
        assert agent.id

        # create message
        attachment = MessageAttachment(
            file_id=file_id,
            data_source=kwargs.get("data_source"),
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
        thread = ai_client.threads.create(messages=[message])
        assert thread.id

        run = ai_client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
        )
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = list(ai_client.messages.list(thread_id=thread.id))
        assert len(messages)
        ai_client.delete_agent(agent.id)
        ai_client.close()

    def _get_azure_ai_search_tool(self, **kwargs):
        """Get the azure AI search tool."""
        conn_id = kwargs.pop("azure_ai_agents_tests_search_connection_id", "my-search-connection-ID")
        index_name = kwargs.pop("azure_ai_agents_tests_search_index_name", "my-search-index")

        return AzureAISearchTool(
            index_connection_id=conn_id,
            index_name=index_name,
        )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_azure_ai_search_tool(self, **kwargs):
        """Test using the AzureAISearchTool with an agent."""
        azure_search_tool = self._get_azure_ai_search_tool(**kwargs)
        with self.create_client(by_endpoint=True, **kwargs) as client:
            assert isinstance(client, AgentsClient)

            self._do_test_tool(
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
    @recorded_by_proxy
    def test_azure_ai_search_tool_streaming(self, **kwargs):
        """Test using the AzureAISearchTool with an agent in streaming scenario."""
        azure_search_tool = self._get_azure_ai_search_tool(**kwargs)
        with self.create_client(by_endpoint=True, **kwargs) as client:
            assert isinstance(client, AgentsClient)
            self._do_test_tool_streaming(
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
    @recorded_by_proxy
    def test_include_file_search_results_no_stream(self, **kwargs):
        """Test using include_file_search."""
        self._do_test_include_file_search_results(use_stream=False, include_content=True, **kwargs)
        self._do_test_include_file_search_results(use_stream=False, include_content=False, **kwargs)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_include_file_search_results_stream(self, **kwargs):
        """Test using include_file_search with streaming."""
        self._do_test_include_file_search_results(use_stream=True, include_content=True, **kwargs)
        self._do_test_include_file_search_results(use_stream=True, include_content=False, **kwargs)

    def _do_test_include_file_search_results(self, use_stream, include_content, **kwargs):
        """Run the test with file search results."""
        with self.create_client(**kwargs) as ai_client:
            ds = [
                VectorStoreDataSource(
                    asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                    asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
                )
            ]
            vector_store = ai_client.vector_stores.create_and_poll(
                file_ids=[], data_sources=ds, name="my_vectorstore", polling_interval=self._sleep_time()
            )
            # vector_store = await ai_client.vector_stores.get('vs_M9oxKG7JngORHcYNBGVZ6Iz3')
            assert vector_store.id

            file_search = FileSearchTool(vector_store_ids=[vector_store.id])
            agent = ai_client.create_agent(
                model="gpt-4o",
                name="my-agent",
                instructions="Hello, you are helpful agent and can search information from uploaded files",
                tools=file_search.definitions,
                tool_resources=file_search.resources,
            )
            assert agent.id
            thread = ai_client.threads.create()
            assert thread.id
            # create message
            message = ai_client.messages.create(
                thread_id=thread.id,
                role="user",
                # content="What does the attachment say?"
                content="What Contoso Galaxy Innovations produces?",
            )
            assert message.id, "The message was not created."
            include = [RunAdditionalFieldList.FILE_SEARCH_CONTENTS] if include_content else None

            if use_stream:
                run = None
                with ai_client.runs.stream(thread_id=thread.id, agent_id=agent.id, include=include) as stream:
                    for event_type, event_data, _ in stream:
                        if isinstance(event_data, ThreadRun):
                            run = event_data
                        elif event_type == AgentStreamEvent.THREAD_RUN_STEP_COMPLETED:
                            if isinstance(event_data.step_details, RunStepToolCallDetails):
                                self._assert_file_search_valid(event_data.step_details.tool_calls[0], include_content)
                        elif event_type == AgentStreamEvent.DONE:
                            print("Stream completed.")
                            break
            else:
                run = ai_client.runs.create_and_process(
                    thread_id=thread.id, agent_id=agent.id, include=include, polling_interval=self._sleep_time()
                )
                assert run.status == RunStatus.COMPLETED
            assert run is not None
            steps = list(ai_client.run_steps.list(thread_id=thread.id, run_id=run.id, include=include))
            # The 1st (not 0th) step is a tool call.
            step_id = steps[1].id

            one_step = ai_client.run_steps.get(thread_id=thread.id, run_id=run.id, step_id=step_id, include=include)

            self._assert_file_search_valid(one_step.step_details.tool_calls[0], include_content)
            self._assert_file_search_valid(steps[1].step_details.tool_calls[0], include_content)

            messages = list(ai_client.messages.list(thread_id=thread.id))
            assert len(messages) > 1

            ai_client.vector_stores.delete(vector_store.id)
            # delete agent and close client
            ai_client.delete_agent(agent.id)
            print("Deleted agent")
            ai_client.close()

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
    @recorded_by_proxy
    def test_agents_with_json_schema(self, **kwargs):
        """Test structured output from the agent."""
        with self.create_client(**kwargs) as ai_client:
            agent = ai_client.create_agent(
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

            thread = ai_client.threads.create()
            assert thread.id

            message = ai_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=("The mass of the Mars is 6.4171E23 kg"),
            )
            assert message.id

            run = ai_client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
            )

            assert run.status == RunStatus.COMPLETED, run.last_error.message

            ai_client.delete_agent(agent.id)

            messages = list(ai_client.messages.list(thread_id=thread.id))

            planet_info = []
            # The messages are returned in reverse order; iterate and keep only agent-text contents.
            for data_point in reversed(messages):
                last_message_content = data_point.content[-1]
                if isinstance(last_message_content, MessageTextContent) and data_point.role == MessageRole.AGENT:
                    planet_info.append(json.loads(last_message_content.text.value))

            assert len(planet_info) == 1
            assert len(planet_info[0]) == 2
            assert planet_info[0].get("mass") == pytest.approx(6.4171e23, 1e22)
            assert planet_info[0].get("planet") == "Mars"

    def _get_file_id_maybe(self, ai_client: AgentsClient, **kwargs) -> str:
        """Return file id if kwargs has file path."""
        if "file_path" in kwargs:
            file = ai_client.files.upload_and_poll(file_path=kwargs["file_path"], purpose=FilePurpose.AGENTS)
            assert file.id, "The file was not uploaded."
            return file.id
        return None

    def _remove_file_maybe(self, file_id: str, ai_client: AgentsClient) -> None:
        """Remove file if we have file ID."""
        if file_id:
            ai_client.files.delete(file_id)

    @agentClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy
    def test_code_interpreter_and_save_file(self, **kwargs):
        output_file_exist = False

        # create client
        with self.create_client(**kwargs) as client:

            with tempfile.TemporaryDirectory() as temp_dir:

                # create a temporary input file for upload
                test_file_path = os.path.join(temp_dir, "input.txt")

                with open(test_file_path, "w") as f:
                    f.write("This is a test file")

                file: FileInfo = client.files.upload_and_poll(file_path=test_file_path, purpose=FilePurpose.AGENTS)

                # create agent
                code_interpreter = CodeInterpreterTool(file_ids=[file.id])
                agent = client.create_agent(
                    model="gpt-4-1106-preview",
                    name="my-agent",
                    instructions="You are helpful agent",
                    tools=code_interpreter.definitions,
                    tool_resources=code_interpreter.resources,
                )
                print(f"Created agent, agent ID: {agent.id}")

                thread = client.threads.create()
                print(f"Created thread, thread ID: {thread.id}")

                # create a message
                message = client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content="Create an image file same as the text file and give me file id?",
                )
                print(f"Created message, message ID: {message.id}")

                # create run
                run = client.runs.create_and_process(
                    thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
                )
                print(f"Run finished with status: {run.status}")

                # delete file
                client.files.delete(file.id)
                print("Deleted file")

                # get messages
                messages = list(client.messages.list(thread_id=thread.id))
                print(f"Messages: {messages}")

                last_msg = client.messages.get_last_message_text_by_role(thread_id=thread.id, role=MessageRole.AGENT)
                if last_msg:
                    print(f"Last Message: {last_msg.text.value}")

                for message in messages:
                    for annotation in message.file_path_annotations:
                        file_id = annotation.file_path.file_id
                        print(f"Image File ID: {file_id}")

                        temp_file_path = os.path.join(temp_dir, "output.png")
                        client.files.save(
                            file_id=file_id,
                            file_name="output.png",
                            target_dir=temp_dir,
                        )
                        output_file_exist = os.path.exists(temp_file_path)

            assert output_file_exist

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
    @recorded_by_proxy
    def test_azure_function_call(self, **kwargs):
        """Test calling Azure functions."""
        storage_queue = kwargs["azure_ai_agents_tests_storage_queue"]
        with self.create_client(by_endpoint=True, **kwargs) as client:
            azure_function_tool = self._get_azure_function_tool(storage_queue)

            self._do_test_tool(
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
    @recorded_by_proxy
    def test_azure_function_call_streaming(self, **kwargs):
        """Test calling Azure functions in streaming scenarios."""
        storage_queue = kwargs["azure_ai_agents_tests_storage_queue"]
        with self.create_client(by_endpoint=True, **kwargs) as client:
            azure_function_tool = self._get_azure_function_tool(storage_queue)

            self._do_test_tool_streaming(
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
    @recorded_by_proxy
    def test_browser_automation_tool(self, **kwargs):
        connection_id = kwargs["azure_ai_agents_tests_playwright_connection_id"]
        with self.create_client(by_endpoint=True, **kwargs) as client:
            browser_automation_tool = BrowserAutomationTool(connection_id=connection_id)
            self._do_test_tool(
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
    @recorded_by_proxy
    def test_deep_research_tool(self, **kwargs):
        """Test using the DeepResearchTool with an agent."""
        # create client
        with self.create_client(by_endpoint=True, **kwargs) as client:
            assert isinstance(client, AgentsClient)

            # Get connection ID and model name from test environment
            bing_conn_id = kwargs.pop("azure_ai_agents_tests_bing_connection_id")
            deep_research_model = kwargs.pop("azure_ai_agents_tests_deep_research_model")

            # Create DeepResearchTool
            deep_research_tool = DeepResearchTool(
                bing_grounding_connection_id=bing_conn_id,
                deep_research_model=deep_research_model,
            )

            self._do_test_tool(
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
    @pytest.mark.skip("Recordings not yet implemented.")
    @recorded_by_proxy
    def test_client_with_thread_messages(self, **kwargs):
        """Test agent with thread messages."""
        with self.create_client(**kwargs) as client:

            # [START create_agent]
            agent = client.create_agent(
                model="gpt-4-1106-preview",
                name="my-agent",
                instructions="You are a personal electronics tutor. Write and run code to answer questions.",
            )
            assert agent.id, "The agent was not created."
            thread = client.threads.create()
            assert thread.id, "Thread was not created"

            message = client.messages.create(
                thread_id=thread.id, role="user", content="What is the equation of light energy?"
            )
            assert message.id, "The message was not created."

            additional_messages = [
                ThreadMessageOptions(role=MessageRole.AGENT, content="E=mc^2"),
                ThreadMessageOptions(role=MessageRole.USER, content="What is the impedance formula?"),
            ]
            run = client.runs.create(thread_id=thread.id, agent_id=agent.id, additional_messages=additional_messages)

            # poll the run as long as run status is queued or in progress
            while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS]:
                # wait for a second
                time.sleep(self._sleep_time())
                run = client.runs.get(
                    thread_id=thread.id,
                    run_id=run.id,
                )
            assert run.status in RunStatus.COMPLETED

            client.delete_agent(agent.id)
            messages = list(client.messages.list(thread_id=thread.id))
            assert messages, "No data was received from the agent."

    def _get_connected_agent_tool(self, client, model_name, connected_agent_name):
        """Get the connected agent tool."""
        stock_price_agent = client.create_agent(
            model=model_name,
            name=connected_agent_name,
            instructions=(
                "Your job is to get the stock price of a company. If asked for the Microsoft stock price, always return $350."
            ),
        )
        return ConnectedAgentTool(
            id=stock_price_agent.id, name=connected_agent_name, description="Gets the stock price of a company"
        )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_connected_agent_tool(self, **kwargs):
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            connected_agent_name = "stock_bot"
            connected_agent = self._get_connected_agent_tool(client, model_name, connected_agent_name)

            try:
                self._do_test_tool(
                    client=client,
                    model_name=model_name,
                    tool_to_test=connected_agent,
                    instructions="You are a helpful assistant, and use the connected agents to get stock prices.",
                    prompt="What is the stock price of Microsoft?",
                    expected_class=RunStepConnectedAgentToolCall,
                )
            finally:
                client.delete_agent(connected_agent.connected_agent.id)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_tool_streaming_connected_agent(self, **kwargs):
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            connected_agent_name = "stock_bot"
            connected_agent = self._get_connected_agent_tool(client, model_name, connected_agent_name)

            try:
                self._do_test_tool_streaming(
                    client=client,
                    model_name=model_name,
                    tool_to_test=connected_agent,
                    instructions="You are a helpful assistant, and use the connected agents to get stock prices.",
                    prompt="What is the stock price of Microsoft?",
                    expected_delta_class=RunStepDeltaConnectedAgentToolCall,
                )
            finally:
                client.delete_agent(connected_agent.connected_agent.id)

    def _get_file_search_tool_and_file_id(self, client, **kwargs):
        """Helper method to get the file search tool."""
        ds = [
            VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_agents_tests_data_path"],
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
        ]
        vector_store = client.vector_stores.create_and_poll(
            data_sources=ds, name="my_vectorstore", polling_interval=self._sleep_time()
        )
        file_id = None
        for fle in client.vector_store_files.list(vector_store.id):
            # We have only one file in vector store.
            file_id = fle.id
        assert file_id is not None, "No files were found in the vector store."
        return FileSearchTool(vector_store_ids=[vector_store.id]), file_id

    @agentClientPreparer()
    @recorded_by_proxy
    def test_file_search_tool(self, **kwargs):
        """Test file search tool."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            file_search_tool, file_id = self._get_file_search_tool_and_file_id(client, **kwargs)
            assert file_search_tool.resources.file_search is not None
            assert file_search_tool.resources.file_search.vector_store_ids

            try:
                self._do_test_tool(
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
                client.vector_stores.delete(file_search_tool.resources.file_search.vector_store_ids[0])

    @agentClientPreparer()
    @recorded_by_proxy
    def test_file_search_tool_streaming(self, **kwargs):
        """Test file search tool."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            file_search_tool, file_id = self._get_file_search_tool_and_file_id(client, **kwargs)
            assert file_search_tool.resources.file_search is not None
            assert file_search_tool.resources.file_search.vector_store_ids

            try:
                self._do_test_tool_streaming(
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
                client.vector_stores.delete(file_search_tool.resources.file_search.vector_store_ids[0])

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
    @recorded_by_proxy
    def test_open_api_tool(self, **kwargs):
        """Test open API tool call in non-streaming Scenario."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            openapi_tool = self._get_open_api_tool()

            self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=openapi_tool,
                instructions="You are helpful agent",
                prompt="What is the weather in Centralia, PA?",
                expected_class=RunStepOpenAPIToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_open_api_tool_streaming(self, **kwargs):
        """Test open API tool call in streaming Scenario."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            openapi_tool = self._get_open_api_tool()

            self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=openapi_tool,
                instructions="You are helpful agent",
                prompt="What is the weather in Centralia, PA?",
                expected_delta_class=RunStepDeltaOpenAPIToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_bing_grounding_tool(self, **kwargs):
        """Test Bing grounding tool call in non-streaming Scenario."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            openapi_tool = BingGroundingTool(connection_id=kwargs.get("azure_ai_agents_tests_bing_connection_id"))

            self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=openapi_tool,
                instructions="You are helpful agent",
                prompt="How does wikipedia explain Euler's Identity?",
                expected_class=RunStepBingGroundingToolCall,
                uri_annotation=MessageTextUrlCitationDetails(
                    url="*",
                    title="*",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_bing_grounding_tool_streaming(self, **kwargs):
        """Test Bing grounding tool call in streaming Scenario."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            openapi_tool = BingGroundingTool(connection_id=kwargs.get("azure_ai_agents_tests_bing_connection_id"))

            self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=openapi_tool,
                instructions="You are helpful agent",
                prompt="How does wikipedia explain Euler's Identity?",
                expected_delta_class=RunStepDeltaBingGroundingToolCall,
                uri_annotation=MessageTextUrlCitationDetails(
                    url="*",
                    title="*",
                ),
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_custom_bing_grounding_tool(self, **kwargs):
        """Test Bing grounding tool call in non-streaming Scenario."""
        with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            bing_custom_tool = BingCustomSearchTool(
                connection_id=kwargs.get("azure_ai_agents_tests_bing_custom_connection_id"),
                instance_name=kwargs.get("azure_ai_agents_tests_bing_configuration_name"),
            )

            self._do_test_tool(
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
    @recorded_by_proxy
    def test_custom_bing_grounding_tool_streaming(self, **kwargs):
        """Test Bing grounding tool call in streaming Scenario."""
        with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            bing_custom_tool = BingCustomSearchTool(
                connection_id=kwargs.get("azure_ai_agents_tests_bing_custom_connection_id"),
                instance_name=kwargs.get("azure_ai_agents_tests_bing_configuration_name"),
            )

            self._do_test_tool_streaming(
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
    @recorded_by_proxy
    def test_microsoft_fabric_tool(self, **kwargs):
        """Test Microsoft Fabric tool call in non-streaming Scenario."""
        with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            fabric_tool = FabricTool(connection_id=kwargs.get("azure_ai_agents_tests_fabric_connection_id"))

            self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=fabric_tool,
                instructions="You are helpful agent",
                prompt="What are top 3 weather events with largest revenue loss?",
                expected_class=RunStepMicrosoftFabricToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_microsoft_fabric_tool_streaming(self, **kwargs):
        """Test Microsoft Fabric tool call in streaming Scenario."""
        with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            fabric_tool = FabricTool(connection_id=kwargs.get("azure_ai_agents_tests_fabric_connection_id"))

            self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=fabric_tool,
                instructions="You are helpful agent",
                prompt="What are top 3 weather events with largest revenue loss?",
                expected_delta_class=RunStepDeltaMicrosoftFabricToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_sharepoint_tool(self, **kwargs):
        """Test SharePoint tool call in non-streaming Scenario."""
        with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            sharepoint_tool = SharepointTool(connection_id=kwargs.get("azure_ai_agents_tests_sharepoint_connection_id"))

            self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=sharepoint_tool,
                instructions="You are helpful agent",
                prompt="Hello, summarize the key points of the first document in the list.",
                expected_class=RunStepSharepointToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_sharepoint_tool_streaming(self, **kwargs):
        """Test SharePoint tool call in streaming Scenario."""
        with self.create_client(by_endpoint=True, **kwargs) as client:
            model_name = "gpt-4o"
            sharepoint_tool = SharepointTool(connection_id=kwargs.get("azure_ai_agents_tests_sharepoint_connection_id"))

            self._do_test_tool_streaming(
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
    @recorded_by_proxy
    def test_code_interpreter_tool(self, **kwargs):
        """Test file search tool."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            code_iterpreter = self._get_code_interpreter_tool(**kwargs)

            self._do_test_tool(
                client=client,
                model_name=model_name,
                tool_to_test=code_iterpreter,
                instructions="You are helpful agent",
                prompt="What feature does Smart Eyewear offer?",
                expected_class=RunStepCodeInterpreterToolCall,
            )

    @agentClientPreparer()
    @recorded_by_proxy
    def test_code_interpreter_tool_streaming(self, **kwargs):
        """Test file search tool."""
        with self.create_client(**kwargs, by_endpoint=True) as client:
            model_name = "gpt-4o"
            code_iterpreter = self._get_code_interpreter_tool(**kwargs)

            self._do_test_tool_streaming(
                client=client,
                model_name=model_name,
                tool_to_test=code_iterpreter,
                instructions="You are helpful agent",
                prompt="What feature does Smart Eyewear offer?",
                expected_delta_class=RunStepDeltaCodeInterpreterToolCall,
            )

    def _do_test_tool(
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

        Note: kwargs may take:
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
        agent = client.create_agent(
            model=model_name,
            name="my-assistant",
            instructions=instructions,
            tools=tool_to_test.definitions,
            tool_resources=tool_to_test.resources,
            headers=headers,
        )
        thread = client.threads.create()
        client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=prompt,
        )
        run = client.runs.create_and_process(
            thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time(polling_interval)
        )
        try:
            assert run.status != RunStatus.FAILED, run.last_error

            # Fetch and log all messages
            messages = list(client.messages.list(thread_id=thread.id))
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
                for run_step in client.run_steps.list(thread_id=thread.id, run_id=run.id):
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
            client.delete_agent(agent.id)
            client.threads.delete(thread.id)

    def _do_test_tool_streaming(
        self,
        client,
        model_name,
        tool_to_test,
        instructions,
        prompt,
        expected_delta_class: Type,
        headers: Dict[str, str] = None,
        uri_annotation: MessageTextUrlCitationDetails = None,
        file_annotation: MessageTextFileCitationDetails = None,
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
        agent = client.create_agent(
            model=model_name,
            name="my-assistant",
            instructions=instructions,
            tools=tool_to_test.definitions,
            tool_resources=tool_to_test.resources,
            headers=headers,
        )
        thread = client.threads.create()
        client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=prompt,
        )

        try:
            with client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:

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
                for event_type, event_data, _ in stream:

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
                ), f"The text {agent_message_regex} was not found: {' '.join(received_messages)}."

                assert (
                    has_uri_annotation
                ), f"The annotation [{uri_annotation.title}]({uri_annotation.url}) was not found."
                assert has_file_annotation, f"The annotation {file_annotation} was not found."
            # Assertions on messages
            messages = list(client.messages.list(thread_id=thread.id))
            assert len(messages) > 1
        finally:
            client.delete_agent(agent.id)
            client.threads.delete(thread.id)

    def _get_mcp_tool(self):
        """Helper method to get an MCP tool."""
        return McpTool(
            server_label="github",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            allowed_tools=[],  # Optional: specify allowed tools
        )

    def _get_computer_use_tool(self):
        """Helper method to get a Computer Use tool (preview)."""
        return ComputerUseTool(display_width=1024, display_height=768, environment="browser")

    @agentClientPreparer()
    @recorded_by_proxy
    def test_mcp_tool(self, **kwargs):
        """Test MCP tool call."""
        mcp_tool = self._get_mcp_tool()
        with self.create_client(**kwargs, by_endpoint=True) as agents_client:
            agent = agents_client.create_agent(
                model="gpt-4o",
                name="my-mcp-agent",
                instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                tools=mcp_tool.definitions,
            )
            thread = agents_client.threads.create()
            try:
                agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content="Please summarize the Azure REST API specifications Readme",
                )
                mcp_tool.update_headers("SuperSecret", "123456")
                run = agents_client.runs.create(
                    thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources
                )
                was_approved = False
                while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                    time.sleep(self._sleep_time())
                    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

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
                            agents_client.runs.submit_tool_outputs(
                                thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                            )
                assert was_approved, "The run was never approved."
                assert run.status != RunStatus.FAILED, run.last_error

                is_activity_step_found = False
                is_tool_call_step_found = False
                for run_step in agents_client.run_steps.list(thread_id=thread.id, run_id=run.id):
                    if isinstance(run_step.step_details, RunStepActivityDetails):
                        is_activity_step_found = True
                    if isinstance(run_step.step_details, RunStepToolCallDetails):
                        for tool_call in run_step.step_details.tool_calls:
                            if isinstance(tool_call, RunStepMcpToolCall):
                                is_tool_call_step_found = True
                                break
                assert is_activity_step_found, "RunStepMcpToolCall was not found."
                assert is_tool_call_step_found, "No RunStepMcpToolCall"
                messages = list(agents_client.messages.list(thread_id=thread.id))
                assert len(messages) > 1
            finally:
                agents_client.threads.delete(thread.id)
                agents_client.delete_agent(agent.id)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_computer_use_tool(self, **kwargs):
        """Test Computer Use tool call.

        Model name is fixed to the preview model as required: 'computer-use-preview'.
        """
        cu_tool = self._get_computer_use_tool()
        with self.create_client(**kwargs, by_endpoint=True) as agents_client:
            agent = agents_client.create_agent(
                model="computer-use-preview",  # NOTE: spelling per requirement
                name="my-cu-agent",
                instructions=(
                    "You are a computer automation assistant. Use the computer_use_preview tool to interact with the screen when needed."
                ),
                tools=cu_tool.definitions,
            )
            thread = agents_client.threads.create()
            try:
                input_message = (
                    "I can see a web browser with bing.com open and the cursor in the search box."
                    "Type 'movies near me' without pressing Enter or any other key. Only type 'movies near me'."
                )
                image_base64 = image_to_base64(self._get_screenshot_file())
                img_url = f"data:image/jpeg;base64,{image_base64}"
                url_param = MessageImageUrlParam(url=img_url, detail="high")
                content_blocks: List[MessageInputContentBlock] = [
                    MessageInputTextBlock(text=input_message),
                    MessageInputImageUrlBlock(image_url=url_param),
                ]
                # Create message to thread
                message = agents_client.messages.create(
                    thread_id=thread.id, role=MessageRole.USER, content=content_blocks
                )
                run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
                submitted_tool_outputs = False
                result_image_base64 = image_to_base64(self._get_screenshot_next_file())
                result_img_url = f"data:image/jpeg;base64,{result_image_base64}"
                computer_screenshot = ComputerScreenshot(image_url=result_img_url)
                while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                    time.sleep(self._sleep_time())
                    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

                    if run.status == RunStatus.REQUIRES_ACTION and isinstance(
                        run.required_action, SubmitToolOutputsAction
                    ):
                        tool_calls = run.required_action.submit_tool_outputs.tool_calls
                        assert tool_calls, "No tool calls to fulfill."
                        tool_outputs = []
                        for tool_call in tool_calls:
                            if isinstance(tool_call, RequiredComputerUseToolCall):
                                # Provide a fake screenshot response
                                tool_outputs.append(
                                    ComputerToolOutput(tool_call_id=tool_call.id, output=computer_screenshot)
                                )
                        if tool_outputs:
                            submitted_tool_outputs = True
                            agents_client.runs.submit_tool_outputs(
                                thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                            )
                assert submitted_tool_outputs, "Tool outputs were never submitted."
                assert run.status != RunStatus.FAILED, run.last_error

                # Validate run steps contain a Computer Use tool call
                found_cu_tool_call = False
                for run_step in agents_client.run_steps.list(thread_id=thread.id, run_id=run.id):
                    if isinstance(run_step.step_details, RunStepToolCallDetails):
                        for tc in run_step.step_details.tool_calls:
                            if isinstance(tc, RunStepComputerUseToolCall):
                                found_cu_tool_call = True
                                break
                    if found_cu_tool_call:
                        break
                assert found_cu_tool_call, "No RunStepComputerUseToolCall was found."
                messages = list(agents_client.messages.list(thread_id=thread.id))
                assert len(messages) > 1
            finally:
                agents_client.threads.delete(thread.id)
                agents_client.delete_agent(agent.id)

    @agentClientPreparer()
    @recorded_by_proxy
    def test_mcp_tool_streaming(self, **kwargs):
        """Test MCP tool call in streaming scenarios."""
        mcp_tool = self._get_mcp_tool()
        with self.create_client(**kwargs, by_endpoint=True) as agents_client:
            agent = agents_client.create_agent(
                model="gpt-4o",
                name="my-mcp-agent",
                instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
                tools=mcp_tool.definitions,
            )
            thread = agents_client.threads.create()
            agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Please summarize the Azure REST API specifications Readme",
            )
            mcp_tool.update_headers("SuperSecret", "123456")

            try:
                with agents_client.runs.stream(
                    thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources
                ) as stream:
                    is_started = False
                    received_message = False
                    got_expected_delta = False
                    is_completed = False
                    is_run_step_created = False
                    found_activity_details = False
                    found_tool_call_step = False
                    for event_type, event_data, _ in stream:

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
                                    agents_client.runs.submit_tool_outputs_stream(
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
                messages = list(agents_client.messages.list(thread_id=thread.id))
                assert len(messages) > 1
            finally:
                agents_client.threads.delete(thread.id)
                agents_client.delete_agent(agent.id)
