# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_face_detection_async.py

DESCRIPTION:
    This sample demonstrates how to detect faces and analyze faces from an image or binary data.

USAGE:
    python sample_face_detection_async.py

    Set the environment variables with your own values before running this sample:
    1) AZURE_FACE_API_ENDPOINT - the endpoint to your Face resource.
    2) AZURE_FACE_API_ACCOUNT_KEY - your Face API key.
"""
import asyncio
import os

from dotenv import find_dotenv, load_dotenv

from shared.constants import (
    CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY,
    CONFIGURATION_NAME_FACE_API_ENDPOINT,
    DEFAULT_FACE_API_ACCOUNT_KEY,
    DEFAULT_FACE_API_ENDPOINT,
    TestImages,
)
from shared import helpers
from shared.helpers import beautify_json, get_logger


class DetectFaces:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(
            CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT
        )
        self.key = os.getenv(
            CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY
        )
        self.logger = get_logger("sample_face_detection_async")

    async def detect(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face.aio import FaceClient
        from azure.ai.vision.face.models import (
            FaceDetectionModel,
            FaceRecognitionModel,
            FaceAttributeTypeDetection03,
            FaceAttributeTypeRecognition04,
        )

        async with FaceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_client:
            sample_file_path = helpers.get_image_path(TestImages.IMAGE_DETECTION_5)
            result = await face_client.detect(
                helpers.read_file_content(sample_file_path),
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True,
                return_face_attributes=[
                    FaceAttributeTypeDetection03.BLUR,
                    FaceAttributeTypeDetection03.HEAD_POSE,
                    FaceAttributeTypeDetection03.MASK,
                    FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
                ],
                return_face_landmarks=True,
                return_recognition_model=True,
                face_id_time_to_live=120,
            )

            self.logger.info(f"Detect faces from the file: {sample_file_path}")
            for idx, face in enumerate(result):
                self.logger.info(f"----- Detection result: #{idx+1} -----")
                self.logger.info(f"Face: {beautify_json(face.as_dict())}")

    async def detect_from_url(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face.aio import FaceClient
        from azure.ai.vision.face.models import (
            FaceDetectionModel,
            FaceRecognitionModel,
            FaceAttributeTypeDetection01,
        )

        async with FaceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_client:
            sample_url = TestImages.DEFAULT_IMAGE_URL
            result = await face_client.detect_from_url(
                url=sample_url,
                detection_model=FaceDetectionModel.DETECTION_01,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=False,
                return_face_attributes=[
                    FaceAttributeTypeDetection01.ACCESSORIES,
                    FaceAttributeTypeDetection01.EXPOSURE,
                    FaceAttributeTypeDetection01.GLASSES,
                    FaceAttributeTypeDetection01.NOISE,
                ],
            )

            self.logger.info(f"Detect faces from the url: {sample_url}")
            for idx, face in enumerate(result):
                self.logger.info(f"----- Detection result: #{idx+1} -----")
                self.logger.info(f"Face: {beautify_json(face.as_dict())}")


async def main():
    sample = DetectFaces()
    await sample.detect()
    await sample.detect_from_url()


if __name__ == "__main__":
    asyncio.run(main())
