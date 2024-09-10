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

#
# Define these environment variables. They should point to a Mistral Large model
# hosted on MaaS, or any other MaaS model that suppots chat completions with tools.
# AZURE_AI_CHAT_ENDPOINT=https://<endpoint-name>.<azure-region>.models.ai.azure.com
# AZURE_AI_CHAT_KEY=<32-char-api-key>
#
ServicePreparerChatCompletions = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_chat",
    azure_ai_chat_endpoint="https://your-deployment-name.eastus2.inference.ai.azure.com",
    azure_ai_chat_key="00000000000000000000000000000000",
)

#
# Define these environment variables. They should point to any GPT model that
# accepts image input in chat completions (e.g. GPT-4o model).
# hosted on Azure OpenAI (AOAI) endpoint.
# TODO: When we have a MaaS model that supports chat completions with image input,
# use that instead.
# AZURE_OPENAI_CHAT_ENDPOINT=https://<endpont-name>.openai.azure.com/openai/deployments/gpt-4o
# AZURE_OPENAI_CHAT_KEY=<32-char-api-key>
#
ServicePreparerAOAIChatCompletions = functools.partial(
    EnvironmentVariableLoader,
    "azure_openai_chat",
    azure_openai_chat_endpoint="https://your-deployment-name.openai.azure.com/openai/deployments/gpt-4o",
    azure_openai_chat_key="00000000000000000000000000000000",
)

#
# Define these environment variables. They should point to a Cohere model
# hosted on MaaS, or any other MaaS model that text embeddings.
# AZURE_AI_EMBEDDINGS_ENDPOINT=https://<endpoint-name>.<azure-region>.models.ai.azure.com
# AZURE_AI_EMBEDDINGS_KEY=<32-char-api-key>
#
ServicePreparerEmbeddings = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_embeddings",
    azure_ai_embeddings_endpoint="https://your-deployment-name.eastus2.inference.ai.azure.com",
    azure_ai_embeddings_key="00000000000000000000000000000000",
)


