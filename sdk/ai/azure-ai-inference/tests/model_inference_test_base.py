# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging
import sys
import azure.ai.inference as sdk
import azure.ai.inference as async_sdk

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
    logger.setLevel(logging.INFO)  # INFO or DEBUG

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

ServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "model",
    model_endpoint="https://your-azure-resource-name.your-azure-region.inference.ai.azure.com",
    model_key="00000000000000000000000000000000"
)


# The test class name needs to start with "Test" to get collected by pytest
class ModelInferenceTestBase(AzureRecordedTestCase):

    client: sdk.ModelClient
    async_client: async_sdk.ModelClient
    connection_url: str

    # Set to True to print out all analysis results
    PRINT_CHAT_COMPLETION_RESULTS = True

    def _create_client_for_standard_test(self, sync: bool, get_connection_url: bool = False, **kwargs):
        endpoint = kwargs.pop("model_endpoint")
        key = kwargs.pop("model_key")
        self._create_client(endpoint, key, sync, get_connection_url)

    def _create_client_for_authentication_failure(self, sync: bool, **kwargs):
        endpoint = kwargs.pop("model_endpoint")
        key = "00000000000000000000000000000000"
        self._create_client(endpoint, key, sync, False)

    def _create_client(self, endpoint: str, key: str, sync: bool, get_connection_url: bool):
        credential = AzureKeyCredential(key)
        if sync:
            self.client = sdk.ModelClient(
                endpoint=endpoint,
                credential=credential,
                logging_enable=LOGGING_ENABLED,
                raw_request_hook=self._raw_request_check if get_connection_url else None,
            )
            assert self.client is not None
        else:
            self.async_client = async_sdk.ModelClient(
                endpoint=endpoint,
                credential=credential,
                logging_enable=LOGGING_ENABLED,
                raw_request_hook=self._raw_request_check if get_connection_url else None,
            )
            assert self.async_client is not None

    def _raw_request_check(self, request: PipelineRequest):
        self.connection_url = request.http_request.url
        print(f"Connection URL: {request.http_request.url}")

    def _do_chat_completions(
        self,
        options: sdk.models.ChatCompletionsOptions,
        query_params: Optional[dict] = None,
        **kwargs,
    ):

        result = self.client.get_chat_completions(options=options, params=query_params)

        # Optional: console printout of all results
        if ModelInferenceTestBase.PRINT_CHAT_COMPLETION_RESULTS:
            ModelInferenceTestBase._print_chat_completion_results(result)

        # Validate all results
        ModelInferenceTestBase._validate_chat_completion_results(result)

        # Validate that additional query parameters exists in the connection URL, if specify
        if query_params is not None:
            ModelInferenceTestBase._validate_query_parameters(query_params, self.connection_url)

    async def _do_async_chat_completion(
        self,
        options: sdk.models.ChatCompletionsOptions,
        query_params: Optional[dict] = None,
        **kwargs,
    ):

        result = await self.async_client.chat_completions(options=options, params=query_params)

        # Optional: console printout of all results
        if ModelInferenceTestBase.PRINT_CHAT_COMPLETION_RESULTS:
            ModelInferenceTestBase._print_chat_completion_results(result)

        # Validate all results
        ModelInferenceTestBase._validate_chat_completion_results(result)

        # Validate that additional query parameters exists in the connection URL, if specify
        if query_params is not None:
            ModelInferenceTestBase._validate_query_parameters(query_params, self.connection_url)

    def _do_chat_completion_with_error(
        self,
        options: sdk.models.ChatCompletionsOptions,
        expected_status_code: int,
        expected_message_contains: str,
        **kwargs,
    ):

        try:
            result = self.client.get_chat_completions(options=options)

        except AzureError as e:
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == expected_status_code
            assert expected_message_contains in e.message
            return
        assert False  # We should not get here

    async def _do_async_chat_completion_with_error(
        self,
        options: sdk.models.ChatCompletionsOptions,
        expected_status_code: int,
        expected_message_contains: str,
        **kwargs,
    ):

        try:
            result = await self.async_client.get_chat_completions(options=options)

        except AzureError as e:
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == expected_status_code
            assert expected_message_contains in e.message
            return
        assert False  # We should not get here

    @staticmethod
    def _validate_query_parameters(query_params: dict, connection_url: str):
        assert len(query_params) > 0
        query_string = ""
        for key, value in query_params.items():
            query_string += "&" + key + "=" + value
        query_string = "?" + query_string[1:]
        assert query_string in connection_url

    @staticmethod
    def _validate_result(result: sdk.models.ChatCompletions):
        assert True

    @staticmethod
    def _print_analysis_results(result: sdk.models.ChatCompletions):

        for choice in result.choices:
            print(" choices[0].message.content: {}".format(choice.message.content))
            print(" choices[0].message.role: {}".format(choice.message.role))
            print(" choices[0].finish_reason: {}".format(choice.finish_reason))
            print(" choices[0].index: {}".format(choice.index))

        print(" id: {}".format(result.id))
        print(" created: {}".format(result.created))
        print(" model: {}".format(result.model))
        print(" object: {}".format(result.object))
        print(" usage.completion_tokens: {}".format(result.usage.completion_tokens))
        print(" usage.prompt_tokens: {}".format(result.usage.prompt_tokens))
        print(" usage.completion_tokens: {}".format(result.usage.completion_tokens))

