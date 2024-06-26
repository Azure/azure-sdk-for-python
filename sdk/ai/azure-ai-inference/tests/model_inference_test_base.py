# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import azure.ai.inference as sdk
import azure.ai.inference.aio as async_sdk
import functools
import io
import json
import logging
import re
import sys

from os import path
from pathlib import Path
from typing import List, Optional, Union, Dict
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

    # Regular expression describing the pattern of a result ID. Format allowed are:
    # "183b56eb-8512-484d-be50-5d8df82301a2", "26ef25aa45424781865a2d38a4484274" and "Sanitized"
    REGEX_RESULT_ID = re.compile(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$|^[0-9a-fA-F]{32}$|^Sanitized$"
    )

    # Methods to load credentials from environment variables
    def _load_chat_credentials(self, *, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("chat_completions_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("chat_completions_key")
        credential = AzureKeyCredential(key)
        return endpoint, credential

    def _load_embeddings_credentials(self, *, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("embeddings_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("embeddings_key")
        credential = AzureKeyCredential(key)
        return endpoint, credential

    # Methods to create sync and async clients using Load_client() function
    async def _load_async_chat_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials(bad_key=bad_key, **kwargs)
        return await async_sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _load_chat_client(self, *, bad_key: bool = False, **kwargs) -> sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials(bad_key=bad_key, **kwargs)
        return sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    async def _load_async_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials(bad_key=bad_key, **kwargs)
        return await async_sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _load_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials(bad_key=bad_key, **kwargs)
        return sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    # Methos to create the different sync and async clients directly
    def _create_async_chat_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials(bad_key=bad_key, **kwargs)
        return async_sdk.ChatCompletionsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _create_chat_client(self, *, bad_key: bool = False, **kwargs) -> sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials(bad_key=bad_key, **kwargs)
        return sdk.ChatCompletionsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _create_async_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials(bad_key=bad_key, **kwargs)
        return async_sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _create_embeddings_client(self, *, sync: bool = True, bad_key: bool = False, **kwargs) -> sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials(bad_key=bad_key, **kwargs)
        return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _create_embeddings_client_with_chat_completions_credentials(self, **kwargs) -> sdk.EmbeddingsClient:
        endpoint = kwargs.pop("chat_completions_endpoint")
        key = kwargs.pop("chat_completions_key")
        credential = AzureKeyCredential(key)
        return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def request_callback(self, pipeline_request) -> None:
        self.pipeline_request = pipeline_request

    @staticmethod
    def read_text_file(file_name: str) -> io.BytesIO:
        """
        Reads a text file and returns a BytesIO object with the file content in UTF-8 encoding.
        The file is expected to be in the same directory as this Python script.
        """
        with Path(__file__).with_name(file_name).open("r") as f:
            return io.BytesIO(f.read().encode("utf-8"))

    @staticmethod
    def _print_model_info_result(model_info: sdk.models.ModelInfo):
        if ModelClientTestBase.PRINT_RESULT:
            print(" Model info:")
            print("\tmodel_name: {}".format(model_info.model_name))
            print("\tmodel_type: {}".format(model_info.model_type))
            print("\tmodel_provider_name: {}".format(model_info.model_provider_name))

    @staticmethod
    def _validate_model_info_result(
        model_info: sdk.models.ModelInfo, expected_model_type: Union[str, sdk.models.ModelType]
    ):
        assert model_info.model_name is not None
        assert len(model_info.model_name) > 0
        assert model_info.model_provider_name is not None
        assert len(model_info.model_provider_name) > 0
        assert model_info.model_type is not None
        assert model_info.model_type == expected_model_type

    @staticmethod
    def _validate_model_extras(body: str, headers: Dict[str, str]):
        assert headers is not None
        assert headers["unknown-parameters"] == "pass_through"
        assert body is not None
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            print("Invalid JSON format")
        assert body_json["key1"] == 1
        assert body_json["key2"] == True
        assert body_json["key3"] == "Some value"
        assert body_json["key4"][0] == 1
        assert body_json["key4"][1] == 2
        assert body_json["key4"][2] == 3
        assert body_json["key5"]["key6"] == 2
        assert body_json["key5"]["key7"] == False
        assert body_json["key5"]["key8"] == "Some other value"
        assert body_json["key5"]["key9"][0] == 4
        assert body_json["key5"]["key9"][1] == 5
        assert body_json["key5"]["key9"][2] == 6
        assert body_json["key5"]["key9"][3] == 7

    @staticmethod
    def _validate_chat_completions_result(response: sdk.models.ChatCompletions, contains: List[str]):
        assert any(item in response.choices[0].message.content for item in contains)
        assert response.choices[0].message.role == sdk.models.ChatRole.ASSISTANT
        assert response.choices[0].finish_reason == sdk.models.CompletionsFinishReason.STOPPED
        assert response.choices[0].index == 0
        assert bool(ModelClientTestBase.REGEX_RESULT_ID.match(response.id))
        assert response.created is not None
        assert response.created != ""
        assert response.model is not None
        assert response.model != ""
        assert response.usage.prompt_tokens > 0
        assert response.usage.completion_tokens > 0
        assert response.usage.total_tokens == response.usage.prompt_tokens + response.usage.completion_tokens

    @staticmethod
    def _validate_chat_completions_tool_result(response: sdk.models.ChatCompletions):
        assert response.choices[0].message.content == None or response.choices[0].message.content == ""
        assert response.choices[0].message.role == sdk.models.ChatRole.ASSISTANT
        assert response.choices[0].finish_reason == sdk.models.CompletionsFinishReason.TOOL_CALLS
        assert response.choices[0].index == 0
        function_args = json.loads(response.choices[0].message.tool_calls[0].function.arguments.replace("'", '"'))
        print(function_args)
        assert function_args["city"].lower() == "seattle"
        assert function_args["days"] == "2"
        assert bool(ModelClientTestBase.REGEX_RESULT_ID.match(response.id))
        assert response.created is not None
        assert response.created != ""
        assert response.model is not None
        # assert response.model != ""
        assert response.usage.prompt_tokens > 0
        assert response.usage.completion_tokens > 0
        assert response.usage.total_tokens == response.usage.prompt_tokens + response.usage.completion_tokens

    @staticmethod
    def _validate_chat_completions_update(update: sdk.models.StreamingChatCompletionsUpdate, first: bool) -> str:
        if first:
            # Why is 'content','created' and 'object' missing in the first update?
            assert update.choices[0].delta.role == sdk.models.ChatRole.ASSISTANT
        else:
            assert update.choices[0].delta.role == None
            assert update.choices[0].delta.content != None
            assert update.created is not None
            assert update.created != ""
        assert update.choices[0].delta.tool_calls == None
        assert update.choices[0].index == 0
        assert update.id is not None
        assert bool(ModelClientTestBase.REGEX_RESULT_ID.match(update.id))
        assert update.model is not None
        assert update.model != ""
        if update.choices[0].delta.content != None:
            return update.choices[0].delta.content
        else:
            return ""

    @staticmethod
    def _validate_chat_completions_streaming_result(response: sdk.models.StreamingChatCompletions):
        count = 0
        content = ""
        for update in response:
            content += ModelClientTestBase._validate_chat_completions_update(update, count == 0)
            count += 1
        assert count > 2
        assert len(content) > 100  # Some arbitrary number
        # The last update should have a finish reason and usage
        assert update.choices[0].finish_reason == sdk.models.CompletionsFinishReason.STOPPED
        assert update.usage.prompt_tokens > 0
        assert update.usage.completion_tokens > 0
        assert update.usage.total_tokens == update.usage.prompt_tokens + update.usage.completion_tokens
        if ModelClientTestBase.PRINT_RESULT:
            print(content)

    @staticmethod
    async def _validate_async_chat_completions_streaming_result(response: sdk.models.AsyncStreamingChatCompletions):
        count = 0
        content = ""
        async for update in response:
            content += ModelClientTestBase._validate_chat_completions_update(update, count == 0)
            count += 1
        assert count > 2
        assert len(content) > 100  # Some arbitrary number
        # The last update should have a finish reason and usage
        assert update.choices[0].finish_reason == sdk.models.CompletionsFinishReason.STOPPED
        assert update.usage.prompt_tokens > 0
        assert update.usage.completion_tokens > 0
        assert update.usage.total_tokens == update.usage.prompt_tokens + update.usage.completion_tokens
        if ModelClientTestBase.PRINT_RESULT:
            print(content)

    @staticmethod
    def _print_chat_completions_result(response: sdk.models.ChatCompletions):
        if ModelClientTestBase.PRINT_RESULT:
            print(" Chat Completions response:")
            for choice in response.choices:
                print(f"\tchoices[0].message.content: {choice.message.content}")
                print(f"\tchoices[0].message.tool_calls: {choice.message.tool_calls}")
                print("\tchoices[0].message.role: {}".format(choice.message.role))
                print("\tchoices[0].finish_reason: {}".format(choice.finish_reason))
                print("\tchoices[0].index: {}".format(choice.index))
            print("\tid: {}".format(response.id))
            print("\tcreated: {}".format(response.created))
            print("\tmodel: {}".format(response.model))
            print("\tusage.prompt_tokens: {}".format(response.usage.prompt_tokens))
            print("\tusage.completion_tokens: {}".format(response.usage.completion_tokens))
            print("\tusage.total_tokens: {}".format(response.usage.total_tokens))

    @staticmethod
    def _validate_embeddings_result(response: sdk.models.EmbeddingsResult):
        assert response is not None
        assert response.data is not None
        assert len(response.data) == 3
        for i in [0, 1, 2]:
            assert response.data[i] is not None
            assert response.data[i].index == i
            assert len(response.data[i].embedding) == 1024
            assert response.data[i].embedding[0] != 0.0
            assert response.data[i].embedding[1023] != 0.0
        assert bool(ModelClientTestBase.REGEX_RESULT_ID.match(response.id))
        # assert len(response.model) > 0  # At the time of writing this test, this JSON field existed but was empty
        assert response.usage.prompt_tokens > 0
        assert response.usage.total_tokens == response.usage.prompt_tokens

    @staticmethod
    def _print_embeddings_result(response: sdk.models.EmbeddingsResult):
        if ModelClientTestBase.PRINT_RESULT:
            print("Embeddings response:")
            for item in response.data:
                length = len(item.embedding)
                print(
                    f"\tdata[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, ..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                )
            print(f"\tid: {response.id}")
            print(f"\tmodel: {response.model}")
            print(f"\tusage.prompt_tokens: {response.usage.prompt_tokens}")
            print(f"\tusage.total_tokens: {response.usage.total_tokens}")
