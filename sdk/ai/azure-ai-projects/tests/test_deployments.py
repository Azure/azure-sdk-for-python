# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.projects import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy


class TestDeployments(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_deployments.py::TestDeployments::test_deployments -s
    @servicePreparer()
    @recorded_by_proxy
    def test_deployments(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        model_publisher = self.test_deployments_params["model_publisher"]
        model_name = self.test_deployments_params["model_name"]
        model_deployment_name = self.test_deployments_params["model_deployment_name"]

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print("[test_deployments] List all deployments")
            empty = True
            for deployment in project_client.deployments.list():
                empty = False
                TestBase.validate_deployment(deployment)
            assert not empty

            print(f"[test_deployments] List all deployments by the model publisher `{model_publisher}`")
            empty = True
            for deployment in project_client.deployments.list(model_publisher=model_publisher):
                empty = False
                TestBase.validate_deployment(deployment, expected_model_publisher=model_publisher)
            assert not empty

            print(f"[test_deployments] List all deployments of model `{model_name}`")
            empty = True
            for deployment in project_client.deployments.list(model_name=model_name):
                empty = False
                TestBase.validate_deployment(deployment, expected_model_name=model_name)
            assert not empty

            print(f"[test_deployments] Get a single deployment named `{model_deployment_name}`")
            deployment = project_client.deployments.get(model_deployment_name)
            TestBase.validate_deployment(deployment, expected_model_deployment_name=model_deployment_name)
