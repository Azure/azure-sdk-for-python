# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform
from datetime import datetime, timedelta

from azure.core.exceptions import AzureError, ResourceExistsError
from azure.storage.blob import (
    VERSION,
    generate_blob_sas,
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobSasPermissions
)
from azure.storage.blob._generated.version import VERSION
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'


class StorageClientTest(StorageTestCase):
    def setUp(self):
        super(StorageClientTest, self).setUp()
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = VERSION
        self.container_name = self.get_resource_name('utcontainer')

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self, prefix=TEST_BLOB_PREFIX):
        return self.get_resource_name(prefix)

    def _create_container(self, bsc):
        container = bsc.get_container_client(self.container_name)
        try:
            container.create_container()
        except ResourceExistsError:
            pass
        return container

    # --Test Cases--------------------------------------------------------------

    def test_service_client_api_version_property(self):
        service_client = BlobServiceClient(
            "https://foo.blob.core.windows.net/account",
            credential="fake_key")
        self.assertEqual(service_client.api_version, self.api_version_2)
        self.assertEqual(service_client._client._config.version, self.api_version_2)

        with pytest.raises(AttributeError):
            service_client.api_version = "foo"

        service_client = BlobServiceClient(
            "https://foo.blob.core.windows.net/account",
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(service_client.api_version, self.api_version_1)
        self.assertEqual(service_client._client._config.version, self.api_version_1)

        container_client = service_client.get_container_client("foo")
        self.assertEqual(container_client.api_version, self.api_version_1)
        self.assertEqual(container_client._client._config.version, self.api_version_1)

        blob_client = service_client.get_blob_client("foo", "bar")
        self.assertEqual(blob_client.api_version, self.api_version_1)
        self.assertEqual(blob_client._client._config.version, self.api_version_1)

    def test_container_client_api_version_property(self):
        container_client = ContainerClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            credential="fake_key")
        self.assertEqual(container_client.api_version, self.api_version_2)
        self.assertEqual(container_client._client._config.version, self.api_version_2)

        container_client = ContainerClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(container_client.api_version, self.api_version_1)
        self.assertEqual(container_client._client._config.version, self.api_version_1)

        blob_client = container_client.get_blob_client("foo")
        self.assertEqual(blob_client.api_version, self.api_version_1)
        self.assertEqual(blob_client._client._config.version, self.api_version_1)

    def test_blob_client_api_version_property(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            self._get_blob_reference(),
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(blob_client.api_version, self.api_version_1)
        self.assertEqual(blob_client._client._config.version, self.api_version_1)

        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            self._get_blob_reference(),
            credential="fake_key")
        self.assertEqual(blob_client.api_version, self.api_version_2)
        self.assertEqual(blob_client._client._config.version, self.api_version_2)

    def test_invalid_api_version(self):
        with pytest.raises(ValueError) as error:
            BlobServiceClient(
                "https://foo.blob.core.windows.net/account",
                credential="fake_key",
                api_version="foo")
        self.assertTrue(str(error.value).startswith("Unsupported API version 'foo'."))

        with pytest.raises(ValueError) as error:
            ContainerClient(
                "https://foo.blob.core.windows.net/account",
                self.container_name,
                credential="fake_key",
                api_version="foo")
        self.assertTrue(str(error.value).startswith("Unsupported API version 'foo'."))

        with pytest.raises(ValueError) as error:
            BlobClient(
                "https://foo.blob.core.windows.net/account",
                self.container_name,
                self._get_blob_reference(),
                credential="fake_key",
                api_version="foo")
        self.assertTrue(str(error.value).startswith("Unsupported API version 'foo'."))

    @GlobalStorageAccountPreparer()
    def test_old_api_get_page_ranges_succeeds(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key,
            connection_data_block_size=4 * 1024,
            max_page_size=4 * 1024,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        blob = container.get_blob_client(blob_name)
        blob.create_page_blob(2048)
        data = self.get_random_bytes(1536)

        snapshot1 = blob.create_snapshot()
        blob.upload_page(data, offset=0, length=1536)
        snapshot2 = blob.create_snapshot()
        blob.clear_page(offset=512, length=512)

        # Act
        ranges1, cleared1 = blob.get_page_ranges(previous_snapshot_diff=snapshot1)
        ranges2, cleared2 = blob.get_page_ranges(previous_snapshot_diff=snapshot2['snapshot'])

        # Assert
        self.assertIsNotNone(ranges1)
        self.assertIsInstance(ranges1, list)
        self.assertEqual(len(ranges1), 2)
        self.assertIsInstance(cleared1, list)
        self.assertEqual(len(cleared1), 1)
        self.assertEqual(ranges1[0]['start'], 0)
        self.assertEqual(ranges1[0]['end'], 511)
        self.assertEqual(cleared1[0]['start'], 512)
        self.assertEqual(cleared1[0]['end'], 1023)
        self.assertEqual(ranges1[1]['start'], 1024)
        self.assertEqual(ranges1[1]['end'], 1535)

        self.assertIsNotNone(ranges2)
        self.assertIsInstance(ranges2, list)
        self.assertEqual(len(ranges2), 0)
        self.assertIsInstance(cleared2, list)
        self.assertEqual(len(cleared2), 1)
        self.assertEqual(cleared2[0]['start'], 512)
        self.assertEqual(cleared2[0]['end'], 1023)

# ------------------------------------------------------------------------------
