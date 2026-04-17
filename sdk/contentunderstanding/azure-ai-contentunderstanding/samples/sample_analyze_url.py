# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_url.py

DESCRIPTION:
    Another great value of Content Understanding is its rich set of prebuilt analyzers. Great examples
    of these are the RAG analyzers that work for all modalities (prebuilt-documentSearch,
    prebuilt-imageSearch, prebuilt-audioSearch, and prebuilt-videoSearch). This sample demonstrates
    these RAG analyzers. Many more prebuilt analyzers are available (for example, prebuilt-invoice);
    see the invoice sample or the prebuilt analyzer documentation to explore the full list.

    ## About analyzing URLs across modalities

    Content Understanding supports both local binary inputs (see sample_analyze_binary.py) and URL
    inputs across all modalities. This sample focuses on prebuilt RAG analyzers (the prebuilt-*Search
    analyzers, such as prebuilt-documentSearch) with URL inputs.

    Important: For URL inputs, use begin_analyze() with AnalysisInput objects that wrap the URL.
    For binary data (local files), use begin_analyze_binary() instead. This sample demonstrates
    begin_analyze() with URL inputs.

    Documents, HTML, and images with text are returned as DocumentContent (derived from AnalysisContent),
    while audio and video are returned as AudioVisualContent (also derived from AnalysisContent). These
    prebuilt RAG analyzers return markdown and a one-paragraph Summary for each content item;
    prebuilt-videoSearch can return multiple segments, so iterate over all contents rather than just
    the first.

USAGE:
    python sample_analyze_url.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults.py for model deployment setup guidance.
