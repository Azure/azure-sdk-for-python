# pylint: disable=too-many-lines
# # ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import time
import functools
import datetime
import logging
import sys
import io

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, CodeInterpreterTool, FileSearchTool, ToolSet, AgentThread
from azure.core.pipeline.transport import RequestsTransport
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError, HttpResponseError
from azure.ai.projects.models import FunctionTool
from azure.identity import DefaultAzureCredential

# TODO clean this up / get rid of anything not in use

"""
issues I've noticed with the code: 
    delete_thread(thread.id) fails
    cancel_thread(thread.id) expires/times out occasionally
    added time.sleep() to the beginning of my last few tests to avoid limits
    when using the endpoint from Howie, delete_agent(agent.id) did not work but would not cause an error
"""

# Set to True to enable SDK logging
LOGGING_ENABLED = True

if LOGGING_ENABLED:
    # Create a logger for the 'azure' SDK
    # See https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)  # INFO or DEBUG

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)


agentClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects",
    azure_ai_projects_agents_tests_project_connection_string="foo.bar.some-domain.ms;00000000-0000-0000-0000-000000000000;rg-resour-cegr-oupfoo1;abcd-abcdabcdabcda-abcdefghijklm",
)
"""
agentClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    'azure_ai_projects',
    azure_ai_project_host_name="https://foo.bar.some-domain.ms",
    azure_ai_project_subscription_id="00000000-0000-0000-0000-000000000000",
    azure_ai_project_resource_group_name="rg-resour-cegr-oupfoo1",
    azure_ai_project_workspace_name="abcd-abcdabcdabcda-abcdefghijklm",
)
"""


# create tool for agent use
def fetch_current_datetime_live():
    """
    Get the current time as a JSON string.

    :return: Static time string so that test recordings work.
    :rtype: str
    """
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_json = json.dumps({"current_time": current_datetime})
    return time_json


# create tool for agent use
def fetch_current_datetime_recordings():
    """
    Get the current time as a JSON string.

    :return: Static time string so that test recordings work.
    :rtype: str
    """
    time_json = json.dumps({"current_time": "2024-10-10 12:30:19"})
    return time_json


# Statically defined user functions for fast reference
user_functions_recording = [fetch_current_datetime_recordings]
user_functions_live = [fetch_current_datetime_live]


