# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.storage.blob import BlobClient, ContainerClient
from azure.storage.blob._encryption import _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION
from azure.storage.blob._shared.base_client import TransportWrapper

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestStorageBlobClientGaps(StorageRecordedTestCase):

    @BlobPreparer()
    def test_seal_append_blob_when_encryption_required_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='foo',
            blob_name='bar',
            credential=storage_account_key.secret,
            require_encryption=True,
        )

        with pytest.raises(ValueError) as error:
            blob_client.seal_append_blob()

        assert str(error.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

    @BlobPreparer()
    def test_get_container_client_when_transport_not_wrapped_wraps_transport(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='foo',
            blob_name='bar',
            credential=storage_account_key.secret,
        )

        assert not isinstance(blob_client._pipeline._transport, TransportWrapper)

        container_client = blob_client._get_container_client()

        assert isinstance(container_client, ContainerClient)
        assert container_client.container_name == 'foo'
        assert container_client.account_name == storage_account_name
        assert container_client.credential.account_name == storage_account_name
        assert container_client.credential.account_key == storage_account_key.secret
        assert container_client._pipeline is not blob_client._pipeline
        assert isinstance(container_client._pipeline._transport, TransportWrapper)
