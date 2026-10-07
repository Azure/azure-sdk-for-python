# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_extract_document_metadata_async.py

DESCRIPTION:
    SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

    This sample demonstrates how to extract embedded document metadata from PDF and DOCX files
    using the ``prebuilt-layout`` analyzer.

    Content Understanding can return metadata embedded in source documents through
    ``AnalysisContent.metadata``. The metadata is a string-to-string dictionary, and only
    properties with extracted values are included. Applications should enumerate the dictionary
    and tolerate additional keys as support evolves.

    ## Extract PDF metadata

    PDF metadata can include ``author``, ``contentType``, ``createdAt``, ``language``,
    ``pageCount``, and ``title``. Each property is optional because the service only returns
    values embedded in or derivable from the source document.

    Example output from ``sample_files/sample_metadata.pdf``::

        author: Contoso Metadata Team
        contentType: application/pdf
        language: en-US
        pageCount: 1
        title: Contoso Metadata Extraction Sample

    ## Extract DOCX metadata

    DOCX files can expose additional Office document properties, including the last person who
    modified the document and application-maintained content counts. DOCX metadata can include
    ``author``, ``characterCount``, ``contentType``, ``createdAt``, ``lastModifiedAt``,
    ``lastModifiedBy``, ``pageCount``, ``title``, and ``wordCount``.

    Example output from ``sample_files/sample_metadata.docx``::

        author: Contoso Metadata Team
        characterCount: 207
        contentType: application/vnd.openxmlformats-officedocument.wordprocessingml.document
        createdAt: 2026-07-16T19:00:00Z
        lastModifiedAt: 2026-07-16T20:30:00Z
        lastModifiedBy: Megan Bowen
        pageCount: 1
        title: Contoso Metadata Extraction Sample
        wordCount: 29

USAGE:
    python sample_extract_document_metadata_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults_async.py for model deployment setup guidance.
"""


import asyncio
import os
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisResult, DocumentContent
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def print_metadata(client: ContentUnderstandingClient, file_path: str) -> None:
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    poller = await client.begin_analyze_binary(
        analyzer_id="prebuilt-layout",
        binary_input=file_bytes,
    )
    result: AnalysisResult = await poller.result()

    document = cast(DocumentContent, result.contents[0])
    print(f"\nMetadata for {file_path}:")
    metadata = document.metadata or {}
    for key, value in sorted(metadata.items()):
        print(f"{key}: {value}")


async def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START extract_pdf_metadata]
        await print_metadata(client, "sample_files/sample_metadata.pdf")
        # [END extract_pdf_metadata]

        # [START extract_docx_metadata]
        await print_metadata(client, "sample_files/sample_metadata.docx")
        # [END extract_docx_metadata]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
