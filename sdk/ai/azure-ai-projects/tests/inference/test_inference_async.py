# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live_and_not_recording
from inference_test_base import InferenceTestBase, servicePreparerInferenceTests
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.exceptions import ResourceNotFoundError


# The test class name needs to start with "Test" to get collected by pytest
class TestInferenceAsync(InferenceTestBase):

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_azure_openai_client_key_auth_async(self, **kwargs):
        api_version = kwargs.pop("azure_ai_projects_inference_tests_aoai_api_version")
        model = kwargs.pop("azure_ai_projects_inference_tests_aoai_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            # See API versions in https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
            async with await project_client.inference.get_azure_openai_client(
                api_version=api_version
            ) as azure_openai_client:
                if is_live_and_not_recording():
                    response = await azure_openai_client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": "How many feet are in a mile?",
                            }
                        ],
                        model=model,
                    )
                    print("\nAsyncAzureOpenAI response:")
                    pprint.pprint(response)
                    contains = ["5280", "5,280"]
                    assert any(item in response.choices[0].message.content for item in contains)
                else:
                    print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
                    pass

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_azure_openai_client_entra_id_auth_async(self, **kwargs):
        connection_name = kwargs.pop("azure_ai_projects_inference_tests_entraid_auth_aoai_connection_name")
        api_version = kwargs.pop("azure_ai_projects_inference_tests_aoai_api_version")
        model = kwargs.pop("azure_ai_projects_inference_tests_aoai_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            # See API versions in https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
            async with await project_client.inference.get_azure_openai_client(
                api_version=api_version, connection_name=connection_name
            ) as azure_openai_client:
                if is_live_and_not_recording():
                    response = await azure_openai_client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": "How many feet are in a mile?",
                            }
                        ],
                        model=model,
                    )
                    print("\nAsyncAzureOpenAI response:")
                    pprint.pprint(response)
                    contains = ["5280", "5,280"]
                    assert any(item in response.choices[0].message.content for item in contains)
                else:
                    print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
                    pass

    @servicePreparerInferenceTests()
    async def test_inference_get_aoai_client_with_empty_connection_name_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            try:
                async with await project_client.inference.get_azure_openai_client(
                    connection_name=""
                ) as azure_openai_client:
                    assert False
            except ValueError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_aoai_client_with_nonexisting_connection_name_async(self, **kwargs):
        if is_live_and_not_recording():
            async with self.get_async_client(**kwargs) as project_client:
                try:
                    async with await project_client.inference.get_azure_openai_client(
                        connection_name=InferenceTestBase.NON_EXISTING_CONNECTION_NAME
                    ) as azure_openai_client:
                        assert False
                except ResourceNotFoundError as e:
                    print(e)
                    assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message
        else:
            print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
            pass

    # ----------------------------------------------------------------------------------------------------------------------

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_chat_completions_client_key_auth_async(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_inference_tests_chat_completions_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            async with await project_client.inference.get_chat_completions_client() as chat_completions_client:
                response = await chat_completions_client.complete(
                    model=model,
                    messages=[
                        SystemMessage(content="You are a helpful assistant."),
                        UserMessage(content="How many feet are in a mile?"),
                    ],
                )
                print("\nAsync ChatCompletionsClient response:")
                pprint.pprint(response)
                contains = ["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_chat_completions_client_entra_id_auth_async(self, **kwargs):
        connection_name = kwargs.pop("azure_ai_projects_inference_tests_entraid_auth_aiservices_connection_name")
        model = kwargs.pop("azure_ai_projects_inference_tests_chat_completions_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            async with await project_client.inference.get_chat_completions_client(
                connection_name=connection_name
            ) as chat_completions_client:
                response = await chat_completions_client.complete(
                    model=model,
                    messages=[
                        SystemMessage(content="You are a helpful assistant."),
                        UserMessage(content="How many feet are in a mile?"),
                    ],
                )
                print("\nAsync ChatCompletionsClient response:")
                pprint.pprint(response)
                contains = ["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)

    @servicePreparerInferenceTests()
    async def test_inference_get_chat_completions_client_with_empty_connection_name_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            try:
                async with await project_client.inference.get_chat_completions_client(
                    connection_name=""
                ) as chat_completions_client:
                    assert False
            except ValueError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_chat_completions_client_with_nonexisting_connection_name_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            try:
                async with await project_client.inference.get_chat_completions_client(
                    connection_name=InferenceTestBase.NON_EXISTING_CONNECTION_NAME
                ) as chat_completions_client:
                    assert False
            except ResourceNotFoundError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message

    # ----------------------------------------------------------------------------------------------------------------------

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_embeddings_client_key_auth_async(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_inference_tests_embeddings_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            async with await project_client.inference.get_embeddings_client() as embeddings_client:
                response = await embeddings_client.embed(
                    model=model, input=["first phrase", "second phrase", "third phrase"]
                )
                print("\nEmbeddingsClient response:")
                for item in response.data:
                    length = len(item.embedding)
                    print(
                        f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                    )
                assert len(response.data) == 3
                for item in response.data:
                    assert len(item.embedding) > 0
                    assert item.embedding[0] != 0
                    assert item.embedding[-1] != 0

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_embeddings_client_entra_id_auth_async(self, **kwargs):
        connection_name = kwargs.pop("azure_ai_projects_inference_tests_entraid_auth_aiservices_connection_name")
        model = kwargs.pop("azure_ai_projects_inference_tests_embeddings_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            async with await project_client.inference.get_embeddings_client(
                connection_name=connection_name
            ) as embeddings_client:
                response = await embeddings_client.embed(
                    model=model, input=["first phrase", "second phrase", "third phrase"]
                )
                print("\nEmbeddingsClient response:")
                for item in response.data:
                    length = len(item.embedding)
                    print(
                        f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                    )
                assert len(response.data) == 3
                for item in response.data:
                    assert len(item.embedding) > 0
                    assert item.embedding[0] != 0
                    assert item.embedding[-1] != 0

    @servicePreparerInferenceTests()
    async def test_inference_get_embeddings_client_with_empty_connection_name_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            try:
                async with await project_client.inference.get_embeddings_client(
                    connection_name=""
                ) as embeddings_client:
                    assert False
            except ValueError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_embeddings_client_with_nonexisting_connection_name_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            try:
                async with await project_client.inference.get_embeddings_client(
                    connection_name=InferenceTestBase.NON_EXISTING_CONNECTION_NAME
                ) as embeddings_client:
                    assert False
            except ResourceNotFoundError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message
