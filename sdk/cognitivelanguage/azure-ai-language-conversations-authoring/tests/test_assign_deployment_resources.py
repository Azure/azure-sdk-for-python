# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ResourceMetadata,
    AssignDeploymentResourcesDetails,
    DeploymentResourcesState,
)
from azure.identity import DefaultAzureCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)

class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = DefaultAzureCredential()
        return ConversationAuthoringClient(endpoint=endpoint, credential=credential)

class TestConversationsAssignDeploymentResourcesLROSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_assign_deployment_resources_lro(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint)
        project_name = "EmailApp"
        project_client = client.get_project_client(project_name)

        # Build request body
        resource = ResourceMetadata(
            azure_resource_id="/subscriptions/b72743ec-8bb3-453f-83ad-a53e8a50712e/resourceGroups/language-sdk-rg/providers/Microsoft.CognitiveServices/accounts/sdk-test-02",
            custom_domain="sdk-test-02",
            region="eastus2",
        )
        details = AssignDeploymentResourcesDetails(metadata=[resource])

        # Act: begin assign and wait for completion
        poller = project_client.project.begin_assign_deployment_resources(body=details)
        result: DeploymentResourcesState = poller.result()

        # Assert + print LRO state
        assert result.status == "succeeded", f"Assign resources failed with status: {result.status}"
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")
