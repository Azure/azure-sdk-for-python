# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import CreateDeploymentDetails

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))  # type: ignore[arg-type]


class TestConversationsDeployProjectAsync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_deploy_project_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_name = "single-class-project"
            deployment_name = "deployment0902"
            trained_model_label = "model5"

            project_client = client.get_project_client(project_name)

            # Build request body for deployment
            details = CreateDeploymentDetails(trained_model_label=trained_model_label)

            # Act: begin deploy and wait for completion
            poller = await project_client.deployment.begin_deploy_project(
                deployment_name=deployment_name,
                body=details,
            )
            try:
                await poller.result()
            except HttpResponseError as e:
                msg = getattr(getattr(e, "error", None), "message", str(e))
                print(f"Operation failed: {msg}")
                raise

            # If we get here, the deploy succeeded
            print(f"Deploy project completed. done={poller.done()} status={poller.status()}")