"""

import os
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AnalysisResult,
    AudioVisualContent,
    DocumentContent,
    AnalysisContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START analyze_document_from_url]
    print("=" * 60)
    print("DOCUMENT ANALYSIS FROM URL")
    print("=" * 60)
    # You can replace this URL with your own publicly accessible document URL.
    document_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/mixed_financial_docs.pdf"

    print(f"Analyzing document from URL with prebuilt-documentSearch...")
    print(f"  URL: {document_url}")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-documentSearch",
        inputs=[AnalysisInput(url=document_url)],
    )
    result: AnalysisResult = poller.result()

    # Extract markdown content
    print("\nMarkdown:")
    content = result.contents[0]
    print(content.markdown)

    # Cast AnalysisContent to DocumentContent to access document-specific properties
    # DocumentContent derives from AnalysisContent and provides additional properties
    # to access full information about document, including Pages, Tables and many others
    document_content = cast(DocumentContent, content)
    print(
        f"\nPages: {document_content.start_page_number} - {document_content.end_page_number}"
    )

    # Check for pages
    if document_content.pages and len(document_content.pages) > 0:
        print(f"Number of pages: {len(document_content.pages)}")
        for page in document_content.pages:
            unit = document_content.unit or "units"
            print(f"  Page {page.page_number}: {page.width} x {page.height} {unit}")
    # [END analyze_document_from_url]

    # [START analyze_document_url_with_content_range]
    # Restrict to specific pages with a content range string.
    # Use a multi-page document to demonstrate content range filtering.
    multi_page_document_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/mixed_financial_invoices.pdf"

    # Extract only page 1 of the document.
    print("\nAnalyzing page 1 only with content range '1'...")
    range_poller = client.begin_analyze(
        analyzer_id="prebuilt-documentSearch",
        inputs=[AnalysisInput(url=multi_page_document_url, content_range="1")],
    )
    range_result: AnalysisResult = range_poller.result()

    range_doc_content = cast(DocumentContent, range_result.contents[0])
    print(
        f"Content range analysis returned pages"
        f" {range_doc_content.start_page_number} - {range_doc_content.end_page_number}"
    )

    # Combine multiple page ranges: pages 1-3, page 5, and pages 9 onward.
    print("\nAnalyzing combined pages (1-3, 5, 9-) with content range '1-3,5,9-'...")
    combine_range_poller = client.begin_analyze(
        analyzer_id="prebuilt-documentSearch",
        inputs=[AnalysisInput(url=multi_page_document_url, content_range="1-3,5,9-")],
    )
    combine_range_result: AnalysisResult = combine_range_poller.result()

    combine_doc_content = cast(DocumentContent, combine_range_result.contents[0])
    print(
        f"Combined content range analysis returned pages"
        f" {combine_doc_content.start_page_number} - {combine_doc_content.end_page_number}"
    )
    # [END analyze_document_url_with_content_range]

    # [START analyze_video_from_url]
    print("\n" + "=" * 60)
    print("VIDEO ANALYSIS FROM URL")
    print("=" * 60)
    video_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/videos/sdk_samples/FlightSimulator.mp4"

    print(f"Analyzing video from URL with prebuilt-videoSearch...")
    print(f"  URL: {video_url}")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-videoSearch",
        inputs=[AnalysisInput(url=video_url)],
    )
    result = poller.result()

    # prebuilt-videoSearch can detect video segments, so we should iterate through all segments
    segment_index = 1
    for media in result.contents:
        # Cast AnalysisContent to AudioVisualContent to access audio/visual-specific properties
        # AudioVisualContent derives from AnalysisContent and provides additional properties
        # to access full information about audio/video, including timing, transcript phrases, and many others
        video_content = cast(AudioVisualContent, media)
        print(f"\n--- Segment {segment_index} ---")
        print("Markdown:")
        print(video_content.markdown)

        summary = video_content.fields.get("Summary") if video_content.fields else None
        if summary and hasattr(summary, "value"):
            print(f"Summary: {summary.value}")

        print(
            f"Start: {video_content.start_time_ms} ms, End: {video_content.end_time_ms} ms"
        )
        print(f"Frame size: {video_content.width} x {video_content.height}")

        print("---------------------")
        segment_index += 1
    # [END analyze_video_from_url]

    # [START analyze_video_url_with_content_range]
    # Restrict to a time window with a content range string.
    # Analyze only the first 5 seconds of the video (milliseconds: "0-5000").
    print("\nAnalyzing first 5 seconds of video with content range '0-5000'...")
    video_range_poller = client.begin_analyze(
        analyzer_id="prebuilt-videoSearch",
        inputs=[
            AnalysisInput(
                url=video_url,
                content_range="0-5000",
            )
        ],
    )
    video_range_result = video_range_poller.result()

    for range_media in video_range_result.contents:
        range_video_content = cast(AudioVisualContent, range_media)
        print(
            f"Content range segment:"
            f" {range_video_content.start_time_ms} ms - {range_video_content.end_time_ms} ms"
        )
    # [END analyze_video_url_with_content_range]

    # [START analyze_video_url_with_additional_content_ranges]
    # Additional content range examples for video (time ranges use milliseconds):

    # "10000-" — analyze from 10 seconds onward
    print("\nAnalyzing video from 10 seconds onward with content range '10000-'...")
    video_from_poller = client.begin_analyze(
        analyzer_id="prebuilt-videoSearch",
        inputs=[
            AnalysisInput(
                url=video_url,
                content_range="10000-",
            )
        ],
    )
    video_from_result = video_from_poller.result()
    for from_media in video_from_result.contents:
        from_video = cast(AudioVisualContent, from_media)
        print(
            f"'10000-' segment:"
            f" {from_video.start_time_ms} ms - {from_video.end_time_ms} ms"
        )

    # "1200-3651" — sub-second precision (1.2s to 3.651s)
    print("\nAnalyzing video with sub-second precision (1.2s to 3.651s) with content range '1200-3651'...")
    video_subsec_poller = client.begin_analyze(
        analyzer_id="prebuilt-videoSearch",
        inputs=[
            AnalysisInput(
                url=video_url,
                content_range="1200-3651",
            )
        ],
    )
    video_subsec_result = video_subsec_poller.result()
    for subsec_media in video_subsec_result.contents:
        subsec_video = cast(AudioVisualContent, subsec_media)
        print(
            f"'1200-3651' segment:"
            f" {subsec_video.start_time_ms} ms - {subsec_video.end_time_ms} ms"
        )

    # "0-3000,30000-" — multiple disjoint time ranges (0-3s and 30s onward)
    print("\nAnalyzing video with combined time ranges (0-3s and 30s onward) with content range '0-3000,30000-'...")
    video_combine_poller = client.begin_analyze(
        analyzer_id="prebuilt-videoSearch",
        inputs=[
            AnalysisInput(
                url=video_url,
                content_range="0-3000,30000-",
            )
        ],
    )
    video_combine_result = video_combine_poller.result()
    for combine_media in video_combine_result.contents:
        combine_video = cast(AudioVisualContent, combine_media)
        print(
            f"'0-3000,30000-' segment:"
            f" {combine_video.start_time_ms} ms - {combine_video.end_time_ms} ms"
        )
    # [END analyze_video_url_with_additional_content_ranges]

    # [START analyze_audio_from_url]
    print("\n" + "=" * 60)
    print("AUDIO ANALYSIS FROM URL")
    print("=" * 60)
    audio_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/audio/callCenterRecording.mp3"

    print(f"Analyzing audio from URL with prebuilt-audioSearch...")
    print(f"  URL: {audio_url}")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-audioSearch",
        inputs=[AnalysisInput(url=audio_url)],
    )
    result = poller.result()

    # Cast AnalysisContent to AudioVisualContent to access audio/visual-specific properties
    # AudioVisualContent derives from AnalysisContent and provides additional properties
    # to access full information about audio/video, including timing, transcript phrases, and many others
    audio_content = cast(AudioVisualContent, result.contents[0])
    print("Markdown:")
    print(audio_content.markdown)

    summary = audio_content.fields.get("Summary") if audio_content.fields else None
    if summary and hasattr(summary, "value"):
        print(f"Summary: {summary.value}")

    # Example: Access an additional field in AudioVisualContent (transcript phrases)
    if audio_content.transcript_phrases and len(audio_content.transcript_phrases) > 0:
        print("Transcript (first two phrases):")
        for phrase in audio_content.transcript_phrases[:2]:
            print(f"  [{phrase.speaker}] {phrase.start_time_ms} ms: {phrase.text}")
    # [END analyze_audio_from_url]

    # [START analyze_audio_url_with_content_range]
    # Restrict to a time window with a content range string.
    # Analyze only the first 5 seconds of the audio (milliseconds: "0-5000").
    print("\nAnalyzing first 5 seconds of audio with content range '0-5000'...")
    audio_range_poller = client.begin_analyze(
        analyzer_id="prebuilt-audioSearch",
        inputs=[
            AnalysisInput(
                url=audio_url,
                content_range="0-5000",
            )
        ],
    )
    audio_range_result = audio_range_poller.result()

    range_audio_content = cast(AudioVisualContent, audio_range_result.contents[0])
    print(
        f"Content range audio segment:"
        f" {range_audio_content.start_time_ms} ms - {range_audio_content.end_time_ms} ms"
    )
    # [END analyze_audio_url_with_content_range]

    # [START analyze_audio_url_with_additional_content_ranges]
    # Additional content range examples for audio (time ranges use milliseconds):

    # "10000-" — analyze from 10 seconds onward
    print("\nAnalyzing audio from 10 seconds onward with content range '10000-'...")
    audio_from_poller = client.begin_analyze(
        analyzer_id="prebuilt-audioSearch",
        inputs=[
            AnalysisInput(
                url=audio_url,
                content_range="10000-",
            )
        ],
    )
    audio_from_result = audio_from_poller.result()
    audio_from_content = cast(AudioVisualContent, audio_from_result.contents[0])
    print(
        f"'10000-':"
        f" {audio_from_content.start_time_ms} ms - {audio_from_content.end_time_ms} ms"
    )

    # "1200-3651" — sub-second precision (1.2s to 3.651s)
    print("\nAnalyzing audio with sub-second precision (1.2s to 3.651s) with content range '1200-3651'...")
    audio_subsec_poller = client.begin_analyze(
        analyzer_id="prebuilt-audioSearch",
        inputs=[
            AnalysisInput(
                url=audio_url,
                content_range="1200-3651",
            )
        ],
    )
    audio_subsec_result = audio_subsec_poller.result()
    audio_subsec_content = cast(AudioVisualContent, audio_subsec_result.contents[0])
    print(
        f"'1200-3651':"
        f" {audio_subsec_content.start_time_ms} ms - {audio_subsec_content.end_time_ms} ms"
    )

    # "0-3000,30000-" — multiple disjoint time ranges (0-3s and 30s onward)
    print("\nAnalyzing audio with combined time ranges (0-3s and 30s onward) with content range '0-3000,30000-'...")
    audio_combine_poller = client.begin_analyze(
        analyzer_id="prebuilt-audioSearch",
        inputs=[
            AnalysisInput(
                url=audio_url,
                content_range="0-3000,30000-",
            )
        ],
    )
    audio_combine_result = audio_combine_poller.result()
    audio_combine_content = cast(AudioVisualContent, audio_combine_result.contents[0])
    print(
        f"'0-3000,30000-':"
        f" {audio_combine_content.start_time_ms} ms - {audio_combine_content.end_time_ms} ms"
    )
    # [END analyze_audio_url_with_additional_content_ranges]

    # [START analyze_image_from_url]
    print("\n" + "=" * 60)
    print("IMAGE ANALYSIS FROM URL")
    print("=" * 60)
    image_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/image/pieChart.jpg"

    print(f"Analyzing image from URL with prebuilt-imageSearch...")
    print(f"  URL: {image_url}")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-imageSearch",
        inputs=[AnalysisInput(url=image_url)],
    )
    result = poller.result()

    content = result.contents[0]
    print("Markdown:")
    print(content.markdown)

    summary = content.fields.get("Summary") if content.fields else None
    if summary and hasattr(summary, "value"):
        print(f"Summary: {summary.value}")
    # [END analyze_image_from_url]


if __name__ == "__main__":
    main()
