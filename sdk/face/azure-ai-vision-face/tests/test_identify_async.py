# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.ai.vision.face.aio import FaceClient, FaceAdministrationClient
from azure.ai.vision.face.models import (
    FaceDetectionModel,
    FaceRecognitionModel,
)

from preparers import AsyncFaceClientPreparer, FacePreparer, AsyncFaceAdministrationClientPreparer
from _shared.constants import TestImages
from _shared import helpers


class TestIdentify(AzureRecordedTestCase):
    test_images = [
        TestImages.IMAGE_FAMILY_1_DAD_1,
        TestImages.IMAGE_FAMILY_1_DAUGHTER_1,
        TestImages.IMAGE_FAMILY_1_MOM_1,
        TestImages.IMAGE_FAMILY_1_SON_1,
    ]
    group_id = "identify"

    async def _setup_faces(self, client: FaceClient):
        face_ids = []
        image_path = helpers.get_image_path(TestImages.IMAGE_IDENTIFICATION1)
        result = await client.detect(
            helpers.read_file_content(image_path),
            detection_model=FaceDetectionModel.DETECTION03,
            recognition_model=FaceRecognitionModel.RECOGNITION04,
            return_face_id=True,
        )
        for face in result:
            face_ids.append(face.face_id)
        return face_ids

    async def _setup_group(self, operations):
        await operations.create(self.group_id, name=self.group_id, recognition_model=FaceRecognitionModel.RECOGNITION04)

        person_ids = []
        for image in self.test_images:
            result = await operations.create_person(self.group_id, name="test_person")
            assert result.person_id
            person_ids.append(result.person_id)
            image_path = helpers.get_image_path(image)
            await operations.add_face(
                self.group_id,
                result.person_id,
                helpers.read_file_content(image_path),
                detection_model=FaceDetectionModel.DETECTION03,
            )

        poller = await operations.begin_train(self.group_id)
        await poller.wait()

        return person_ids

    async def _teardown_group(self, operations):
        await operations.delete(self.group_id)

    @FacePreparer()
    @AsyncFaceClientPreparer()
    @AsyncFaceAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_identify_from_large_person_group(
        self, client: FaceClient, administration_client: FaceAdministrationClient
    ):
        face_ids = await self._setup_faces(client)
        await self._setup_group(administration_client.large_person_group)

        identify_result = await client.identify_from_large_person_group(
            face_ids=face_ids, large_person_group_id=self.group_id
        )

        assert len(identify_result) == len(face_ids)
        for result in identify_result:
            assert result.candidates is not None
            assert result.face_id is not None
            for candidate in result.candidates:
                assert candidate.confidence is not None
                assert candidate.person_id is not None

        await self._teardown_group(administration_client.large_person_group)
