# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_get_result_file_async.py

DESCRIPTION:
    This sample demonstrates how to retrieve result files (such as keyframe images) from a
    video analysis operation using the get_result_file API.

    About result files:
    When analyzing video content, the Content Understanding service can generate result files such as:
    - Keyframe images: Extracted frames from the video at specific timestamps
    - Other result files: Additional files generated during analysis

    The get_result_file API allows you to retrieve these files using:
    - Operation ID: Extracted from the analysis operation
    - File path: The path to the specific result file. In the recording, keyframes were accessed
                 with paths like keyframes/733 and keyframes/9000, following the
                 keyframes/{frameTimeMs} pattern.

USAGE:
    python sample_get_result_file_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    AudioVisualContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START analyze_video_for_result_files]
        # Use a sample video URL to get keyframes for GetResultFile testing
        # You can replace this with your own video file URL
        video_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-assets/raw/refs/heads/main/videos/sdk_samples/FlightSimulator.mp4"

        print("Analyzing video with prebuilt-videoSearch...")
        print(f"  URL: {video_url}")

        # Analyze and wait for completion
        analyze_operation = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[AnalyzeInput(url=video_url)],
        )

        # Get the operation ID - this is needed to retrieve result files later
        operation_id = analyze_operation.operation_id
        print(f"  Operation ID: {operation_id}")

        print("  Waiting for analysis to complete...")
        result: AnalyzeResult = await analyze_operation.result()
        # [END analyze_video_for_result_files]

        # [START get_result_file]
        if not result.contents or len(result.contents) == 0:
            print("No content found in the analysis result.")
            return

        # For video analysis, keyframes would be found in AudioVisualContent.key_frame_times_ms
        # Cast MediaContent to AudioVisualContent to access video-specific properties
        video_content: AudioVisualContent = result.contents[0]  # type: ignore

        # Print keyframe information
        if video_content.key_frame_times_ms and len(video_content.key_frame_times_ms) > 0:
            total_keyframes = len(video_content.key_frame_times_ms)
            first_frame_time_ms = video_content.key_frame_times_ms[0]

            print(f"Total keyframes: {total_keyframes}")
            print(f"First keyframe time: {first_frame_time_ms} ms")

            # Get the first keyframe as an example
            frame_path = f"keyframes/{first_frame_time_ms}"

            print(f"Getting result file: {frame_path}")

            # Get the result file (keyframe image) using the operation ID obtained from Operation<T>.id
            file_response = await client.get_result_file(
                operation_id=operation_id,
                path=frame_path,
            )

            image_bytes = b"".join([chunk async for chunk in file_response])
            print(f"Retrieved keyframe image ({len(image_bytes):,} bytes)")

            # Save the keyframe image to sample_output directory
            output_dir = Path(__file__).parent.parent / "sample_output"
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
        # [END get_result_file]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
