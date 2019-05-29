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
from datetime import datetime, timedelta
from azure.common import (
    AzureHttpError,
    AzureMissingResourceHttpError,
    AzureException,
)
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.common import (
    AccessPolicy,
    ResourceTypes,
    AccountPermissions,
    TokenCredential,
)
from azure.storage.blob import (
    SharedKeyCredentials,
    BlobServiceClient,
    ContainerClient,
    BlobClient
)
from azure.storage.blob.models import (
    BlobPermissions,
    ContentSettings,
    BlobProperties,
    RetentionPolicy,
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

        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            container = self.bsc.get_container_client(self.container_name)
            container.create_container()

        self.byte_data = self.get_random_bytes(1024)

        remote_url = self._get_remote_account_url()
        remote_credentials = SharedKeyCredentials(*self._get_remote_shared_key_credentials())
        self.bsc2 = BlobServiceClient(remote_url, credentials=remote_credentials)
        self.remote_container_name = None

    def tearDown(self):
        if not self.is_playback():
            try:
                container = self.bsc.get_container_client(self.container_name)
                container.delete_container()
            except:
                pass

            if self.remote_container_name:
                try:
                    container = self.bsc2.get_container_client(self.remote_container_name)
                    container.delete_container()
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
        remote_container.create_container()

    def _create_remote_block_blob(self, blob_data=None):
        if not blob_data:
            blob_data = b'12345678' * 1024 * 1024
        source_blob_name = self._get_blob_reference()
        source_blob = self.bsc2.get_blob_client(self.remote_container_name, source_blob_name)
        source_blob.upload_blob(blob_data)
        return source_blob

    def _wait_for_async_copy(self, container_name, blob_name):
        count = 0
        blob = self.bsc.get_blob_client(container_name, blob_name)
        props = blob.get_blob_properties()
        while props.copy.status != 'success':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            props = blob.get_blob_properties()
        self.assertEqual(props.copy.status, 'success')

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
        blob = self.bsc.get_blob_client(self.container_name, snapshot)
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
    def test_make_blob_url(self):
        # Arrange

        # Act
        blob = self.bsc.get_blob_client("vhds", "my.vhd")
        res = blob.make_url()

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd')

    @record
    def test_make_blob_url_with_protocol(self):
        # Arrange

        # Act
        blob = self.bsc.get_blob_client("vhds", "my.vhd")
        res = blob.make_url(protocol='http')

        # Assert
        self.assertEqual(res, 'http://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd')

    @record
    def test_make_blob_url_with_sas(self):
        # Arrange

        # Act
        blob = self.bsc.get_blob_client("vhds", "my.vhd")
        res = blob.make_url(sas_token='sas')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd?sas')

    @record
    def test_make_blob_url_with_snapshot(self):
        # Arrange

        # Act
        blob = self.bsc.get_blob_client("vhds", "my.vhd", snapshot='2016-11-09T14:11:07.6175300Z')
        res = blob.make_url()

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd?'
                           'snapshot=2016-11-09T14:11:07.6175300Z')

    @record
    def test_make_blob_url_with_snapshot_and_sas(self):
        # Arrange

        # Act
        blob = self.bsc.get_blob_client("vhds", "my.vhd", snapshot='2016-11-09T14:11:07.6175300Z')
        res = blob.make_url(sas_token='sas')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds/my.vhd?'
                           'snapshot=2016-11-09T14:11:07.6175300Z&sas')

    def test_make_container_url(self):
        pytest.skip("not yet supported")
        # Arrange

        # Act
        res = self.bs.make_container_url('vhds')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds?restype=container')

    def test_make_container_url_with_protocol(self):
        pytest.skip("not yet supported")
        # Arrange

        # Act
        res = self.bs.make_container_url('vhds', protocol='http')

        # Assert
        self.assertEqual(res, 'http://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.blob.core.windows.net/vhds?restype=container')

    def test_make_container_url_with_sas(self):
        pytest.skip("not yet supported")
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
            blob.upload_blob(blob_data, len(blob_data))

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
        resp = blob.upload_blob(data, len(data), lease=lease)

        # Assert
        self.assertIsNotNone(resp.get('ETag'))
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
        resp = blob.upload_blob(data, len(data), metadata=metadata)

        # Assert
        self.assertIsNotNone(resp.get('ETag'))
        md = blob.get_blob_metadata()
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
        snapshot = self.bsc.get_blob_client(self.container_name, blob.create_snapshot())

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
        snapshot = self.bsc.get_blob_client(self.container_name, blob.create_snapshot())

        upload_data = b'hello world again'
        blob.upload_blob(upload_data, len(upload_data))

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
        self.assertEqual(b"".join(list(data)), self.byte_data[:6])

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
        blob.set_blob_properties(
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
        blob.set_blob_properties(content_settings=props.content_settings)

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
        self.assertEqual(props.blob_type, blob.blob_type)
        self.assertEqual(props.content_length, len(self.byte_data))
        self.assertEqual(props.lease.status, 'unlocked')
        self.assertIsNotNone(props.creation_time)

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # HEAD request.
    @record
    def test_get_blob_properties_fail(self):
        pytest.skip("Failing with no error code")  # TODO
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with self.assertRaises(HttpResponseError) as e:
            blob.get_blob_properties() # Invalid snapshot value of 1

        # Assert
        self.assertEqual('InvalidQueryParameterValue', e.exception.error_code)

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # GET request. This is preferred to relying on the ErrorCode in the body.
    @ record
    def test_get_blob_metadata_fail(self):
        pytest.skip("Failing with no error code")  # TODO
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with self.assertRaises(HttpResponseError) as e:
            blob.get_blob_metadata() # Invalid snapshot value of 1

        # Assert
        self.assertEqual('InvalidQueryParameterValue', e.exception.error_code)

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
        self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blob_properties()

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
        blobs = list(container.list_blob_properties(include='snapshots'))
        self.assertEqual(len(blobs), 2)

        # Act
        snapshot = self.bsc.get_blob_client(self.container_name, res)
        blob = snapshot.get_blob_properties()

        # Assert
        self.assertIsNotNone(blob)
        self.assertEqual(blob.blob_type, snapshot.blob_type)
        self.assertEqual(blob.content_length, len(self.byte_data))

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
        self.assertEqual(props.blob_type, blob.blob_type)
        self.assertEqual(props.content_length, len(self.byte_data))
        self.assertEqual(props.lease.status, 'locked')
        self.assertEqual(props.lease.state, 'leased')
        self.assertEqual(props.lease.duration, 'infinite')

    @record
    def test_get_blob_metadata(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        md = blob.get_blob_metadata()

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
        md = blob.get_blob_metadata()
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
        snapshot = self.bsc.get_blob_client(self.container_name, blob.create_snapshot())

        # Act
        snapshot.delete_blob()

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blob_properties(include='snapshots'))
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
        blob.delete_blob(delete_snapshots='only')  # TODO: Separate calls?

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blob_properties(include='snapshots'))
        self.assertEqual(len(blobs), 1)
        self.assertIsNone(blobs[0].snapshot)

    @record
    def test_delete_blob_with_snapshots(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.create_snapshot()

        # Act
        blob.delete_blob(delete_snapshots='include')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blob_properties(include='snapshots'))
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
            blob_list = list(container.list_blob_properties(include='deleted'))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(container.list_blob_properties())

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blob_properties(include='deleted'))

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
            snapshot_1 = self.bsc.get_blob_client(self.container_name, blob_snapshot_1)
            snapshot_1.delete_blob()

            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blob_properties(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1.snapshot:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blob_properties(include='snapshots'))

            # Assert
            self.assertEqual(len(blob_list), 2)

            # Restore snapshot with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blob_properties(include=["snapshots", "deleted"]))

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
            blob_list = list(container.list_blob_properties(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1.snapshot:
                    self._assert_blob_is_soft_deleted(listedblob)
                elif listedblob.snapshot == blob_snapshot_2.snapshot:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blob_properties(include="snapshots"))

            # Assert
            self.assertEqual(len(blob_list), 1)

            # Restore snapshots with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blob_properties(include=["snapshots", "deleted"]))

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
            blob.delete_blob(delete_snapshots="include")
            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blob_properties(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                self._assert_blob_is_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blob_properties(include=["snapshots"]))

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob and snapshots with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blob_properties(include=["snapshots", "deleted"]))

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
            blob_list = list(container.list_blob_properties(include="deleted"))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(container.list_blob_properties())

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete, this also gets rid of the lease
            blob.undelete_blob()
            blob_list = list(container.list_blob_properties(include="deleted"))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            self._disable_soft_delete()

    @record
    def test_copy_blob_with_existing_blob(self):
        pytest.skip("in progress")
        # Arrange
        # blob_name = self._create_block_blob()
        # blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # # # Act
        # source_blob = '/{0}/{1}/{2}'.format(self.settings.STORAGE_ACCOUNT_NAME,
        #                                    self.container_name,
        #                                    blob_name)
        import logging
        logger = logging.getLogger(__name__)

        source_blob = "http://www.gutenberg.org/files/59466/59466-0.txt"
        copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')
        copy = copied_blob.copy_blob_from_url(source_blob)
        self.assertEqual(copy.status(), 'pending')
        copy.wait()

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy.status(), 'success')
        self.assertIsNotNone(copy.id())
    
        #copy_blob = copied_blob.download_blob()
        #self.assertEqual(b"".join(list(copy_blob)), self.byte_data)

    @record
    def test_copy_blob_async_private_blob(self):
        pytest.skip("in progress")
        # Arrange
        self._create_remote_container()
        source_blob = self._create_remote_block_blob()
        source_blob_url = source_blob.make_url()

        # Act
        target_blob_name = 'targetblob'
        with self.assertRaises(ResourceNotFoundError):
            target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
            target_blob.copy_blob_from_url(source_blob_url)

        # Assert

    @record
    def test_copy_blob_async_private_blob_with_sas(self):
        pytest.skip("in progress")
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)

        sas_token = source_blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        source_blob_url = source_blob.make_url(sas_token=sas_token)
        #raise Exception(source_blob_url)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = target_blob.copy_blob_from_url(source_blob_url)

        # Assert
        #self.assertEqual(copy_resp.status(), 'pending')
        copy_resp.wait()
        self.assertEqual(copy_resp.status(), 'success')
        actual_data = target_blob.download_blob()
        self.assertEqual(b"".join(list(actual_data)), data)

    @record
    def test_abort_copy_blob(self):
        pytest.skip("in progress")
        import logging
        logger = logging.getLogger(__name__)
        # Arrange
        data = b'12345678' * 1024 * 1024
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        logger.warning("blob uploaded")
        sas_token = source_blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        source_blob_url = source_blob.make_url(sas_token=sas_token)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = target_blob.copy_blob_from_url(source_blob_url)

        #self.assertEqual(copy_resp.status(), 'pending')
        copy_resp.abort()

        # Assert
        actual_data = target_blob.download_blob()
        self.assertEqual(b"".join(list(actual_data)), data)
        self.assertEqual(actual_data.properties.copy.status, 'aborted')

    @record
    def test_abort_copy_blob_with_synchronous_copy_fails(self):
        pytest.skip("copy not yet supported")
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
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.create_snapshot()

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.snapshot)

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
        resp = blob.upload_blob(b'hello 2', 7, lease=lease)
        self.sleep(15)

        # Assert
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(b'hello 3', 7, lease=lease)

    @record
    def test_lease_blob_with_proposed_lease_id(self):
        # Arrange
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease(proposed_lease_id=lease_id)

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
        lease_time = blob.break_lease(lease_break_period=5)

        resp = blob.upload_blob(b'hello 2', 7, lease=lease)
        self.sleep(5)

        with self.assertRaises(HttpResponseError):
            blob.upload_blob(b'hello 3', 7, lease=lease)

        # Assert
        self.assertIsNotNone(lease.id)
        self.assertIsNotNone(lease_time)
        self.assertIsNotNone(resp.get('ETag'))

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
        pytest.skip("Not working")  # TODO
        # Arrange
        blob_name = '啊齄丂狛狜'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'hello world', 11)

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
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        resp = blob.upload_blob(data, len(data))

        # Assert
        self.assertIsNotNone(resp.get('ETag'))

    @record
    def test_no_sas_private_blob(self):
        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        url = blob.make_url()
        response = requests.get(url)

        # Assert
        self.assertFalse(response.ok)
        self.assertNotEqual(-1, response.text.find('ResourceNotFound'))

    @record
    def test_no_sas_public_blob(self):
        pytest.skip("not yet supported")
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
        pytest.skip("not yet supported")
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
        pytest.skip("not yet suppoerted")
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
        pytest.skip("not yet supported")
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
        pytest.skip("not yet suppoerted")
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
        pytest.skip("not yet supported")
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
        pytest.skip("failing with 404")  # TODO
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        url = blob.make_url(sas_token=token)
        response = requests.get(url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        self.assertEqual(self.byte_data, response.content)

    @record
    def test_shared_read_access_blob_with_content_query_params(self):
        # SAS URL is calculated from storage key, so this test runs live only
        pytest.skip("failing with 404")  # TODO
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )
        url = blob.make_url(sas_token=token)

        # Act
        response = requests.get(url)

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
        pytest.skip("failing with 404")  # TODO
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        updated_data = b'updated blob data'
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobPermissions.WRITE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        url = blob.make_url(sas_token=token)

        # Act
        headers = {'x-ms-blob-type': blob.blob_type}
        response = requests.put(url, headers=headers, data=updated_data)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        data = blob.download_blob()
        self.assertEqual(updated_data, b"".join(list(data)))

    @record
    def test_shared_delete_access_blob(self):
        pytest.skip("failing with 404")  # TODO
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        url = blob.make_url(sas_token=token)

        # Act
        response = requests.delete(url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        with self.assertRaises(ResourceNotFoundError):
            blob.download_blob()

    @record
    def test_get_account_information(self):
        pytest.skip("not yet supported")
        # Act)
        info = self.bs.get_blob_account_information()

        # Assert
        self.assertIsNotNone(info.sku_name)
        self.assertIsNotNone(info.account_kind)

    @record
    def test_get_account_information_with_container_name(self):
        pytest.skip("not yet supported")
        # Act
        # Container name gets ignored
        info = self.bs.get_blob_account_information("missing")

        # Assert
        self.assertIsNotNone(info.sku_name)
        self.assertIsNotNone(info.account_kind)

    @record
    def test_get_account_information_with_blob_name(self):
        pytest.skip("not yet supported")
        # Act
        # Both container and blob names get ignored
        blob = self.bsc.get_blob_client("missing", "missing")
        info = blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('SKU'))
        self.assertIsNotNone(info.get('AccountType'))

    @record
    def test_get_account_information_with_container_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        pytest.skip("not yet supported")
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
        pytest.skip("not yet supported")
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        url = blob.make_url(sas_token=token)

        bs_with_sas = BlobClient(url)

        # Act
        info = bs_with_sas.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('SKU'))
        self.assertIsNotNone(info.get('AccountType'))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
