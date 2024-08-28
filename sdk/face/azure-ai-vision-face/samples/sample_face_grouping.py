# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_face_grouping.py

DESCRIPTION:
    This sample demonstrates how to group faces based on face similarity.

USAGE:
    python sample_face_grouping.py

    Set the environment variables with your own values before running this sample:
    1) AZURE_FACE_API_ENDPOINT - the endpoint to your Face resource.
    2) AZURE_FACE_API_ACCOUNT_KEY - your Face API key.
"""
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


class GroupFaces:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(
            CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT
        )
        self.key = os.getenv(
            CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY
        )
        self.logger = get_logger("sample_face_grouping")

    def group(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceClient
        from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

        with FaceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_client:
            sample_file_path = helpers.get_image_path(TestImages.IMAGE_NINE_FACES)
            detect_result = face_client.detect(
                helpers.read_file_content(sample_file_path),
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True,
            )

            face_ids = [str(face.face_id) for face in detect_result]
            self.logger.info(
                f"Detect {len(face_ids)} faces from the file '{sample_file_path}': {face_ids}"
            )

            group_result = face_client.group(face_ids=face_ids)
            self.logger.info(f"Group result: {beautify_json(group_result.as_dict())}")


if __name__ == "__main__":
    sample = GroupFaces()
    sample.group()
