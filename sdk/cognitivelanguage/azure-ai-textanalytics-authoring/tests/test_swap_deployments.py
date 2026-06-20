# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    SwapDeploymentsDetails,
)

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsSwapDeploymentsSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_swap_deployments(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "single-class-project"
        deployment_name_1 = "deployment1"
        deployment_name_2 = "deployment0902"

        project_client = authoring_client.get_project_client(project_name)

        details = SwapDeploymentsDetails(
            first_deployment_name=deployment_name_1,
            second_deployment_name=deployment_name_2,
        )

        # Act: begin swap and wait for completion
        poller = project_client.project.begin_swap_deployments(body=details)
        try:
            poller.result()  # completes with None; raises on failure
        except HttpResponseError as e:
            msg = getattr(getattr(e, "error", None), "message", str(e))
            print(f"Operation failed: {msg}")
            raise

        # Success -> poller completed
        print(f"Swap deployments completed. done={poller.done()} status={poller.status()}")
