# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import PowerShellPreparer, AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import SwapDeploymentsDetails, SwapDeploymentsState

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsAsync(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsSwapDeploymentsAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_swap_deployments_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "EmailApp"
            deployment_name_1 = "staging"
            deployment_name_2 = "production"

            project_client = client.get_project_client(project_name)

            details = SwapDeploymentsDetails(
                first_deployment_name=deployment_name_1,
                second_deployment_name=deployment_name_2,
            )

            # Act: begin swap and wait for completion
            poller = await project_client.project.begin_swap_deployments(body=details)
            result: SwapDeploymentsState = await poller.result()

            # Assert + print LRO state
            assert result.status == "succeeded", f"Swap failed with status: {result.status}"
            print(f"Job ID: {result.job_id}")
            print(f"Status: {result.status}")
            print(f"Created on: {result.created_on}")
            print(f"Last updated on: {result.last_updated_on}")
            print(f"Expires on: {result.expires_on}")
            print(f"Warnings: {result.warnings}")
            print(f"Errors: {result.errors}")
        finally:
            await client.close()
