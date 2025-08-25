# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential

from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationExportedProjectAsset,
    ConversationExportedIntent,
    ConversationExportedEntity,
    ConversationExportedUtterance,
    ExportedUtteranceEntityLabel,
    ExportedProject,
    ProjectSettings,
    CreateProjectOptions,
    ProjectKind,
    ExportedProjectFormat,
)

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsImportCaseAsync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_import_project_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "PythonImportProject0820"
            project_client = client.get_project_client(project_name)

            # ----- Build assets using objects -----
            intents = [
                ConversationExportedIntent(category="None"),
                ConversationExportedIntent(category="Buy"),
            ]

            entities = [
                ConversationExportedEntity(
                    category="product",
                    composition_mode="combineComponents",
                )
            ]

            u1 = ConversationExportedUtterance(
                text="I want to buy a house",
                intent="Buy",
                language="en-us",
                dataset="Train",
                entities=[ExportedUtteranceEntityLabel(category="product", offset=16, length=5)],
            )

            u2 = ConversationExportedUtterance(
                text="I want to buy surface pro",
                intent="Buy",
                language="en-us",
                dataset="Train",
                entities=[ExportedUtteranceEntityLabel(category="product", offset=14, length=11)],
            )

            u3 = ConversationExportedUtterance(
                text="I want to buy xbox",
                intent="Buy",
                language="en-us",
                dataset="Train",
                entities=[ExportedUtteranceEntityLabel(category="product", offset=14, length=4)],
            )

            assets = ConversationExportedProjectAsset(
                intents=intents,
                entities=entities,
                utterances=[u1, u2, u3],
            )

            metadata = CreateProjectOptions(
                project_kind=ProjectKind.CONVERSATION,
                project_name=project_name,
                language="en-us",
                settings=ProjectSettings(confidence_threshold=0.0),
                multilingual=False,
                description="",
            )

            exported_project = ExportedProject(
                project_file_version="2025-05-15-preview",
                string_index_type="Utf16CodeUnit",
                metadata=metadata,
                assets=assets,
            )

            # ----- Act: begin import (LRO) -----
            poller = await project_client.project.begin_import(
                body=exported_project,
                exported_project_format=ExportedProjectFormat.CONVERSATION,
            )

            # Wait for completion and get the ImportProjectState
            result = await poller.result()

            assert result.status == "succeeded", f"Import failed with status: {result.status}"

            # Optional debug prints
            print(f"Job ID: {result.job_id}")
            print(f"Status: {result.status}")
            print(f"Created on: {result.created_on}")
            print(f"Last updated on: {result.last_updated_on}")
            print(f"Expires on: {result.expires_on}")
            print(f"Warnings: {result.warnings}")
            print(f"Errors: {result.errors}")
        finally:
            await client.close()
