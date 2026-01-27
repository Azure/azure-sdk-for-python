# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
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

    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        credential = AzureKeyCredential(key)
        return ConversationAuthoringClient(endpoint, credential)


class TestConversationsCaseAsync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_create_project_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        project_name = "MyPythonProject1110Async"

        # Create the project body
        body = CreateProjectOptions(
            project_kind=ProjectKind.CONVERSATION,
            project_name=project_name,
            language="en-us",
            multilingual=True,
            description="Project created for testing via Python SDK",
        )

        result = await client.create_project(project_name=project_name, body=body)

        # Assert
        assert isinstance(result, ProjectDetails)
        assert result.project_name == project_name
        print(f"Created project: {result.project_name}, language: {result.language}, kind: {result.project_kind}")
