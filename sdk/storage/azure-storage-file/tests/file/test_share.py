# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta
import requests
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError)

from azure.storage.file.models import AccessPolicy, SharePermissions
from azure.storage.file.file_service_client import FileServiceClient
from azure.storage.file.directory_client import DirectoryClient
from azure.storage.file.file_client import FileClient
from azure.storage.file.share_client import ShareClient
from azure.storage.file._generated.models import DeleteSnapshotsOptionType, ListSharesIncludeType
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
    LogCaptured,
)

# ------------------------------------------------------------------------------
TEST_SHARE_PREFIX = 'share'


# ------------------------------------------------------------------------------

class StorageShareTest(StorageTestCase):
    def setUp(self):
        super(StorageShareTest, self).setUp()

        file_url = self.get_file_url()
        credentials = self.get_shared_key_credential()
        self.fsc = FileServiceClient(account_url=file_url, credential=credentials)
        self.test_shares = []

    def tearDown(self):
        if not self.is_playback():
            for share_name in self.test_shares:
                try:
                    self.fsc.delete_share(share_name, delete_snapshots=True)
                except:
                    pass
        return super(StorageShareTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_share_reference(self, prefix=TEST_SHARE_PREFIX):
        share_name = self.get_resource_name(prefix)
        share = self.fsc.get_share_client(share_name)
        self.test_shares.append(share)
        return share

    def _create_share(self, prefix=TEST_SHARE_PREFIX):
        share_client = self._get_share_reference(prefix)
        share = share_client.create_share()
        return share_client

    # --Test cases for shares -----------------------------------------
    @record
    def test_create_share(self):
        # Arrange
        share_name = self._get_share_reference()

        # Act
        created = share_name.create_share()

        # Assert
        self.assertTrue(created)

    @record
    def test_create_share_snapshot(self):
        # Arrange
        share_name = self._get_share_reference()

        # Act
        created = share_name.create_share()
        snapshot = share_name.create_snapshot()
        print(snapshot)
        # Assert
        self.assertTrue(created)
        self.assertIsNotNone(snapshot['snapshot'])
        self.assertIsNotNone(snapshot['etag'])
        self.assertIsNotNone(snapshot['last_modified'])

    @record
    def test_create_snapshot_with_metadata(self):
        # Arrange
        share_name = self._get_share_reference()
        metadata = {"test1": "foo", "test2": "bar"}
        metadata2 = {"test100": "foo100", "test200": "bar200"}

        # Act
        created = share_name.create_share(metadata=metadata)
        snapshot = share_name.create_snapshot(metadata=metadata2)
        # Assert
        self.assertTrue(created)
        self.assertIsNotNone(snapshot['snapshot'])
        self.assertIsNotNone(snapshot['etag'])
        self.assertIsNotNone(snapshot['last_modified'])

    @record
    def test_delete_share_with_snapshots(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()
        snapshot = share_name.create_snapshot()

        # Act
        with self.assertRaises(HttpResponseError):
            share_name.delete_share()

        deleted = share_name.delete_share(delete_snapshots=DeleteSnapshotsOptionType.include)
        self.assertIsNone(deleted)

    @record
    def test_delete_snapshot(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()
        snapshot = share_name.create_snapshot()

        # Act
        with self.assertRaises(HttpResponseError):
            share_name.delete_share()

        deleted = share_name.delete_share(delete_snapshots=True)
        self.assertIsNone(deleted)

    @record
    def test_create_share_fail_on_exist(self):
        # Arrange
        share_name = self._get_share_reference()

        # Act
        created = share_name.create_share()

        # Assert
        self.assertTrue(created)

    @record
    def test_create_share_with_already_existing_share(self):
        # Arrange
        share_name = self._get_share_reference()

        # Act
        created1 = share_name.create_share()
        created2 = None
        with self.assertRaises(HttpResponseError):
            created2 = share_name.create_share()

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_create_share_with_already_existing_share_fail_on_exist(self):
        # Arrange
        share_name = self._get_share_reference()

        # Act
        created = share_name.create_share()
        with self.assertRaises(HttpResponseError):
            share_name.create_share()

        # Assert
        self.assertTrue(created)

    @record
    def test_create_share_with_metadata(self):
        # Arrange
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self.fsc.get_share_client(share_name)
        created = client.create_share(metadata)

        # Assert
        self.assertTrue(created)
        md = client.get_share_properties().metadata
        self.assertDictEqual(md, metadata)

    @record
    def test_create_share_with_quota(self):
        # Arrange
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)

        # Act
        client = self.fsc.get_share_client(share_name)
        created = client.create_share(quota=1)

        # Assert
        print(client.get_share_properties())
        self.assertTrue(created)
        self.assertEqual(client.get_share_properties().quota, 1)

    @record
    def test_unicode_create_share_unicode_name(self):
        # Arrange
        share_name = u'啊齄丂狛狜'

        # Act
        with self.assertRaises(HttpResponseError):
            # not supported - share name must be alphanumeric, lowercase
            client = self.fsc.get_share_client(share_name)
            client.create_share()

            # Assert

    @record
    def test_list_shares_no_options(self):
        # Arrange

        # Act
        shares = self.fsc.list_shares()
        # Assert
        self.assertIsNotNone(shares)

    @record
    def test_list_shares_with_snapshot(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()
        share_name.create_snapshot()
        share_name.create_snapshot()

        # Act
        shares = self.fsc.list_shares(include_snapshots=True)

        # Assert
        self.assertIsNotNone(shares)

    @record
    def test_list_shares_with_prefix(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()

        # Act
        shares = self.fsc.list_shares(prefix=TEST_SHARE_PREFIX)

        # Assert
        self.assertIsNotNone(shares)

    @record
    def test_list_shares_with_include_metadata(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        share_name = self._get_share_reference()
        share_name.create_share(metadata)

        # Act

        shares = list(self.fsc.list_shares(include_metadata=True))

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, share_name)
        self.assertDictEqual(shares[0].metadata, metadata)

    @record
    def test_list_shares_with_num_results_and_marker(self):
        # Arrange
        prefix = 'listshare'
        share_names = []
        for i in range(0, 4):
            share_names.append(self._create_share(prefix + str(i)))

        share_names.sort()

        # Act
        generator1 = self.fsc.list_shares(prefix, num_results=2)
        generator2 = self.fsc.list_shares(prefix,
                                         marker=generator1.next_marker,
                                         num_results=2)

        shares1 = generator1.items
        shares2 = generator2.items

        # Assert
        self.assertIsNotNone(shares1)
        self.assertEqual(len(shares1), 2)
        self.assertNamedItemInContainer(shares1, share_names[0])
        self.assertNamedItemInContainer(shares1, share_names[1])
        self.assertIsNotNone(shares2)
        self.assertEqual(len(shares2), 2)
        self.assertNamedItemInContainer(shares2, share_names[2])
        self.assertNamedItemInContainer(shares2, share_names[3])

    @record
    def test_set_share_metadata(self):
        # Arrange
        share_name = self._create_share()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        share_name.set_share_metadata(metadata)

        # Assert
        md = share_name.get_share_properties().metadata
        self.assertDictEqual(md, metadata)

    @record
    def test_get_share_metadata(self):
        # Arrange
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self.fsc.get_share_client(share_name)
        created = client.create_share(metadata)

        # Assert
        self.assertTrue(created)
        md = client.get_share_properties().metadata
        self.assertDictEqual(md, metadata)

    @record
    def test_get_share_metadata_with_snapshot(self):
        # Arrange
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self.fsc.get_share_client(share_name)
        created = client.create_share(metadata)
        snapshot = client.create_snapshot()

        # Assert
        self.assertTrue(created)
        md = client.get_share_properties().metadata
        self.assertDictEqual(md, metadata)

    @record
    def test_delete_share_with_existing_share(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()
        # Act
        deleted = share_name.delete_share()

        # Assert
        self.assertIsNone(deleted)

    @record
    def test_delete_share_with_existing_share_fail_not_exist(self):
        # Arrange
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)
        client = self.fsc.get_share_client(share_name)

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                client.delete_share()

            log_as_str = log_captured.getvalue()

    @record
    def test_delete_share_with_non_existing_share(self):
        # Arrange
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)
        client = self.fsc.get_share_client(share_name)

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                deleted = client.delete_share()

            log_as_str = log_captured.getvalue()
            self.assertTrue('ERROR' not in log_as_str)

    @record
    def test_delete_share_with_non_existing_share_fail_not_exist(self):
        # Arrange
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)
        client = self.fsc.get_share_client(share_name)

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                client.delete_share()

            log_as_str = log_captured.getvalue()

    @record
    def test_get_share_stats(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()

        # Act
        share_usage = share_name.get_share_stats()

        # Assert
        self.assertIn('etag', share_usage)
        self.assertIn('last_modified', share_usage)

    @record
    def test_set_share_acl(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()

        # Act
        resp = share_name.set_share_acl()

        # Assert
        acl = share_name.get_share_acl()
        self.assertIsNotNone(acl)

    @record
    def test_set_share_acl_with_empty_signed_identifiers(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()

        # Act
        resp = share_name.set_share_acl(dict())

        # Assert
        acl = share_name.get_share_acl()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 0)

    @record
    def test_set_share_acl_with_signed_identifiers(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()

        # Act
        identifiers = dict()
        identifiers['testid'] = AccessPolicy(
            permission=SharePermissions.WRITE,
            expiry=datetime.utcnow() + timedelta(hours=1),
            start=datetime.utcnow() - timedelta(minutes=1),
        )

        resp = share_name.set_share_acl(identifiers)

        # Assert
        acl = share_name.get_share_acl()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 1)
        self.assertTrue('testid' in acl)

    @record
    def test_set_share_acl_too_many_ids(self):
        # Arrange
        share_name = self._get_share_reference()
        share_name.create_share()

        # Act
        identifiers = dict()
        for i in range(0, 6):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaisesRegexp(ValueError,
                                     'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'):
            share_name.set_share_acl(identifiers)

    @record
    def test_list_directories_and_files(self):
        # Arrange
        share_name = self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        dir1.create_directory()
        dir2 = share_name.get_directory_client('dir2')
        dir2.create_directory()

        # Act
        resp = list(share_name.list_directories_and_files('dir1'))
        print(resp)
        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')
        self.assertNamedItemInContainer(resp, 'file1')

    @record
    def test_list_directories_and_files_with_snapshot(self):
        # Arrange
        share_name = self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        dir1.create_directory()
        dir2 = share_name.get_directory_client('dir2')
        dir2.create_directory()
        snapshot1 = share_name.create_snapshot()
        dir2 = share_name.get_directory_client('dir3')
        dir2.create_directory()

        # Act
        resp = list(share_name.list_directories_and_files('dir1', snapshot=snapshot1['snapshot']))

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')

    @record
    def test_list_directories_and_files_with_num_results(self):
        # Arrange
        share_name = self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        dir1.create_directory()
        dir1.create_file(share_name, None, 'filea1', 1024)
        dir1.create_file(share_name, None, 'filea2', 1024)
        dir1.create_file(share_name, None, 'filea3', 1024)
        dir1.create_file(share_name, None, 'fileb1', 1024)

        # Act
        result = list(share_name.list_directories_and_files(num_results=2))

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertNamedItemInContainer(result, 'dir1')
        self.assertNamedItemInContainer(result, 'filea1')

    @record
    def test_list_directories_and_files_with_num_results_and_marker(self):
        # Arrange
        share_name = self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        dir1.create_directory()
        self.fs.create_file(share_name, 'dir1', 'filea1', 1024)
        self.fs.create_file(share_name, 'dir1', 'filea2', 1024)
        self.fs.create_file(share_name, 'dir1', 'filea3', 1024)
        self.fs.create_file(share_name, 'dir1', 'fileb1', 1024)

        # Act
        generator1 = self.fs.list_directories_and_files(share_name, 'dir1', num_results=2)
        generator2 = self.fs.list_directories_and_files(share_name, 'dir1',
                                                        marker=generator1.next_marker,
                                                        num_results=2)

        result1 = generator1.items
        result2 = generator2.items

        # Assert
        self.assertEqual(len(result1), 2)
        self.assertEqual(len(result2), 2)
        self.assertNamedItemInContainer(result1, 'filea1')
        self.assertNamedItemInContainer(result1, 'filea2')
        self.assertNamedItemInContainer(result2, 'filea3')
        self.assertNamedItemInContainer(result2, 'fileb1')
        self.assertEqual(result2.next_marker, None)

    @record
    def test_list_directories_and_files_with_prefix(self):
        # Arrange
        share_name = self._create_share()
        self.fs.create_directory(share_name, 'dir1')
        self.fs.create_directory(share_name, 'dir2')
        self.fs.create_file(share_name, None, 'file1', 1024)
        self.fs.create_directory(share_name, 'dir1/pref_dir3')
        self.fs.create_file(share_name, 'dir1', 'pref_file2', 1025)
        self.fs.create_file(share_name, 'dir1', 'file3', 1025)

        # Act
        resp = list(self.fs.list_directories_and_files(share_name, 'dir1', prefix='pref'))

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'pref_file2')
        self.assertNamedItemInContainer(resp, 'pref_dir3')

    @record
    def test_shared_access_share(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        file_name = 'file1'
        dir_name = 'dir1'
        data = b'hello world'

        share_name = self._create_share()
        dir1 = share_name.create_directory(dir_name)
        dir1.create_file(file_name, data)

        token = share_name.generate_share_shared_access_signature(
            expiry=datetime.utcnow() + timedelta(hours=1),
            permission=SharePermissions.READ,
        )
        url = share_name.make_file_url(
            dir_name,
            file_name,
            sas_token=token,
        )

        # Act
        response = requests.get(url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
