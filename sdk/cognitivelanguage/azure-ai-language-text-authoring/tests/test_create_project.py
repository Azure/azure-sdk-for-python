# pylint: disable=line-too-long,useless-suppression
import functools
from urllib import response
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.text.authoring import AuthoringClient 
from azure.ai.language.text.authoring.models import TextAuthoringCreateProjectDetails 
from azure.core.credentials import AzureKeyCredential

TextPreparer = functools.partial(
    PowerShellPreparer,
    "text",
    conversations_endpoint="fake_resource.servicebus.windows.net/",
    conversations_key="fake_key",
)


class TestText(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = AuthoringClient(endpoint, credential)
        return client

    ...


class TestTextCase(TestText):
    @TextPreparer()
    @recorded_by_proxy
    def test_create_project(self, conversations_endpoint, conversations_key):
        client = self.create_client(conversations_endpoint, conversations_key)

        # Access the project operation group 
        project_client = client.text_authoring_project

        # Define project name and creation parameters 

        project_name = "MyPythonTextProject0724" 
        project_data = TextAuthoringCreateProjectDetails( 
            project_kind="customMultiLabelClassification", 
            language="en", 
            storage_input_container_name="test-data", 
            project_name=project_name,
            multilingual=True,
            description="Project description for a Custom Entity Recognition project"
        )

        # Create the project 
        response = project_client.create_project( 
            project_name=project_name, 
            body=project_data 
        ) 

        # Print confirmation 
        print(f"Project created: {response.project_name}, Kind: {response.project_kind}, Language: {response.language}") 