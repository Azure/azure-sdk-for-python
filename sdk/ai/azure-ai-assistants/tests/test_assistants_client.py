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

import azure.ai.assistants as sdk
from azure.core.pipeline.transport import RequestsTransport
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential
from azure.ai.assistants.models import FunctionTool
# TODO from models import assistantthread or whatever 
# TODO clean this up / get rid of anything not in use


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


AssistantClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    'azure_ai_assistants',
    azure_ai_assistants_endpoint="https://your-deployment-name.openai.azure.com/",
    azure_ai_assistants_key="00000000000000000000000000000000"
    
)

# create tool for assistant use
def fetch_current_datetime():
        """
        Get the current time as a JSON string.

        :return: The current time in JSON format.
        :rtype: str
        """
        current_time = datetime.datetime.now()
        time_json = json.dumps({"current_time": current_time.strftime("%Y-%m-%d %H:%M:%S")})
        return time_json


# Statically defined user functions for fast reference
user_functions = {"fetch_current_datetime": fetch_current_datetime}


# The test class name needs to start with "Test" to get collected by pytest
class TestAssistantClient(AzureRecordedTestCase):

    # helper function: create client and using environment variables
    def create_client(self, **kwargs):
        # fetch environment variables
        endpoint = kwargs.pop("azure_ai_assistants_endpoint")
        credential = AzureKeyCredential(kwargs.pop("azure_ai_assistants_key"))
        api_version=os.environ.get("AZUREAI_API_VERSION", "2024-07-01-preview")

        # create and return client
        client = sdk.AssistantsClient(endpoint=endpoint, credential=credential, api_version=api_version)
        return client
    
    # for debugging purposes: if a test fails and its assistant has not been deleted, it will continue to show up in the assistants list
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_clear_client(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # clear assistant list
        assistants = client.list_assistants().data
        for assistant in assistants:
            client.delete_assistant(assistant.id)
        assert client.list_assistants().data.__len__() == 0
       
        # close client
        client.close()


#     # **********************************************************************************
#     #
#     #                               UNIT TESTS
#     #
#     # **********************************************************************************

    

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Assistant APIs
    # #
    # # **********************************************************************************
    
    # test client creation
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_client(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # close client
        client.close()

    # test assistant creation and deletion
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_delete_assistant(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)
        print("Created client")

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)
        
        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test assistant creation with tools
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_assistant_with_tools(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # initialize assistant functions
        functions = FunctionTool(functions=user_functions)

        # create assistant with tools
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant", tools=functions.definitions)
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)
        assert assistant.tools
        assert assistant.tools[0]['function'] == functions.definitions[0]['function']
        print("Tool successfully submitted:", functions.definitions[0]['function']['name'])

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_update_assistant(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id

        # update assistant and confirm changes went through
        assistant.update(name="my-assistant2", instructions="You are helpful assistant")
        assert assistant.name
        assert assistant.name == "my-assistant2"

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_assistant_list(self, **kwargs):
        # create client and ensure there are no previous assistants
        client = self.create_client(**kwargs)
        assert client.list_assistants().data.__len__() == 0

        # create assistant and check that it appears in the list
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert client.list_assistants().data.__len__() == 1
        assert client.list_assistants().data[0].id == assistant.id 

        # create second assistant and check that it appears in the list
        assistant2 = client.create_assistant(model="gpt-4o", name="my-assistant2", instructions="You are helpful assistant")
        assert client.list_assistants().data.__len__() == 2
        assert client.list_assistants().data[0].id == assistant.id or client.list_assistants().data[1].id == assistant.id 

        # delete assistants and check list 
        client.delete_assistant(assistant.id)
        assert client.list_assistants().data.__len__() == 1
        assert client.list_assistants().data[0].id == assistant2.id 

        client.delete_assistant(assistant2.id)
        assert client.list_assistants().data.__len__() == 0
        print("Deleted assistants")

        # close client
        client.close()

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - Thread APIs
    #
    # **********************************************************************************

    # test creating thread  
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        # assert isinstance(thread, AssistantThread) TODO finish this ! need to import assistantThread from _models
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test getting thread
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_get_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # get thread
        thread2 = client.get_thread(thread.id)
        assert thread2.id
        assert thread.id == thread2.id
        print("Got thread, thread ID", thread2.id)


        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    '''
    TODO what  can I update a thread with? 
    # test updating thread  
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_update_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # update thread
        client.update_thread(thread.id, ) # TODO what can we update it with? 
        assert not thread

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()
    '''

    '''
    # TODO this test is failing?  client.delete_thread(thread.id) isn't working
    # status_code = 404, response = <HttpResponse: 404 Resource Not Found, Content-Type: application/json>
    # error_map = {304: <class 'azure.core.exceptions.ResourceNotModifiedError'>, 401: <class 'azure.core.exceptions.ClientAuthenticatio..., 404: <class 'azure.core.exceptions.ResourceNotFoundError'>, 409: <class 'azure.core.exceptions.ResourceExistsError'>}
    
    # test deleting thread
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_delete_thread(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        # assert isinstance(thread, AssistantThread) TODO finish this ! need to import assistantThread from _models
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # delete thread
        deletion_status = client.delete_thread(thread.id)
        # assert not thread

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()
    '''


    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Message APIs
    # #
    # # **********************************************************************************
    
    # test creating message in a thread
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_message(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test creating multiple messages in a thread
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_multiple_messages(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create messages
        message = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)
        message2 = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me another joke")
        assert message2.id
        print("Created message, message ID", message2.id)
        message3 = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a third joke")
        assert message3.id
        print("Created message, message ID", message3.id)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test listing messages in a thread
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_list_messages(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check that initial message list is empty
        messages0 = client.list_messages(thread_id=thread.id)
        print(messages0.data)
        assert messages0.data.__len__() == 0

        # create messages and check message list for each one
        message1 = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message1.id
        print("Created message, message ID", message1.id)
        messages1 = client.list_messages(thread_id=thread.id)
        assert messages1.data.__len__() == 1
        assert messages1.data[0].id == message1.id 

        message2 = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me another joke")
        assert message2.id
        print("Created message, message ID", message2.id)
        messages2 = client.list_messages(thread_id=thread.id)
        assert messages2.data.__len__() == 2
        assert messages2.data[0].id == message2.id or messages2.data[1].id == message2.id

        message3 = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a third joke")
        assert message3.id
        print("Created message, message ID", message3.id)
        messages3 = client.list_messages(thread_id=thread.id)
        assert messages3.data.__len__() == 3
        assert messages3.data[0].id == message3.id or messages3.data[1].id == message2.id or messages3.data[2].id == message2.id

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test getting message in a thread
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_get_message(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # get message
        message2 = client.get_message(thread_id=thread.id, message_id=message.id)
        assert message2.id
        assert message.id == message2.id
        print("Got message, message ID", message.id)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    '''
    TODO format the updated body
    # test updating message in a thread
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_update_message(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # update message
        body_json = json.dumps # TODO format body into json -- figure out what the message looks like so I can update it (might be in that picture) 
        client.update_message(thread_id=thread.id, message_id=message.id, body=)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()
    '''

    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Run APIs
    # #
    # # **********************************************************************************

    # test creating run
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test getting run
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_get_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)

        # get run
        run2 = client.get_run(thread_id=thread.id, run_id=run.id)
        assert run2.id
        assert run.id == run2.id
        print("Got run, run ID", run2.id)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # TODO fix bc sometimes it works? and sometimes it doesnt? 
    # test sucessful run status     TODO test for cancelled/unsucessful runs
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_run_status(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check status
        assert run.status in ["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.get_run(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)

        assert run.status in ["cancelled", "failed", "completed", "expired"]
        print("Run completed with status:", run.status)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    '''
    # TODO another, but check that the number of runs decreases after cancelling runs
    # TODO can each thread only support one run? 
    # test listing runs
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_list_runs(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check list for current runs
        runs0 = client.list_runs(thread_id=thread.id)
        assert runs0.data.__len__() == 0

        # create run and check list
        run = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)
        runs1 = client.list_runs(thread_id=thread.id)
        assert runs1.data.__len__() == 1
        assert runs1.data[0].id == run.id

        # create second run
        run2 = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run2.id
        print("Created run, run ID", run2.id)
        runs2 = client.list_runs(thread_id=thread.id)
        assert runs2.data.__len__() == 2
        assert runs2.data[0].id == run2.id or runs2.data[1].id == run2.id

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()
    '''

    '''
    # TODO figure out what to update the run with
    # test updating run
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_update_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create run
        run = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)

        # update run
        body = json.dumps({'todo': 'placeholder'})
        client.update_run(thread_id=thread.id, run_id=run.id, body=body)

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()
    '''

    # test submitting tool outputs to run
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_submit_tool_outputs_to_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # initialize assistant functions
        functions = FunctionTool(functions=self.user_functions)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant", tools=functions.definitions)
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

        # check that tools are uploaded
        assert run.tools
        assert run.tools[0]['function'] == functions.definitions[0]['function']
        print("Tool successfully submitted:", functions.definitions[0]['function']['name'])

        # check status
        assert run.status in  ["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.get_run(thread_id=thread.id, run_id=run.id)

            # check if tools are needed
            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                print("Requires action: submit tool outputs")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run") # TODO how can i make sure that it wants tools? should i have some kind of error message?
                    client.cancel_run(thread_id=thread.id, run_id=run.id)
                    break

                # submit tool outputs to run
                tool_outputs = functions.execute(tool_calls)
                print("Tool outputs:", tool_outputs)
                if tool_outputs:
                    client.submit_tool_outputs_to_run(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            print("Current run status:", run.status)

        print("Run completed with status:", run.status)

        
        # check that messages used the tool
        messages = client.list_messages(thread_id=thread.id, run_id=run.id)
        tool_message = messages['data'][0]['content'][0]['text']['value']
        hour12 = time.strftime("%H")
        hour24 = time.strftime("%I")
        minute = time.strftime("%M")
        assert hour12 + ":" + minute in tool_message or hour24 + ":" + minute
        print("Used tool_outputs")

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test cancelling run
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_cancel_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

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
            run = client.get_run(thread_id=thread.id, run_id=run.id)
            print("Current run status:", run.status)
        assert run.status == "cancelled"
        print("Run cancelled")

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test create thread and run
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_create_thread_and_run(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread and run
        run = client.create_thread_and_run(assistant_id=assistant.id)
        assert run.id
        assert run.thread_id
        print("Created run, run ID", run.id)

        # get thread
        thread = client.get_thread(run.thread_id)
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # check status
        assert run.status in  ["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.get_run(thread_id=thread.id, run_id=run.id)
            # assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)

        assert run.status == "completed"
        print("Run completed")

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test listing run steps
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_list_run_step(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

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

        steps = client.list_run_steps(thread_id=thread.id, run_id=run.id)
        assert steps['data'].__len__() == 0

        # check status
        assert run.status in ["queued", "in_progress", "requires_action", "completed"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.get_run(thread_id=thread.id, run_id=run.id)
            assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)
            steps = client.list_run_steps(thread_id=thread.id, run_id=run.id)
            assert steps['data'].__len__() > 0 # TODO what else should we look at? 

        assert run.status == "completed"
        print("Run completed")

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()

    # test getting run step
    # TODO where are step ids from
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_get_run_step(self, **kwargs):
        # create client
        client = self.create_client(**kwargs)
        assert isinstance(client, sdk.AssistantsClient)

        # create assistant
        assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        assert assistant.id
        print("Created assistant, assistant ID", assistant.id)

        # create thread
        thread = client.create_thread()
        assert thread.id
        print("Created thread, thread ID", thread.id)

        # create message
        message = client.create_message(thread_id=thread.id, role="user", content="Hello, can you tell me a joke?")
        assert message.id
        print("Created message, message ID", message.id)

        # create run
        run = client.create_run(thread_id=thread.id, assistant_id=assistant.id)
        assert run.id
        print("Created run, run ID", run.id)

        # check status
        assert run.status in ["queued", "in_progress", "requires_action", "completed"]
        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.get_run(thread_id=thread.id, run_id=run.id)
            assert run.status in ["queued", "in_progress", "requires_action", "completed"]
            print("Run status:", run.status)

        # list steps, check that get_run_step works with first step_id
        steps = client.list_run_steps(thread_id=thread.id, run_id=run.id)
        assert steps['data'].__len__() > 0
        step = steps['data'][0]
        get_step = client.get_run_step(thread_id=thread.id, run_id=run.id, step_id=step.id)
        assert step == get_step

        # delete assistant and close client
        client.delete_assistant(assistant.id)
        print("Deleted assistant")
        client.close()
    
    # # **********************************************************************************
    # #
    # #                      HAPPY PATH SERVICE TESTS - Streaming APIs
    # #
    # # **********************************************************************************

    
    # # **********************************************************************************
    # #
    # #         NEGATIVE TESTS - TODO idk what goes here
    # #
    # # **********************************************************************************

    # test assistant creation and deletion
    @AssistantClientPreparer()
    @recorded_by_proxy
    def test_negative_create_delete_assistant(self, **kwargs):
        # create client using bad endpoint
        bad_endpoint = "https://your-deployment-name.openai.azure.com/"
        azure_ai_assistants_key = kwargs["azure_ai_assistants_key"]
        api_version=os.environ.get("AZUREAI_API_VERSION", "2024-07-01-preview")
        client = sdk.AssistantsClient(endpoint=bad_endpoint, credential=AzureKeyCredential(azure_ai_assistants_key), api_version=api_version)
        
        # attempt to create assistant with bad client
        exception_caught = False
        try:
            assistant = client.create_assistant(model="gpt-4o", name="my-assistant", instructions="You are helpful assistant")
        # check for error (will not have a status code since it failed on request -- no response was recieved)
        except ServiceRequestError as e:
            exception_caught = True
            assert e.message
            assert "failed to resolve 'your-deployment-name.openai.azure.com'" in e.message.lower()
        
        # close client and confirm an exception was caught
        client.close()
        assert exception_caught


