# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath
import time

import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from search_service_preparer import SearchServicePreparer

from azure.core.exceptions import HttpResponseError
from azure.search.documents import SearchServiceClient, SearchApiKeyCredential


class SearchIndexClientTest(AzureMgmtTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    def test_get_service_statistics(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}
