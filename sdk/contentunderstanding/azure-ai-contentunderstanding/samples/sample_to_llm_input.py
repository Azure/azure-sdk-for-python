# pylint: disable=line-too-long,useless-suppression
# mypy: disable-error-code="attr-defined"
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_to_llm_input.py

DESCRIPTION:
    This sample demonstrates advanced usage of the ``to_llm_input`` helper. For a basic introduction
    to ``to_llm_input``, see sample_analyze_binary.py (document analysis), sample_analyze_invoice.py
    (field extraction), and sample_create_classifier.py (classification).

    ## About ``to_llm_input``

    When using Content Understanding with large language models, you typically need to convert the
    structured ``AnalysisResult`` into a text format that an LLM can consume. The ``to_llm_input``
    helper handles this conversion automatically:

    - **YAML front matter** with content type, extracted fields, page numbers, and optional metadata
    - **Markdown body** with the document content and page markers

    The helper supports all content types (documents, images, audio, video) and handles
    multi-segment results (e.g., video with multiple scenes) by rendering each segment with its
    time range. For classification results, it automatically skips the parent document and renders
    each categorized child with its category label.

    ### Scenarios demonstrated

    1. **Output options** — Fields-only, markdown-only, and custom metadata
    2. **Multi-page PDF with content_range** — Analyze specific pages and verify page markers
    3. **Multi-segment video** — Analyze a video with multiple segments and time ranges
    4. **Audio with content_range** — Analyze a specific time range of an audio file

    For classification results, see ``sample_create_classifier.py``.

USAGE:
    python sample_to_llm_input.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient, to_llm_input
from azure.ai.contentunderstanding.models import AnalysisInput
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # ================================================================
    # 1. OUTPUT OPTIONS — Fields-only, markdown-only, metadata
    # ================================================================

    # [START to_llm_input]
    # First, analyze an invoice to get a result we can demonstrate options with.
    invoice_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

    print("=" * 60)
    print("OUTPUT OPTIONS")
    print("=" * 60)
    print("Analyzing invoice for output option demos...")
    print(f"  URL: {invoice_url}\n")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-invoice",
        inputs=[AnalysisInput(url=invoice_url)],
    )
    result = poller.result()

    # Convert to LLM-ready text (YAML front matter + markdown)
    # For basic usage, see sample_analyze_binary.py and sample_analyze_invoice.py.
    text = to_llm_input(result)
    print("Default output (fields + markdown):")
    print(text)

    # [START to_llm_input_options]

    # Fields-only mode — smaller token footprint when you only need structured data.
    # Useful for agentic workflows where the LLM only needs extracted values.
    fields_only = to_llm_input(result, include_markdown=False)
    print("\n--- Fields only (include_markdown=False) ---")
    print(fields_only)

    # Markdown-only mode — when you only need the document text.
    # Useful for summarization or when fields are not relevant.
    markdown_only = to_llm_input(result, include_fields=False)
    print("\n--- Markdown only (include_fields=False) ---")
    print(markdown_only)

    # Custom metadata — add your own key-value pairs to the YAML front matter.
    # Useful for RAG pipelines to track document source, department, batch, etc.
    with_metadata = to_llm_input(
        result,
        metadata={"source": "invoice.pdf", "department": "finance"},
    )
    print("\n--- With metadata ---")
    print(with_metadata)
    # [END to_llm_input_options]

    # ================================================================
    # 2. MULTI-PAGE PDF WITH CONTENT RANGE
    # ================================================================

    # [START to_llm_input_content_range]
    multi_page_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/mixed_financial_invoices.pdf"

    print("\n" + "=" * 60)
    print("MULTI-PAGE PDF WITH CONTENT RANGE")
    print("=" * 60)

    # Analyze specific pages using content_range.
    # Page markers in the output will use the original document page numbers,
    # so even though we only requested pages 2-3 and 5, the markers will say
    # <!-- page 2 -->, <!-- page 3 -->, <!-- page 5 --> (not 1, 2, 3).
    print("Analyzing pages 2-3 and 5 of a multi-page PDF...")
    print(f"  URL: {multi_page_url}")
    print(f"  content_range: '2-3,5'\n")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-documentSearch",
        inputs=[AnalysisInput(url=multi_page_url, content_range="2-3,5")],
    )
    result = poller.result()

    text = to_llm_input(result)
    print("Output:")
    print(text)
    # [END to_llm_input_content_range]

    # ================================================================
    # 3. MULTI-SEGMENT VIDEO
    # ================================================================

    # [START to_llm_input_video]
    video_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/videos/sdk_samples/FlightSimulator.mp4"

    print("\n" + "=" * 60)
    print("MULTI-SEGMENT VIDEO")
    print("=" * 60)

    # Analyze a video — the result may contain multiple segments.
    # to_llm_input renders each segment with its time range in the front matter
    # (e.g., timeRange: 00:00 – 00:15) and separates segments with ***** dividers.
    print("Analyzing video...")
    print(f"  URL: {video_url}\n")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-videoSearch",
        inputs=[AnalysisInput(url=video_url)],
    )
    result = poller.result()

    text = to_llm_input(result)
    print(f"Video produced {len(result.contents)} segment(s)")
    print("\nOutput:")
    print(text)
    # [END to_llm_input_video]

    # ================================================================
    # 4. AUDIO WITH CONTENT RANGE
    # ================================================================

    # [START to_llm_input_audio]
    audio_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/audio/callCenterRecording.mp3"

    print("\n" + "=" * 60)
    print("AUDIO WITH CONTENT RANGE")
    print("=" * 60)

    # Analyze a specific time range of an audio file (first 10 seconds).
    # For audio, content_range uses milliseconds: "0-10000" means 0s to 10s.
    print("Analyzing first 10 seconds of audio...")
    print(f"  URL: {audio_url}")
    print(f"  content_range: '0-10000'\n")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-audioSearch",
        inputs=[AnalysisInput(url=audio_url, content_range="0-10000")],
    )
    result = poller.result()

    # Include metadata to track the source file in RAG pipelines
    text = to_llm_input(
        result,
        metadata={"source": "callCenterRecording.mp3"},
    )
    print("Output:")
    print(text)
    # [END to_llm_input_audio]


if __name__ == "__main__":
    main()
