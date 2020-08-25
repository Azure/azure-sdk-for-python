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
    BlobProperties,
)

from azure.storage.blob._deserialize import deserialize_ors_policies


class StorageObjectReplicationTest(StorageTestCase):
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
        self.assertEqual(len(result), 2)  # 2 policies
        self.assertEqual(len(result[0].rules), 2)  # 2 rules for policy 111
        self.assertEqual(len(result[1].rules), 2)  # 2 rules for policy 222

        # check individual result
        self.assertEqual(result[0].rules[0].status, 'Completed' if result[0].rules[0].rule_id == '111' else 'Failed')
        self.assertEqual(result[0].rules[1].status, 'Failed' if result[0].rules[1].rule_id == '222' else 'Completed')
        self.assertEqual(result[1].rules[0].status, 'Completed' if result[1].rules[0].rule_id == '111' else 'Failed')
        self.assertEqual(result[1].rules[1].status, 'Failed' if result[1].rules[1].rule_id == '222' else 'Completed')

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
        for replication_policy in props.object_replication_source_properties:
            self.assertNotEqual(replication_policy.policy_id, '')
            self.assertIsNotNone(replication_policy.rules)

            for rule in replication_policy.rules:
                self.assertNotEqual(rule.rule_id, '')
                self.assertIsNotNone(rule.status)
                self.assertNotEqual(rule.status, '')

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
