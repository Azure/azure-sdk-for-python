# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_project.py
DESCRIPTION:
    This sample demonstrates how to create a project.
USAGE:
    python sample_create_project.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_AUTHORING_ENDPOINT             - endpoint for your Text Analysis resource.
    2) AZURE_TEXT_AUTHORING_KEY                  - API key for your Text Analysis resource.
    3) AZURE_TEXT_AUTHORING_STORAGE              - storage container for the project to be created in
"""
def sample_create_project():
    from azure.ai.language.text.authoring import TextAuthoringClient
    from azure.core.credentials import AzureKeyCredential
    import os

    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_TEXT_AUTHORING_KEY"]
    storageContainer = os.environ["AZURE_TEXT_AUTHORING_STORAGE"]

    client = TextAuthoringClient(endpoint, AzureKeyCredential(key)).text_analysis_authoring

    project_name = "Project_Name"
    project_body = {
        "projectName": project_name,
        "language": "en",
        "projectKind": "customSingleLabelClassification",
        "description": "Test Project",
        "multilingual": "True",
        "storageInputContainerName": storageContainer
    }
    client.create_project(project_name, project_body)

    created_projects = client.list_projects()
    created_projects_names = map(lambda project: project["projectName"], created_projects)
    if(project_name in created_projects_names):
        print("The project is created successfully")
    else:
        print("An error has occured")

if(__name__ == "__main__"):
    sample_create_project()