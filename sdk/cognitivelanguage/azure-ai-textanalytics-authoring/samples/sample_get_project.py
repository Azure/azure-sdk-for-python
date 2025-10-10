# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_project.py
DESCRIPTION:
    This sample demonstrates how to get a **Text Authoring** project and print its details.
USAGE:
    python sample_get_project.py
REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
OPTIONAL ENV VARS:
    PROJECT_NAME  # defaults to "<project-name>"
"""

# [START text_authoring_get_project]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient


def sample_get_project():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # get project
    result = client.get_project(project_name)

    # print project details (direct attribute access; no getattr)
    print("=== Project Details ===")
    print(f"  name: {result.project_name}")
    print(f"  language: {result.language}")
    print(f"  created: {result.created_on}")
    print(f"  last modified: {result.last_modified_on}")
    print(f"  storage container: {result.storage_input_container_name}")


# [END text_authoring_get_project]


def main():
    sample_get_project()


if __name__ == "__main__":
    main()
