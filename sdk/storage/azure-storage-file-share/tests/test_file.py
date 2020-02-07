# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import os
import unittest
from datetime import datetime, timedelta

import requests
import pytest
import uuid
from azure.core import MatchConditions

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ResourceExistsError
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.storage.fileshare import (
    generate_account_sas,
    generate_file_sas,
    ShareFileClient,
    ShareServiceClient,
    ContentSettings,
    FileSasPermissions,
    AccessPolicy,
    ResourceTypes,
    AccountSasPermissions,
    StorageErrorCode,
    NTFSAttributes,
    CopyFileSmbInfo)
from azure.storage.fileshare._parser import _datetime_to_str
from _shared.testcase import (
    StorageTestCase,
    LogCaptured,
    GlobalStorageAccountPreparer
)

# ------------------------------------------------------------------------------
TEST_SHARE_PREFIX = 'share'
TEST_DIRECTORY_PREFIX = 'dir'
TEST_FILE_PREFIX = 'file'
INPUT_FILE_PATH = 'file_input.temp.{}.dat'.format(str(uuid.uuid4()))
OUTPUT_FILE_PATH = 'file_output.temp.{}.dat'.format(str(uuid.uuid4()))
LARGE_FILE_SIZE = 64 * 1024 + 5


# ------------------------------------------------------------------------------

