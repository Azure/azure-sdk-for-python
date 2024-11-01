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
from azure.identity import DefaultAzureCredential

# TODO clean this up / get rid of anything not in use
# TODO after update_agent(), update_thread(), etc. -- need to get the object again -- is that the expected behavior? 
# TODO what should happen after updating a message? 

'''
issues I've noticed with the code: 
    delete_thread(thread.id) fails
    cancel_thread(thread.id) expires/times out occasionally
    added time.sleep() to the beginning of my last few tests to avoid limits
    when using the endpoint from Howie, delete_agent(agent.id) did not work but would not cause an error
'''

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
    azure_ai_projects_connection_string_agents_tests="foo.bar.some-domain.ms;00000000-0000-0000-0000-000000000000;rg-resour-cegr-oupfoo1;abcd-abcdabcdabcda-abcdefghijklm",
)
"""
agentClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    'azure_ai_project',
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
class TestagentClient(AzureRecordedTestCase):

    # helper function: create client using environment variables
    def create_client(self, **kwargs):
        # fetch environment variables
        connection_string = kwargs.pop("azure_ai_projects_connection_string_agents_tests")
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
    def test_create_agent_with_body_iobytes(self, **kwargs):
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

    
    # test update agent without body: JSON
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_agent(self, **kwargs):
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
        client.agents.update_agent(agent.id, name="my-agent2")
        updatedagent = client.agents.get_agent(agent.id)
        assert updatedagent.name
        assert updatedagent.name == "my-agent2"

        # delete agent and close client
        client.agents.delete_agent(updatedagent.id)
        print("Deleted agent")
        client.close()

    # NOTE update_agent with overloads isn't working
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
        client.agents.update_agent(agent.id, body=body2)
        updatedagent = client.agents.get_agent(agent.id)
        assert updatedagent.name
        assert updatedagent.name == "my-agent2"

        # delete agent and close client
        client.agents.delete_agent(updatedagent.id)
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
        client.agents.update_agent(agent.id, body=io.BytesIO(binary_body))
        updatedagent = client.agents.get_agent(agent.id)
        assert updatedagent.name
        assert updatedagent.name == "my-agent2"

        # delete agent and close client
        client.agents.delete_agent(updatedagent.id)
        print("Deleted agent")
        client.close()

    
    # test creating thread with no body
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_thread(self, **kwargs):
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

    # test updating thread without body 
    @agentClientPreparer()
    @recorded_by_proxy
    def test_update_thread(self, **kwargs):
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
        client.agents.update_thread(thread.id, metadata=metadata2)
        updatedthread = client.agents.get_thread(thread.id)
        assert updatedthread.metadata == {"key1": "value1", "key2": "newvalue2"}

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
        client.agents.update_thread(thread.id, body=body)
        updatedthread = client.agents.get_thread(thread.id)
        assert updatedthread.metadata == {"key1": "value1", "key2": "value2"}

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
        client.agents.update_thread(thread.id, body=io.BytesIO(binary_body))
        updatedthread = client.agents.get_thread(thread.id)
        assert updatedthread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        client.close()
        

    # test creating message in a thread without body
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_message(self, **kwargs):
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

        # close client
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
        client.agents.update_message(thread_id=thread.id, message_id=message.id, metadata={"key1": "value1", "key2": "value2"})
        updatedmessage = client.agents.get_message(thread_id=thread.id, message_id=message.id)
        assert updatedmessage.metadata == {"key1": "value1", "key2": "value2"}

        # message1 =  client.agents.get_message(thread_id=thread.id, message_id=message.id)
        # print("curiosity")
        # print(message1)
        # assert 1 == 0
        # NOTE should documentation say something about needing to get the message again after updating it?

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
        client.agents.update_message(thread_id=thread.id, message_id=message.id, body=body)
        updatedmessage = client.agents.get_message(thread_id=thread.id, message_id=message.id)
        assert updatedmessage.metadata == {"key1": "value1", "key2": "value2"}

        # message1 =  client.agents.get_message(thread_id=thread.id, message_id=message.id)
        # print("curiosity")
        # print(message1)
        # assert 1 == 0
        # NOTE should documentation say something about needing to get the message again after updating it?

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
        client.agents.update_message(thread_id=thread.id, message_id=message.id, body=io.BytesIO(binary_body))
        updatedmessage = client.agents.get_message(thread_id=thread.id, message_id=message.id)
        assert updatedmessage.metadata == {"key1": "value1", "key2": "value2"}

        # message1 =  client.agents.get_message(thread_id=thread.id, message_id=message.id)
        # print("curiosity")
        # print(message1)
        # assert 1 == 0
        # NOTE should documentation say something about needing to get the message again after updating it?

        # close client
        client.close()

    # test creating run without body
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

    # NOTE when does a run get updated? at what status? 
    # test updating run without body
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
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id, metadata={"key1": "value1", "key2": "value2"})
        assert run.id
        assert run.metadata == {"key1": "value1", "key2": "value2"}
        print("Created run, run ID", run.id)

        # update run
        while run.status in ["queued", "in_progress"]:
            time.sleep(5)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        client.agents.update_run(thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "newvalue2"})
        updatedrun = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        assert updatedrun.metadata == {"key1": "value1", "key2": "newvalue2"}

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
        client.agents.update_run(thread_id=thread.id, run_id=run.id, body=body)
        updatedrun = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        assert updatedrun.metadata == {"key1": "value1", "key2": "newvalue2"}

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
        client.agents.update_run(thread_id=thread.id, run_id=run.id, body=io.BytesIO(binary_body))
        updatedrun = client.agents.get_run(thread_id=thread.id, run_id=run.id)
        assert updatedrun.metadata == {"key1": "value1", "key2": "newvalue2"}

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



    '''
    functions left from _patch:
    upload file
    create vector store
    modify vector store
    create vector store file
    create vector store file batch
    list secrets
    create
    update
    create schedule
    create stream (patch)
    submit tool outputs to stream (patch)
    upload file and poll (patch)
    create vector store and poll (patch)
    '''

    

    


   