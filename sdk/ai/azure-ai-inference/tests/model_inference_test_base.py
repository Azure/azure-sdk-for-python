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
from typing import List, Optional, Union, Dict, Any
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
    azure_ai_chat_endpoint="https://your-deployment-name.eastus2.models.ai.azure.com",
    azure_ai_chat_key="00000000000000000000000000000000",
    azure_ai_chat_model="mistral-large-2411",
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
    azure_openai_chat_endpoint="https://your-deployment-name.openai.azure.com/openai/deployments/gpt-4o-deployment",
    azure_openai_chat_key="00000000000000000000000000000000",
    azure_openai_chat_api_version="yyyy-mm-dd-preview",
)

#
# Define these environment variables for text embeddings. They should point to a Cohere model
# hosted on MaaS, or any other MaaS model that text embeddings.
# AZURE_AI_EMBEDDINGS_ENDPOINT=https://<endpoint-name>.<azure-region>.models.ai.azure.com
# AZURE_AI_EMBEDDINGS_KEY=<32-char-api-key>
#
ServicePreparerEmbeddings = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_embeddings",
    azure_ai_embeddings_endpoint="https://your-deployment-name.eastus2.models.ai.azure.com",
    azure_ai_embeddings_key="00000000000000000000000000000000",
)

#
# Define these environment variables for image embeddings. They should point to a Cohere model
# hosted on MaaS, or any other MaaS model that text embeddings.
# AZURE_AI_IMAGE_EMBEDDINGS_ENDPOINT=https://<endpoint-name>.<azure-region>.models.ai.azure.com
# AZURE_AI_IMAGE_EMBEDDINGS_KEY=<32-char-api-key>
#
ServicePreparerImageEmbeddings = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_image_embeddings",
    azure_ai_image_embeddings_endpoint="https://your-deployment-name.eastus2.models.ai.azure.com",
    azure_ai_image_embeddings_key="00000000000000000000000000000000",
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

    IMAGE_EMBEDDINGDS_JSON_REQUEST_PAYLOAD = '{"input": [{"image": "data:image/png;base64,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", "text": "some text"}], "dimensions": 2048, "encoding_format": "ubinary", "input_type": "query", "model": "some-model-id", "key1": 1, "key2": true, "key3": "Some value", "key4": [1, 2, 3], "key5": {"key6": 2, "key7": false, "key8": "Some other value", "key9": [4, 5, 6, 7]}}'

    OUTPUT_FORMAT_JSON_SCHEMA: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "distances": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "location1": {
                            "type": "string",
                            "description": "The name of the first location",
                        },
                        "location2": {
                            "type": "string",
                            "description": "The name of the second location",
                        },
                        "distance": {
                            "type": "integer",
                            "description": "The distance between the two locations in miles",
                        },
                    },
                    "required": ["location1", "location2", "distance"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["distances"],
        "additionalProperties": False,
    }

    # **********************************************************************************
    #
    #              HELPER METHODS TO LOAD AUTH CREDENTIALS FOR ALL CLIENTS
    #
    # **********************************************************************************

    # Method to load chat completions api-key credentials from environment variables
    def _load_chat_credentials_api_key(self, *, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("azure_ai_chat_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("azure_ai_chat_key")
        credential = AzureKeyCredential(key)
        return endpoint, credential

    # Method to load chat completions Entra ID credentials from environment variables
    def _load_chat_credentials_entra_id(self, *, is_async: bool = False, **kwargs):
        endpoint = kwargs.pop("azure_ai_chat_endpoint")
        credential = self.get_credential(sdk.ChatCompletionsClient, is_async=is_async)
        return endpoint, credential

    # Method to load chat completions credentials when using OpenAI models.
    # See the "Data plane - inference" row in the table here for latest AOAI api-version:
    # https://aka.ms/azsdk/azure-ai-inference/azure-openai-api-versions
    def _load_aoai_chat_credentials(self, *, key_auth: bool, bad_key: bool, is_async: bool = False, **kwargs):
        endpoint = kwargs.pop("azure_openai_chat_endpoint")
        api_version = kwargs.pop("azure_openai_chat_api_version")
        if key_auth:
            key = "00000000000000000000000000000000" if bad_key else kwargs.pop("azure_openai_chat_key")
            # We no longer need to set "api-key" header, since the SDK was updated to set this header
            # (both "api-key" header and "Authorization": "Bearer ..." headers are now used for api key auth).
            # headers = {"api-key": key}
            credential = AzureKeyCredential(key)
            credential_scopes: list[str] = []
        else:
            credential = self.get_credential(sdk.ChatCompletionsClient, is_async=is_async)
            credential_scopes: list[str] = ["https://cognitiveservices.azure.com/.default"]
            # headers = {}
        return endpoint, credential, credential_scopes, api_version  # , headers

    def _load_embeddings_credentials_api_key(self, *, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("azure_ai_embeddings_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("azure_ai_embeddings_key")
        credential = AzureKeyCredential(key)
        return endpoint, credential

    def _load_embeddings_credentials_entra_id(self, is_async: bool = False, **kwargs):
        endpoint = kwargs.pop("azure_ai_embeddings_endpoint")
        credential = self.get_credential(sdk.EmbeddingsClient, is_async=is_async)
        return endpoint, credential

    def _load_image_embeddings_credentials_key_auth(self, *, bad_key: bool, **kwargs):
        endpoint = kwargs.pop("azure_ai_image_embeddings_endpoint")
        key = "00000000000000000000000000000000" if bad_key else kwargs.pop("azure_ai_image_embeddings_key")
        credential = AzureKeyCredential(key)
        return endpoint, credential

    def _load_image_embeddings_credentials_entra_id(self, is_async: bool = False, **kwargs):
        endpoint = kwargs.pop("azure_ai_image_embeddings_endpoint")
        credential = self.get_credential(sdk.ImageEmbeddingsClient, is_async=is_async)
        return endpoint, credential

    # **********************************************************************************
    #
    #     HELPER METHODS TO CREATE CLIENTS USING THE SDK's load_client() FUNCTION
    #
    # **********************************************************************************

    # Methods to create sync and async clients using Load_client() function
    async def _load_async_chat_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials_api_key(bad_key=bad_key, **kwargs)
        return await async_sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _load_chat_client(self, *, bad_key: bool = False, **kwargs) -> sdk.ChatCompletionsClient:
        endpoint, credential = self._load_chat_credentials_api_key(bad_key=bad_key, **kwargs)
        return sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    async def _load_async_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> async_sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials_api_key(bad_key=bad_key, **kwargs)
        return await async_sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _load_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> sdk.EmbeddingsClient:
        endpoint, credential = self._load_embeddings_credentials_api_key(bad_key=bad_key, **kwargs)
        return sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    async def _load_async_image_embeddings_client(
        self, *, bad_key: bool = False, **kwargs
    ) -> async_sdk.ImageEmbeddingsClient:
        endpoint, credential = self._load_image_embeddings_credentials_key_auth(bad_key=bad_key, **kwargs)
        return await async_sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    def _load_image_embeddings_client(self, *, bad_key: bool = False, **kwargs) -> sdk.ImageEmbeddingsClient:
        endpoint, credential = self._load_image_embeddings_credentials_key_auth(bad_key=bad_key, **kwargs)
        return sdk.load_client(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    # **********************************************************************************
    #
    #                  HELPER METHODS TO DIRECTLY CREATE CLIENTS
    #
    # **********************************************************************************

    def _create_chat_client(
        self, *, bad_key: bool = False, key_auth: bool = True, **kwargs
    ) -> sdk.ChatCompletionsClient:
        if key_auth:
            endpoint, credential = self._load_chat_credentials_api_key(bad_key=bad_key, **kwargs)
        else:
            endpoint, credential = self._load_chat_credentials_entra_id(**kwargs)
        return sdk.ChatCompletionsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    # Methos to create the different sync and async clients directly
    def _create_async_chat_client(
        self, *, bad_key: bool = False, key_auth: bool = True, **kwargs
    ) -> async_sdk.ChatCompletionsClient:
        if key_auth:
            endpoint, credential = self._load_chat_credentials_api_key(bad_key=bad_key, **kwargs)
        else:
            endpoint, credential = self._load_chat_credentials_entra_id(is_async=True, **kwargs)
        return async_sdk.ChatCompletionsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    def _create_aoai_chat_client(
        self, *, key_auth: bool = True, bad_key: bool = False, **kwargs
    ) -> sdk.ChatCompletionsClient:
        endpoint, credential, credential_scopes, api_version = self._load_aoai_chat_credentials(
            key_auth=key_auth, bad_key=bad_key, **kwargs
        )
        return sdk.ChatCompletionsClient(
            endpoint=endpoint,
            credential=credential,
            credential_scopes=credential_scopes,
            api_version=api_version,
            logging_enable=LOGGING_ENABLED,
        )

    def _create_async_aoai_chat_client(
        self, *, key_auth: bool = True, bad_key: bool = False, **kwargs
    ) -> async_sdk.ChatCompletionsClient:
        endpoint, credential, credential_scopes, api_version = self._load_aoai_chat_credentials(
            key_auth=True, bad_key=bad_key, is_async=True, **kwargs
        )
        return async_sdk.ChatCompletionsClient(
            endpoint=endpoint,
            credential=credential,
            credential_scopes=credential_scopes,
            api_version=api_version,
            logging_enable=LOGGING_ENABLED,
        )

    def _create_async_embeddings_client(
        self, *, bad_key: bool = False, key_auth: bool = True, **kwargs
    ) -> async_sdk.EmbeddingsClient:
        if key_auth:
            endpoint, credential = self._load_embeddings_credentials_api_key(bad_key=bad_key, **kwargs)
        else:
            endpoint, credential = self._load_embeddings_credentials_entra_id(is_async=True, **kwargs)
        return async_sdk.EmbeddingsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    def _create_embeddings_client(
        self, *, bad_key: bool = False, key_auth: bool = True, **kwargs
    ) -> sdk.EmbeddingsClient:
        if key_auth:
            endpoint, credential = self._load_embeddings_credentials_api_key(bad_key=bad_key, **kwargs)
        else:
            endpoint, credential = self._load_embeddings_credentials_entra_id(**kwargs)
        return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs)

    def _create_image_embeddings_client(
        self, *, bad_key: bool = False, key_auth: bool = True, **kwargs
    ) -> sdk.ImageEmbeddingsClient:
        if key_auth:
            endpoint, credential = self._load_image_embeddings_credentials_key_auth(bad_key=bad_key, **kwargs)
        else:
            endpoint, credential = self._load_image_embeddings_credentials_entra_id(**kwargs)
        return sdk.ImageEmbeddingsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    def _create_async_image_embeddings_client(
        self, *, bad_key: bool = False, key_auth: bool = True, **kwargs
    ) -> async_sdk.ImageEmbeddingsClient:
        if key_auth:
            endpoint, credential = self._load_image_embeddings_credentials_key_auth(bad_key=bad_key, **kwargs)
        else:
            endpoint, credential = self._load_image_embeddings_credentials_entra_id(is_async=True, **kwargs)
        return async_sdk.ImageEmbeddingsClient(
            endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED, **kwargs
        )

    def _create_embeddings_client_with_chat_completions_credentials(self, **kwargs) -> sdk.EmbeddingsClient:
        endpoint = kwargs.pop("azure_ai_chat_endpoint")
        key = kwargs.pop("azure_ai_chat_key")
        credential = AzureKeyCredential(key)
        return sdk.EmbeddingsClient(endpoint=endpoint, credential=credential, logging_enable=LOGGING_ENABLED)

    # **********************************************************************************
    #
    #             HELPER METHODS TO VALIDATE TEST RESULTS
    #
    # **********************************************************************************

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
        assert headers["api-key"] == "key-value"
        assert self.pipeline_request.http_request.data == self.EMBEDDINGDS_JSON_REQUEST_PAYLOAD

    def _validate_image_embeddings_json_request_payload(self) -> None:
        headers = self.pipeline_request.http_request.headers
        print(f"Actual HTTP request headers: {self.pipeline_request.http_request.headers}")
        print(f"Actual JSON request payload: {self.pipeline_request.http_request.data}")
        assert headers["Content-Type"] == "application/json"
        assert headers["Content-Length"] == "10364"
        assert headers["extra-parameters"] == "pass-through"
        assert headers["Accept"] == "application/json"
        assert headers["some_header"] == "some_header_value"
        assert "MyAppId azsdk-python-ai-inference/" in headers["User-Agent"]
        assert " Python/" in headers["User-Agent"]
        assert headers["Authorization"] == "Bearer key-value"
        assert headers["api-key"] == "key-value"
        assert self.pipeline_request.http_request.data == self.IMAGE_EMBEDDINGDS_JSON_REQUEST_PAYLOAD

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
        assert headers["api-key"] == "key-value"
        assert self.pipeline_request.http_request.data == self.CHAT_COMPLETIONS_JSON_REQUEST_PAYLOAD

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
        response: sdk.models.ChatCompletions,
        contains: List[str],
        *,
        is_aoai: Optional[bool] = False,
        is_json: Optional[bool] = False,
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
        if is_json:
            # Validate legal JSON format by parsing it
            json_data = json.loads(response.choices[0].message.content)

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
    def _validate_image_embeddings_result(
        response: sdk.models.EmbeddingsResult,
        encoding_format: sdk.models.EmbeddingEncodingFormat = sdk.models.EmbeddingEncodingFormat.FLOAT,
    ):
        assert response is not None
        assert response.data is not None
        assert len(response.data) == 1
        for i in [0]:
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

    # **********************************************************************************
    #
    #                   HELPER METHODS TO PRINT RESULTS
    #
    # **********************************************************************************

    @staticmethod
    def _print_model_info_result(model_info: sdk.models.ModelInfo):
        if ModelClientTestBase.PRINT_RESULT:
            print(" Model info:")
            print("\tmodel_name: {}".format(model_info.model_name))
            print("\tmodel_type: {}".format(model_info.model_type))
            print("\tmodel_provider_name: {}".format(model_info.model_provider_name))

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

    # **********************************************************************************
    #
    #                         OTHER HELPER METHODS
    #
    # **********************************************************************************

    def request_callback(self, pipeline_request) -> None:
        self.pipeline_request = pipeline_request

    @staticmethod
    def _get_image_embeddings_input(with_text: Optional[bool] = True) -> sdk.models.ImageEmbeddingInput:
        local_folder = path.dirname(path.abspath(__file__))
        image_file = path.join(local_folder, "test_image1.png")
        if with_text:
            return sdk.models.ImageEmbeddingInput.load(
                image_file=image_file,
                image_format="png",
                text="some text",
            )
        else:
            return sdk.models.ImageEmbeddingInput.load(
                image_file=image_file,
                image_format="png",
            )

    @staticmethod
    def _read_text_file(file_name: str) -> io.BytesIO:
        """
        Reads a text file and returns a BytesIO object with the file content in UTF-8 encoding.
        The file is expected to be in the same directory as this Python script.
        """
        with Path(__file__).with_name(file_name).open("r") as f:
            return io.BytesIO(f.read().encode("utf-8"))
