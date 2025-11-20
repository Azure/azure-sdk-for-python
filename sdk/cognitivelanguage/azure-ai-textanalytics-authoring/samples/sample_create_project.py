# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_project.py
DESCRIPTION:
    This sample demonstrates how to create a **Text Authoring** project.
USAGE:
    python sample_create_project.py
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
    PROJECT_NAME                  # defaults to "<project-name>"
    LANGUAGE_TAG                  # defaults to "<language-tag>"
    STORAGE_INPUT_CONTAINER_NAME  # defaults to "<storage-container-name>"
    DESCRIPTION                   # defaults to "<description>"
"""

# [START text_authoring_create_project]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CreateProjectOptions,
    ProjectKind,
)


def sample_text_create_project():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    language_tag = os.environ.get("LANGUAGE_TAG", "<language-tag>")  # e.g., "en"
    storage_container = os.environ.get("STORAGE_INPUT_CONTAINER_NAME", "<storage-container-name>")
    description = os.environ.get("DESCRIPTION", "<description>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # build project definition (Custom Multi-Label Classification)
    body = CreateProjectOptions(
        project_kind=ProjectKind.CUSTOM_MULTI_LABEL_CLASSIFICATION,
        storage_input_container_name=storage_container,
        project_name=project_name,
        language=language_tag,
        description=description,
        multilingual=True,
    )

    # create project
    result = client.create_project(project_name=project_name, body=body)

    # print project details (direct attribute access; no getattr)
    print("=== Create Text Authoring Project Result ===")
    print(f"Project Name: {result.project_name}")
    print(f"Language: {result.language}")
    print(f"Kind: {result.project_kind}")
    print(f"Multilingual: {result.multilingual}")
    print(f"Description: {result.description}")
    print(f"Storage Input Container: {result.storage_input_container_name}")


# [END text_authoring_create_project]


def main():
    sample_text_create_project()


if __name__ == "__main__":
    main()
