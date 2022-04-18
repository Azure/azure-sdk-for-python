# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import unittest

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.filedatalake import CustomerProvidedEncryptionKey
from azure.storage.filedatalake.aio import DataLakeServiceClient
from devtools_testutils.storage import StorageTestCase
from settings.testcase import DataLakePreparer

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
TEST_FILE_PREFIX = 'file'
TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(
    key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
    key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")
# ------------------------------------------------------------------------------


class DatalakeCpkTest(StorageTestCase):
    async def _setup(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=account_key)
        self.file_system_name = self.get_resource_name('utfilesystem')

        if self.is_live:
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                await file_system.create_file_system(timeout=5)
            except ResourceExistsError:
                pass

    def teardown(self):
        if self.is_live:
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.dsc.delete_file_system(self.file_system_name))
                loop.run_until_complete(self.dsc.__aexit__())
            except ResourceNotFoundError:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    def _get_file_reference(self, prefix=TEST_FILE_PREFIX):
        file_name = self.get_resource_name(prefix)
        return file_name

    async def _create_directory(self, name=None, cpk=None):
        directory_name = name if name else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        try:
            await directory_client.create_directory(cpk=cpk)
        except ResourceExistsError:
            pass
        return directory_client

    async def _create_file(self, directory_name=None, file_name=None, cpk=None):
        if directory_name:
            await self._create_directory(directory_name, cpk)
        if not file_name:
            file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.file_system_name, directory_name + '/' + file_name)
        try:
            await file_client.create_file(cpk=cpk)
        except ResourceExistsError:
            pass
        return file_client
    # ---------------------------------------------------------------------------

    @DataLakePreparer()
    async def test_create_directory_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, 'cpkdirectory')
        response = await directory_client.create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(response)
        self.assertTrue(response['request_server_encrypted'])
        self.assertEqual(TEST_ENCRYPTION_KEY.key_hash, response['encryption_key_sha256'])

    @DataLakePreparer()
    async def test_create_sub_directory_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = await self._create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Act
        sub_directory_client = await directory_client.create_sub_directory('cpksubdirectory', cpk=TEST_ENCRYPTION_KEY)
        props = await sub_directory_client.get_directory_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(props)

    @DataLakePreparer()
    async def test_create_file_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = await self._create_directory(cpk=TEST_ENCRYPTION_KEY)
        file_client = directory_client.get_file_client('cpkfile')

        # Act
        response = await file_client.create_file(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(response)
        self.assertTrue(response['request_server_encrypted'])
        self.assertEqual(TEST_ENCRYPTION_KEY.key_hash, response['encryption_key_sha256'])

    @DataLakePreparer()
    async def test_get_directory_properties_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = await self._create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Act
        props = await directory_client.get_directory_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(props)

    @DataLakePreparer()
    async def test_get_file_properties_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = await self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)

        # Act
        props = await file_client.get_file_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(props)

    @DataLakePreparer()
    async def test_directory_exists_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = await self._create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Act
        exists = await directory_client.exists()

        # Assert
        self.assertTrue(exists)

    @DataLakePreparer()
    async def test_file_exists_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = await self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)

        # Act
        exists = await file_client.exists()

        # Assert
        self.assertIsNotNone(exists)

    @DataLakePreparer()
    async def test_file_upload_data_file_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = await self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)
        data = self.get_random_bytes(1024)

        # Act
        response = await file_client.upload_data(data, overwrite=True, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(response)
        self.assertTrue(response['request_server_encrypted'])
        self.assertEqual(TEST_ENCRYPTION_KEY.key_hash, response['encryption_key_sha256'])

    @DataLakePreparer()
    async def test_file_append_flush_data_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = await self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)
        data = self.get_random_bytes(1024)

        # Act
        await file_client.append_data(data, offset=0, cpk=TEST_ENCRYPTION_KEY)
        response = await file_client.flush_data(offset=0, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(response)
        self.assertTrue(response['request_server_encrypted'])
        self.assertEqual(TEST_ENCRYPTION_KEY.key_hash, response['encryption_key_sha256'])

    @DataLakePreparer()
    async def test_file_download_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = await self._create_directory(cpk=TEST_ENCRYPTION_KEY)
        file_name = self._get_file_reference()
        file_client = directory_client.get_file_client(file_name)

        data = self.get_random_bytes(1024)
        await file_client.upload_data(data, overwrite=True, cpk=TEST_ENCRYPTION_KEY)

        # Act
        download = await file_client.download_file(cpk=TEST_ENCRYPTION_KEY)
        file = await download.readall()

        # Assert
        self.assertIsNotNone(file)
        self.assertEqual(data, file)

    @DataLakePreparer()
    async def test_set_metadata_cpk(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        await self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = await self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        await file_client.set_metadata(metadata, cpk=TEST_ENCRYPTION_KEY)
        props = await file_client.get_file_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(metadata, props.metadata)


if __name__ == '__main__':
    unittest.main()

