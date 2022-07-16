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
from azure.core.credentials import AzureSasCredential

from azure.core.exceptions import (HttpResponseError, ResourceExistsError,
                                   ResourceNotFoundError, ClientAuthenticationError,
                                   ResourceModifiedError)
from azure.storage.filedatalake import (ContentSettings, generate_account_sas, generate_file_sas,
                                        ResourceTypes, AccountSasPermissions, DataLakeFileClient,
                                        FileSystemClient, DataLakeDirectoryClient, FileSasPermissions,
                                        generate_file_system_sas, FileSystemSasPermissions)
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.filedatalake._models import FileSystemEncryptionScope
from settings.testcase import DataLakePreparer
from devtools_testutils.storage import StorageTestCase

# ------------------------------------------------------------------------------

TEST_DIRECTORY_PREFIX = 'directory'
TEST_FILE_PREFIX = 'file'
FILE_PATH = 'file_output.temp.dat'

# ------------------------------------------------------------------------------


class FileTest(StorageTestCase):
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
            except:
                pass

        return super(FileTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    def _get_file_reference(self, prefix=TEST_FILE_PREFIX):
        file_name = self.get_resource_name(prefix)
        return file_name

    def _create_file_system(self):
        return self.dsc.create_file_system(self._get_file_system_reference())

    def _create_directory_and_return_client(self, directory=None):
        directory_name = directory if directory else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        return directory_client

    def _create_file_and_return_client(self, directory="", file=None):
        if directory:
            self._create_directory_and_return_client(directory)
        if not file:
            file = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.file_system_name, directory + '/' + file)
        file_client.create_file()
        return file_client

    # --Helpers-----------------------------------------------------------------

    @DataLakePreparer()
    def test_create_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        response = file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_create_file_owner_group_acl(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_string_acl = 'user::rwx,group::r-x,other::rwx'
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file(owner=test_string, group=test_string, acl=test_string_acl)

        # Assert
        acl_properties = file_client.get_access_control()
        self.assertIsNotNone(acl_properties)
        self.assertEqual(acl_properties['owner'], test_string)
        self.assertEqual(acl_properties['group'], test_string)
        self.assertEqual(acl_properties['acl'], test_string_acl)

    @DataLakePreparer()
    def test_create_file_proposed_lease_id(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_duration = 15
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file(lease_id=test_string, lease_duration=test_duration)

        # Assert
        properties = file_client.get_file_properties()
        self.assertIsNotNone(properties)
        self.assertEqual(properties.lease['status'], 'locked')
        self.assertEqual(properties.lease['state'], 'leased')
        self.assertEqual(properties.lease['duration'], 'fixed')

    @DataLakePreparer()
    def test_create_file_relative_expiry(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_expiry_time = 86400000  # 1 day in milliseconds
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file(expires_on=test_expiry_time)

        # Assert
        file_properties = file_client.get_file_properties()
        expiry_time = file_properties['expiry_time']
        expiry_time = expiry_time.replace(tzinfo=None)  # Strip timezone info to be able to compare
        creation_time = file_properties['creation_time']
        creation_time = creation_time.replace(tzinfo=None)  # Strip timezone info to be able to compare
        self.assertIsNotNone(file_properties)
        self.assertAlmostEqual(expiry_time, creation_time + timedelta(days=1), delta=timedelta(seconds=60))

    @DataLakePreparer()
    def test_create_file_absolute_expiry(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_expiry_time = datetime(2075, 4, 4)
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file(expires_on=test_expiry_time)

        # Assert
        file_properties = file_client.get_file_properties()
        expiry_time = file_properties['expiry_time']
        expiry_time = expiry_time.replace(tzinfo=None)  # Strip timezone info to be able to compare
        self.assertIsNotNone(file_properties)
        self.assertAlmostEqual(expiry_time, test_expiry_time, delta=timedelta(seconds=1))

    @DataLakePreparer()
    def test_create_file_extra_backslashes(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = self._create_file_and_return_client()

        new_file_client = DataLakeFileClient(self.account_url(datalake_storage_account_name, 'dfs'),
                                             file_client.file_system_name + '/',
                                             '/' + file_client.path_name,
                                             credential=datalake_storage_account_key, logging_enable=True)
        response = new_file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_file_exists(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client1 = directory_client.get_file_client('filename')
        file_client2 = directory_client.get_file_client('nonexistentfile')
        file_client1.create_file()

        self.assertTrue(file_client1.exists())
        self.assertFalse(file_client2.exists())

    @DataLakePreparer()
    def test_create_file_using_oauth_token_credential(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_name = self._get_file_reference()
        token_credential = self.generate_oauth_token()

        # Create a directory to put the file under that
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, file_name,
                                         credential=token_credential)

        response = file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_create_file_with_existing_name(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = self._create_file_and_return_client()

        with self.assertRaises(ResourceExistsError):
            # if the file exists then throw error
            # if_none_match='*' is to make sure no existing file
            file_client.create_file(match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    def test_create_file_with_lease_id(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        # Act
        file_client.create_file()
        lease = file_client.acquire_lease()
        create_resp = file_client.create_file(lease=lease)

        # Assert
        file_properties = file_client.get_file_properties()
        self.assertIsNotNone(file_properties)
        self.assertEqual(file_properties.etag, create_resp.get('etag'))
        self.assertEqual(file_properties.last_modified, create_resp.get('last_modified'))

    @DataLakePreparer()
    def test_create_file_under_root_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        # get a file client to interact with the file under root directory
        file_client = self.dsc.get_file_client(self.file_system_name, "filename")

        response = file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_append_data(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file()

        # Act
        response = file_client.append_data(b'abc', 0, 3)
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_append_empty_data(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()

        # Act
        file_client.flush_data(0)
        file_props = file_client.get_file_properties()

        self.assertIsNotNone(file_props['size'], 0)

    @DataLakePreparer()
    def test_flush_data(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file()

        # Act
        file_client.append_data(b'abc', 0, 3)
        response = file_client.flush_data(3)

        # Assert
        prop = file_client.get_file_properties()
        self.assertIsNotNone(response)
        self.assertEqual(prop['size'], 3)

    @DataLakePreparer()
    def test_flush_data_with_bool(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file()

        # Act
        response = file_client.append_data(b'abc', 0, 3, flush=True)

        # Assert
        prop = file_client.get_file_properties()
        self.assertIsNotNone(response)
        self.assertEqual(prop['size'], 3)

    @DataLakePreparer()
    def test_flush_data_with_match_condition(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        resp = file_client.create_file()

        # Act
        file_client.append_data(b'abc', 0, 3)

        # flush is successful because it isn't touched
        response = file_client.flush_data(3, etag=resp['etag'], match_condition=MatchConditions.IfNotModified)

        file_client.append_data(b'abc', 3, 3)
        with self.assertRaises(ResourceModifiedError):
            # flush is unsuccessful because extra data were appended.
            file_client.flush_data(6, etag=resp['etag'], match_condition=MatchConditions.IfNotModified)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_upload_data_to_none_existing_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # parallel upload cannot be recorded

        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        data = self.get_random_bytes(200*1024)
        file_client.upload_data(data, overwrite=True, max_concurrency=3)

        downloaded_data = file_client.download_file().readall()
        self.assertEqual(data, downloaded_data)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_upload_data_in_substreams(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # parallel upload cannot be recorded
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        # Get 16MB data
        data = self.get_random_bytes(16*1024*1024)
        # Ensure chunk size is greater than threshold (8MB > 4MB) - for optimized upload
        file_client.upload_data(data, chunk_size=8*1024*1024, overwrite=True, max_concurrency=3)
        downloaded_data = file_client.download_file().readall()
        self.assertEqual(data, downloaded_data)

        # Run on single thread
        file_client.upload_data(data, chunk_size=8*1024*1024, overwrite=True)
        downloaded_data = file_client.download_file().readall()
        self.assertEqual(data, downloaded_data)

    @DataLakePreparer()
    def test_upload_data_to_existing_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        # create an existing file
        file_client = directory_client.get_file_client('filename')
        file_client.create_file()
        file_client.append_data(b"abc", 0)
        file_client.flush_data(3)

        # to override the existing file
        data = self.get_random_bytes(100)
        with self.assertRaises(HttpResponseError):
            file_client.upload_data(data, max_concurrency=5)
        file_client.upload_data(data, overwrite=True, max_concurrency=5)

        downloaded_data = file_client.download_file().readall()
        self.assertEqual(data, downloaded_data)

    @DataLakePreparer()
    def test_upload_data_to_existing_file_with_content_settings(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        # create an existing file
        file_client = directory_client.get_file_client('filename')
        etag = file_client.create_file()['etag']

        # to override the existing file
        data = self.get_random_bytes(100)
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')

        file_client.upload_data(data, max_concurrency=5,
                                content_settings=content_settings, etag=etag,
                                match_condition=MatchConditions.IfNotModified)

        downloaded_data = file_client.download_file().readall()
        properties = file_client.get_file_properties()

        self.assertEqual(data, downloaded_data)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @DataLakePreparer()
    def test_upload_data_to_existing_file_with_permission_and_umask(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        # create an existing file
        file_client = directory_client.get_file_client('filename')
        etag = file_client.create_file()['etag']

        # to override the existing file
        data = self.get_random_bytes(100)

        file_client.upload_data(data, overwrite=True, max_concurrency=5,
                                permissions='0777', umask="0000",
                                etag=etag,
                                match_condition=MatchConditions.IfNotModified)

        downloaded_data = file_client.download_file().readall()
        prop = file_client.get_access_control()

        # Assert
        self.assertEqual(data, downloaded_data)
        self.assertEqual(prop['permissions'], 'rwxrwxrwx')

    @DataLakePreparer()
    def test_read_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()
        data = self.get_random_bytes(1024)

        # upload data to file
        file_client.append_data(data, 0, len(data))
        file_client.flush_data(len(data))

        # doanload the data and make sure it is the same as uploaded data
        downloaded_data = file_client.download_file().readall()
        self.assertEqual(data, downloaded_data)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_read_file_with_user_delegation_key(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        # Create file
        file_client = self._create_file_and_return_client()
        data = self.get_random_bytes(1024)
        # Upload data to file
        file_client.append_data(data, 0, len(data))
        file_client.flush_data(len(data))

        # Get user delegation key
        token_credential = self.generate_oauth_token()
        service_client = DataLakeServiceClient(self.account_url(datalake_storage_account_name, 'dfs'), credential=token_credential, logging_enable=True)
        user_delegation_key = service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        sas_token = generate_file_sas(file_client.account_name,
                                      file_client.file_system_name,
                                      None,
                                      file_client.path_name,
                                      user_delegation_key,
                                      permission=FileSasPermissions(read=True, create=True, write=True, delete=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1),
                                      )

        # doanload the data and make sure it is the same as uploaded data
        new_file_client = DataLakeFileClient(self.account_url(datalake_storage_account_name, 'dfs'),
                                             file_client.file_system_name,
                                             file_client.path_name,
                                             credential=sas_token, logging_enable=True)
        downloaded_data = new_file_client.download_file().readall()
        self.assertEqual(data, downloaded_data)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_set_acl_with_user_delegation_key(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        # Create file
        file_client = self._create_file_and_return_client()
        data = self.get_random_bytes(1024)
        # Upload data to file
        file_client.append_data(data, 0, len(data))
        file_client.flush_data(len(data))

        # Get user delegation key
        token_credential = self.generate_oauth_token()
        service_client = DataLakeServiceClient(self.account_url(datalake_storage_account_name, 'dfs'), credential=token_credential)
        user_delegation_key = service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        sas_token = generate_file_sas(file_client.account_name,
                                      file_client.file_system_name,
                                      None,
                                      file_client.path_name,
                                      user_delegation_key,
                                      permission=FileSasPermissions(execute=True, manage_access_control=True,
                                                                    manage_ownership=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1),
                                      )

        # doanload the data and make sure it is the same as uploaded data
        new_file_client = DataLakeFileClient(self.account_url(datalake_storage_account_name, 'dfs'),
                                             file_client.file_system_name,
                                             file_client.path_name,
                                             credential=sas_token)
        acl = 'user::rwx,group::r-x,other::rwx'
        owner = "dc140949-53b7-44af-b1e9-cd994951fb86"
        new_file_client.set_access_control(acl=acl, owner=owner)
        access_control = new_file_client.get_access_control()
        self.assertEqual(acl, access_control['acl'])
        self.assertEqual(owner, access_control['owner'])

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_preauthorize_user_with_user_delegation_key(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        # Create file
        file_client = self._create_file_and_return_client()
        data = self.get_random_bytes(1024)
        # Upload data to file
        file_client.append_data(data, 0, len(data))
        file_client.flush_data(len(data))
        file_client.set_access_control(owner="68390a19-a643-458b-b726-408abf67b4fc", permissions='0777')
        acl = file_client.get_access_control()

        # Get user delegation key
        token_credential = self.generate_oauth_token()
        service_client = DataLakeServiceClient(self.account_url(datalake_storage_account_name, 'dfs'), credential=token_credential)
        user_delegation_key = service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        sas_token = generate_file_sas(file_client.account_name,
                                      file_client.file_system_name,
                                      None,
                                      file_client.path_name,
                                      user_delegation_key,
                                      permission=FileSasPermissions(read=True, write=True, manage_access_control=True,
                                                                    manage_ownership=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1),
                                      preauthorized_agent_object_id="68390a19-a643-458b-b726-408abf67b4fc"
                                      )

        # doanload the data and make sure it is the same as uploaded data
        new_file_client = DataLakeFileClient(self.account_url(datalake_storage_account_name, 'dfs'),
                                             file_client.file_system_name,
                                             file_client.path_name,
                                             credential=sas_token)

        acl = new_file_client.set_access_control(permissions='0777')
        self.assertIsNotNone(acl)

    @DataLakePreparer()
    def test_read_file_into_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()
        data = self.get_random_bytes(1024)

        # upload data to file
        file_client.append_data(data, 0, len(data))
        file_client.flush_data(len(data))

        # doanload the data into a file and make sure it is the same as uploaded data
        with open(FILE_PATH, 'wb') as stream:
            download = file_client.download_file(max_concurrency=2)
            download.readinto(stream)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @DataLakePreparer()
    def test_read_file_to_text(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()
        data = self.get_random_text_data(1024)

        # upload data to file
        file_client.append_data(data, 0, len(data))
        file_client.flush_data(len(data))

        # doanload the text data and make sure it is the same as uploaded data
        downloaded_data = file_client.download_file(max_concurrency=2, encoding="utf-8").readall()

        # Assert
        self.assertEqual(data, downloaded_data)


    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_account_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        file_name = self._get_file_reference()
        # create a file under root directory
        self._create_file_and_return_client(file=file_name)

        # generate a token with file level read permission
        token = generate_account_sas(
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(file_system=True, object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        for credential in [token, AzureSasCredential(token)]:
            # read the created file which is under root directory
            file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, file_name, credential=credential)
            properties = file_client.get_file_properties()

            # make sure we can read the file properties
            self.assertIsNotNone(properties)

            # try to write to the created file with the token
            with self.assertRaises(HttpResponseError):
                file_client.append_data(b"abcd", 0, 4)

    @DataLakePreparer()
    def test_account_sas_raises_if_sas_already_in_uri(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        with self.assertRaises(ValueError):
            DataLakeFileClient(self.dsc.url + "?sig=foo", self.file_system_name, "foo", credential=AzureSasCredential("?foo=bar"))

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_file_sas_only_applies_to_file_level(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only
        file_name = self._get_file_reference()
        directory_name = self._get_directory_reference()
        self._create_file_and_return_client(directory=directory_name, file=file_name)

        # generate a token with file level read and write permissions
        token = generate_file_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            file_name,
            self.dsc.credential.account_key,
            permission=FileSasPermissions(read=True, write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, directory_name+'/'+file_name,
                                         credential=token)
        properties = file_client.get_file_properties()

        # make sure we can read the file properties
        self.assertIsNotNone(properties)

        # try to write to the created file with the token
        response = file_client.append_data(b"abcd", 0, 4, validate_content=True)
        self.assertIsNotNone(response)

        # the token is for file level, so users are not supposed to have access to file system level operations
        file_system_client = FileSystemClient(self.dsc.url, self.file_system_name, credential=token)
        with self.assertRaises(ClientAuthenticationError):
            file_system_client.get_file_system_properties()

        # the token is for file level, so users are not supposed to have access to directory level operations
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        with self.assertRaises(ClientAuthenticationError):
            directory_client.get_directory_properties()

    @DataLakePreparer()
    def test_delete_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = self._create_file_and_return_client()

        file_client.delete_file()

        with self.assertRaises(ResourceNotFoundError):
            file_client.get_file_properties()

    @DataLakePreparer()
    def test_delete_file_with_if_unmodified_since(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = self._create_file_and_return_client()

        prop = file_client.get_file_properties()
        file_client.delete_file(if_unmodified_since=prop['last_modified'])

        # Make sure the file was deleted
        with self.assertRaises(ResourceNotFoundError):
            file_client.get_file_properties()

    @DataLakePreparer()
    def test_set_access_control(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()

        response = file_client.set_access_control(permissions='0777')

        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_set_access_control_with_match_conditions(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()

        with self.assertRaises(ResourceModifiedError):
            file_client.set_access_control(permissions='0777', match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    def test_get_access_control(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()
        file_client.set_access_control(permissions='0777')

        # Act
        response = file_client.get_access_control()

        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_get_access_control_with_if_modified_since(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()
        file_client.set_access_control(permissions='0777')

        prop = file_client.get_file_properties()

        # Act
        response = file_client.get_access_control(if_modified_since=prop['last_modified']-timedelta(minutes=15))

        # Assert
        self.assertIsNotNone(response)

    @DataLakePreparer()
    def test_set_access_control_recursive(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        acl = 'user::rwx,group::r-x,other::rwx'
        file_client = self._create_file_and_return_client()

        summary = file_client.set_access_control_recursive(acl=acl)

        # Assert
        self.assertEqual(summary.counters.directories_successful, 0)
        self.assertEqual(summary.counters.files_successful, 1)
        self.assertEqual(summary.counters.failure_count, 0)
        access_control = file_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_update_access_control_recursive(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        acl = 'user::rwx,group::r-x,other::rwx'
        file_client = self._create_file_and_return_client()

        summary = file_client.update_access_control_recursive(acl=acl)

        # Assert
        self.assertEqual(summary.counters.directories_successful, 0)
        self.assertEqual(summary.counters.files_successful, 1)
        self.assertEqual(summary.counters.failure_count, 0)
        access_control = file_client.get_access_control()
        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_remove_access_control_recursive(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        acl = "mask," + "default:user,default:group," + \
             "user:ec3595d6-2c17-4696-8caa-7e139758d24a,group:ec3595d6-2c17-4696-8caa-7e139758d24a," + \
             "default:user:ec3595d6-2c17-4696-8caa-7e139758d24a,default:group:ec3595d6-2c17-4696-8caa-7e139758d24a"
        file_client = self._create_file_and_return_client()
        summary = file_client.remove_access_control_recursive(acl=acl)

        # Assert
        self.assertEqual(summary.counters.directories_successful, 0)
        self.assertEqual(summary.counters.files_successful, 1)
        self.assertEqual(summary.counters.failure_count, 0)

    @DataLakePreparer()
    def test_get_properties(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_client = self._create_directory_and_return_client()

        metadata = {'hello': 'world', 'number': '42'}
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        file_client = directory_client.create_file("newfile", metadata=metadata, content_settings=content_settings)
        file_client.append_data(b"abc", 0, 3)
        file_client.flush_data(3)
        properties = file_client.get_file_properties()

        # Assert
        self.assertTrue(properties)
        self.assertEqual(properties.size, 3)
        self.assertEqual(properties.metadata['hello'], metadata['hello'])
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @DataLakePreparer()
    def test_set_expiry(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_client = self._create_directory_and_return_client()

        metadata = {'hello': 'world', 'number': '42'}
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        expires_on = datetime.utcnow() + timedelta(hours=1)
        file_client = directory_client.create_file("newfile", metadata=metadata, content_settings=content_settings)
        file_client.set_file_expiry("Absolute", expires_on=expires_on)
        properties = file_client.get_file_properties()

        # Assert
        self.assertTrue(properties)
        self.assertIsNotNone(properties.expiry_time)

    @DataLakePreparer()
    def test_rename_file_with_non_used_name(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = self._create_file_and_return_client()
        data_bytes = b"abc"
        file_client.append_data(data_bytes, 0, 3)
        file_client.flush_data(3)
        new_client = file_client.rename_file(file_client.file_system_name+'/'+'newname')

        data = new_client.download_file().readall()
        self.assertEqual(data, data_bytes)
        self.assertEqual(new_client.path_name, "newname")

    @DataLakePreparer()
    def test_file_encryption_scope_from_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        url = self.account_url(datalake_storage_account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=datalake_storage_account_key, logging_enable=True)
        self.file_system_name = self.get_resource_name('filesystem')
        file_name = 'testfile'
        encryption_scope = FileSystemEncryptionScope(default_encryption_scope="hnstestscope1")

        file_system = self.dsc.get_file_system_client(self.file_system_name)
        file_system.create_file_system(file_system_encryption_scope=encryption_scope)

        file_client = file_system.create_file(file_name)
        props = file_client.get_file_properties()

        # Assert
        self.assertTrue(props)
        self.assertIsNotNone(props['encryption_scope'])
        self.assertEqual(props['encryption_scope'], encryption_scope.default_encryption_scope)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_account_sas_encryption_scope_token(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        token = generate_account_sas(
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(object=True),
            AccountSasPermissions(write=True, read=True, create=True, delete=True),
            datetime.utcnow() + timedelta(hours=5),
            encryption_scope="hnstestscope1",
        )
        self.assertTrue("hnstestscope1" in token)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_rename_file_with_file_system_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # sas token is calculated from storage key, so live only
        token = generate_file_system_sas(
            self.dsc.account_name,
            self.file_system_name,
            self.dsc.credential.account_key,
            FileSystemSasPermissions(write=True, read=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, "oldfile", credential=token)
        file_client.create_file()
        data_bytes = b"abc"
        file_client.append_data(data_bytes, 0, 3)
        file_client.flush_data(3)
        new_client = file_client.rename_file(file_client.file_system_name+'/'+'newname')

        data = new_client.download_file().readall()
        self.assertEqual(data, data_bytes)
        self.assertEqual(new_client.path_name, "newname")

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_rename_file_with_file_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only
        token = generate_file_sas(self.dsc.account_name,
                                  self.file_system_name,
                                  None,
                                  "oldfile",
                                  datalake_storage_account_key,
                                  permission=FileSasPermissions(read=True, create=True, write=True, delete=True),
                                  expiry=datetime.utcnow() + timedelta(hours=1),
                                  )

        new_token = generate_file_sas(self.dsc.account_name,
                                      self.file_system_name,
                                      None,
                                      "newname",
                                      datalake_storage_account_key,
                                      permission=FileSasPermissions(read=True, create=True, write=True, delete=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1),
                                      )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, "oldfile", credential=token)
        file_client.create_file()
        data_bytes = b"abc"
        file_client.append_data(data_bytes, 0, 3)
        file_client.flush_data(3)
        new_client = file_client.rename_file(file_client.file_system_name+'/'+'newname'+'?'+new_token)

        data = new_client.download_file().readall()
        self.assertEqual(data, data_bytes)
        self.assertEqual(new_client.path_name, "newname")

    @pytest.mark.skip(reason="Service bug, requires further investigation.")
    @DataLakePreparer()
    def test_rename_file_with_account_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        token = generate_account_sas(
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(object=True),
            AccountSasPermissions(write=True, read=True, create=True, delete=True),
            datetime.utcnow() + timedelta(hours=5),
        )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, "oldfile", credential=token)
        file_client.create_file()
        data_bytes = b"abc"
        file_client.append_data(data_bytes, 0, 3)
        file_client.flush_data(3)
        new_client = file_client.rename_file(file_client.file_system_name+'/'+'newname')

        data = new_client.download_file().readall()
        self.assertEqual(data, data_bytes)
        self.assertEqual(new_client.path_name, "newname")

    @DataLakePreparer()
    def test_rename_file_to_existing_file(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # create the existing file
        existing_file_client = self._create_file_and_return_client(file="existingfile")
        existing_file_client.append_data(b"a", 0, 1)
        existing_file_client.flush_data(1)
        old_url = existing_file_client.url

        # prepare to rename the file to the existing file
        file_client = self._create_file_and_return_client()
        data_bytes = b"abc"
        file_client.append_data(data_bytes, 0, 3)
        file_client.flush_data(3)
        new_client = file_client.rename_file(file_client.file_system_name+'/'+existing_file_client.path_name)
        new_url = file_client.url

        data = new_client.download_file().readall()
        # the existing file was overridden
        self.assertEqual(data, data_bytes)

    @DataLakePreparer()
    def test_rename_file_will_not_change_existing_directory(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # create none empty directory(with 2 files)
        dir1 = self._create_directory_and_return_client(directory="dir1")
        f1 = dir1.create_file("file1")
        f1.append_data(b"file1", 0, 5)
        f1.flush_data(5)
        f2 = dir1.create_file("file2")
        f2.append_data(b"file2", 0, 5)
        f2.flush_data(5)

        # create another none empty directory(with 2 files)
        dir2 = self._create_directory_and_return_client(directory="dir2")
        f3 = dir2.create_file("file3")
        f3.append_data(b"file3", 0, 5)
        f3.flush_data(5)
        f4 = dir2.create_file("file4")
        f4.append_data(b"file4", 0, 5)
        f4.flush_data(5)

        new_client = f3.rename_file(f1.file_system_name+'/'+f1.path_name)

        self.assertEqual(new_client.download_file().readall(), b"file3")

        # make sure the data in file2 and file4 weren't touched
        f2_data = f2.download_file().readall()
        self.assertEqual(f2_data, b"file2")

        f4_data = f4.download_file().readall()
        self.assertEqual(f4_data, b"file4")

        with self.assertRaises(HttpResponseError):
            f3.download_file().readall()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
