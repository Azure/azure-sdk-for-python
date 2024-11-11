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

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, CodeInterpreterTool, FileSearchTool, ToolSet, VectorStore
from azure.core.pipeline.transport import RequestsTransport
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError, HttpResponseError
from azure.identity import DefaultAzureCredential

# TODO clean this up / get rid of anything not in use

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
    azure_ai_projects_agents_tests_project_connection_string="foo.bar.some-domain.ms;00000000-0000-0000-0000-000000000000;rg-resour-cegr-oupfoo1;abcd-abcdabcdabcda-abcdefghijklm",
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

    # # test agent creation and deletion
    # @agentClientPreparer()
    # @recorded_by_proxy
    # def test_create_delete_agent(self, **kwargs):
    #     # create client
    #     client = self.create_client(**kwargs)
    #     assert isinstance(client, AIProjectClient)
    #     print("Created client")

    #     # create agent
    #     agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
    #     assert agent.id
    #     print("Created agent, agent ID", agent.id)
        
    #     # delete agent and close client
    #     client.agents.delete_agent(agent.id)
    #     print("Deleted agent")
    #     client.close()

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - File Search
    # #
    # # **********************************************************************************

    # TODO test upload file

    # test assistant creation with file_search and add_vector_store
    @agentClientPreparer()
    @recorded_by_proxy
    def test_file_search_add_vector_store(self, **kwargs):
        # Create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)
        print("Created client")

        # Create file search tool
        file_search = FileSearchTool()
        # Adjust the file path to be relative to the test file location
        file_path = os.path.join(os.path.dirname(__file__), "product_info_1.md")
        openai_file = client.agents.upload_file_and_poll(file_path=file_path, purpose="assistants")
        # openai_file = client.agents.upload_file_and_poll(file_path="agents/product_info_1.md", purpose="assistants")
        print(f"Uploaded file, file ID: {openai_file.id}")
        
        openai_vectorstore = client.agents.create_vector_store_and_poll(file_ids=[openai_file.id], name="my_vectorstore")
        print(f"Created vector store, vector store ID: {openai_vectorstore.id}")
        
        file_search.add_vector_store(openai_vectorstore.id)

        toolset = ToolSet()
        toolset.add(file_search)
        print("Created toolset and added file search")

        # create agent
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset)
        assert agent.id
        print("Created agent, agent ID", agent.id)

        # check assistant tools and vector store resources
        assert agent.tools
        assert agent.tools[0]['type'] == 'file_search'
        assert agent.tool_resources
        assert agent.tool_resources['file_search']['vector_store_ids'][0] == openai_vectorstore.id

        # delete assistant and close client
        client.agents.delete_agent(agent.id)
        print("Deleted assistant")
        client.close()

    # test create vector store and poll
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store_and_poll(self, **kwargs):
        # Create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)
        print("Created client")
         
        # Create vector store
        body = {
            "name": "test_vector_store",
            "metadata": {"key1": "value1", "key2": "value2"}
        }
        try:
            vector_store = client.agents.create_vector_store_and_poll(body=body, sleep_interval=2)
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

    
    # test create vector store and poll
    @agentClientPreparer()
    @recorded_by_proxy
    def test_create_vector_store(self, **kwargs):
        # Create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AIProjectClient)
        print("Created client")
         
        # Create vector store
        body = {
            "name": "test_vector_store",
            "metadata": {"key1": "value1", "key2": "value2"}
        }
        try:
            vector_store = client.agents.create_vector_store(body=body)
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
         

    
    # # **********************************************************************************
    # #
    # #         NEGATIVE TESTS - TODO idk what goes here
    # #
    # # **********************************************************************************

    # # test assistant creation and deletion
    # @AssistantClientPreparer()
    # @recorded_by_proxy
    # def test_negative_create_delete_assistant(self, **kwargs):
    #     # create client using bad endpoint
    #     bad_endpoint = "https://your-deployment-name.openai.azure.com/"
    #     azure_ai_assistants_key = kwargs["azure_ai_assistants_key"]
    #     api_version=os.environ.get("AZUREAI_API_VERSION", "2024-07-01-preview")
    #     client = sdk.AssistantsClient(endpoint=bad_endpoint, credential=AzureKeyCredential(azure_ai_assistants_key), api_version=api_version)
        
    #     # attempt to create assistant with bad client
    #     exception_caught = False
    #     try:
    #         assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
    #     # check for error (will not have a status code since it failed on request -- no response was recieved)
    #     except (ServiceRequestError, HttpResponseError) as e:
    #         exception_caught = True
    #         if type(e) == ServiceRequestError:
    #             assert e.message
    #             assert "failed to resolve 'your-deployment-name.openai.azure.com'" in e.message.lower()
    #         else:
    #             assert "No such host is known" and "your-deployment-name.openai.azure.com" in str(e)
        
    #     # close client and confirm an exception was caught
    #     client.close()
    #     assert exception_caught

