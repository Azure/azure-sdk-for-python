# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, \
    ResourceModifiedError, ServiceRequestError, AzureError
from azure.storage.filedatalake import ContentSettings, DirectorySasPermissions, DataLakeDirectoryClient, \
    generate_file_system_sas, FileSystemSasPermissions
from azure.storage.filedatalake import DataLakeServiceClient, generate_directory_sas
from azure.storage.filedatalake._models import AccessControlChangeResult, AccessControlChangeCounters
from azure.storage.filedatalake._serialize import _SUPPORTED_API_VERSIONS

from settings.testcase import DataLakePreparer
from devtools_testutils.storage import StorageTestCase

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
REMOVE_ACL = "mask," + "default:user,default:group," + \
             "user:ec3595d6-2c17-4696-8caa-7e139758d24a,group:ec3595d6-2c17-4696-8caa-7e139758d24a," + \
             "default:user:ec3595d6-2c17-4696-8caa-7e139758d24a,default:group:ec3595d6-2c17-4696-8caa-7e139758d24a"


# ------------------------------------------------------------------------------


class DirectoryTest(StorageTestCase):
    def _setUp(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=account_key, logging_enable=True)
        self.config = self.dsc._config

        self.file_system_name = self.get_resource_name('filesystem')

        if not self.is_playback():
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                file_system.create_file_system(timeout=5)
            except ResourceExistsError:
                pass

    def tearDown(self):
        if not self.is_playback():
            try:
                self.dsc.delete_file_system(self.file_system_name)
                for file_system in self.dsc.list_file_systems():
                    self.dsc.delete_file_system(file_system.name)
            except:
                pass

        return super(DirectoryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    def _create_directory_and_get_directory_client(self, directory_name=None):
        directory_name = directory_name if directory_name else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        return directory_client

    def _create_sub_directory_and_files(self, directory_client, num_of_dirs, num_of_files_per_dir):
        # the name suffix matter since we need to avoid creating the same directories/files in record mode
        for i in range(0, num_of_dirs):
            sub_dir = directory_client.create_sub_directory(self.get_resource_name('subdir' + str(i)))
            for j in range(0, num_of_files_per_dir):
                sub_dir.create_file(self.get_resource_name('subfile' + str(j)))

    def _create_file_system(self):
        return self.dsc.create_file_system(self._get_file_system_reference())

    # --Helpers-----------------------------------------------------------------

    @DataLakePreparer()
    def test_create_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @DataLakePreparer()
    def test_create_directory_owner_group_acl(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_string_acl = 'user::rwx,group::r-x,other::rwx'
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(owner=test_string, group=test_string, acl=test_string_acl)

        # Assert
        acl_properties = directory_client.get_access_control()
        self.assertIsNotNone(acl_properties)
        self.assertEqual(acl_properties['owner'], test_string)
        self.assertEqual(acl_properties['group'], test_string)
        self.assertEqual(acl_properties['acl'], test_string_acl)

    @DataLakePreparer()
    def test_create_directory_proposed_lease_id(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_duration = 15
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(lease_id=test_string, lease_duration=test_duration)

        # Assert
        properties = directory_client.get_directory_properties()
        self.assertIsNotNone(properties)
        self.assertEqual(properties.lease['status'], 'locked')
        self.assertEqual(properties.lease['state'], 'leased')
        self.assertEqual(properties.lease['duration'], 'fixed')

    @DataLakePreparer()
    def test_create_sub_directory_proposed_lease_id(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_duration = 15
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client = directory_client.create_sub_directory(sub_directory='sub1',
                                                                 lease_id=test_string,
                                                                 lease_duration=test_duration)

        # Assert
        properties = directory_client.get_directory_properties()
        self.assertIsNotNone(properties)
        self.assertEqual(properties.lease['status'], 'locked')
        self.assertEqual(properties.lease['state'], 'leased')
        self.assertEqual(properties.lease['duration'], 'fixed')

    @DataLakePreparer()
    def test_directory_exists(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client1 = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client2 = self.dsc.get_directory_client(self.file_system_name, "nonexistentdir")
        directory_client1.create_directory()

        self.assertTrue(directory_client1.exists())
        self.assertFalse(directory_client2.exists())

    @DataLakePreparer()
    def test_using_oauth_token_credential_to_create_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # generate a token with directory level create permission
        directory_name = self._get_directory_reference()
        token_credential = self.generate_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        response = directory_client.create_directory()
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_create_directory_with_match_conditions(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(match_condition=MatchConditions.IfMissing)

        # Assert
        self.assertTrue(created)

    @DataLakePreparer()
    def test_create_directory_with_permission(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(permissions="rwxr--r--", umask="0000")

        prop = directory_client.get_access_control()

        # Assert
        self.assertTrue(created)
        self.assertEqual(prop['permissions'], 'rwxr--r--')

    @DataLakePreparer()
    def test_create_directory_with_content_settings(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @DataLakePreparer()
    def test_create_directory_with_metadata(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(metadata=metadata)

        properties = directory_client.get_directory_properties()

        # Assert
        self.assertTrue(created)

    @DataLakePreparer()
    def test_delete_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        directory_client.delete_directory()

    @DataLakePreparer()
    def test_delete_directory_with_if_modified_since(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        prop = directory_client.get_directory_properties()

        with self.assertRaises(ResourceModifiedError):
            directory_client.delete_directory(if_modified_since=prop['last_modified'])

    @DataLakePreparer()
    def test_create_sub_directory_and_delete_sub_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Create a directory first, to prepare for creating sub directory
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        # Create sub directory from the current directory
        sub_directory_name = 'subdir'
        sub_directory_created = directory_client.create_sub_directory(sub_directory_name)

        # to make sure the sub directory was indeed created by get sub_directory properties from sub directory client
        sub_directory_client = self.dsc.get_directory_client(self.file_system_name,
                                                             directory_name + '/' + sub_directory_name)
        sub_properties = sub_directory_client.get_directory_properties()

        # Assert
        self.assertTrue(sub_directory_created)
        self.assertTrue(sub_properties)

        # Act
        directory_client.delete_sub_directory(sub_directory_name)
        with self.assertRaises(ResourceNotFoundError):
            sub_directory_client.get_directory_properties()

    @DataLakePreparer()
    def test_set_access_control(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        response = directory_client.set_access_control(permissions='0777')
        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_set_access_control_with_acl(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        acl = 'user::rwx,group::r-x,other::rwx'
        directory_client.set_access_control(acl=acl)
        access_control = directory_client.get_access_control()

        # Assert

        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_set_access_control_if_none_modified(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = directory_client.create_directory()

        response = directory_client.set_access_control(permissions='0777', etag=resp['etag'],
                                                       match_condition=MatchConditions.IfNotModified)
        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_get_access_control(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata, permissions='0777')

        # Act
        response = directory_client.get_access_control()
        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_get_access_control_with_match_conditions(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = directory_client.create_directory(permissions='0777', umask='0000')

        # Act
        response = directory_client.get_access_control(etag=resp['etag'], match_condition=MatchConditions.IfNotModified)
        # Assert
        self.assertIsNotNone(response)
        self.assertEqual(response['permissions'], 'rwxrwxrwx')

    @DataLakePreparer()
    def test_set_access_control_recursive(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = directory_client.set_access_control_recursive(acl=acl)

        # Assert
        # +1 as the dir itself was also included
        self.assertEqual(summary.counters.directories_successful, num_sub_dirs + 1)
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertIsNone(summary.continuation)
        access_control = directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_set_access_control_recursive_throws_exception_containing_continuation_token(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        response_list = list()

        def callback(response):
            response_list.append(response)
            if len(response_list) == 2:
                raise ServiceRequestError("network problem")
        acl = 'user::rwx,group::r-x,other::rwx'

        with self.assertRaises(AzureError) as acl_error:
            directory_client.set_access_control_recursive(acl=acl, batch_size=2, max_batches=2,
                                                          raw_response_hook=callback, retry_total=0)
        self.assertIsNotNone(acl_error.exception.continuation_token)
        self.assertEqual(acl_error.exception.message, "network problem")
        self.assertIsInstance(acl_error.exception, ServiceRequestError)

    @DataLakePreparer()
    def test_set_access_control_recursive_in_batches(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = directory_client.set_access_control_recursive(acl=acl, batch_size=2)

        # Assert
        # +1 as the dir itself was also included
        self.assertEqual(summary.counters.directories_successful, num_sub_dirs + 1)
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertIsNone(summary.continuation)
        access_control = directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_set_access_control_recursive_in_batches_with_progress_callback(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        last_response = AccessControlChangeResult(None, "")

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count

            last_response.counters = resp.aggregate_counters

        summary = directory_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertIsNone(summary.continuation)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(summary.counters.directories_successful, last_response.counters.directories_successful)
        self.assertEqual(summary.counters.files_successful, last_response.counters.files_successful)
        self.assertEqual(summary.counters.failure_count, last_response.counters.failure_count)
        access_control = directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_set_access_control_recursive_with_failures(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            failed_entries.append(resp.batch_failures)

        summary = directory_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                batch_size=2)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)

    @DataLakePreparer()
    def test_set_access_control_recursive_stop_on_failures(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            if resp.batch_failures:
                failed_entries.extend(resp.batch_failures)

        summary = directory_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                batch_size=6)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)

    @DataLakePreparer()
    def test_set_access_control_recursive_continue_on_failures(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()
        self.dsc.get_directory_client(self.file_system_name, directory_name).get_sub_directory_client("cannottouchthisdir") \
            .create_directory()

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            if resp.batch_failures:
                failed_entries.extend(resp.batch_failures)

        # set acl for all directories
        summary = directory_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                batch_size=6,
                                                                continue_on_failure=True)

        # Assert
        self.assertEqual(summary.counters.failure_count, 2)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 2)
        self.assertIsNone(summary.continuation)

        # reset the counter, set acl for part of the directories
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []
        summary2 = directory_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                 batch_size=6, max_batches=3,
                                                                 continue_on_failure=True)
        self.assertEqual(summary2.counters.failure_count, 2)
        self.assertEqual(summary2.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary2.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary2.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 2)
        self.assertIsNotNone(summary2.continuation)

    @DataLakePreparer()
    def test_set_access_control_recursive_in_batches_with_explicit_iteration(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        result = AccessControlChangeResult(None, "")
        iteration_count = 0
        max_batches = 2
        batch_size = 2

        while result.continuation is not None:
            result = directory_client.set_access_control_recursive(acl=acl, batch_size=batch_size, max_batches=max_batches,
                                                                   continuation=result.continuation)

            running_tally.directories_successful += result.counters.directories_successful
            running_tally.files_successful += result.counters.files_successful
            running_tally.failure_count += result.counters.failure_count
            iteration_count += 1

        # Assert
        self.assertEqual(running_tally.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(running_tally.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(running_tally.failure_count, 0)
        access_control = directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_update_access_control_recursive(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = directory_client.update_access_control_recursive(acl=acl)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        access_control = directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_update_access_control_recursive_in_batches(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        summary = directory_client.update_access_control_recursive(acl=acl, batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        access_control = directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_update_access_control_recursive_in_batches_with_progress_callback(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        last_response = AccessControlChangeResult(None, "")

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count

            last_response.counters = resp.aggregate_counters

        summary = directory_client.update_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                   batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertIsNone(summary.continuation)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(summary.counters.directories_successful, last_response.counters.directories_successful)
        self.assertEqual(summary.counters.files_successful, last_response.counters.files_successful)
        self.assertEqual(summary.counters.failure_count, last_response.counters.failure_count)
        access_control = directory_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_update_access_control_recursive_with_failures(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            failed_entries.append(resp.batch_failures)

        summary = directory_client.update_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                   batch_size=2)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)

    @DataLakePreparer()
    def test_remove_access_control_recursive(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        summary = directory_client.remove_access_control_recursive(acl=REMOVE_ACL)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)

    @DataLakePreparer()
    def test_remove_access_control_recursive_in_batches(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        summary = directory_client.remove_access_control_recursive(acl=REMOVE_ACL, batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)

    @DataLakePreparer()
    def test_remove_access_control_recursive_in_batches_with_progress_callback(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        running_tally = AccessControlChangeCounters(0, 0, 0)
        last_response = AccessControlChangeResult(None, "")

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count

            last_response.counters = resp.aggregate_counters

        summary = directory_client.remove_access_control_recursive(acl=REMOVE_ACL, progress_hook=progress_callback,
                                                                   batch_size=2)

        # Assert
        self.assertEqual(summary.counters.directories_successful,
                         num_sub_dirs + 1)  # +1 as the dir itself was also included
        self.assertEqual(summary.counters.files_successful, num_sub_dirs * num_file_per_sub_dir)
        self.assertEqual(summary.counters.failure_count, 0)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(summary.counters.directories_successful, last_response.counters.directories_successful)
        self.assertEqual(summary.counters.files_successful, last_response.counters.files_successful)
        self.assertEqual(summary.counters.failure_count, last_response.counters.failure_count)

    @DataLakePreparer()
    def test_remove_access_control_recursive_with_failures(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        if not self.is_playback():
            return
        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Using an AAD identity, create a directory to put files under that
        directory_name = self._get_directory_reference()
        token_credential = self.generate_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        # Create a file as super user
        self.dsc.get_directory_client(self.file_system_name, directory_name).get_file_client("cannottouchthis") \
            .create_file()

        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            failed_entries.append(resp.batch_failures)

        summary = directory_client.remove_access_control_recursive(acl=REMOVE_ACL, progress_hook=progress_callback,
                                                                   batch_size=2)

        # Assert
        self.assertEqual(summary.counters.failure_count, 1)
        self.assertEqual(summary.counters.directories_successful, running_tally.directories_successful)
        self.assertEqual(summary.counters.files_successful, running_tally.files_successful)
        self.assertEqual(summary.counters.failure_count, running_tally.failure_count)
        self.assertEqual(len(failed_entries), 1)

    @DataLakePreparer()
    def test_rename_from(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        new_name = "newname"

        new_directory_client = self.dsc.get_directory_client(self.file_system_name, new_name)

        new_directory_client._rename_path('/' + self.file_system_name + '/' + directory_name,
                                          content_settings=content_settings)
        properties = new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)
        self.assertIsNone(properties.get('content_settings'))

    @pytest.mark.skip(reason="Investigate why renaming from shorter path to longer path does not work")
    @DataLakePreparer()
    def test_rename_from_a_shorter_directory_to_longer_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        self._create_directory_and_get_directory_client(directory_name="old")

        new_name = "newname"
        new_directory_client = self._create_directory_and_get_directory_client(directory_name=new_name)
        new_directory_client = new_directory_client.create_sub_directory("newsub")

        new_directory_client._rename_path('/' + self.file_system_name + '/' + directory_name)
        properties = new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)

    @DataLakePreparer()
    def test_rename_from_a_directory_in_another_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # create a file dir1 under filesystem1
        old_file_system_name = self._get_directory_reference("oldfilesystem")
        old_dir_name = "olddir"
        old_client = self.dsc.get_file_system_client(old_file_system_name)
        old_client.create_file_system()
        old_client.create_directory(old_dir_name)

        # create a dir2 under filesystem2
        new_name = "newname"
        new_directory_client = self._create_directory_and_get_directory_client(directory_name=new_name)
        new_directory_client = new_directory_client.create_sub_directory("newsub")

        # rename dir1 under filesystem1 to dir2 under filesystem2
        new_directory_client._rename_path('/' + old_file_system_name + '/' + old_dir_name)
        properties = new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)

    @DataLakePreparer()
    def test_rename_from_an_unencoded_directory_in_another_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # create a directory under filesystem1
        old_file_system_name = self._get_directory_reference("oldfilesystem")
        old_dir_name = "old dir"
        old_client = self.dsc.get_file_system_client(old_file_system_name)
        old_client.create_file_system()
        old_dir_client = old_client.create_directory(old_dir_name)
        file_name = "oldfile"
        old_dir_client.create_file(file_name)

        # move the directory under filesystem2
        new_name = "new name/sub dir"
        new_file_system_name = self._get_directory_reference("newfilesystem")
        new_file_system_client = self.dsc.get_file_system_client(new_file_system_name)
        new_file_system_client.create_file_system()
        new_file_system_client.create_directory(new_name)

        # rename dir1 under filesystem1 to dir2 under filesystem2
        new_directory_client = old_dir_client.rename_directory('/' + new_file_system_name + '/' + new_name)
        properties = new_directory_client.get_directory_properties()
        file_properties = new_directory_client.get_file_client(file_name).get_file_properties()

        self.assertIsNotNone(properties)
        self.assertIsNotNone(file_properties)
        old_client.delete_file_system()

    @DataLakePreparer()
    def test_rename_to_an_existing_directory_in_another_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # create a file dir1 under filesystem1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        destination_dir_name = "destdir"
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        fs_client.create_file_system()
        destination_directory_client = fs_client.create_directory(destination_dir_name)

        # create a dir2 under filesystem2
        source_name = "source"
        source_directory_client = self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = source_directory_client.create_sub_directory("subdir")

        # rename dir2 under filesystem2 to dir1 under filesystem1
        res = source_directory_client.rename_directory('/' + destination_file_system_name + '/' + destination_dir_name)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            source_directory_client.get_directory_properties()

        self.assertEqual(res.url, destination_directory_client.url)

    @DataLakePreparer()
    def test_rename_with_none_existing_destination_condition_and_source_unmodified_condition(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        non_existing_dir_name = "nonexistingdir"

        # create a filesystem1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        fs_client.create_file_system()

        # create a dir2 under filesystem2
        source_name = "source"
        source_directory_client = self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = source_directory_client.create_sub_directory("subdir")

        # rename dir2 under filesystem2 to a non existing directory under filesystem1,
        # when dir1 does not exist and dir2 wasn't modified
        etag = source_directory_client.get_directory_properties()['etag']
        res = source_directory_client.rename_directory('/' + destination_file_system_name + '/' + non_existing_dir_name,
                                                       match_condition=MatchConditions.IfMissing,
                                                       source_etag=etag,
                                                       source_match_condition=MatchConditions.IfNotModified)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            source_directory_client.get_directory_properties()

        self.assertEqual(non_existing_dir_name, res.path_name)

    @DataLakePreparer()
    def test_rename_to_an_non_existing_directory_in_another_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # create a file dir1 under filesystem1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        non_existing_dir_name = "nonexistingdir"
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        fs_client.create_file_system()

        # create a dir2 under filesystem2
        source_name = "source"
        source_directory_client = self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = source_directory_client.create_sub_directory("subdir")

        # rename dir2 under filesystem2 to dir1 under filesystem1
        res = source_directory_client.rename_directory('/' + destination_file_system_name + '/' + non_existing_dir_name)


        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            source_directory_client.get_directory_properties()

        self.assertEqual(non_existing_dir_name, res.path_name)

    @pytest.mark.skip(reason="Investigate why renaming non-empty directory doesn't work")
    @DataLakePreparer()
    def test_rename_directory_to_non_empty_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        dir1 = self._create_directory_and_get_directory_client("dir1")
        dir1.create_sub_directory("subdir")

        dir2 = self._create_directory_and_get_directory_client("dir2")
        dir2.rename_directory(dir1.file_system_name + '/' + dir1.path_name)

        with self.assertRaises(HttpResponseError):
            dir2.get_directory_properties()

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_rename_dir_with_file_system_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        token = generate_file_system_sas(
            self.dsc.account_name,
            self.file_system_name,
            self.dsc.credential.account_key,
            FileSystemSasPermissions(write=True, read=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        dir_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, "olddirectory", credential=token)
        dir_client.create_directory()
        new_client = dir_client.rename_directory(dir_client.file_system_name+'/'+'newdirectory')

        new_client.get_directory_properties()
        self.assertEqual(new_client.path_name, "newdirectory")

    @DataLakePreparer()
    def test_get_properties(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        properties = directory_client.get_directory_properties()
        # Assert
        self.assertTrue(properties)
        self.assertIsNotNone(properties.metadata)
        self.assertEqual(properties.metadata['hello'], metadata['hello'])

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_using_directory_sas_to_read(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        client = self._create_directory_and_get_directory_client()
        directory_name = client.path_name

        # generate a token with directory level read permission
        token = generate_directory_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            self.dsc.credential.account_key,
            permission=DirectorySasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        access_control = directory_client.get_access_control()

        self.assertIsNotNone(access_control)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_using_directory_sas_to_create(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        # generate a token with directory level create permission
        directory_name = self._get_directory_reference()
        token = generate_directory_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            self.dsc.credential.account_key,
            permission=DirectorySasPermissions(create=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        response = directory_client.create_directory()
        self.assertIsNotNone(response)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_using_directory_sas_to_create_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        client = self._create_directory_and_get_directory_client()
        directory_name = client.path_name

        # generate a token with directory level read permission
        token = generate_directory_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            self.dsc.credential.account_key,
            permission=DirectorySasPermissions(create=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        directory_client.create_sub_directory("subdir")

        with self.assertRaises(HttpResponseError):
            directory_client.delete_directory()

    @DataLakePreparer()
    def test_using_directory_sas_to_create_file(self, datalake_storage_account_name, datalake_storage_account_key):
        newest_api_version = _SUPPORTED_API_VERSIONS[-1]

        service_client = DataLakeServiceClient("https://abc.dfs.core.windows.net", credential='fake')
        filesys_client = service_client.get_file_system_client("filesys")
        dir_client = DataLakeDirectoryClient("https://abc.dfs.core.windows.net", "filesys", "dir", credential='fake')
        file_client = dir_client.get_file_client("file")
        self.assertEqual(service_client.api_version, newest_api_version)
        self.assertEqual(filesys_client.api_version, newest_api_version)
        self.assertEqual(dir_client.api_version, newest_api_version)
        self.assertEqual(file_client.api_version, newest_api_version)
        
        service_client2 = DataLakeServiceClient("https://abc.dfs.core.windows.net", credential='fake', api_version="2019-02-02")
        filesys_client2 = service_client2.get_file_system_client("filesys")
        dir_client2 = DataLakeDirectoryClient("https://abc.dfs.core.windows.net", "filesys", "dir", credential='fake', api_version="2019-02-02")
        file_client2 = dir_client2.get_file_client("file")
        self.assertEqual(service_client2.api_version, "2019-02-02")
        self.assertEqual(filesys_client2.api_version, "2019-02-02")
        self.assertEqual(dir_client2.api_version, "2019-02-02")
        self.assertEqual(file_client2.api_version, "2019-02-02")

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
