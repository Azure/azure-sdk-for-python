# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.storage.blob import BlobProperties
from azure.storage.blob.aio import BlobServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer


# ------------------------------------------------------------------------------


class TestStorageObjectReplicationAsync(AsyncStorageRecordedTestCase):
    SRC_CONTAINER = "test1"
    DST_CONTAINER = "test2"
    BLOB_NAME = "bla.txt"

    # -- Test cases for Object Replication enabled account ----------------------------------------------
    # TODO the tests will temporarily use designated account, containers, and blobs to check the OR headers
    # TODO use generated account and set OR policy dynamically

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_ors_source(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
        )
        blob = bsc.get_blob_client(container=self.SRC_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = await blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.object_replication_source_properties is not None
        for replication_policy in props.object_replication_source_properties:
            assert replication_policy.policy_id != ''
            assert replication_policy.rules is not None

            for rule in replication_policy.rules:
                assert rule.rule_id != ''
                assert rule.status is not None
                assert rule.status != ''

        # Check that the download function gives back the same result
        stream = await blob.download_blob()
        assert stream.properties.object_replication_source_properties == props.object_replication_source_properties

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_ors_destination(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
        )
        blob = bsc.get_blob_client(container=self.DST_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = await blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.object_replication_destination_policy is not None

        # Check that the download function gives back the same result
        stream = await blob.download_blob()
        assert stream.properties.object_replication_destination_policy == props.object_replication_destination_policy

# ------------------------------------------------------------------------------
