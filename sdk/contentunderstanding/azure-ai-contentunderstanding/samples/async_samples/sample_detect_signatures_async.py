# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_detect_signatures_async.py

DESCRIPTION:
    SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

    This sample demonstrates how to detect signatures in an image using the ``prebuilt-layout``
    analyzer.

    Signature detection is available when layout extraction is enabled (``enable_layout``,
    including ``prebuilt-layout``). Detected regions are returned as ``DocumentSignature``
    values in ``DocumentContent.signatures``.

    Each ``DocumentSignature`` includes an identifier and a source that locates the signature in
    the analyzed content. A semantic role and markdown span are also available when the service
    can determine them.

    ## How signatures appear in markdown

    In ``DocumentContent.markdown``, each detected signature appears as a Markdown image
    reference::

        ![recognized signature text](signatures/1.1)

    The image alt text contains OCR text recognized from the handwritten signature region, so it
    may be incomplete or include extra characters. The link target uses ``signatures/{id}``, where
    ``{id}`` matches the corresponding ``DocumentSignature.id``. The signature's ``span``
    identifies the exact offset and length of this image reference in ``DocumentContent.markdown``.

USAGE:
    python sample_detect_signatures_async.py

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


async def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START detect_signatures]
        file_path = "sample_files/sample_signature.png"
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        print(f"Analyzing {file_path} for signatures...")
        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-layout",
            binary_input=image_bytes,
        )
        result: AnalysisResult = await poller.result()

        document = cast(DocumentContent, result.contents[0])
        signatures = document.signatures or []
        print(f"Found {len(signatures)} signature(s).")
        for signature in signatures:
            print(f"Signature ID: {signature.id}")
            print(f"  Role: {signature.role or '(not available)'}")
            print(f"  Source: {signature.source}")
            if signature.span:
                print(f"  Span: offset={signature.span.offset}, length={signature.span.length}")
                markdown = document.markdown or ""
                markdown_fragment = markdown[signature.span.offset : signature.span.offset + signature.span.length]
                print(f"  Markdown: {markdown_fragment}")
        # [END detect_signatures]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
