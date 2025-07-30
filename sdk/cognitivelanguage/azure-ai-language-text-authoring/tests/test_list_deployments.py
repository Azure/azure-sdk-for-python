# pylint: disable=line-too-long,useless-suppression
import functools
from urllib import response
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.text.authoring import TextAuthoringClient
from azure.ai.language.text.authoring.models import (
    TextAuthoringProjectDeployment
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
    def test_list_deployments(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "single-class-project"  # Replace with actual project name that has deployments
        deployments = client.list_deployments(project_name)

        assert deployments is not None

        for deployment in deployments:
            assert isinstance(deployment, TextAuthoringProjectDeployment)
            assert deployment.deployment_name is not None
            print(f"Deployment: {deployment.deployment_name}, model: {deployment.model_id}")