# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_get_result_file.py

DESCRIPTION:
    This sample demonstrates how to retrieve result files (such as keyframe images) from a
    video analysis operation using the get_result_file API.

    When analyzing video content, the Content Understanding service can generate result files:
    - Keyframe images: Extracted frames from the video at specific timestamps
    - Other result files: Additional files generated during analysis

    The get_result_file API allows you to retrieve these files using:
    - Operation ID: Extracted from the analysis operation
    - File path: The path to the specific result file (e.g., "keyframes/{frameTimeMs}")

USAGE:
    python sample_get_result_file.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    AudioVisualContent,
    MediaContentKind,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # Analyze video and get result files
    analyze_video_and_get_result_files(client)


# [START ContentUnderstandingAnalyzeVideoForResultFiles]
def analyze_video_and_get_result_files(client: ContentUnderstandingClient) -> None:
    """Analyze a video and retrieve result files (keyframe images)."""

    # Use a sample video URL
    video_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/sample_video.mp4"

    print(f"Analyzing video with prebuilt-videoSearch...")
    print(f"  URL: {video_url}")

    # Start the analysis operation (using begin_analyze which returns a poller)
    poller = client.begin_analyze(
        analyzer_id="prebuilt-videoSearch",
        inputs=[AnalyzeInput(url=video_url)],
    )

    # Get the operation ID from the poller
    operation_id = poller.operation_id
    print(f"  Operation ID: {operation_id}")

    # Wait for completion
    print("  Waiting for analysis to complete...")
    result: AnalyzeResult = poller.result()

    # Get result files
    get_result_files(client, operation_id, result)
# [END ContentUnderstandingAnalyzeVideoForResultFiles]


# [START ContentUnderstandingGetResultFile]
def get_result_files(client: ContentUnderstandingClient, operation_id: str, result: AnalyzeResult) -> None:
    """Retrieve result files (keyframe images) using the operation ID and file path."""

    if not result.contents or len(result.contents) == 0:
        print("No content found in the analysis result.")
        return

    content = result.contents[0]

    # For video analysis, keyframes would be found in AudioVisualContent.KeyFrameTimesMs
    if content.kind in [MediaContentKind.VIDEO, MediaContentKind.AUDIO]:
        video_content: AudioVisualContent = content  # type: ignore

        if video_content.key_frame_times_ms and len(video_content.key_frame_times_ms) > 0:
            total_keyframes = len(video_content.key_frame_times_ms)
            first_frame_time_ms = video_content.key_frame_times_ms[0]

            print(f"\nTotal keyframes: {total_keyframes}")
            print(f"First keyframe time: {first_frame_time_ms} ms")

            # Get the first keyframe as an example
            frame_path = f"keyframes/{first_frame_time_ms}"

            print(f"Getting result file: {frame_path}")

            # Get the result file (keyframe image)
            file_response = client.get_result_file(
                operation_id=operation_id,
                file_path=frame_path,
            )

            image_bytes = file_response
            print(f"Retrieved keyframe image ({len(image_bytes):,} bytes)")

            # Save the keyframe image to sample_output directory
            output_dir = Path(__file__).parent / "sample_output"
            output_dir.mkdir(exist_ok=True)
            output_filename = f"keyframe_{first_frame_time_ms}.jpg"
            output_path = output_dir / output_filename

            with open(output_path, "wb") as f:
                f.write(image_bytes)

            print(f"Keyframe image saved to: {output_path}")
        else:
            print("\nNote: This sample demonstrates GetResultFile API usage.")
            print("      For video analysis with keyframes, use prebuilt-videoSearch analyzer.")
            print("      Keyframes are available in AudioVisualContent.key_frame_times_ms.")
            print()
            print(f"Example usage with operation ID '{operation_id}':")
            print("  file_response = client.get_result_file(")
            print("      operation_id=operation_id,")
            print('      file_path="keyframes/1000")')
    else:
        print("\nNote: This sample is designed for video analysis.")
        print("      The analyzed content is not a video.")
# [END ContentUnderstandingGetResultFile]


if __name__ == "__main__":
    main()
