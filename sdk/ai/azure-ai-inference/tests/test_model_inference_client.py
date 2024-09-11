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
    ServicePreparerEmbeddings,
)
from azure.core.pipeline.transport import RequestsTransport
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential


# The test class name needs to start with "Test" to get collected by pytest
class TestModelClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    # Test custom code in ChatCompletions class to print its content in a nice multi-line JSON format
    def test_print_method_of_chat_completions_class(self, **kwargs):
        response = sdk.models.ChatCompletions(
            {
                "choices": [
                    {
                        "message": {
                            "content": "some content",
                            "role": "assistant",
                        }
                    }
                ]
            }
        )
        print(response)  # This will invoke the customized __str__ method
        assert json.dumps(response.as_dict(), indent=2) == response.__str__()

    # Test custom code in EmbeddingsResult class to print its content in a nice multi-line JSON format
    def test_print_method_of_embeddings_result_class(self, **kwargs):
        response = sdk.models.ChatCompletions(
            {
                "id": "f060ce24-0bbf-4aef-8341-62659b6e19be",
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            0.0013399124,
                            -0.01576233,
                        ],
                    },
                    {
                        "index": 1,
                        "embedding": [
                            0.036590576,
                            -0.0059547424,
                        ],
                    },
                ],
                "model": "model-name",
                "usage": {"prompt_tokens": 6, "completion_tokens": 0, "total_tokens": 6},
            }
        )
        print(response)  # This will invoke the customized __str__ method
        assert json.dumps(response.as_dict(), indent=2) == response.__str__()

    # Test custom code in ImageUrl class to load an image file
    def test_image_url_load(self, **kwargs):
        local_folder = os.path.dirname(os.path.abspath(__file__))
        image_file = os.path.join(local_folder, "test_image1.png")
        image_url = sdk.models.ImageUrl.load(
            image_file=image_file,
            image_format="png",
            detail=sdk.models.ImageDetailLevel.AUTO,
        )
        assert image_url
        assert image_url.url.startswith("data:image/png;base64,iVBORw")
        assert image_url.detail == sdk.models.ImageDetailLevel.AUTO

    # **********************************************************************************
    #
    #         EMBEDDINGS REGRESSION TESTS - NO SERVICE RESPONSE REQUIRED
    #
    # **********************************************************************************

    # Regression test. Send a request that includes all supported types of input objects. Make sure the resulting
    # JSON payload that goes up to the service (including headers) is the correct one after hand-inspection.
    def test_embeddings_request_payload(self, **kwargs):
        client = sdk.EmbeddingsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
        )
        for _ in range(2):
            try:
                response = client.embed(
                    input=["first phrase", "second phrase", "third phrase"],
                    dimensions=2048,
                    encoding_format=sdk.models.EmbeddingEncodingFormat.UBINARY,
                    input_type=sdk.models.EmbeddingInputType.QUERY,
                    model_extras={
                        "key1": 1,
                        "key2": True,
                        "key3": "Some value",
                        "key4": [1, 2, 3],
                        "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
                    },
                    model="some-model-id",
                    raw_request_hook=self.request_callback,
                )
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_embeddings_json_request_payload()
                continue
            assert False

    # Regression test. Send a request that includes all supported types of input objects, with embedding settings
    # specified in the constructor. Make sure the resulting JSON payload that goes up to the service
    # is the correct one after hand-inspection.
    def test_embeddings_request_payload_with_defaults(self, **kwargs):
        client = sdk.EmbeddingsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
            dimensions=2048,
            encoding_format=sdk.models.EmbeddingEncodingFormat.UBINARY,
            input_type=sdk.models.EmbeddingInputType.QUERY,
            model_extras={
                "key1": 1,
                "key2": True,
                "key3": "Some value",
                "key4": [1, 2, 3],
                "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
            },
            model="some-model-id",
        )

        for _ in range(2):
            try:
                response = client.embed(
                    input=["first phrase", "second phrase", "third phrase"], raw_request_hook=self.request_callback
                )
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_embeddings_json_request_payload()
                continue
            assert False

    # Regression test. Send a request that includes all supported types of input objects, with embeddings settings
    # specified in the constructor and all of them overwritten in the 'embed' call.
    # Make sure the resulting JSON payload that goes up to the service is the correct one after hand-inspection.
    def test_embeddings_request_payload_with_defaults_and_overrides(self, **kwargs):
        client = sdk.EmbeddingsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
            dimensions=1024,
            encoding_format=sdk.models.EmbeddingEncodingFormat.UINT8,
            input_type=sdk.models.EmbeddingInputType.DOCUMENT,
            model_extras={
                "hey1": 2,
                "key2": False,
                "key3": "Some other value",
                "key9": "Yet another value",
            },
            model="some-other-model-id",
        )
        for _ in range(2):
            try:
                response = client.embed(
                    input=["first phrase", "second phrase", "third phrase"],
                    dimensions=2048,
                    encoding_format=sdk.models.EmbeddingEncodingFormat.UBINARY,
                    input_type=sdk.models.EmbeddingInputType.QUERY,
                    model_extras={
                        "key1": 1,
                        "key2": True,
                        "key3": "Some value",
                        "key4": [1, 2, 3],
                        "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
                    },
                    model="some-model-id",
                    raw_request_hook=self.request_callback,
                )
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_embeddings_json_request_payload()
                continue
            assert False

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - TEXT EMBEDDINGS
    #
    # **********************************************************************************

    @ServicePreparerEmbeddings()
    @recorded_by_proxy
    def test_load_embeddings_client(self, **kwargs):

        client = self._load_embeddings_client(**kwargs)
        assert isinstance(client, sdk.EmbeddingsClient)
        assert client._model_info
        response1 = client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(
            response1, "embedding"
        )  # TODO: This should be ModelType.EMBEDDINGS once the model is fixed
        client.close()

    @ServicePreparerEmbeddings()
    @recorded_by_proxy
    def test_get_model_info_on_embeddings_client(self, **kwargs):

        client = self._create_embeddings_client(**kwargs)
        assert not client._model_info  # pylint: disable=protected-access

        response1 = client.get_model_info()
        assert client._model_info  # pylint: disable=protected-access

        self._print_model_info_result(response1)
        self._validate_model_info_result(
            response1, "embedding"
        )  # TODO: This should be ModelType.EMBEDDINGS once the model is fixed

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2
        client.close()

    @ServicePreparerEmbeddings()
    @recorded_by_proxy
    def test_embeddings(self, **kwargs):
        client = self._create_embeddings_client(**kwargs)
        input = ["first phrase", "second phrase", "third phrase"]

        # Request embeddings with default service format (list of floats)
        response1 = client.embed(input=input)
        self._print_embeddings_result(response1)
        self._validate_embeddings_result(response1)
        assert json.dumps(response1.as_dict(), indent=2) == response1.__str__()

        # Request embeddings as base64 encoded strings
        response2 = client.embed(input=input, encoding_format=sdk.models.EmbeddingEncodingFormat.BASE64)
        self._print_embeddings_result(response2, sdk.models.EmbeddingEncodingFormat.BASE64)
        self._validate_embeddings_result(response2, sdk.models.EmbeddingEncodingFormat.BASE64)

        client.close()

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
                response = client.complete(
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
                    response_format=sdk.models.ChatCompletionsResponseFormatJSON(),
                    seed=654,
                    stop=["stop1", "stop2"],
                    stream=True,
                    temperature=8.976,
                    tool_choice=sdk.models.ChatCompletionsToolChoicePreset.AUTO,
                    tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
                    top_p=9.876,
                    raw_request_hook=self.request_callback,
                )
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_chat_completions_json_request_payload()
                continue
            assert False

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
            response_format=sdk.models.ChatCompletionsResponseFormatJSON(),
            seed=654,
            stop=["stop1", "stop2"],
            temperature=8.976,
            tool_choice=sdk.models.ChatCompletionsToolChoicePreset.AUTO,
            tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
            top_p=9.876,
        )

        for _ in range(2):
            try:
                response = client.complete(
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
                    stream=True,
                    raw_request_hook=self.request_callback,
                )
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_chat_completions_json_request_payload()
                continue
            assert False

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
            response_format=sdk.models.ChatCompletionsResponseFormatText(),
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
                response = client.complete(
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
                    response_format=sdk.models.ChatCompletionsResponseFormatJSON(),
                    seed=654,
                    stop=["stop1", "stop2"],
                    stream=True,
                    temperature=8.976,
                    tool_choice=sdk.models.ChatCompletionsToolChoicePreset.AUTO,
                    tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
                    top_p=9.876,
                    raw_request_hook=self.request_callback,
                )
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_chat_completions_json_request_payload()
                continue
            assert False

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
            response1, "completion"
        )  # TODO: This should be ModelType.CHAT once the model is fixed
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
            response1, "completion"
        )  # TODO: This should be ModelType.CHAT once the model is fixed

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_multi_turn(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant answering questions regarding length units."),
            sdk.models.UserMessage(content="How many feet are in a mile?"),
        ]
        response = client.complete(messages=messages)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        assert json.dumps(response.as_dict(), indent=2) == response.__str__()
        messages.append(sdk.models.AssistantMessage(content=response.choices[0].message.content))
        messages.append(sdk.models.UserMessage(content="and how many yards?"))
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
        response = client.complete(self.read_text_file("chat.test.json"))
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_streaming(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        response = client.complete(
            stream=True,
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="Give me 3 good reasons why I should exercise every day."),
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
        self._validate_chat_completions_result(response, ["juggling", "balls", "blue", "red", "green", "yellow"], True)
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
        self._validate_chat_completions_result(response, ["juggling", "balls", "blue", "red", "green", "yellow"], True)
        client.close()

    # We use AOAI endpoint here because at the moment MaaS does not support Entra ID auth.
    @ServicePreparerAOAIChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_entra_id_auth(self, **kwargs):
        client = self._create_aoai_chat_client(key_auth=False, **kwargs)
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant answering questions regarding length units."),
            sdk.models.UserMessage(content="How many feet are in a mile?"),
        ]
        response = client.complete(messages=messages)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["5280", "5,280"], True)
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
            response = client.complete(messages=[sdk.models.UserMessage(content="How many feet are in a mile?")])
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