# The test class name needs to start with "Test" to get collected by pytest
class TestAgentClient(AzureRecordedTestCase):

    # helper function: create client using environment variables
    def create_client(self, **kwargs):
        # fetch environment variables
        connection_string = kwargs.pop("azure_ai_projects_agents_tests_project_connection_string")
        credential = self.get_credential(AIProjectClient, is_async=False)

        # create and return client
        client = AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=connection_string,
        )

        return client

    # for debugging purposes: if a test fails and its agent has not been deleted, it will continue to show up in the agents list
    """
    # NOTE: this test should not be run against a shared resource, as it will delete all agents
    @agentClientPreparer()
    @recorded_by_proxy
    def test_clear_client(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # clear agent list
        agents = client.agents.list_agents().data
        for agent in agents:
            client.agents.delete_agent(agent.id)
        assert client.agents.list_agents().data.__len__() == 0
       
        # close client
        client.close()
    """

    #     # **********************************************************************************
    #     #
    #     #                               UNIT TESTS
    #     #
    #     # **********************************************************************************

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - agent APIs
    # #
    # # **********************************************************************************

    # test client creation
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_client(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # close client
        client.close()

    # test agent creation and deletion
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_delete_agent(self, **kwargs):
        # create client
        # client = self.create_client(**kwargs)
        with self.create_client(**kwargs) as client:
            assert isinstance(client, AIProjectClient)
            print("Created client")

            # create agent
            agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
            assert agent.id
            print("Created agent, agent ID", agent.id)

            # delete agent and close client
            client.agents.delete_agent(agent.id)
            print("Deleted agent")
        
        # assert not client
        client.close()

    # test agent creation with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)
        print("Created client")

        # create body for agent
        body = {
            "name": "my-agent",
            "model": "gpt-4o",
            "instructions": "You are helpful agent"
        }

        # create agent
        agent = client.agents.create_agent(body=body)
        assert agent.id
        print("Created agent, agent ID", agent.id)
        
        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test agent creation with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)
        print("Created client")

        # create body for agent
        body = {
            "name": "my-agent",
            "model": "gpt-4o",
            "instructions": "You are helpful agent"
        }
        binary_body = json.dumps(body).encode("utf-8")

        # create agent
        agent = client.agents.create_agent(body=io.BytesIO(binary_body))
        assert agent.id
        print("Created agent, agent ID", agent.id)
        assert agent.name == "my-agent"
        assert agent.model == "gpt-4o"
        
        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test agent creation with tools
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_agent_with_tools(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # initialize agent functions
        functions = FunctionTool(user_functions_recording)

        # create agent with tools
        agent = client.agents.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", tools=functions.definitions
        )
        assert agent.id
        print("Created agent, agent ID", agent.id)
        assert agent.tools
        assert agent.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
        print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_agent(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id

        # update agent and confirm changes went through
        agent.update(name="my-agent2", instructions="You are helpful agent")
        assert agent.name
        assert agent.name == "my-agent2"

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test update agent without body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_agent_2(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create body for agent
        body = {
            "name": "my-agent",
            "model": "gpt-4o",
            "instructions": "You are helpful agent"
        }

        # create agent
        agent = client.agents.create_agent(body=body)
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # update agent and confirm changes went through
        agent = client.agents.update_agent(agent.id, name="my-agent2")
        assert agent.name
        assert agent.name == "my-agent2"

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test update agent with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_agent_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create body for agent
        body = {
            "name": "my-agent",
            "model": "gpt-4o",
            "instructions": "You are helpful agent"
        }

        # create agent
        agent = client.agents.create_agent(body=body)
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create body for agent
        body2 = {
            "name": "my-agent2",
            "instructions": "You are helpful agent"
        }

        # update agent and confirm changes went through
        agent = client.agents.update_agent(agent.id, body=body2)
        assert agent.name
        assert agent.name == "my-agent2"

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # NOTE update_agent with overloads isn't working
    # test update agent with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_agent_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id

        # create body for agent
        body = {
            "name": "my-agent2",
            "instructions": "You are helpful agent"
        }
        binary_body = json.dumps(body).encode("utf-8")

        # update agent and confirm changes went through
        agent = client.agents.update_agent(agent.id, body=io.BytesIO(binary_body))
        assert agent.name
        assert agent.name == "my-agent2"

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    """
    DISABLED: can't perform consistently on shared resource
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_list(self, **kwargs):
        # create client and ensure there are no previous agents
        client = self.create_client(**kwargs)
        list_length = client.agents.list_agents().data.__len__()

        # create agent and check that it appears in the list
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert client.agents.list_agents().data.__len__() == list_length + 1
        assert client.agents.list_agents().data[0].id == agent.id 

        # create second agent and check that it appears in the list
        agent2 = client.agents.create_agent(model="gpt-4o", name="my-agent2", instructions="You are helpful agent")
        assert client.agents.list_agents().data.__len__() == list_length + 2
        assert client.agents.list_agents().data[0].id == agent.id or client.agents.list_agents().data[1].id == agent.id 

        # delete agents and check list 
        client.agents.delete_agent(agent.id)
        assert client.agents.list_agents().data.__len__() == list_length + 1
        assert client.agents.list_agents().data[0].id == agent2.id 

        client.agents.delete_agent(agent2.id)
        assert client.agents.list_agents().data.__len__() == list_length 
        print("Deleted agents")

        # close client
        client.close()
        """

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - Thread APIs
    #
    # **********************************************************************************

    # test creating thread
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert isinstance(thread, AgentThread)
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test creating thread with no body
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_with_metadata(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create metadata for thread
        metadata = {"key1": "value1", "key2": "value2"}

        # create thread
        thread = client.agents.create_thread(metadata=metadata)
        assert isinstance(thread, AgentThread) 
        assert thread.id
        print("Created thread, thread ID", thread.id)
        assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        print("Deleted agent")
        client.close()

    # test creating thread with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create body for thread
        body = {
            "metadata": {"key1": "value1", "key2": "value2"},
        }

        # create thread
        thread = client.agents.create_thread(body=body)
        assert isinstance(thread, AgentThread) 
        assert thread.id
        print("Created thread, thread ID", thread.id)
        assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        print("Deleted agent")
        client.close()

    # test creating thread with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create body for thread
        body = {
            "metadata": {"key1": "value1", "key2": "value2"},
        }
        binary_body = json.dumps(body).encode("utf-8")

        # create thread
        thread = client.agents.create_thread(body=io.BytesIO(binary_body))
        assert isinstance(thread, AgentThread) 
        assert thread.id
        print("Created thread, thread ID", thread.id)
        assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        print("Deleted agent")
        client.close()

    # test getting thread
    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # get thread
        thread2 = client.agents.get_thread(thread.id)
        assert thread2.id
        assert thread.id == thread2.id
        print("Got thread, thread ID", thread2.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test updating thread  
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)
        
        # update thread
        thread = client.agents.update_thread(thread.id, metadata={"key1": "value1", "key2": "value2"})
        assert thread.metadata == {"key1": "value1", "key2": "value2"}
        
        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

        
    # test updating thread without body 
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread_with_metadata(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # set metadata
        metadata = {"key1": "value1", "key2": "value2"}

        # create thread
        thread = client.agents.create_thread(metadata=metadata)
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # set metadata
        metadata2 = {"key1": "value1", "key2": "newvalue2"}

        # update thread
        thread = client.agents.update_thread(thread.id, metadata=metadata2)
        assert thread.metadata == {"key1": "value1", "key2": "newvalue2"}

        # close client
        client.close()

    # test updating thread with body: JSON 
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # set metadata
        body = {
            "metadata": {"key1": "value1", "key2": "value2"}
        }

        # update thread
        thread = client.agents.update_thread(thread.id, body=body)
        assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        client.close()

    # test updating thread with body: IO[bytes] 
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # set metadata
        body = {
            "metadata": {"key1": "value1", "key2": "value2"}
        }
        binary_body = json.dumps(body).encode("utf-8")

        # update thread
        thread = client.agents.update_thread(thread.id, body=io.BytesIO(binary_body))
        assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        client.close()

    
    # test deleting thread
    @agentClientPreparer()
    @recorded_by_proxy
    def test_delete_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert isinstance(thread, AgentThread)
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # delete thread
        deletion_status = client.agents.delete_thread(thread.id)
        assert deletion_status.id == thread.id
        assert deletion_status.deleted == True
        print("Deleted thread, thread ID", deletion_status.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()
    

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Message APIs
    # #
    # # **********************************************************************************

    # test creating message in a thread
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_message(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()


    # test creating message in a thread with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_message_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create body for message
        body = {
            "role": "user",
            "content": "Hello, tell me a joke"
        }

        # create message
        message = client.agents.create_message(thread_id=thread.id, body=body)
        assert message.id
        print("Created message, message ID", message.id)

        # close client
        client.close()

    # test creating message in a thread with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_message_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create body for message
        body = {
            "role": "user",
            "content": "Hello, tell me a joke"
        }
        binary_body = json.dumps(body).encode("utf-8")

        # create message
        message = client.agents.create_message(thread_id=thread.id, body=io.BytesIO(binary_body))
        assert message.id
        print("Created message, message ID", message.id)

        # close client
        client.close()

    # test creating multiple messages in a thread
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_multiple_messages(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create messages
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)
        message2 = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me another joke")
        assert message2.id
        print("Created message, message ID", message2.id)
        message3 = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a third joke")
        assert message3.id
        print("Created message, message ID", message3.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test listing messages in a thread
    @agentClientPreparer()
    @recorded_by_proxy
    def test_list_messages(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check that initial message list is empty
        messages0 = client.agents.list_messages(thread_id=thread.id)
        print(messages0.data)
        assert messages0.data.__len__() == 0

        # create messages and check message list for each one
        message1 = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message1.id
        print("Created message, message ID", message1.id)
        messages1 = client.agents.list_messages(thread_id=thread.id)
        assert messages1.data.__len__() == 1
        assert messages1.data[0].id == message1.id

        message2 = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me another joke")
        assert message2.id
        print("Created message, message ID", message2.id)
        messages2 = client.agents.list_messages(thread_id=thread.id)
        assert messages2.data.__len__() == 2
        assert messages2.data[0].id == message2.id or messages2.data[1].id == message2.id

        message3 = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a third joke")
        assert message3.id
        print("Created message, message ID", message3.id)
        messages3 = client.agents.list_messages(thread_id=thread.id)
        assert messages3.data.__len__() == 3
        assert (
            messages3.data[0].id == message3.id
            or messages3.data[1].id == message2.id
            or messages3.data[2].id == message2.id
        )

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test getting message in a thread
    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_message(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # get message
        message2 = client.agents.get_message(thread_id=thread.id, message_id=message.id)
        assert message2.id
        assert message.id == message2.id
        print("Got message, message ID", message.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test updating message in a thread without body
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_message(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # update message
        message = client.agents.update_message(thread_id=thread.id, message_id=message.id, metadata={"key1": "value1", "key2": "value2"})
        assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        client.close()

    # test updating message in a thread with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_message_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # create body for message
        body = {
            "metadata": {"key1": "value1", "key2": "value2"}
        }

        # update message
        message = client.agents.update_message(thread_id=thread.id, message_id=message.id, body=body)
        assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        client.close()

    # test updating message in a thread with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_message_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # create body for message
        body = {
            "metadata": {"key1": "value1", "key2": "value2"}
        }
        binary_body = json.dumps(body).encode("utf-8")

        # update message
        message = client.agents.update_message(thread_id=thread.id, message_id=message.id, body=io.BytesIO(binary_body))
        assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        client.close()
    

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Run APIs
    # #
    # # **********************************************************************************

    # test creating run
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()


    # test creating run without body
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run_with_metadata(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id, metadata={"key1": "value1", "key2": "value2"})
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test creating run with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create body for run
        body = {
            "assistant_id": agent.id,
            "metadata": {"key1": "value1", "key2": "value2"}
        }

        # create run
        run = client.agents.create_run(thread_id=thread.id, body=body)
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    
    # test creating run with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_run_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create body for run
        body = {
            "assistant_id": agent.id,
            "metadata": {"key1": "value1", "key2": "value2"}
        }
        binary_body = json.dumps(body).encode("utf-8")

        # create run
        run = client.agents.create_run(thread_id=thread.id, body=io.BytesIO(binary_body))
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test getting run
    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # get run
        run2 = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        assert run2.id
        assert run.id == run2.id
        print("Got run, run ID", run2.id)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    
    # test sucessful run status 
    @agentClientPreparer()
    @recorded_by_proxy
    def test_run_status(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
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
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)

        assert run.status in ["cancelled", "failed", "completed", "expired"]
        print("Run completed with status:", run.status)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    """
    # TODO another, but check that the number of runs decreases after cancelling runs
    # TODO can each thread only support one run? 
    # test listing runs
    @agentClientPreparer()
    @recorded_by_proxy
    def test_list_runs(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check list for current runs
        runs0 = client.agents.list_runs(thread_id=thread.id)
        assert runs0.data.__len__() == 0

        # create run and check list
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)
        runs1 = client.agents.list_runs(thread_id=thread.id)
        assert runs1.data.__len__() == 1
        assert runs1.data[0].id == run.id

        # create second run
        run2 = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run2.id
        print("Created run, run ID", run2.id)
        runs2 = client.agents.list_runs(thread_id=thread.id)
        assert runs2.data.__len__() == 2
        assert runs2.data[0].id == run2.id or runs2.data[1].id == run2.id

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()
    """

    
    # test updating run
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # update run
        while run.status in ["queued", "in_progress"]:
            time.sleep(5)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        run = client.agents.update_run(thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "value2"})
        assert run.metadata == {"key1": "value1", "key2": "value2"}

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test updating run without body
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run_with_metadata(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id, metadata={"key1": "value1", "key2": "value2"})
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # update run
        while run.status in ["queued", "in_progress"]:
            time.sleep(5)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        run = client.agents.update_run(thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "newvalue2"})
        assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test updating run with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id, metadata={"key1": "value1", "key2": "value2"})
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # create body for run
        body = {
            "metadata": {"key1": "value1", "key2": "newvalue2"}
        }

        # update run
        while run.status in ["queued", "in_progress"]:
            time.sleep(5)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        run = client.agents.update_run(thread_id=thread.id, run_id=run.id, body=body)
        assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test updating run with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_run_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id, metadata={"key1": "value1", "key2": "value2"})
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # create body for run
        body = {
            "metadata": {"key1": "value1", "key2": "newvalue2"}
        }
        binary_body = json.dumps(body).encode("utf-8")

        # update run
        while run.status in ["queued", "in_progress"]:
            time.sleep(5)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        run = client.agents.update_run(thread_id=thread.id, run_id=run.id, body=io.BytesIO(binary_body))
        assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test submitting tool outputs to run
    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # Initialize agent tools
        functions = FunctionTool(user_functions_recording) 
        # TODO add files for code interpreter tool
        # code_interpreter = CodeInterpreterTool()

        toolset = ToolSet()
        toolset.add(functions)
        # toolset.add(code_interpreter)

        # create agent
        agent = client.agents.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
        )
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
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
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

            # check if tools are needed
            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                print("Requires action: submit tool outputs")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print(
                        "No tool calls provided - cancelling run"
                    )
                    client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                # submit tool outputs to run
                tool_outputs = toolset.execute_tool_calls(tool_calls) 
                print("Tool outputs:", tool_outputs)
                if tool_outputs:
                    client.agents.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        # check that messages used the tool
        messages = client.agents.list_messages(thread_id=thread.id, run_id=run.id)
        tool_message = messages["data"][0]["content"][0]["text"]["value"]
        hour12 = time.strftime("%H")
        hour24 = time.strftime("%I")
        minute = time.strftime("%M")
        assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
        print("Used tool_outputs")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test submitting tool outputs to run with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_run_with_body(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # Initialize agent tools
        functions = FunctionTool(user_functions_live)
        # code_interpreter = CodeInterpreterTool()

        toolset = ToolSet()
        toolset.add(functions)
        # toolset.add(code_interpreter)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset)
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check that tools are uploaded
        assert run.tools
        assert run.tools[0]['function']['name'] == functions.definitions[0]['function']['name']
        print("Tool successfully submitted:", functions.definitions[0]['function']['name'])

        # check status
        assert run.status in  ["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

            # check if tools are needed
            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                print("Requires action: submit tool outputs")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run") 
                    client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                # submit tool outputs to run
                tool_outputs = toolset.execute_tool_calls(tool_calls)
                print("Tool outputs:", tool_outputs)
                if tool_outputs:
                    body = {
                        "tool_outputs": tool_outputs
                    }
                    client.agents.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, body=body
                    )

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        
        # check that messages used the tool
        messages = client.agents.list_messages(thread_id=thread.id, run_id=run.id)
        tool_message = messages['data'][0]['content'][0]['text']['value']
        hour12 = time.strftime("%H")
        hour24 = time.strftime("%I")
        minute = time.strftime("%M")
        assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
        print("Used tool_outputs")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test submitting tool outputs to run with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_run_with_iobytes(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # Initialize agent tools
        functions = FunctionTool(user_functions_live)
        # code_interpreter = CodeInterpreterTool()

        toolset = ToolSet()
        toolset.add(functions)
        # toolset.add(code_interpreter)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset)
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check that tools are uploaded
        assert run.tools
        assert run.tools[0]['function']['name'] == functions.definitions[0]['function']['name']
        print("Tool successfully submitted:", functions.definitions[0]['function']['name'])

        # check status
        assert run.status in  ["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

            # check if tools are needed
            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                print("Requires action: submit tool outputs")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run")
                    client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                # submit tool outputs to run
                tool_outputs = toolset.execute_tool_calls(tool_calls)
                print("Tool outputs:", tool_outputs)
                if tool_outputs:
                    body = {
                        "tool_outputs": tool_outputs
                    }
                    binary_body = json.dumps(body).encode("utf-8")
                    client.agents.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, body=io.BytesIO(binary_body)
                    )

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        
        # check that messages used the tool
        messages = client.agents.list_messages(thread_id=thread.id, run_id=run.id)
        tool_message = messages['data'][0]['content'][0]['text']['value']
        hour12 = time.strftime("%H")
        hour24 = time.strftime("%I")
        minute = time.strftime("%M")
        assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
        print("Used tool_outputs")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    """
    # DISABLED: rewrite to ensure run is not complete when cancel_run is called
    # test cancelling run
    @agentClientPreparer()
    @recorded_by_proxy
    def test_cancel_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check status and cancel
        assert run.status in ["queued", "in_progress", "requires_action"]
        client.agents.cancel_run(thread_id=thread.id, run_id=run.id)

        while run.status in ["queued", "cancelling"]:
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            print("Current run status:", run.status)
        assert run.status == "cancelled"
        print("Run cancelled")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()
        """

    # test create thread and run
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_and_run(self, **kwargs):
        time.sleep(26)
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread and run
        run = client.agents.create_thread_and_run(assistant_id=agent.id)
        assert run.id
        assert run.thread_id
        print("Created run, run ID", run.id)

        # get thread
        thread = client.agents.get_thread(run.thread_id)
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
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)

        assert run.status == "completed"
        print("Run completed")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test create thread and run with body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_and_run_with_body(self, **kwargs):
        # time.sleep(26)
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create body for thread
        body = {
            "assistant_id": agent.id,
            "metadata": {"key1": "value1", "key2": "value2"},
        }

        # create thread and run
        run = client.agents.create_thread_and_run(body=body)
        assert run.id
        assert run.thread_id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # get thread
        thread = client.agents.get_thread(run.thread_id)
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check status
        assert run.status in  ["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)

        assert run.status == "completed"
        print("Run completed")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    # test create thread and run with body: IO[bytes]
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread_and_run_with_iobytes(self, **kwargs):
        # time.sleep(26)
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create body for thread
        body = {
            "assistant_id": agent.id,
            "metadata": {"key1": "value1", "key2": "value2"},
        }
        binary_body = json.dumps(body).encode("utf-8")

        # create thread and run
        run = client.agents.create_thread_and_run(body=io.BytesIO(binary_body))
        assert run.id
        assert run.thread_id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # get thread
        thread = client.agents.get_thread(run.thread_id)
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check status
        assert run.status in  ["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)

        assert run.status == "completed"
        print("Run completed")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

    """
    # test listing run steps
    @agentClientPreparer()
    @recorded_by_proxy
    def test_list_run_step(self, **kwargs):

        time.sleep(50)
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
        assert run.id
        print("Created run, run ID", run.id)

        steps = client.agents.list_run_steps(thread_id=thread.id, run_id=run.id)
        # commenting assertion out below, do we know exactly when run starts?
        # assert steps['data'].__len__() == 0

        # check status
        assert run.status in ["queued", "in_progress", "requires_action", "completed"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)
            steps = client.agents.list_run_steps(thread_id=thread.id, run_id=run.id)
            assert steps["data"].__len__() > 0 

        assert run.status == "completed"
        print("Run completed")

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()
    """

    # test getting run step
    @agentClientPreparer()
    @recorded_by_proxy
    def test_get_run_step(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # create thread
        thread = client.agents.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.agents.create_message(
            thread_id=thread.id, role="user", content="Hello, can you tell me a joke?"
        )
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
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
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            if run.status == "failed":
                assert run.last_error
                print(run.last_error)
                print("FAILED HERE")
            assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)

        # list steps, check that get_run_step works with first step_id
        steps = client.agents.list_run_steps(thread_id=thread.id, run_id=run.id)
        assert steps["data"].__len__() > 0
        step = steps["data"][0]
        get_step = client.agents.get_run_step(thread_id=thread.id, run_id=run.id, step_id=step.id)
        assert step == get_step

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        client.close()

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
    @recorded_by_proxy
    def test_negative_create_delete_agent(self, **kwargs):
        # create client using bad endpoint
        bad_connection_string = "https://foo.bar.some-domain.ms;00000000-0000-0000-0000-000000000000;rg-resour-cegr-oupfoo1;abcd-abcdabcdabcda-abcdefghijklm"

        credential = self.get_credential(AIProjectClient, is_async=False)
        client = AIProjectClient.from_connection_string(
            credential=credential,
            connection=bad_connection_string,
        )
        
        # attempt to create agent with bad client
        exception_caught = False
        try:
            agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        # check for error (will not have a status code since it failed on request -- no response was recieved)
        except (ServiceRequestError, HttpResponseError) as e:
            exception_caught = True
            if type(e) == ServiceRequestError:
                assert e.message
                assert "failed to resolve 'foo.bar.some-domain.ms'" in e.message.lower()
            else:
                assert "No such host is known" and "foo.bar.some-domain.ms" in str(e)
        
        # close client and confirm an exception was caught
        client.close()
        assert exception_caught
    """
