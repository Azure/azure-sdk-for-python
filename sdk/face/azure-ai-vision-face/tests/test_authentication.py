# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from pathlib import Path

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.ai.vision.face.models import (
        FaceDetectionModel, FaceRecognitionModel, FaceAttributeTypeDetection03, FaceAttributeTypeRecognition04)

from preparers import FaceClientPreparer, FacePreparer
from _shared.constants import IMAGE_DETECTION_1


class TestAuthentication(AzureRecordedTestCase):
    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_face_client_api_key_authentication(self, client, **kwargs):
        sample_file_path = Path(__file__).resolve().parent / IMAGE_DETECTION_1
        with open(sample_file_path, "rb") as fd:
            file_content = fd.read()

        result = client.detect(
            file_content,
            detection_model=FaceDetectionModel.DETECTION_03,
            recognition_model=FaceRecognitionModel.RECOGNITION_04,
            return_face_id=False,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION],
            return_face_landmarks=True)

        assert result is not None
