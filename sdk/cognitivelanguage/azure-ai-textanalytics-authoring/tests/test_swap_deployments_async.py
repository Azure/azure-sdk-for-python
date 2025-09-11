# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    SwapDeploymentsDetails,
)

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsSwapDeploymentsAsync(AzureRecordedTestCase):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_swap_deployments_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as authoring_client:
            project_name = "single-class-project"
            deployment_name_1 = "deployment1"
            deployment_name_2 = "deployment0902"

            project_client = authoring_client.get_project_client(project_name)

            details = SwapDeploymentsDetails(
                first_deployment_name=deployment_name_1,
                second_deployment_name=deployment_name_2,
            )

            # Act: begin swap and wait for completion
            poller = await project_client.project.begin_swap_deployments(body=details)
            try:
                await poller.result()  # completes with None; raises on failure
            except HttpResponseError as e:
                msg = getattr(getattr(e, "error", None), "message", str(e))
                print(f"Operation failed: {msg}")
                raise

            # Success -> poller completed
            print(f"Swap deployments completed. done={poller.done()} status={poller.status()}")
