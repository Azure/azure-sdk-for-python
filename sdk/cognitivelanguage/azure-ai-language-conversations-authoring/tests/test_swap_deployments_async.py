# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import EnvironmentVariableLoader, AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import SwapDeploymentsDetails, SwapDeploymentsState

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
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
        async with client:
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
            try:
                await poller.result()  # completes with None; raises on failure
            except HttpResponseError as e:
                print(f"Operation failed: {e.message}")
                print(e.error)
                raise

            # Success -> poller completed
            print(f"Swap deployments completed. done={poller.done()} status={poller.status()}")
