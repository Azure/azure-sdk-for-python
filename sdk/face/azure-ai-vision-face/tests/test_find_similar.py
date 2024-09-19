# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.ai.vision.face import FaceClient, FaceAdministrationClient
from azure.ai.vision.face.models import (
    FaceDetectionModel,
    FaceRecognitionModel,
)

from preparers import FaceClientPreparer, FacePreparer, FaceAdministrationClientPreparer
from _shared.constants import TestImages
from _shared import helpers


class TestFindSimilar(AzureRecordedTestCase):
    test_images = [TestImages.IMAGE_FAMILY_1_MOM_1, TestImages.IMAGE_FAMILY_2_LADY_1]
    list_id = "findsimilar"

    def _setup_faces(self, client: FaceClient):
        face_ids = []
        for image in self.test_images:
            image_path = helpers.get_image_path(image)
            result = client.detect(
                helpers.read_file_content(image_path),
                detection_model=FaceDetectionModel.DETECTION03,
                recognition_model=FaceRecognitionModel.RECOGNITION04,
                return_face_id=True,
            )
            face_ids.append(result[0].face_id)
        return face_ids

    def _setup_large_face_list(self, client: FaceAdministrationClient):
        operations = client.large_face_list
        operations.create(self.list_id, name=self.list_id, recognition_model=FaceRecognitionModel.RECOGNITION04)

        persisted_face_ids = []
        for image in self.test_images:
            image_path = helpers.get_image_path(image)
            result = operations.add_face(
                self.list_id, helpers.read_file_content(image_path), detection_model=FaceDetectionModel.DETECTION03
            )
            assert result.persisted_face_id
            persisted_face_ids.append(result.persisted_face_id)

        poller = operations.begin_train(self.list_id, polling_interval=3)
        poller.wait()

        return persisted_face_ids

    # TODO: Use fixtures to replace teardown methods
    def _teardown_large_face_list(self, client: FaceAdministrationClient):
        client.large_face_list.delete(self.list_id)

    @FacePreparer()
    @FaceClientPreparer()
    @FaceAdministrationClientPreparer()
    @recorded_by_proxy
    def test_find_similar_from_large_face_list(
        self, client: FaceClient, administration_client: FaceAdministrationClient
    ):
        face_ids = self._setup_faces(client)
        persisted_face_ids = self._setup_large_face_list(administration_client)

        similar_faces = client.find_similar_from_large_face_list(face_id=face_ids[0], large_face_list_id=self.list_id)
        assert similar_faces[0].persisted_face_id == persisted_face_ids[0]
        assert similar_faces[0].confidence > 0.9

        self._teardown_large_face_list(administration_client)
