# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import CreateDeploymentDetails, AssignedProjectResource

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

class TestConversationsDeleteDeploymentSync(TestConversations):

    @ConversationsPreparer()
    @recorded_by_proxy
    def test_deploy_project(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "Test-data-labels"
        deployment_name = "deployment1"
        trained_model_label = "MyModel"

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
        poller = project_client.deployment.begin_deploy_project(
            deployment_name=deployment_name,
            body=details,
        )
        try:
            poller.result()
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)
            raise

        # If we get here, the deploy succeeded
        print(f"Deploy project completed. done={poller.done()} status={poller.status()}")

    @ConversationsPreparer()
    @recorded_by_proxy
    def test_delete_deployment(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "Test-data-labels"
        deployment_name = "deployment1"

        project_client = client.get_project_client(project_name)

        # Act: begin delete and wait for completion
        poller = project_client.deployment.begin_delete_deployment(deployment_name=deployment_name)

        try:
            poller.result()
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)
            raise

        # If we get here, the delete succeeded
        print(f"Delete completed. done={poller.done()} status={poller.status()}")
