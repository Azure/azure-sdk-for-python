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
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceNotFoundError
from azure.storage.filedatalake import (
    AccessPolicy,
    AccountSasPermissions,
    DataLakeDirectoryClient,
    DataLakeFileClient,
    DataLakeServiceClient,
    EncryptionScopeOptions,
    FileSystemClient,
    FileSystemSasPermissions,
    generate_account_sas,
    generate_directory_sas,
    generate_file_sas,
    generate_file_system_sas,
    PublicAccess,
    ResourceTypes
)
from azure.storage.filedatalake._models import FileSasPermissions

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import DataLakePreparer

# ------------------------------------------------------------------------------
TEST_FILE_SYSTEM_PREFIX = 'filesystem'
# ------------------------------------------------------------------------------


class TestFileSystem(StorageRecordedTestCase):
    def _setUp(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, account_key)
        self.config = self.dsc._config
        self.test_file_systems = []

    def tearDown(self):
        if not self.is_playback():
            try:
                for file_system in self.test_file_systems:
                    self.dsc.delete_file_system(file_system)
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_file_system_reference(self, prefix=TEST_FILE_SYSTEM_PREFIX):
        file_system_name = self.get_resource_name(prefix)
        self.test_file_systems.append(file_system_name)
        return file_system_name

    def _create_file_system(self, file_system_prefix=TEST_FILE_SYSTEM_PREFIX):
        try:
            return self.dsc.create_file_system(self._get_file_system_reference(prefix=file_system_prefix))
        except:
            pass

    def _is_almost_equal(self, first, second, delta):
        if first == second:
            return True
        diff = abs(first - second)
        if delta is not None:
            if diff <= delta:
                return True
        return False


    # --Test cases for file system ---------------------------------------------

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = file_system_client.create_file_system()

        # Assert
        assert created

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system_extra_backslash(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name + '/')
        created = file_system_client.create_file_system()

        # Assert
        assert created

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system_encryption_scope(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system(encryption_scope_options=encryption_scope)
        props = file_system_client.get_file_system_properties()

        # Assert
        assert props
        assert props['encryption_scope'] is not None
        assert props['encryption_scope'].default_encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system_encryption_scope_account_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        url = self.account_url(datalake_storage_account_name, 'dfs')
        token = self.generate_sas(
            generate_account_sas,
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(service=True, file_system=True, object=True),
            permission=AccountSasPermissions(write=True, read=True, create=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=5),
            encryption_scope="hnstestscope1")
        file_system_name = self._get_file_system_reference()
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system(encryption_scope_options=encryption_scope)

        fsc_sas = FileSystemClient(url, file_system_name, token)
        fsc_sas.create_file('file1')
        fsc_sas.create_directory('dir1')
        dir_props = fsc_sas.get_directory_client('dir1').get_directory_properties()
        file_props = fsc_sas.get_file_client('file1').get_file_properties()

        # Assert
        assert dir_props
        assert dir_props.encryption_scope is not None
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope
        assert file_props
        assert file_props.encryption_scope is not None
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system_encryption_scope_file_system_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        url = self.account_url(datalake_storage_account_name, 'dfs')
        file_system_name = self._get_file_system_reference()
        token = self.generate_sas(
            generate_file_system_sas,
            self.dsc.account_name,
            file_system_name,
            self.dsc.credential.account_key,
            permission=FileSystemSasPermissions(write=True, read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=5),
            encryption_scope="hnstestscope1")
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system(encryption_scope_options=encryption_scope)

        fsc_sas = FileSystemClient(url, file_system_name, token)
        fsc_sas.create_file('file1')
        fsc_sas.create_directory('dir1')
        dir_props = fsc_sas.get_directory_client('dir1').get_directory_properties()
        file_props = fsc_sas.get_file_client('file1').get_file_properties()

        # Assert
        assert dir_props
        assert dir_props.encryption_scope is not None
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope
        assert file_props
        assert file_props.encryption_scope is not None
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system_encryption_scope_directory_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        url = self.account_url(datalake_storage_account_name, 'dfs')
        file_system_name = self._get_file_system_reference()
        token = self.generate_sas(
            generate_directory_sas,
            self.dsc.account_name,
            file_system_name,
            'dir1',
            self.dsc.credential.account_key,
            permission=FileSasPermissions(write=True, read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=5),
            encryption_scope="hnstestscope1")
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system(encryption_scope_options=encryption_scope)

        dir_client = DataLakeDirectoryClient(url, file_system_name, 'dir1', credential=token)
        dir_client.create_directory()
        dir_props = dir_client.get_directory_properties()

        # Assert
        assert dir_props
        assert dir_props.encryption_scope is not None
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system_encryption_scope_file_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        url = self.account_url(datalake_storage_account_name, 'dfs')
        file_system_name = self._get_file_system_reference()
        token = self.generate_sas(
            generate_file_sas,
            self.dsc.account_name,
            file_system_name,
            'dir1',
            'file1',
            self.dsc.credential.account_key,
            permission=FileSasPermissions(write=True, read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=5),
            encryption_scope="hnstestscope1")
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system(encryption_scope_options=encryption_scope)
        file_system_client.create_directory('dir1')

        file_client = DataLakeFileClient(url, file_system_name, 'dir1/file1', token)
        file_client.create_file()
        file_props = file_client.get_file_properties()

        # Assert
        assert file_props
        assert file_props.encryption_scope is not None
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy
    def test_file_system_exists(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client1 = self.dsc.get_file_system_client(file_system_name)
        file_system_client2 = self.dsc.get_file_system_client("nonexistentfs")
        file_system_client1.create_file_system()

        assert file_system_client1.exists()
        assert not file_system_client2.exists()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_system_with_metadata(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = file_system_client.create_file_system(metadata=metadata)

        # Assert
        meta = file_system_client.get_file_system_properties().metadata
        assert created
        assert meta == metadata

    @pytest.mark.playback_test_only
    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_file_system_acl(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Act
        file_system = self._create_file_system()
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        access_policy = AccessPolicy(permission=FileSystemSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifier1 = {'testid': access_policy}
        response = file_system.set_file_system_access_policy(signed_identifier1, public_access=PublicAccess.FileSystem)

        assert response.get('etag') is not None
        assert response.get('last_modified') is not None
        acl1 = file_system.get_file_system_access_policy()
        assert acl1['public_access'] is not None
        assert len(acl1['signed_identifiers']) == 1

        # If set signed identifier without specifying the access policy then it will be default to None
        signed_identifier2 = {'testid': access_policy, 'test2': access_policy}
        file_system.set_file_system_access_policy(signed_identifier2)
        acl2 = file_system.get_file_system_access_policy()
        assert acl2['public_access'] is None
        assert len(acl2['signed_identifiers']) == 2

        return variables

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_file_systems(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.create_file_system(file_system_name)

        # Act
        file_systems = list(self.dsc.list_file_systems())

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        assert file_systems[0].has_immutability_policy is not None
        assert file_systems[0].has_legal_hold is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_file_systems_encryption_scope(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name1 = self._get_file_system_reference(prefix='es')
        file_system_name2 = self._get_file_system_reference(prefix='es2')
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")
        self.dsc.create_file_system(file_system_name1, encryption_scope_options=encryption_scope)
        self.dsc.create_file_system(file_system_name2, encryption_scope_options=encryption_scope)

        # Act
        file_systems = []
        for filesystem in self.dsc.list_file_systems():
            if filesystem['name'] in [file_system_name1, file_system_name2]:
                file_systems.append(filesystem)

        # Assert
        assert file_systems is not None
        assert len(file_systems) == 2
        assert file_systems[0].encryption_scope.default_encryption_scope == encryption_scope.default_encryption_scope
        assert file_systems[1].encryption_scope.default_encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_file_systems_account_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.create_file_system(file_system_name)
        sas_token = self.generate_sas(
            generate_account_sas,
            datalake_storage_account_name,
            datalake_storage_account_key,
            ResourceTypes(service=True),
            AccountSasPermissions(list=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        dsc = DataLakeServiceClient(self.account_url(datalake_storage_account_name, 'dfs'), credential=sas_token)
        file_systems = list(dsc.list_file_systems())

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        filesystem1 = self.dsc.create_file_system(old_name1)
        self.dsc.create_file_system(old_name2)

        new_filesystem = self.dsc._rename_file_system(name=old_name1, new_name=new_name)
        with pytest.raises(HttpResponseError):
            self.dsc._rename_file_system(name=old_name2, new_name=new_name)
        with pytest.raises(HttpResponseError):
            filesystem1.get_file_system_properties()
        with pytest.raises(HttpResponseError):
            self.dsc._rename_file_system(name="badfilesystem", new_name="filesystem")
        assert new_name == new_filesystem.get_file_system_properties().name

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_file_system_with_file_system_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        bad_name = self._get_file_system_reference(prefix="badcontainer")
        filesystem1 = self.dsc.create_file_system(old_name1)
        file_system2 = self.dsc.create_file_system(old_name2)
        bad_file_system = self.dsc.get_file_system_client(bad_name)

        new_filesystem = filesystem1._rename_file_system(new_name=new_name)
        with pytest.raises(HttpResponseError):
            file_system2._rename_file_system(new_name=new_name)
        with pytest.raises(HttpResponseError):
            filesystem1.get_file_system_properties()
        with pytest.raises(HttpResponseError):
            bad_file_system._rename_file_system(new_name="filesystem")
        assert new_name == new_filesystem.get_file_system_properties().name

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_system_filesystems(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        dsc = DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key)
        # Act
        filesystems = list(dsc.list_file_systems(include_system=True))

        # Assert
        found = False
        for fs in filesystems:
            if fs.name == "$logs":
                found = True
        assert found == True

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @DataLakePreparer()
    @recorded_by_proxy
    def test_rename_file_system_with_source_lease(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name = self._get_file_system_reference(prefix="old")
        new_name = self._get_file_system_reference(prefix="new")
        filesystem = self.dsc.create_file_system(old_name)
        filesystem_lease_id = filesystem.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        with pytest.raises(HttpResponseError):
            self.dsc._rename_file_system(name=old_name, new_name=new_name)
        with pytest.raises(HttpResponseError):
            self.dsc._rename_file_system(name=old_name, new_name=new_name, lease="bad_id")
        new_filesystem = self.dsc._rename_file_system(name=old_name, new_name=new_name, lease=filesystem_lease_id)
        assert new_name == new_filesystem.get_file_system_properties().name

    @DataLakePreparer()
    @recorded_by_proxy
    def test_undelete_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        name = self._get_file_system_reference("testfs5")
        filesystem_client = self.dsc.create_file_system(name)

        # Act
        filesystem_client.delete_file_system()
        if self.is_live:
            sleep(30)
        # to make sure the filesystem deleted
        with pytest.raises(ResourceNotFoundError):
            filesystem_client.get_file_system_properties()

        filesystem_list = list(self.dsc.list_file_systems(include_deleted=True))
        assert len(filesystem_list) >= 1

        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = self.dsc.undelete_file_system(filesystem.name, filesystem.deleted_version)

                # to make sure the deleted filesystem is restored
                props = restored_fs_client.get_file_system_properties()
                assert props is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_restore_file_system_with_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        token = self.generate_sas(
            generate_account_sas,
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(service=True, file_system=True),
            AccountSasPermissions(read=True, write=True, list=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        dsc = DataLakeServiceClient(self.dsc.url, token)
        name = self._get_file_system_reference(prefix="filesystem9")
        filesystem_client = dsc.create_file_system(name)
        filesystem_client.delete_file_system()
        if self.is_live:
            sleep(30)
        # to make sure the filesystem is deleted
        with pytest.raises(ResourceNotFoundError):
            filesystem_client.get_file_system_properties()

        filesystem_list = list(dsc.list_file_systems(include_deleted=True))
        assert len(filesystem_list) >= 1

        restored_version = 0
        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = dsc.undelete_file_system(filesystem.name, filesystem.deleted_version)

                # to make sure the deleted filesystem is restored
                props = restored_fs_client.get_file_system_properties()
                assert props is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_delete_file_system_with_existing_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()

        # Act
        deleted = file_system.delete_file_system()

        # Assert
        assert deleted is None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_delete_none_existing_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        fake_file_system_client = self.dsc.get_file_system_client("fakeclient")

        # Act
        with pytest.raises(ResourceNotFoundError):
            fake_file_system_client.delete_file_system(match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_file_systems_with_include_metadata(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        metadata = {'hello': 'world', 'number': '42'}
        resp = file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = list(self.dsc.list_file_systems(
            name_starts_with=file_system.file_system_name,
            include_metadata=True))

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        assert file_systems[0].metadata == metadata

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_file_systems_by_page(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        for i in range(0, 6):
            self._create_file_system(file_system_prefix="filesystem{}".format(i))

        # Act
        file_systems = list(next(self.dsc.list_file_systems(
            results_per_page=3,
            name_starts_with="file",
            include_metadata=True).by_page()))

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 3

    @pytest.mark.playback_test_only
    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_file_systems_with_public_access(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.get_file_system_client(file_system_name)
        file_system.create_file_system(public_access="blob")
        metadata = {'hello': 'world', 'number': '42'}
        resp = file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = list(self.dsc.list_file_systems(
            name_starts_with=file_system.file_system_name,
            include_metadata=True))

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        assert file_systems[0].metadata == metadata
        assert file_systems[0].public_access is PublicAccess.File

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_file_system_properties(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system = self._create_file_system()
        file_system.set_file_system_metadata(metadata)

        # Act
        props = file_system.get_file_system_properties()

        # Assert
        assert props is not None
        assert props.metadata == metadata
        assert props.has_immutability_policy is not None
        assert props.has_legal_hold is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_service_client_session_closes_after_filesystem_creation(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        dsc2 = DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key)
        with DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key) as ds_client:
            fs1 = ds_client.create_file_system(self._get_file_system_reference(prefix="fs1"))
            fs1.delete_file_system()
        dsc2.create_file_system(self._get_file_system_reference(prefix="fs2"))
        dsc2.close()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

        paths = list(file_system.get_paths(upn=True))

        assert len(paths) == 6
        assert isinstance(paths[0].last_modified, datetime)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths_create_expiry(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_client = file_system.create_file('file1')

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(days=1))
        file_client.set_file_expiry("Absolute", expires_on=expiry_time)

        # Act
        paths = list(file_system.get_paths(upn=True))

        # Assert
        assert 1 == len(paths)
        props = file_client.get_file_properties()
        # Properties do not include microseconds so let them vary by 1 second
        self._is_almost_equal(props.creation_time, paths[0].creation_time, delta=timedelta(seconds=1))
        self._is_almost_equal(props.expiry_time, paths[0].expiry_time, delta=timedelta(seconds=1))

        return variables

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths_no_expiry(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_system.create_file('file1')

        # Act
        paths = list(file_system.get_paths(upn=True))

        # Assert
        assert 1 == len(paths)
        assert paths[0].expiry_time is None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_deleted_paths(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file0 = file_system.create_file("file0")
        file1 = file_system.create_file("file1")

        dir1 = file_system.create_directory("dir1")
        dir2 = file_system.create_directory("dir2")
        dir3 = file_system.create_directory("dir3")
        file_in_dir3 = dir3.create_file("file_in_dir3")
        file_in_subdir = dir3.create_file("subdir/file_in_subdir")

        file0.delete_file()
        file1.delete_file()
        dir1.delete_directory()
        dir2.delete_directory()
        file_in_dir3.delete_file()
        file_in_subdir.delete_file()
        deleted_paths = list(file_system.list_deleted_paths())
        dir3_paths = list(file_system.list_deleted_paths(path_prefix="dir3/"))

        # Assert
        assert len(deleted_paths) == 6
        assert len(dir3_paths) == 2
        assert dir3_paths[0].deletion_id is not None
        assert dir3_paths[1].deletion_id is not None
        assert dir3_paths[0].name == 'dir3/file_in_dir3'
        assert dir3_paths[1].name == 'dir3/subdir/file_in_subdir'

        paths_generator1 = file_system.list_deleted_paths(results_per_page=2).by_page()
        paths1 = list(next(paths_generator1))

        paths_generator2 = file_system.list_deleted_paths(results_per_page=4).by_page(
            continuation_token=paths_generator1.continuation_token)
        paths2 = list(next(paths_generator2))

        # Assert
        assert len(paths1) == 2
        assert len(paths2) == 4

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths_which_are_all_files(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_file("file{}".format(i))

        paths = list(file_system.get_paths(upn=True))

        assert len(paths) == 6

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths_with_max_per_page(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

        generator1 = file_system.get_paths(max_results=2, upn=True).by_page()
        paths1 = list(next(generator1))

        generator2 = file_system.get_paths(max_results=4, upn=True)\
            .by_page(continuation_token=generator1.continuation_token)
        paths2 = list(next(generator2))

        assert len(paths1) == 2
        assert len(paths2) == 4
        assert paths2[0].name == "dir12"

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths_under_specific_path(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = file_system.get_directory_client("dir1{}".format(i)).create_sub_directory("subdir")
            subdir.create_sub_directory("subsub")

            # create a file under the current directory
            file_client = subdir.create_file("file")
            file_client.append_data(b"abced", 0, 5) # cspell:disable-line
            file_client.flush_data(5)

        generator1 = file_system.get_paths(path="dir10/subdir", max_results=2, upn=True).by_page()
        paths = list(next(generator1))

        assert len(paths) == 2
        assert paths[0].content_length == 5

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths_recursively(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = file_system.get_directory_client("dir1{}".format(i)).create_sub_directory("subdir")
            subdir.create_sub_directory("subsub")

            # create a file under the current directory
            subdir.create_file("file")

        paths = list(file_system.get_paths(recursive=True, upn=True))

        # there are 24 subpaths in total
        assert len(paths) == 24

    @DataLakePreparer()
    @recorded_by_proxy
    def test_list_paths_pages_correctly(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system(file_system_prefix="fs1")
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))
        for i in range(0, 6):
            file_system.create_file("file{}".format(i))

        generator = file_system.get_paths(max_results=6, upn=True).by_page()
        paths1 = list(next(generator))
        paths2 = list(next(generator))
        with pytest.raises(StopIteration):
            list(next(generator))

        assert len(paths1) == 6
        assert len(paths2) == 6

    @DataLakePreparer()
    @recorded_by_proxy
    def test_path_properties_encryption_scope(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system(encryption_scope_options=encryption_scope)
        file_system_client.create_directory('dir1')
        file_system_client.create_file('dir1/file1')

        dir_props = file_system_client.get_directory_client('dir1').get_directory_properties()
        file_props = file_system_client.get_file_client('dir1/file1').get_file_properties()
        paths = list(file_system_client.get_paths(recursive=False, upn=True))

        # Assert
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope
        assert paths
        assert paths[0].encryption_scope is not None
        assert paths[0].encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_from_file_system_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_system.create_directory("dir1/dir2")

        paths = list(file_system.get_paths(recursive=False, upn=True))

        assert len(paths) == 1
        assert paths[0].name == "dir1"

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_from_file_system_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_system.create_file("dir1/dir2/file")

        paths = list(file_system.get_paths(recursive=True, upn=True))

        assert len(paths) == 3
        assert paths[0].name == "dir1"
        assert paths[2].is_directory == False

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_root_directory_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system = self._create_file_system()
        directory_client = file_system._get_root_directory_client()

        acl = 'user::rwx,group::r-x,other::rwx'
        directory_client.set_access_control(acl=acl)
        access_control = directory_client.get_access_control()

        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_file_system_sessions_closes_properly(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_client = self._create_file_system("fenrhxsbfvsdvdsvdsadb") # cspell:disable-line
        with file_system_client as fs_client:
            with fs_client.get_file_client("file1.txt") as f_client:
                f_client.create_file()
            with fs_client.get_file_client("file2.txt") as f_client:
                f_client.create_file()
            with fs_client.get_directory_client("file1") as f_client:
                f_client.create_directory()
            with fs_client.get_directory_client("file2") as f_client:
                f_client.create_directory()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_undelete_dir_with_version_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system_client = self._create_file_system("fs2")
        if file_system_client is None:
            file_system_client = self.dsc.get_file_system_client(self._get_file_system_reference(prefix="fs2"))
        dir_path = 'dir10'
        dir_client = file_system_client.create_directory(dir_path)
        resp = dir_client.delete_directory()
        with pytest.raises(HttpResponseError):
            file_system_client.get_file_client(dir_path).get_file_properties()
        restored_dir_client = file_system_client._undelete_path(dir_path, resp['deletion_id'])
        resp = restored_dir_client.get_directory_properties()
        assert resp is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_undelete_file_with_version_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system_client = self._create_file_system("fs3")
        if file_system_client is None:
            file_system_client = self.dsc.get_file_system_client(self._get_file_system_reference(prefix="fs3"))
        file_path = 'dir10/file'
        dir_client = file_system_client.create_file(file_path)
        resp = dir_client.delete_file()
        with pytest.raises(HttpResponseError):
            file_system_client.get_file_client(file_path).get_file_properties()
        restored_file_client = file_system_client._undelete_path(file_path, resp['deletion_id'])
        resp = restored_file_client.get_file_properties()
        assert resp is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_storage_account_audience_service_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self.account_url(datalake_storage_account_name, 'dfs')
        file_system_name = self._get_file_system_reference()
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system()
        file_system_client.create_directory('testdir1')

        # Act
        token_credential = self.get_credential(DataLakeServiceClient)
        fsc = FileSystemClient(
            url, file_system_name,
            credential=token_credential,
            audience=f'https://{datalake_storage_account_name}.blob.core.windows.net/'
        )

        # Assert
        response1 = fsc.exists()
        response2 = fsc.create_directory('testdir11')
        assert response1 is not None
        assert response2 is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_bad_audience_service_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self.account_url(datalake_storage_account_name, 'dfs')
        file_system_name = self._get_file_system_reference()
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        file_system_client.create_file_system()
        file_system_client.create_directory('testdir2')

        # Act
        token_credential = self.get_credential(DataLakeServiceClient)
        fsc = FileSystemClient(
            url, file_system_name,
            credential=token_credential,
            audience=f'https://badaudience.blob.core.windows.net/'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        fsc.exists()
        fsc.create_directory('testdir22')

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
