# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_export_project.py
DESCRIPTION:
    This sample demonstrates how to export a project.
USAGE:
    python sample_export_project.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_AUTHORING_ENDPOINT             - endpoint for your Text Analysis resource.
    2) AZURE_TEXT_AUTHORING_KEY                  - API key for your Text Analysis resource.
"""
def sample_export_project():
    from azure.ai.textanalytics.authoring import TextAuthoringClient
    from azure.core.credentials import AzureKeyCredential
    import os

    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_TEXT_AUTHORING_KEY"]

    client = TextAuthoringClient(endpoint, AzureKeyCredential(key))

    project_name = "Project_Name"
    poller = client.begin_export_project(project_name, string_index_type="Utf16CodeUnit")
    result = poller.result()

    if result["status"] == "succeeded":
        export_url = result["resultUrl"]
        print("The project is exported at: " + export_url)
    else:
        print("An error has occured")

if __name__ == "__main__":
    sample_export_project()