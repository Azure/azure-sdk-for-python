# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import io
import pytest
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.ai.vision.face.models import (
    FaceDetectionModel,
    FaceRecognitionModel,
    FaceAttributeTypeDetection03,
    FaceAttributeTypeRecognition04,
)

from preparers import FaceClientPreparer, FacePreparer
from _shared.constants import TestImages
from _shared import helpers


class TestDetection(AzureRecordedTestCase):
    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_from_image_content(self, client, **kwargs):
        sample_file_path = helpers.get_image_path(TestImages.IMAGE_DETECTION_1)
        result = client.detect(
            image_content=helpers.read_file_content(sample_file_path),
            detection_model=FaceDetectionModel.DETECTION_03,
            recognition_model=FaceRecognitionModel.RECOGNITION_04,
            return_face_id=False,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
            ],
            return_face_landmarks=True,
        )

        assert result is not None

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_from_url(self, client, **kwargs):
        sample_url = TestImages.IMAGE_URL
        result = client.detect(
            url=sample_url,
            detection_model=FaceDetectionModel.DETECTION_03,
            recognition_model=FaceRecognitionModel.RECOGNITION_04,
            return_face_id=False,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
            ],
            return_face_landmarks=True,
        )

        assert result is not None

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_from_body_with_image_content(self, client, **kwargs):
        sample_file_path = helpers.get_image_path(TestImages.IMAGE_DETECTION_1)
        result = client.detect(
            helpers.read_file_content(sample_file_path),
            content_type="application/octet-stream",
            detection_model=FaceDetectionModel.DETECTION_03,
            recognition_model=FaceRecognitionModel.RECOGNITION_04,
            return_face_id=False,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
            ],
            return_face_landmarks=True,
        )

        assert result is not None

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_from_body_with_image(self, client, **kwargs):
        sample_file_path = helpers.get_image_path(TestImages.IMAGE_DETECTION_1)
        with open(sample_file_path, "rb") as fd:
            result = client.detect(
                fd,
                content_type="application/octet-stream",
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=False,
                return_face_attributes=[
                    FaceAttributeTypeDetection03.HEAD_POSE,
                    FaceAttributeTypeDetection03.MASK,
                    FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
                ],
                return_face_landmarks=True,
            )

        assert result is not None

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_from_body_with_json_dict(self, client, **kwargs):
        sample_url = TestImages.IMAGE_URL
        result = client.detect(
            {"url": sample_url},
            content_type="application/json",
            detection_model=FaceDetectionModel.DETECTION_03,
            recognition_model=FaceRecognitionModel.RECOGNITION_04,
            return_face_id=False,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
            ],
            return_face_landmarks=True,
        )

        assert result is not None

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_from_body_with_json_byte(self, client, **kwargs):
        sample_url = TestImages.IMAGE_URL
        result = client.detect(
            f'{{"url": "{sample_url}"}}'.encode("utf-8"),
            content_type="application/json",
            detection_model=FaceDetectionModel.DETECTION_03,
            recognition_model=FaceRecognitionModel.RECOGNITION_04,
            return_face_id=False,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
            ],
            return_face_landmarks=True,
        )

        assert result is not None

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_from_body_with_json_byte_io(self, client, **kwargs):
        sample_url = TestImages.IMAGE_URL
        result = client.detect(
            io.BytesIO(f'{{"url": "{sample_url}"}}'.encode("utf-8")),
            content_type="application/json",
            detection_model=FaceDetectionModel.DETECTION_03,
            recognition_model=FaceRecognitionModel.RECOGNITION_04,
            return_face_id=False,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
            ],
            return_face_landmarks=True,
        )

        assert result is not None

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_without_anything(self, client, **kwargs):
        with pytest.raises(TypeError) as ex:
            client.detect()

            assert "missing required argument: body, url or image_content" == str(
                ex.value
            )

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_with_both_url_and_image_content(self, client, **kwargs):
        with pytest.raises(TypeError) as ex:
            client.detect(
                image_content=b"fakeimagecontent",
                url="fakeurl",
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=False,
            )

            assert (
                "setting url and image_content at the same time is not allowed"
                == str(ex.value)
            )

    @FacePreparer()
    @FaceClientPreparer()
    @recorded_by_proxy
    def test_detect_without_content_type(self, client, **kwargs):
        with pytest.raises(TypeError) as ex:
            client.detect(
                b"fakeimagecontent",
                detection_model=FaceDetectionModel.DETECTION_03,
                recognition_model=FaceRecognitionModel.RECOGNITION_04,
                return_face_id=False,
            )

            assert "content_type should be set together with body" == str(ex.value)