# The test class name needs to start with "Test" to get collected by pytest
class ModelClientTestBase(AzureRecordedTestCase):

    # Set to True to print out all results to the console
    PRINT_RESULT = True

    # Regular expression describing the pattern of a result ID returned from MaaS/MaaP endpoint. Format allowed are:
    # "183b56eb-8512-484d-be50-5d8df82301a2", "26ef25aa45424781865a2d38a4484274" and "Sanitized" (when running tests
    # from recordings)
    REGEX_RESULT_ID = re.compile(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$|^[0-9a-fA-F]{32}$|^Sanitized$"
    )

    # Regular expression describing the pattern of a result ID returned from AOAI endpoint.
    # For example: "chatcmpl-9jscXwejvOMnGrxRfACmNrCCdiwWb" or "Sanitized" (when runing tests from recordings) # cspell:disable-line
    REGEX_AOAI_RESULT_ID = re.compile(r"^chatcmpl-[0-9a-zA-Z]{29}$|^Sanitized$")  # cspell:disable-line

    # Regular expression describing the pattern of a base64 string
    REGEX_BASE64_STRING = re.compile(r"^[A-Za-z0-9+/]+={0,3}$")

    # A couple of tool definitions to use in the tests
    TOOL1 = sdk.models.ChatCompletionsToolDefinition(
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

    TOOL2 = sdk.models.ChatCompletionsToolDefinition(
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

    # Expected JSON request payload in regression tests. These are common to
    # sync and async tests, therefore they are defined here.
    CHAT_COMPLETIONS_JSON_REQUEST_PAYLOAD = '{"messages": [{"role": "system", "content": "system prompt"}, {"role": "user", "content": "user prompt 1"}, {"role": "assistant", "tool_calls": [{"function": {"name": "my-first-function-name", "arguments": {"first_argument": "value1", "second_argument": "value2"}}, "id": "some-id", "type": "function"}, {"function": {"name": "my-second-function-name", "arguments": {"first_argument": "value1"}}, "id": "some-other-id", "type": "function"}]}, {"role": "tool", "tool_call_id": "some id", "content": "function response"}, {"role": "assistant", "content": "assistant prompt"}, {"role": "user", "content": [{"type": "text", "text": "user prompt 2"}, {"type": "image_url", "image_url": {"url": "https://does.not.exit/image.png", "detail": "high"}}]}], "stream": true, "frequency_penalty": 0.123, "max_tokens": 321, "model": "some-model-id", "presence_penalty": 4.567, "response_format": {"type": "json_object"}, "seed": 654, "stop": ["stop1", "stop2"], "temperature": 8.976, "tool_choice": "auto", "tools": [{"function": {"name": "my-first-function-name", "description": "My first function description", "parameters": {"type": "object", "properties": {"first_argument": {"type": "string", "description": "First argument description"}, "second_argument": {"type": "string", "description": "Second argument description"}}, "required": ["first_argument", "second_argument"]}}, "type": "function"}, {"function": {"name": "my-second-function-name", "description": "My second function description", "parameters": {"type": "object", "properties": {"first_argument": {"type": "int", "description": "First argument description"}}, "required": ["first_argument"]}}, "type": "function"}], "top_p": 9.876, "key1": 1, "key2": true, "key3": "Some value", "key4": [1, 2, 3], "key5": {"key6": 2, "key7": false, "key8": "Some other value", "key9": [4, 5, 6, 7]}}'

    EMBEDDINGDS_JSON_REQUEST_PAYLOAD = '{"input": ["first phrase", "second phrase", "third phrase"], "dimensions": 2048, "encoding_format": "ubinary", "input_type": "query", "model": "some-model-id", "key1": 1, "key2": true, "key3": "Some value", "key4": [1, 2, 3], "key5": {"key6": 2, "key7": false, "key8": "Some other value", "key9": [4, 5, 6, 7]}}'

    # Methods to load credentials from environment variables
    def _load_chat_credentials(self, *, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("azure_ai_chat_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("azure_ai_chat_key")
        credential = AzureKeyCredential(key)
        return endpoint, credential

    # See the "Data plane - inference" row in the table here for latest AOAI api-version:
    # https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
    def _load_aoai_chat_credentials(self, *, key_auth: bool, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("azure_openai_chat_endpoint")
        if key_auth:
            key = "00000000000000000000000000000000" if bad_key else kwargs.pop("azure_openai_chat_key")
            headers = {"api-key": key}
            credential = AzureKeyCredential("")
            credential_scopes: list[str] = []
        else:
            credential = self.get_credential(sdk.ChatCompletionsClient, is_async=False)
            credential_scopes: list[str] = ["https://cognitiveservices.azure.com/.default"]
            headers = {}
        api_version = "2024-06-01"
        return endpoint, credential, credential_scopes, headers, api_version

    def _load_embeddings_credentials(self, *, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("azure_ai_embeddings_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("azure_ai_embeddings_key")
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

    def _create_chat_client(self, *, bad_key: bool = False, **kwargs) -> sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials(bad_key=bad_key, **kwargs)
        return sdk.ChatCompletionsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    # Methos to create the different sync and async clients directly
    def _create_async_chat_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials(bad_key=bad_key, **kwargs)
        return async_sdk.ChatCompletionsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    def _create_aoai_chat_client(
        self, *, key_auth: bool = True, bad_key: bool = False, **kwargs
    ) -> sdk.ChatCompletionsClient:
        endpoint, credential, credential_scopes, headers, api_version = self._load_aoai_chat_credentials(
            key_auth=key_auth, bad_key=bad_key, **kwargs
        )
        return sdk.ChatCompletionsClient(
            endpoint=endpoint,
            credential=credential,
            credential_scopes=credential_scopes,
            headers=headers,
            api_version=api_version,
            logging_enable=LOGGING_ENABLED,
        )

    def _create_async_aoai_chat_client(
        self, *, key_auth: bool = True, bad_key: bool = False, **kwargs
    ) -> async_sdk.ChatCompletionsClient:
        endpoint, credential, credential_scopes, headers, api_version = self._load_aoai_chat_credentials(
            key_auth=True, bad_key=bad_key, **kwargs
        )
        return async_sdk.ChatCompletionsClient(
            endpoint=endpoint,
            credential=credential,
            credential_scopes=credential_scopes,
            headers=headers,
            api_version=api_version,
            logging_enable=LOGGING_ENABLED,
        )

    def _create_async_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials(bad_key=bad_key, **kwargs)
        return async_sdk.EmbeddingsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    def _create_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials(bad_key=bad_key, **kwargs)
        return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs)

    def _create_embeddings_client_with_chat_completions_credentials(self, **kwargs) -> sdk.EmbeddingsClient:
        endpoint = kwargs.pop("azure_ai_chat_endpoint")
        key = kwargs.pop("azure_ai_chat_key")
        credential = AzureKeyCredential(key)
        return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def request_callback(self, pipeline_request) -> None:
        self.pipeline_request = pipeline_request

    def _validate_embeddings_json_request_payload(self) -> None:
        headers = self.pipeline_request.http_request.headers
        print(f"Actual HTTP request headers: {self.pipeline_request.http_request.headers}")
        print(f"Actual JSON request payload: {self.pipeline_request.http_request.data}")
        assert headers["Content-Type"] == "application/json"
        assert headers["Content-Length"] == "311"
        assert headers["extra-parameters"] == "pass-through"
        assert headers["Accept"] == "application/json"
        assert headers["some_header"] == "some_header_value"
        assert "MyAppId azsdk-python-ai-inference/" in headers["User-Agent"]
        assert " Python/" in headers["User-Agent"]
        assert headers["Authorization"] == "Bearer key-value"
        assert self.pipeline_request.http_request.data == self.EMBEDDINGDS_JSON_REQUEST_PAYLOAD

    def _validate_chat_completions_json_request_payload(self) -> None:
        print(f"Actual HTTP request headers: {self.pipeline_request.http_request.headers}")
        print(f"Actual JSON request payload: {self.pipeline_request.http_request.data}")
        headers = self.pipeline_request.http_request.headers
        assert headers["Content-Type"] == "application/json"
        assert headers["Content-Length"] == "1840"
        assert headers["extra-parameters"] == "pass-through"
        assert headers["Accept"] == "application/json"
        assert headers["some_header"] == "some_header_value"
        assert "MyAppId azsdk-python-ai-inference/" in headers["User-Agent"]
        assert " Python/" in headers["User-Agent"]
        assert headers["Authorization"] == "Bearer key-value"
        assert self.pipeline_request.http_request.data == self.CHAT_COMPLETIONS_JSON_REQUEST_PAYLOAD

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
        assert headers["extra-parameters"] == "pass-through"
        assert body is not None
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            print("Invalid JSON format")
        assert body_json["n"] == 1

    @staticmethod
    def _validate_chat_completions_result(
        response: sdk.models.ChatCompletions, contains: List[str], is_aoai: Optional[bool] = False
    ):
        assert any(item in response.choices[0].message.content for item in contains)
        assert response.choices[0].message.role == sdk.models.ChatRole.ASSISTANT
        assert response.choices[0].finish_reason == sdk.models.CompletionsFinishReason.STOPPED
        assert response.choices[0].index == 0
        if is_aoai:
            assert bool(ModelClientTestBase.REGEX_AOAI_RESULT_ID.match(response.id))
        else:
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
    def _validate_embeddings_result(
        response: sdk.models.EmbeddingsResult,
        encoding_format: sdk.models.EmbeddingEncodingFormat = sdk.models.EmbeddingEncodingFormat.FLOAT,
    ):
        assert response is not None
        assert response.data is not None
        assert len(response.data) == 3
        for i in [0, 1, 2]:
            assert response.data[i] is not None
            assert response.data[i].index == i
            if encoding_format == sdk.models.EmbeddingEncodingFormat.FLOAT:
                assert isinstance(response.data[i].embedding, List)
                assert len(response.data[i].embedding) > 0
                assert response.data[i].embedding[0] != 0.0
                assert response.data[i].embedding[-1] != 0.0
            elif encoding_format == sdk.models.EmbeddingEncodingFormat.BASE64:
                assert isinstance(response.data[i].embedding, str)
                assert len(response.data[i].embedding) > 0
                assert bool(ModelClientTestBase.REGEX_BASE64_STRING.match(response.data[i].embedding))  # type: ignore[arg-type]
            else:
                raise ValueError(f"Unsupported encoding format: {encoding_format}")
        assert bool(ModelClientTestBase.REGEX_RESULT_ID.match(response.id))
        # assert len(response.model) > 0  # At the time of writing this test, this JSON field existed but was empty
        assert response.usage.prompt_tokens > 0
        assert response.usage.total_tokens == response.usage.prompt_tokens

    @staticmethod
    def _print_embeddings_result(
        response: sdk.models.EmbeddingsResult,
        encoding_format: sdk.models.EmbeddingEncodingFormat = sdk.models.EmbeddingEncodingFormat.FLOAT,
    ):
        if ModelClientTestBase.PRINT_RESULT:
            print("Embeddings response:")
            for item in response.data:
                if encoding_format == sdk.models.EmbeddingEncodingFormat.FLOAT:
                    length = len(item.embedding)
                    print(
                        f"data[{item.index}] (vector length={length}): "
                        f"[{item.embedding[0]}, {item.embedding[1]}, "
                        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                    )
                elif encoding_format == sdk.models.EmbeddingEncodingFormat.BASE64:
                    print(
                        f"data[{item.index}] encoded (string length={len(item.embedding)}): "
                        f'"{item.embedding[:32]}...{item.embedding[-32:]}"'
                    )
                else:
                    raise ValueError(f"Unsupported encoding format: {encoding_format}")
            print(f"\tid: {response.id}")
            print(f"\tmodel: {response.model}")
            print(f"\tusage.prompt_tokens: {response.usage.prompt_tokens}")
            print(f"\tusage.total_tokens: {response.usage.total_tokens}")
