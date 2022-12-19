# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.storage.blob import BlobProperties, BlobServiceClient
from azure.storage.blob._deserialize import deserialize_ors_policies

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestStorageObjectReplication(StorageRecordedTestCase):
    SRC_CONTAINER = "test1"
    DST_CONTAINER = "test2"
    BLOB_NAME = "bla.txt"

    # -- Test cases for Object Replication enabled account ----------------------------------------------
    # TODO the tests will temporarily use designated account, containers, and blobs to check the OR headers
    # TODO use generated account and set OR policy dynamically

    # mock a response to test the deserializer
    def test_deserialize_ors_policies(self):
        headers = {
            'x-ms-or-111_111': 'Completed',
            'x-ms-or-111_222': 'Failed',
            'x-ms-or-222_111': 'Completed',
            'x-ms-or-222_222': 'Failed',
            'x-ms-or-policy-id': '333',  # to be ignored
            'x-ms-not-related': 'garbage',  # to be ignored
        }

        result = deserialize_ors_policies(headers)
        assert len(result) == 2  # 2 policies
        assert len(result[0].rules) == 2  # 2 rules for policy 111
        assert len(result[1].rules) == 2  # 2 rules for policy 222

        # check individual result
        assert result[0].rules[0].status == 'Completed' if result[0].rules[0].rule_id == '111' else 'Failed'
        assert result[0].rules[1].status == 'Failed' if result[0].rules[1].rule_id == '222' else 'Completed'
        assert result[1].rules[0].status == 'Completed' if result[1].rules[0].rule_id == '111' else 'Failed'
        assert result[1].rules[1].status == 'Failed' if result[1].rules[1].rule_id == '222' else 'Completed'

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy
    def test_ors_source(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        blob = bsc.get_blob_client(container=self.SRC_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = blob.get_blob_properties()

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
        stream = blob.download_blob()
        assert stream.properties.object_replication_source_properties == props.object_replication_source_properties

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy
    def test_ors_destination(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        blob = bsc.get_blob_client(container=self.DST_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.object_replication_destination_policy is not None

        # Check that the download function gives back the same result
        stream = blob.download_blob()
        assert stream.properties.object_replication_destination_policy == props.object_replication_destination_policy

# ------------------------------------------------------------------------------
