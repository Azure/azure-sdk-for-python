# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import azure.ai.inference as sdk

from model_inference_test_base import ModelClientTestBase, ServicePreparerChatCompletions, ServicePreparerEmbeddings
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import AzureError

# The test class name needs to start with "Test" to get collected by pytest
class TestModelAsyncClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                            HAPPY PATH TESTS
    #
    # **********************************************************************************

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_async_chat_completions_error_free(self, **kwargs):
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant answering questions regarding length units."),
            sdk.models.UserMessage(content="How many feet are in a mile?")
        ]

        client = self._create_chat_client(sync=False, **kwargs)
        result = await client.create(messages=messages)
        self._print_chat_completions_result(result)
        self._validate_chat_completions_result(result, ["5280", "5,280"])

        messages.append(sdk.models.AssistantMessage(content=result.choices[0].message.content))
        messages.append(sdk.models.UserMessage(content="and how many yards?"))
        result = await client.create(messages=messages)
        self._print_chat_completions_result(result)
        self._validate_chat_completions_result(result, ["1760", "1,760"])
        await client.close()

    @ServicePreparerEmbeddings()
    @recorded_by_proxy_async
    async def test_async_embeddings_error_free(self, **kwargs):
        client = self._create_embeddings_client(sync=False, **kwargs)
        result = await client.create(input=["first phrase", "second phrase", "third phrase"])
        self._print_embeddings_result(result)
        self._validate_embeddings_result(result)
        await client.close()

    # **********************************************************************************
    #
    #                            ERROR TESTS
    #
    # **********************************************************************************

    @ServicePreparerEmbeddings()
    @recorded_by_proxy_async
    async def test_embeddings_with_auth_failure(self, **kwargs):
        client = self._create_embeddings_client(sync=False, bad_key=True, **kwargs)
        exception_caught = False
        try:
            result = await client.create(input=["first phrase", "second phrase", "third phrase"])
        except AzureError as e:
            exception_caught = True
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 401
            assert "unauthorized" in e.message.lower()
        await client.close()
        assert exception_caught
