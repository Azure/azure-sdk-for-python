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
    def test_load_chat_completions_client(self, **kwargs):

        client = self._load_chat_client(**kwargs)
        assert isinstance(client, sdk.ChatCompletionsClient)
        response1 = client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(response1, "completion") # TODO: This should be ModelType.CHAT once the model is fixed
        client.close()

    @ServicePreparerEmbeddings()
    @recorded_by_proxy
    def test_load_embeddings_client(self, **kwargs):

        client = self._load_embeddings_client(**kwargs)
        assert isinstance(client, sdk.EmbeddingsClient)
        response1 = client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(response1, "embedding") # TODO: This should be ModelType.EMBEDDINGS once the model is fixed
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_get_model_info_on_chat_client(self, **kwargs):

        client = self._create_chat_client(**kwargs)
        response1 = client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(response1, "completion") # TODO: This should be ModelType.CHAT once the model is fixed

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2

        client.close()

    @ServicePreparerEmbeddings()
    @recorded_by_proxy
    def test_get_model_info_on_embeddings_client(self, **kwargs):

        client = self._create_embeddings_client(**kwargs)
        response1 = client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(response1, "embedding") # TODO: This should be ModelType.EMBEDDINGS once the model is fixed

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2

        client.close()
    
    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_hyper_params(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        response = client.complete(
            messages=[sdk.models.UserMessage(content="How many feet are in a mile?")],
            unknown_params=sdk.models.UnknownParams.IGNORE,
            hyper_params={
                "key1": 1,
                "key2": True,
                "key3": "Some value",
                "key4": [1, 2, 3],
                "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
            },
        )
        self._print_chat_completions_result(response)
        self._validate_chat_completions_result(response, ["5280", "5,280"])
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_streaming(self, **kwargs):
        client = self._create_chat_client(**kwargs)
        response = client.complete(
            stream=True,
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="Give me 3 good reasons why I should exercise every day."),
            ],
        )
        self._validate_chat_completions_streaming_result(response)
        client.close()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completions_with_tool(self, **kwargs):
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
        response = client.complete(
            messages=messages,
            tools=[forecast_tool],
        )
        self._print_chat_completions_result(response)
        self._validate_chat_completions_tool_result(response)
        messages.append(sdk.models.AssistantMessage(tool_calls=response.choices[0].message.tool_calls))
        messages.append(
            sdk.models.ToolMessage(
                content="62",
                tool_call_id=response.choices[0].message.tool_calls[0].id,
            )
        )
        response = client.complete(
            messages=messages,
            tools=[forecast_tool],
        )
        self._validate_chat_completions_result(response, ["62"])
        client.close()

    @ServicePreparerEmbeddings()
    @recorded_by_proxy
    def test_embeddings(self, **kwargs):
        client = self._create_embeddings_client(**kwargs)
        response = client.embedding(input=["first phrase", "second phrase", "third phrase"])
        self._print_embeddings_result(response)
        self._validate_embeddings_result(response)
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
            response = client.complete(messages=[sdk.models.UserMessage(content="How many feet are in a mile?")])
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
            response = client.embedding(input=["first phrase", "second phrase", "third phrase"])
        except AzureError as e:
            exception_caught = True
            print(e)
            assert hasattr(e, "status_code")
            assert e.status_code == 404 or e.status_code == 405  # `404 - not found` or `405 - method not allowed`
            assert "not found" in e.message.lower() or "not allowed" in e.message.lower()
        client.close()
        assert exception_caught
