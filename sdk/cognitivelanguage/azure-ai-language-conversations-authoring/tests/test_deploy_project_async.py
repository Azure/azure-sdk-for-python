# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import EnvironmentVariableLoader, AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import CreateDeploymentDetails, DeploymentState

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsAsync(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsDeployProjectAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_deploy_project_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "EmailApp"
            deployment_name = "production"
            trained_model_label = "Model1"

            project_client = client.get_project_client(project_name)

            # Build request body for deployment
            details = CreateDeploymentDetails(trained_model_label=trained_model_label)

            # Act: begin deploy and wait for completion
            poller = await project_client.deployment.begin_deploy_project(
                deployment_name=deployment_name,
                body=details,
            )
            result: DeploymentState = await poller.result()

            # Assert + print LRO state
            assert result.status == "succeeded", f"Deploy failed with status: {result.status}"
            print(f"Job ID: {result.job_id}")
            print(f"Status: {result.status}")
            print(f"Created on: {result.created_on}")
            print(f"Last updated on: {result.last_updated_on}")
            print(f"Expires on: {result.expires_on}")
            print(f"Warnings: {result.warnings}")
            print(f"Errors: {result.errors}")
        finally:
            await client.close()
