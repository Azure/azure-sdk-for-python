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

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_get_model_info_error_free(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        result = client.get_model_info()
        self._print_model_info_result(result)
        self._validate_model_info_result(result)
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_error_free(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        result = client.create(messages=[sdk.models.UserMessage(content="How many feet are in a mile?")])
        self._print_chat_completions_result(result)
        self._validate_chat_completions_result(result, ["5280", "5,280"])
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_streaming_error_free(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        result = client.create_streaming(
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="Give me 5 good reasons why I should exercise every day."),
            ]
        )
        self._validate_chat_completions_streaming_result(result)
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_tool_error_free(self, **kwargs):
        forecast_tool = sdk.models.ChatCompletionsFunctionToolDefinition(
            function=sdk.models.FunctionDefinition(
                name="get_max_temperature",
                description="A function that returns the forecasted maximum temperature IN a given city, a given few days from now, in Fahrenheit. It returns `unknown` if the forecast is not known.",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city",
                        },
                        "days": {
                            "type": "string",
                            "description": "The number of days from now, starting from 0, where 0 represents today, 1 represents tomorrow, etc.",
                        },
                    },
                    "required": ["city", "days"],
                },
            )
        )
        client = self._create_chat_client(**kwargs)
        messages = [
            sdk.models.SystemMessage(content="You are an assistant that helps users find weather information."),
            sdk.models.UserMessage(content="what's the maximum temperature in Seattle two days from now?"),
        ]
        result = client.create(
            messages=messages,
            tools=[forecast_tool],
        )
        self._print_chat_completions_result(result)
        self._validate_chat_completions_tool_result(result)
        messages.append(sdk.models.AssistantMessage(tool_calls=result.choices[0].message.tool_calls))
        messages.append(
            sdk.models.ToolMessage(
                content="62",
                tool_call_id=result.choices[0].message.tool_calls[0].id,
            )
        )
        result = client.create(
            messages=messages,
            tools=[forecast_tool],
        )
        self._validate_chat_completions_result(result, ["62"])
        client.close()

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
        exception_caught = False
        try:
            result = client.create(messages=[sdk.models.UserMessage(content="How many feet are in a mile?")])
        except AzureError as e:
            exception_caught = True
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 401
            assert "unauthorized" in e.message.lower()
        client.close()
        assert exception_caught

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_embeddings_on_chat_completion_endpoint(self, **kwargs):
        client = self._create_embeddings_client_with_chat_completions_credentials(**kwargs)
        exception_caught = False
        try:
            result = client.create(input=["first phrase", "second phrase", "third phrase"])
        except AzureError as e:
            exception_caught = True
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 404 or e.status_code == 405  # `404 - not found` or `405 - method not allowed`
            assert "not found" in e.message.lower() or "not allowed" in e.message.lower()
        client.close()
        assert exception_caught