class StorageFileTest(StorageTestCase):
    def _setup(self, storage_account, storage_account_key, rmt_account=None, rmt_key=None):
        super(StorageFileTest, self).setUp()

        url = self.account_url(storage_account, "file")
        credential = storage_account_key

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.fsc = ShareServiceClient(url, credential=credential, max_range_size=4 * 1024)
        self.share_name = self.get_resource_name('utshare')
        if self.is_live:
            self.fsc.create_share(self.share_name)

        self.short_byte_data = self.get_random_bytes(1024)

        remote_url = self.account_url(rmt_account, "file")
        remote_credential = rmt_key
        
        if rmt_account:
            self.fsc2 = ShareServiceClient(remote_url, credential=remote_credential)
            self.remote_share_name = None

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass
    # --Helpers-----------------------------------------------------------------
    def _get_file_reference(self):
        return self.get_resource_name(TEST_FILE_PREFIX)

    def _create_file(self, file_name=None):
        file_name = self._get_file_reference() if file_name is None else file_name
        share_client = self.fsc.get_share_client(self.share_name)
        file_client = share_client.get_file_client(file_name)
        file_client.upload_file(self.short_byte_data)
        return file_client

    def _create_empty_file(self, file_name=None, file_size=2048):
        file_name = self._get_file_reference() if file_name is None else file_name
        share_client = self.fsc.get_share_client(self.share_name)
        file_client = share_client.get_file_client(file_name)
        file_client.create_file(file_size)
        return file_client

    def _get_file_client(self):
        file_name = self._get_file_reference()
        share_client = self.fsc.get_share_client(self.share_name)
        file_client = share_client.get_file_client(file_name)
        return file_client

    def _create_remote_share(self):
        self.remote_share_name = self.get_resource_name('remoteshare')
        remote_share = self.fsc2.get_share_client(self.remote_share_name)
        try:
            remote_share.create_share()
        except ResourceExistsError:
            pass
        return remote_share

    def _create_remote_file(self, file_data=None):
        if not file_data:
            file_data = b'12345678' * 1024 * 1024
        source_file_name = self._get_file_reference()
        remote_share = self.fsc2.get_share_client(self.remote_share_name)
        remote_file = remote_share.get_file_client(source_file_name)
        remote_file.upload_file(file_data)
        return remote_file

    def _wait_for_async_copy(self, share_name, file_path):
        count = 0
        share_client = self.fsc.get_share_client(share_name)
        file_client = share_client.get_file_client(file_path)
        properties = file_client.get_file_properties()
        while properties.copy.status != 'success':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            properties = file_client.get_file_properties()
        self.assertEqual(properties.copy.status, 'success')

    def assertFileEqual(self, file_client, expected_data):
        actual_data = file_client.download_file().readall()
        self.assertEqual(actual_data, expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    # --Test cases for files ----------------------------------------------
    @GlobalStorageAccountPreparer()
    def test_make_file_url(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)

        share = self.fsc.get_share_client("vhds")
        file_client = share.get_file_client("vhd_dir/my.vhd")

        # Act
        res = file_client.url

        # Assert
        self.assertEqual(res, 'https://' + storage_account.name
                         + '.file.core.windows.net/vhds/vhd_dir/my.vhd')

    @GlobalStorageAccountPreparer()
    def test_make_file_url_no_directory(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self.fsc.get_share_client("vhds")
        file_client = share.get_file_client("my.vhd")

        # Act
        res = file_client.url

        # Assert
        self.assertEqual(res, 'https://' + storage_account.name
                         + '.file.core.windows.net/vhds/my.vhd')

    @GlobalStorageAccountPreparer()
    def test_make_file_url_with_protocol(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        url = self.account_url(storage_account, "file").replace('https', 'http')
        fsc = ShareServiceClient(url, credential=storage_account_key)
        share = fsc.get_share_client("vhds")
        file_client = share.get_file_client("vhd_dir/my.vhd")

        # Act
        res = file_client.url

        # Assert
        self.assertEqual(res, 'http://' + storage_account.name
                         + '.file.core.windows.net/vhds/vhd_dir/my.vhd')

    @GlobalStorageAccountPreparer()
    def test_make_file_url_with_sas(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        sas = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name="vhds",
            file_path="vhd_dir/my.vhd",
            credential=sas
        )

        # Act
        res = file_client.url

        # Assert
        self.assertEqual(res, 'https://' + storage_account.name +
                         '.file.core.windows.net/vhds/vhd_dir/my.vhd{}'.format(sas))

    @GlobalStorageAccountPreparer()
    def test_create_file(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        resp = file_client.create_file(1024, file_attributes="hidden")

        # Assert
        props = file_client.get_file_properties()
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.lease)
        self.assertIsNotNone(props.lease.state)
        self.assertIsNotNone(props.lease.status)
        self.assertEqual(props.etag, resp['etag'])
        self.assertEqual(props.last_modified, resp['last_modified'])

    @GlobalStorageAccountPreparer()
    def test_create_file_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        resp = file_client.create_file(1024, metadata=metadata)

        # Assert
        props = file_client.get_file_properties()
        self.assertIsNotNone(props)
        self.assertEqual(props.etag, resp['etag'])
        self.assertEqual(props.last_modified, resp['last_modified'])
        self.assertDictEqual(props.metadata, metadata)

    @GlobalStorageAccountPreparer()
    def test_create_file_when_file_permission_is_too_long(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._get_file_client()
        permission = str(self.get_random_bytes(8 * 1024 + 1))
        with self.assertRaises(ValueError):
            file_client.create_file(1024, file_permission=permission)

    @GlobalStorageAccountPreparer()
    def test_create_file_with_invalid_file_permission(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_client()

        with self.assertRaises(HttpResponseError):
            file_name.create_file(1024, file_permission="abcde")

    @GlobalStorageAccountPreparer()
    def test_create_file_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._get_file_client()
        file_client.create_file(1024)

        lease = file_client.acquire_lease()
        resp = file_client.create_file(1024, lease=lease)
        self.assertIsNotNone(resp)

        # There is currently a lease on the file so there should be an exception when delete the file without lease
        with self.assertRaises(HttpResponseError):
            file_client.delete_file()

        # There is currently a lease on the file so delete the file with the lease will succeed
        file_client.delete_file(lease=lease)

    @GlobalStorageAccountPreparer()
    def test_create_file_with_changed_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._get_file_client()
        file_client.create_file(1024)

        lease = file_client.acquire_lease()
        old_lease_id = lease.id
        lease.change(str(uuid.uuid4()))

        # use the old lease id to create file will throw exception.
        with self.assertRaises(HttpResponseError):
            file_client.create_file(1024, lease=old_lease_id)

        # use the new lease to create file will succeed.
        resp = file_client.create_file(1024, lease=lease)

        self.assertIsNotNone(resp)

    @GlobalStorageAccountPreparer()
    def test_create_file_will_set_all_smb_properties(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._get_file_client()

        # Act
        file_client.create_file(1024)
        file_properties = file_client.get_file_properties()

        # Assert
        self.assertIsNotNone(file_properties)
        self.assertIsNotNone(file_properties.change_time)
        self.assertIsNotNone(file_properties.creation_time)
        self.assertIsNotNone(file_properties.file_attributes)
        self.assertIsNotNone(file_properties.last_write_time)

    @GlobalStorageAccountPreparer()
    def test_file_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        exists = file_client.get_file_properties()

        # Assert
        self.assertTrue(exists)

    @GlobalStorageAccountPreparer()
    def test_file_not_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path="missingdir/" + file_name,
            credential=storage_account_key)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            file_client.get_file_properties()

        # Assert

    @GlobalStorageAccountPreparer()
    def test_file_exists_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()
        file_client.delete_file()

        # Act
        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)
        props = snapshot_client.get_file_properties()

        # Assert
        self.assertTrue(props)

    @GlobalStorageAccountPreparer()
    def test_file_not_exists_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()

        file_client = self._create_file()

        # Act
        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            snapshot_client.get_file_properties()

    @GlobalStorageAccountPreparer()
    def test_resize_file(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        file_client.resize_file(5)

        # Assert
        props = file_client.get_file_properties()
        self.assertEqual(props.size, 5)

    @GlobalStorageAccountPreparer()
    def test_resize_file_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        lease = file_client.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            file_client.resize_file(5)
        file_client.resize_file(5, lease=lease)

        # Assert
        props = file_client.get_file_properties()
        self.assertEqual(props.size, 5)

    @GlobalStorageAccountPreparer()
    def test_set_file_properties(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        resp = file_client.set_http_headers(content_settings=content_settings)

        # Assert
        properties = file_client.get_file_properties()
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self.assertEqual(properties.content_settings.content_disposition, content_settings.content_disposition)
        self.assertIsNotNone(properties.last_write_time)
        self.assertIsNotNone(properties.creation_time)
        self.assertIsNotNone(properties.permission_key)

    @GlobalStorageAccountPreparer()
    def test_set_file_properties_with_file_permission(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        properties_on_creation = file_client.get_file_properties()

        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')

        ntfs_attributes = NTFSAttributes(archive=True, temporary=True)
        last_write_time = properties_on_creation.last_write_time + timedelta(hours=3)
        creation_time = properties_on_creation.creation_time + timedelta(hours=3)

        # Act
        file_client.set_http_headers(
            content_settings=content_settings,
            file_attributes=ntfs_attributes,
            file_last_write_time=last_write_time,
            file_creation_time=creation_time,
        )

        # Assert
        properties = file_client.get_file_properties()
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self.assertEqual(properties.content_settings.content_disposition, content_settings.content_disposition)
        self.assertEqual(properties.creation_time, creation_time)
        self.assertEqual(properties.last_write_time, last_write_time)
        self.assertIn("Archive", properties.file_attributes)
        self.assertIn("Temporary", properties.file_attributes)

    @GlobalStorageAccountPreparer()
    def test_get_file_properties(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        properties = file_client.get_file_properties()

        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.size, len(self.short_byte_data))

    @GlobalStorageAccountPreparer()
    def test_get_file_properties_with_invalid_lease_fails(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        file_client.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            file_client.get_file_properties(lease=str(uuid.uuid4()))

        # get properties on a leased file will succeed
        properties = file_client.get_file_properties()
        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.size, len(self.short_byte_data))

    @GlobalStorageAccountPreparer()
    def test_get_file_properties_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        metadata = {"test1": "foo", "test2": "bar"}
        file_client.set_file_metadata(metadata)

        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()

        metadata2 = {"test100": "foo100", "test200": "bar200"}
        file_client.set_file_metadata(metadata2)

        # Act
        file_props = file_client.get_file_properties()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)
        snapshot_props = snapshot_client.get_file_properties()

        # Assert
        self.assertIsNotNone(file_props)
        self.assertIsNotNone(snapshot_props)
        self.assertEqual(file_props.size, snapshot_props.size)
        self.assertDictEqual(metadata, snapshot_props.metadata)

    @GlobalStorageAccountPreparer()
    def test_get_file_metadata_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        metadata = {"test1": "foo", "test2": "bar"}
        file_client.set_file_metadata(metadata)

        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        metadata2 = {"test100": "foo100", "test200": "bar200"}
        file_client.set_file_metadata(metadata2)

        # Act
        file_metadata = file_client.get_file_properties().metadata
        file_snapshot_metadata = snapshot_client.get_file_properties().metadata

        # Assert
        self.assertDictEqual(metadata2, file_metadata)
        self.assertDictEqual(metadata, file_snapshot_metadata)

    @GlobalStorageAccountPreparer()
    def test_get_file_properties_with_non_existing_file(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            file_client.get_file_properties()

            # Assert

    @GlobalStorageAccountPreparer()
    def test_get_file_metadata(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        md = file_client.get_file_properties().metadata

        # Assert
        self.assertIsNotNone(md)
        self.assertEqual(0, len(md))

    @GlobalStorageAccountPreparer()
    def test_set_file_metadata_with_upper_case(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        file_client = self._create_file()

        # Act
        file_client.set_file_metadata(metadata)

        # Assert
        md = file_client.get_file_properties().metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @GlobalStorageAccountPreparer()
    def test_set_file_metadata_with_broken_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        file_client = self._create_file()

        lease = file_client.acquire_lease()
        with self.assertRaises(HttpResponseError):
            file_client.set_file_metadata(metadata)

        lease_id_to_be_broken = lease.id
        lease.break_lease()

        # lease is broken, set metadata doesn't require a lease
        file_client.set_file_metadata({'hello': 'world'})
        # Act
        md = file_client.get_file_properties().metadata
        # Assert
        self.assertEqual(1, len(md))
        self.assertEqual(md['hello'], 'world')

        # Act
        file_client.acquire_lease(lease_id=lease_id_to_be_broken)
        file_client.set_file_metadata(metadata, lease=lease_id_to_be_broken)

        # Assert
        md = file_client.get_file_properties().metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @GlobalStorageAccountPreparer()
    def test_delete_file_with_existing_file(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        file_client.delete_file()

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            file_client.get_file_properties()

    @GlobalStorageAccountPreparer()
    def test_delete_file_with_non_existing_file(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            file_client.delete_file()

            # Assert

    @GlobalStorageAccountPreparer()
    def test_update_range(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        data = b'abcdefghijklmnop' * 32
        file_client.upload_range(data, offset=0, length=512)

        # Assert
        content = file_client.download_file().readall()
        self.assertEqual(len(data), 512)
        self.assertEqual(data, content[:512])
        self.assertEqual(self.short_byte_data[512:], content[512:])

    @GlobalStorageAccountPreparer()
    def test_update_range_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        lease = file_client.acquire_lease()

        # Act
        data = b'abcdefghijklmnop' * 32
        with self.assertRaises(HttpResponseError):
            file_client.upload_range(data, offset=0, length=512)

        file_client.upload_range(data, offset=0, length=512, lease=lease)

        # Assert
        content = file_client.download_file().readall()
        self.assertEqual(len(data), 512)
        self.assertEqual(data, content[:512])
        self.assertEqual(self.short_byte_data[512:], content[512:])

    @GlobalStorageAccountPreparer()
    def test_update_range_with_md5(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        data = b'abcdefghijklmnop' * 32
        file_client.upload_range(data, offset=0, length=512, validate_content=True)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_update_range_from_file_url_when_source_file_does_not_have_enough_bytes(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_file_name = 'testfile1'
        source_file_client = self._create_file(source_file_name)

        destination_file_name = 'filetoupdate'
        destination_file_client = self._create_file(destination_file_name)

        # generate SAS for the source file
        sas_token_for_source_file = generate_file_sas(
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
        )

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file

        # Act
        with self.assertRaises(HttpResponseError):
            # when the source file has less bytes than 2050, throw exception
            destination_file_client.upload_range_from_url(source_file_url, offset=0, length=2050, source_offset=0)

    @GlobalStorageAccountPreparer()
    def test_update_range_from_file_url(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_file_name = 'testfile'
        source_file_client = self._create_file(file_name=source_file_name)
        data = b'abcdefghijklmnop' * 32
        resp = source_file_client.upload_range(data, offset=0, length=512)

        destination_file_name = 'filetoupdate'
        destination_file_client = self._create_empty_file(file_name=destination_file_name)

        # generate SAS for the source file
        sas_token_for_source_file = generate_file_sas(
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file
        # Act
        destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0,
                                                      source_etag=resp['etag'],
                                                      source_match_condition=MatchConditions.IfNotModified)

        # Assert
        # To make sure the range of the file is actually updated
        file_ranges = destination_file_client.get_ranges()
        file_content = destination_file_client.download_file(offset=0, length=512).readall()
        self.assertEqual(1, len(file_ranges))
        self.assertEqual(0, file_ranges[0].get('start'))
        self.assertEqual(511, file_ranges[0].get('end'))
        self.assertEqual(data, file_content)

    @GlobalStorageAccountPreparer()
    def test_update_range_from_file_url_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_file_name = 'testfile'
        source_file_client = self._create_file(file_name=source_file_name)
        data = b'abcdefghijklmnop' * 32
        resp = source_file_client.upload_range(data, offset=0, length=512)

        destination_file_name = 'filetoupdate'
        destination_file_client = self._create_empty_file(file_name=destination_file_name)
        lease = destination_file_client.acquire_lease()

        # generate SAS for the source file
        sas_token_for_source_file = generate_file_sas(
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file
        # Act
        with self.assertRaises(HttpResponseError):
            destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0,
                                                          source_etag=resp['etag'],
                                                          source_match_condition=MatchConditions.IfNotModified)

        destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0,
                                                      source_etag=resp['etag'],
                                                      source_match_condition=MatchConditions.IfNotModified,
                                                      lease=lease)

        # Assert
        # To make sure the range of the file is actually updated
        file_ranges = destination_file_client.get_ranges()
        file_content = destination_file_client.download_file(offset=0, length=512).readall()
        self.assertEqual(1, len(file_ranges))
        self.assertEqual(0, file_ranges[0].get('start'))
        self.assertEqual(511, file_ranges[0].get('end'))
        self.assertEqual(data, file_content)

    @GlobalStorageAccountPreparer()
    def test_update_big_range_from_file_url(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_file_name = 'testfile1'
        end = 1048575

        source_file_client = self._create_empty_file(file_name=source_file_name, file_size=1024 * 1024)
        data = b'abcdefghijklmnop' * 65536
        source_file_client.upload_range(data, offset=0, length=end+1)

        destination_file_name = 'filetoupdate1'
        destination_file_client = self._create_empty_file(file_name=destination_file_name, file_size=1024 * 1024)

        # generate SAS for the source file
        sas_token_for_source_file = generate_file_sas(
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file

        # Act
        destination_file_client.upload_range_from_url(source_file_url, offset=0, length=end+1, source_offset=0)

        # Assert
        # To make sure the range of the file is actually updated
        file_ranges = destination_file_client.get_ranges()
        file_content = destination_file_client.download_file(offset=0, length=end + 1).readall()
        self.assertEqual(1, len(file_ranges))
        self.assertEqual(0, file_ranges[0].get('start'))
        self.assertEqual(end, file_ranges[0].get('end'))
        self.assertEqual(data, file_content)

    @GlobalStorageAccountPreparer()
    def test_clear_range(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        resp = file_client.clear_range(offset=0, length=512)

        # Assert
        content = file_client.download_file().readall()
        self.assertEqual(b'\x00' * 512, content[:512])
        self.assertEqual(self.short_byte_data[512:], content[512:])

    @GlobalStorageAccountPreparer()
    def test_update_file_unicode(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()

        # Act
        data = u'abcdefghijklmnop' * 32
        file_client.upload_range(data, offset=0, length=512)

        encoded = data.encode('utf-8')

        # Assert
        content = file_client.download_file().readall()
        self.assertEqual(encoded, content[:512])
        self.assertEqual(self.short_byte_data[512:], content[512:])

        # Assert

    @GlobalStorageAccountPreparer()
    def test_list_ranges_none(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.create_file(1024)

        # Act
        ranges = file_client.get_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertEqual(len(ranges), 0)

    @GlobalStorageAccountPreparer()
    def test_list_ranges_none_with_invalid_lease_fails(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.create_file(1024)

        file_client.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            file_client.get_ranges(lease=str(uuid.uuid4()))

        # Get ranges on a leased file will succeed without provide the lease
        ranges = file_client.get_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertEqual(len(ranges), 0)

    @GlobalStorageAccountPreparer()
    def test_list_ranges_2(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.create_file(2048)

        data = b'abcdefghijklmnop' * 32
        resp1 = file_client.upload_range(data, offset=0, length=512)
        resp2 = file_client.upload_range(data, offset=1024, length=512)

        # Act
        ranges = file_client.get_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0]['start'], 0)
        self.assertEqual(ranges[0]['end'], 511)
        self.assertEqual(ranges[1]['start'], 1024)
        self.assertEqual(ranges[1]['end'], 1535)

    @GlobalStorageAccountPreparer()
    def test_list_ranges_none_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.create_file(1024)
        
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        file_client.delete_file()

        # Act
        ranges = snapshot_client.get_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertEqual(len(ranges), 0)

    @GlobalStorageAccountPreparer()
    def test_list_ranges_2_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.create_file(2048)
        data = b'abcdefghijklmnop' * 32
        resp1 = file_client.upload_range(data, offset=0, length=512)
        resp2 = file_client.upload_range(data, offset=1024, length=512)
        
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        file_client.delete_file()

        # Act
        ranges = snapshot_client.get_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0]['start'], 0)
        self.assertEqual(ranges[0]['end'], 511)
        self.assertEqual(ranges[1]['start'], 1024)
        self.assertEqual(ranges[1]['end'], 1535)

    @GlobalStorageAccountPreparer()
    def test_copy_file_with_existing_file(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_client = self._create_file()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)

        # Act
        copy = file_client.start_copy_from_url(source_client.url)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertIsNotNone(copy['copy_id'])

        copy_file = file_client.download_file().readall()
        self.assertEqual(copy_file, self.short_byte_data)

    @GlobalStorageAccountPreparer()
    def test_copy_existing_file_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_client = self._create_file()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)
        file_client.create_file(1024)
        lease = file_client.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            file_client.start_copy_from_url(source_client.url)

        copy = file_client.start_copy_from_url(source_client.url, lease=lease)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertIsNotNone(copy['copy_id'])

        copy_file = file_client.download_file().readall()
        self.assertEqual(copy_file, self.short_byte_data)

    @GlobalStorageAccountPreparer()
    def test_copy_file_with_specifying_acl_copy_behavior_attributes(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_client = self._create_file()
        user_given_permission = "O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-" \
                                "1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;" \
                                "S-1-5-21-397955417-626881126-188441444-3053964)"
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)

        file_creation_time = "2017-05-10T17:52:33.9551860Z"
        file_attributes = "Temporary|NoScrubData"
        smb_info = CopyFileSmbInfo(ignore_read_only=True,
                                   file_attributes=file_attributes,
                                   file_creation_time=file_creation_time)
        # Act
        copy = file_client.start_copy_from_url(source_client.url,
                                               file_permission=user_given_permission,
                                               file_permission_copy_mode="override",
                                               copy_file_smb_info=smb_info)

        # Assert
        dest_prop = file_client.get_file_properties()
        # to make sure the attributes are the same as the set ones
        self.assertEqual(_datetime_to_str(dest_prop['creation_time']),
                         file_creation_time)
        self.assertIn('Temporary', dest_prop['file_attributes'])
        self.assertIn('NoScrubData', dest_prop['file_attributes'])

        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertIsNotNone(copy['copy_id'])

        copy_file = file_client.download_file().readall()
        self.assertEqual(copy_file, self.short_byte_data)

    @GlobalStorageAccountPreparer()
    def test_copy_file_with_specifying_acl_and_attributes_from_source(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_client = self._create_file()
        source_prop = source_client.get_file_properties()

        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)

        # Act
        copy = file_client.start_copy_from_url(source_client.url,
                                               file_permission_copy_mode="source")

        # Assert
        dest_prop = file_client.get_file_properties()
        # to make sure the acl is copied from source
        self.assertEqual(source_prop['permission_key'], dest_prop['permission_key'])

        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertIsNotNone(copy['copy_id'])

        copy_file = file_client.download_file().readall()
        self.assertEqual(copy_file, self.short_byte_data)

    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_copy_file_async_private_file(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key, rmt, rmt_key)
        self._create_remote_share()
        source_file = self._create_remote_file()

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        with self.assertRaises(HttpResponseError) as e:
            file_client.start_copy_from_url(source_file.url)

        # Assert
        self.assertEqual(e.exception.error_code, StorageErrorCode.cannot_verify_copy_source)

    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_copy_file_async_private_file_with_sas(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key, rmt, rmt_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_share()
        source_file = self._create_remote_file(file_data=data)
        sas_token = generate_file_sas(
            source_file.account_name,
            source_file.share_name,
            source_file.file_path,
            source_file.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        source_url = source_file.url + '?' + sas_token

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        copy_resp = file_client.start_copy_from_url(source_url)

        # Assert
        self.assertTrue(copy_resp['copy_status'] in ['success', 'pending'])
        self._wait_for_async_copy(self.share_name, target_file_name)

        actual_data = file_client.download_file().readall()
        self.assertEqual(actual_data, data)

    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_abort_copy_file(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key, rmt, rmt_key)
        data = b'12345678' * 1024 * 1024
        self._create_remote_share()
        source_file = self._create_remote_file(file_data=data)
        sas_token = generate_file_sas(
            source_file.account_name,
            source_file.share_name,
            source_file.file_path,
            source_file.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        source_url = source_file.url + '?' + sas_token

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        copy_resp = file_client.start_copy_from_url(source_url)
        self.assertEqual(copy_resp['copy_status'], 'pending')
        file_client.abort_copy(copy_resp)

        # Assert
        target_file = file_client.download_file()
        self.assertEqual(target_file.readall(), b'')
        self.assertEqual(target_file.properties.copy.status, 'aborted')

    @GlobalStorageAccountPreparer()
    def test_abort_copy_file_with_synchronous_copy_fails(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_file = self._create_file()

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        copy_resp = file_client.start_copy_from_url(source_file.url)

        with self.assertRaises(HttpResponseError):
            file_client.abort_copy(copy_resp)

        # Assert
        self.assertEqual(copy_resp['copy_status'], 'success')

    @GlobalStorageAccountPreparer()
    def test_unicode_get_file_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = '啊齄丂狛狜'
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.upload_file(b'hello world')

        # Act
        content = file_client.download_file().readall()

        # Assert
        self.assertEqual(content, b'hello world')

    @GlobalStorageAccountPreparer()
    def test_unicode_get_file_unicode_name_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = '啊齄丂狛狜'
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.create_file(1024)
        lease = file_client.acquire_lease()
        with self.assertRaises(HttpResponseError):
            file_client.upload_file(b'hello world')

        file_client.upload_file(b'hello world', lease=lease)

        # Act
        # download the file with a wrong lease id will fail
        with self.assertRaises(HttpResponseError):
            file_client.upload_file(b'hello world', lease=str(uuid.uuid4()))

        content = file_client.download_file(lease=lease).readall()

        # Assert
        self.assertEqual(content, b'hello world')

    @GlobalStorageAccountPreparer()
    def test_file_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        file_client.upload_file(data)

        # Assert
        content = file_client.download_file().readall()
        self.assertEqual(content, data)

    @GlobalStorageAccountPreparer()
    def test_file_unicode_data_and_file_attributes(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = self._get_file_client()

        # Act
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        file_client.upload_file(data, file_attributes=NTFSAttributes(temporary=True))

        # Assert
        content = file_client.download_file().readall()
        properties = file_client.get_file_properties()
        self.assertEqual(content, data)
        self.assertIn('Temporary', properties.file_attributes)

    @GlobalStorageAccountPreparer()
    def test_unicode_get_file_binary_data(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        file_client.upload_file(binary_data)

        # Act
        content = file_client.download_file().readall()

        # Assert
        self.assertEqual(content, binary_data)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_bytes_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        response = file_client.upload_file(data, max_concurrency=2, raw_response_hook=callback)
        assert isinstance(response, dict)
        assert 'last_modified' in response
        assert 'etag' in response

        # Assert
        self.assertFileEqual(file_client, data)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_bytes_with_index(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        index = 1024
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        response = file_client.upload_file(data[index:], max_concurrency=2)
        assert isinstance(response, dict)
        assert 'last_modified' in response
        assert 'etag' in response

        # Assert
        self.assertFileEqual(file_client, data[1024:])

    @GlobalStorageAccountPreparer()
    def test_create_file_from_bytes_with_index_and_count(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        index = 512
        count = 1024
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        response = file_client.upload_file(data[index:], length=count, max_concurrency=2)
        assert isinstance(response, dict)
        assert 'last_modified' in response
        assert 'etag' in response

        # Assert
        self.assertFileEqual(file_client, data[index:index + count])

    @GlobalStorageAccountPreparer()
    def test_create_file_from_path(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)        
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        with open(INPUT_FILE_PATH, 'wb') as stream:
            stream.write(data)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        with open(INPUT_FILE_PATH, 'rb') as stream:
            response = file_client.upload_file(stream, max_concurrency=2)
            assert isinstance(response, dict)
            assert 'last_modified' in response
            assert 'etag' in response

        # Assert
        self.assertFileEqual(file_client, data)
        self._teardown(INPUT_FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_path_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)        
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        with open(INPUT_FILE_PATH, 'wb') as stream:
            stream.write(data)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with open(INPUT_FILE_PATH, 'rb') as stream:
            response = file_client.upload_file(stream, max_concurrency=2, raw_response_hook=callback)
            assert isinstance(response, dict)
            assert 'last_modified' in response
            assert 'etag' in response

        # Assert
        self.assertFileEqual(file_client, data)
        self.assert_upload_progress(
            len(data),
            self.fsc._config.max_range_size,
            progress, unknown_size=False)
        self._teardown(INPUT_FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_stream(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)       
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        with open(INPUT_FILE_PATH, 'wb') as stream:
            stream.write(data)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_size = len(data)
        with open(INPUT_FILE_PATH, 'rb') as stream:
            response = file_client.upload_file(stream, max_concurrency=2)
            assert isinstance(response, dict)
            assert 'last_modified' in response
            assert 'etag' in response

        # Assert
        self.assertFileEqual(file_client, data[:file_size])
        self._teardown(INPUT_FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_stream_non_seekable(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)      
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        with open(INPUT_FILE_PATH, 'wb') as stream:
            stream.write(data)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_size = len(data)
        with open(INPUT_FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageFileTest.NonSeekableFile(stream)
            file_client.upload_file(non_seekable_file, length=file_size, max_concurrency=1)

        # Assert
        self.assertFileEqual(file_client, data[:file_size])
        self._teardown(INPUT_FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_stream_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)      
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        with open(INPUT_FILE_PATH, 'wb') as stream:
            stream.write(data)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        file_size = len(data)
        with open(INPUT_FILE_PATH, 'rb') as stream:
            file_client.upload_file(stream, max_concurrency=2, raw_response_hook=callback)

        # Assert
        self.assertFileEqual(file_client, data[:file_size])
        self.assert_upload_progress(
            len(data),
            self.fsc._config.max_range_size,
            progress, unknown_size=False)
        self._teardown(INPUT_FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_stream_truncated(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)       
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        with open(INPUT_FILE_PATH, 'wb') as stream:
            stream.write(data)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_size = len(data) - 512
        with open(INPUT_FILE_PATH, 'rb') as stream:
            file_client.upload_file(stream, length=file_size, max_concurrency=2)

        # Assert
        self.assertFileEqual(file_client, data[:file_size])
        self._teardown(INPUT_FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_stream_with_progress_truncated(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)       
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        with open(INPUT_FILE_PATH, 'wb') as stream:
            stream.write(data)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        file_size = len(data) - 5
        with open(INPUT_FILE_PATH, 'rb') as stream:
            file_client.upload_file(stream, length=file_size, max_concurrency=2, raw_response_hook=callback)


        # Assert
        self.assertFileEqual(file_client, data[:file_size])
        self.assert_upload_progress(
            file_size,
            self.fsc._config.max_range_size,
            progress, unknown_size=False)
        self._teardown(INPUT_FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_text(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_client.upload_file(text)

        # Assert
        self.assertFileEqual(file_client, data)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_text_with_encoding(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_client.upload_file(text, encoding='UTF-16')

        # Assert
        self.assertFileEqual(file_client, data)

    @GlobalStorageAccountPreparer()
    def test_create_file_from_text_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        data = self.get_random_text_data(LARGE_FILE_SIZE)
        encoded_data = data.encode('utf-8')
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_client.upload_file(data)

        # Assert
        self.assertFileEqual(file_client, encoded_data)

    @GlobalStorageAccountPreparer()
    def test_create_file_with_md5_small(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        data = self.get_random_bytes(512)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_client.upload_file(data, validate_content=True)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_create_file_with_md5_large(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_client.upload_file(data, validate_content=True, max_concurrency=2)

        # Assert

    # --Test cases for sas & acl ------------------------------------------------
    @GlobalStorageAccountPreparer()
    def test_sas_access_file(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        token = generate_file_sas(
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)
        content = file_client.download_file().readall()

        # Assert
        self.assertEqual(self.short_byte_data, content)

    @GlobalStorageAccountPreparer()
    def test_sas_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        share_client = self.fsc.get_share_client(self.share_name)

        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = FileSasPermissions(read=True)
        identifiers = {'testid': access_policy}
        share_client.set_share_access_policy(identifiers)

        token = generate_file_sas(
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            policy_id='testid')

        # Act
        sas_file = ShareFileClient.from_file_url(
            file_client.url,
            credential=token)

        content = file_client.download_file().readall()

        # Assert
        self.assertEqual(self.short_byte_data, content)

    @GlobalStorageAccountPreparer()
    def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        token = generate_account_sas(
            self.fsc.account_name,
            self.fsc.credential.account_key,
            ResourceTypes(object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)

        response = requests.get(file_client.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(self.short_byte_data, response.content)

    @GlobalStorageAccountPreparer()
    def test_shared_read_access_file(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        token = generate_file_sas(
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)
        response = requests.get(file_client.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(self.short_byte_data, response.content)

    @GlobalStorageAccountPreparer()
    def test_shared_read_access_file_with_content_query_params(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = self._create_file()
        token = generate_file_sas(
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)
        response = requests.get(file_client.url)

        # Assert
        self.assertEqual(self.short_byte_data, response.content)
        self.assertEqual(response.headers['cache-control'], 'no-cache')
        self.assertEqual(response.headers['content-disposition'], 'inline')
        self.assertEqual(response.headers['content-encoding'], 'utf-8')
        self.assertEqual(response.headers['content-language'], 'fr')
        self.assertEqual(response.headers['content-type'], 'text')

    @GlobalStorageAccountPreparer()
    def test_shared_write_access_file(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        updated_data = b'updated file data'
        file_client_admin = self._create_file()
        token = generate_file_sas(
            file_client_admin.account_name,
            file_client_admin.share_name,
            file_client_admin.file_path,
            file_client_admin.credential.account_key,
            permission=FileSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client_admin.file_name,
            credential=token)

        # Act
        headers = {'x-ms-range': 'bytes=0-16', 'x-ms-write': 'update'}
        response = requests.put(file_client.url + '&comp=range', headers=headers, data=updated_data)

        # Assert
        self.assertTrue(response.ok)
        file_content = file_client_admin.download_file().readall()
        self.assertEqual(updated_data, file_content[:len(updated_data)])

    @GlobalStorageAccountPreparer()
    def test_shared_delete_access_file(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client_admin = self._create_file()
        token = generate_file_sas(
            file_client_admin.account_name,
            file_client_admin.share_name,
            file_client_admin.file_path,
            file_client_admin.credential.account_key,
            permission=FileSasPermissions(delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=file_client_admin.file_name,
            credential=token)

        # Act
        response = requests.delete(file_client.url)

        # Assert
        self.assertTrue(response.ok)
        with self.assertRaises(ResourceNotFoundError):
            file_client_admin.download_file()


# ------------------------------------------------------------------------------
