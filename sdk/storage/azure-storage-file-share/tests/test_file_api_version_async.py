# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform
from datetime import datetime, timedelta

from azure.core.exceptions import AzureError, ResourceExistsError
from azure.storage.fileshare.aio import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer

# ------------------------------------------------------------------------------
TEST_FILE_PREFIX = 'file'


class StorageClientTest(StorageTestCase):
    def setUp(self):
        super(StorageClientTest, self).setUp()
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = "2019-07-07"

    # --Helpers-----------------------------------------------------------------

    def _get_file_reference(self, prefix=TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    def _create_share(self, fsc):
        share_name = self.get_resource_name('utshare')
        share = fsc.get_share_client(share_name)
        try:
            share.create_share()
        except ResourceExistsError:
            pass
        return share

    def _delete_share(self, share):
        try:
            share.delete_share()
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


# ------------------------------------------------------------------------------
