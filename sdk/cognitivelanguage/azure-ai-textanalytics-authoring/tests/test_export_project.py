# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import StringIndexType

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
    def test_export_project(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "single-class-project"
        project_client = client.get_project_client(project_name)

        # Act – LRO export
        poller = project_client.project.begin_export(
            string_index_type=StringIndexType.UTF16_CODE_UNIT,
        )

        try:
            poller.result()  # completes with None; raises on failure
        except HttpResponseError as e:
            msg = getattr(getattr(e, "error", None), "message", str(e))
            print(f"Operation failed: {msg}")
            raise

        # Success -> poller completed
        print(f"Export completed. done={poller.done()} status={poller.status()}")
