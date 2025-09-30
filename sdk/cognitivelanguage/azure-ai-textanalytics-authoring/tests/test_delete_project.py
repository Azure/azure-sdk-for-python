# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAuthoringClient:
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_delete_project(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "MyImportTextProjectRaw0723"

        # Act: begin delete (LRO)
        poller = client.begin_delete_project(project_name)

        try:
            poller.result()
        except HttpResponseError as e:
            msg = getattr(getattr(e, "error", None), "message", str(e))
            print(f"Operation failed: {msg}")
            raise

        # If we get here, the delete succeeded
        print(f"Delete completed. done={poller.done()} status={poller.status()}")
