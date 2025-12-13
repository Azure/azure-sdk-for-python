# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.ai.projects.aio import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async


class TestDeploymentsAsync(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_deployments_async.py::TestDeploymentsAsync::test_deployments_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_deployments_async(self, **kwargs):

        model_publisher = self.test_deployments_params["model_publisher"]
        model_name = self.test_deployments_params["model_name"]
        model_deployment_name = self.test_deployments_params["model_deployment_name"]

        async with self.create_async_client(**kwargs) as project_client:

            print("[test_deployments_async] List all deployments")
            empty = True
            async for deployment in project_client.deployments.list():
                empty = False
                TestBase.validate_deployment(deployment)
            assert not empty

            print(f"[test_deployments_async] List all deployments by the model publisher `{model_publisher}`")
            empty = True
            async for deployment in project_client.deployments.list(model_publisher=model_publisher):
                empty = False
                TestBase.validate_deployment(deployment, expected_model_publisher=model_publisher)
            assert not empty

            print(f"[test_deployments_async] List all deployments of model `{model_name}`")
            empty = True
            async for deployment in project_client.deployments.list(model_name=model_name):
                empty = False
                TestBase.validate_deployment(deployment, expected_model_name=model_name)
            assert not empty

            print(f"[test_deployments_async] Get a single deployment named `{model_deployment_name}`")
            deployment = await project_client.deployments.get(model_deployment_name)
            TestBase.validate_deployment(deployment, expected_model_deployment_name=model_deployment_name)
