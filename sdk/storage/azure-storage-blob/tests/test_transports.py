# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.blob import BlobClient, BlobServiceClient
from azure.core.exceptions import ResourceExistsError

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import MockCoreTransport, MockLegacyTransport


class TestStorageTransports(StorageRecordedTestCase):
    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key)
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name, timeout=5)
            except ResourceExistsError:
                pass
            try:
                self.bsc.create_container(self.source_container_name, timeout=5)
            except ResourceExistsError:
                pass
        self.byte_data = self.get_random_bytes(1024)

    @BlobPreparer()
    def test_legacy_transport(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockLegacyTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='test_cont',
            blob_name='test_blob',
            credential=storage_account_key,
            transport=transport,
            retry_total=0
        )

        content = blob_client.download_blob()
        assert content is not None

        props = blob_client.get_blob_properties()
        assert props is not None

        data = b"Hello World!"
        resp = blob_client.upload_blob(data, overwrite=True)
        assert resp is not None

        blob_data = blob_client.download_blob().read()
        assert blob_data == b"Hello World!"  # data is fixed by mock transport

        resp = blob_client.delete_blob()
        assert resp is None

    @BlobPreparer()
    def test_legacy_transport_content_validation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockLegacyTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='test_cont',
            blob_name='test_blob',
            credential=storage_account_key,
            transport=transport,
            retry_total=0
        )

        data = b"Hello World!"
        resp = blob_client.upload_blob(data, overwrite=True, validate_content=True)
        assert resp is not None

        blob_data = blob_client.download_blob(validate_content=True).read()
        assert blob_data == b"Hello World!"  # data is fixed by mock transport

    @BlobPreparer()
    def test_core_transport(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockCoreTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='test_cont',
            blob_name='test_blob',
            credential=storage_account_key,
            transport=transport,
            retry_total=0
        )

        content = blob_client.download_blob()
        assert content is not None

        props = blob_client.get_blob_properties()
        assert props is not None

        data = b"Hello World!"
        resp = blob_client.upload_blob(data, overwrite=True)
        assert resp is not None

        blob_data = blob_client.download_blob().read()
        assert blob_data == b"Hello World!"  # data is fixed by mock transport

        resp = blob_client.delete_blob()
        assert resp is None

    @BlobPreparer()
    def test_core_transport_content_validation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockCoreTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='test_cont',
            blob_name='test_blob',
            credential=storage_account_key,
            transport=transport,
            retry_total=0
        )

        data = b"Hello World!"
        resp = blob_client.upload_blob(data, overwrite=True, validate_content=True)
        assert resp is not None

        blob_data = blob_client.download_blob(validate_content=True).read()
        assert blob_data == b"Hello World!"  # data is fixed by mock transport
