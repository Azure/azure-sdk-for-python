# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import DeploymentState

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))

@pytest.mark.playback_test_only
class TestConversationsDeleteDeploymentSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_delete_deployment(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "single-class-project"
        deployment_name = "deployment0902"

        project_client = client.get_project_client(project_name)

        # Act: begin delete and wait for completion
        poller = project_client.deployment.begin_delete_deployment(deployment_name=deployment_name)

        try:
            poller.result()
        except HttpResponseError as e:
            msg = getattr(getattr(e, "error", None), "message", str(e))
            print(f"Operation failed: {msg}")
            raise

        # If we get here, the delete succeeded
        print(f"Delete completed. done={poller.done()} status={poller.status()}")
