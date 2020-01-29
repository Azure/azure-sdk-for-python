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
    CpkScopeInfo,
    ContainerCpkScopeInfo,
    BlobSasPermissions
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
TEST_ENCRYPTION_KEY_SCOPE = CpkScopeInfo(encryption_scope="antjoscope1")
TEST_CONTAINER_ENCRYPTION_KEY_SCOPE = ContainerCpkScopeInfo(default_encryption_scope="containerscope")
TEST_CONTAINER_ENCRYPTION_KEY_SCOPE_DENY_OVERRIDE = ContainerCpkScopeInfo(default_encryption_scope="containerscope",
                                                                          deny_encryption_scope_override=True)


class StorageClientTest(StorageTestCase):
    def setUp(self):
        super(StorageClientTest, self).setUp()
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = "2019-07-07"
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
    def test_old_api_create_append_blob_succeeds(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        create_resp = blob_client.create_append_blob()

        # Assert
        blob_properties = blob_client.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertIsNone(blob_properties.encryption_scope)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_new_api_create_append_blob_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        with pytest.raises(ValueError) as error:
            blob_client.create_append_blob(cpk_scope_info=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertTrue(str(error.value).startswith("The current API version '2019-02-02' does not support the following parameters:\n'cpk_scope_info'"))

    @GlobalStorageAccountPreparer()
    def test_old_api_append_block_succeeds(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_append_blob()
        update_resp = blob_client.append_block(b'testdata')

        # Assert
        blob_properties = blob_client.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertIsNone(blob_properties.encryption_scope)
        self.assertEqual(blob_properties.etag, update_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, update_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_new_api_append_block_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_append_blob()
        with pytest.raises(ValueError) as error:
            blob_client.append_block(b'testdata', cpk_scope_info=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertTrue(str(error.value).startswith("The current API version '2019-02-02' does not support the following parameters:\n'cpk_scope_info'"))

    @GlobalStorageAccountPreparer()
    def test_old_api_create_page_blob_succeeds(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        create_resp = blob_client.create_page_blob(1024)

        # Assert
        blob_properties = blob_client.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertIsNone(blob_properties.encryption_scope)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_new_api_create_page_blob_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        with pytest.raises(ValueError) as error:
            blob_client.create_page_blob(1024, cpk_scope_info=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertTrue(str(error.value).startswith("The current API version '2019-02-02' does not support the following parameters:\n'cpk_scope_info'"))

    @GlobalStorageAccountPreparer()
    def test_old_api_upload_page_succeeds(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_page_blob(1024)
        update_resp = blob_client.upload_page(512 * b'0', 0, 512)

        # Assert
        blob_properties = blob_client.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertIsNone(blob_properties.encryption_scope)
        self.assertEqual(blob_properties.etag, update_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, update_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_new_api_upload_page_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_page_blob(1024)
        with pytest.raises(ValueError) as error:
            blob_client.upload_page(512 * b'0', 0, 512, cpk_scope_info=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertTrue(str(error.value).startswith("The current API version '2019-02-02' does not support the following parameters:\n'cpk_scope_info'"))

    @GlobalStorageAccountPreparer()
    def test_old_api_clear_page_succeeds(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_page_blob(1024)
        update_resp = blob_client.clear_page(0, 512)

        # Assert
        blob_properties = blob_client.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertIsNone(blob_properties.encryption_scope)
        self.assertEqual(blob_properties.etag, update_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, update_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_new_api_clear_page_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_page_blob(1024)
        with pytest.raises(ValueError) as error:
            blob_client.clear_page(0, 512, cpk_scope_info=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertTrue(str(error.value).startswith("The current API version '2019-02-02' does not support the following parameters:\n'cpk_scope_info'"))

    @GlobalStorageAccountPreparer()
    def test_old_api_resize_succeeds(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_page_blob(1024)
        update_resp = blob_client.resize_blob(512)

        # Assert
        blob_properties = blob_client.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertIsNone(blob_properties.encryption_scope)
        self.assertEqual(blob_properties.etag, update_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, update_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_new_api_resize_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob_client = container.get_blob_client(blob_name)
        blob_client.create_page_blob(1024)
        with pytest.raises(ValueError) as error:
            blob_client.resize_blob(512, cpk_scope_info=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertTrue(str(error.value).startswith("The current API version '2019-02-02' does not support the following parameters:\n'cpk_scope_info'"))

    @GlobalStorageAccountPreparer()
    def test_new_api_get_page_managed_disk_diff_fails(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            api_version=self.api_version_1)
        container = self._create_container(bsc)
        blob_name = self._get_blob_reference()

        blob = container.get_blob_client(blob_name)
        blob.create_page_blob(1536)
        data = self.get_random_bytes(1536)

        snapshot = blob.create_snapshot()
        snapshot_blob = BlobClient.from_blob_url(
            blob.url,
            credential=storage_account_key,
            snapshot=snapshot['snapshot'],
            api_version=self.api_version_1)

        sas_token1 = generate_blob_sas(
            snapshot_blob.account_name,
            snapshot_blob.container_name,
            snapshot_blob.blob_name,
            snapshot=snapshot_blob.snapshot,
            account_key=snapshot_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob.upload_page(data, offset=0, length=1536)

        # Act
        with pytest.raises(ValueError) as error:
            blob.get_managed_disk_page_range_diff(prev_snapshot_url=snapshot_blob.url + '&' + sas_token1)
        
        # Assert
        self.assertEqual(
            str(error.value),
            "The function 'get_managed_disk_page_range_diff' only supports API version '2019-07-07' or above. Currently using API version: '2019-02-02'.")

# ------------------------------------------------------------------------------
