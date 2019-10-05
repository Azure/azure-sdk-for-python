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
    StandardBlobTier)
from azure.storage.blob._generated.models import RehydratePriority
from testcase import (
    StorageTestCase,
    TestMode,
    record,
)

#------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_data.temp.dat'
#------------------------------------------------------------------------------

class StorageCommonBlobTest(StorageTestCase):

    def setUp(self):
        super(StorageCommonBlobTest, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()
        self.bsc = BlobServiceClient(url, credential=credential)

        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            container = self.bsc.get_container_client(self.container_name)
            try:
                container.create_container(timeout=5)
            except ResourceExistsError:
                pass

        self.byte_data = self.get_random_bytes(1024)

        remote_url = self._get_remote_account_url()
        remote_credential = self._get_remote_shared_key_credential()
        self.bsc2 = BlobServiceClient(remote_url, credential=remote_credential)
        self.remote_container_name = None

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bsc.delete_container(self.container_name, timeout=5)
            except:
                pass

            if self.remote_container_name:
                try:
                    self.bsc2.delete_container(self.remote_container_name)
                except:
                    pass
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageCommonBlobTest, self).tearDown()

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
        source_blob.upload_blob(blob_data)
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
        if not self.is_playback():
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
    @record
    def test_blob_exists(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        exists = blob.get_blob_properties()

        # Assert
        self.assertTrue(exists)

    @record
    def test_blob_not_exists(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()

    @record
    def test_blob_snapshot_exists(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = blob.create_snapshot()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=snapshot)
        exists = blob.get_blob_properties()

        # Assert
        self.assertTrue(exists)

    @record
    def test_blob_snapshot_not_exists(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot="1988-08-18T07:52:31.6690068Z")
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()

    @record
    def test_blob_container_not_exists(self):
        # In this case both the blob and container do not exist
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self._get_container_reference(), blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()

    @record
    def test_create_blob_with_question_mark(self):
        # Arrange
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

    @record
    def test_create_blob_with_special_chars(self):
        # Arrange

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

    @record
    def test_create_blob_with_lease_id(self):
        # Arrange
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

    @record
    def test_create_blob_with_metadata(self):
        # Arrange
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

    @record
    def test_get_blob_with_existing_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        content = b"".join(list(data))
        self.assertEqual(content, self.byte_data)

    @record
    def test_get_blob_with_snapshot(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        # Act
        data = snapshot.download_blob()

        # Assert
        content = b"".join(list(data))
        self.assertEqual(content, self.byte_data)

    @record
    def test_get_blob_with_snapshot_previous(self):
        # Arrange
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

    @record
    def test_get_blob_with_range(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob(offset=0, length=5)

        # Assert
        self.assertEqual(b"".join(list(data)), self.byte_data[:5])

    @record
    def test_get_blob_with_lease(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        data = blob.download_blob(lease=lease)
        lease.release()

        # Assert
        self.assertEqual(b"".join(list(data)), self.byte_data)

    @record
    def test_get_blob_with_non_existing_blob(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.download_blob()

        # Assert

    @record
    def test_set_blob_properties_with_existing_blob(self):
        # Arrange
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

    @record
    def test_set_blob_properties_with_blob_settings_param(self):
        # Arrange
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

    @record
    def test_get_blob_properties(self):
        # Arrange
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
    @record
    def test_get_blob_properties_fail(self):
        # Arrange
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
    @ record
    def test_get_blob_metadata_fail(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with self.assertRaises(HttpResponseError) as e:
            blob.get_blob_properties().metadata # Invalid snapshot value of 1

        # Assert
        # TODO: No error code returned
        #self.assertEqual(StorageErrorCode.invalid_query_parameter_value, e.exception.error_code)

    @record
    def test_get_blob_server_encryption(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        self.assertTrue(data.properties.server_encrypted)

    @record
    def test_get_blob_properties_server_encryption(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Assert
        self.assertTrue(props.server_encrypted)

    @record
    def test_list_blobs_server_encryption(self):
        #Arrange
        self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blobs()

        #Act

        #Assert
        for blob in blob_list:
            self.assertTrue(blob.server_encrypted)

    @record
    def test_no_server_encryption(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        #Act
        def callback(response):
            response.http_response.headers['x-ms-server-encrypted'] = 'false'

        props = blob.get_blob_properties(raw_response_hook=callback)

        #Assert
        self.assertFalse(props.server_encrypted)

    @record
    def test_get_blob_properties_with_snapshot(self):
        # Arrange
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

    @record
    def test_get_blob_properties_with_leased_blob(self):
        # Arrange
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

    @record
    def test_get_blob_metadata(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        md = blob.get_blob_properties().metadata

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_set_blob_metadata_with_upper_case(self):
        # Arrange
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

    @record
    def test_delete_blob_with_existing_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.delete_blob()

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_non_existing_blob(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.delete_blob()

        # Assert

    @record
    def test_delete_blob_snapshot(self):
        # Arrange
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

    @record
    def test_delete_blob_snapshots(self):
        # Arrange
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

    @record
    def test_delete_blob_with_snapshots(self):
        # Arrange
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

    @record
    def test_soft_delete_blob_without_snapshots(self):
        try:
            # Arrange
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

    @record
    def test_soft_delete_single_blob_snapshot(self):
        try:
            # Arrange
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

    @record
    def test_soft_delete_only_snapshots_of_blob(self):
        try:
            # Arrange
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

    @record
    def test_soft_delete_blob_including_all_snapshots(self):
        try:
            # Arrange
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

    @record
    def test_soft_delete_with_leased_blob(self):
        try:
            # Arrange
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

    @record
    def test_copy_blob_with_existing_blob(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self._get_account_url(), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertIsNotNone(copy['copy_id'])

        copy_content = copyblob.download_blob().content_as_bytes()
        self.assertEqual(copy_content, self.byte_data)

    @record
    def test_copy_blob_with_blob_tier_specified(self):
        # Arrange
        blob_name = self._create_block_blob()
        self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self._get_account_url(), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        blob_tier = StandardBlobTier.Cool
        copyblob.start_copy_from_url(sourceblob, standard_blob_tier=blob_tier)

        copy_blob_properties = copyblob.get_blob_properties()

        # Assert
        self.assertEqual(copy_blob_properties.blob_tier, blob_tier)

    @record
    def test_copy_blob_with_rehydrate_priority(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self._get_account_url(), self.container_name, blob_name)

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

    @record
    def test_copy_blob_async_private_blob_no_sas(self):
        # Arrange
        self._create_remote_container()
        source_blob = self._create_remote_block_blob()

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            target_blob.start_copy_from_url(source_blob.url)

    @record
    def test_copy_blob_async_private_blob_with_sas(self):
        # Arrange
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

    @record
    def test_abort_copy_blob(self):
        # Arrange
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

    @record
    def test_abort_copy_blob_with_synchronous_copy_fails(self):
        # Arrange
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

    @record
    def test_snapshot_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.create_snapshot()

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])

    @record
    def test_lease_blob_acquire_and_release(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()
        lease.release()
        lease2 = blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease)
        self.assertIsNotNone(lease2)

    @record
    def test_lease_blob_with_duration(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_duration=15)
        resp = blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(15)

        # Assert
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(b'hello 3', length=7, lease=lease)

    @record
    def test_lease_blob_with_proposed_lease_id(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease(lease_id=lease_id)

        # Assert
        self.assertEqual(lease.id, lease_id)

    @record
    def test_lease_blob_change_lease_id(self):
        # Arrange
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

    @record
    def test_lease_blob_break_period(self):
        # Arrange
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

    @record
    def test_lease_blob_acquire_and_renew(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()
        first_id = lease.id
        lease.renew()
        
        # Assert
        self.assertEqual(first_id, lease.id)

    @record
    def test_lease_blob_acquire_twice_fails(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease.id)

    @record
    def test_unicode_get_blob_unicode_name(self):
        # Arrange
        blob_name = '啊齄丂狛狜'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'hello world')

        # Act
        data = blob.download_blob()

        # Assert
        self.assertEqual(b"".join(list(data)), b'hello world')

    @record
    def test_create_blob_blob_unicode_data(self):
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world啊齄丂狛狜'
        resp = blob.upload_blob(data)

        # Assert
        self.assertIsNotNone(resp.get('etag'))

    @record
    def test_no_sas_private_blob(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertFalse(response.ok)
        self.assertNotEqual(-1, response.text.find('ResourceNotFound'))

    @record
    def test_no_sas_public_blob(self):
        # Arrange
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

    @record
    def test_public_access_blob(self):
        # Arrange
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

    @record
    def test_sas_access_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    def test_sas_access_blob_snapshot(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_sas_signed_identifier(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_account_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_get_user_delegation_key(self):
        # Act
        token_credential = self.generate_oauth_token()

        # Action 1: make sure token works
        service = BlobServiceClient(self._get_oauth_account_url(), credential=token_credential)

        start = datetime.utcnow()
        expiry = datetime.utcnow() + timedelta(hours=1)
        user_delegation_key_1 = service.get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)
        user_delegation_key_2 = service.get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)

        # Assert key1 is valid
        self.assertIsNotNone(user_delegation_key_1.signed_oid)
        self.assertIsNotNone(user_delegation_key_1.signed_tid)
        self.assertIsNotNone(user_delegation_key_1.signed_start)
        self.assertIsNotNone(user_delegation_key_1.signed_expiry)
        self.assertIsNotNone(user_delegation_key_1.signed_version)
        self.assertIsNotNone(user_delegation_key_1.signed_service)
        self.assertIsNotNone(user_delegation_key_1.value)

        # Assert key1 and key2 are equal, since they have the exact same start and end times
        self.assertEqual(user_delegation_key_1.signed_oid, user_delegation_key_2.signed_oid)
        self.assertEqual(user_delegation_key_1.signed_tid, user_delegation_key_2.signed_tid)
        self.assertEqual(user_delegation_key_1.signed_start, user_delegation_key_2.signed_start)
        self.assertEqual(user_delegation_key_1.signed_expiry, user_delegation_key_2.signed_expiry)
        self.assertEqual(user_delegation_key_1.signed_version, user_delegation_key_2.signed_version)
        self.assertEqual(user_delegation_key_1.signed_service, user_delegation_key_2.signed_service)
        self.assertEqual(user_delegation_key_1.value, user_delegation_key_2.value)

    def test_user_delegation_sas_for_blob(self):
        pytest.skip("Current Framework Cannot Support OAUTH")
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        token_credential = self.generate_oauth_token()
        service_client = BlobServiceClient(self._get_oauth_account_url(), credential=token_credential)
        user_delegation_key = service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        container_client = service_client.create_container(self.get_resource_name('oauthcontainer'))
        blob_client = container_client.get_blob_client(self.get_resource_name('oauthblob'))
        blob_client.upload_blob(self.byte_data, length=len(self.byte_data))

        token = blob_client.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            user_delegation_key=user_delegation_key,
            account_name='emilydevtest',
        )

        # Act
        # Use the generated identity sas
        new_blob_client = BlobClient.from_blob_url(blob_client.url, credential=token)
        content = new_blob_client.download_blob()

        # Assert
        self.assertEqual(self.byte_data, b"".join(list(content)))

    @record
    def test_token_credential(self):
        token_credential = self.generate_oauth_token()
        get_token = token_credential.get_token

        # Action 1: make sure token works
        service = BlobServiceClient(self._get_oauth_account_url(), credential=token_credential)
        result = service.get_service_properties()
        self.assertIsNotNone(result)

        # Action 2: change token value to make request fail
        fake_credential = self.generate_fake_token()
        service = BlobServiceClient(self._get_oauth_account_url(), credential=fake_credential)
        with self.assertRaises(ClientAuthenticationError):
            service.get_service_properties()

        # Action 3: update token to make it working again
        service = BlobServiceClient(self._get_oauth_account_url(), credential=token_credential)
        result = service.get_service_properties()
        self.assertIsNotNone(result)

    @record
    def test_shared_read_access_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_shared_read_access_blob_with_content_query_params(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_shared_write_access_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_shared_delete_access_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_get_account_information(self):
        # Act
        info = self.bsc.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @record
    def test_get_account_information_with_container_name(self):
        # Act
        # Container name gets ignored
        container = self.bsc.get_container_client("missing")
        info = container.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @record
    def test_get_account_information_with_blob_name(self):
        # Act
        # Both container and blob names get ignored
        blob = self.bsc.get_blob_client("missing", "missing")
        info = blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @record
    def test_get_account_information_with_container_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_get_account_information_with_blob_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_download_to_file_with_sas(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        sas_token = source_blob.generate_shared_access_signature(
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)


        # Act
        download_blob_from_url(blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_download_to_file_with_credential(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)

        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            max_concurrency=2,
            credential=self.settings.REMOTE_STORAGE_ACCOUNT_KEY)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_download_to_stream_with_credential(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            download_blob_from_url(
                source_blob.url, stream,
                max_concurrency=2,
                credential=self.settings.REMOTE_STORAGE_ACCOUNT_KEY)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_download_to_file_with_existing_file(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)

        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=self.settings.REMOTE_STORAGE_ACCOUNT_KEY)

        with self.assertRaises(ValueError):
            download_blob_from_url(source_blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_download_to_file_with_existing_file_overwrite(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)

        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=self.settings.REMOTE_STORAGE_ACCOUNT_KEY)

        data2 = b'ABCDEFGH' * 1024 * 1024
        source_blob = self._create_remote_block_blob(blob_data=data2)
        download_blob_from_url(
            source_blob.url, FILE_PATH, overwrite=True,
            credential=self.settings.REMOTE_STORAGE_ACCOUNT_KEY)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data2, actual)

    @record
    def test_upload_to_url_bytes_with_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_upload_to_url_bytes_with_credential(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=self.settings.STORAGE_ACCOUNT_KEY)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(data, content)

    @record
    def test_upload_to_url_bytes_with_existing_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        with self.assertRaises(ResourceExistsError):
            upload_blob_to_url(
                blob.url, data, credential=self.settings.STORAGE_ACCOUNT_KEY)

        # Assert
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(b"existing_data", content)

    @record
    def test_upload_to_url_bytes_with_existing_blob_overwrite(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data,
            overwrite=True,
            credential=self.settings.STORAGE_ACCOUNT_KEY)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(data, content)

    @record
    def test_upload_to_url_text_with_credential(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        data = '12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=self.settings.STORAGE_ACCOUNT_KEY)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_text()
        self.assertEqual(data, content)

    @record
    def test_upload_to_url_file_with_credential(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        data = b'12345678' * 1024 * 1024
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        with open(FILE_PATH, 'rb'):
            uploaded = upload_blob_to_url(
                blob.url, data, credential=self.settings.STORAGE_ACCOUNT_KEY)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().content_as_bytes()
        self.assertEqual(data, content)

    def test_set_blob_permission_from_string(self):
        # Arrange
        permission1 = BlobSasPermissions(read=True, write=True)
        permission2 = BlobSasPermissions.from_string('wr')
        self.assertEqual(permission1.read, permission2.read)
        self.assertEqual(permission1.write, permission2.write)

    def test_set_blob_permission(self):
        # Arrange
        permission = BlobSasPermissions.from_string('wrdx')
        self.assertEqual(permission.read, True)
        self.assertEqual(permission.delete, True)
        self.assertEqual(permission.write, True)
        self.assertEqual(permission._str, 'wrdx')

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
