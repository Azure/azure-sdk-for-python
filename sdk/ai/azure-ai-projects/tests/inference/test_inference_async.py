# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
from devtools_testutils.aio import recorded_by_proxy_async
from inference_test_base import InferenceTestBase, servicePreparerInferenceTests
from azure.ai.inference.models import SystemMessage, UserMessage

# The test class name needs to start with "Test" to get collected by pytest
class TestInferenceAsync(InferenceTestBase):
    
    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_azure_openai_client_async(self, **kwargs):
        model = kwargs.pop("azure_ai_projects_connections_test_model_deployment_name")
        async with self.get_async_client(**kwargs) as project_client:
            async with await project_client.inference.get_azure_openai_client() as azure_openai_client:
                response = await azure_openai_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": "How many feet are in a mile?",
                        }
                    ],
                    model=model,
                )
                pprint.pprint(response)
                contains=["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)


    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_chat_completions_client_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            async with await project_client.inference.get_chat_completions_client() as azure_ai_inference_client:
                response = await azure_ai_inference_client.complete(
                    messages=[
                        SystemMessage(content="You are a helpful assistant."),
                        UserMessage(content="How many feet are in a mile?"),
                    ]
                )
                pprint.pprint(response)
                contains=["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)

    @servicePreparerInferenceTests()
    @recorded_by_proxy_async
    async def test_inference_get_embeddings_client_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:
            # TODO: Add test code here
            pass
