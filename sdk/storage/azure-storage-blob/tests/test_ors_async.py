# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from _shared.asynctestcase import AsyncStorageTestCase
from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer
from azure.storage.blob import BlobProperties
from azure.storage.blob.aio import BlobServiceClient


# ------------------------------------------------------------------------------
class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """

    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageObjectReplicationTest(StorageTestCase):
    SRC_CONTAINER = "test1"
    DST_CONTAINER = "test2"
    BLOB_NAME = "bla.txt"

    # -- Test cases for Object Replication enabled account ----------------------------------------------
    # TODO the tests will temporarily use designated account, containers, and blobs to check the OR headers
    # TODO use generated account and set OR policy dynamically

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_ors_source(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        blob = bsc.get_blob_client(container=self.SRC_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = await blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertIsNotNone(props.object_replication_source_properties)
        for replication_policy in props.object_replication_source_properties:
            self.assertNotEqual(replication_policy.policy_id, '')
            self.assertIsNotNone(replication_policy.rules)

            for rule in replication_policy.rules:
                self.assertNotEqual(rule.rule_id, '')
                self.assertIsNotNone(rule.status)
                self.assertNotEqual(rule.status, '')

        # Check that the download function gives back the same result
        stream = await blob.download_blob()
        self.assertEqual(stream.properties.object_replication_source_properties,
                         props.object_replication_source_properties)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_ors_destination(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        blob = bsc.get_blob_client(container=self.DST_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = await blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertIsNotNone(props.object_replication_destination_policy)

        # Check that the download function gives back the same result
        stream = await blob.download_blob()
        self.assertEqual(stream.properties.object_replication_destination_policy,
                         props.object_replication_destination_policy)

# ------------------------------------------------------------------------------
