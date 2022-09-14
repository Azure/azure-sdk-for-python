# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob.aio import (
    ContainerClient,
    BlobClient,
    BlobServiceClient,
)
from azure.storage.blob._shared.constants import X_MS_VERSION

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer

TEST_BLOB_PREFIX = 'blob'


class TestStorageBlobApiVersionAsync(AsyncStorageRecordedTestCase):

    # --Helpers-----------------------------------------------------------------
    def _setup(self):
        self.api_version_1 = "2019-02-02"
        self.api_version_2 = X_MS_VERSION
        self.container_name = self.get_resource_name('utcontainer')

    def _get_blob_reference(self, prefix=TEST_BLOB_PREFIX):
        return self.get_resource_name(prefix)

    async def _create_container(self, bsc):
        container = bsc.get_container_client(self.container_name)
        try:
            await container.create_container()
        except ResourceExistsError:
            pass
        return container

    # --Test Cases--------------------------------------------------------------

    def test_service_client_api_version_property(self):
        self._setup()
        service_client = BlobServiceClient(
            "https://foo.blob.core.windows.net/account",
            credential="fake_key")
        assert service_client.api_version == self.api_version_2
        assert service_client._client._config.version == self.api_version_2

        with pytest.raises(AttributeError):
            service_client.api_version = "foo"

        service_client = BlobServiceClient(
            "https://foo.blob.core.windows.net/account",
            credential="fake_key",
            api_version=self.api_version_1)
        assert service_client.api_version == self.api_version_1
        assert service_client._client._config.version == self.api_version_1

        container_client = service_client.get_container_client("foo")
        assert container_client.api_version == self.api_version_1
        assert container_client._client._config.version == self.api_version_1

        blob_client = service_client.get_blob_client("foo", "bar")
        assert blob_client.api_version == self.api_version_1
        assert blob_client._client._config.version == self.api_version_1

    def test_container_client_api_version_property(self):
        self._setup()
        container_client = ContainerClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            credential="fake_key")
        assert container_client.api_version == self.api_version_2
        assert container_client._client._config.version == self.api_version_2

        container_client = ContainerClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            credential="fake_key",
            api_version=self.api_version_1)
        assert container_client.api_version == self.api_version_1
        assert container_client._client._config.version == self.api_version_1

        blob_client = container_client.get_blob_client("foo")
        assert blob_client.api_version == self.api_version_1
        assert blob_client._client._config.version == self.api_version_1

    def test_blob_client_api_version_property(self):
        self._setup()
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            self._get_blob_reference(),
            credential="fake_key",
            api_version=self.api_version_1)
        assert blob_client.api_version == self.api_version_1
        assert blob_client._client._config.version == self.api_version_1

        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            self.container_name,
            self._get_blob_reference(),
            credential="fake_key")
        assert blob_client.api_version == self.api_version_2
        assert blob_client._client._config.version == self.api_version_2

    def test_invalid_api_version(self):
        self._setup()
        with pytest.raises(ValueError) as error:
            BlobServiceClient(
                "https://foo.blob.core.windows.net/account",
                credential="fake_key",
                api_version="foo")
        assert str(error.value).startswith("Unsupported API version 'foo'.")

        with pytest.raises(ValueError) as error:
            ContainerClient(
                "https://foo.blob.core.windows.net/account",
                self.container_name,
                credential="fake_key",
                api_version="foo")
        assert str(error.value).startswith("Unsupported API version 'foo'.")

        with pytest.raises(ValueError) as error:
            BlobClient(
                "https://foo.blob.core.windows.net/account",
                self.container_name,
                self._get_blob_reference(),
                credential="fake_key",
                api_version="foo")
        assert str(error.value).startswith("Unsupported API version 'foo'.")

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_old_api_get_page_ranges_succeeds(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup()
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=4 * 1024,
            max_page_size=4 * 1024,
            api_version=self.api_version_1)
        container = await self._create_container(bsc)
        blob_name = self._get_blob_reference()

        blob = container.get_blob_client(blob_name)
        await blob.create_page_blob(2048)
        data = self.get_random_bytes(1536)

        snapshot1 = await blob.create_snapshot()
        await blob.upload_page(data, offset=0, length=1536)
        snapshot2 = await blob.create_snapshot()
        await blob.clear_page(offset=512, length=512)

        # Act
        ranges1, cleared1 = await blob.get_page_ranges(previous_snapshot_diff=snapshot1)
        ranges2, cleared2 = await blob.get_page_ranges(previous_snapshot_diff=snapshot2['snapshot'])

        # Assert
        assert ranges1 is not None
        assert isinstance(ranges1, list)
        assert len(ranges1) == 2
        assert isinstance(cleared1, list)
        assert len(cleared1) == 1
        assert ranges1[0]['start'] == 0
        assert ranges1[0]['end'] == 511
        assert cleared1[0]['start'] == 512
        assert cleared1[0]['end'] == 1023
        assert ranges1[1]['start'] == 1024
        assert ranges1[1]['end'] == 1535

        assert ranges2 is not None
        assert isinstance(ranges2, list)
        assert len(ranges2) == 0
        assert isinstance(cleared2, list)
        assert len(cleared2) == 1
        assert cleared2[0]['start'] == 512
        assert cleared2[0]['end'] == 1023

# ------------------------------------------------------------------------------
