# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording
from inference_test_base import InferenceTestBase, servicePreparerInferenceTests
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.exceptions import ResourceNotFoundError


# The test class name needs to start with "Test" to get collected by pytest
class TestInference(InferenceTestBase):

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_aoai_client_key_auth(self, **kwargs):
        api_version = kwargs.pop("azure_ai_projects_inference_tests_aoai_api_version")
        model = kwargs.pop("azure_ai_projects_inference_tests_aoai_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            # See API versions in https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
            with project_client.inference.get_azure_openai_client(api_version=api_version) as azure_openai_client:
                if is_live_and_not_recording():
                    response = azure_openai_client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": "How many feet are in a mile?",
                            }
                        ],
                        model=model,
                    )
                    print("\nAzureOpenAI response:")
                    pprint.pprint(response)
                    contains = ["5280", "5,280"]
                    assert any(item in response.choices[0].message.content for item in contains)
                else:
                    print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
                    pass

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_aoai_client_entra_id_auth(self, **kwargs):
        connection_name = kwargs.pop("azure_ai_projects_inference_tests_entraid_auth_aoai_connection_name")
        api_version = kwargs.pop("azure_ai_projects_inference_tests_aoai_api_version")
        model = kwargs.pop("azure_ai_projects_inference_tests_aoai_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            # See API versions in https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
            with project_client.inference.get_azure_openai_client(
                api_version=api_version, connection_name=connection_name
            ) as azure_openai_client:
                if is_live_and_not_recording():
                    response = azure_openai_client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": "How many feet are in a mile?",
                            }
                        ],
                        model=model,
                    )
                    print("\nAzureOpenAI response:")
                    pprint.pprint(response)
                    contains = ["5280", "5,280"]
                    assert any(item in response.choices[0].message.content for item in contains)
                else:
                    print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
                    pass

    @servicePreparerInferenceTests()
    def test_inference_get_aoai_client_with_empty_connection_name(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            try:
                with project_client.inference.get_azure_openai_client(connection_name="") as _:
                    assert False
            except ValueError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_aoai_client_with_nonexisting_connection_name(self, **kwargs):
        if is_live_and_not_recording():
            with self.get_sync_client(**kwargs) as project_client:
                try:
                    with project_client.inference.get_azure_openai_client(
                        connection_name=InferenceTestBase.NON_EXISTING_CONNECTION_NAME
                    ) as _:
                        assert False
                except ResourceNotFoundError as e:
                    print(e)
                    assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message
        else:
            print("Skipped chat completions call with AOAI client, because it cannot be recorded.")
            pass

    # ----------------------------------------------------------------------------------------------------------------------

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_chat_completions_client_key_auth(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_inference_tests_chat_completions_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_chat_completions_client() as chat_completions_client:
                response = chat_completions_client.complete(
                    model=model,
                    messages=[
                        SystemMessage(content="You are a helpful assistant."),
                        UserMessage(content="How many feet are in a mile?"),
                    ],
                )
                print("\nChatCompletionsClient response:")
                pprint.pprint(response)
                contains = ["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_chat_completions_client_entra_id_auth(self, **kwargs):
        connection_name = kwargs.pop("azure_ai_projects_inference_tests_entraid_auth_aiservices_connection_name")
        model = kwargs.pop("azure_ai_projects_inference_tests_chat_completions_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_chat_completions_client(
                connection_name=connection_name
            ) as chat_completions_client:
                response = chat_completions_client.complete(
                    model=model,
                    messages=[
                        SystemMessage(content="You are a helpful assistant."),
                        UserMessage(content="How many feet are in a mile?"),
                    ],
                )
                print("\nChatCompletionsClient response:")
                pprint.pprint(response)
                contains = ["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)

    @servicePreparerInferenceTests()
    def test_inference_get_chat_completions_client_with_empty_connection_name(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            try:
                with project_client.inference.get_chat_completions_client(connection_name="") as _:
                    assert False
            except ValueError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_chat_completions_client_with_nonexisting_connection_name(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            try:
                with project_client.inference.get_chat_completions_client(
                    connection_name=InferenceTestBase.NON_EXISTING_CONNECTION_NAME
                ) as _:
                    assert False
            except ResourceNotFoundError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message

    # ----------------------------------------------------------------------------------------------------------------------

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_embeddings_client_key_auth(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_inference_tests_embeddings_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_embeddings_client() as embeddings_client:
                response = embeddings_client.embed(model=model, input=["first phrase", "second phrase", "third phrase"])
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
    @recorded_by_proxy
    def test_inference_get_embeddings_client_entra_id_auth(self, **kwargs):
        connection_name = kwargs.pop("azure_ai_projects_inference_tests_entraid_auth_aiservices_connection_name")
        model = kwargs.pop("azure_ai_projects_inference_tests_embeddings_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_embeddings_client(connection_name=connection_name) as embeddings_client:
                response = embeddings_client.embed(model=model, input=["first phrase", "second phrase", "third phrase"])
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
    def test_inference_get_embeddings_client_with_empty_connection_name(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            try:
                with project_client.inference.get_embeddings_client(connection_name="") as _:
                    assert False
            except ValueError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_embeddings_client_with_nonexisting_connection_name(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            try:
                with project_client.inference.get_embeddings_client(
                    connection_name=InferenceTestBase.NON_EXISTING_CONNECTION_NAME
                ) as _:
                    assert False
            except ResourceNotFoundError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message

    # ----------------------------------------------------------------------------------------------------------------------

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_image_embeddings_client_key_auth(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_inference_tests_embeddings_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_image_embeddings_client() as embeddings_client:
                response = embeddings_client.embed(model=model, input=[InferenceTestBase.get_image_embeddings_input()])
                print("\nImageEmbeddingsClient response:")
                for item in response.data:
                    length = len(item.embedding)
                    print(
                        f"data[{item.index}] (vector length={length}): "
                        f"[{item.embedding[0]}, {item.embedding[1]}, "
                        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                    )
                assert len(response.data) == 1
                assert len(response.data[0].embedding) > 0
                assert response.data[0].embedding[0] != 0.0
                assert response.data[0].embedding[-1] != 0.0

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_image_embeddings_client_entra_id_auth(self, **kwargs):
        connection_name = kwargs.pop("azure_ai_projects_inference_tests_entraid_auth_aiservices_connection_name")
        model = kwargs.pop("azure_ai_projects_inference_tests_embeddings_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_image_embeddings_client(
                connection_name=connection_name
            ) as embeddings_client:
                response = embeddings_client.embed(model=model, input=[InferenceTestBase.get_image_embeddings_input()])
                print("\nImageEmbeddingsClient response:")
                for item in response.data:
                    length = len(item.embedding)
                    print(
                        f"data[{item.index}] (vector length={length}): "
                        f"[{item.embedding[0]}, {item.embedding[1]}, "
                        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                    )
                assert len(response.data) == 1
                assert len(response.data[0].embedding) > 0
                assert response.data[0].embedding[0] != 0.0
                assert response.data[0].embedding[-1] != 0.0

    @servicePreparerInferenceTests()
    def test_inference_get_image_embeddings_client_with_empty_connection_name(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            try:
                with project_client.inference.get_image_embeddings_client(connection_name="") as _:
                    assert False
            except ValueError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_image_embeddings_client_with_nonexisting_connection_name(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            try:
                with project_client.inference.get_image_embeddings_client(
                    connection_name=InferenceTestBase.NON_EXISTING_CONNECTION_NAME
                ) as _:
                    assert False
            except ResourceNotFoundError as e:
                print(e)
                assert InferenceTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message
