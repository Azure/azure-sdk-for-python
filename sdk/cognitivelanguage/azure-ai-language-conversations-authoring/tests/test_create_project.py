# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationAuthoringCreateProjectDetails,
    ConversationAuthoringProjectMetadata,
    ConversationAuthoringProjectKind,
)

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="fake_resource.servicebus.windows.net/",
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
        project_name = "MyPythonProject0802"

        # Create the project body
        body = ConversationAuthoringCreateProjectDetails(
            project_kind=ConversationAuthoringProjectKind.CONVERSATION,
            project_name=project_name,
            language="en-us",
            multilingual=True,
            description="Project created for testing via Python SDK",
        )

        # Act
        result = authoring_client.create_project(project_name=project_name, body=body)

        # Assert
        assert isinstance(result, ConversationAuthoringProjectMetadata)
        assert result.project_name == project_name
        print(f"Created project: {result.project_name}, language: {result.language}, kind: {result.project_kind}")
