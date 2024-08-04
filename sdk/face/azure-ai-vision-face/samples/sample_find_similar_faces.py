# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_find_similar_faces.py

DESCRIPTION:
    This sample demonstrates how to find similar faces from a specified list of face ids or a largeFaceList.

USAGE:
    python sample_find_similar_faces.py

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


class FindSimilarFaces:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(
            CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT
        )
        self.key = os.getenv(
            CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY
        )
        self.logger = get_logger("sample_findsimilar_faces")

    def find_similar_from_face_ids(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceClient
        from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

        with FaceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_client:
            # Detect faces from 'IMAGE_NINE_FACES'
            nine_faces_file_path = helpers.get_image_path(TestImages.IMAGE_NINE_FACES)
            detect_result1 = face_client.detect(
                helpers.read_file_content(nine_faces_file_path),
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True,
            )

            face_ids = [str(face.face_id) for face in detect_result1]
            self.logger.info(
                f"Detect {len(face_ids)} faces from the file '{nine_faces_file_path}': {face_ids}"
            )

            # Detect face from 'IMAGE_FINDSIMILAR'
            find_similar_file_path = helpers.get_image_path(
                TestImages.IMAGE_FINDSIMILAR
            )
            detect_result2 = face_client.detect(
                helpers.read_file_content(find_similar_file_path),
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True,
            )

            assert len(detect_result2) == 1
            face_id = str(detect_result2[0].face_id)
            self.logger.info(
                f"Detect 1 face from the file '{find_similar_file_path}': {face_id}"
            )

            # Call Find Similar
            # The default find similar mode is MATCH_PERSON
            find_similar_result1 = face_client.find_similar(
                face_id=face_id, face_ids=face_ids
            )
            self.logger.info("Find Similar with matchPerson mode:")
            for r in find_similar_result1:
                self.logger.info(f"{beautify_json(r.as_dict())}")


if __name__ == "__main__":
    sample = FindSimilarFaces()
    sample.find_similar_from_face_ids()
