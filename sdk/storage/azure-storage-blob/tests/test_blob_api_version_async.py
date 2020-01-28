# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform

from azure.core.exceptions import AzureError
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from _shared.testcase import GlobalStorageAccountPreparer
from _shared.asynctestcase import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'


class StorageClientTest(AsyncStorageTestCase):
    def setUp(self):
        super(StorageClientTest, self).setUp()
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = "2019-07-07"
        self.container_name = self.get_resource_name('utcontainer')

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self, prefix=TEST_BLOB_PREFIX):
        return self.get_resource_name(prefix)

    # --Test Cases--------------------------------------------------------------

    def test_service_client_api_version_property(self):
        service_client = BlobServiceClient(
            "https://foo.blob.core.windows.net/account",
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(service_client.api_version, self.api_version_1)
        self.assertEqual(service_client._client._config.version, self.api_version_1)

        service_client.api_version = self.api_version_2
        self.assertEqual(service_client.api_version, self.api_version_2)
        self.assertEqual(service_client._client._config.version, self.api_version_2)

        service_client = BlobServiceClient(
            "https://foo.blob.core.windows.net/account",
            credential="fake_key")
        self.assertEqual(service_client.api_version, self.api_version_2)
        self.assertEqual(service_client._client._config.version, self.api_version_2)

        service_client.api_version = self.api_version_1
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
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(container_client.api_version, self.api_version_1)
        self.assertEqual(container_client._client._config.version, self.api_version_1)

        container_client.api_version = self.api_version_2
        self.assertEqual(container_client.api_version, self.api_version_2)
        self.assertEqual(container_client._client._config.version, self.api_version_2)

        container_client = ContainerClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            credential="fake_key")
        self.assertEqual(container_client.api_version, self.api_version_2)
        self.assertEqual(container_client._client._config.version, self.api_version_2)

        container_client.api_version = self.api_version_1
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

        blob_client.api_version = self.api_version_2
        self.assertEqual(blob_client.api_version, self.api_version_2)
        self.assertEqual(blob_client._client._config.version, self.api_version_2)

        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            self._get_blob_reference(),
            credential="fake_key")
        self.assertEqual(blob_client.api_version, self.api_version_2)
        self.assertEqual(blob_client._client._config.version, self.api_version_2)

        blob_client.api_version = self.api_version_1
        self.assertEqual(blob_client.api_version, self.api_version_1)
        self.assertEqual(blob_client._client._config.version, self.api_version_1)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_old_api_create_append_blob_succeeds(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        create_resp = await blob.create_append_blob()

        # Assert
        blob_properties = await blob.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))






# ------------------------------------------------------------------------------
