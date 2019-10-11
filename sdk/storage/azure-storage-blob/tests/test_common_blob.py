# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import requests
import time
import unittest
import os
from datetime import datetime, timedelta

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError)
from azure.storage.blob import (
    upload_blob_to_url,
    download_blob_from_url,
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobType,
    StorageErrorCode,
    BlobSasPermissions,
    ContainerSasPermissions,
    ContentSettings,
    BlobProperties,
    RetentionPolicy,
    AccessPolicy,
    ResourceTypes,
    AccountSasPermissions,
    StandardBlobTier,
)
from azure.storage.blob._generated.models import RehydratePriority
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from testcase import (
    StorageTestCase
)

#------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
#------------------------------------------------------------------------------

class StorageCommonBlobTest(StorageTestCase):

    def _setup(self, name, key=None):
        self.bsc = BlobServiceClient(self._account_url(name), credential=key)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                container.create_container(timeout=5)
            except ResourceExistsError:
                pass
        self.byte_data = self.get_random_bytes(1024)
        self.bsc2 = BlobServiceClient(self._account_url(name), credential=key)
        self.remote_container_name = 'rmt'

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    #--Helpers-----------------------------------------------------------------
    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_block_blob(self):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(self.byte_data, length=len(self.byte_data))
        return blob_name

    def _create_remote_container(self):
        self.remote_container_name = self.get_resource_name('remotectnr')
        remote_container = self.bsc2.get_container_client(self.remote_container_name)
        try:
            remote_container.create_container()
        except ResourceExistsError:
            pass

    def _create_remote_block_blob(self, blob_data=None):
        if not blob_data:
            blob_data = b'12345678' * 1024 * 1024
        source_blob_name = self._get_blob_reference()
        source_blob = self.bsc2.get_blob_client(self.remote_container_name, source_blob_name)
        source_blob.upload_blob(blob_data, overwrite=True)
        return source_blob

    def _wait_for_async_copy(self, blob):
        count = 0
        props = blob.get_blob_properties()
        while props.copy.status == 'pending':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            props = blob.get_blob_properties()
        return props

    def _enable_soft_delete(self):
        delete_retention_policy = RetentionPolicy(enabled=True, days=2)
        self.bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # wait until the policy has gone into effect
        if self.is_live:
            time.sleep(30)

    def _disable_soft_delete(self):
        delete_retention_policy = RetentionPolicy(enabled=False)
        self.bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

    def _assert_blob_is_soft_deleted(self, blob):
        self.assertTrue(blob.deleted)
        self.assertIsNotNone(blob.deleted_time)
        self.assertIsNotNone(blob.remaining_retention_days)

    def _assert_blob_not_soft_deleted(self, blob):
        self.assertFalse(blob.deleted)
        self.assertIsNone(blob.deleted_time)
        self.assertIsNone(blob.remaining_retention_days)

    #-- Common test cases for blobs ----------------------------------------------
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        exists = blob.get_blob_properties()

        # Assert
        self.assertTrue(exists)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_not_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()
        
 
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_snapshot_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = blob.create_snapshot()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=snapshot)
        exists = blob.get_blob_properties()

        # Assert
        self.assertTrue(exists)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_snapshot_not_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot="1988-08-18T07:52:31.6690068Z")
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_container_not_exists(self, resource_group, location, storage_account, storage_account_key):
        # In this case both the blob and container do not exist
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self._get_container_reference(), blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_with_question_mark(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = '?ques?tion?'
        blob_data = u'???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Assert
        data = blob.download_blob()
        self.assertIsNotNone(data)
        content = b"".join(list(data))
        self.assertEqual(content.decode('utf-8'), blob_data)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_with_special_chars(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)

        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob.upload_blob(blob_data, length=len(blob_data))

            data = blob.download_blob()
            content = b"".join(list(data))
            self.assertEqual(content.decode('utf-8'), blob_data)
        

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        data = b'hello world again'
        resp = blob.upload_blob(data, length=len(data), lease=lease)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        content = b"".join(list(blob.download_blob(lease=lease)))
        self.assertEqual(content, data)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._get_blob_reference()
        metadata={'hello': 'world', 'number': '42'}

        # Act
        data = b'hello world'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.upload_blob(data, length=len(data), metadata=metadata)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        md = blob.get_blob_properties().metadata
        self.assertDictEqual(md, metadata)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        content = b"".join(list(data))
        self.assertEqual(content, self.byte_data)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        # Act
        data = snapshot.download_blob()

        # Assert
        content = b"".join(list(data))
        self.assertEqual(content, self.byte_data)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_with_snapshot_previous(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        upload_data = b'hello world again'
        blob.upload_blob(upload_data, length=len(upload_data), overwrite=True)

        # Act
        blob_previous = snapshot.download_blob()
        blob_latest = blob.download_blob()

        # Assert
        self.assertEqual(b"".join(list(blob_previous)), self.byte_data)
        self.assertEqual(b"".join(list(blob_latest)), b'hello world again')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_with_range(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob(offset=0, length=5)

        # Assert
        self.assertEqual(b"".join(list(data)), self.byte_data[:5])
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        data = blob.download_blob(lease=lease)
        lease.release()

        # Assert
        self.assertEqual(b"".join(list(data)), self.byte_data)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_with_non_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.download_blob()

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_set_blob_properties_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.set_http_headers(
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
        )

        # Assert
        props = blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_set_blob_properties_with_blob_settings_param(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Act
        props.content_settings.content_language = 'spanish'
        props.content_settings.content_disposition = 'inline'
        blob.set_http_headers(content_settings=props.content_settings)

        # Assert
        props = blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_properties(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.lease.status, 'unlocked')
        self.assertIsNotNone(props.creation_time)
        

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # HEAD request.
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_properties_fail(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)

        with self.assertRaises(HttpResponseError) as e:
            blob.get_blob_properties() # Invalid snapshot value of 1
        

        # Assert
        # TODO: No error code returned
        #self.assertEqual(StorageErrorCode.invalid_query_parameter_value, e.exception.error_code)

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # GET request. This is preferred to relying on the ErrorCode in the body.
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_metadata_fail(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with self.assertRaises(HttpResponseError) as e:
            blob.get_blob_properties().metadata # Invalid snapshot value of 1
        
        # Assert
        # TODO: No error code returned
        #self.assertEqual(StorageErrorCode.invalid_query_parameter_value, e.exception.error_code)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        self.assertTrue(data.properties.server_encrypted)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_properties_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Assert
        self.assertTrue(props.server_encrypted)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_list_blobs_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blobs()

        #Act

        #Assert
        for blob in blob_list:
            self.assertTrue(blob.server_encrypted)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_no_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        #Act
        def callback(response):
            response.http_response.headers['x-ms-server-encrypted'] = 'false'

        props = blob.get_blob_properties(raw_response_hook=callback)

        #Assert
        self.assertFalse(props.server_encrypted)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_properties_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        res = blob.create_snapshot()
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 2)

        # Act
        snapshot = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=res)
        props = snapshot.get_blob_properties()

        # Assert
        self.assertIsNotNone(blob)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_properties_with_leased_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.lease.status, 'locked')
        self.assertEqual(props.lease.state, 'leased')
        self.assertEqual(props.lease.duration, 'infinite')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_blob_metadata(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        md = blob.get_blob_properties().metadata

        # Assert
        self.assertIsNotNone(md)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_set_blob_metadata_with_upper_case(self, resource_group, location, storage_account, storage_account_key):
        if not self.is_live:
            # bug in devtools...converts upper case header to lowercase
            # passes live.
            return
        self._setup(storage_account.name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.set_blob_metadata(metadata)

        # Assert
        md = blob.get_blob_properties().metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_delete_blob_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.delete_blob()

        # Assert
        self.assertIsNone(resp)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_delete_blob_with_non_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.delete_blob()

        # Assert
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_delete_blob_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        # Act
        snapshot.delete_blob()

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0].name, blob_name)
        self.assertIsNone(blobs[0].snapshot)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_delete_blob_snapshots(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.create_snapshot()

        # Act
        blob.delete_blob(delete_snapshots='only')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 1)
        self.assertIsNone(blobs[0].snapshot)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_delete_blob_with_snapshots(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.create_snapshot()

        # Act
        #with self.assertRaises(HttpResponseError):
        #    blob.delete_blob()

        blob.delete_blob(delete_snapshots='include')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 0)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_soft_delete_blob_without_snapshots(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account.name, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()

            container = self.bsc.get_container_client(self.container_name)
            blob = container.get_blob_client(blob_name)

            # Soft delete the blob
            blob.delete_blob()
            blob_list = list(container.list_blobs(include='deleted'))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs())

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include='deleted'))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            self._disable_soft_delete()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_soft_delete_single_blob_snapshot(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account.name, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = blob.create_snapshot()
            blob_snapshot_2 = blob.create_snapshot()

            # Soft delete blob_snapshot_1
            snapshot_1 = self.bsc.get_blob_client(
                self.container_name, blob_name, snapshot=blob_snapshot_1)
            snapshot_1.delete_blob()

            with self.assertRaises(ValueError):
                snapshot_1.delete_blob(delete_snapshots='only')

            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs(include='snapshots'))

            # Assert
            self.assertEqual(len(blob_list), 2)

            # Restore snapshot with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)
        finally:
            self._disable_soft_delete()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_soft_delete_only_snapshots_of_blob(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account.name, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = blob.create_snapshot()
            blob_snapshot_2 = blob.create_snapshot()

            # Soft delete all snapshots
            blob.delete_blob(delete_snapshots='only')
            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                elif listedblob.snapshot == blob_snapshot_2['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs(include="snapshots"))

            # Assert
            self.assertEqual(len(blob_list), 1)

            # Restore snapshots with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)

        finally:
            self._disable_soft_delete()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_soft_delete_blob_including_all_snapshots(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account.name, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = blob.create_snapshot()
            blob_snapshot_2 = blob.create_snapshot()

            # Soft delete blob and all snapshots
            blob.delete_blob(delete_snapshots='include')
            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                self._assert_blob_is_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs(include=["snapshots"]))

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob and snapshots with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)

        finally:
            self._disable_soft_delete()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_soft_delete_with_leased_blob(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account.name, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            lease = blob.acquire_lease()

            # Soft delete the blob without lease_id should fail
            with self.assertRaises(HttpResponseError):
                blob.delete_blob()

            # Soft delete the blob
            blob.delete_blob(lease=lease)
            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include="deleted"))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs())

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete, this also gets rid of the lease
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include="deleted"))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            self._disable_soft_delete()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_copy_blob_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self._account_url(storage_account.name), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertIsNotNone(copy['copy_id'])

        copy_content = copyblob.download_blob().content_as_bytes()
        self.assertEqual(copy_content, self.byte_data)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_copy_blob_with_blob_tier_specified(self, resource_group, location, storage_account, storage_account_key):
        pytest.skip("Unable to set premium account")
        # Arrange
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self._account_url(storage_account.name), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        blob_tier = StandardBlobTier.Cool
        copyblob.start_copy_from_url(sourceblob, standard_blob_tier=blob_tier)

        copy_blob_properties = copyblob.get_blob_properties()

        # Assert
        self.assertEqual(copy_blob_properties.blob_tier, blob_tier)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_copy_blob_with_rehydrate_priority(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        pytest.skip("Unabe to set up premium storage account type")
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self._account_url(storage_account.name), self.container_name, blob_name)

        blob_tier = StandardBlobTier.Archive
        rehydrate_priority = RehydratePriority.high
        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob,
                                            standard_blob_tier=blob_tier,
                                            rehydrate_priority=rehydrate_priority)
        copy_blob_properties = copyblob.get_blob_properties()
        copyblob.set_standard_blob_tier(StandardBlobTier.Hot)
        second_resp = copyblob.get_blob_properties()

        # Assert
        self.assertIsNotNone(copy)
        self.assertIsNotNone(copy.get('copy_id'))
        self.assertEqual(copy_blob_properties.blob_tier, blob_tier)
        self.assertEqual(second_resp.archive_status, 'rehydrate-pending-to-hot')
        

    # TODO: external copy was supported since 2019-02-02
    # @record
    # def test_copy_blob_with_external_blob_fails(self):
    #     # Arrange
    #     source_blob = "http://www.google.com"
    #     copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')
    #
    #     # Act
    #     copy = copied_blob.start_copy_from_url(source_blob)
    #     self.assertEqual(copy['copy_status'], 'pending')
    #     props = self._wait_for_async_copy(copied_blob)
    #
    #     # Assert
    #     self.assertEqual(props.copy.status_description, '500 InternalServerError "Copy failed."')
    #     self.assertEqual(props.copy.status, 'success')
    #     self.assertIsNotNone(props.copy.id)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_copy_blob_async_private_blob_no_sas(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob()

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            target_blob.start_copy_from_url(source_blob.url)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_copy_blob_async_private_blob_with_sas(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        sas_token = source_blob.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = target_blob.start_copy_from_url(blob.url)

        # Assert
        props = self._wait_for_async_copy(target_blob)
        self.assertEqual(props.copy.status, 'success')
        actual_data = target_blob.download_blob()
        self.assertEqual(b"".join(list(actual_data)), data)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_abort_copy_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        source_blob = "http://www.gutenberg.org/files/59466/59466-0.txt"
        copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')

        # Act
        copy = copied_blob.start_copy_from_url(source_blob)
        self.assertEqual(copy['copy_status'], 'pending')

        copied_blob.abort_copy(copy)
        props = self._wait_for_async_copy(copied_blob)
        self.assertEqual(props.copy.status, 'aborted')

        # Assert
        actual_data = copied_blob.download_blob()
        self.assertEqual(b"".join(list(actual_data)), b"")
        self.assertEqual(actual_data.properties.copy.status, 'aborted')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_abort_copy_blob_with_synchronous_copy_fails(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        source_blob_name = self._create_block_blob()
        source_blob = self.bsc.get_blob_client(self.container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = target_blob.start_copy_from_url(source_blob.url)

        with self.assertRaises(HttpResponseError):
            target_blob.abort_copy(copy_resp)

        # Assert
        self.assertEqual(copy_resp['copy_status'], 'success')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_snapshot_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.create_snapshot()

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_lease_blob_acquire_and_release(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()
        lease.release()
        lease2 = blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease)
        self.assertIsNotNone(lease2)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_lease_blob_with_duration(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_duration=15)
        resp = blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(15)

        # Assert
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(b'hello 3', length=7, lease=lease)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_lease_blob_with_proposed_lease_id(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease(lease_id=lease_id)

        # Assert
        self.assertEqual(lease.id, lease_id)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_lease_blob_change_lease_id(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease()
        first_lease_id = lease.id
        lease.change(lease_id)
        lease.renew()

        # Assert
        self.assertNotEqual(first_lease_id, lease.id)
        self.assertEqual(lease.id, lease_id)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_lease_blob_break_period(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_duration=15)
        lease_time = lease.break_lease(lease_break_period=5)

        resp = blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(5)

        with self.assertRaises(HttpResponseError):
            blob.upload_blob(b'hello 3', length=7, lease=lease)

        # Assert
        self.assertIsNotNone(lease.id)
        self.assertIsNotNone(lease_time)
        self.assertIsNotNone(resp.get('etag'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_lease_blob_acquire_and_renew(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()
        first_id = lease.id
        lease.renew()
        
        # Assert
        self.assertEqual(first_id, lease.id)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_lease_blob_acquire_twice_fails(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease.id)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_unicode_get_blob_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = '啊齄丂狛狜'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'hello world')

        # Act
        data = blob.download_blob()

        # Assert
        self.assertEqual(b"".join(list(data)), b'hello world')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_blob_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world啊齄丂狛狜'
        resp = blob.upload_blob(data)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_no_sas_private_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertFalse(response.ok)
        self.assertNotEqual(-1, response.text.find('ResourceNotFound'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_no_sas_public_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        data = b'a public blob can be read without a shared access signature'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        try:
            container = self.bsc.create_container(container_name, public_access='blob')
        except ResourceExistsError:
            container = self.bsc.get_container_client(container_name)
        blob = container.upload_blob(blob_name, data, overwrite=True)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_public_access_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        data = b'public access blob'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        try:
            container = self.bsc.create_container(container_name, public_access='blob')
        except ResourceExistsError:
            container = self.bsc.get_container_client(container_name)
        blob = container.upload_blob(blob_name, data, overwrite=True)

        # Act
        service = BlobClient.from_blob_url(blob.url)
        #self._set_test_proxy(service, self.settings)
        content = service.download_blob().content_as_bytes()

        # Assert
        self.assertEqual(data, content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_sas_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        
        token = blob.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        #self._set_test_proxy(service, self.settings)
        content = service.download_blob().content_as_bytes()

        # Assert
        self.assertEqual(self.byte_data, content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_sas_access_blob_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot = blob_client.create_snapshot()
        blob_snapshot_client = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=blob_snapshot)

        token = blob_snapshot_client.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        service = BlobClient.from_blob_url(blob_snapshot_client.url, credential=token)

        # Act
        snapshot_content = service.download_blob().content_as_bytes()

        # Assert
        self.assertEqual(self.byte_data, snapshot_content)

        # Act
        service.delete_blob()

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            service.get_blob_properties()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_sas_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = BlobSasPermissions(read=True)
        identifiers = {'testid': access_policy}

        resp = container.set_container_access_policy(identifiers)

        token = blob.generate_shared_access_signature(policy_id='testid')

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        #self._set_test_proxy(service, self.settings)
        result = service.download_blob().content_as_bytes()

        # Assert
        self.assertEqual(self.byte_data, result)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()

        token = self.bsc.generate_shared_access_signature(
            ResourceTypes(container=True, object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name, credential=token)
        container = ContainerClient(
            self.bsc.url, container_name=self.container_name, credential=token)
        container.get_container_properties()
        blob_response = requests.get(blob.url)
        container_response = requests.get(container.url, params={'restype':'container'})

        # Assert
        self.assertTrue(blob_response.ok)
        self.assertEqual(self.byte_data, blob_response.content)
        self.assertTrue(container_response.ok)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_token_credential(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        token_credential = self.generate_oauth_token()
        get_token = token_credential.get_token

        # Action 1: make sure token works
        service = BlobServiceClient(self._account_url(storage_account.name), credential=token_credential)
        result = service.get_service_properties()
        self.assertIsNotNone(result)

        # Action 2: change token value to make request fail
        fake_credential = self.generate_fake_token()
        service = BlobServiceClient(self._account_url(storage_account.name), credential=fake_credential)
        with self.assertRaises(ClientAuthenticationError):
            service.get_service_properties()

        # Action 3: update token to make it working again
        service = BlobServiceClient(self._account_url(storage_account.name), credential=token_credential)
        result = service.get_service_properties()
        self.assertIsNotNone(result)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_shared_read_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        self.assertEqual(self.byte_data, response.content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_shared_read_access_blob_with_content_query_params(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertEqual(self.byte_data, response.content)
        self.assertEqual(response.headers['cache-control'], 'no-cache')
        self.assertEqual(response.headers['content-disposition'], 'inline')
        self.assertEqual(response.headers['content-encoding'], 'utf-8')
        self.assertEqual(response.headers['content-language'], 'fr')
        self.assertEqual(response.headers['content-type'], 'text')
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_shared_write_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        updated_data = b'updated blob data'
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        headers = {'x-ms-blob-type': 'BlockBlob'}
        response = requests.put(sas_blob.url, headers=headers, data=updated_data)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        data = blob.download_blob()
        self.assertEqual(updated_data, b"".join(list(data)))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_shared_delete_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobSasPermissions(delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.delete(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        with self.assertRaises(HttpResponseError):
            sas_blob.download_blob()
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_account_information(self, resource_group, location, storage_account, storage_account_key):
        # Act
        self._setup(storage_account.name, storage_account_key)
        info = self.bsc.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_account_information_with_container_name(self, resource_group, location, storage_account, storage_account_key):
        # Act
        self._setup(storage_account.name, storage_account_key)
        # Container name gets ignored
        container = self.bsc.get_container_client("missing")
        info = container.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_account_information_with_blob_name(self, resource_group, location, storage_account, storage_account_key):
        # Act
        self._setup(storage_account.name, storage_account_key)
        # Both container and blob names get ignored
        blob = self.bsc.get_blob_client("missing", "missing")
        info = blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_account_information_with_container_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        token = container.generate_shared_access_signature(
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_container = ContainerClient.from_container_url(container.url, credential=token)

        # Act
        info = sas_container.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_account_information_with_blob_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        info = sas_blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_download_to_file_with_sas(self, resource_group, location, storage_account, storage_account_key):
        if not self.is_live:
            return
        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        sas_token = source_blob.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)
        FILE_PATH = 'download_to_file_with_sas.temp.dat'

        # Act
        download_blob_from_url(blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @StorageAccountPreparer(name_prefix='pyacrstorage', parameter_name='rmt')
    def test_download_to_file_with_credential(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        if not self.is_live:
            return
        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'to_file_with_credential.temp.dat'
        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            max_concurrency=2,
            credential=rmt_key)
        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @StorageAccountPreparer(name_prefix='pyacrstorage', parameter_name='rmt')
    def test_download_to_stream_with_credential(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        if not self.is_live:
            return
        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'download_to_stream_with_credential.temp.dat'
        # Act
        with open(FILE_PATH, 'wb') as stream:
            download_blob_from_url(
                source_blob.url, stream,
                max_concurrency=2,
                credential=rmt_key)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @StorageAccountPreparer(name_prefix='pyacrstorage', parameter_name='rmt')
    def test_download_to_file_with_existing_file(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        if not self.is_live:
            return
        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'file_with_existing_file.temp.dat'
        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=rmt_key)

        with self.assertRaises(ValueError):
            download_blob_from_url(source_blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @StorageAccountPreparer(name_prefix='pyacrstorage', parameter_name='rmt')
    def test_download_to_file_with_existing_file_overwrite(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        if not self.is_live:
            return
        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'file_with_existing_file_overwrite.temp.dat'
        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=rmt_key)

        data2 = b'ABCDEFGH' * 1024 * 1024
        source_blob = self._create_remote_block_blob(blob_data=data2)
        download_blob_from_url(
            source_blob.url, FILE_PATH, overwrite=True,
            credential=rmt_key)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data2, actual)
        self._teardown(FILE_PATH)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_upload_to_url_bytes_with_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        uploaded = upload_blob_to_url(sas_blob.url, data)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(data, content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_upload_to_url_bytes_with_credential(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(data, content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_upload_to_url_bytes_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        with self.assertRaises(ResourceExistsError):
            upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(b"existing_data", content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_upload_to_url_bytes_with_existing_blob_overwrite(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data,
            overwrite=True,
            credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(data, content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_upload_to_url_text_with_credential(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account.name, storage_account_key)
        data = '12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_text()
        self.assertEqual(data, content)
        

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_upload_to_url_file_with_credential(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return
        FILE_PATH = 'upload_to_url_file_with_credential.temp.dat'
        self._setup(storage_account.name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        with open(FILE_PATH, 'rb'):
            uploaded = upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(data, content)
        self._teardown(FILE_PATH)


#------------------------------------------------------------------------------
