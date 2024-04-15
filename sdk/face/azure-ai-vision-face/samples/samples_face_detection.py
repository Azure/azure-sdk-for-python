# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_face_detection.py

DESCRIPTION:
    This sample demonstrates how to detect faces and analyze faces from an image or binary data.

USAGE:
    python sample_face_detection.py

    Set the environment variables with your own values before running this sample:
    1) FACE_ENDPOINT - the endpoint to your Face resource.
    2) FACE_KEY - your Face API key.
"""
import os

from dotenv import find_dotenv, load_dotenv

from _shared.constants import (
    CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY,
    CONFIGURATION_NAME_FACE_API_ENDPOINT,
    DEFAULT_FACE_API_ACCOUNT_KEY,
    DEFAULT_FACE_API_ENDPOINT,
    DEFAULT_IMAGE_URL,
    IMAGE_DETECTION_5,
)
from _shared.helpers import beautify_json, get_logger


class DetectFaces():
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT)
        self.key = os.getenv(CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY)
        self.logger = get_logger("sample_face_detection")

    def detect(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceClient
        from azure.ai.vision.face.models import (
                FaceDetectionModel, FaceRecognitionModel, FaceAttributeTypeDetection03, FaceAttributeTypeRecognition04)

        with FaceClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as face_client:
            from pathlib import Path

            sample_file_path = Path(__file__).resolve().parent / IMAGE_DETECTION_5
            with open(sample_file_path, "rb") as fd:
                file_content = fd.read()

            result = face_client.detect(
                file_content,
                FaceDetectionModel.DETECTION_03,
                FaceRecognitionModel.RECOGNITION_04,
                True,  # return_face_id
                return_face_attributes=[
                    FaceAttributeTypeDetection03.HEAD_POSE,
                    FaceAttributeTypeDetection03.MASK,
                    FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION],
                return_face_landmarks=True,
                return_recognition_model=True,
                face_id_time_to_live=120)

            self.logger.info(f"Detect faces from the file: {sample_file_path}")
            for idx, face in enumerate(result):
                self.logger.info(f"----- Detection result: #{idx+1} -----")
                self.logger.info(f"Face: {beautify_json(face.as_dict())}")

    def detect_from_url(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceClient
        from azure.ai.vision.face.models import (
                FaceDetectionModel, FaceRecognitionModel, FaceAttributeTypeDetection01)

        with FaceClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as face_client:
            sample_url = DEFAULT_IMAGE_URL
            result = face_client.detect_from_url(
                sample_url,
                FaceDetectionModel.DETECTION_01,
                FaceRecognitionModel.RECOGNITION_04,
                False,  # return_face_id
                return_face_attributes=[
                    FaceAttributeTypeDetection01.ACCESSORIES,
                    FaceAttributeTypeDetection01.EXPOSURE,
                    FaceAttributeTypeDetection01.GLASSES,
                    FaceAttributeTypeDetection01.NOISE])

            self.logger.info(f"Detect faces from the url: {sample_url}")
            for idx, face in enumerate(result):
                self.logger.info(f"----- Detection result: #{idx+1} -----")
                self.logger.info(f"Face: {beautify_json(face.as_dict())}")


if __name__ == "__main__":
    sample = DetectFaces()
    sample.detect()
    sample.detect_from_url()
