# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ExportedProjectFormat,
)

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsExportCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_export_project(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "PythonImportProject0820"
        project_client = authoring_client.get_project_client(project_name)

        # Act: begin export (LRO)
        poller = project_client.project.begin_export(
            string_index_type="Utf16CodeUnit",
            exported_project_format=ExportedProjectFormat.CONVERSATION,
        )

        try:
            poller.result()  # completes with None; raises on failure
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)
            raise

        # Success -> poller completed
        print(f"Export completed. done={poller.done()} status={poller.status()}")
