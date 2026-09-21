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

    def test_name_based_link_is_url_encoded(self):
        # The signing link must be URL-encoded the same way GetPathFromLink encodes
        # the request path, so the auth signature validates on the server
        # (see https://github.com/Azure/azure-sdk-for-python/issues/47503)
        assert base.GetResourceIdOrFullNameFromLink(
            "dbs/paas_cmr/colls/spaced id") == "dbs/paas_cmr/colls/spaced%20id"
        assert base.GetPathFromLink(
            "dbs/paas_cmr/colls/spaced id").startswith("/dbs/paas_cmr/colls/spaced%20id/")
        # links without URL-unsafe characters are unchanged
        assert base.GetResourceIdOrFullNameFromLink(
            "dbs/paas_cmr/colls/plain_id") == "dbs/paas_cmr/colls/plain_id"
