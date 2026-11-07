# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

import azure.cosmos._base as base


@pytest.mark.cosmosEmulator
class TestIdAndNameBased(unittest.TestCase):
    def test_is_name_based(self):
        self.assertFalse(base.IsNameBased("dbs/xjwmAA==/"))

        # This is a database name that ran into 'Incorrect padding'
        # exception within base.IsNameBased function
        self.assertTrue(base.IsNameBased("dbs/paas_cmr"))

    def test_collection_id(self):
        # correctly formatted link
        assert base.GetResourceIdOrFullNameFromLink("dbs/xjwmAA==/colls/1234") == "1234"
        # incorrectly formatted link should raise ValueError
        with pytest.raises(ValueError):
            base.GetResourceIdOrFullNameFromLink("db/xjwmAA==/coll/")

    def test_name_based_link_is_not_url_encoded(self):
        # Standard operations sign with the unencoded link; only the
        # partitionkeydelete sub-operation signs with the URL-encoded form
        # (see https://github.com/Azure/azure-sdk-for-python/issues/47503)
        assert base.GetResourceIdOrFullNameFromLink(
            "dbs/paas_cmr/colls/spaced id") == "dbs/paas_cmr/colls/spaced id"
        assert base.GetResourceIdOrFullNameFromLink(
            "dbs/paas_cmr/colls/plain_id") == "dbs/paas_cmr/colls/plain_id"

    def test_delete_all_items_by_partition_key_signs_with_encoded_link(self):
        # The partitionkeydelete sub-operation is the one path where the
        # service validates the auth signature against the URL-encoded
        # resource link (see https://github.com/Azure/azure-sdk-for-python/issues/47503)
        from unittest import mock
        import azure.cosmos._cosmos_client_connection as conn_module

        # bypass __init__ (no network or policy setup needed for this unit test)
        client = conn_module.CosmosClientConnection.__new__(
            conn_module.CosmosClientConnection)
        client.default_headers = {}
        client.availability_strategy = False
        client.availability_strategy_executor = None
        with mock.patch.object(base, "GetHeaders", return_value={}) as get_headers, \
                mock.patch.object(conn_module.CosmosClientConnection,
                                  "_CosmosClientConnection__Post",
                                  return_value=({}, {})), \
                mock.patch.object(conn_module.CosmosClientConnection,
                                  "_UpdateSessionIfRequired"):
            client.DeleteAllItemsByPartitionKey(
                "dbs/paas_cmr/colls/spaced id", options={"partitionKey": "x"})
        signed_resource_id = get_headers.call_args[0][4]
        assert signed_resource_id == "dbs/paas_cmr/colls/spaced%20id"
