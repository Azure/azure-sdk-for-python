# ---------- SYNC ----------

import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ProjectDeletionState  # optional (type hint only)

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
        project_name = "PythonImportProject082001"

        # Act: begin delete (LRO)
        poller = authoring_client.begin_delete_project(project_name)

        # Wait for completion and get the ProjectDeletionState
        result = poller.result()

        assert result.status == "succeeded", f"Deletion failed with status: {result.status}"
        # Print details of the ProjectDeletionState
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")
