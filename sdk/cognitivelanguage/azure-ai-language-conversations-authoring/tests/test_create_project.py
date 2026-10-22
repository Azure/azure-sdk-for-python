# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    CreateProjectOptions,
    ProjectDetails,
    ProjectKind,
)

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = ConversationAuthoringClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_create_project(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "MyPythonProject1110"

        # Create the project body
        body = CreateProjectOptions(
            project_kind=ProjectKind.CONVERSATION,
            project_name=project_name,
            language="en-us",
            multilingual=True,
            description="Project created for testing via Python SDK",
        )

        # Act
        result = authoring_client.create_project(project_name=project_name, body=body)

        # Assert
        assert isinstance(result, ProjectDetails)
        assert result.project_name == project_name
        print(f"Created project: {result.project_name}, language: {result.language}, kind: {result.project_kind}")
