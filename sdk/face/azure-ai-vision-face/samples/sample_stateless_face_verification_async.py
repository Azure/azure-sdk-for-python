# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_stateless_face_verification_async.py

DESCRIPTION:
    This sample demonstrates verifying whether two faces belong to a same person.

USAGE:
    python sample_stateless_face_verification_async.py

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


class StatelessFaceVerification:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(
            CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT
        )
        self.key = os.getenv(
            CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY
        )
        self.logger = get_logger("sample_stateless_face_verification_async")

    async def verify_face_to_face(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face.aio import FaceClient
        from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

        async with FaceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_client:
            dad_picture1 = helpers.get_image_path(TestImages.IMAGE_FAMILY_1_DAD_1)
            detect_result1 = await face_client.detect(
                helpers.read_file_content(dad_picture1),
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True,
            )
            assert len(detect_result1) == 1
            dad_face_id1 = str(detect_result1[0].face_id)
            self.logger.info(
                f"Detect 1 face from the file '{dad_picture1}': {dad_face_id1}"
            )

            dad_picture2 = helpers.get_image_path(TestImages.IMAGE_FAMILY_1_DAD_2)
            detect_result2 = await face_client.detect(
                helpers.read_file_content(dad_picture2),
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True,
            )
            assert len(detect_result2) == 1
            dad_face_id2 = str(detect_result2[0].face_id)
            self.logger.info(
                f"Detect 1 face from the file '{dad_picture2}': {dad_face_id2}"
            )

            # Call Verify to check if dad_face_id1 and dad_face_id2 belong to the same person.
            verify_result1 = await face_client.verify_face_to_face(
                face_id1=dad_face_id1, face_id2=dad_face_id2
            )
            self.logger.info(
                f"Verify if the faces in '{TestImages.IMAGE_FAMILY_1_DAD_1}' and '{TestImages.IMAGE_FAMILY_1_DAD_2}'"
                f" belongs to the same person."
            )
            self.logger.info(f"{beautify_json(verify_result1.as_dict())}")

            man_picture = helpers.get_image_path(TestImages.IMAGE_FAMILY_3_Man_1)
            detect_result3 = await face_client.detect(
                helpers.read_file_content(man_picture),
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=True,
            )
            assert len(detect_result3) == 1
            man_face_id = str(detect_result3[0].face_id)
            self.logger.info(
                f"Detect 1 face from the file '{man_picture}': {man_face_id}"
            )

            # Call Verify to check if dad_face_id1 and man_face_id belong to the same person.
            verify_result2 = await face_client.verify_face_to_face(
                face_id1=dad_face_id1, face_id2=man_face_id
            )
            self.logger.info(
                f"Verify if the faces in '{TestImages.IMAGE_FAMILY_1_DAD_1}' and '{TestImages.IMAGE_FAMILY_3_Man_1}'"
                f" belongs to the same person."
            )
            self.logger.info(f"{beautify_json(verify_result2.as_dict())}")


async def main():
    sample = StatelessFaceVerification()
    await sample.verify_face_to_face()


if __name__ == "__main__":
    asyncio.run(main())
