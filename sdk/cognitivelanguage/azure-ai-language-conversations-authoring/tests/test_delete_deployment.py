# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import DeploymentState

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
    def test_delete_deployment(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "Test-data-labels"
        deployment_name = "deployment2"

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
