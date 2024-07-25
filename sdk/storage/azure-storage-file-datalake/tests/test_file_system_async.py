# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import unittest
import uuid
from datetime import datetime, timedelta
from time import sleep

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceNotFoundError
from azure.storage.filedatalake import (
    AccessPolicy,
    AccountSasPermissions,
    DirectorySasPermissions,
    EncryptionScopeOptions,
    FileSystemSasPermissions,
    generate_account_sas,
    generate_directory_sas,
    generate_file_sas,
    generate_file_system_sas,
    PublicAccess,
    ResourceTypes
)
from azure.storage.filedatalake.aio import DataLakeDirectoryClient, DataLakeFileClient, DataLakeServiceClient, FileSystemClient
from azure.storage.filedatalake._models import FileSasPermissions

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import DataLakePreparer

# ------------------------------------------------------------------------------
TEST_FILE_SYSTEM_PREFIX = 'filesystem'
# ------------------------------------------------------------------------------


class TestFileSystemAsync(AsyncStorageRecordedTestCase):
    def _setUp(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=account_key, logging_enable=True)
        self.config = self.dsc._config
        self.test_file_systems = []

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                for file_system in self.test_file_systems:
                    loop.run_until_complete(self.dsc.delete_file_system(file_system))
                loop.run_until_complete(self.fsc.__aexit__())
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_file_system_reference(self, prefix=TEST_FILE_SYSTEM_PREFIX):
        file_system_name = self.get_resource_name(prefix)
        self.test_file_systems.append(file_system_name)
        return file_system_name

    async def _create_file_system(self, file_system_prefix=TEST_FILE_SYSTEM_PREFIX):
        return await self.dsc.create_file_system(self._get_file_system_reference(prefix=file_system_prefix))

    async def _to_list(self, async_iterator):
        result = []
        async for item in async_iterator:
            result.append(item)
        return result

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
    @recorded_by_proxy_async
    async def test_create_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = await file_system_client.create_file_system()

        # Assert
        assert created

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_system_async_extra_backslash(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name + '/')
        created = await file_system_client.create_file_system()

        # Assert
        assert created

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_system_encryption_scope(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        await file_system_client.create_file_system(encryption_scope_options=encryption_scope)
        props = await file_system_client.get_file_system_properties()

        # Assert
        assert props
        assert props['encryption_scope'] is not None
        assert props['encryption_scope'].default_encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_system_encryption_scope_account_sas(self, **kwargs):
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
        await file_system_client.create_file_system(encryption_scope_options=encryption_scope)

        fsc_sas = FileSystemClient(url, file_system_name, token)
        await fsc_sas.create_file('file1')
        await fsc_sas.create_directory('dir1')
        dir_props = await fsc_sas.get_directory_client('dir1').get_directory_properties()
        file_props = await fsc_sas.get_file_client('file1').get_file_properties()

        # Assert
        assert dir_props
        assert dir_props.encryption_scope is not None
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope
        assert file_props
        assert file_props.encryption_scope is not None
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_system_encryption_scope_file_system_sas(self, **kwargs):
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
        await file_system_client.create_file_system(encryption_scope_options=encryption_scope)

        fsc_sas = FileSystemClient(url, file_system_name, token)
        await fsc_sas.create_file('file1')
        await fsc_sas.create_directory('dir1')
        dir_props = await fsc_sas.get_directory_client('dir1').get_directory_properties()
        file_props = await fsc_sas.get_file_client('file1').get_file_properties()

        # Assert
        assert dir_props
        assert dir_props.encryption_scope is not None
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope
        assert file_props
        assert file_props.encryption_scope is not None
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_system_encryption_scope_directory_sas(self, **kwargs):
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
        await file_system_client.create_file_system(encryption_scope_options=encryption_scope)

        dir_client = DataLakeDirectoryClient(url, file_system_name, 'dir1', credential=token)
        await dir_client.create_directory()
        dir_props = await dir_client.get_directory_properties()

        # Assert
        assert dir_props
        assert dir_props.encryption_scope is not None
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_system_encryption_scope_file_sas(self, **kwargs):
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
        await file_system_client.create_file_system(encryption_scope_options=encryption_scope)
        await file_system_client.create_directory('dir1')

        file_client = DataLakeFileClient(url, file_system_name, 'dir1/file1', token)
        await file_client.create_file()
        file_props = await file_client.get_file_properties()

        # Assert
        assert file_props
        assert file_props.encryption_scope is not None
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_file_system_exists(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client1 = self.dsc.get_file_system_client(file_system_name)
        file_system_client2 = self.dsc.get_file_system_client("nonexistentfs")
        await file_system_client1.create_file_system()

        assert await file_system_client1.exists()
        assert not await file_system_client2.exists()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_system_with_metadata_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = await file_system_client.create_file_system(metadata=metadata)

        # Assert
        properties = await file_system_client.get_file_system_properties()
        assert created
        assert properties.metadata == metadata

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_file_systems(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = await self.dsc.create_file_system(file_system_name)

        # Act
        file_systems = []
        async for filesystem in self.dsc.list_file_systems():
            file_systems.append(filesystem)

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        assert file_systems[0].has_immutability_policy is not None
        assert file_systems[0].has_legal_hold is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_file_systems_encryption_scope(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name1 = self._get_file_system_reference(prefix='es')
        file_system_name2 = self._get_file_system_reference(prefix='es2')
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")
        await self.dsc.create_file_system(file_system_name1, encryption_scope_options=encryption_scope)
        await self.dsc.create_file_system(file_system_name2, encryption_scope_options=encryption_scope)

        # Act
        file_systems = []
        async for filesystem in self.dsc.list_file_systems():
            if filesystem['name'] in [file_system_name1, file_system_name2]:
                file_systems.append(filesystem)

        # Assert
        assert file_systems is not None
        assert len(file_systems) == 2
        assert file_systems[0].encryption_scope.default_encryption_scope == encryption_scope.default_encryption_scope
        assert file_systems[1].encryption_scope.default_encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_file_systems_account_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = await self.dsc.create_file_system(file_system_name)
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
        file_systems = []
        async for filesystem in dsc.list_file_systems():
            file_systems.append(filesystem)

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_delete_file_system_with_existing_file_system_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()

        # Act
        deleted = await file_system.delete_file_system()

        # Assert
        assert deleted is None

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        filesystem1 = await self.dsc.create_file_system(old_name1)
        await self.dsc.create_file_system(old_name2)

        new_filesystem = await self.dsc._rename_file_system(name=old_name1, new_name=new_name)
        with pytest.raises(HttpResponseError):
            await self.dsc._rename_file_system(name=old_name2, new_name=new_name)
        with pytest.raises(HttpResponseError):
            await filesystem1.get_file_system_properties()
        with pytest.raises(HttpResponseError):
            await self.dsc._rename_file_system(name="badfilesystem", new_name="filesystem")
        props = await new_filesystem.get_file_system_properties()
        assert new_name == props.name

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_system_with_file_system_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        bad_name = self._get_file_system_reference(prefix="badcontainer")
        filesystem1 = await self.dsc.create_file_system(old_name1)
        file_system2 = await self.dsc.create_file_system(old_name2)
        bad_file_system = self.dsc.get_file_system_client(bad_name)

        new_filesystem = await filesystem1._rename_file_system(new_name=new_name)
        with pytest.raises(HttpResponseError):
            await file_system2._rename_file_system(new_name=new_name)
        with pytest.raises(HttpResponseError):
            await filesystem1.get_file_system_properties()
        with pytest.raises(HttpResponseError):
            await bad_file_system._rename_file_system(new_name="filesystem")
        new_file_system_props = await new_filesystem.get_file_system_properties()
        assert new_name == new_file_system_props.name

    @pytest.mark.skip(reason="Feature not yet enabled. Make sure to record this test once enabled.")
    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_system_with_source_lease(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name = self._get_file_system_reference(prefix="old")
        new_name = self._get_file_system_reference(prefix="new")
        filesystem = await self.dsc.create_file_system(old_name)
        filesystem_lease_id = await filesystem.acquire_lease()
        with pytest.raises(HttpResponseError):
            await self.dsc._rename_file_system(name=old_name, new_name=new_name)
        with pytest.raises(HttpResponseError):
            await self.dsc._rename_file_system(name=old_name, new_name=new_name, lease="bad_id")
        new_filesystem = await self.dsc._rename_file_system(name=old_name, new_name=new_name, lease=filesystem_lease_id)
        props = await new_filesystem.get_file_system_properties()
        assert new_name == props.name

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_undelete_file_system(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        name = self._get_file_system_reference(prefix="filesystem2")
        filesystem_client = await self.dsc.create_file_system(name)

        await filesystem_client.delete_file_system()
        if self.is_live:
            sleep(30)
        # to make sure the filesystem deleted
        with pytest.raises(ResourceNotFoundError):
            await filesystem_client.get_file_system_properties()

        filesystem_list = []
        async for fs in self.dsc.list_file_systems(include_deleted=True):
            filesystem_list.append(fs)
        assert len(filesystem_list) >= 1

        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = await self.dsc.undelete_file_system(filesystem.name, filesystem.deleted_version)

                # to make sure the deleted filesystem is restored
                props = await restored_fs_client.get_file_system_properties()
                assert props is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_restore_file_system_with_sas(self, **kwargs):
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
        name = self._get_file_system_reference(prefix="filesystem2")
        filesystem_client = await dsc.create_file_system(name)
        await filesystem_client.delete_file_system()
        if self.is_live:
            sleep(30)
        # to make sure the filesystem is deleted
        with pytest.raises(ResourceNotFoundError):
            await filesystem_client.get_file_system_properties()

        filesystem_list = []
        async for fs in self.dsc.list_file_systems(include_deleted=True):
            filesystem_list.append(fs)
        assert len(filesystem_list) >= 1

        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = await dsc.undelete_file_system(filesystem.name, filesystem.deleted_version)

                # to make sure the deleted filesystem is restored
                props = await restored_fs_client.get_file_system_properties()
                assert props is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_delete_none_existing_file_system_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        fake_file_system_client = self.dsc.get_file_system_client("fakeclient")

        # Act
        with pytest.raises(ResourceNotFoundError):
            await fake_file_system_client.delete_file_system(match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_file_systems_with_include_metadata_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        metadata = {'hello': 'world', 'number': '42'}
        await file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = []
        async for fs in self.dsc.list_file_systems(name_starts_with=file_system.file_system_name,
                                                   include_metadata=True):
            file_systems.append(fs)

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        assert file_systems[0].metadata == metadata

    @pytest.mark.playback_test_only
    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_set_file_system_acl(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Act
        file_system = await self._create_file_system()
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        access_policy = AccessPolicy(permission=FileSystemSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifier1 = {'testid': access_policy}
        response = await file_system.set_file_system_access_policy(
            signed_identifier1, public_access=PublicAccess.FileSystem)

        assert response.get('etag') is not None
        assert response.get('last_modified') is not None

        acl1 = await file_system.get_file_system_access_policy()
        assert acl1['public_access'] is not None
        assert len(acl1['signed_identifiers']) == 1

        # If set signed identifier without specifying the access policy then it will be default to None
        signed_identifier2 = {'testid': access_policy, 'test2': access_policy}
        await file_system.set_file_system_access_policy(signed_identifier2)
        acl2 = await file_system.get_file_system_access_policy()
        assert acl2['public_access'] is None
        assert len(acl2['signed_identifiers']) == 2

        return variables

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_file_systems_by_page(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        for i in range(0, 6):
            await self._create_file_system(file_system_prefix="filesystem{}".format(i))

        # Act
        file_systems = []
        async for fs in await self.dsc.list_file_systems(
                results_per_page=3,
                name_starts_with="file",
                include_metadata=True).by_page().__anext__():
            file_systems.append(fs)

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 3

    @pytest.mark.playback_test_only
    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_file_systems_with_public_access_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.get_file_system_client(file_system_name)
        await file_system.create_file_system(public_access="blob")
        metadata = {'hello': 'world', 'number': '42'}
        await file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = []
        async for fs in self.dsc.list_file_systems(name_starts_with=file_system.file_system_name,
                                                   include_metadata=True):
            file_systems.append(fs)

        # Assert
        assert file_systems is not None
        assert len(file_systems) >= 1
        assert file_systems[0] is not None
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        assert file_systems[0].metadata == metadata
        assert file_systems[0].public_access is PublicAccess.File

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_get_file_system_properties(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system = await self._create_file_system()
        await file_system.set_file_system_metadata(metadata)

        # Act
        props = await file_system.get_file_system_properties()

        # Assert
        assert props is not None
        assert props.metadata == metadata
        assert props.has_immutability_policy is not None
        assert props.has_legal_hold is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_service_client_session_closes_after_filesystem_creation(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        dsc2 = DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key)
        async with DataLakeServiceClient(
                self.dsc.url, credential=datalake_storage_account_key) as ds_client:
            fs1 = await ds_client.create_file_system(self._get_file_system_reference(prefix="fs1"))
            await fs1.delete_file_system()
        await dsc2.create_file_system(self._get_file_system_reference(prefix="fs2"))
        await dsc2.close()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))

        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        assert len(paths) == 6

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths_create_expiry(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        variables = kwargs.pop('variables', {})

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        file_client = await file_system.create_file('file1')

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(days=1))
        await file_client.set_file_expiry("Absolute", expires_on=expiry_time)

        # Act
        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        # Assert
        assert 1 == len(paths)
        props = await file_client.get_file_properties()
        # Properties do not include microseconds so let them vary by 1 second
        self._is_almost_equal(props.creation_time, paths[0].creation_time, delta=timedelta(seconds=1))
        self._is_almost_equal(props.expiry_time, paths[0].expiry_time, delta=timedelta(seconds=1))

        return variables

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths_no_expiry(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        await file_system.create_file('file1')

        # Act
        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        # Assert
        assert 1 == len(paths)
        assert paths[0].expiry_time is None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths_which_are_all_files_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_file("file{}".format(i))

        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        assert len(paths) == 6

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_system_filesystems(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        dsc = DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key)
        # Act
        filesystems = []
        async for fs in dsc.list_file_systems(include_system=True):
            filesystems.append(fs)
        # Assert
        found = False
        for fs in filesystems:
            if fs.name == "$logs":
                found = True
        assert found == True

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths_with_max_per_page_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))

        generator1 = file_system.get_paths(max_results=2, upn=True).by_page()
        paths1 = []
        async for path in await generator1.__anext__():
            paths1.append(path)

        generator2 = file_system.get_paths(max_results=4, upn=True) \
            .by_page(continuation_token=generator1.continuation_token)
        paths2 = []
        async for path in await generator2.__anext__():
            paths2.append(path)

        assert len(paths1) == 2
        assert len(paths2) == 4
        assert paths2[0].name == "dir12"

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths_under_specific_path_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            dir = await file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = await dir.create_sub_directory("subdir")
            await subdir.create_sub_directory("subsub")

            # create a file under the current directory
            file_client = await subdir.create_file("file")
            await file_client.append_data(b"abced", 0, 5) # cspell:disable-line
            await file_client.flush_data(5)

        generator1 = file_system.get_paths(path="dir10/subdir", max_results=2, upn=True).by_page()
        paths = []
        async for path in await generator1.__anext__():
            paths.append(path)

        assert len(paths) == 2
        assert paths[0].content_length == 5

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths_recursively(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            dir = await file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = await dir.create_sub_directory("subdir")
            await subdir.create_sub_directory("subsub")

            # create a file under the current directory
            await subdir.create_file("file")

        paths = []
        async for path in file_system.get_paths(recursive=True, upn=True):
            paths.append(path)

        # there are 24 subpaths in total
        assert len(paths) == 24

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_list_paths_pages_correctly(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system(file_system_prefix="filesystem1")
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))
        for i in range(0, 6):
            await file_system.create_file("file{}".format(i))

        generator = file_system.get_paths(max_results=6, upn=True).by_page()
        paths1 = []
        async for path in await generator.__anext__():
            paths1.append(path)
        paths2 = []
        async for path in await generator.__anext__():
            paths2.append(path)

        with pytest.raises(StopAsyncIteration):
            paths3 = []
            async for path in await generator.__anext__():
                paths3.append(path)

        assert len(paths1) == 6
        assert len(paths2) == 6

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_get_deleted_paths(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        file0 = await file_system.create_file("file0")
        file1 = await file_system.create_file("file1")

        dir1 = await file_system.create_directory("dir1")
        dir2 = await file_system.create_directory("dir2")
        dir3 = await file_system.create_directory("dir3")
        file_in_dir3 = await dir3.create_file("file_in_dir3")
        file_in_subdir = await dir3.create_file("subdir/file_in_subdir")

        await file0.delete_file()
        await file1.delete_file()
        await dir1.delete_directory()
        await dir2.delete_directory()
        await file_in_dir3.delete_file()
        await file_in_subdir.delete_file()
        deleted_paths = []
        async for path in file_system.list_deleted_paths():
            deleted_paths.append(path)
        dir3_paths = []
        async for path in file_system.list_deleted_paths(path_prefix="dir3/"):
            dir3_paths.append(path)

        # Assert
        assert len(deleted_paths) == 6
        assert len(dir3_paths) == 2
        assert dir3_paths[0].deletion_id is not None
        assert dir3_paths[1].deletion_id is not None
        assert dir3_paths[0].name == 'dir3/file_in_dir3'
        assert dir3_paths[1].name == 'dir3/subdir/file_in_subdir'

        paths_generator1 = file_system.list_deleted_paths(results_per_page=2).by_page()
        paths1 = []
        async for path in await paths_generator1.__anext__():
            paths1.append(path)

        paths_generator2 = file_system.list_deleted_paths(results_per_page=4) \
            .by_page(continuation_token=paths_generator1.continuation_token)
        paths2 = []
        async for path in await paths_generator2.__anext__():
            paths2.append(path)

        # Assert
        assert len(paths1) == 2
        assert len(paths2) == 4

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_path_properties_encryption_scope(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        await file_system_client.create_file_system(encryption_scope_options=encryption_scope)
        await file_system_client.create_directory('dir1')
        await file_system_client.create_file('dir1/file1')

        dir_props = await file_system_client.get_directory_client('dir1').get_directory_properties()
        file_props = await file_system_client.get_file_client('dir1/file1').get_file_properties()
        paths = []
        async for path in file_system_client.get_paths(recursive=True, upn=True):
            paths.append(path)

        # Assert
        assert dir_props.encryption_scope == encryption_scope.default_encryption_scope
        assert file_props.encryption_scope == encryption_scope.default_encryption_scope
        assert paths
        assert paths[0].encryption_scope is not None
        assert paths[0].encryption_scope == encryption_scope.default_encryption_scope

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_directory_from_file_system_client_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        await file_system.create_directory("dir1/dir2")

        paths = []
        async for path in file_system.get_paths(recursive=False, upn=True):
            paths.append(path)

        assert len(paths) == 1
        assert paths[0].name == "dir1"

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_from_file_system_client_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        await file_system.create_file("dir1/dir2/file")

        paths = []
        async for path in file_system.get_paths(recursive=True, upn=True):
            paths.append(path)
        assert len(paths) == 3
        assert paths[0].name == "dir1"
        assert paths[2].is_directory == False

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_get_root_directory_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system = await self._create_file_system()
        directory_client = file_system._get_root_directory_client()

        acl = 'user::rwx,group::r-x,other::rwx'
        await directory_client.set_access_control(acl=acl)
        access_control = await directory_client.get_access_control()

        assert acl == access_control['acl']

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_get_access_control_using_delegation_sas_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        url = self.account_url(datalake_storage_account_name, 'dfs')
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        dsc = DataLakeServiceClient(url, token_credential, logging_enable=True)
        file_system_name = self._get_file_system_reference()
        directory_client_name = '/'
        (await dsc.create_file_system(file_system_name)).get_directory_client(directory_client_name)

        directory_client = self.dsc.get_directory_client(file_system_name, directory_client_name)
        random_guid = uuid.uuid4()
        await directory_client.set_access_control(owner=random_guid,
                                                  permissions='0777')
        acl = await directory_client.get_access_control()

        delegation_key = await dsc.get_user_delegation_key(datetime.utcnow(),
                                                           datetime.utcnow() + timedelta(hours=1))

        token = self.generate_sas(
            generate_file_system_sas,
            dsc.account_name,
            file_system_name,
            delegation_key,
            permission=FileSystemSasPermissions(
                read=True, execute=True, manage_access_control=True, manage_ownership=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            agent_object_id=random_guid
        )
        sas_directory_client = DataLakeDirectoryClient(self.dsc.url, file_system_name, directory_client_name,
                                                       credential=token, logging_enable=True)
        access_control = await sas_directory_client.get_access_control()

        assert access_control is not None

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_list_paths_using_file_sys_delegation_sas_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self.account_url(datalake_storage_account_name, 'dfs')
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        dsc = DataLakeServiceClient(url, token_credential)
        file_system_name = self._get_file_system_reference()
        directory_client_name = '/'
        directory_client = (await dsc.create_file_system(file_system_name)).get_directory_client(directory_client_name)

        random_guid = uuid.uuid4()
        await directory_client.set_access_control(owner=random_guid, permissions='0777')

        delegation_key = await dsc.get_user_delegation_key(datetime.utcnow(),
                                                           datetime.utcnow() + timedelta(hours=1))

        token = self.generate_sas(
            generate_file_system_sas,
            dsc.account_name,
            file_system_name,
            delegation_key,
            permission=DirectorySasPermissions(list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            agent_object_id=random_guid
        )
        sas_directory_client = FileSystemClient(self.dsc.url, file_system_name,
                                                credential=token)
        paths = list()
        async for path in sas_directory_client.get_paths():
            paths.append(path)

        assert 0 == 0

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_file_system_sessions_closes_properly_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_client = await self._create_file_system("fs")
        async with file_system_client as fs_client:
            async with fs_client.get_file_client("file1.txt") as f_client:
                await f_client.create_file()
            async with fs_client.get_file_client("file2.txt") as f_client:
                await f_client.create_file()
            async with fs_client.get_directory_client("file1") as f_client:
                await f_client.create_directory()
            async with fs_client.get_directory_client("file2") as f_client:
                await f_client.create_directory()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_undelete_dir_with_version_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system_client = await self._create_file_system("fs2")
        dir_path = 'dir10'
        dir_client = await file_system_client.create_directory(dir_path)
        resp = await dir_client.delete_directory()
        with pytest.raises(HttpResponseError):
            await file_system_client.get_file_client(dir_path).get_file_properties()
        restored_dir_client = await file_system_client._undelete_path(dir_path, resp['deletion_id'])
        resp = await restored_dir_client.get_directory_properties()
        assert resp is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_undelete_file_with_version_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("storage_data_lake_soft_delete_account_name")
        datalake_storage_account_key = kwargs.pop("storage_data_lake_soft_delete_account_key")

        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system_client = await self._create_file_system("fs2")
        file_path = 'dir10/fileŇ'
        dir_client = await file_system_client.create_file(file_path)
        resp = await dir_client.delete_file()
        with pytest.raises(HttpResponseError):
            await file_system_client.get_file_client(file_path).get_file_properties()
        restored_file_client = await file_system_client._undelete_path(file_path, resp['deletion_id'])
        resp = await restored_file_client.get_file_properties()
        assert resp is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_storage_account_audience_service_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self.account_url(datalake_storage_account_name, 'dfs')
        file_system_name = self._get_file_system_reference()
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        await file_system_client.create_file_system()
        await file_system_client.create_directory('testdir1')

        # Act
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        fsc = FileSystemClient(
            url, file_system_name,
            credential=token_credential,
            audience=f'https://{datalake_storage_account_name}.blob.core.windows.net/'
        )

        # Assert
        response1 = await fsc.exists()
        response2 = await fsc.create_directory('testdir11')
        assert response1 is not None
        assert response2 is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_bad_audience_service_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self.account_url(datalake_storage_account_name, 'dfs')
        file_system_name = self._get_file_system_reference()
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        await file_system_client.create_file_system()
        await file_system_client.create_directory('testdir2')

        # Act
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        fsc = FileSystemClient(
            url, file_system_name,
            credential=token_credential,
            audience=f'https://badaudience.blob.core.windows.net/'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        await fsc.exists()
        await fsc.create_directory('testdir22')

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
