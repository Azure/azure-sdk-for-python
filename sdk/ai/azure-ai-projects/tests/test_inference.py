# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint
#import pytest
from azure.ai.projects import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording


class TestInference(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_inference.py::TestInference::test_inference -s
    @servicePreparer()
    @recorded_by_proxy
    # TODO: Why doesn't this work? @pytest.mark.skipif(condition=(not is_live_and_not_recording()), reason="Skipped because we cannot record chat completions call with AOAI client")
    def test_inference(self, **kwargs):

        # Alternative to the above @pytest.mark.skipif
        if not is_live_and_not_recording():
            print("Skipped because we cannot record chat completions call with AOAI client.")
            return

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        model_deployment_name = self.test_inference_params["model_deployment_name"]
        api_version = self.test_inference_params["aoai_api_version"]

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print(
                "[test_inference] Get an authenticated Azure OpenAI client for the parent AI Services resource, and perform a chat completion operation."
            )
            with project_client.inference.get_azure_openai_client(api_version=api_version) as client:

                response = client.chat.completions.create(
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

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_inference.py::TestInference::test_inference_on_connection -s
    @servicePreparer()
    @recorded_by_proxy
    # TODO: Why doesn't this work? @pytest.mark.skipif(condition=(not is_live_and_not_recording()), reason="Skipped because we cannot record chat completions call with AOAI client")
    def test_inference_on_connection(self, **kwargs):

        # Alternative to the above @pytest.mark.skipif
        if not is_live_and_not_recording():
            print("Skipped because we cannot record chat completions call with AOAI client.")
            return

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        connection_name = self.test_inference_params["connection_name"]
        model_deployment_name = self.test_inference_params["model_deployment_name"]
        api_version = self.test_inference_params["aoai_api_version"]

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print(
                "[test_inference_on_connection] Get an authenticated Azure OpenAI client for a connection AOAI service, and perform a chat completion operation."
            )
            with project_client.inference.get_azure_openai_client(
                api_version=api_version, connection_name=connection_name
            ) as client:

                response = client.chat.completions.create(
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
