# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording
from inference_test_base import InferenceTestBase, servicePreparerInferenceTests
from azure.ai.inference.models import SystemMessage, UserMessage


# The test class name needs to start with "Test" to get collected by pytest
class TestInference(InferenceTestBase):

    @servicePreparerInferenceTests()
    @recorded_by_proxy
    def test_inference_get_azure_openai_client(self, **kwargs):
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
    def test_inference_get_chat_completions_client(self, **kwargs):
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
    def test_inference_get_embeddings_client(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_inference_tests_embeddings_model_deployment_name")
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_embeddings_client() as embeddings_client:
                response = embeddings_client.embed(
                    model=model,
                    input=["first phrase", "second phrase", "third phrase"]
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
