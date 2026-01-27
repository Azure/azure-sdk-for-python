# ---------- SYNC ----------

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


class TestConversationsDeleteProjectSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_delete_project(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "MyPythonProject0820"

        # Act: begin delete (LRO)
        poller = authoring_client.begin_delete_project(project_name)

        try:
            poller.result()
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)
            raise

        # If we get here, the delete succeeded
        print(f"Delete completed. done={poller.done()} status={poller.status()}")
