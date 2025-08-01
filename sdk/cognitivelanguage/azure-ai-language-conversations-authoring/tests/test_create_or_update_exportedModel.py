# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationAuthoringExportedModelDetails
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
    def test_begin_create_or_update_exported_model(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "Test-data-labels"
        exported_model_name = "model-label"
        exported_model_client = client.get_exported_model_client(project_name, exported_model_name)

        body = ConversationAuthoringExportedModelDetails(
            trained_model_label="MyModel"
        )

        poller = exported_model_client.begin_create_or_update_exported_model(body=body)
        result = poller.result()

        assert result is None  # Since return type is LROPoller[None]
        assert poller.done()
