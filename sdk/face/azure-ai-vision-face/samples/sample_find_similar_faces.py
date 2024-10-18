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
        self.endpoint = os.getenv(CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT)
        self.key = os.getenv(CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY)
        self.logger = get_logger("sample_findsimilar_faces")

    def find_similar_from_face_ids(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceClient
        from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

        with FaceClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as face_client:
            # Detect faces from 'IMAGE_NINE_FACES'
            nine_faces_file_path = helpers.get_image_path(TestImages.IMAGE_NINE_FACES)
            detect_result1 = face_client.detect(
                helpers.read_file_content(nine_faces_file_path),
                detection_model=FaceDetectionModel.DETECTION03,
                recognition_model=FaceRecognitionModel.RECOGNITION04,
                return_face_id=True,
            )

            face_ids = [str(face.face_id) for face in detect_result1]
            self.logger.info(f"Detect {len(face_ids)} faces from the file '{nine_faces_file_path}': {face_ids}")

            # Detect face from 'IMAGE_FINDSIMILAR'
            find_similar_file_path = helpers.get_image_path(TestImages.IMAGE_FINDSIMILAR)
            detect_result2 = face_client.detect(
                helpers.read_file_content(find_similar_file_path),
                detection_model=FaceDetectionModel.DETECTION03,
                recognition_model=FaceRecognitionModel.RECOGNITION04,
                return_face_id=True,
            )

            assert len(detect_result2) == 1
            face_id = str(detect_result2[0].face_id)
            self.logger.info(f"Detect 1 face from the file '{find_similar_file_path}': {face_id}")

            # Call Find Similar
            # The default find similar mode is MATCH_PERSON
            find_similar_result1 = face_client.find_similar(face_id=face_id, face_ids=face_ids)
            self.logger.info("Find Similar with matchPerson mode:")
            for r in find_similar_result1:
                self.logger.info(f"{beautify_json(r.as_dict())}")

    def find_similar_from_large_face_list(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceAdministrationClient, FaceClient
        from azure.ai.vision.face.models import (
            FaceDetectionModel,
            FaceRecognitionModel,
            FindSimilarMatchMode,
        )

        with FaceAdministrationClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_admin_client, FaceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_client:

            large_face_list_id = "lfl01"
            # Prepare a LargeFaceList which contains several faces.
            self.logger.info(f"Create a LargeFaceList, id = {large_face_list_id}")
            face_admin_client.large_face_list.create(
                large_face_list_id,
                name="List of Face",
                user_data="Large Face List for Test",
                recognition_model=FaceRecognitionModel.RECOGNITION04,
            )

            # Add faces into the largeFaceList
            self.logger.info(f"Add faces into the LargeFaceList {large_face_list_id}")
            face_admin_client.large_face_list.add_face(
                large_face_list_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_MOM_1)),
                detection_model=FaceDetectionModel.DETECTION02,
                user_data="Lady1-1",
            )
            face_admin_client.large_face_list.add_face(
                large_face_list_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_MOM_2)),
                detection_model=FaceDetectionModel.DETECTION02,
                user_data="Lady1-2",
            )
            face_admin_client.large_face_list.add_face(
                large_face_list_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_2_LADY_1)),
                detection_model=FaceDetectionModel.DETECTION02,
                user_data="Lady2-1",
            )
            face_admin_client.large_face_list.add_face(
                large_face_list_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_2_LADY_2)),
                detection_model=FaceDetectionModel.DETECTION02,
                user_data="Lady2-2",
            )
            face_admin_client.large_face_list.add_face(
                large_face_list_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_3_LADY_1)),
                detection_model=FaceDetectionModel.DETECTION02,
                user_data="Lady3-1",
            )

            # The LargeFaceList should be trained to make it ready for find similar operation.
            self.logger.info(f"Train the LargeFaceList {large_face_list_id}, and wait until the operation completes.")
            poller = face_admin_client.large_face_list.begin_train(large_face_list_id, polling_interval=30)
            poller.wait()  # Keep polling until the "Train" operation completes.

            # Detect face from 'IMAGE_FINDSIMILAR'
            find_similar_file_path = helpers.get_image_path(TestImages.IMAGE_FINDSIMILAR)
            detect_result = face_client.detect(
                helpers.read_file_content(find_similar_file_path),
                detection_model=FaceDetectionModel.DETECTION03,
                recognition_model=FaceRecognitionModel.RECOGNITION04,
                return_face_id=True,
            )

            assert len(detect_result) == 1
            face_id = str(detect_result[0].face_id)
            self.logger.info(f"Detect 1 face from the file '{find_similar_file_path}': {face_id}")

            # Call Find Similar
            find_similar_result = face_client.find_similar_from_large_face_list(
                face_id=face_id,
                large_face_list_id=large_face_list_id,
                max_num_of_candidates_returned=3,
                mode=FindSimilarMatchMode.MATCH_FACE,
            )
            self.logger.info("Find Similar with matchFace mode:")
            for r in find_similar_result:
                self.logger.info(f"{beautify_json(r.as_dict())}")

            # Clean up: Remove the LargeFaceList
            self.logger.info(f"Remove the LargeFaceList {large_face_list_id}")
            face_admin_client.large_face_list.delete(large_face_list_id)


if __name__ == "__main__":
    sample = FindSimilarFaces()
    sample.find_similar_from_face_ids()
    sample.find_similar_from_large_face_list()
