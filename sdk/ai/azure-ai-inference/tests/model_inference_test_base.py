# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging
import sys
import azure.ai.inference as sdk
import azure.ai.inference.aio as async_sdk
import asyncio
import time

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

ServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "chat_completions",
    chat_completions_endpoint="https://your-deployment-name.your-azure-region.inference.ai.azure.com",
    chat_completions_key="00000000000000000000000000000000",
)


# The test class name needs to start with "Test" to get collected by pytest
class ModelClientTestBase(AzureRecordedTestCase):

    client: sdk.ModelClient
    async_client: async_sdk.ModelClient
    connection_url: str

    # Set to True to print out all analysis results
    PRINT_CHAT_COMPLETION_RESULTS = True

    def _create_client_for_standard_test(self, sync: bool, get_connection_url: bool = False, **kwargs):
        endpoint = kwargs.pop("chat_completions_endpoint")
        key = kwargs.pop("chat_completions_key")
        self._create_client(endpoint, key, sync, get_connection_url)

    def _create_client_for_authentication_failure(self, sync: bool, **kwargs):
        endpoint = kwargs.pop("chat_completions_endpoint")
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
        query_params: Optional[dict] = None,
        **kwargs,
    ):

        result = self.client.get_chat_completions(messages=kwargs.get("messages"), params=query_params)

        # Optional: console printout of all results
        if ModelClientTestBase.PRINT_CHAT_COMPLETION_RESULTS:
            ModelClientTestBase._print_chat_completions_results(result)

        # Validate all results
        ModelClientTestBase._validate_chat_completions_results(result)

        # Validate that additional query parameters exists in the connection URL, if specify
        if query_params is not None:
            ModelClientTestBase._validate_query_parameters(query_params, self.connection_url)

    async def _do_async_chat_completions(
        self,
        query_params: Optional[dict] = None,
        **kwargs,
    ):
        start_time = time.time()

        # Start the operation and get a Future object
        future = asyncio.ensure_future(self.async_client.get_chat_completions(messages=kwargs.get("messages")))

        # Loop until the operation is done
        while not future.done():
            await asyncio.sleep(0.1)  # sleep for 100 ms
            print(f"Elapsed time: {int(1000*(time.time()- start_time))}ms")

        # Get the result (this will not block since the operation is done)
        result = future.result()

        # Optional: console printout of all results
        if ModelClientTestBase.PRINT_CHAT_COMPLETION_RESULTS:
            ModelClientTestBase._print_chat_completions_results(result)

        # Validate all results
        ModelClientTestBase._validate_chat_completions_results(result)

        # Validate that additional query parameters exists in the connection URL, if specify
        if query_params is not None:
            ModelClientTestBase._validate_query_parameters(query_params, self.connection_url)

    def _do_chat_completion_with_error(
        self,
        expected_status_code: int,
        expected_message_contains: str,
        **kwargs,
    ):

        try:
            result = self.client.get_chat_completions(messages=kwargs.get("messages"))

        except AzureError as e:
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == expected_status_code
            assert expected_message_contains in e.message
            return
        assert False  # We should not get here

    async def _do_async_chat_completion_with_error(
        self,
        expected_status_code: int,
        expected_message_contains: str,
        **kwargs,
    ):

        try:
            result = await self.async_client.get_chat_completions(messages=kwargs.get("messages"))

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
    def _validate_chat_completions_results(result: sdk.models.ChatCompletions):

        assert "5,280" in result.choices[0].message.content or "5280" in result.choices[0].message.content
        assert result.choices[0].message.role == sdk.models.ChatRole.ASSISTANT
        assert result.choices[0].finish_reason == sdk.models.CompletionsFinishReason.STOPPED
        assert result.choices[0].index == 0

        assert result.id is not None
        assert result.id != ""
        assert result.created is not None
        assert result.created != ""
        assert result.model is not None
        assert result.model != ""
        assert result.object == "chat.completion"
        assert result.usage.prompt_tokens > 0
        assert result.usage.completion_tokens > 0
        assert result.usage.total_tokens == result.usage.prompt_tokens + result.usage.completion_tokens

    @staticmethod
    def _print_chat_completions_results(result: sdk.models.ChatCompletions):

        print(" Chat Completions:")

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
