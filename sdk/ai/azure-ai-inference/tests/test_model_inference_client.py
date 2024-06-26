# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import os
import azure.ai.inference as sdk

from model_inference_test_base import ModelClientTestBase, ServicePreparerChatCompletions, ServicePreparerEmbeddings
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential


# The test class name needs to start with "Test" to get collected by pytest
class TestModelClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                      HAPPY PATH TESTS - TEXT EMBEDDINGS
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
        assert not client._model_info

        response1 = client.get_model_info()
        assert client._model_info

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
        response = client.embed(input=["first phrase", "second phrase", "third phrase"])
        self._print_embeddings_result(response)
        self._validate_embeddings_result(response)
        client.close()

    def test_image_url_load(self, **kwargs):
        local_folder = os.path.dirname(os.path.abspath(__file__))
        image_file = os.path.join(local_folder, "../samples/sample1.png")
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
    #                      HAPPY PATH TESTS - CHAT COMPLETIONS
    #
    # **********************************************************************************

    # Regression test. Send a request that includes almost all supported types of input objects. Make sure the resulting
    # JSON payload that goes up to the service (including headers) is the correct one after hand-inspection.
    def test_chat_completions_request_payload(self, **kwargs):

        client = sdk.ChatCompletionsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
        )

        tool1 = sdk.models.ChatCompletionsFunctionToolDefinition(
            function=sdk.models.FunctionDefinition(
                name="my-first-function-name",
                description="My first function description",
                parameters={
                    "type": "object",
                    "properties": {
                        "first_argument": {
                            "type": "string",
                            "description": "First argument description",
                        },
                        "second_argument": {
                            "type": "string",
                            "description": "Second argument description",
                        },
                    },
                    "required": ["first_argument", "second_argument"],
                },
            )
        )

        tool2 = sdk.models.ChatCompletionsFunctionToolDefinition(
            function=sdk.models.FunctionDefinition(
                name="my-second-function-name",
                description="My second function description",
                parameters={
                    "type": "object",
                    "properties": {
                        "first_argument": {
                            "type": "int",
                            "description": "First argument description",
                        },
                    },
                    "required": ["first_argument"],
                },
            )
        )

        try:
            response = client.complete(
                messages=[
                    sdk.models.SystemMessage(content="system prompt"),
                    sdk.models.UserMessage(content="user prompt 1"),
                    sdk.models.AssistantMessage(
                        tool_calls=[
                            sdk.models.ChatCompletionsFunctionToolCall(function=sdk.models.FunctionCall(name="my-first-function-name", arguments={"first_argument": "value1", "second_argument": "value2"})),
                            sdk.models.ChatCompletionsFunctionToolCall(function=sdk.models.FunctionCall(name="my-second-function-name", arguments={"first_argument": "value1"})),
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
                response_format=sdk.models.ChatCompletionsResponseFormat.JSON_OBJECT,
                seed=654,
                stop=["stop1", "stop2"],
                stream=True,
                temperature=8.976,
                tool_choice=sdk.models.ChatCompletionsToolSelectionPreset.AUTO,
                tools=[tool1, tool2],
                top_p=9.876,
                raw_request_hook=self.request_callback,
            )
        except ServiceRequestError as e:
            headers = self.pipeline_request.http_request.headers
            print(f"Actual HTTP request headers: {self.pipeline_request.http_request.headers}")
            print(f"Actual JSON request payload: {self.pipeline_request.http_request.data}")
            assert headers["Content-Type"] == "application/json"
            assert headers["Content-Length"] == "1790"
            assert headers["unknown-parameters"] == "pass_through"
            assert headers["Accept"] == "application/json"
            assert headers["some_header"] == "some_header_value"
            assert "azsdk-python-ai-inference/" in headers["User-Agent"]
            assert headers["Authorization"] == "Bearer key-value"
            assert (
                self.pipeline_request.http_request.data
                == '{\"frequency_penalty\": 0.123, \"max_tokens\": 321, \"messages\": [{\"role\": \"system\", \"content\": \"system prompt\"}, {\"role\": \"user\", \"content\": \"user prompt 1\"}, {\"role\": \"assistant\", \"tool_calls\": [{\"type\": \"function\", \"function\": {\"name\": \"my-first-function-name\", \"arguments\": {\"first_argument\": \"value1\", \"second_argument\": \"value2\"}}}, {\"type\": \"function\", \"function\": {\"name\": \"my-second-function-name\", \"arguments\": {\"first_argument\": \"value1\"}}}]}, {\"role\": \"tool\", \"tool_call_id\": \"some id\", \"content\": \"function response\"}, {\"role\": \"assistant\", \"content\": \"assistant prompt\"}, {\"role\": \"user\", \"content\": [{\"type\": \"text\", \"text\": \"user prompt 2\"}, {\"type\": \"image_url\", \"image_url\": {\"url\": \"https://does.not.exit/image.png\", \"detail\": \"high\"}}]}], \"model\": \"some-model-id\", \"presence_penalty\": 4.567, \"response_format\": \"json_object\", \"seed\": 654, \"stop\": [\"stop1\", \"stop2\"], \"stream\": true, \"temperature\": 8.976, \"tool_choice\": \"auto\", \"tools\": [{\"type\": \"function\", \"function\": {\"name\": \"my-first-function-name\", \"description\": \"My first function description\", \"parameters\": {\"type\": \"object\", \"properties\": {\"first_argument\": {\"type\": \"string\", \"description\": \"First argument description\"}, \"second_argument\": {\"type\": \"string\", \"description\": \"Second argument description\"}}, \"required\": [\"first_argument\", \"second_argument\"]}}}, {\"type\": \"function\", \"function\": {\"name\": \"my-second-function-name\", \"description\": \"My second function description\", \"parameters\": {\"type\": \"object\", \"properties\": {\"first_argument\": {\"type\": \"int\", \"description\": \"First argument description\"}}, \"required\": [\"first_argument\"]}}}], \"top_p\": 9.876, \"key1\": 1, \"key2\": true, \"key3\": \"Some value\", \"key4\": [1, 2, 3], \"key5\": {\"key6\": 2, \"key7\": false, \"key8\": \"Some other value\", \"key9\": [4, 5, 6, 7]}}'
            )
            return
        assert False

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
        assert client._model_info

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
            model_extras={
                "key1": 1,
                "key2": True,
                "key3": "Some value",
                "key4": [1, 2, 3],
                "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
            },
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
        forecast_tool = sdk.models.ChatCompletionsFunctionToolDefinition(
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

    # **********************************************************************************
    #
    #                            ERROR TESTS
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
            assert "unauthorized" in e.message.lower()
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
