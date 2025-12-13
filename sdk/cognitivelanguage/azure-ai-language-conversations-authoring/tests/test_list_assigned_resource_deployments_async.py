import functools
import pytest
from datetime import date, datetime

from devtools_testutils import EnvironmentVariableLoader, AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    AssignedProjectDeploymentsMetadata,
    AssignedProjectDeploymentMetadata,
)

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsAsync(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsDeployProjectAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_list_assigned_resource_deployments_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        async with client:
            # Act
            paged = client.list_assigned_resource_deployments()

            # Assert
            async for meta in paged:
                assert isinstance(meta, AssignedProjectDeploymentsMetadata)
                assert isinstance(meta.project_name, str) and meta.project_name
                assert isinstance(meta.deployments_metadata, list)

                for d in meta.deployments_metadata:
                    assert isinstance(d, AssignedProjectDeploymentMetadata)
                    assert isinstance(d.deployment_name, str) and d.deployment_name
                    assert isinstance(d.last_deployed_on, datetime)
                    assert isinstance(d.deployment_expires_on, date)
