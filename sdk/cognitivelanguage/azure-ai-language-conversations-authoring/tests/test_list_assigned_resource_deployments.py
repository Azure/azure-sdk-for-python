# pylint: disable=line-too-long,useless-suppression
from datetime import date, datetime
import functools
from importlib import resources

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
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


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsDeployProjectSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_list_assigned_resource_deployments(self, authoring_endpoint, authoring_key):
        # Arrange
        client = self.create_client(authoring_endpoint, authoring_key)
        paged = client.list_assigned_resource_deployments()

        # Assert
        for meta in paged:
            assert isinstance(meta, AssignedProjectDeploymentsMetadata)
            assert isinstance(meta.project_name, str) and meta.project_name
            assert isinstance(meta.deployments_metadata, list)

            for d in meta.deployments_metadata:
                assert isinstance(d, AssignedProjectDeploymentMetadata)
                assert isinstance(d.deployment_name, str) and d.deployment_name
                assert isinstance(d.last_deployed_on, datetime)
                assert isinstance(d.deployment_expires_on, date)
