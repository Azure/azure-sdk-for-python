# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import LoadSnapshotState

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
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
        result: LoadSnapshotState = poller.result()

        # Print properties from the LRO result (LoadSnapshotState)
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")
