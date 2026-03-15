# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.blob import ContainerClient, StandardBlobTier
from azure.storage.blob._container_client_helpers import _generate_set_tiers_options

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestContainerClientHelpersSetTiersGaps(StorageRecordedTestCase):

    @BlobPreparer()
    def test_generate_set_tiers_options_when_no_blobs_provided_returns_empty_requests_and_batch_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container_client = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            credential=storage_account_key.secret,
        )

        reqs, options = _generate_set_tiers_options(
            query_str=container_client._query_str,
            container_name=container_client.container_name,
            blob_tier=StandardBlobTier.Hot,
            client=container_client._client,
        )

        assert reqs == []
        assert options == {
            'raise_on_any_failure': True,
            'sas': '',
            'timeout': '',
            'path': 'container',
            'restype': 'restype=container&'
        }
