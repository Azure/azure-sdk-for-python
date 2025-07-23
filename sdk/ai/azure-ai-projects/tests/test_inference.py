# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pprint

import pytest
from azure.ai.projects import AIProjectClient
from test_base import TestBase, servicePreparer
from openai import OpenAI
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording


# To run all tests in this class, use the following command in the \sdk\ai\azure-ai-projects folder:
# cls & pytest tests\test_inference.py -s
class TestInference(TestBase):

    @classmethod
    def _test_openai_client(cls, client: OpenAI, model_deployment_name: str):
        chat_completions = client.chat.completions.create(
            model=model_deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": "How many feet are in a mile?",
                },
            ],
        )

        print("Raw dump of chat completions object: ")
        pprint.pprint(chat_completions)
        print("Response message: ", chat_completions.choices[0].message.content)
        contains = ["5280", "5,280"]
        assert any(item in chat_completions.choices[0].message.content for item in contains)

        response = client.responses.create(
            model=model_deployment_name,
            input="How many feet are in a mile?",
        )

        print("Raw dump of responses object: ")
        pprint.pprint(response)
        print("Response message: ", response.output_text)
        contains = ["5280", "5,280"]
        assert any(item in response.output_text for item in contains)

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_inference.py::TestInference::test_inference -s
    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with AOAI client",
    )
    @recorded_by_proxy
    def test_inference(self, **kwargs):

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
            with project_client.get_openai_client(api_version=api_version) as client:
                self._test_openai_client(client, model_deployment_name)

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_inference.py::TestInference::test_inference_on_api_key_auth_connection -s
    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with AOAI client",
    )
    @recorded_by_proxy
    def test_inference_on_api_key_auth_connection(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        connection_name = self.test_inference_params["connection_name_api_key_auth"]
        model_deployment_name = self.test_inference_params["model_deployment_name"]
        api_version = self.test_inference_params["aoai_api_version"]

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print(
                "[test_inference_on_api_key_auth_connection] Get an authenticated Azure OpenAI client for a connection AOAI service, and perform a chat completion operation."
            )
            with project_client.get_openai_client(api_version=api_version, connection_name=connection_name) as client:
                self._test_openai_client(client, model_deployment_name)

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_inference.py::TestInference::test_inference_on_entra_id_auth_connection -s
    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with AOAI client",
    )
    @recorded_by_proxy
    def test_inference_on_entra_id_auth_connection(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        connection_name = self.test_inference_params["connection_name_entra_id_auth"]
        model_deployment_name = self.test_inference_params["model_deployment_name"]
        api_version = self.test_inference_params["aoai_api_version"]

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print(
                "[test_inference_on_entra_id_auth_connection] Get an authenticated Azure OpenAI client for a connection AOAI service, and perform a chat completion operation."
            )
            with project_client.get_openai_client(api_version=api_version, connection_name=connection_name) as client:
                self._test_openai_client(client, model_deployment_name)
