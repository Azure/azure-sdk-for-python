# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
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


class TestConversationsCaseAsync(AzureRecordedTestCase):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_create_project_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as authoring_client:
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
            result = await authoring_client.create_project(project_name=project_name, body=body)

            # Assert
            assert isinstance(result, ProjectDetails)
            assert result.project_name == project_name
            print(f"Created project: {result.project_name}, language: {result.language}, kind: {result.project_kind}")
