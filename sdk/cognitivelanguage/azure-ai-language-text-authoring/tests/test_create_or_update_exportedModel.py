# pylint: disable=line-too-long,useless-suppression
import functools
from urllib import response
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.text.authoring import TextAuthoringClient
from azure.ai.language.text.authoring.models import (
    TextAuthoringExportedModelDetails
)
from azure.core.credentials import AzureKeyCredential

TextPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="fake_resource.servicebus.windows.net/",
    authoring_key="fake_key",
)

class TestText(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = TextAuthoringClient(endpoint, credential)
        return client

    ...

class TestTextCase(TestText):
    @TextPreparer()
    @recorded_by_proxy
    def test_begin_create_or_update_exported_model(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "multi-class-project"
        exported_model_name = "exportedModel"
        exported_model_client = client.get_exported_model_client(project_name, exported_model_name)

        body = TextAuthoringExportedModelDetails(
            trained_model_label="model1"
        )

        poller = exported_model_client.begin_create_or_update_exported_model(body=body)
        result = poller.result()

        assert result is None  # Since return type is LROPoller[None]
        assert poller.done()