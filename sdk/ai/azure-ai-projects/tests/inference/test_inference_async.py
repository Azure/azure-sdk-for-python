# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live_and_not_recording
from inference_test_base import InferenceTestBase, servicePreparerInferenceTests
from azure.ai.inference.models import SystemMessage, UserMessage


# The test class name needs to start with "Test" to get collected by pytest
class TestInferenceAsync(InferenceTestBase):

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_azure_openai_client_async(self, **kwargs):
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
    async def test_inference_get_chat_completions_client_async(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_inference_tests_aiservices_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            async with await project_client.inference.get_chat_completions_client() as azure_ai_inference_client:
                response = await azure_ai_inference_client.complete(
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
    async def test_inference_get_embeddings_client_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            # TODO: Add test code here
            pass
