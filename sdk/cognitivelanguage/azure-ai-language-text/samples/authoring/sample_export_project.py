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
    3) AZURE_TEXT_AUTHORING_STORAGE              - storage container for the project to be exported from
"""
def sample_export_project():
    from azure.ai.language.text.authoring import TextAuthoringClient
    from azure.core.credentials import AzureKeyCredential
    import os

    endpoint = os.environ["AZURE_TEXT_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_TEXT_AUTHORING_KEY"]
    storageContainer = os.environ["AZURE_TEXT_AUTHORING_STORAGE"]

    client = TextAuthoringClient(endpoint, AzureKeyCredential(key)).text_analysis_authoring

    project_name = "Project_Name"
    client.begin_export(project_name, string_index_type="Utf16CodeUnit")

    

if(__name__ == "__main__"):
    sample_export_project()