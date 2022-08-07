# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_project.py
DESCRIPTION:
    This sample demonstrates how to delete a project.
USAGE:
    python sample_delete_project.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_AUTHORING_ENDPOINT             - endpoint for your Text Analysis resource.
    2) AZURE_TEXT_AUTHORING_KEY                  - API key for your Text Analysis resource.
"""
def sample_delete_project():
    from azure.ai.language.text.authoring import TextAuthoringClient
    from azure.core.credentials import AzureKeyCredential
    import os

    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_TEXT_AUTHORING_KEY"]

    client = TextAuthoringClient(endpoint, AzureKeyCredential(key)).text_analysis_authoring

    project_name = "Project_Name"
    created_projects = client.list_projects()
    created_projects_names = map(lambda project: project["projectName"], created_projects)
    if(project_name not in created_projects_names):
        print("The project cannot be deleted because no such project exists")
        return
    
    poller = client.begin_delete_project(project_name)
    poller.result()     #Waits for the project to get deleted

    created_projects = client.list_projects()
    created_projects_names = map(lambda project: project["projectName"], created_projects)
    if(project_name not in created_projects_names):
        print("The project is deleted successfully")
    else:
        print("An error has occured")

if(__name__ == "__main__"):
    sample_delete_project()