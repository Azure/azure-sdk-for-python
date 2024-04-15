# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging
import sys
import azure.ai.inference as sdk
import azure.ai.inference.aio as async_sdk
import re

from os import path
from typing import List, Optional, Union
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from azure.core.pipeline import PipelineRequest


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

ServicePreparerChatCompletions = functools.partial(
    EnvironmentVariableLoader,
    "chat_completions",
    chat_completions_endpoint="https://your-deployment-name.your-azure-region.inference.ai.azure.com",
    chat_completions_key="00000000000000000000000000000000",
)

ServicePreparerEmbeddings = functools.partial(
    EnvironmentVariableLoader,
    "embeddings",
    embeddings_endpoint="https://your-deployment-name.your-azure-region.inference.ai.azure.com",
    embeddings_key="00000000000000000000000000000000",
)

# The test class name needs to start with "Test" to get collected by pytest
class ModelClientTestBase(AzureRecordedTestCase):

    # Set to True to print out all results to the console
    PRINT_RESULT = True

    # Regular expression describing the pattern of a result ID (e.g. "183b56eb-8512-484d-be50-5d8df82301a2")
    REGEX_RESULT_ID = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')

    def _create_chat_client(self, *, sync: bool = True, bad_key: bool = False, **kwargs):
        endpoint = kwargs.pop("chat_completions_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("chat_completions_key")
        credential = AzureKeyCredential(key)
        if sync:
            return sdk.ChatCompletionsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)
        else:
            return async_sdk.ChatCompletionsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _create_embeddings_client(self, *, sync: bool = True, bad_key: bool = False, **kwargs) -> sdk.EmbeddingsClient | async_sdk.EmbeddingsClient:
        endpoint = kwargs.pop("embeddings_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("embeddings_key")
        credential = AzureKeyCredential(key)
        if sync:
            return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)
        else:
            return async_sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _create_embeddings_client_with_chat_completions_credentials(self, **kwargs) -> sdk.EmbeddingsClient:
        endpoint = kwargs.pop("chat_completions_endpoint")
        key = kwargs.pop("chat_completions_key")
        credential = AzureKeyCredential(key)
        return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    @staticmethod
    def _validate_chat_completions_result(result: sdk.models.ChatCompletions, contains: List[str]):
        assert any(item in result.choices[0].message.content for item in contains)
        assert result.choices[0].message.role == sdk.models.ChatRole.ASSISTANT
        assert result.choices[0].finish_reason == sdk.models.CompletionsFinishReason.STOPPED
        assert result.choices[0].index == 0

        assert result.id is not None
        assert len(result.id) == 36
        assert result.created is not None
        assert result.created != ""
        assert result.model is not None
        assert result.model != ""
        assert result.object == "chat.completion"
        assert result.usage.prompt_tokens > 0
        assert result.usage.completion_tokens > 0
        assert result.usage.total_tokens == result.usage.prompt_tokens + result.usage.completion_tokens


    @staticmethod
    def _print_chat_completions_result(result: sdk.models.ChatCompletions):
        if ModelClientTestBase.PRINT_RESULT:
            print(" Chat Completions result:")
            for choice in result.choices:
                print(f"\tchoices[0].message.content: {choice.message.content}")
                print("\tchoices[0].message.role: {}".format(choice.message.role))
                print("\tchoices[0].finish_reason: {}".format(choice.finish_reason))
                print("\tchoices[0].index: {}".format(choice.index))
            print("\tid: {}".format(result.id))
            print("\tcreated: {}".format(result.created))
            print("\tmodel: {}".format(result.model))
            print("\tobject: {}".format(result.object))
            print("\tusage.prompt_tokens: {}".format(result.usage.prompt_tokens))
            print("\tusage.completion_tokens: {}".format(result.usage.completion_tokens))
            print("\tusage.total_tokens: {}".format(result.usage.total_tokens))


    @staticmethod
    def _validate_embeddings_result(result: sdk.models.EmbeddingsResult):
        assert result is not None
        assert result.data is not None
        assert len(result.data) == 3
        for i in [0, 1, 2]:
            assert result.data[i] is not None
            assert result.data[i].object == "embedding"
            assert result.data[i].index == i
            assert len(result.data[i].embedding) == 1024
            assert result.data[i].embedding[0] != 0.0
            assert result.data[i].embedding[1023] != 0.0
        assert bool(ModelClientTestBase.REGEX_RESULT_ID.match(result.id))
        #assert len(result.model) > 0  # At the time of writing this test, this JSON field existed but was empty
        assert result.object == "list"
        # At the time of writing this test, input_tokens did not exist (I see completion tokens instead)
        #assert result.usage.input_tokens > 0
        #assert result.usage.prompt_tokens > 0
        #assert result.total_tokens == result.usage.input_tokens + result.usage.prompt_tokens


    @staticmethod
    def _print_embeddings_result(result: sdk.models.EmbeddingsResult):
        if ModelClientTestBase.PRINT_RESULT:
            print("Embeddings result:")
            for item in result.data:
                length = len(item.embedding)
                print(
                    f"\tdata[{item.index}]: length={length}, object={item.object}, [{item.embedding[0]}, {item.embedding[1]}, ..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                )
            print(f"\tid: {result.id}")
            print(f"\tmodel: {result.model}")
            print(f"\tobject: {result.object}")
            #print(f"\tusage.input_tokens: {result.usage.input_tokens}") # At the time of writing this test, this JSON field does not exist
            print(f"\tusage.prompt_tokens: {result.usage.prompt_tokens}")
            print(f"\tusage.total_tokens: {result.usage.total_tokens}")
