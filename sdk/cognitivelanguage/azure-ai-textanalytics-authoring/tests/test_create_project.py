# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CreateProjectOptions,
    ProjectDetails,
    ProjectKind,
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
    def test_create_project(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "MyTextProject0902"

        # Arrange
        body = CreateProjectOptions(
            project_kind=ProjectKind.CUSTOM_MULTI_LABEL_CLASSIFICATION,
            storage_input_container_name="multi-class-example",
            project_name=project_name,
            language="en",
            description="Project description for a Custom Entity Recognition project",
            multilingual=True,
        )

        # Act
        result = authoring_client.create_project(project_name=project_name, body=body)

        # Assert
        assert isinstance(result, ProjectDetails)
        assert result.project_name == project_name
        print(f"Created project: {result.project_name}, language: {result.language}, kind: {result.project_kind}")
