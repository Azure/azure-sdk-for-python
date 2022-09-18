# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_import_project.py
DESCRIPTION:
    This sample demonstrates how to import a project, using a dummy project provided at https://docs.microsoft.com/en-us/rest/api/language/text-analysis-authoring/import?tabs=HTTP.
USAGE:
    python sample_import_project.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_AUTHORING_ENDPOINT             - endpoint for your Text Analysis resource.
    2) AZURE_TEXT_AUTHORING_KEY                  - API key for your Text Analysis resource.
    3) AZURE_TEXT_AUTHORING_STORAGE              - name of the storage container for the project to be imported into
"""
from multiprocessing import dummy
from random import sample


def sample_import_project():
    from azure.ai.textanalytics.authoring import TextAuthoringClient
    from azure.core.credentials import AzureKeyCredential
    import os
    import json

    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_TEXT_AUTHORING_KEY"]
    storage_container = os.environ["AZURE_TEXT_AUTHORING_STORAGE"]

    client = TextAuthoringClient(endpoint, AzureKeyCredential(key))

    sample_project = json.load(open("sample_project.json"))
    sample_project["metadata"]["storageInputContainerName"] = storage_container
    poller = client.begin_import_project("LoanAgreements", sample_project)
    result = poller.result()
    
    if result["status"] == "succeeded":
        print("The project is imported successfully")
    else:
        print("An error has occured")


if __name__ == "__main__":
    sample_import_project()