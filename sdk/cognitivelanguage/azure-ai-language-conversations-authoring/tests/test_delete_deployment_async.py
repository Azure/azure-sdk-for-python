# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import PowerShellPreparer, AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import DeploymentState

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsAsync(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsDeleteDeploymentAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_deployment_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "Test-data-labels"
            deployment_name = "deployment3"

            project_client = client.get_project_client(project_name)

            # Act: begin delete and wait for completion
            poller = await project_client.deployment.begin_delete_deployment(deployment_name=deployment_name)
            result: DeploymentState = await poller.result()

            # Assert + print LRO state
            assert result.status == "succeeded", f"Delete failed with status: {result.status}"
            print(f"Job ID: {result.job_id}")
            print(f"Status: {result.status}")
            print(f"Created on: {result.created_on}")
            print(f"Last updated on: {result.last_updated_on}")
            print(f"Expires on: {result.expires_on}")
            print(f"Warnings: {result.warnings}")
            print(f"Errors: {result.errors}")
        finally:
            await client.close()
