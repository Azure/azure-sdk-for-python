# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_train_project.py
DESCRIPTION:
    This sample demonstrates how to train a dummy project provided at https://docs.microsoft.com/en-us/rest/api/language/text-analysis-authoring/import?tabs=HTTP.
    You have to first import the dummy project by running sample_import_project.py, or create a project of your own.
USAGE:
    python sample_train_project.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_AUTHORING_ENDPOINT             - endpoint for your Text Analysis resource.
    2) AZURE_TEXT_AUTHORING_KEY                  - API key for your Text Analysis resource.
"""
def sample_train_project():
    from azure.ai.textanalytics.authoring import TextAuthoringClient
    from azure.core.credentials import AzureKeyCredential
    from samples.authoring.dummy_project import dummy_project
    import os

    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_TEXT_AUTHORING_KEY"]

    client = TextAuthoringClient(endpoint, AzureKeyCredential(key))

    project_name = dummy_project["metadata"]["projectName"]
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
    
    if result["result"]["trainingStatus"]["status"] == "succeeded":
        print("The project is trained successfully")
    else:
        print("An error has occured")


if __name__ == "__main__":
    sample_train_project()