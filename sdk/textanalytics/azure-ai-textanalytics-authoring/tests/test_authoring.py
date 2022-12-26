# pre-apply the client_cls positional argument so it needn't be explicitly passed below
import functools
import json
import os

from devtools_testutils import recorded_by_proxy
import pytest
from testcase import TextAnalyticsTest, TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from azure.ai.textanalytics.authoring import TextAuthoringClient

TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAuthoringClient)

class TestAuthoring(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_create_project(self, client):
        storage_container = os.environ["AZURE_TEXT_AUTHORING_STORAGE"]
        project_name = "Project_Name"
        project_body = {
            "projectName": project_name,
            "language": "en",
            "projectKind": "customSingleLabelClassification",
            "description": "Test Project",
            "multilingual": True,
            "storageInputContainerName": storage_container
        }

        successfully_created = False
        client.create_project(project_name, project_body)
        for project in client.list_projects():
            if project["projectName"] == project_name:
                successfully_created = True

        assert successfully_created


    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_delete_project(self, client):
        storage_container = os.environ["AZURE_TEXT_AUTHORING_STORAGE"]
        project_name = "Project_Name"
        project_body = {
            "projectName": project_name,
            "language": "en",
            "projectKind": "customSingleLabelClassification",
            "description": "Test Project",
            "multilingual": True,
            "storageInputContainerName": storage_container
        }

        successfully_created = False
        client.create_project(project_name, project_body)
        for project in client.list_projects():
            if project["projectName"] == project_name:
                successfully_created = True

        poller = client.begin_delete_project(project_name)
        result = poller.result()
        successfully_deleted = True

        for project in client.list_projects():
            if project["projectName"] == project_name:
                successfully_deleted = False

        assert successfully_created and successfully_deleted
        
    
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_export_project(self, client):
        project_name = "Project_Name"
        poller = client.begin_export_project(project_name, string_index_type="Utf16CodeUnit")
        result = poller.result()

        assert result["status"] == "succeeded"

    
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_import_project(self, client):
        storage_container = os.environ["AZURE_TEXT_AUTHORING_STORAGE"]
        sample_project = json.load(open("./samples/sample_project.json"))
        sample_project["metadata"]["storageInputContainerName"] = storage_container
        poller = client.begin_import_project("LoanAgreements", sample_project)
        result = poller.result()
        
        assert result["status"] == "succeeded"
    

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_train_project(self, client):
        sample_project = json.load(open("./samples/sample_project.json"))
        project_name = "Emails"
        training_parameters = {
            "modelLabel": "model1",
            "trainingConfigVersion": "latest",
            "evaluationOptions": {
                "kind": "percentage",
                "testingSplitPercentage": 20,
                "trainingSplitPercentage": 80
            }
        }
        
        poller = client.begin_train(project_name, training_parameters)
        result = poller.result()
        
        assert result["status"] == "succeeded"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_deploy_project(self, client):
        project_name = "Emails"
        deployment_name = "Deployment_Name"
        deployment_label = {
            "trainedModelLabel": "v2"
        }

        poller = client.begin_deploy_project(project_name, deployment_name, deployment_label)
        result = poller.result()