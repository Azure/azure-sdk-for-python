# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.storage.blob._models import BlobProperties

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestStorageBlobClientHelpersFromBlobUrl(StorageRecordedTestCase):

    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key.secret)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                container.create_container()
            except ResourceExistsError:
                pass

    def _get_blob_reference(self):
        return self.get_resource_name('blob')

    def test_from_blob_url_when_url_has_no_host_raises_invalid_url(self):
        with pytest.raises(ValueError) as error:
            BlobClient.from_blob_url("https:///container/blob")

        assert str(error.value) == "Invalid URL: https:///container/blob"

    @BlobPreparer()
    def test_from_blob_url_when_custom_domain_has_extra_path_segments_preserves_account_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_url = "https://www.mydomain.com/account/path/container/blob"
        blob_client = BlobClient.from_blob_url(
            blob_url,
            credential={
                'account_name': storage_account_name,
                'account_key': storage_account_key.secret,
            }
        )

        assert blob_client.url == blob_url
        assert blob_client.container_name == "container"
        assert blob_client.blob_name == "blob"
        assert blob_client.primary_endpoint == blob_url

    def test_from_blob_url_when_container_name_is_empty_raises_invalid_url(self):
        with pytest.raises(ValueError) as error:
            BlobClient.from_blob_url("https://www.mydomain.com/account/path//blob")

        assert str(error.value) == "Invalid URL. Provide a blob_url with a valid blob and container name."

    def test_from_blob_url_when_snapshot_is_blob_properties_uses_snapshot_value(self):
        blob_url = "https://storagename.blob.core.windows.net/container/blob"
        snapshot_properties = BlobProperties.__new__(BlobProperties)
        snapshot_properties.snapshot = "2026-03-15T00:00:00.0000000Z"

        parsed_client = BlobClient.from_blob_url(
            blob_url,
            snapshot=snapshot_properties
        )

        assert parsed_client.container_name == "container"
        assert parsed_client.blob_name == "blob"
        assert parsed_client.snapshot == snapshot_properties.snapshot
        assert parsed_client.url == blob_url + "?snapshot=" + snapshot_properties.snapshot
