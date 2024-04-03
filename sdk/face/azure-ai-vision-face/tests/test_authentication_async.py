# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from pathlib import Path

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.ai.vision.face.models import (
        FaceDetectionModel, FaceRecognitionModel, FaceAttributeTypeDetection03, FaceAttributeTypeRecognition04)

from preparers import AsyncFaceClientPreparer, FacePreparer
from _shared.constants import IMAGE_DETECTION_1


class TestAuthenticationAsync(AzureRecordedTestCase):
    @FacePreparer()
    @AsyncFaceClientPreparer()
    @recorded_by_proxy_async
    async def test_face_client_api_key_authentication(self, client, **kwargs):
        sample_file_path = Path(__file__).resolve().parent / IMAGE_DETECTION_1
        with open(sample_file_path, "rb") as fd:
            file_content = fd.read()

        result = await client.detect(
            file_content,
            FaceDetectionModel.DETECTION_03,
            FaceRecognitionModel.RECOGNITION_04,
            False,  # return_face_id
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION],
            return_face_landmarks=True)

        assert result is not None

        await client.close()
