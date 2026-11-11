# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_chunking.py

DESCRIPTION:
    SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

    This sample demonstrates how to configure ``SemanticChunkingStrategy`` on a custom analyzer
    and read chunks from analysis results.

    The walkthrough uses ``sample_files/sample_invoice.pdf``. After analysis, each chunk exposes a
    ``source`` plus ``spans`` into ``DocumentContent.markdown``. Reconstruct chunk text by
    slicing the markdown with those span offsets and lengths.

    Example output from ``sample_invoice.pdf`` (``max_tokens=300``)::

        Chunk count: 3
        --- Chunk 1 ---
        CONTOSO LTD.
        ...
        --- Chunk 2 ---
        <table>...line items...</table>
        --- Chunk 3 ---
        <table>...totals...</table>
        THANK YOU FOR YOUR BUSINESS!
        ...

    Chunk boundaries can vary slightly by model and ``max_tokens``, but with this invoice the
    service typically separates header/party details, line items, and totals into distinct chunks.

USAGE:
    python sample_analyze_chunking.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults.py for model deployment setup guidance.
"""


import os
import time
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AnalysisResult,
    ContentAnalyzer,
    ContentAnalyzerConfig,
    DocumentContent,
    SemanticChunkingStrategy,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START analyze_with_semantic_chunking]
    analyzer_id = f"chunking_analyzer_{int(time.time())}"
    analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Analyzer with semantic chunking",
        config=ContentAnalyzerConfig(
            return_details=True,
            enable_layout=True,
            chunking_strategy=SemanticChunkingStrategy(max_tokens=300),
        ),
        models={"completion": "gpt-5.2"},
    )

    try:
        client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=analyzer,
            allow_replace=True,
        ).result()

        with open("sample_files/sample_invoice.pdf", "rb") as f:
            file_bytes = f.read()

        analyze_poller = client.begin_analyze(
            analyzer_id=analyzer_id,
            inputs=[AnalysisInput(data=file_bytes)],
        )
        result: AnalysisResult = analyze_poller.result()
        # [END analyze_with_semantic_chunking]

        content = cast(DocumentContent, result.contents[0])
        markdown = content.markdown or ""
        chunks = content.chunks or []
        print(f"Chunk count: {len(chunks)}")
        for index, chunk in enumerate(chunks):
            print(f"--- Chunk {index + 1} ---")
            chunk_parts = []
            for span in chunk.spans or []:
                chunk_parts.append(markdown[span.offset : span.offset + span.length])
            print("\n".join(chunk_parts))
    finally:
        client.delete_analyzer(analyzer_id)


if __name__ == "__main__":
    main()
