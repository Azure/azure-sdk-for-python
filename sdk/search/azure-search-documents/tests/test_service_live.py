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

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "hotel_small.json")))

class SearchIndexClientTest(AzureMgmtTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    def test_get_service_statistics(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    def test_list_indexes_empty(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = client.list_indexes()
        assert len(result) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_list_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = client.list_indexes()
        assert len(result) == 1
        assert set(result[0].keys()) == {'tokenizers', 'e_tag', 'analyzers', 'token_filters', 'fields', 'name', 'char_filters', 'suggesters', 'scoring_profiles'}
        assert result[0]["name"] == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_index(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = client.get_index(index_name)
        assert set(result.keys()) == {'tokenizers', 'e_tag', 'analyzers', 'token_filters', 'fields', 'name', 'char_filters', 'suggesters', 'scoring_profiles'}
        assert result["name"] == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_index_statistics(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = client.get_index_statistics(index_name)
        assert set(result.keys()) == {'document_count', 'storage_size'}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        client.delete_index(index_name)
        import time
        time.sleep(5)
        result = client.list_indexes()
        assert len(result) == 0