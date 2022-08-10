# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_deploy_project.py
DESCRIPTION:
    This sample demonstrates how to deploy a project.
USAGE:
    python sample_deploy_project.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_AUTHORING_ENDPOINT             - endpoint for your Text Analysis resource.
    2) AZURE_TEXT_AUTHORING_KEY                  - API key for your Text Analysis resource.
"""
def sample_deploy_project():
    from azure.ai.textanalytics.authoring import TextAuthoringClient
    from azure.core.credentials import AzureKeyCredential
    from samples.authoring.dummy_project import dummy_project
    import os

    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_TEXT_AUTHORING_KEY"]

    client = TextAuthoringClient(endpoint, AzureKeyCredential(key))

    project_name = "Project_Name"
    deployment_name = "Deployment_Name"
    deployment_label = {
        "trainedModelLabel": "model1"
    }

    poller = client.begin_deploy_project(project_name, deployment_name, deployment_label)
    result = poller.result()
    print(result)

if __name__ == "__main__":
    sample_deploy_project()