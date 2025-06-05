# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
from azure.ai.projects.aio import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from devtools_testutils.aio import recorded_by_proxy_async


class TestInferenceAsync(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_inference_async.py::TestInferenceAsync::test_inference_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_inference_async(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        model_deployment_name = self.test_inference_params["model_deployment_name"]
        api_version = self.test_inference_params["aoai_api_version"]

        async with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=True),
        ) as project_client:

            print(
                "[test_inference_async] Get an authenticated Azure OpenAI client for the parent AI Services resource, and perform a chat completion operation."
            )
            if is_live_and_not_recording():
                async with await project_client.inference.get_azure_openai_client(api_version=api_version) as client:

                    response = await client.chat.completions.create(
                        model=model_deployment_name,
                        messages=[
                            {
                                "role": "user",
                                "content": "How many feet are in a mile?",
                            },
                        ],
                    )

                    print("Raw dump of response object: ")
                    pprint.pprint(response)
                    print("Response message: ", response.choices[0].message.content)
                    contains = ["5280", "5,280"]
                    assert any(item in response.choices[0].message.content for item in contains)
            else:
                print("Skipped because we cannot record chat completions call with AOAI client.")

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_inference_async.py::TestInferenceAsync::test_inference_on_connection_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_inference_on_connection_async(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        connection_name = self.test_inference_params["connection_name"]
        model_deployment_name = self.test_inference_params["model_deployment_name"]
        api_version = self.test_inference_params["aoai_api_version"]

        async with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print(
                "[test_inference_on_connection_async] Get an authenticated Azure OpenAI client for a connection AOAI service, and perform a chat completion operation."
            )
            if is_live_and_not_recording():
                async with await project_client.inference.get_azure_openai_client(
                    api_version=api_version, connection_name=connection_name
                ) as client:

                    response = await client.chat.completions.create(
                        model=model_deployment_name,
                        messages=[
                            {
                                "role": "user",
                                "content": "How many feet are in a mile?",
                            },
                        ],
                    )

                    print("Raw dump of response object: ")
                    pprint.pprint(response)
                    print("Response message: ", response.choices[0].message.content)
                    contains = ["5280", "5,280"]
                    assert any(item in response.choices[0].message.content for item in contains)
            else:
                print("Skipped because we cannot record chat completions call with AOAI client.")
