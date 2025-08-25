# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    SwapDeploymentsDetails,
    SwapDeploymentsState,
)  # adjust if your SDK names differ

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsSwapDeploymentsSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_swap_deployments(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "EmailApp"
        deployment_name_1 = "staging"
        deployment_name_2 = "production"

        project_client = authoring_client.get_project_client(project_name)

        details = SwapDeploymentsDetails(
            first_deployment_name=deployment_name_1,
            second_deployment_name=deployment_name_2,
        )

        # Act: begin swap and wait for completion
        poller = project_client.project.begin_swap_deployments(body=details)
        result: SwapDeploymentsState = poller.result()

        # Assert + print LRO state
        assert result.status == "succeeded", f"Swap failed with status: {result.status}"
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")
