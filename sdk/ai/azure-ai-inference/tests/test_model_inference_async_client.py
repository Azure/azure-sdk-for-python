# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import azure.ai.inference as sdk
import azure.ai.inference.aio as async_sdk

from model_inference_test_base import ModelClientTestBase, ServicePreparerChatCompletions, ServicePreparerEmbeddings
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import AzureError


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
