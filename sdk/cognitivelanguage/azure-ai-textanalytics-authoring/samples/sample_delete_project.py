# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_project.py
DESCRIPTION:
    This sample demonstrates how to delete a **Text Authoring** project.
USAGE:
    python sample_delete_project.py
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

# [START text_authoring_delete_project]
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient


def sample_delete_project():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # delete the project (LRO)
    poller = client.begin_delete_project(project_name)

    # handle success/error from the LRO
    try:
        poller.result()  # completes with None; raises on failure
        print("Delete completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)


# [END text_authoring_delete_project]


def main():
    sample_delete_project()


if __name__ == "__main__":
    main()
