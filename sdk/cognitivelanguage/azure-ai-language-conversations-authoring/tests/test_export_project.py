# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ExportedProjectFormat,
)

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
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

        # Wait for completion and get the ExportProjectState
        result = poller.result()

        assert result.status == "succeeded", f"Export failed with status: {result.status}"
        # Print details of the ExportProjectState
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")
