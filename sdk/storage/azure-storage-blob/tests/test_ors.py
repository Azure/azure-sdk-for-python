# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer

from azure.storage.blob import (
    BlobServiceClient,
    BlobType,
    BlobProperties,
)

from azure.storage.blob._deserialize import deserialize_ors_policies


class StorageObjectReplicationTest(StorageTestCase):
    SRC_CONTAINER = "test1"
    DST_CONTAINER = "test2"
    # BLOB_NAME = "pythonorstest"
    BLOB_NAME = "bla.txt"

    # -- Test cases for Object Replication enabled account ----------------------------------------------
    # TODO the tests will temporarily use designated account, containers, and blobs to check the OR headers

    def test_deserialize_ors_policies(self):
        class StubHTTPResponse:
            headers = {}

        response = StubHTTPResponse()
        response.headers = {
            'x-ms-or-111_111': 'Completed',
            'x-ms-or-111_222': 'Failed',
            'x-ms-or-222_111': 'Completed',
            'x-ms-or-222_222': 'Failed',
            'x-ms-or-policy-id': '333',  # to be ignored
            'x-ms-not-related': 'garbage',  # to be ignored
        }

        result = deserialize_ors_policies(response)
        self.assertEqual(len(result), 2)  # 2 policies
        self.assertEqual(len(result.get('111')), 2)  # 2 rules for policy 111
        self.assertEqual(len(result.get('222')), 2)  # 2 rules for policy 222

        # check individual result
        self.assertEqual(result.get('111').get('111'), 'Completed')
        self.assertEqual(result.get('111').get('222'), 'Failed')
        self.assertEqual(result.get('222').get('111'), 'Completed')
        self.assertEqual(result.get('222').get('222'), 'Failed')

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_ors_source(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key)
        blob = bsc.get_blob_client(container=self.SRC_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertIsNotNone(props.object_replication_source_properties)
        for policy, rule_result in props.object_replication_source_properties.items():
            self.assertNotEqual(policy, '')
            self.assertIsNotNone(rule_result)

            for rule_id, result in rule_result.items():
                self.assertNotEqual(rule_id, '')
                self.assertIsNotNone(result)
                self.assertNotEqual(result, '')

        # Check that the download function gives back the same result
        stream = blob.download_blob()
        self.assertEqual(stream.properties.object_replication_source_properties,
                         props.object_replication_source_properties)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_ors_destination(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key)
        blob = bsc.get_blob_client(container=self.DST_CONTAINER, blob=self.BLOB_NAME)

        # Act
        props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertIsNotNone(props.object_replication_destination_policy)

        # Check that the download function gives back the same result
        stream = blob.download_blob()
        self.assertEqual(stream.properties.object_replication_destination_policy,
                         props.object_replication_destination_policy)

# ------------------------------------------------------------------------------
