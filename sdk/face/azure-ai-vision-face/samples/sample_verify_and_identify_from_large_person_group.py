# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_verify_and_identify_from_large_person_group.py

DESCRIPTION:
    This sample demonstrates how to verify and identify faces from a large person group.

USAGE:
    python sample_verify_and_identify_from_large_person_group.py

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


class VerifyAndIdentifyFromLargePersonGroup:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT)
        self.key = os.getenv(CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY)
        self.logger = get_logger("sample_verify_and_identify_from_large_person_group")

    def verify_and_identify_from_large_person_group(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceAdministrationClient, FaceClient
        from azure.ai.vision.face.models import (
            FaceDetectionModel,
            FaceRecognitionModel,
        )

        with FaceAdministrationClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_admin_client, FaceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_client:

            large_person_group_id = "lpg_family1"
            # Prepare a LargePersonGroup which contains several person objects.
            self.logger.info(f"Create a LargePersonGroup, id = {large_person_group_id}")
            face_admin_client.large_person_group.create(
                large_person_group_id,
                name="Family 1",
                user_data="A sweet family",
                recognition_model=FaceRecognitionModel.RECOGNITION04,
            )

            # Add person and faces into the LargePersonGroup
            self.logger.info("Add person and faces into the LargePersonGroup")

            person1 = face_admin_client.large_person_group.create_person(
                large_person_group_id, name="Bill", user_data="Dad"
            )
            face_admin_client.large_person_group.add_face(
                large_person_group_id,
                person1.person_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_DAD_1)),
                user_data="Dad-1",
                detection_model=FaceDetectionModel.DETECTION03,
            )
            face_admin_client.large_person_group.add_face(
                large_person_group_id,
                person1.person_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_DAD_2)),
                user_data="Dad-2",
                detection_model=FaceDetectionModel.DETECTION03,
            )

            person2 = face_admin_client.large_person_group.create_person(
                large_person_group_id, name="Clare", user_data="Mom"
            )
            face_admin_client.large_person_group.add_face(
                large_person_group_id,
                person2.person_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_MOM_1)),
                user_data="Mom-1",
                detection_model=FaceDetectionModel.DETECTION03,
            )
            face_admin_client.large_person_group.add_face(
                large_person_group_id,
                person2.person_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_MOM_2)),
                user_data="Mom-2",
                detection_model=FaceDetectionModel.DETECTION03,
            )

            person3 = face_admin_client.large_person_group.create_person(
                large_person_group_id, name="Ron", user_data="Son"
            )
            face_admin_client.large_person_group.add_face(
                large_person_group_id,
                person3.person_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_SON_1)),
                user_data="Son-1",
                detection_model=FaceDetectionModel.DETECTION03,
            )
            face_admin_client.large_person_group.add_face(
                large_person_group_id,
                person3.person_id,
                helpers.read_file_content(helpers.get_image_path(TestImages.IMAGE_FAMILY_1_SON_2)),
                user_data="Son-2",
                detection_model=FaceDetectionModel.DETECTION03,
            )

            # Train the LargePersonGroup
            self.logger.info("Train the LargePersonGroup")
            poller = face_admin_client.large_person_group.begin_train(large_person_group_id, polling_interval=5)
            poller.wait()

            # Detect face from 'DAD_3'
            dad_3_image = helpers.get_image_path(TestImages.IMAGE_FAMILY_1_DAD_3)
            detect_result = face_client.detect(
                helpers.read_file_content(dad_3_image),
                detection_model=FaceDetectionModel.DETECTION03,
                recognition_model=FaceRecognitionModel.RECOGNITION04,
                return_face_id=True,
            )

            assert len(detect_result) == 1
            face_id = str(detect_result[0].face_id)

            # Verify the face with the person in LargePersonGroup
            self.logger.info("Verify the face with Bill")
            verify_result = face_client.verify_from_large_person_group(
                face_id=face_id, large_person_group_id=large_person_group_id, person_id=person1.person_id
            )
            self.logger.info(beautify_json(verify_result.as_dict()))

            self.logger.info("Verify the face with Clare")
            verify_result = face_client.verify_from_large_person_group(
                face_id=face_id, large_person_group_id=large_person_group_id, person_id=person2.person_id
            )
            self.logger.info(beautify_json(verify_result.as_dict()))

            # Identify the face from the LargePersonGroup
            self.logger.info("Identify the face from the LargePersonGroup")
            identify_result = face_client.identify_from_large_person_group(
                face_ids=[face_id], large_person_group_id=large_person_group_id
            )
            self.logger.info(beautify_json(identify_result[0].as_dict()))

            # Clean up: Remove the LargePersonGroup
            self.logger.info(f"Remove the LargePersonGroup {large_person_group_id}")
            face_admin_client.large_person_group.delete(large_person_group_id)


if __name__ == "__main__":
    sample = VerifyAndIdentifyFromLargePersonGroup()
    sample.verify_and_identify_from_large_person_group()
