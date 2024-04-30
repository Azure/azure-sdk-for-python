# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_face_grouping_async.py

DESCRIPTION:
    This sample demonstrates how to group faces based on face similarity.

USAGE:
    python sample_face_grouping_async.py

    Set the environment variables with your own values before running this sample:
    1) FACE_ENDPOINT - the endpoint to your Face resource.
    2) FACE_KEY - your Face API key.
"""
import asyncio
import os
import sys

from dotenv import find_dotenv, load_dotenv

# To import utility files in ../_shared folder
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from _shared.constants import (  # noqa: E402
    CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY,
    CONFIGURATION_NAME_FACE_API_ENDPOINT,
    DEFAULT_FACE_API_ACCOUNT_KEY,
    DEFAULT_FACE_API_ENDPOINT,
    IMAGE_NINE_FACES,
)
from _shared.helpers import beautify_json, get_logger  # noqa: E402


class GroupFaces():
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT)
        self.key = os.getenv(CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY)
        self.logger = get_logger("sample_face_grouping_async")

    async def group(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face.aio import FaceClient
        from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

        async with FaceClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as face_client:
            from pathlib import Path

            sample_file_path = Path(__file__).resolve().parent / ("../" + IMAGE_NINE_FACES)
            with open(sample_file_path, "rb") as fd:
                file_content = fd.read()

            detect_result = await face_client.detect(
                image_content=file_content,
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True)

            face_ids = [face.face_id for face in detect_result]
            self.logger.info(f"Detect {len(face_ids)} faces from the file '{sample_file_path}': {face_ids}")

            group_result = await face_client.group(face_ids=face_ids)
            self.logger.info(f"Group result: {beautify_json(group_result.as_dict())}")


async def main():
    sample = GroupFaces()
    await sample.group()

if __name__ == "__main__":
    asyncio.run(main())
