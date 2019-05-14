# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import requests
import time
import unittest
from datetime import datetime, timedelta
from azure.common import (
    AzureHttpError,
    AzureMissingResourceHttpError,
    AzureException,
)
from azure.storage.common import (
    AccessPolicy,
    ResourceTypes,
    AccountPermissions,
    DeleteRetentionPolicy,
    TokenCredential,
)
from azure.storage.blob import (
    #Blob,  # TODO
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    # BlobPermissions,
    # ContentSettings,
    # DeleteSnapshot,
    # Include,
    # ContainerPermissions,
)
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
)

#------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
#------------------------------------------------------------------------------

class StorageCommonBlobTest(StorageTestCase):

    def setUp(self):
        super(StorageCommonBlobTest, self).setUp()

        url = self._get_account_url()
        credentials = SharedKeyCredentials(*self._get_shared_key_credentials())
        self.bsc = BlobServiceClient(url, credentials=credentials)

        #self.bs = self._create_storage_service(BlockBlobService, self.settings)
        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bs.create_container(self.container_name)

        self.byte_data = self.get_random_bytes(1024)

        self.bs2 = self._create_remote_storage_service(BlockBlobService, self.settings)
        self.remote_container_name = None

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bs.delete_container(self.container_name)
            except:
                pass

            if self.remote_container_name:
                try:
                    self.bs2.delete_container(self.remote_container_name)
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
        self.bs.create_blob_from_bytes(self.container_name, blob_name, self.byte_data)
        return blob_name

    def _create_remote_container(self):
        self.remote_container_name = self.get_resource_name('remotectnr')
        self.bs2.create_container(self.remote_container_name)

    def _create_remote_block_blob(self, blob_data=None):
        if not blob_data:
            blob_data = b'12345678' * 1024 * 1024
        source_blob_name = self._get_blob_reference()
        self.bs2.create_blob_from_bytes(
            self.remote_container_name, source_blob_name, blob_data)
        return source_blob_name

    def _wait_for_async_copy(self, container_name, blob_name):
        count = 0
        blob = self.bs.get_blob_properties(container_name, blob_name)
        while blob.properties.copy.status != 'success':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            blob = self.bs.get_blob_properties(container_name, blob_name)
        self.assertEqual(blob.properties.copy.status, 'success')

    def _enable_soft_delete(self):
        delete_retention_policy = DeleteRetentionPolicy(enabled=True, days=2)
        self.bs.set_blob_service_properties(delete_retention_policy=delete_retention_policy)

        # wait until the policy has gone into effect
        if not self.is_playback():
            time.sleep(30)

    def _disable_soft_delete(self):
        delete_retention_policy = DeleteRetentionPolicy(enabled=False)
        self.bs.set_blob_service_properties(delete_retention_policy=delete_retention_policy)

    def _assert_blob_is_soft_deleted(self, blob):
        self.assertTrue(blob.deleted)
        self.assertIsNotNone(blob.properties.deleted_time)
        self.assertIsNotNone(blob.properties.remaining_retention_days)

    def _assert_blob_not_soft_deleted(self, blob):
        self.assertFalse(blob.deleted)
        self.assertIsNone(blob.properties.deleted_time)
        self.assertIsNone(blob.properties.remaining_retention_days)

    #-- Common test cases for blobs ----------------------------------------------
    @record
    def test_blob_exists(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        exists = self.bs.exists(self.container_name, blob_name)

        # Assert
        self.assertTrue(exists)

    @record
    def test_blob_not_exists(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        exists = self.bs.exists(self.container_name, blob_name)

        # Assert
        self.assertFalse(exists)

    @record
    def test_blob_snapshot_exists(self):
        # Arrange
        blob_name = self._create_block_blob()
        snapshot = self.bs.snapshot_blob(self.container_name, blob_name)

        # Act
        exists = self.bs.exists(self.container_name, blob_name, snapshot.snapshot)

        # Assert
        self.assertTrue(exists)

    @record
    def test_blob_snapshot_not_exists(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        exists = self.bs.exists(self.container_name, blob_name, "1988-08-18T07:52:31.6690068Z")

        # Assert
        self.assertFalse(exists)

    @record
    def test_blob_container_not_exists(self):
        # In this case both the blob and container do not exist
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        exists = self.bs.exists(self._get_container_reference(), blob_name)

        # Assert
        self.assertFalse(exists)

    @record
    def test_make_blob_url(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd')

    @record
    def test_make_blob_url_with_protocol(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd', protocol='http')

        # Assert
        self.assertEqual(res, 'http://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd')

    @record
    def test_make_blob_url_with_sas(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd', sas_token='sas')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd?sas')

    @record
    def test_make_blob_url_with_snapshot(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd',
                                    snapshot='2016-11-09T14:11:07.6175300Z')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd?'
                           'snapshot=2016-11-09T14:11:07.6175300Z')

    @record
    def test_make_blob_url_with_snapshot_and_sas(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd', sas_token='sas',
                                    snapshot='2016-11-09T14:11:07.6175300Z')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd?'
                           'snapshot=2016-11-09T14:11:07.6175300Z&sas')

    def test_make_container_url(self):
        # Arrange

        # Act
        res = self.bs.make_container_url('vhds')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds?restype=container')

    def test_make_container_url_with_protocol(self):
        # Arrange

        # Act
        res = self.bs.make_container_url('vhds', protocol='http')

        # Assert
        self.assertEqual(res, 'http://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds?restype=container')

    def test_make_container_url_with_sas(self):
        # Arrange

        # Act
        res = self.bs.make_container_url('vhds', sas_token='sas')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds?restype=container&sas')

    @record
    def test_create_blob_with_question_mark(self):
        # Arrange
        blob_name = '?ques?tion?'
        blob_data = u'???'

        # Act
        self.bs.create_blob_from_text(self.container_name, blob_name, blob_data)

        # Assert
        blob = self.bs.get_blob_to_text(self.container_name, blob_name)
        self.assertEqual(blob.content, blob_data)

    @record
    def test_create_blob_with_special_chars(self):
        # Arrange

        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            self.bs.create_blob_from_text(self.container_name, blob_name, blob_data)
            blob = self.bs.get_blob_to_text(self.container_name, blob_name)
            self.assertEqual(blob.content, blob_data)

        # Assert

    @record
    def test_create_blob_with_lease_id(self):
        # Arrange
        blob_name = self._create_block_blob()
        lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name)

        # Act
        data = b'hello world again'
        resp = self.bs.create_blob_from_bytes (
            self.container_name, blob_name, data,
            lease_id=lease_id)

        # Assert
        self.assertIsNotNone(resp.etag)
        blob = self.bs.get_blob_to_bytes(
            self.container_name, blob_name, lease_id=lease_id)
        self.assertEqual(blob.content, b'hello world again')

    @record
    def test_create_blob_with_metadata(self):
        # Arrange
        blob_name = self._get_blob_reference()
        metadata={'hello': 'world', 'number': '42'}

        # Act
        data = b'hello world'
        resp = self.bs.create_blob_from_bytes(
            self.container_name, blob_name, data, metadata=metadata)

        # Assert
        self.assertIsNotNone(resp.etag)
        md = self.bs.get_blob_metadata(self.container_name, blob_name)
        self.assertDictEqual(md, metadata)

    @record
    def test_get_blob_with_existing_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, self.byte_data)

    @record
    def test_get_blob_with_snapshot(self):
        # Arrange
        blob_name = self._create_block_blob()
        snapshot = self.bs.snapshot_blob(self.container_name, blob_name)

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, snapshot.snapshot)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, self.byte_data)

    @record
    def test_get_blob_with_snapshot_previous(self):
        # Arrange
        blob_name = self._create_block_blob()
        snapshot = self.bs.snapshot_blob(self.container_name, blob_name)
        self.bs.create_blob_from_bytes (self.container_name, blob_name,
                         b'hello world again', )

        # Act
        blob_previous = self.bs.get_blob_to_bytes(
            self.container_name, blob_name, snapshot.snapshot)
        blob_latest = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertIsInstance(blob_previous, Blob)
        self.assertIsInstance(blob_latest, Blob)
        self.assertEqual(blob_previous.content, self.byte_data)
        self.assertEqual(blob_latest.content, b'hello world again')

    @record
    def test_get_blob_with_range(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, start_range=0, end_range=5)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, self.byte_data[:6])

    @record
    def test_get_blob_with_lease(self):
        # Arrange
        blob_name = self._create_block_blob()
        lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name)

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, lease_id=lease_id)
        self.bs.release_blob_lease(self.container_name, blob_name, lease_id)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, self.byte_data)

    @record
    def test_get_blob_with_non_existing_blob(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert

    @record
    def test_set_blob_properties_with_existing_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        self.bs.set_blob_properties(
            self.container_name,
            blob_name,
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
        )

        # Assert
        blob = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertEqual(blob.properties.content_settings.content_language, 'spanish')
        self.assertEqual(blob.properties.content_settings.content_disposition, 'inline')

    @record
    def test_set_blob_properties_with_blob_settings_param(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Act
        blob.properties.content_settings.content_language = 'spanish'
        blob.properties.content_settings.content_disposition = 'inline'
        self.bs.set_blob_properties(
            self.container_name,
            blob_name,
            content_settings=blob.properties.content_settings,
        )

        # Assert
        blob = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertEqual(blob.properties.content_settings.content_language, 'spanish')
        self.assertEqual(blob.properties.content_settings.content_disposition, 'inline')

    @record
    def test_get_blob_properties(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.properties.blob_type, self.bs.blob_type)
        self.assertEqual(blob.properties.content_length, len(self.byte_data))
        self.assertEqual(blob.properties.lease.status, 'unlocked')
        self.assertIsNotNone(blob.properties.creation_time)

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # HEAD request.
    @record
    def test_get_blob_properties_fail(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        with self.assertRaises(AzureException) as e:
            self.bs.get_blob_properties(self.container_name, blob_name, 1) # Invalid snapshot value of 1

        # Assert
        self.assertIn('ErrorCode: InvalidQueryParameterValue', str(e.exception))

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # GET request. This is preferred to relying on the ErrorCode in the body.
    @ record
    def test_get_blob_metadata_fail(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        with self.assertRaises(AzureException) as e:
            self.bs.get_blob_metadata(self.container_name, blob_name, 1) # Invalid snapshot value of 1

        # Assert
        self.assertIn('ErrorCode: InvalidQueryParameterValue', str(e.exception))

    @record
    def test_get_blob_server_encryption(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertTrue(blob.properties.server_encrypted)

    @record
    def test_get_blob_properties_server_encryption(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertTrue(blob.properties.server_encrypted)

    @record
    def test_list_blobs_server_encryption(self):
        #Arrange
        self._create_block_blob()
        self._create_block_blob()
        blob_list = self.bs.list_blobs(self.container_name)

        #Act

        #Assert
        for blob in blob_list:
            self.assertTrue(blob.properties.server_encrypted)

    @record
    def test_no_server_encryption(self):
        # Arrange
        blob_name = self._create_block_blob()

        #Act
        def callback(response):
            response.headers['x-ms-server-encrypted'] = 'false'

        self.bs.response_callback = callback
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        #Assert
        self.assertFalse(blob.properties.server_encrypted)

    @record
    def test_get_blob_properties_with_snapshot(self):
        # Arrange
        blob_name = self._create_block_blob()
        res = self.bs.snapshot_blob(self.container_name, blob_name)
        blobs = list(self.bs.list_blobs(self.container_name, include='snapshots'))
        self.assertEqual(len(blobs), 2)

        # Act
        blob = self.bs.get_blob_properties(self.container_name, blob_name, snapshot=res.snapshot)

        # Assert
        self.assertIsNotNone(blob)
        self.assertEqual(blob.properties.blob_type, self.bs.blob_type)
        self.assertEqual(blob.properties.content_length, len(self.byte_data))

    @record
    def test_get_blob_properties_with_leased_blob(self):
        # Arrange
        blob_name = self._create_block_blob()
        lease = self.bs.acquire_blob_lease(self.container_name, blob_name)

        # Act
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.properties.blob_type, self.bs.blob_type)
        self.assertEqual(blob.properties.content_length, len(self.byte_data))
        self.assertEqual(blob.properties.lease.status, 'locked')
        self.assertEqual(blob.properties.lease.state, 'leased')
        self.assertEqual(blob.properties.lease.duration, 'infinite')

    @record
    def test_get_blob_metadata(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        md = self.bs.get_blob_metadata(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_set_blob_metadata_with_upper_case(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob()

        # Act
        self.bs.set_blob_metadata(self.container_name, blob_name, metadata)

        # Assert
        md = self.bs.get_blob_metadata(self.container_name, blob_name)
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
        resp = self.bs.delete_blob(self.container_name, blob_name)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_non_existing_blob(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.delete_blob (self.container_name, blob_name)

        # Assert

    @record
    def test_delete_blob_snapshot(self):
        # Arrange
        blob_name = self._create_block_blob()
        res = self.bs.snapshot_blob(self.container_name, blob_name)

        # Act
        self.bs.delete_blob(self.container_name, blob_name, snapshot=res.snapshot)

        # Assert
        blobs = list(self.bs.list_blobs(self.container_name, include='snapshots'))
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0].name, blob_name)
        self.assertIsNone(blobs[0].snapshot)

    @record
    def test_delete_blob_snapshots(self):
        # Arrange
        blob_name = self._create_block_blob()
        self.bs.snapshot_blob(self.container_name, blob_name)

        # Act
        self.bs.delete_blob(self.container_name, blob_name,
                            delete_snapshots=DeleteSnapshot.Only)

        # Assert
        blobs = list(self.bs.list_blobs(self.container_name, include='snapshots'))
        self.assertEqual(len(blobs), 1)
        self.assertIsNone(blobs[0].snapshot)

    @record
    def test_delete_blob_with_snapshots(self):
        # Arrange
        blob_name = self._create_block_blob()
        self.bs.snapshot_blob(self.container_name, blob_name)

        # Act
        self.bs.delete_blob(self.container_name, blob_name,
                            delete_snapshots=DeleteSnapshot.Include)

        # Assert
        blobs = list(self.bs.list_blobs(self.container_name, include='snapshots'))
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
            blob_list = list(container.list_blob_properties(include=Include(deleted=True)))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(container.list_blob_properties())

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include=Include(deleted=True)))

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
            blob_snapshot_1 = self.bs.snapshot_blob(self.container_name, blob_name)
            blob_snapshot_2 = self.bs.snapshot_blob(self.container_name, blob_name)

            # Soft delete blob_snapshot_1
            self.bs.delete_blob(self.container_name, blob_name, snapshot=blob_snapshot_1.snapshot)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True, snapshots=True)))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                if blob.snapshot == blob_snapshot_1.snapshot:
                    self._assert_blob_is_soft_deleted(blob)
                else:
                    self._assert_blob_not_soft_deleted(blob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(snapshots=True)))

            # Assert
            self.assertEqual(len(blob_list), 2)

            # Restore snapshot with undelete
            self.bs.undelete_blob(self.container_name, blob_name)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True, snapshots=True)))

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
            blob_snapshot_1 = self.bs.snapshot_blob(self.container_name, blob_name)
            blob_snapshot_2 = self.bs.snapshot_blob(self.container_name, blob_name)

            # Soft delete all snapshots
            self.bs.delete_blob(self.container_name, blob_name, delete_snapshots=DeleteSnapshot.Only)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True, snapshots=True)))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                if blob.snapshot == blob_snapshot_1.snapshot:
                    self._assert_blob_is_soft_deleted(blob)
                elif blob.snapshot == blob_snapshot_2.snapshot:
                    self._assert_blob_is_soft_deleted(blob)
                else:
                    self._assert_blob_not_soft_deleted(blob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(snapshots=True)))

            # Assert
            self.assertEqual(len(blob_list), 1)

            # Restore snapshots with undelete
            self.bs.undelete_blob(self.container_name, blob_name)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True, snapshots=True)))

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
            blob_snapshot_1 = self.bs.snapshot_blob(self.container_name, blob_name)
            blob_snapshot_2 = self.bs.snapshot_blob(self.container_name, blob_name)

            # Soft delete blob and all snapshots
            self.bs.delete_blob(self.container_name, blob_name, delete_snapshots=DeleteSnapshot.Include)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True, snapshots=True)))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_is_soft_deleted(blob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(snapshots=True)))

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob and snapshots with undelete
            self.bs.undelete_blob(self.container_name, blob_name)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True, snapshots=True)))

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
            lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name)

            # Soft delete the blob without lease_id should fail
            with self.assertRaises(AzureHttpError):
                self.bs.delete_blob(self.container_name, blob_name)

            # Soft delete the blob
            self.bs.delete_blob(self.container_name, blob_name, lease_id=lease_id)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True)))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(self.bs.list_blobs(self.container_name))

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete, this also gets rid of the lease
            self.bs.undelete_blob(self.container_name, blob_name)
            blob_list = list(self.bs.list_blobs(self.container_name, include=Include(deleted=True)))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            self._disable_soft_delete()

    @record
    def test_copy_blob_with_existing_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        sourceblob = '/{0}/{1}/{2}'.format(self.settings.STORAGE_ACCOUNT_NAME,
                                           self.container_name,
                                           blob_name)
        copy = self.bs.copy_blob(self.container_name, 'blob1copy', sourceblob)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy.status, 'success')
        self.assertIsNotNone(copy.id)
        copy_blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1copy')
        self.assertEqual(copy_blob.content, self.byte_data)

    @record
    def test_copy_blob_async_private_blob(self):
        # Arrange
        self._create_remote_container()
        source_blob_name = self._create_remote_block_blob()
        source_blob_url = self.bs2.make_blob_url(self.remote_container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        with self.assertRaises(AzureMissingResourceHttpError):
            self.bs.copy_blob(self.container_name, target_blob_name, source_blob_url)

        # Assert

    @record
    def test_copy_blob_async_private_blob_with_sas(self):
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob_name = self._create_remote_block_blob(blob_data=data)

        sas_token = self.bs2.generate_blob_shared_access_signature(
            self.remote_container_name,
            source_blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        source_blob_url = self.bs2.make_blob_url(
            self.remote_container_name,
            source_blob_name,
            sas_token=sas_token,
        )

        # Act
        target_blob_name = 'targetblob'
        copy_resp = self.bs.copy_blob(
            self.container_name, target_blob_name, source_blob_url)

        # Assert
        self.assertEqual(copy_resp.status, 'pending')
        self._wait_for_async_copy(self.container_name, target_blob_name)
        actual_data = self.bs.get_blob_to_bytes(self.container_name, target_blob_name)
        self.assertEqual(actual_data.content, data)

    @record
    def test_abort_copy_blob(self):
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob_name = self._create_remote_block_blob(blob_data=data)

        sas_token = self.bs2.generate_blob_shared_access_signature(
            self.remote_container_name,
            source_blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),          
        )

        source_blob_url = self.bs2.make_blob_url(
            self.remote_container_name,
            source_blob_name,
            sas_token=sas_token,
        )

        # Act
        target_blob_name = 'targetblob'
        copy_resp = self.bs.copy_blob(
            self.container_name, target_blob_name, source_blob_url)
        self.assertEqual(copy_resp.status, 'pending')
        self.bs.abort_copy_blob(
            self.container_name, 'targetblob', copy_resp.id)

        # Assert
        target_blob = self.bs.get_blob_to_bytes(self.container_name, target_blob_name)
        self.assertEqual(target_blob.content, b'')
        self.assertEqual(target_blob.properties.copy.status, 'aborted')

    @record
    def test_abort_copy_blob_with_synchronous_copy_fails(self):
        # Arrange
        source_blob_name = self._create_block_blob()
        source_blob_url = self.bs.make_blob_url(
            self.container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        copy_resp = self.bs.copy_blob(
            self.container_name, target_blob_name, source_blob_url)
        with self.assertRaises(AzureHttpError):
            self.bs.abort_copy_blob(
                self.container_name,
                target_blob_name,
                copy_resp.id)

        # Assert
        self.assertEqual(copy_resp.status, 'success')

    @record
    def test_snapshot_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        resp = self.bs.snapshot_blob(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.snapshot)

    @record
    def test_lease_blob_acquire_and_release(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name)
        self.bs.release_blob_lease(self.container_name, blob_name, lease_id)
        lease_id2 = self.bs.acquire_blob_lease(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(lease_id)
        self.assertIsNotNone(lease_id2)

    @record
    def test_lease_blob_with_duration(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        lease_id = self.bs.acquire_blob_lease(
            self.container_name, blob_name, lease_duration=15)
        resp2 = self.bs.create_blob_from_bytes (self.container_name, blob_name, b'hello 2',
                                 lease_id=lease_id)
        self.sleep(15)

        # Assert
        with self.assertRaises(AzureHttpError):
            self.bs.create_blob_from_bytes (self.container_name, blob_name, b'hello 3',
                             lease_id=lease_id)

    @record
    def test_lease_blob_with_proposed_lease_id(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease_id1 = self.bs.acquire_blob_lease(
            self.container_name, blob_name,
            proposed_lease_id=lease_id)

        # Assert
        self.assertEqual(lease_id1, lease_id)

    @record
    def test_lease_blob_change_lease_id(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        cur_lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name)
        self.bs.change_blob_lease(self.container_name, blob_name, cur_lease_id, lease_id)
        next_lease_id = self.bs.renew_blob_lease(self.container_name, blob_name, lease_id)

        # Assert
        self.assertNotEqual(cur_lease_id, next_lease_id)
        self.assertEqual(next_lease_id, lease_id)

    @record
    def test_lease_blob_break_period(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name,
                                   lease_duration=15)
        lease_time = self.bs.break_blob_lease(self.container_name, blob_name,
                                   lease_break_period=5)
        blob = self.bs.create_blob_from_bytes (self.container_name, blob_name, b'hello 2', lease_id=lease_id)
        self.sleep(5)

        with self.assertRaises(AzureHttpError):
            self.bs.create_blob_from_bytes (self.container_name, blob_name, b'hello 3', lease_id=lease_id)

        # Assert
        self.assertIsNotNone(lease_id)
        self.assertIsNotNone(lease_time)
        self.assertIsNotNone(blob.etag)

    @record
    def test_lease_blob_acquire_and_renew(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        lease_id1 = self.bs.acquire_blob_lease(self.container_name, blob_name)
        lease_id2 = self.bs.renew_blob_lease(self.container_name, blob_name, lease_id1)

        # Assert
        self.assertEqual(lease_id1, lease_id2)

    @record
    def test_lease_blob_acquire_twice_fails(self):
        # Arrange
        blob_name = self._create_block_blob()
        lease_id1 = self.bs.acquire_blob_lease(self.container_name, blob_name)

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.acquire_blob_lease(self.container_name, blob_name)
        self.bs.release_blob_lease(self.container_name, blob_name, lease_id1)

        # Assert
        self.assertIsNotNone(lease_id1)

    @record
    def test_unicode_get_blob_unicode_name(self):
        # Arrange
        blob_name = '啊齄丂狛狜'
        self.bs.create_blob_from_bytes(self.container_name, blob_name, b'hello world')

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, b'hello world')

    @record
    def test_create_blob_blob_unicode_data(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        resp = self.bs.create_blob_from_bytes (
            self.container_name, blob_name, data, )

        # Assert
        self.assertIsNotNone(resp.etag)

    @record
    def test_no_sas_private_blob(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        url = self.bs.make_blob_url(self.container_name, blob_name)
        response = requests.get(url)

        # Assert
        self.assertFalse(response.ok)
        self.assertNotEqual(-1, response.text.find('ResourceNotFound'))

    @record
    def test_no_sas_public_blob(self):
        # Arrange
        data = b'a public blob can be read without a shared access signature'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        self.bs.create_container(container_name, None, 'blob')
        self.bs.create_blob_from_bytes (container_name, blob_name, data, )

        # Act
        url = self.bs.make_blob_url(container_name, blob_name)
        response = requests.get(url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)

    @record
    def test_public_access_blob(self):
        # Arrange
        data = b'public access blob'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        self.bs.create_container(container_name, None, 'blob')
        self.bs.create_blob_from_bytes (container_name, blob_name, data, )

        # Act
        service = BlockBlobService(
            self.settings.STORAGE_ACCOUNT_NAME,
            request_session=requests.Session(),
        )
        self._set_test_proxy(service, self.settings)
        result = service.get_blob_to_bytes(container_name, blob_name)

        # Assert
        self.assertEqual(data, result.content)

    @record
    def test_sas_access_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()
        
        token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = BlockBlobService(
            self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
            request_session=requests.Session(),
        )
        self._set_test_proxy(service, self.settings)
        result = service.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(self.byte_data, result.content)

    @record
    def test_sas_signed_identifier(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()

        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = BlobPermissions.READ
        identifiers = {'testid': access_policy}

        resp = self.bs.set_container_acl(self.container_name, identifiers)

        token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            blob_name,
            id='testid'
            )

        # Act
        service = BlockBlobService(
            self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
            request_session=requests.Session(),
        )
        self._set_test_proxy(service, self.settings)
        result = service.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(self.byte_data, result.content)

    @record
    def test_account_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()

        token = self.bs.generate_account_shared_access_signature(
            ResourceTypes.OBJECT + ResourceTypes.CONTAINER,
            AccountPermissions.READ,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob_url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )
        container_url = self.bs.make_container_url(
            self.container_name,
            sas_token=token,
        )

        blob_response = requests.get(blob_url)
        container_response = requests.get(container_url)

        # Assert
        self.assertTrue(blob_response.ok)
        self.assertEqual(self.byte_data, blob_response.content)
        self.assertTrue(container_response.ok)

    @record
    def test_token_credential(self):
        token_credential = TokenCredential(self.generate_oauth_token())

        # Action 1: make sure token works
        service = BlockBlobService(self.settings.OAUTH_STORAGE_ACCOUNT_NAME, token_credential=token_credential)
        result = service.exists("test")
        self.assertIsNotNone(result)

        # Action 2: change token value to make request fail
        token_credential.token = "YOU SHALL NOT PASS"
        with self.assertRaises(AzureException):
            result = service.exists("test")
            self.assertIsNone(result)

        # Action 3: update token to make it working again
        token_credential.token = self.generate_oauth_token()
        result = service.exists("test")
        self.assertIsNotNone(result)

    @record
    def test_shared_read_access_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()

        token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )
        response = requests.get(url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(self.byte_data, response.content)

    @record
    def test_shared_read_access_blob_with_content_query_params(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()

        token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )

        # Act
        response = requests.get(url)

        # Assert
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

        token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            blob_name,
            permission=BlobPermissions.WRITE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )

        # Act
        headers = {'x-ms-blob-type': self.bs.blob_type}
        response = requests.put(url, headers=headers, data=updated_data)

        # Assert
        self.assertTrue(response.ok)
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)
        self.assertEqual(updated_data, blob.content)

    @record
    def test_shared_delete_access_blob(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()

        token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            blob_name,
            permission=BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )

        # Act
        response = requests.delete(url)

        # Assert
        self.assertTrue(response.ok)
        with self.assertRaises(AzureMissingResourceHttpError):
            blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)

    @record
    def test_get_account_information(self):
        # Act
        info = self.bs.get_blob_account_information()

        # Assert
        self.assertIsNotNone(info.sku_name)
        self.assertIsNotNone(info.account_kind)

    @record
    def test_get_account_information_with_container_name(self):
        # Act
        # Container name gets ignored
        info = self.bs.get_blob_account_information("missing")

        # Assert
        self.assertIsNotNone(info.sku_name)
        self.assertIsNotNone(info.account_kind)

    @record
    def test_get_account_information_with_blob_name(self):
        # Act
        # Both container and blob names get ignored
        info = self.bs.get_blob_account_information("missing", "missing")

        # Assert
        self.assertIsNotNone(info.sku_name)
        self.assertIsNotNone(info.account_kind)

    @record
    def test_get_account_information_with_container_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        token = self.bs.generate_container_shared_access_signature(
            self.container_name,
            permission=ContainerPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        bs_with_sas = BlockBlobService(account_name=self.settings.STORAGE_ACCOUNT_NAME, sas_token=token,
                                       protocol=self.settings.PROTOCOL)

        # Act
        info = bs_with_sas.get_blob_account_information(self.container_name)

        # Assert
        self.assertIsNotNone(info.sku_name)
        self.assertIsNotNone(info.account_kind)

    @record
    def test_get_account_information_with_blob_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()

        token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        bs_with_sas = BlockBlobService(account_name=self.settings.STORAGE_ACCOUNT_NAME, sas_token=token,
                                       protocol=self.settings.PROTOCOL)

        # Act
        info = bs_with_sas.get_blob_account_information(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(info.sku_name)
        self.assertIsNotNone(info.account_kind)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
