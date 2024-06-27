# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta
from time import sleep

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ServiceRequestError
)
from azure.storage.filedatalake import (
    ContentSettings,
    DataLakeDirectoryClient,
    DataLakeServiceClient,
    DirectorySasPermissions,
    EncryptionScopeOptions,
    FileSystemSasPermissions,
    generate_directory_sas,
    generate_file_system_sas
)
from azure.storage.filedatalake._models import AccessControlChangeCounters, AccessControlChangeResult
from azure.storage.filedatalake._serialize import _SUPPORTED_API_VERSIONS

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import DataLakePreparer

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
REMOVE_ACL = "mask," + "default:user,default:group," + \
             "user:ec3595d6-2c17-4696-8caa-7e139758d24a,group:ec3595d6-2c17-4696-8caa-7e139758d24a," + \
             "default:user:ec3595d6-2c17-4696-8caa-7e139758d24a,default:group:ec3595d6-2c17-4696-8caa-7e139758d24a"


# ------------------------------------------------------------------------------


class TestDirectory(StorageRecordedTestCase):
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
    @recorded_by_proxy
    def test_create_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert created

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_owner_group_acl(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert acl_properties is not None
        assert acl_properties['owner'] == test_string
        assert acl_properties['group'] == test_string
        assert acl_properties['acl'] == test_string_acl

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_proposed_lease_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_duration = 15
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(lease_id=test_string, lease_duration=test_duration)

        # Assert
        properties = directory_client.get_directory_properties()
        assert properties is not None
        assert properties.lease['status'] == 'locked'
        assert properties.lease['state'] == 'leased'
        assert properties.lease['duration'] == 'fixed'

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_sub_directory_proposed_lease_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert properties is not None
        assert properties.lease['status'] == 'locked'
        assert properties.lease['state'] == 'leased'
        assert properties.lease['duration'] == 'fixed'

    @DataLakePreparer()
    @recorded_by_proxy
    def test_directory_exists(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client1 = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client2 = self.dsc.get_directory_client(self.file_system_name, "nonexistentdir")
        directory_client1.create_directory()

        assert directory_client1.exists()
        assert not directory_client2.exists()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_using_oauth_token_credential_to_create_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # generate a token with directory level create permission
        directory_name = self._get_directory_reference()
        token_credential = self.get_credential(DataLakeServiceClient)
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        response = directory_client.create_directory()
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_with_match_conditions(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(match_condition=MatchConditions.IfMissing)

        # Assert
        assert created

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_with_permission(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(permissions="rwxr--r--", umask="0000")

        prop = directory_client.get_access_control()

        # Assert
        assert created
        assert prop['permissions'] == 'rwxr--r--'

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_with_content_settings(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert created

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_with_metadata(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(metadata=metadata)

        properties = directory_client.get_directory_properties()

        # Assert
        assert created

    @DataLakePreparer()
    @recorded_by_proxy
    def test_delete_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        directory_client.delete_directory()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_delete_directory_with_if_modified_since(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        prop = directory_client.get_directory_properties()

        with pytest.raises(ResourceModifiedError):
            directory_client.delete_directory(if_modified_since=prop['last_modified'])

    @DataLakePreparer()
    @pytest.mark.live_test_only
    @pytest.mark.skip(reason="Requires manual OAuth setup and creates 5000+ files")
    def test_delete_directory_paginated(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Set this to object id (not client id) of an AAD app that does not have permission
        # to storage account through RBAC.
        # Also make sure oauth settings (TENANT_ID, CLIENT_ID, CLIENT_SECRET) are pointing to this AAD app
        object_id = '68bff720-253b-428c-b124-603700654ea9'

        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        for i in range (0, 5020):
            file_client = directory_client.get_file_client(f"file{i}")
            file_client.create_file()

        root_directory = self.dsc.get_directory_client(self.file_system_name, "/")
        acl = root_directory.get_access_control()['acl']

        # Add permission for AAD app on root directory
        new_acl = acl + "," + f"user:{object_id}:rwx"
        root_directory.set_access_control_recursive(new_acl)

        token_credential = self.get_credential(DataLakeServiceClient)
        directory_client_oauth = DataLakeDirectoryClient(
            self.dsc.url,
            self.file_system_name,
            directory_name,
            credential=token_credential
        )

        # Act
        directory_client_oauth.delete_directory()

        self.dsc.delete_file_system(self.file_system_name)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_sub_directory_and_delete_sub_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert sub_directory_created
        assert sub_properties

        # Act
        directory_client.delete_sub_directory(sub_directory_name)
        with pytest.raises(ResourceNotFoundError):
            sub_directory_client.get_directory_properties()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        response = directory_client.set_access_control(permissions='0777')
        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control_with_acl(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        acl = 'user::rwx,group::r-x,other::rwx'
        directory_client.set_access_control(acl=acl)
        access_control = directory_client.get_access_control()

        # Assert

        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control_if_none_modified(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = directory_client.create_directory()

        response = directory_client.set_access_control(permissions='0777', etag=resp['etag'],
                                                       match_condition=MatchConditions.IfNotModified)
        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_access_control(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata, permissions='0777')

        # Act
        response = directory_client.get_access_control()
        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_access_control_with_match_conditions(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = directory_client.create_directory(permissions='0777', umask='0000')

        # Act
        response = directory_client.get_access_control(etag=resp['etag'], match_condition=MatchConditions.IfNotModified)
        # Assert
        assert response is not None
        assert response['permissions'] == 'rwxrwxrwx'

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control_recursive(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert summary.counters.directories_successful == num_sub_dirs + 1
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0
        assert summary.continuation is None
        access_control = directory_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control_recursive_throws_exception_containing_continuation_token(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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

        with pytest.raises(AzureError) as acl_error:
            directory_client.set_access_control_recursive(acl=acl, batch_size=2, max_batches=2,
                                                          raw_response_hook=callback, retry_total=0)
        assert acl_error.value.continuation_token is not None
        assert acl_error.value.message == "network problem"
        assert acl_error.typename == "ServiceRequestError"

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control_recursive_in_batches(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert summary.counters.directories_successful == num_sub_dirs + 1
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0
        assert summary.continuation is None
        access_control = directory_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control_recursive_in_batches_with_progress_callback(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert summary.counters.directories_successful == num_sub_dirs + 1  # +1 as the dir itself was also included
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0
        assert summary.continuation is None
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert summary.counters.directories_successful == last_response.counters.directories_successful
        assert summary.counters.files_successful == last_response.counters.files_successful
        assert summary.counters.failure_count == last_response.counters.failure_count
        access_control = directory_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_set_access_control_recursive_with_failures(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        url = self.account_url(datalake_storage_account_name, 'dfs')
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Create files and directories with provided owner except file3
        test_guid = "5d56d308-df82-4266-ba63-ef1da3945873"
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(owner=test_guid)
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir1').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir2').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir1/file1').create_file(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir2/file2').create_file(owner=test_guid, permissions='0777')
        directory_client.get_file_client('file3').create_file()

        # User delegation SAS with provided owner permissions
        token_credential = self.get_credential(DataLakeServiceClient)
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        owner_dsc = DataLakeServiceClient(url, credential=token_credential)
        user_delegation_key = owner_dsc.get_user_delegation_key(start_time, expiry_time)
        sas_token = self.generate_sas(
            generate_directory_sas,
            datalake_storage_account_name,
            self.file_system_name,
            directory_name,
            user_delegation_key,
            permission='racwdlmeop',
            expiry=expiry_time,
            agent_object_id=test_guid
        )

        if self.is_live:
            sleep(10)

        owner_dir_client = DataLakeDirectoryClient(url, self.file_system_name, directory_name, sas_token)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            failed_entries.append(resp.batch_failures)

        summary = owner_dir_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                batch_size=2)

        # Assert
        assert summary.counters.failure_count == 1
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert len(failed_entries) == 1

        return variables

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_set_access_control_recursive_stop_on_failures(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        url = self.account_url(datalake_storage_account_name, 'dfs')
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Create files and directories with provided owner except file3
        test_guid = "5d56d308-df82-4266-ba63-ef1da3945873"
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(owner=test_guid)
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir1').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir2').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir1/file1').create_file(owner=test_guid,permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir2/file2').create_file(owner=test_guid,permissions='0777')
        directory_client.get_file_client('file3').create_file()

        # User delegation SAS with provided owner permissions
        token_credential = self.get_credential(DataLakeServiceClient)
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        owner_dsc = DataLakeServiceClient(url, credential=token_credential)
        user_delegation_key = owner_dsc.get_user_delegation_key(start_time, expiry_time)
        sas_token = self.generate_sas(
            generate_directory_sas,
            datalake_storage_account_name,
            self.file_system_name,
            directory_name,
            user_delegation_key,
            permission='racwdlmeop',
            expiry=expiry_time,
            agent_object_id=test_guid
        )

        if self.is_live:
            sleep(10)

        owner_dir_client = DataLakeDirectoryClient(url, self.file_system_name, directory_name, sas_token)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            if resp.batch_failures:
                failed_entries.append(resp.batch_failures)

        summary = owner_dir_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                batch_size=2)

        # Assert
        assert summary.counters.failure_count == 1
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert len(failed_entries) == 1

        return variables

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_set_access_control_recursive_continue_on_failures(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        url = self.account_url(datalake_storage_account_name, 'dfs')
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Create files and directories with provided owner except file3, dir3
        test_guid = "5d56d308-df82-4266-ba63-ef1da3945873"
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(owner=test_guid)
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir1').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir2').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir1/file1').create_file(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir2/file2').create_file(owner=test_guid, permissions='0777')

        directory_client.get_file_client('file3').create_file()
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/dir3').create_directory()

        # User delegation SAS with provided owner permissions
        token_credential = self.get_credential(DataLakeServiceClient)
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        owner_dsc = DataLakeServiceClient(url, credential=token_credential)
        user_delegation_key = owner_dsc.get_user_delegation_key(start_time, expiry_time)
        sas_token = self.generate_sas(
            generate_directory_sas,
            datalake_storage_account_name,
            self.file_system_name,
            directory_name,
            user_delegation_key,
            permission='racwdlmeop',
            expiry=expiry_time,
            agent_object_id=test_guid
        )

        if self.is_live:
            sleep(10)

        owner_dir_client = DataLakeDirectoryClient(url, self.file_system_name, directory_name, sas_token)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            if resp.batch_failures:
                failed_entries.append(resp.batch_failures)

        summary = owner_dir_client.set_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                batch_size=2, continue_on_failure=True)

        # Assert
        assert summary.counters.failure_count == 2
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert len(failed_entries) == 2

        return variables

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_access_control_recursive_in_batches_with_explicit_iteration(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert running_tally.directories_successful == num_sub_dirs + 1  # +1 as the dir itself was also included
        assert running_tally.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert running_tally.failure_count == 0
        access_control = directory_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_update_access_control_recursive(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert summary.counters.directories_successful == num_sub_dirs + 1 # +1 as the dir itself was also included
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0
        access_control = directory_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_update_access_control_recursive_in_batches(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert summary.counters.directories_successful == num_sub_dirs + 1 # +1 as the dir itself was also included
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0
        access_control = directory_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_update_access_control_recursive_in_batches_with_progress_callback(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert summary.counters.directories_successful == num_sub_dirs + 1  # +1 as the dir itself was also included
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0
        assert summary.continuation is None
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert summary.counters.directories_successful == last_response.counters.directories_successful
        assert summary.counters.files_successful == last_response.counters.files_successful
        assert summary.counters.failure_count == last_response.counters.failure_count
        access_control = directory_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_update_access_control_recursive_with_failures(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        url = self.account_url(datalake_storage_account_name, 'dfs')
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Create files and directories with provided owner except file3
        test_guid = "5d56d308-df82-4266-ba63-ef1da3945873"
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(owner=test_guid)
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir1').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir2').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir1/file1').create_file(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir2/file2').create_file(owner=test_guid, permissions='0777')
        directory_client.get_file_client('file3').create_file()

        # User delegation SAS with provided owner permissions
        token_credential = self.get_credential(DataLakeServiceClient)
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        owner_dsc = DataLakeServiceClient(url, credential=token_credential)
        user_delegation_key = owner_dsc.get_user_delegation_key(start_time, expiry_time)
        sas_token = self.generate_sas(
            generate_directory_sas,
            datalake_storage_account_name,
            self.file_system_name,
            directory_name,
            user_delegation_key,
            permission='racwdlmeop',
            expiry=expiry_time,
            agent_object_id=test_guid
        )

        if self.is_live:
            sleep(10)

        owner_dir_client = DataLakeDirectoryClient(url, self.file_system_name, directory_name, sas_token)

        acl = 'user::rwx,group::r-x,other::rwx'
        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            if resp.batch_failures:
                failed_entries.append(resp.batch_failures)

        summary = owner_dir_client.update_access_control_recursive(acl=acl, progress_hook=progress_callback,
                                                                   batch_size=2)

        # Assert
        assert summary.counters.failure_count == 1
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert len(failed_entries) == 1

        return variables

    @DataLakePreparer()
    @recorded_by_proxy
    def test_remove_access_control_recursive(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        summary = directory_client.remove_access_control_recursive(acl=REMOVE_ACL)

        # Assert
        assert summary.counters.directories_successful == num_sub_dirs + 1  # +1 as the dir itself was also included
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0

    @DataLakePreparer()
    @recorded_by_proxy
    def test_remove_access_control_recursive_in_batches(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        num_sub_dirs = 5
        num_file_per_sub_dir = 5
        self._create_sub_directory_and_files(directory_client, num_sub_dirs, num_file_per_sub_dir)

        summary = directory_client.remove_access_control_recursive(acl=REMOVE_ACL, batch_size=2)

        # Assert
        summary.counters.directories_successful == num_sub_dirs + 1  # +1 as the dir itself was also included
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0

    @DataLakePreparer()
    @recorded_by_proxy
    def test_remove_access_control_recursive_in_batches_with_progress_callback(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        summary.counters.directories_successful == num_sub_dirs + 1  # +1 as the dir itself was also included
        assert summary.counters.files_successful == num_sub_dirs * num_file_per_sub_dir
        assert summary.counters.failure_count == 0
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert summary.counters.directories_successful == last_response.counters.directories_successful
        assert summary.counters.files_successful == last_response.counters.files_successful
        assert summary.counters.failure_count == last_response.counters.failure_count

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_remove_access_control_recursive_with_failures(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        url = self.account_url(datalake_storage_account_name, 'dfs')
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        root_directory_client = self.dsc.get_file_system_client(self.file_system_name)._get_root_directory_client()
        root_directory_client.set_access_control(acl="user::--x,group::--x,other::--x")

        # Create files and directories with provided owner except file3
        test_guid = "5d56d308-df82-4266-ba63-ef1da3945873"
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(owner=test_guid)
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir1').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_directory_client(self.file_system_name, directory_name + '/subdir2').create_directory(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir1/file1').create_file(owner=test_guid, permissions='0777')
        self.dsc.get_file_client(self.file_system_name, directory_name + '/subdir2/file2').create_file(owner=test_guid, permissions='0777')
        directory_client.get_file_client('file3').create_file()

        # User delegation SAS with provided owner permissions
        token_credential = self.get_credential(DataLakeServiceClient)
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        owner_dsc = DataLakeServiceClient(url, credential=token_credential)
        user_delegation_key = owner_dsc.get_user_delegation_key(start_time, expiry_time)
        sas_token = self.generate_sas(
            generate_directory_sas,
            datalake_storage_account_name,
            self.file_system_name,
            directory_name,
            user_delegation_key,
            permission='racwdlmeop',
            expiry=expiry_time,
            agent_object_id=test_guid
        )

        if self.is_live:
            sleep(10)

        owner_dir_client = DataLakeDirectoryClient(url, self.file_system_name, directory_name, sas_token)

        running_tally = AccessControlChangeCounters(0, 0, 0)
        failed_entries = []

        def progress_callback(resp):
            running_tally.directories_successful += resp.batch_counters.directories_successful
            running_tally.files_successful += resp.batch_counters.files_successful
            running_tally.failure_count += resp.batch_counters.failure_count
            if resp.batch_failures:
                failed_entries.append(resp.batch_failures)

        summary = owner_dir_client.remove_access_control_recursive(acl=REMOVE_ACL, progress_hook=progress_callback, batch_size=2)

        # Assert
        assert summary.counters.failure_count == 1
        assert summary.counters.directories_successful == running_tally.directories_successful
        assert summary.counters.files_successful == running_tally.files_successful
        assert summary.counters.failure_count == running_tally.failure_count
        assert len(failed_entries) == 1

        return variables

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_from(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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

        assert properties is not None
        assert properties.get('content_settings') is None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_from_a_shorter_directory_to_longer_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        self._create_directory_and_get_directory_client(directory_name=directory_name)

        new_name = "newname"
        new_directory_client = self._create_directory_and_get_directory_client(directory_name=new_name)
        new_directory_client = new_directory_client.create_sub_directory("newsub")

        new_directory_client._rename_path('/' + self.file_system_name + '/' + directory_name)
        properties = new_directory_client.get_directory_properties()

        assert properties is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_from_a_directory_in_another_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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

        assert properties is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_from_an_unencoded_directory_in_another_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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

        assert properties is not None
        assert file_properties is not None
        old_client.delete_file_system()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_to_an_existing_directory_in_another_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        with pytest.raises(HttpResponseError):
            source_directory_client.get_directory_properties()

        assert res.url == destination_directory_client.url

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_with_none_existing_destination_condition_and_source_unmodified_condition(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        with pytest.raises(HttpResponseError):
            source_directory_client.get_directory_properties()

        assert non_existing_dir_name == res.path_name

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_to_an_non_existing_directory_in_another_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        with pytest.raises(HttpResponseError):
            source_directory_client.get_directory_properties()

        assert non_existing_dir_name == res.path_name

    @pytest.mark.skip(reason="Investigate why renaming non-empty directory doesn't work")
    @DataLakePreparer()
    def test_rename_directory_to_non_empty_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        dir1 = self._create_directory_and_get_directory_client("dir1")
        dir1.create_sub_directory("subdir")

        dir2 = self._create_directory_and_get_directory_client("dir2")
        dir2.rename_directory(dir1.file_system_name + '/' + dir1.path_name)

        with pytest.raises(HttpResponseError):
            dir2.get_directory_properties()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_dir_with_file_system_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        token = self.generate_sas(
            generate_file_system_sas,
            self.dsc.account_name,
            self.file_system_name,
            self.dsc.credential.account_key,
            FileSystemSasPermissions(write=True, read=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        dir_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, "olddir", credential=token)
        dir_client.create_directory()
        new_client = dir_client.rename_directory(dir_client.file_system_name + '/' + 'newdir')

        new_client.get_directory_properties()
        assert new_client.path_name == "newdir"

    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_directory_special_chars(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        dir_client = self._create_directory_and_get_directory_client('olddir')
        new_client = dir_client.rename_directory(dir_client.file_system_name + '/' + '?!@#$%^&*.?test')
        new_props = new_client.get_directory_properties()

        assert new_props.name == '?!@#$%^&*.?test'

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_properties(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        properties = directory_client.get_directory_properties()
        # Assert
        assert properties
        assert properties.metadata is not None
        assert properties.metadata['hello'] == metadata['hello']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_directory_encryption_scope_from_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        url = self.account_url(datalake_storage_account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=datalake_storage_account_key, logging_enable=True)
        self.config = self.dsc._config
        self.file_system_name = self.get_resource_name('filesystem')
        dir_name = 'testdir'
        file_system = self.dsc.get_file_system_client(self.file_system_name)
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        file_system.create_file_system(encryption_scope_options=encryption_scope)
        file_system.create_directory(dir_name)

        directory_client = file_system.get_directory_client(dir_name)
        props = directory_client.get_directory_properties()

        # Assert
        assert props
        assert props['encryption_scope'] is not None
        assert props['encryption_scope'] == encryption_scope.default_encryption_scope

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_using_directory_sas_to_read(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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

        assert access_control is not None

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_using_directory_sas_to_create(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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
        assert response is not None

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_using_directory_sas_to_create_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

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

        with pytest.raises(HttpResponseError):
            directory_client.delete_directory()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_using_directory_sas_to_create_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        newest_api_version = _SUPPORTED_API_VERSIONS[-1]

        service_client = DataLakeServiceClient("https://abc.dfs.core.windows.net", credential='fake')
        filesys_client = service_client.get_file_system_client("filesys")
        dir_client = DataLakeDirectoryClient("https://abc.dfs.core.windows.net", "filesys", "dir", credential='fake')
        file_client = dir_client.get_file_client("file")
        assert service_client.api_version == newest_api_version
        assert filesys_client.api_version == newest_api_version
        assert dir_client.api_version == newest_api_version
        assert file_client.api_version == newest_api_version
        
        service_client2 = DataLakeServiceClient("https://abc.dfs.core.windows.net", credential='fake', api_version="2019-02-02")
        filesys_client2 = service_client2.get_file_system_client("filesys")
        dir_client2 = DataLakeDirectoryClient("https://abc.dfs.core.windows.net", "filesys", "dir", credential='fake', api_version="2019-02-02")
        file_client2 = dir_client2.get_file_client("file")
        assert service_client2.api_version == "2019-02-02"
        assert filesys_client2.api_version == "2019-02-02"
        assert dir_client2.api_version == "2019-02-02"
        assert file_client2.api_version == "2019-02-02"

    @DataLakePreparer()
    @recorded_by_proxy
    def test_storage_account_audience_dir_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        # Act
        token_credential = self.get_credential(DataLakeServiceClient)
        directory_client = DataLakeDirectoryClient(
            self.dsc.url, self.file_system_name, directory_name,
            credential=token_credential,
            audience=f'https://{datalake_storage_account_name}.blob.core.windows.net/'
        )

        # Assert
        response1 = directory_client.exists()
        response2 = directory_client.create_sub_directory('testsubdir')
        assert response1 is not None
        assert response2 is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_bad_audience_dir_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        # Act
        token_credential = self.get_credential(DataLakeServiceClient)
        directory_client = DataLakeDirectoryClient(
            self.dsc.url, self.file_system_name, directory_name,
            credential=token_credential, audience=f'https://badaudience.blob.core.windows.net/'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        directory_client.exists()
        directory_client.create_sub_directory('testsubdir')

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
