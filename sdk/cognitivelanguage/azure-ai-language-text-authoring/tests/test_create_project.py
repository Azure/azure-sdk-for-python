# pylint: disable=line-too-long,useless-suppression
import functools
from urllib import response
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.text.authoring import TextAuthoringClient
from azure.ai.language.text.authoring.models import (
    TextAuthoringCreateProjectDetails,
    TextAuthoringProjectMetadata,
    TextAuthoringProjectKind
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
    def test_create_project(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "MyTextPythonProject0728"
        project_client = client.get_project_client(project_name)
        
        # Create the project body
        body = TextAuthoringCreateProjectDetails(
            project_kind=TextAuthoringProjectKind.CUSTOM_MULTI_LABEL_CLASSIFICATION,
            language="en",
            storage_input_container_name="multi-class-example",
            multilingual=True,
            description="Project description for a Custom Entity Recognition project",
        )

        # Create the project
        result = project_client.create_project(body=body)

        # Assert
        assert isinstance(result, TextAuthoringProjectMetadata)
        assert result.project_name == project_name
        print(f"Created project: {result.project_name}, language: {result.language}, kind: {result.project_kind}")
