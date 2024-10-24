# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
from devtools_testutils import recorded_by_proxy
from inference_test_base import InferenceTestBase, servicePreparerConnectionsTests
from azure.ai.inference.models import SystemMessage, UserMessage

# The test class name needs to start with "Test" to get collected by pytest
class TestInference(InferenceTestBase):

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_inference_get_azure_openai_client(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_azure_openai_client() as azure_openai_client:
                response = azure_openai_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": "How many feet are in a mile?",
                        }
                    ],
                    model="gpt-4-0613", # TODO: Get this from environment variable
                )
                pprint.pprint(response)
                contains=["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_inference_get_chat_completions_client(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:
            with project_client.inference.get_chat_completions_client() as azure_ai_inference_client:
                response = azure_ai_inference_client.complete(
                    messages=[
                        SystemMessage(content="You are a helpful assistant."),
                        UserMessage(content="How many feet are in a mile?"),
                    ]
                )
                pprint.pprint(response)
                contains=["5280", "5,280"]
                assert any(item in response.choices[0].message.content for item in contains)

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_inference_get_embeddings_client(self, **kwargs):
        project_client = self.get_sync_client(**kwargs)
