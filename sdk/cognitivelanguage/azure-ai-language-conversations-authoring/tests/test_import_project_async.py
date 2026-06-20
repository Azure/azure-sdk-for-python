# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
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
    EnvironmentVariableLoader,
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
        async with client:
            project_name = "PythonImportProject1113"
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

            try:
                await poller.result()
            except HttpResponseError as e:
                print(f"Operation failed: {e.message}")
                print(e.error)
                raise

            print(f"Import completed. done={poller.done()} status={poller.status()}")
