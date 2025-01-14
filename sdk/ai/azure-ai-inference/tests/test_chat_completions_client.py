# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import azure.ai.inference as sdk

from model_inference_test_base import (
    ModelClientTestBase,
    ServicePreparerChatCompletions,
    ServicePreparerAOAIChatCompletions,
)

from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential


# The test class name needs to start with "Test" to get collected by pytest
class TestChatCompletionsClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #         CHAT COMPLETIONS REGRESSION TESTS - NO SERVICE RESPONSE REQUIRED
    #
    # **********************************************************************************

    # Regression test. Send a request that includes all supported types of input objects. Make sure the resulting
    # JSON payload that goes up to the service (including headers) is the correct one after hand-inspection.
    def test_chat_completions_request_payload(self, **kwargs):

        client = sdk.ChatCompletionsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
        )

        for _ in range(2):
            try:
                _ = client.complete(
                    messages=[
                        sdk.models.SystemMessage(content="system prompt"),
                        sdk.models.UserMessage(content="user prompt 1"),
                        sdk.models.AssistantMessage(
                            tool_calls=[
                                sdk.models.ChatCompletionsToolCall(
                                    function=sdk.models.FunctionCall(
                                        name="my-first-function-name",
                                        arguments={"first_argument": "value1", "second_argument": "value2"},
                                    ),
                                    id="some-id",
                                ),
                                sdk.models.ChatCompletionsToolCall(
                                    function=sdk.models.FunctionCall(
                                        name="my-second-function-name", arguments={"first_argument": "value1"}
                                    ),
                                    id="some-other-id",
                                ),
                            ]
                        ),
                        sdk.models.ToolMessage(tool_call_id="some id", content="function response"),
                        sdk.models.AssistantMessage(content="assistant prompt"),
                        sdk.models.UserMessage(
                            content=[
                                sdk.models.TextContentItem(text="user prompt 2"),
                                sdk.models.ImageContentItem(
                                    image_url=sdk.models.ImageUrl(
                                        url="https://does.not.exit/image.png",
                                        detail=sdk.models.ImageDetailLevel.HIGH,
                                    ),
                                ),
                            ],
                        ),
                    ],
                    model_extras={
                        "key1": 1,
                        "key2": True,
                        "key3": "Some value",
                        "key4": [1, 2, 3],
                        "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
                    },
                    frequency_penalty=0.123,
                    max_tokens=321,
                    model="some-model-id",
                    presence_penalty=4.567,
                    response_format="json_object",
                    seed=654,
                    stop=["stop1", "stop2"],
                    stream=True,
                    temperature=8.976,
                    tool_choice=sdk.models.ChatCompletionsToolChoicePreset.AUTO,
                    tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
                    top_p=9.876,
                    raw_request_hook=self.request_callback,
                )
                assert False
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_chat_completions_json_request_payload()
                continue

    # Regression test. Send a request that includes all supported types of input objects, with chat settings
    # specified in the constructor. Make sure the resulting JSON payload that goes up to the service
    # is the correct one after hand-inspection.
    def test_chat_completions_request_payload_with_defaults(self, **kwargs):

        client = sdk.ChatCompletionsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
            model_extras={
                "key1": 1,
                "key2": True,
                "key3": "Some value",
                "key4": [1, 2, 3],
                "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
            },
            frequency_penalty=0.123,
            max_tokens=321,
            model="some-model-id",
            presence_penalty=4.567,
            response_format="json_object",
            seed=654,
            stop=["stop1", "stop2"],
            temperature=8.976,
            tool_choice=sdk.models.ChatCompletionsToolChoicePreset.AUTO,
            tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
            top_p=9.876,
        )

        for _ in range(2):
            try:
                _ = client.complete(
                    messages=[
                        sdk.models.SystemMessage("system prompt"),
                        sdk.models.UserMessage("user prompt 1"),
                        sdk.models.AssistantMessage(
                            tool_calls=[
                                sdk.models.ChatCompletionsToolCall(
                                    function=sdk.models.FunctionCall(
                                        name="my-first-function-name",
                                        arguments={"first_argument": "value1", "second_argument": "value2"},
                                    ),
                                    id="some-id",
                                ),
                                sdk.models.ChatCompletionsToolCall(
                                    function=sdk.models.FunctionCall(
                                        name="my-second-function-name", arguments={"first_argument": "value1"}
                                    ),
                                    id="some-other-id",
                                ),
                            ]
                        ),
                        sdk.models.ToolMessage("function response", tool_call_id="some id"),
                        sdk.models.AssistantMessage("assistant prompt"),
                        sdk.models.UserMessage(
                            [
                                sdk.models.TextContentItem(text="user prompt 2"),
                                sdk.models.ImageContentItem(
                                    image_url=sdk.models.ImageUrl(
                                        url="https://does.not.exit/image.png",
                                        detail=sdk.models.ImageDetailLevel.HIGH,
                                    ),
                                ),
                            ],
                        ),
                    ],
                    stream=True,
                    raw_request_hook=self.request_callback,
                )
                assert False
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_chat_completions_json_request_payload()
                continue

    # Regression test. Send a request that includes all supported types of input objects, with chat settings
    # specified in the constructor and all of them overwritten in the 'complete' call.
    # Make sure the resulting JSON payload that goes up to the service is the correct one after hand-inspection.
    def test_chat_completions_request_payload_with_defaults_and_overrides(self, **kwargs):

        client = sdk.ChatCompletionsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
            model_extras={
                "key1": 2,
                "key3": False,
                "key4": "Some other value",
                "key9": "Yet another value",
            },
            frequency_penalty=0.456,
            max_tokens=768,
            model="some-other-model-id",
            presence_penalty=1.234,
            response_format="text",
            seed=987,
            stop=["stop3", "stop5"],
            temperature=5.432,
            tool_choice=sdk.models.ChatCompletionsNamedToolChoice(
                function=sdk.models.ChatCompletionsNamedToolChoiceFunction(name="my-function-name")
            ),
            tools=[ModelClientTestBase.TOOL2],
            top_p=3.456,
        )

        for _ in range(2):
            try:
                _ = client.complete(
                    messages=[
                        sdk.models.SystemMessage(content="system prompt"),
                        sdk.models.UserMessage(content="user prompt 1"),
                        sdk.models.AssistantMessage(
                            tool_calls=[
                                sdk.models.ChatCompletionsToolCall(
                                    function=sdk.models.FunctionCall(
                                        name="my-first-function-name",
                                        arguments={"first_argument": "value1", "second_argument": "value2"},
                                    ),
                                    id="some-id",
                                ),
                                sdk.models.ChatCompletionsToolCall(
                                    function=sdk.models.FunctionCall(
                                        name="my-second-function-name", arguments={"first_argument": "value1"}
                                    ),
                                    id="some-other-id",
                                ),
                            ]
                        ),
                        sdk.models.ToolMessage(tool_call_id="some id", content="function response"),
                        sdk.models.AssistantMessage(content="assistant prompt"),
                        sdk.models.UserMessage(
                            content=[
                                sdk.models.TextContentItem(text="user prompt 2"),
                                sdk.models.ImageContentItem(
                                    image_url=sdk.models.ImageUrl(
                                        url="https://does.not.exit/image.png",
                                        detail=sdk.models.ImageDetailLevel.HIGH,
                                    ),
                                ),
                            ],
                        ),
                    ],
                    model_extras={
                        "key1": 1,
                        "key2": True,
                        "key3": "Some value",
                        "key4": [1, 2, 3],
                        "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
                    },
                    frequency_penalty=0.123,
                    max_tokens=321,
                    model="some-model-id",
                    presence_penalty=4.567,
                    response_format="json_object",
                    seed=654,
                    stop=["stop1", "stop2"],
                    stream=True,
                    temperature=8.976,
                    tool_choice=sdk.models.ChatCompletionsToolChoicePreset.AUTO,
                    tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
                    top_p=9.876,
                    raw_request_hook=self.request_callback,
                )
                assert False
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_chat_completions_json_request_payload()
                continue

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - CHAT COMPLETIONS
    #
    # **********************************************************************************

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_load_chat_completions_client(self, **kwargs):

        client = self._load_chat_client(**kwargs)
        assert isinstance(client, sdk.ChatCompletionsClient)
        assert client._model_info

        response1 = client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(
            response1, "chat-completion"
        )  # TODO: This should be ModelType.CHAT_COMPLETION once the model is fixed
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_get_model_info_on_chat_client(self, **kwargs):

        client = self._create_chat_client(**kwargs)
        assert not client._model_info

        response1 = client.get_model_info()
        assert client._model_info  # pylint: disable=protected-access

        self._print_model_info_result(response1)
        self._validate_model_info_result(
            response1, "chat-completion"  # TODO: This should be chat_comletions according to REST API spec...
        )  # TODO: This should be ModelType.CHAT_COMPLETION once the model is fixed

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_entra_id_auth(self, **kwargs):
        with self._create_chat_client(key_auth=False, **kwargs) as client:
            messages = [
                sdk.models.SystemMessage(
                    content="You are a helpful assistant answering questions regarding length units."
                ),
                sdk.models.UserMessage(content="How many feet are in a mile?"),
            ]
            response = client.complete(messages=messages)
            self._print_chat_completions_result(response)
            self._validate_chat_completions_result(response, ["5280", "5,280"])
            assert json.dumps(response.as_dict(), indent=2) == response.__str__()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_multi_turn(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        messages = [
            sdk.models.SystemMessage("You are a helpful assistant answering questions regarding length units."),
            sdk.models.UserMessage("How many feet are in a mile?"),
        ]
        response = client.complete(messages=messages)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        assert json.dumps(response.as_dict(), indent=2) == response.__str__()
        messages.append(sdk.models.AssistantMessage(response.choices[0].message.content))
        messages.append(sdk.models.UserMessage("and how many yards?"))
        response = client.complete(messages=messages)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["1760", "1,760"])
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_model_extras(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        response = client.complete(
            messages=[sdk.models.UserMessage(content="How many feet are in a mile?")],
            model_extras={"n": 1},
            raw_request_hook=self.request_callback,
        )

        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        self._validate_model_extras(self.pipeline_request.http_request.data, self.pipeline_request.http_request.headers)
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_json_input(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        request_body = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "How many feet are in a mile?"},
            ]
        }
        response = client.complete(request_body)
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_bytes_input(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        response = client.complete(self._read_text_file("chat.test.json"))
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_streaming(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        response = client.complete(
            stream=True,
            messages=[
                sdk.models.SystemMessage("You are a helpful assistant."),
                sdk.models.UserMessage("Give me 3 good reasons why I should exercise every day."),
            ],
        )
        self._validate_chat_completions_streaming_result(response)
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_streaming_with_json_input(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        request_body = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Give me 3 good reasons why I should exercise every day."},
            ],
            "stream": True,
        }
        response = client.complete(request_body)
        self._validate_chat_completions_streaming_result(response)
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_tool(self, **kwargs):
        forecast_tool = sdk.models.ChatCompletionsToolDefinition(
            function=sdk.models.FunctionDefinition(
                name="get_max_temperature",
                description="A function that returns the forecasted maximum temperature IN a given city, a given few days from now, in Fahrenheit. It returns `unknown` if the forecast is not known.",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city",
                        },
                        "days": {
                            "type": "string",
                            "description": "The number of days from now, starting from 0, where 0 represents today, 1 represents tomorrow, etc.",
                        },
                    },
                    "required": ["city", "days"],
                },
            )
        )
        client = self._create_chat_client(**kwargs)
        messages = [
            sdk.models.SystemMessage(content="You are an assistant that helps users find weather information."),
            sdk.models.UserMessage(content="what's the maximum temperature in Seattle two days from now?"),
        ]
        response = client.complete(
            messages=messages,
            tools=[forecast_tool],
        )
        self._print_chat_completions_result(response)
        self._validate_chat_completions_tool_result(response)
        messages.append(sdk.models.AssistantMessage(tool_calls=response.choices[0].message.tool_calls))
        messages.append(
            sdk.models.ToolMessage(
                content="62",
                tool_call_id=response.choices[0].message.tool_calls[0].id,
            )
        )
        response = client.complete(
            messages=messages,
            tools=[forecast_tool],
        )
        self._validate_chat_completions_result(response, ["62"])
        client.close()

    # We use AOAI endpoint here because at the moment there is no MaaS model that supports
    # input image.
    @ServicePreparerAOAIChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_input_image_file(self, **kwargs):
        client = self._create_aoai_chat_client(**kwargs)

        # Construct the full path to the image file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_file_path = os.path.join(script_dir, "test_image1.png")

        response = client.complete(
            messages=[
                sdk.models.SystemMessage(content="You are an AI assistant that describes images in details."),
                sdk.models.UserMessage(
                    content=[
                        sdk.models.TextContentItem(text="What's in this image?"),
                        sdk.models.ImageContentItem(
                            image_url=sdk.models.ImageUrl.load(
                                image_file=image_file_path,
                                image_format="png",
                                detail=sdk.models.ImageDetailLevel.HIGH,
                            ),
                        ),
                    ],
                ),
            ],
        )
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(
            response, ["juggling", "balls", "blue", "red", "green", "yellow"], is_aoai=True
        )
        client.close()

    # We use AOAI endpoint here because at the moment there is no MaaS model that supports
    # input image.
    @ServicePreparerAOAIChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_input_image_url(self, **kwargs):
        url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/ai/azure-ai-inference/tests/test_image1.png"
        client = self._create_aoai_chat_client(**kwargs)
        response = client.complete(
            messages=[
                sdk.models.SystemMessage(content="You are an AI assistant that describes images in details."),
                sdk.models.UserMessage(
                    content=[
                        sdk.models.TextContentItem(text="What's in this image?"),
                        sdk.models.ImageContentItem(
                            image_url=sdk.models.ImageUrl(url=url, detail=sdk.models.ImageDetailLevel.AUTO)
                        ),
                    ],
                ),
            ],
        )
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(
            response, ["juggling", "balls", "blue", "red", "green", "yellow"], is_aoai=True
        )
        client.close()

    # We use AOAI endpoint here because at the moment MaaS does not support Entra ID auth.
    @ServicePreparerAOAIChatCompletions()
    @recorded_by_proxy
    def test_aoai_chat_completions_with_entra_id_auth(self, **kwargs):
        client = self._create_aoai_chat_client(key_auth=False, **kwargs)
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant answering questions regarding length units."),
            sdk.models.UserMessage(content="How many feet are in a mile?"),
        ]
        response = client.complete(messages=messages)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["5280", "5,280"], is_aoai=True)
        client.close()

    @ServicePreparerAOAIChatCompletions()
    @recorded_by_proxy
    def test_aoai_chat_completions_with_structured_output(self, **kwargs):
        client = self._create_aoai_chat_client(key_auth=True, **kwargs)
        response_format = sdk.models.JsonSchemaFormat(
            name="Test_JSON_Schema",
            schema=ModelClientTestBase.OUTPUT_FORMAT_JSON_SCHEMA,
            description="Describes a set of distances between locations",
            strict=True,
        )
        print(type(response_format))
        messages = [
            sdk.models.SystemMessage("You are a helpful assistant answering questions on US geography"),
            sdk.models.UserMessage("What's the distance between Seattle and Portland, as the crow flies?"),
        ]
        response = client.complete(messages=messages, response_format=response_format)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(
            response, ["distances", "location1", "Seattle", "location2", "Portland"], is_aoai=True, is_json=True
        )
        client.close()

    # **********************************************************************************
    #
    #                            ERROR TESTS - CHAT COMPLETIONS
    #
    # **********************************************************************************

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_with_auth_failure(self, **kwargs):
        client = self._create_chat_client(bad_key=True, **kwargs)
        exception_caught = False
        try:
            response = client.complete(messages=[sdk.models.UserMessage("How many feet are in a mile?")])
        except AzureError as e:
            exception_caught = True
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 401
            assert "auth token validation failed" in e.message.lower()
        client.close()
        assert exception_caught

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_embeddings_on_chat_completion_endpoint(self, **kwargs):
        client = self._create_embeddings_client_with_chat_completions_credentials(**kwargs)
        exception_caught = False
        try:
            response = client.embed(input=["first phrase", "second phrase", "third phrase"])
        except AzureError as e:
            exception_caught = True
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 404 or e.status_code == 405  # `404 - not found` or `405 - method not allowed`
            assert "not found" in e.message.lower() or "not allowed" in e.message.lower()
        client.close()
        assert exception_caught
