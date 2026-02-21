# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import EnvironmentVariableLoader, AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import CreateDeploymentDetails, AssignedProjectResource

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
        async with client:
            project_name = "EmailAppEnglish"
            deployment_name = "staging0828"
            trained_model_label = "ModelWithDG"

            project_client = client.get_project_client(project_name)

            # Build request body for deployment
            details = CreateDeploymentDetails(trained_model_label=trained_model_label,
            azure_resource_ids=[
                AssignedProjectResource(
                    resource_id="/subscriptions/b72743ec-8bb3-453f-83ad-a53e8a50712e/resourceGroups/language-sdk-rg/providers/Microsoft.CognitiveServices/accounts/sdk-test-02",
                    region="eastus2",
                )
                ],
            )

            # Act: begin deploy and wait for completion
            poller = await project_client.deployment.begin_deploy_project(
                deployment_name=deployment_name,
                body=details,
            )
            try:
                await poller.result()
            except HttpResponseError as e:
                print(f"Operation failed: {e.message}")
                print(e.error)
                raise

            # If we get here, the deploy succeeded
            print(f"Deploy project completed. done={poller.done()} status={poller.status()}")
