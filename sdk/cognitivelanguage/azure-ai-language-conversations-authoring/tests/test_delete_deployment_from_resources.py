# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ProjectResourceIds

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
    def test_delete_deployment_from_resources(self, authoring_endpoint, authoring_key):
        # Arrange
        client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "EmailApp"
        deployment_name = "deploysdk2"
        project_client = client.get_project_client(project_name)

        # Create request body with the resource IDs to unassign/delete from
        delete_body = ProjectResourceIds(
            azure_resource_ids=[
                "/subscriptions/b72743ec-8bb3-453f-83ad-a53e8a50712e/resourceGroups/language-sdk-rg/providers/Microsoft.CognitiveServices/accounts/sdk-test-02"
            ]
        )

        # Act: begin delete and wait for completion
        poller = project_client.deployment.begin_delete_deployment_from_resources(
            deployment_name=deployment_name, body=delete_body
        )

        try:
            poller.result()
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)
            raise

        # Assert completion
        print(f"Delete completed. done={poller.done()} status={poller.status()}")
