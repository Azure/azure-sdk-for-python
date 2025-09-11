# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import ProjectDetails

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
    async def test_get_project_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_name = "single-class-project"
            # Act
            result = await client.get_project(project_name)

            # Assert
            assert isinstance(result, ProjectDetails)
            assert result.project_name == project_name
            assert result.language is not None
            assert result.created_on is not None
            assert result.last_modified_on is not None
            assert result.storage_input_container_name is not None

            print("Project details:")
            print(f"  name: {result.project_name}")
            print(f"  language: {result.language}")
            print(f"  created: {result.created_on}")
            print(f"  last modified: {result.last_modified_on}")
            print(f"  storage container: {result.storage_input_container_name}")
