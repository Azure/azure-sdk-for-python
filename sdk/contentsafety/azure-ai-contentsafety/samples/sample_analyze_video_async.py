# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio


def analyze_video_async():
    # [START analyze_video_async]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import ImageCategory
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

    import datetime
    from decord import VideoReader
    from io import BytesIO
    import numpy as np
    from tqdm import tqdm
    from PIL import Image

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
    video_path = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "./sample_data/video.mp4"))

    # Create a Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    # Read the video
    video = VideoReader(video_path)
    sampling_fps = 1  # process at 1 frames per second
    key_frames = video.get_batch(
        np.int_(np.arange(0, len(video), video.get_avg_fps() / sampling_fps))).asnumpy()

    # Iterate over key frames
    for key_frame_idx in tqdm(range(len(key_frames)), desc="Processing video",
                              total=len(key_frames)):
        frame = Image.fromarray(key_frames[key_frame_idx])
        frame_bytes = BytesIO()
        frame.save(frame_bytes, format="PNG")

        # Build request
        request = AnalyzeImageOptions(image=ImageData(content=frame_bytes.getvalue()))

        # Analyze image
        frame_time_ms = key_frame_idx * 1000 / sampling_fps
        frame_timestamp = datetime.timedelta(milliseconds=frame_time_ms)
        print(f"Analyzing video at {frame_timestamp}")
        try:
            response = client.analyze_image(request)
        except HttpResponseError as e:
            print(f"Analyze video failed at {frame_timestamp}")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

        hate_result = next(
            item for item in response.categories_analysis if item.category == ImageCategory.HATE)
        self_harm_result = next(item for item in response.categories_analysis if
                                item.category == ImageCategory.SELF_HARM)
        sexual_result = next(
            item for item in response.categories_analysis if item.category == ImageCategory.SEXUAL)
        violence_result = next(item for item in response.categories_analysis if
                               item.category == ImageCategory.VIOLENCE)

        if hate_result:
            print(f"Hate severity: {hate_result.severity}")
        if self_harm_result:
            print(f"SelfHarm severity: {self_harm_result.severity}")
        if sexual_result:
            print(f"Sexual severity: {sexual_result.severity}")
        if violence_result:
            print(f"Violence severity: {violence_result.severity}")

        # [END analyze_video_async]


async def main():
    await analyze_video_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
