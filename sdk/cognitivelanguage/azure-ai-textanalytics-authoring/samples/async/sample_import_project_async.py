# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_import_project_async.py
DESCRIPTION:
    This sample demonstrates how to import assets into a **Text Authoring** project (async).
USAGE:
    python sample_import_project_async.py
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
    PROJECT_NAME                 # defaults to "<project-name>"
    LANGUAGE_TAG                 # defaults to "<language-tag>"
    STORAGE_INPUT_CONTAINER_NAME # defaults to "<storage-container-name>"
    DOC1_PATH                    # defaults to "<doc1-path>"
    DOC2_PATH                    # defaults to "<doc2-path>"
"""

# [START text_authoring_import_project_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CreateProjectOptions,
    ExportedProject,
    ProjectSettings,
    ExportedCustomSingleLabelClassificationProjectAsset,
    ExportedCustomSingleLabelClassificationDocument,
    ExportedDocumentClass,
    ExportedClass,
    ProjectKind,
    StringIndexType,
)


async def sample_import_project_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    language_tag = os.environ.get("LANGUAGE_TAG", "<language-tag>")  # e.g., "en"
    storage_container = os.environ.get("STORAGE_INPUT_CONTAINER_NAME", "<storage-container-name>")
    doc1_path = os.environ.get("DOC1_PATH", "<doc1-path>")  # e.g., "01.txt"
    doc2_path = os.environ.get("DOC2_PATH", "<doc2-path>")  # e.g., "02.txt"

    # create a client with AAD
    credential = DefaultAzureCredential()
    async with TextAuthoringClient(endpoint, credential=credential) as client:
        # project-scoped client
        project_client = client.get_project_client(project_name)

        project_metadata = CreateProjectOptions(
            project_kind=ProjectKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION,
            storage_input_container_name=storage_container,
            project_name=project_name,
            language=language_tag,
            description="Sample project imported via Python SDK.",
            multilingual=False,
            settings=ProjectSettings(),
        )

        project_assets = ExportedCustomSingleLabelClassificationProjectAsset(
            classes=[
                ExportedClass(category="ClassA"),
                ExportedClass(category="ClassB"),
                ExportedClass(category="ClassC"),
            ],
            documents=[
                ExportedCustomSingleLabelClassificationDocument(
                    document_class=ExportedDocumentClass(category="ClassA"),
                    location=doc1_path,
                    language=language_tag,
                ),
                ExportedCustomSingleLabelClassificationDocument(
                    document_class=ExportedDocumentClass(category="ClassB"),
                    location=doc2_path,
                    language=language_tag,
                ),
            ],
        )

        exported_project = ExportedProject(
            project_file_version="2022-05-01",
            string_index_type=StringIndexType.UTF16_CODE_UNIT,
            metadata=project_metadata,
            assets=project_assets,
        )

        poller = await project_client.project.begin_import(body=exported_project)
        try:
            await poller.result()  # completes with None; raises on failure
            print("Import completed.")
            print(f"done: {poller.done()}")
            print(f"status: {poller.status()}")
        except HttpResponseError as e:
            print(f"Operation failed: {e.message}")
            print(e.error)


# [END text_authoring_import_project_async]


async def main():
    await sample_import_project_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
