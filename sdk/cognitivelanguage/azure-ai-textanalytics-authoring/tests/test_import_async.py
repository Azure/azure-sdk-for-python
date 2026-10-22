# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CreateProjectOptions,
    ExportedProject,
    ProjectSettings,
    ExportedCustomSingleLabelClassificationProjectAsset,
    ExportedCustomSingleLabelClassificationDocument,
    ExportedDocumentClass,
    ExportedClass,
    ProjectKind,
    StringIndexType,
)

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsCaseAsync(AzureRecordedTestCase):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_import_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_name = "MyImportTextProject0902"
            project_client = client.get_project_client(project_name)

            # Arrange - metadata
            project_metadata = CreateProjectOptions(
                project_kind=ProjectKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION,
                storage_input_container_name="single-class-example",
                project_name=project_name,
                language="en",
                description=(
                    "This is a sample dataset provided by the Azure Language service team to help users get "
                    "started with Custom named entity recognition. The provided sample dataset contains 20 loan "
                    "agreements drawn up between two entities."
                ),
                multilingual=False,
                settings=ProjectSettings(),
            )

            # Arrange - assets
            project_assets = ExportedCustomSingleLabelClassificationProjectAsset(
                classes=[
                    ExportedClass(category="Date"),
                    ExportedClass(category="LenderName"),
                    ExportedClass(category="LenderAddress"),
                ],
                documents=[
                    ExportedCustomSingleLabelClassificationDocument(
                        document_class=ExportedDocumentClass(category="Date"),
                        location="01.txt",
                        language="en",
                    ),
                    ExportedCustomSingleLabelClassificationDocument(
                        document_class=ExportedDocumentClass(category="LenderName"),
                        location="02.txt",
                        language="en",
                    ),
                ],
            )

            exported_project = ExportedProject(
                project_file_version="2022-05-01",
                string_index_type=StringIndexType.UTF16_CODE_UNIT,
                metadata=project_metadata,
                assets=project_assets,
            )

            # Act - long-running import
            poller = await project_client.project.begin_import(body=exported_project)

            try:
                await poller.result()
            except HttpResponseError as e:
                msg = getattr(getattr(e, "error", None), "message", str(e))
                print(f"Operation failed: {msg}")
                raise

            print(f"Import completed. done={poller.done()} status={poller.status()}")
