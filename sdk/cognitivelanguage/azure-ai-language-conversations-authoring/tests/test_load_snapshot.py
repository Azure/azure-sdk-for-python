# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsLoadSnapshotPrintResultSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_load_snapshot(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "EmailApp"
        trained_model_label = "Model1"

        project_client = client.get_project_client(project_name)

        # Start LRO and wait for completion
        poller = project_client.trained_model.begin_load_snapshot(trained_model_label)
        try:
            poller.result()  # completes with None; raises on failure
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)
            raise

        # Success -> poller completed
        print(f"Load snapshot completed. done={poller.done()} status={poller.status()}")
