# pylint: disable=too-many-lines,line-too-long,useless-suppression
# # ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
from typing import Any

import datetime
import functools
import json
import logging
import os
import pytest
import sys
import io
import time

from azure.ai.assistants.aio import AssistantsClient
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.assistants.models import (
    AzureFunctionTool,
    AzureFunctionStorageQueue,
    AssistantStreamEvent,
    AssistantThread,
    CodeInterpreterTool,
    CodeInterpreterToolResource,
    FilePurpose,
    FileSearchTool,
    FileSearchToolCallContent,
    FileSearchToolResource,
    FunctionTool,
    MessageAttachment,
    MessageRole,
    MessageTextContent,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
    RunAdditionalFieldList,
    RunStepDeltaChunk,
    RunStepDeltaToolCallObject,
    RunStepFileSearchToolCall,
    RunStepFileSearchToolCallResult,
    RunStepFileSearchToolCallResults,
    RunStatus,
    ThreadMessageOptions,
    ThreadRun,
    ToolResources,
    ToolSet,
    VectorStore,
    VectorStoreConfigurations,
    VectorStoreConfiguration,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)

# TODO clean this up / get rid of anything not in use

"""
issues I've noticed with the code: 
    delete_thread(thread.id) fails
    cancel_thread(thread.id) expires/times out occasionally
    added time.sleep() to the beginning of my last few tests to avoid limits
    when using the endpoint from Howie, delete_assistant(assistant.id) did not work but would not cause an error
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


assistantClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_assistants",
    # TODO: uncomment this endpoint when re running with 1DP
    #azure_ai_assistants_tests_project_endpoint="https://aiservices-id.services.ai.azure.com/api/projects/project-name",
    # TODO: remove this endpoint when re running with 1DP
    azure_ai_assistants_tests_project_endpoint="https://Sanitized.api.azureml.ms/agents/v1.0/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/",
    azure_ai_assistants_tests_data_path="azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rg-resour-cegr-oupfoo1/workspaces/abcd-abcdabcdabcda-abcdefghijklm/datastores/workspaceblobstore/paths/LocalUpload/000000000000/product_info_1.md",
    azure_ai_assistants_tests_storage_queue="https://foobar.queue.core.windows.net",
    azure_ai_assistants_tests_search_index_name="sample_index",
    azure_ai_assistants_tests_search_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/connections/someindex",
)


# create tool for assistant use
def fetch_current_datetime_live():
    """
    Get the current time as a JSON string.

    :return: Static time string so that test recordings work.
    :rtype: str
    """
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_json = json.dumps({"current_time": current_datetime})
    return time_json


# create tool for assistant use
def fetch_current_datetime_recordings():
    """
    Get the current time as a JSON string.

    :return: Static time string so that test recordings work.
    :rtype: str
    """
    time_json = json.dumps({"current_time": "2024-10-10 12:30:19"})
    return time_json


# Statically defined user functions for fast reference
user_functions_recording = {fetch_current_datetime_recordings}
user_functions_live = {fetch_current_datetime_live}


# The test class name needs to start with "Test" to get collected by pytest
class TestAssistantClientAsync(AzureRecordedTestCase):

    # helper function: create client using environment variables
    def create_client(self, **kwargs):
        # fetch environment variables
        endpoint = kwargs.pop("azure_ai_assistants_tests_project_endpoint")
        credential = self.get_credential(AssistantsClient, is_async=True)

        # create and return client
        client = AssistantsClient(
            endpoint=endpoint,
            credential=credential,
        )

        return client

    def _get_data_file(self) -> str:
        """Return the test file name."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data", "product_info_1.md")

    # for debugging purposes: if a test fails and its assistant has not been deleted, it will continue to show up in the assistants list
    """
    # NOTE: this test should not be run against a shared resource, as it will delete all assistants
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_clear_client(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

        # clear assistant list
        assistants = await client.list_assistants().data
        for assistant in assistants:
            await client.delete_assistant(assistant.id)
        assert client.list_assistants().data.__len__() == 0
       
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
    #                      HAPPY PATH SERVICE TESTS - assistant APIs
    #
    # **********************************************************************************

    # test client creation
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_client(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AssistantsClient)
        print("Created client")

        # close client
        await client.close()

    # test assistant creation and deletion
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_delete_assistant(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            assert isinstance(client, AssistantsClient)
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test assistant creation with tools
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_assistant_with_tools(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            assert isinstance(client, AssistantsClient)
            print("Created client")

            # initialize assistant functions
            functions = FunctionTool(functions=user_functions_recording)

            # create assistant with tools
            assistant = await client.create_assistant(
                model="gpt-4o",
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=functions.definitions,
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)
            assert assistant.tools
            assert assistant.tools[0]["function"]["name"] == functions.definitions[0]["function"]["name"]
            print("Tool successfully submitted:", functions.definitions[0]["function"]["name"])

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test update assistant without body: JSON
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_assistant(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            assert isinstance(client, AssistantsClient)
            print("Created client")

            # create body for assistant
            body = {"name": "my-assistant", "model": "gpt-4o", "instructions": "You are helpful assistant"}

            # create assistant
            assistant = await client.create_assistant(body=body)
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # update assistant and confirm changes went through
            assistant = await client.update_assistant(assistant.id, name="my-assistant2")
            assert assistant.name
            assert assistant.name == "my-assistant2"

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test update assistant with body: JSON
    @assistantClientPreparer()
    @pytest.mark.skip("Overload performs inconsistently.")
    @recorded_by_proxy_async
    async def test_update_assistant_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create body for assistant
            body = {"name": "my-assistant", "model": "gpt-4o", "instructions": "You are helpful assistant"}

            # create assistant
            assistant = await client.create_assistant(body=body)
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create body for assistant
            body2 = {"name": "my-assistant2", "instructions": "You are helpful assistant"}

            # update assistant and confirm changes went through
            assistant = await client.update_assistant(assistant.id, body=body2)
            assert assistant.name
            assert assistant.name == "my-assistant2"

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # NOTE update_assistant with overloads isn't working
    # test update assistant with body: IO[bytes]
    @assistantClientPreparer()
    @pytest.mark.skip("Overload performs inconsistently.")
    @recorded_by_proxy_async
    async def test_update_assistant_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id

            # create body for assistant
            body = {"name": "my-assistant2", "instructions": "You are helpful assistant"}
            binary_body = json.dumps(body).encode("utf-8")

            # update assistant and confirm changes went through
            assistant = await client.update_assistant(assistant.id, body=io.BytesIO(binary_body))
            assert assistant.name
            assert assistant.name == "my-assistant2"

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    """
    DISABLED: can't perform consistently on shared resource
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_assistant_list(self, **kwargs):
        # create client and ensure there are no previous assistants
        client = self.create_client(**kwargs)
        list_length = await client.list_assistants().data.__len__()

        # create assistant and check that it appears in the list
       assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
        assert client.list_assistants().data.__len__() == list_length + 1
        assert client.list_assistants().data[0].id == assistant.id 

        # create second assistant and check that it appears in the list
        assistant2 = await client.create_assistant(model="gpt-4o", name="my-assistant2", instructions="You are helpful assistant")
        assert client.list_assistants().data.__len__() == list_length + 2
        assert client.list_assistants().data[0].id == assistant.id or client.list_assistants().data[1].id == assistant.id 

        # delete assistants and check list 
        await client.delete_assistant(assistant.id)
        assert client.list_assistants().data.__len__() == list_length + 1
        assert client.list_assistants().data[0].id == assistant2.id 

        client.delete_assistant(assistant2.id)
        assert client.list_assistants().data.__len__() == list_length 
        print("Deleted assistants")

        # close client
        await client.close()
        """

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - Thread APIs
    #
    # **********************************************************************************

    # test creating thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert isinstance(thread, AssistantThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test creating thread with no body
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create metadata for thread
            metadata = {"key1": "value1", "key2": "value2"}

            # create thread
            thread = await client.create_thread(metadata=metadata)
            assert isinstance(thread, AssistantThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # close client
            print("Deleted assistant")
        await client.close()

    # test creating thread with body: JSON
    @assistantClientPreparer()
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
            thread = await client.create_thread(body=body)
            assert isinstance(thread, AssistantThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # close client
            print("Deleted assistant")
        await client.close()

    # test creating thread with body: IO[bytes]
    @assistantClientPreparer()
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
            thread = await client.create_thread(body=io.BytesIO(binary_body))
            assert isinstance(thread, AssistantThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # close client
            print("Deleted assistant")
        await client.close()

    # test getting thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_get_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # get thread
            thread2 = await client.get_thread(thread.id)
            assert thread2.id
            assert thread.id == thread2.id
            print("Got thread, thread ID", thread2.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test updating thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # update thread
            thread = await client.update_thread(thread.id, metadata={"key1": "value1", "key2": "value2"})
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test updating thread without body
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # set metadata
            metadata = {"key1": "value1", "key2": "value2"}

            # create thread
            thread = await client.create_thread(metadata=metadata)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # set metadata
            metadata2 = {"key1": "value1", "key2": "newvalue2"}

            # update thread
            thread = await client.update_thread(thread.id, metadata=metadata2)
            assert thread.metadata == {"key1": "value1", "key2": "newvalue2"}

        # close client
        await client.close()

    # test updating thread with body: JSON
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # set metadata
            body = {"metadata": {"key1": "value1", "key2": "value2"}}

            # update thread
            thread = await client.update_thread(thread.id, body=body)
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test updating thread with body: IO[bytes]
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_thread_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # set metadata
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # update thread
            thread = await client.update_thread(thread.id, body=io.BytesIO(binary_body))
            assert thread.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test deleting thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_delete_thread(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            # assert isinstance(thread, AssistantThread)
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # delete thread
            deletion_status = await client.delete_thread(thread.id)
            assert deletion_status.id == thread.id
            assert deletion_status.deleted == True
            print("Deleted thread, thread ID", deletion_status.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Message APIs
    # #
    # # **********************************************************************************

    # test creating message in a thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_message(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test creating message in a thread with body: JSON
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_message_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for message
            body = {"role": "user", "content": "Hello, tell me a joke"}

            # create message
            message = await client.create_message(thread_id=thread.id, body=body)
            assert message.id
            print("Created message, message ID", message.id)

        # close client
        await client.close()

    # test creating message in a thread with body: IO[bytes]
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_message_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for message
            body = {"role": "user", "content": "Hello, tell me a joke"}
            binary_body = json.dumps(body).encode("utf-8")

            # create message
            message = await client.create_message(thread_id=thread.id, body=io.BytesIO(binary_body))
            assert message.id
            print("Created message, message ID", message.id)

        # close client
        await client.close()

    # test creating multiple messages in a thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_multiple_messages(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create messages
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message.id
            print("Created message, message ID", message.id)
            message2 = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me another joke"
            )
            assert message2.id
            print("Created message, message ID", message2.id)
            message3 = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a third joke"
            )
            assert message3.id
            print("Created message, message ID", message3.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test listing messages in a thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_list_messages(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # check that initial message list is empty
            messages0 = await client.list_messages(thread_id=thread.id)
            print(messages0.data)
            assert messages0.data.__len__() == 0

            # create messages and check message list for each one
            message1 = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message1.id
            print("Created message, message ID", message1.id)
            messages1 = await client.list_messages(thread_id=thread.id)
            assert messages1.data.__len__() == 1
            assert messages1.data[0].id == message1.id

            message2 = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me another joke"
            )
            assert message2.id
            print("Created message, message ID", message2.id)
            messages2 = await client.list_messages(thread_id=thread.id)
            assert messages2.data.__len__() == 2
            assert messages2.data[0].id == message2.id or messages2.data[1].id == message2.id

            message3 = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a third joke"
            )
            assert message3.id
            print("Created message, message ID", message3.id)
            messages3 = await client.list_messages(thread_id=thread.id)
            assert messages3.data.__len__() == 3
            assert (
                messages3.data[0].id == message3.id
                or messages3.data[1].id == message2.id
                or messages3.data[2].id == message2.id
            )

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test getting message in a thread
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_get_message(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # get message
            message2 = await client.get_message(thread_id=thread.id, message_id=message.id)
            assert message2.id
            assert message.id == message2.id
            print("Got message, message ID", message.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test updating message in a thread without body
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_message(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # update message
            message = await client.update_message(
                thread_id=thread.id, message_id=message.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test updating message in a thread with body: JSON
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_message_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create body for message
            body = {"metadata": {"key1": "value1", "key2": "value2"}}

            # update message
            message = await client.update_message(thread_id=thread.id, message_id=message.id, body=body)
            assert message.metadata == {"key1": "value1", "key2": "value2"}

        # close client
        await client.close()

    # test updating message in a thread with body: IO[bytes]
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_message_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create body for message
            body = {"metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # update message
            message = await client.update_message(
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
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
            assert run.id
            print("Created run, run ID", run.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test creating run without body
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.create_run(
                thread_id=thread.id, assistant_id=assistant.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test creating run with body: JSON
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for run
            body = {"assistant_id": assistant.id, "metadata": {"key1": "value1", "key2": "value2"}}

            # create run
            run = await client.create_run(thread_id=thread.id, body=body)
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test creating run with body: IO[bytes]
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_run_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create body for run
            body = {"assistant_id": assistant.id, "metadata": {"key1": "value1", "key2": "value2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # create run
            run = await client.create_run(thread_id=thread.id, body=io.BytesIO(binary_body))
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test getting run
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_get_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
            assert run.id
            print("Created run, run ID", run.id)

            # get run
            run2 = await client.get_run(thread_id=thread.id, run_id=run.id)
            assert run2.id
            assert run.id == run2.id
            print("Got run, run ID", run2.id)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test sucessful run status
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_run_status(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
                print("Run status:", run.status)

            assert run.status in ["cancelled", "failed", "completed", "expired"]
            print("Run completed with status:", run.status)

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    """
    # TODO another, but check that the number of runs decreases after cancelling runs
    # TODO can each thread only support one run? 
    # test listing runs
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_list_runs(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

        # create assistant
        assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = await client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check list for current runs
        runs0 = await client.list_runs(thread_id=thread.id)
        assert runs0.data.__len__() == 0

        # create run and check list
        run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)
        runs1 = await client.list_runs(thread_id=thread.id)
        assert runs1.data.__len__() == 1
        assert runs1.data[0].id == run.id

        # create second run
        run2 = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run2.id
        print("Created run, run ID", run2.id)
        runs2 = await client.list_runs(thread_id=thread.id)
        assert runs2.data.__len__() == 2
        assert runs2.data[0].id == run2.id or runs2.data[1].id == run2.id

        # delete assistant and close client
        await client.delete_assistant(assistant.id)
        print("Deleted assistant")
        await client.close()
    """

    # test updating run
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
            assert run.id
            print("Created run, run ID", run.id)

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(5)
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
            run = await client.update_run(
                thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.metadata == {"key1": "value1", "key2": "value2"}

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test updating run without body
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run_with_metadata(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.create_run(
                thread_id=thread.id, assistant_id=assistant.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(5)
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
            run = await client.update_run(
                thread_id=thread.id, run_id=run.id, metadata={"key1": "value1", "key2": "newvalue2"}
            )
            assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test updating run with body: JSON
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.create_run(
                thread_id=thread.id, assistant_id=assistant.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # create body for run
            body = {"metadata": {"key1": "value1", "key2": "newvalue2"}}

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(5)
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
            run = await client.update_run(thread_id=thread.id, run_id=run.id, body=body)
            assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test updating run with body: IO[bytes]
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_update_run_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create run
            run = await client.create_run(
                thread_id=thread.id, assistant_id=assistant.id, metadata={"key1": "value1", "key2": "value2"}
            )
            assert run.id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # create body for run
            body = {"metadata": {"key1": "value1", "key2": "newvalue2"}}
            binary_body = json.dumps(body).encode("utf-8")

            # update run
            while run.status in ["queued", "in_progress"]:
                time.sleep(5)
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
            run = await client.update_run(thread_id=thread.id, run_id=run.id, body=io.BytesIO(binary_body))
            assert run.metadata == {"key1": "value1", "key2": "newvalue2"}

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test submitting tool outputs to run
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_submit_tool_outputs_to_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # Initialize assistant tools
            functions = FunctionTool(user_functions_recording)
            # TODO add files for code interpreter tool
            # code_interpreter = CodeInterpreterTool()

            toolset = ToolSet()
            toolset.add(functions)
            # toolset.add(code_interpreter)

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant", toolset=toolset
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, what time is it?"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)

                # check if tools are needed
                if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                    print("Requires action: submit tool outputs")
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await client.cancel_run(thread_id=thread.id, run_id=run.id)
                        break

                    # submit tool outputs to run
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                    print("Tool outputs:", tool_outputs)
                    if tool_outputs:
                        await client.submit_tool_outputs_to_run(
                            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                        )

                print("Current run status:", run.status)

            print("Run completed with status:", run.status)

            # check that messages used the tool
            messages = await client.list_messages(thread_id=thread.id, run_id=run.id)
            tool_message = messages["data"][0]["content"][0]["text"]["value"]
            hour12 = time.strftime("%H")
            hour24 = time.strftime("%I")
            minute = time.strftime("%M")
            assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
            print("Used tool_outputs")

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test submitting tool outputs to run with body: JSON
    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_submit_tool_outputs_to_run_with_body(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # Initialize assistant tools
            functions = FunctionTool(user_functions_recording)
            toolset = ToolSet()
            toolset.add(functions)

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant", toolset=toolset
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, what time is it?"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)

                # check if tools are needed
                if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                    print("Requires action: submit tool outputs")
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await client.cancel_run(thread_id=thread.id, run_id=run.id)
                        break

                    # submit tool outputs to run
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                    print("Tool outputs:", tool_outputs)
                    if tool_outputs:
                        body = {"tool_outputs": tool_outputs}
                        await client.submit_tool_outputs_to_run(
                            thread_id=thread.id, run_id=run.id, body=body
                        )

                print("Current run status:", run.status)

            print("Run completed with status:", run.status)

            # check that messages used the tool
            messages = await client.list_messages(thread_id=thread.id, run_id=run.id)
            tool_message = messages["data"][0]["content"][0]["text"]["value"]
            # hour12 = time.strftime("%H")
            # hour24 = time.strftime("%I")
            # minute = time.strftime("%M")
            # assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
            recorded_time = "12:30"
            assert recorded_time in tool_message
            print("Used tool_outputs")

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test submitting tool outputs to run with body: IO[bytes]
    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_submit_tool_outputs_to_run_with_iobytes(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # Initialize assistant tools
            functions = FunctionTool(user_functions_recording)
            toolset = ToolSet()
            toolset.add(functions)

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant", toolset=toolset
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, what time is it?"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)

                # check if tools are needed
                if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                    print("Requires action: submit tool outputs")
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        client.cancel_run(thread_id=thread.id, run_id=run.id)
                        break

                    # submit tool outputs to run
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                    print("Tool outputs:", tool_outputs)
                    if tool_outputs:
                        body = {"tool_outputs": tool_outputs}
                        binary_body = json.dumps(body).encode("utf-8")
                        await client.submit_tool_outputs_to_run(
                            thread_id=thread.id, run_id=run.id, body=io.BytesIO(binary_body)
                        )

                print("Current run status:", run.status)

            print("Run completed with status:", run.status)

            # check that messages used the tool
            messages = await client.list_messages(thread_id=thread.id, run_id=run.id)
            tool_message = messages["data"][0]["content"][0]["text"]["value"]
            # hour12 = time.strftime("%H")
            # hour24 = time.strftime("%I")
            # minute = time.strftime("%M")
            # assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
            recorded_time = "12:30"
            assert recorded_time in tool_message
            print("Used tool_outputs")

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    """
    # DISABLED: rewrite to ensure run is not complete when cancel_run is called
    # test cancelling run
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_cancel_run(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

        # create assistant
        assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = await client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = await client.create_message(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
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
            run = await client.get_run(thread_id=thread.id, run_id=run.id)

            # check if tools are needed
            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                print("Requires action: submit tool outputs")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print(
                        "No tool calls provided - cancelling run"
                    )  # TODO how can i make sure that it wants tools? should i have some kind of error message?
                    await client.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                # submit tool outputs to run
                tool_outputs = toolset.execute_tool_calls(tool_calls)  # TODO issue somewhere here
                print("Tool outputs:", tool_outputs)
                if tool_outputs:
                    await client.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        # check that messages used the tool
        messages = await client.list_messages(thread_id=thread.id, run_id=run.id)
        tool_message = messages["data"][0]["content"][0]["text"]["value"]
        hour12 = time.strftime("%H")
        hour24 = time.strftime("%I")
        minute = time.strftime("%M")
        assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
        print("Used tool_outputs")

        # delete assistant and close client
        await client.delete_assistant(assistant.id)
        print("Deleted assistant")
        await client.close()
        """

    @assistantClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_thread_true(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(True, True, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_thread_false(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(False, True, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_run_true(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(True, False, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_create_parallel_tool_run_false(self, **kwargs):
        """Test creation of parallel runs."""
        await self._do_test_create_parallel_thread_runs(False, False, **kwargs)

    async def _wait_for_run(self, client, run, timeout=1):
        """Wait while run will get to terminal state."""
        while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
            time.sleep(timeout)
            run = await client.get_run(thread_id=run.thread_id, run_id=run.id)
        return run

    async def _do_test_create_parallel_thread_runs(self, use_parallel_runs, create_thread_run, **kwargs):
        """Test creation of parallel runs."""

        # create client
        client = self.create_client(
            **kwargs,
        )
        assert isinstance(client, AssistantsClient)

        # Initialize assistant tools
        functions = FunctionTool(functions=user_functions_recording)
        code_interpreter = CodeInterpreterTool()

        toolset = ToolSet()
        toolset.add(functions)
        toolset.add(code_interpreter)
        assistant = await client.create_assistant(
            model="gpt-4",
            name="my-assistant",
            instructions="You are helpful assistant",
            toolset=toolset,
        )
        assert assistant.id

        message = ThreadMessageOptions(
            role="user",
            content="Hello, what time is it?",
        )

        if create_thread_run:
            run = await client.create_thread_and_run(
                assistant_id=assistant.id,
                parallel_tool_calls=use_parallel_runs,
            )
            run = await self._wait_for_run(client, run)
        else:
            thread = await client.create_thread(messages=[message])
            assert thread.id

            run = await client.create_and_process_run(
                thread_id=thread.id,
                assistant_id=assistant.id,
                parallel_tool_calls=use_parallel_runs,
            )
        assert run.id
        assert run.status == RunStatus.COMPLETED, run.last_error.message
        assert run.parallel_tool_calls == use_parallel_runs

        assert (await client.delete_assistant(assistant.id)).deleted, "The assistant was not deleted"
        messages = await client.list_messages(thread_id=run.thread_id)
        assert len(messages.data), "The data from the assistant was not received."

    """
    # DISABLED: rewrite to ensure run is not complete when cancel_run is called
    # test cancelling run
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_cancel_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.create_message(thread_id=thread.id, role="user", content="Hello, what time is it?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check status and cancel
        assert run.status in ["queued", "in_progress", "requires_action"]
        client.cancel_run(thread_id=thread.id, run_id=run.id)

        while run.status in ["queued", "cancelling"]:
            time.sleep(1)
            run = await client.get_run(thread_id=thread.id, run_id=run.id)
            print("Current run status:", run.status)
        assert run.status == "cancelled"
        print("Run cancelled")

        # delete assistant and close client
        await client.delete_assistant(assistant.id)
        print("Deleted assistant")
        await client.close()
        """

    # test create thread and run
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_and_run(self, **kwargs):
        time.sleep(26)
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread and run
            run = await client.create_thread_and_run(assistant_id=assistant.id)
            assert run.id
            assert run.thread_id
            print("Created run, run ID", run.id)

            # get thread
            thread = await client.get_thread(run.thread_id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
                # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
                print("Run status:", run.status)

            assert run.status == "completed"
            print("Run completed")

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")

    # test create thread and run with body: JSON
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_and_run_with_body(self, **kwargs):
        # time.sleep(26)
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create body for thread
            body = {
                "assistant_id": assistant.id,
                "metadata": {"key1": "value1", "key2": "value2"},
            }

            # create thread and run
            run = await client.create_thread_and_run(body=body)
            assert run.id
            assert run.thread_id
            assert run.metadata == {"key1": "value1", "key2": "value2"}
            print("Created run, run ID", run.id)

            # get thread
            thread = await client.get_thread(run.thread_id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
                # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
                print("Run status:", run.status)

            assert run.status == "completed"
            print("Run completed")

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    # test create thread and run with body: IO[bytes]
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_thread_and_run_with_iobytes(self, **kwargs):
        # time.sleep(26)
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create body for thread
            body = {
                "assistant_id": assistant.id,
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
            thread = await client.get_thread(run.thread_id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
                # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
                print("Run status:", run.status)

            assert run.status == "completed"
            print("Run completed")

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    """
    # test listing run steps
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_list_run_step(self, **kwargs):

        time.sleep(50)
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, what time is it?"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
            assert run.id
            print("Created run, run ID", run.id)

            steps = await client.list_run_steps(thread_id=thread.id, run_id=run.id)
            # commenting assertion out below, do we know exactly when run starts?
            # assert steps['data'].__len__() == 0

            # check status
            assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            while run.status in ["queued", "in_progress", "requires_action"]:
                # wait for a second
                time.sleep(1)
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
                assert run.status in [
                    "queued",
                    "in_progress",
                    "requires_action",
                    "completed",
                ]
                print("Run status:", run.status)
                steps = await client.list_run_steps(
                    thread_id=thread.id, run_id=run.id
                )
            assert steps["data"].__len__() > 0 

            assert run.status == "completed"
            print("Run completed")

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()
    """

    # test getting run step
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_get_run_step(self, **kwargs):
        # create client
        async with self.create_client(**kwargs) as client:
            print("Created client")

            # create assistant
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
            )
            assert assistant.id
            print("Created assistant, assistant ID", assistant.id)

            # create thread
            thread = await client.create_thread()
            assert thread.id
            print("Created thread, thread ID", thread.id)

            # create message
            message = await client.create_message(
                thread_id=thread.id, role="user", content="Hello, can you tell me a joke?"
            )
            assert message.id
            print("Created message, message ID", message.id)

            # create run
            run = await client.create_run(thread_id=thread.id, assistant_id=assistant.id)
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
                run = await client.get_run(thread_id=thread.id, run_id=run.id)
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
            steps = await client.list_run_steps(thread_id=thread.id, run_id=run.id)
            assert steps["data"].__len__() > 0
            step = steps["data"][0]
            get_step = await client.get_run_step(thread_id=thread.id, run_id=run.id, step_id=step.id)
            assert step == get_step

            # delete assistant and close client
            await client.delete_assistant(assistant.id)
            print("Deleted assistant")
        await client.close()

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_azure(self, **kwargs):
        """Test the assistant with vector store creation."""
        await self._do_test_create_vector_store(streaming=False, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_file_id(self, **kwargs):
        """Test the assistant with vector store creation."""
        await self._do_test_create_vector_store(streaming=False, file_path=self._get_data_file(), **kwargs)

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_azure_streaming(self, **kwargs):
        """Test the assistant with vector store creation."""
        await self._do_test_create_vector_store(streaming=True, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_file_id_streaming(self, **kwargs):
        """Test the assistant with vector store creation."""
        await self._do_test_create_vector_store(streaming=True, file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_vector_store(self, streaming, **kwargs):
        """Test the assistant with vector store creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)
        file_ids = [file_id] if file_id else None
        if file_ids:
            ds = None
        else:
            ds = [
                VectorStoreDataSource(
                    asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
                    asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
                )
            ]
        vector_store = await ai_client.create_vector_store_and_poll(
            file_ids=file_ids, data_sources=ds, name="my_vectorstore"
        )
        assert vector_store.id
        await self._test_file_search(ai_client, vector_store, file_id, streaming)
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_file_id(self, **kwargs):
        """Test adding single file to vector store withn file ID."""
        await self._do_test_create_vector_store_add_file(streaming=False, file_path=self._get_data_file(), **kwargs)

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_azure(self, **kwargs):
        """Test adding single file to vector store with azure asset ID."""
        await self._do_test_create_vector_store_add_file(streaming=False, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_file_id_streaming(self, **kwargs):
        """Test adding single file to vector store withn file ID."""
        await self._do_test_create_vector_store_add_file(streaming=True, file_path=self._get_data_file(), **kwargs)

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_add_file_azure_streaming(self, **kwargs):
        """Test adding single file to vector store with azure asset ID."""
        await self._do_test_create_vector_store_add_file(streaming=True, **kwargs)

    async def _do_test_create_vector_store_add_file(self, streaming, **kwargs):
        """Test adding single file to vector store."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)
        if file_id:
            ds = None
        else:
            ds = VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
        vector_store = await ai_client.create_vector_store_and_poll(file_ids=[], name="sample_vector_store")
        assert vector_store.id
        vector_store_file = await ai_client.create_vector_store_file(
            vector_store_id=vector_store.id, data_source=ds, file_id=file_id
        )
        assert vector_store_file.id
        await self._test_file_search(ai_client, vector_store, file_id, streaming)
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_file_ids(self, **kwargs):
        """Test adding multiple files to vector store with file IDs."""
        await self._do_test_create_vector_store_batch(streaming=False, file_path=self._get_data_file(), **kwargs)

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_azure(self, **kwargs):
        """Test adding multiple files to vector store with azure asset IDs."""
        await self._do_test_create_vector_store_batch(streaming=False, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_file_ids_streaming(self, **kwargs):
        """Test adding multiple files to vector store with file IDs."""
        await self._do_test_create_vector_store_batch(streaming=True, file_path=self._get_data_file(), **kwargs)

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_create_vector_store_batch_azure_streaming(self, **kwargs):
        """Test adding multiple files to vector store with azure asset IDs."""
        await self._do_test_create_vector_store_batch(streaming=True, **kwargs)

    async def _do_test_create_vector_store_batch(self, streaming, **kwargs):
        """Test the assistant with vector store creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)
        if file_id:
            file_ids = [file_id]
            ds = None
        else:
            file_ids = None
            ds = [
                VectorStoreDataSource(
                    asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
                    asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
                )
            ]
        vector_store = await ai_client.create_vector_store_and_poll(file_ids=[], name="sample_vector_store")
        assert vector_store.id
        vector_store_file_batch = await ai_client.create_vector_store_file_batch_and_poll(
            vector_store_id=vector_store.id, data_sources=ds, file_ids=file_ids
        )
        assert vector_store_file_batch.id
        await self._test_file_search(ai_client, vector_store, file_id, streaming)

    async def _test_file_search(
        self, ai_client: AssistantsClient, vector_store: VectorStore, file_id: str, streaming: bool
    ) -> None:
        """Test the file search"""
        file_search = FileSearchTool(vector_store_ids=[vector_store.id])
        assistant = await ai_client.create_assistant(
            model="gpt-4",
            name="my-assistant",
            instructions="Hello, you are helpful assistant and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        assert assistant.id
        thread = await ai_client.create_thread()
        assert thread.id
        # create message
        message = await ai_client.create_message(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        if streaming:
            thread_run = None
            async with await ai_client.create_stream(
                thread_id=thread.id, assistant_id=assistant.id
            ) as stream:
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
            run = await ai_client.get_run(thread_id=thread_run.thread_id, run_id=thread_run.id)
            assert run is not None
        else:
            run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
        await ai_client.delete_vector_store(vector_store.id)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = await ai_client.list_messages(thread_id=thread.id)
        assert len(messages)
        await self._remove_file_maybe(file_id, ai_client)
        # delete assistant and close client
        await ai_client.delete_assistant(assistant.id)
        print("Deleted assistant")
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_message_attachement_azure(self, **kwargs):
        """Test message attachment with azure ID."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_message_attachment(data_sources=[ds], **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_message_attachement_file_ids(self, **kwargs):
        """Test message attachment with file ID."""
        await self._do_test_message_attachment(file_path=self._get_data_file(), **kwargs)

    async def _do_test_message_attachment(self, **kwargs):
        """Test assistant with the message attachment."""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)

        # Create assistant with file search tool
        assistant = await ai_client.create_assistant(
            model="gpt-4-1106-preview",
            name="my-assistant",
            instructions="Hello, you are helpful assistant and can search information from uploaded files",
        )
        assert assistant.id, "Assistant was not created"

        thread = await ai_client.create_thread()
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
        message = await ai_client.create_message(
            thread_id=thread.id,
            role="user",
            content="What does the attachment say?",
            attachments=[attachment],
        )
        assert message.id, "The message was not created."

        run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id, "The run was not created."
        await self._remove_file_maybe(file_id, ai_client)
        await ai_client.delete_assistant(assistant.id)

        messages = await ai_client.list_messages(thread_id=thread.id)
        assert len(messages), "No messages were created"
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("Failing with Http Response Errors.")
    @recorded_by_proxy_async
    async def test_vector_store_threads_file_search_azure(self, **kwargs):
        """Test file search when azure asset ids are supplied during thread creation."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        ds = [
            VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
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
        assistant = await ai_client.create_assistant(
            model="gpt-4o",
            name="my-assistant",
            instructions="Hello, you are helpful assistant and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        assert assistant.id

        thread = await ai_client.create_thread(tool_resources=ToolResources(file_search=fs))
        assert thread.id
        # create message
        message = await ai_client.create_message(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = await ai_client.list_messages(thread.id)
        assert len(messages)
        await ai_client.delete_assistant(assistant.id)
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy_async
    async def test_create_assistant_with_interpreter_azure(self, **kwargs):
        """Test Create assistant with code interpreter with azure asset ids."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_create_assistant_with_interpreter(data_sources=[ds], **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_assistant_with_interpreter_file_ids(self, **kwargs):
        """Test Create assistant with code interpreter with file IDs."""
        await self._do_test_create_assistant_with_interpreter(file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_assistant_with_interpreter(self, **kwargs):
        """Test create assistant with code interpreter and project asset id"""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        code_interpreter = CodeInterpreterTool()

        file_id = None
        if "file_path" in kwargs:
            file = await ai_client.upload_file_and_poll(
                file_path=kwargs["file_path"], purpose=FilePurpose.ASSISTANTS
            )
            assert file.id, "The file was not uploaded."
            file_id = file.id

        cdr = CodeInterpreterToolResource(
            file_ids=[file_id] if file_id else None,
            data_sources=kwargs.get("data_sources"),
        )
        tr = ToolResources(code_interpreter=cdr)
        # notice that CodeInterpreter must be enabled in the assistant creation, otherwise the assistant will not be able to see the file attachment
        assistant = await ai_client.create_assistant(
            model="gpt-4-1106-preview",
            name="my-assistant",
            instructions="Hello, you are helpful assistant and can search information from uploaded files",
            tools=code_interpreter.definitions,
            tool_resources=tr,
        )
        assert assistant.id, "Assistant was not created"

        thread = await ai_client.create_thread()
        assert thread.id, "The thread was not created."

        message = await ai_client.create_message(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id, "The run was not created."
        await self._remove_file_maybe(file_id, ai_client)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        await ai_client.delete_assistant(assistant.id)
        messages = await ai_client.list_messages(thread_id=thread.id)
        assert len(messages), "No messages were created"
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy_async
    async def test_create_thread_with_interpreter_azure(self, **kwargs):
        """Test Create assistant with code interpreter with azure asset ids."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_create_thread_with_interpreter(data_sources=[ds], **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_thread_with_interpreter_file_ids(self, **kwargs):
        """Test Create assistant with code interpreter with file IDs."""
        await self._do_test_create_thread_with_interpreter(file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_thread_with_interpreter(self, **kwargs):
        """Test create assistant with code interpreter and project asset id"""
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        code_interpreter = CodeInterpreterTool()

        file_id = None
        if "file_path" in kwargs:
            file = await ai_client.upload_file_and_poll(
                file_path=kwargs["file_path"], purpose=FilePurpose.ASSISTANTS
            )
            assert file.id, "The file was not uploaded."
            file_id = file.id

        cdr = CodeInterpreterToolResource(
            file_ids=[file_id] if file_id else None,
            data_sources=kwargs.get("data_sources"),
        )
        tr = ToolResources(code_interpreter=cdr)
        # notice that CodeInterpreter must be enabled in the assistant creation, otherwise the assistant will not be able to see the file attachment
        assistant = await ai_client.create_assistant(
            model="gpt-4-1106-preview",
            name="my-assistant",
            instructions="You are helpful assistant",
            tools=code_interpreter.definitions,
        )
        assert assistant.id, "Assistant was not created"

        thread = await ai_client.create_thread(tool_resources=tr)
        assert thread.id, "The thread was not created."

        message = await ai_client.create_message(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id, "The run was not created."
        await self._remove_file_maybe(file_id, ai_client)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        await ai_client.delete_assistant(assistant.id)
        messages = await ai_client.list_messages(thread.id)
        assert len(messages)
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("Failing with Http Response Errors.")
    @recorded_by_proxy_async
    async def test_create_assistant_with_inline_vs_azure(self, **kwargs):
        """Test creation of asistant with vector store inline."""
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        ds = [
            VectorStoreDataSource(
                asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
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
        assistant = await ai_client.create_assistant(
            model="gpt-4o",
            name="my-assistant",
            instructions="Hello, you are helpful assistant and can search information from uploaded files",
            tools=file_search.definitions,
            tool_resources=ToolResources(file_search=fs),
        )
        assert assistant.id

        thread = await ai_client.create_thread()
        assert thread.id
        # create message
        message = await ai_client.create_message(
            thread_id=thread.id, role="user", content="What does the attachment say?"
        )
        assert message.id, "The message was not created."

        run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = await ai_client.list_messages(thread.id)
        assert len(messages)
        await ai_client.delete_assistant(assistant.id)
        await ai_client.close()

    @assistantClientPreparer()
    @pytest.mark.skip("The API is not supported yet.")
    @recorded_by_proxy_async
    async def test_create_attachment_in_thread_azure(self, **kwargs):
        """Create thread with message attachment inline with azure asset IDs."""
        ds = VectorStoreDataSource(
            asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        await self._do_test_create_attachment_in_thread_azure(data_sources=[ds], **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("File ID issues with sanitization.")
    @recorded_by_proxy_async
    async def test_create_attachment_in_thread_file_ids(self, **kwargs):
        """Create thread with message attachment inline with azure asset IDs."""
        await self._do_test_create_attachment_in_thread_azure(file_path=self._get_data_file(), **kwargs)

    async def _do_test_create_attachment_in_thread_azure(self, **kwargs):
        # create client
        ai_client = self.create_client(**kwargs)
        assert isinstance(ai_client, AssistantsClient)

        file_id = await self._get_file_id_maybe(ai_client, **kwargs)

        file_search = FileSearchTool()
        assistant = await ai_client.create_assistant(
            model="gpt-4o",
            name="my-assistant",
            instructions="Hello, you are helpful assistant and can search information from uploaded files",
            tools=file_search.definitions,
        )
        assert assistant.id

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
        thread = await ai_client.create_thread(messages=[message])
        assert thread.id

        run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.status == "completed", f"Error in run: {run.last_error}"
        messages = await ai_client.list_messages(thread.id)
        assert len(messages)
        await ai_client.delete_assistant(assistant.id)
        await ai_client.close()

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_azure_function_call(self, **kwargs):
        """Test calling Azure functions."""
        # Note: This test was recorded in westus region as for now
        # 2025-02-05 it is not supported in test region (East US 2)
        # create client
        storage_queue = kwargs["azure_ai_assistants_tests_storage_queue"]
        async with self.create_client(**kwargs) as client:
            azure_function_tool = AzureFunctionTool(
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
            assistant = await client.create_assistant(
                model="gpt-4",
                name="azure-function-assistant-foo",
                instructions=(
                    "You are a helpful support assistant. Use the provided function any "
                    "time the prompt contains the string 'What would foo say?'. When "
                    "you invoke the function, ALWAYS specify the output queue uri parameter as "
                    f"'{storage_queue}/azure-function-tool-output'"
                    '. Always responds with "Foo says" and then the response from the tool.'
                ),
                headers={"x-ms-enable-preview": "true"},
                tools=azure_function_tool.definitions,
            )
            assert assistant.id, "The assistant was not created"

            # Create a thread
            thread = await client.create_thread()
            assert thread.id, "The thread was not created."

            # Create a message
            message = await client.create_message(
                thread_id=thread.id,
                role="user",
                content="What is the most prevalent element in the universe? What would foo say?",
            )
            assert message.id, "The message was not created."

            run = await client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
            assert run.status == RunStatus.COMPLETED, f"The run is in {run.status} state."

            # Get messages from the thread
            messages = await client.list_messages(thread_id=thread.id)
            assert len(messages.text_messages) > 1, "No messages were received from assistant."

            # Chech that we have function response in at least one message.
            assert any("bar" in msg.text.value.lower() for msg in messages.text_messages)

            # Delete the assistant once done
            result = await client.delete_assistant(assistant.id)
            assert result.deleted, "The assistant was not deleted."

    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_client_with_thread_messages(self, **kwargs):
        """Test assistant with thread messages."""
        async with self.create_client(**kwargs) as client:

            # [START create_assistant]
            assistant = await client.create_assistant(
                model="gpt-4",
                name="my-assistant",
                instructions="You are helpful assistant",
            )
            assert assistant.id, "The assistant was not created."
            thread = await client.create_thread()
            assert thread.id, "Thread was not created"

            message = await client.create_message(
                thread_id=thread.id, role="user", content="What is the equation of light energy?"
            )
            assert message.id, "The message was not created."

            additional_messages = [
                ThreadMessageOptions(role=MessageRole.ASSISTANT, content="E=mc^2"),
                ThreadMessageOptions(role=MessageRole.USER, content="What is the impedance formula?"),
            ]
            run = await client.create_run(
                thread_id=thread.id, assistant_id=assistant.id, additional_messages=additional_messages
            )

            # poll the run as long as run status is queued or in progress
            while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS]:
                # wait for a second
                time.sleep(1)
                run = await client.get_run(
                    thread_id=thread.id,
                    run_id=run.id,
                )
            assert run.status in RunStatus.COMPLETED, run.last_error

            assert (await client.delete_assistant(assistant.id)).deleted, "The assistant was not deleted"
            messages = await client.list_messages(thread_id=thread.id)
            assert len(messages.data), "The data from the assistant was not received."

    @assistantClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_include_file_search_results_no_stream(self, **kwargs):
        """Test using include_file_search."""
        await self._do_test_include_file_search_results(use_stream=False, include_content=True, **kwargs)
        await self._do_test_include_file_search_results(use_stream=False, include_content=False, **kwargs)

    @assistantClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
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
                    asset_identifier=kwargs["azure_ai_assistants_tests_data_path"],
                    asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
                )
            ]
            vector_store = await ai_client.create_vector_store_and_poll(
                file_ids=[], data_sources=ds, name="my_vectorstore"
            )
            # vector_store = await ai_client.get_vector_store('vs_M9oxKG7JngORHcYNBGVZ6Iz3')
            assert vector_store.id

            file_search = FileSearchTool(vector_store_ids=[vector_store.id])
            assistant = await ai_client.create_assistant(
                model="gpt-4o",
                name="my-assistant",
                instructions="Hello, you are helpful assistant and can search information from uploaded files",
                tools=file_search.definitions,
                tool_resources=file_search.resources,
            )
            assert assistant.id
            thread = await ai_client.create_thread()
            assert thread.id
            # create message
            message = await ai_client.create_message(
                thread_id=thread.id,
                role="user",
                # content="What does the attachment say?"
                content="What Contoso Galaxy Innovations produces?",
            )
            assert message.id, "The message was not created."
            include = [RunAdditionalFieldList.FILE_SEARCH_CONTENTS] if include_content else None

            if use_stream:
                run = None
                async with await ai_client.create_stream(
                    thread_id=thread.id, assistant_id=assistant.id, include=include
                ) as stream:
                    async for event_type, event_data, _ in stream:
                        if isinstance(event_data, ThreadRun):
                            run = event_data
                        elif event_type == AssistantStreamEvent.DONE:
                            print("Stream completed.")
                            break
            else:
                run = await ai_client.create_and_process_run(
                    thread_id=thread.id, assistant_id=assistant.id, include=include
                )
                assert run.status == RunStatus.COMPLETED
            assert run is not None
            steps = await ai_client.list_run_steps(thread_id=thread.id, run_id=run.id, include=include)
            # The 1st (not 0th) step is a tool call.
            step_id = steps.data[1].id
            one_step = await ai_client.get_run_step(
                thread_id=thread.id, run_id=run.id, step_id=step_id, include=include
            )
            self._assert_file_search_valid(one_step.step_details.tool_calls[0], include_content)
            self._assert_file_search_valid(steps.data[1].step_details.tool_calls[0], include_content)

            messages = await ai_client.list_messages(thread_id=thread.id)
            assert len(messages)

            await ai_client.delete_vector_store(vector_store.id)
            # delete assistant and close client
            await ai_client.delete_assistant(assistant.id)
            print("Deleted assistant")
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

    @assistantClientPreparer()
    @pytest.mark.skip("Recordings not yet implemented")
    @recorded_by_proxy_async
    async def test_assistants_with_json_schema(self, **kwargs):
        """Test structured output from the assistant."""
        async with self.create_client(**kwargs) as ai_client:
            assistant = await ai_client.create_assistant(
                # Note only gpt-4o-mini-2024-07-18 and
                # gpt-4o-2024-08-06 and later support structured output.
                model="gpt-4o-mini",
                name="my-assistant",
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
            assert assistant.id

            thread = await ai_client.create_thread()
            assert thread.id

            message = await ai_client.create_message(
                thread_id=thread.id,
                role="user",
                content=("The mass of the Mars is 6.4171E23 kg"),
            )
            assert message.id

            run = await ai_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)

            assert run.status == RunStatus.COMPLETED, run.last_error.message

            del_assistant = await ai_client.delete_assistant(assistant.id)
            assert del_assistant.deleted

            messages = await ai_client.list_messages(thread_id=thread.id)

            planet_info = []
            # The messages are following in the reverse order,
            # we will iterate them and output only text contents.
            for data_point in reversed(messages.data):
                last_message_content = data_point.content[-1]
                # We will only list assistant responses here.
                if isinstance(last_message_content, MessageTextContent) and data_point.role == MessageRole.ASSISTANT:
                    planet_info.append(json.loads(last_message_content.text.value))
            assert len(planet_info) == 1
            assert len(planet_info[0]) == 2
            assert planet_info[0].get("mass") == pytest.approx(6.4171e23, 1e22)
            assert planet_info[0].get("planet") == "Mars"

    async def _get_file_id_maybe(self, ai_client: AssistantsClient, **kwargs) -> str:
        """Return file id if kwargs has file path."""
        if "file_path" in kwargs:
            file = await ai_client.upload_file_and_poll(
                file_path=kwargs["file_path"], purpose=FilePurpose.ASSISTANTS
            )
            assert file.id, "The file was not uploaded."
            return file.id
        return None

    async def _remove_file_maybe(self, file_id: str, ai_client: AssistantsClient) -> None:
        """Remove file if we have file ID."""
        if file_id:
            await ai_client.delete_file(file_id)

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
    # test assistant creation and deletion
    @assistantClientPreparer()
    @recorded_by_proxy_async
    async def test_negative_create_delete_assistant(self, **kwargs):
        # create client using bad endpoint
        bad_connection_string = "https://foo.bar.some-domain.ms;00000000-0000-0000-0000-000000000000;rg-resour-cegr-oupfoo1;abcd-abcdabcdabcda-abcdefghijklm"

        credential = self.get_credential(AssistantsClient, is_async=False)
        client = AssistantsClient.from_connection_string(
            credential=credential,
            connection=bad_connection_string,
        )
        
        # attempt to create assistant with bad client
        exception_caught = False
        try:
            assistant = await client.create_assistant(
                model="gpt-4o", name="my-assistant", instructions="You are helpful assistant"
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
