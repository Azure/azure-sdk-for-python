# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import inspect
import azure.ai.inference as sdk

from model_inference_test_base import ModelClientTestBase, ServicePreparerChatCompletions, ServicePreparerEmbeddings
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import AzureError


# The test class name needs to start with "Test" to get collected by pytest
class TestModelClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                            HAPPY PATH TESTS
    #
    # **********************************************************************************

    # Test one chat completion
    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_error_free(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        result = client.create(messages=[sdk.models.UserMessage(content="How many feet are in a mile?")])
        self._print_chat_completions_result(result)
        self._validate_chat_completions_result(result, ["5280", "5,280"])
        client.close()

    # Test one embeddings call
    @ServicePreparerEmbeddings()
    @recorded_by_proxy
    def test_embeddings_error_free(self, **kwargs):
        client = self._create_embeddings_client(**kwargs)
        result = client.create(input=["first phrase", "second phrase", "third phrase"])
        self._print_embeddings_result(result)
        self._validate_embeddings_result(result)
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
        try:
            result = client.create(messages=[sdk.models.UserMessage(content="How many feet are in a mile?")])
        except AzureError as e:
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 401
            assert "unauthorized" in e.message.lower()
        client.close()


    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_embeddings_on_chat_completion_endpoint(self, **kwargs):
        client = self._create_embeddings_client_with_chat_completions_credentials(**kwargs)
        try:
            result = client.create(input=["first phrase", "second phrase", "third phrase"])
        except AzureError as e:
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 404
            assert "not found" in e.message.lower()
        client.close()

