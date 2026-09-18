# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_classify_in_page_segments_async.py

DESCRIPTION:
    SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

    This sample demonstrates how to create a classifier analyzer that can classify multiple
    document segments that appear on the same page.

    By default, document segmentation uses page boundaries. Set ``allow_in_page_segments``
    together with ``enable_segment`` when distinct documents can appear on the same page — for
    example, separating individual supplemental statements that are often appended after the
    main form in a K-1 tax package. See the Content Understanding classifier overview
    (https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/classifier)
    for supported scenarios and Studio guidance.

    This sample uses a simplified synthetic one-page PDF containing an invoice in the upper half
    and an account statement in the lower half
    (``sample_files/mixed_financial_docs_in_page.pdf``).

    Both segments typically report page range ``1-1``, while their distinct ``span`` and ``source``
    values locate each document within that page. ``confidence`` represents the combined
    confidence of segmentation and category classification.

USAGE:
    python sample_classify_in_page_segments_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using classifiers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults_async.py for setup instructions.
"""


import asyncio
import os
import time
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START classify_in_page_segments]
        analyzer_id = f"in_page_classifier_{int(time.time())}"

        config = ContentAnalyzerConfig(
            # Return full content details (markdown, spans, sources, and per-segment
            # metadata) in the result. Required to inspect the segments below.
            return_details=True,
            # Enable classification-based segmentation: the input is split into segments,
            # each classified against the ContentCategories defined below.
            enable_segment=True,
            # Allow a segment to cover only part of a page, so multiple documents that
            # share one page can be separated. When false (the default), segments break
            # on whole-page boundaries only.
            allow_in_page_segments=True,
            # Return grounding source and confidence for extracted fields.
            estimate_field_source_and_confidence=True,
            content_categories={
                "Invoice": ContentCategoryDefinition(
                    description="An invoice requesting payment for goods or services, with line items, totals, and payment terms."
                ),
                "BankStatement": ContentCategoryDefinition(
                    description="A bank account statement listing balances, deposits, withdrawals, fees, and transactions."
                ),
            },
        )

        classifier = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Classify financial documents that may share a page.",
            config=config,
            models={"completion": "gpt-5.2"},
        )

        print(f"Creating classifier '{analyzer_id}'...")
        create_poller = await client.begin_create_analyzer(analyzer_id=analyzer_id, resource=classifier)
        await create_poller.result()

        try:
            file_path = "sample_files/mixed_financial_docs_in_page.pdf"
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            print(f"Analyzing {file_path} with classifier '{analyzer_id}'...")
            analyze_poller = await client.begin_analyze_binary(
                analyzer_id=analyzer_id,
                binary_input=file_bytes,
            )
            result: AnalysisResult = await analyze_poller.result()

            document = cast(DocumentContent, result.contents[0])
            for segment in document.segments or []:
                print(f"Category: {segment.category}")
                print(f"  Pages: {segment.start_page_number}-{segment.end_page_number}")
                print(
                    f"  Confidence: {segment.confidence:.1%}"
                    if segment.confidence is not None
                    else "  Confidence: (not available)"
                )
                print(f"  Source: {segment.source}")
                print(f"  Span: offset={segment.span.offset}, length={segment.span.length}")
        finally:
            print(f"Cleaning up: deleting classifier '{analyzer_id}'...")
            await client.delete_analyzer(analyzer_id=analyzer_id)
        # [END classify_in_page_segments]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
