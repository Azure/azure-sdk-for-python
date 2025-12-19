# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_url_async.py

DESCRIPTION:
    Another great value of Content Understanding is its rich set of prebuilt analyzers. Great examples
    of these are the RAG analyzers that work for all modalities (prebuilt-documentSearch, prebuilt-imageSearch,
    prebuilt-audioSearch, and prebuilt-videoSearch).

    This sample demonstrates these RAG analyzers with URL inputs. Content Understanding supports both
    local binary inputs (see sample_analyze_binary_async.py) and URL inputs across all modalities.

    Important: For URL inputs, use begin_analyze() with AnalyzeInput objects that wrap the URL.
    For binary data (local files), use begin_analyze_binary() instead.

    Documents, HTML, and images with text are returned as DocumentContent (derived from MediaContent),
    while audio and video are returned as AudioVisualContent (also derived from MediaContent). These
    prebuilt RAG analyzers return markdown and a one-paragraph Summary for each content item.

USAGE:
    python sample_analyze_url_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_configure_defaults_async.py for model deployment setup guidance.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    AudioVisualContent,
    DocumentContent,
    MediaContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START analyze_document_from_url]
        print("=" * 60)
        print("DOCUMENT ANALYSIS FROM URL")
        print("=" * 60)
        # You can replace this URL with your own publicly accessible document URL.
        document_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        print(f"Analyzing document from URL with prebuilt-documentSearch...")
        print(f"  URL: {document_url}")

        poller = await client.begin_analyze(
            analyzer_id="prebuilt-documentSearch",
            inputs=[AnalyzeInput(url=document_url)],
        )
        result: AnalyzeResult = await poller.result()

        # Extract markdown content
        print("\nMarkdown:")
        content = result.contents[0]
        print(content.markdown)

        # Cast MediaContent to DocumentContent to access document-specific properties
        # DocumentContent derives from MediaContent and provides additional properties
        # to access full information about document, including Pages, Tables and many others
        document_content: DocumentContent = content  # type: ignore
        print(f"\nPages: {document_content.start_page_number} - {document_content.end_page_number}")

        # Check for pages
        if document_content.pages and len(document_content.pages) > 0:
            print(f"Number of pages: {len(document_content.pages)}")
            for page in document_content.pages:
                unit = document_content.unit or "units"
                print(f"  Page {page.page_number}: {page.width} x {page.height} {unit}")
        # [END analyze_document_from_url]

        # [START analyze_video_from_url]
        print("\n" + "=" * 60)
        print("VIDEO ANALYSIS FROM URL")
        print("=" * 60)
        video_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/videos/sdk_samples/FlightSimulator.mp4"

        print(f"Analyzing video from URL with prebuilt-videoSearch...")
        print(f"  URL: {video_url}")

        poller = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[AnalyzeInput(url=video_url)],
        )
        result = await poller.result()

        # prebuilt-videoSearch can detect video segments, so we should iterate through all segments
        segment_index = 1
        for media in result.contents:
            # Cast MediaContent to AudioVisualContent to access audio/visual-specific properties
            # AudioVisualContent derives from MediaContent and provides additional properties
            # to access full information about audio/video, including timing, transcript phrases, and many others
            video_content: AudioVisualContent = media  # type: ignore
            print(f"\n--- Segment {segment_index} ---")
            print("Markdown:")
            print(video_content.markdown)

            summary = video_content.fields.get("Summary")
            if summary and hasattr(summary, "value"):
                print(f"Summary: {summary.value}")

            print(f"Start: {video_content.start_time_ms} ms, End: {video_content.end_time_ms} ms")
            print(f"Frame size: {video_content.width} x {video_content.height}")

            print("---------------------")
            segment_index += 1
        # [END analyze_video_from_url]

        # [START analyze_audio_from_url]
        print("\n" + "=" * 60)
        print("AUDIO ANALYSIS FROM URL")
        print("=" * 60)
        audio_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/audio/callCenterRecording.mp3"

        print(f"Analyzing audio from URL with prebuilt-audioSearch...")
        print(f"  URL: {audio_url}")

        poller = await client.begin_analyze(
            analyzer_id="prebuilt-audioSearch",
            inputs=[AnalyzeInput(url=audio_url)],
        )
        result = await poller.result()

        # Cast MediaContent to AudioVisualContent to access audio/visual-specific properties
        # AudioVisualContent derives from MediaContent and provides additional properties
        # to access full information about audio/video, including timing, transcript phrases, and many others
        audio_content: AudioVisualContent = result.contents[0]  # type: ignore
        print("Markdown:")
        print(audio_content.markdown)

        summary = audio_content.fields.get("Summary")
        if summary and hasattr(summary, "value"):
            print(f"Summary: {summary.value}")

        # Example: Access an additional field in AudioVisualContent (transcript phrases)
        if audio_content.transcript_phrases and len(audio_content.transcript_phrases) > 0:
            print("Transcript (first two phrases):")
            for phrase in audio_content.transcript_phrases[:2]:
                print(f"  [{phrase.speaker}] {phrase.start_time_ms} ms: {phrase.text}")
        # [END analyze_audio_from_url]

        # [START analyze_image_from_url]
        print("\n" + "=" * 60)
        print("IMAGE ANALYSIS FROM URL")
        print("=" * 60)
        image_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/image/pieChart.jpg"

        print(f"Analyzing image from URL with prebuilt-imageSearch...")
        print(f"  URL: {image_url}")

        poller = await client.begin_analyze(
            analyzer_id="prebuilt-imageSearch",
            inputs=[AnalyzeInput(url=image_url)],
        )
        result = await poller.result()

        content = result.contents[0]
        print("Markdown:")
        print(content.markdown)

        summary = content.fields.get("Summary")
        if summary and hasattr(summary, "value"):
            print(f"Summary: {summary.value}")
        # [END analyze_image_from_url]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
