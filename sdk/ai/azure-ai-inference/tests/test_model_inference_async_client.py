# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import azure.ai.inference as sdk
import azure.ai.inference.aio as async_sdk

from model_inference_test_base import ModelClientTestBase, ServicePreparerChatCompletions, ServicePreparerEmbeddings
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential


# The test class name needs to start with "Test" to get collected by pytest
class TestModelAsyncClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                      HAPPY PATH TESTS - TEXT EMBEDDINGS
    #
    # **********************************************************************************
    """live test with recording fails for this... why?
    @ServicePreparerEmbeddings()
    @recorded_by_proxy_async
    async def test_async_load_embeddings_client(self, **kwargs):

        client = await self._load_async_embeddings_client(**kwargs)
        assert isinstance(client, async_sdk.EmbeddingsClient)
        assert client._model_info

        response1 = await client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(response1, "embedding") # TODO: This should be ModelType.EMBEDDINGS once the model is fixed
        await client.close()
    """

    @ServicePreparerEmbeddings()
    @recorded_by_proxy_async
    async def test_async_get_model_info_on_embeddings_client(self, **kwargs):
        client = self._create_async_embeddings_client(**kwargs)
        assert not client._model_info

        response1 = await client.get_model_info()
        assert client._model_info
        self._print_model_info_result(response1)
        self._validate_model_info_result(
            response1, "embedding"
        )  # TODO: This should be ModelType.EMBEDDINGS once the model is fixed

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = await client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2

        await client.close()

    @ServicePreparerEmbeddings()
    @recorded_by_proxy_async
    async def test_async_embeddings(self, **kwargs):
        client = self._create_async_embeddings_client(**kwargs)
        response = await client.embed(input=["first phrase", "second phrase", "third phrase"])
        self._print_embeddings_result(response)
        self._validate_embeddings_result(response)
        await client.close()

    # **********************************************************************************
    #
    #                      HAPPY PATH TESTS - CHAT COMPLETIONS
    #
    # **********************************************************************************

    # Regression test. Send a request that includes almost all supported types of input objects. Make sure the resulting
    # JSON payload that goes up to the service (including headers) is the correct one after hand-inspection.
    async def test_async_chat_completions_request_payload(self, **kwargs):

        client = async_sdk.ChatCompletionsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
        )

        try:
            response = await client.complete(
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
                tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
                top_p=9.876,
                raw_request_hook=self.request_callback,
            )
        except ServiceRequestError as _:
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

    # Regression test. Send a request that includes almost all supported types of input objects, with input arguments
    # specified via the `with_defaults` method. Make sure the resulting JSON payload that goes up to the service
    # is the correct one after hand-inspection.
    async def test_async_chat_completions_with_defaults_request_payload(self, **kwargs):

        client = async_sdk.ChatCompletionsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
        ).with_defaults(
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
            temperature=8.976,
            tool_choice=sdk.models.ChatCompletionsToolSelectionPreset.AUTO,
            tools=[ModelClientTestBase.TOOL1],
            top_p=9.876,
        )

        try:
            response = await client.complete(
                messages=[
                    sdk.models.SystemMessage(content="system prompt"),
                    sdk.models.UserMessage(content="user prompt 1"),
                ],
                model_extras={
                    "key10": 1,
                    "key11": True,
                    "key12": "Some other value",
                },
                frequency_penalty=0.321,
                max_tokens=123,
                model="some-other-model-id",
                presence_penalty=7.654,
                response_format=sdk.models.ChatCompletionsResponseFormat.TEXT,
                seed=456,
                stop=["stop3"],
                stream=False,
                temperature=6.789,
                tool_choice=sdk.models.ChatCompletionsToolSelectionPreset.NONE,
                tools=[ModelClientTestBase.TOOL2],
                top_p=9.876,
                raw_request_hook=self.request_callback,
            )
        except ServiceRequestError as _:
            print(f"Actual JSON request payload: {self.pipeline_request.http_request.data}")
            assert (
                self.pipeline_request.http_request.data
                == '{\"frequency_penalty\": 0.321, \"max_tokens\": 123, \"messages\": [{\"role\": \"system\", \"content\": \"system prompt\"}, {\"role\": \"user\", \"content\": \"user prompt 1\"}], \"model\": \"some-other-model-id\", \"presence_penalty\": 7.654, \"response_format\": \"text\", \"seed\": 456, \"stop\": [\"stop3\"], \"stream\": false, \"temperature\": 6.789, \"tool_choice\": \"none\", \"tools\": [{\"type\": \"function\", \"function\": {\"name\": \"my-second-function-name\", \"description\": \"My second function description\", \"parameters\": {\"type\": \"object\", \"properties\": {\"first_argument\": {\"type\": \"int\", \"description\": \"First argument description\"}}, \"required\": [\"first_argument\"]}}}], \"top_p\": 9.876, \"key10\": 1, \"key11\": true, \"key12\": \"Some other value\"}'
            )
            return
        assert False

    # Regression test. Send a request that includes almost all supported types of input objects, with input arguments
    # specified via the `with_defaults` method, and all of them overwritten in the 'complete' call.
    # Make sure the resulting JSON payload that goes up to the service is the correct one after hand-inspection.
    async def test_async_chat_completions_with_defaults_and_overrides_request_payload(self, **kwargs):

        client = async_sdk.ChatCompletionsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
        ).with_defaults(
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
            temperature=8.976,
            tool_choice=sdk.models.ChatCompletionsToolSelectionPreset.AUTO,
            tools=[ModelClientTestBase.TOOL1, ModelClientTestBase.TOOL2],
            top_p=9.876,
        )

        try:
            response = await client.complete(
                messages=[
                    sdk.models.SystemMessage(content="system prompt"),
                    sdk.models.UserMessage(content="user prompt 1"),
                ],
                stream=True,
                raw_request_hook=self.request_callback,
            )
        except ServiceRequestError as _:
            print(f"Actual JSON request payload: {self.pipeline_request.http_request.data}")
            assert (
                self.pipeline_request.http_request.data
                == '{\"frequency_penalty\": 0.123, \"max_tokens\": 321, \"messages\": [{\"role\": \"system\", \"content\": \"system prompt\"}, {\"role\": \"user\", \"content\": \"user prompt 1\"}], \"model\": \"some-model-id\", \"presence_penalty\": 4.567, \"response_format\": \"json_object\", \"seed\": 654, \"stop\": [\"stop1\", \"stop2\"], \"stream\": true, \"temperature\": 8.976, \"tool_choice\": \"auto\", \"tools\": [{\"type\": \"function\", \"function\": {\"name\": \"my-first-function-name\", \"description\": \"My first function description\", \"parameters\": {\"type\": \"object\", \"properties\": {\"first_argument\": {\"type\": \"string\", \"description\": \"First argument description\"}, \"second_argument\": {\"type\": \"string\", \"description\": \"Second argument description\"}}, \"required\": [\"first_argument\", \"second_argument\"]}}}, {\"type\": \"function\", \"function\": {\"name\": \"my-second-function-name\", \"description\": \"My second function description\", \"parameters\": {\"type\": \"object\", \"properties\": {\"first_argument\": {\"type\": \"int\", \"description\": \"First argument description\"}}, \"required\": [\"first_argument\"]}}}], \"top_p\": 9.876, \"key1\": 1, \"key2\": true, \"key3\": \"Some value\", \"key4\": [1, 2, 3], \"key5\": {\"key6\": 2, \"key7\": false, \"key8\": \"Some other value\", \"key9\": [4, 5, 6, 7]}}'
            )
            return
        assert False

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_load_chat_completions_client(self, **kwargs):

        client = await self._load_async_chat_client(**kwargs)
        assert isinstance(client, async_sdk.ChatCompletionsClient)
        assert client._model_info

        response1 = await client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(
            response1, "completion"
        )  # TODO: This should be ModelType.CHAT once the model is fixed
        await client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_get_model_info_on_chat_client(self, **kwargs):
        client = self._create_async_chat_client(**kwargs)
        assert not client._model_info

        response1 = await client.get_model_info()
        assert client._model_info
        self._print_model_info_result(response1)
        self._validate_model_info_result(
            response1, "completion"
        )  # TODO: This should be ModelType.CHAT once the model is fixed

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = await client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2

        await client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_chat_completions_multi_turn(self, **kwargs):
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant answering questions regarding length units."),
            sdk.models.UserMessage(content="How many feet are in a mile?"),
        ]
        client = self._create_async_chat_client(**kwargs)
        response = await client.complete(messages=messages)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        messages.append(sdk.models.AssistantMessage(content=response.choices[0].message.content))
        messages.append(sdk.models.UserMessage(content="and how many yards?"))
        response = await client.complete(messages=messages)
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["1760", "1,760"])
        await client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_chat_completions_with_model_extras(self, **kwargs):
        client = self._create_async_chat_client(**kwargs)
        response = await client.complete(
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
        await client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_chat_completions_streaming(self, **kwargs):
        client = self._create_async_chat_client(Sync=False, **kwargs)
        response = await client.complete(
            stream=True,
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="Give me 3 good reasons why I should exercise every day."),
            ],
        )
        await self._validate_async_chat_completions_streaming_result(response)
        await client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_chat_completions_with_json_input(self, **kwargs):
        client = self._create_async_chat_client(**kwargs)
        request_body = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "How many feet are in a mile?"},
            ]
        }
        response = await client.complete(request_body)
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        await client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_chat_completions_with_bytes_input(self, **kwargs):
        client = self._create_async_chat_client(**kwargs)
        response = await client.complete(self.read_text_file("chat.test.json"))
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        await client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_chat_completions_streaming_with_json_input(self, **kwargs):
        client = self._create_async_chat_client(**kwargs)
        request_body = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Give me 3 good reasons why I should exercise every day."},
            ],
            "stream": True,
        }
        response = await client.complete(request_body)
        await self._validate_async_chat_completions_streaming_result(response)
        await client.close()

    # **********************************************************************************
    #
    #                            ERROR TESTS
    #
    # **********************************************************************************

    @ServicePreparerEmbeddings()
    @recorded_by_proxy_async
    async def test_embeddings_with_auth_failure(self, **kwargs):
        client = self._create_async_embeddings_client(bad_key=True, **kwargs)
        exception_caught = False
        try:
            response = await client.embed(input=["first phrase", "second phrase", "third phrase"])
        except AzureError as e:
            exception_caught = True
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 401
            assert "unauthorized" in e.message.lower()
        await client.close()
        assert exception_caught
