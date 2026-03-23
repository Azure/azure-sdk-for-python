# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.blob import BlobClient, BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from azure.core.pipeline.transport import RequestsTransport

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import MockLegacyTransport


class TestStorageTransports(StorageRecordedTestCase):
    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key.secret)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name, timeout=5)
            except ResourceExistsError:
                pass

    @BlobPreparer()
    def test_legacy_transport_old_response(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockLegacyTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=transport,
            retry_total=0
        )

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
    def test_legacy_transport_old_response_content_validation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockLegacyTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=transport,
            retry_total=0
        )

        data = b"Hello World!"
        resp = blob_client.upload_blob(data, overwrite=True, validate_content=True)
        assert resp is not None

        blob_data = blob_client.download_blob(validate_content=True).read()
        assert blob_data == b"Hello World!"  # data is fixed by mock transport

        resp = blob_client.delete_blob()
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_legacy_transport(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        transport = RequestsTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name=self.container_name,
            blob_name=self.get_resource_name('blob'),
            credential=storage_account_key.secret,
            transport=transport
        )

        data = b"Hello World!"
        resp = blob_client.upload_blob(data, overwrite=True)
        assert resp is not None

        blob_data = blob_client.download_blob().read()
        assert blob_data == b"Hello World!"

        resp = blob_client.delete_blob()
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_legacy_transport_content_validation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        transport = RequestsTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name=self.container_name,
            blob_name=self.get_resource_name('blob'),
            credential=storage_account_key.secret,
            transport=transport
        )

        data = b"Hello World!"
        resp = blob_client.upload_blob(data, overwrite=True, validate_content=True)
        assert resp is not None

        blob_data = blob_client.download_blob(validate_content=True).read()
        assert blob_data == b"Hello World!"

        resp = blob_client.delete_blob()
        assert resp is None
