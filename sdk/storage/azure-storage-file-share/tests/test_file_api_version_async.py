# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from _shared.asynctestcase import AsyncStorageTestCase
from _shared.testcase import GlobalStorageAccountPreparer
from azure.core.exceptions import ResourceExistsError
from azure.storage.fileshare.aio import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)
from azure.storage.fileshare._generated import __version__ as version

# ------------------------------------------------------------------------------
TEST_FILE_PREFIX = 'file'


class AsyncStorageClientTest(AsyncStorageTestCase):
    def setUp(self):
        super(AsyncStorageTestCase, self).setUp()
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = version
        self.short_byte_data = self.get_random_bytes(1024)

    # --Helpers-----------------------------------------------------------------

    def _get_file_reference(self, prefix=TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    async def _create_share(self, fsc):
        share_name = self.get_resource_name('utshare')
        share = fsc.get_share_client(share_name)
        try:
            await share.create_share()
        except ResourceExistsError:
            pass
        return share

    async def _delete_share(self, share):
        try:
            await share.delete_share()
        except:
            pass
        return share


    # --Test Cases--------------------------------------------------------------

    def test_service_client_api_version_property(self):
        service_client = ShareServiceClient(
            "https://foo.file.core.windows.net/account",
            credential="fake_key")
        self.assertEqual(service_client.api_version, self.api_version_2)
        self.assertEqual(service_client._client._config.version, self.api_version_2)

        with pytest.raises(AttributeError):
            service_client.api_version = self.api_version_1

        service_client = ShareServiceClient(
            "https://foo.file.core.windows.net/account",
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(service_client.api_version, self.api_version_1)
        self.assertEqual(service_client._client._config.version, self.api_version_1)

        share_client = service_client.get_share_client("foo")
        self.assertEqual(share_client.api_version, self.api_version_1)
        self.assertEqual(share_client._client._config.version, self.api_version_1)

    def test_share_client_api_version_property(self):
        share_client = ShareClient(
            "https://foo.file.core.windows.net/account",
            "share_name",
            credential="fake_key")
        self.assertEqual(share_client.api_version, self.api_version_2)
        self.assertEqual(share_client._client._config.version, self.api_version_2)

        share_client = ShareClient(
            "https://foo.file.core.windows.net/account",
            "share_name",
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(share_client.api_version, self.api_version_1)
        self.assertEqual(share_client._client._config.version, self.api_version_1)

        dir_client = share_client.get_directory_client("foo")
        self.assertEqual(dir_client.api_version, self.api_version_1)
        self.assertEqual(dir_client._client._config.version, self.api_version_1)

        file_client = share_client.get_file_client("foo")
        self.assertEqual(file_client.api_version, self.api_version_1)
        self.assertEqual(file_client._client._config.version, self.api_version_1)

    def test_directory_client_api_version_property(self):
        dir_client = ShareDirectoryClient(
            "https://foo.file.core.windows.net/account",
            "share_name",
            "dir_path",
            credential="fake_key")
        self.assertEqual(dir_client.api_version, self.api_version_2)
        self.assertEqual(dir_client._client._config.version, self.api_version_2)

        dir_client = ShareDirectoryClient(
            "https://foo.file.core.windows.net/account",
            "share_name",
            "dir_path",
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(dir_client.api_version, self.api_version_1)
        self.assertEqual(dir_client._client._config.version, self.api_version_1)

        subdir_client = dir_client.get_subdirectory_client("foo")
        self.assertEqual(subdir_client.api_version, self.api_version_1)
        self.assertEqual(subdir_client._client._config.version, self.api_version_1)

        file_client = dir_client.get_file_client("foo")
        self.assertEqual(file_client.api_version, self.api_version_1)
        self.assertEqual(file_client._client._config.version, self.api_version_1)

    def test_file_client_api_version_property(self):
        file_client = ShareFileClient(
            "https://foo.file.core.windows.net/account",
            "share",
            self._get_file_reference(),
            credential="fake_key")
        self.assertEqual(file_client.api_version, self.api_version_2)
        self.assertEqual(file_client._client._config.version, self.api_version_2)

        file_client = ShareFileClient(
            "https://foo.file.core.windows.net/account",
            "share",
            self._get_file_reference(),
            credential="fake_key",
            api_version=self.api_version_1)
        self.assertEqual(file_client.api_version, self.api_version_1)
        self.assertEqual(file_client._client._config.version, self.api_version_1)

    def test_invalid_api_version(self):
        with pytest.raises(ValueError) as error:
            ShareServiceClient(
                "https://foo.file.core.windows.net/account",
                credential="fake_key",
                api_version="foo")
        self.assertTrue(str(error.value).startswith("Unsupported API version 'foo'."))

        with pytest.raises(ValueError) as error:
            ShareClient(
                "https://foo.file.core.windows.net/account",
                "share_name",
                credential="fake_key",
                api_version="foo")
        self.assertTrue(str(error.value).startswith("Unsupported API version 'foo'."))

        with pytest.raises(ValueError) as error:
            ShareDirectoryClient(
                "https://foo.file.core.windows.net/account",
                "share_name",
                "dir_path",
                credential="fake_key",
                api_version="foo")
        self.assertTrue(str(error.value).startswith("Unsupported API version 'foo'."))

        with pytest.raises(ValueError) as error:
            ShareFileClient(
                "https://foo.file.core.windows.net/account",
                "share",
                self._get_file_reference(),
                credential="fake_key",
                api_version="foo")
        self.assertTrue(str(error.value).startswith("Unsupported API version 'foo'."))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_old_api_copy_file_succeeds_async(self, resource_group, location, storage_account, storage_account_key):
        fsc = ShareServiceClient(
            self.account_url(storage_account, "file"),
            credential=storage_account_key,
            max_range_size=4 * 1024,
            api_version=self.api_version_1
        )
        share = await self._create_share(fsc)
        file_name = self._get_file_reference()

        source_client = share.get_file_client(file_name)
        await source_client.upload_file(self.short_byte_data)
        source_prop = await source_client.get_file_properties()

        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=share.share_name,
            file_path='file1copy',
            credential=storage_account_key,
            api_version=self.api_version_1)

        # Act
        copy = await file_client.start_copy_from_url(source_client.url)

        # Assert
        dest_prop = await file_client.get_file_properties()
        # to make sure the acl is copied from source
        self.assertEqual(source_prop['permission_key'], dest_prop['permission_key'])

        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertIsNotNone(copy['copy_id'])

        copy_file = await (await file_client.download_file()).readall()
        self.assertEqual(copy_file, self.short_byte_data)

# ------------------------------------------------------------------------------
