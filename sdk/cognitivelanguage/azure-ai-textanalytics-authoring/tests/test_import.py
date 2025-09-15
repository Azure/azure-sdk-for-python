# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.core.exceptions import HttpResponseError
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


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAuthoringClient:
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_import(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

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
        poller = project_client.project.begin_import(body=exported_project)

        try:
            poller.result()
        except HttpResponseError as e:
            msg = getattr(getattr(e, "error", None), "message", str(e))
            print(f"Operation failed: {msg}")
            raise

        print(f"Import completed. done={poller.done()} status={poller.status()}")
