# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
import json
from os.path import dirname, join, realpath
import time

import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from search_service_preparer import SearchServicePreparer

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from azure.core.exceptions import HttpResponseError
from azure.search.documents import SearchApiKeyCredential
from azure.search.documents.aio import SearchServiceClient

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "..", "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "..", "hotel_small.json")))

def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
    upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        trim_kwargs_from_test_function(test_fn, kwargs)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

    return run


class SearchIndexClientTest(AzureMgmtTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    @await_prepared_test
    async def test_get_service_statistics(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = await client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    @await_prepared_test
    async def test_list_indexes_empty(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = await client.list_indexes()
        assert len(result) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_list_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = await client.list_indexes()
        assert len(result) == 1
        assert set(result[0].keys()) == {'tokenizers', 'e_tag', 'analyzers', 'token_filters', 'fields', 'name', 'char_filters', 'suggesters', 'scoring_profiles'}
        assert result[0]["name"] == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_index(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = await client.get_index(index_name)
        assert set(result.keys()) == {'tokenizers', 'e_tag', 'analyzers', 'token_filters', 'fields', 'name', 'char_filters', 'suggesters', 'scoring_profiles'}
        assert result["name"] == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_index_statistics(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        result = await client.get_index_statistics(index_name)
        assert set(result.keys()) == {'document_count', 'storage_size'}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_delete_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, SearchApiKeyCredential(api_key))
        await client.delete_index(index_name)
        import time
        time.sleep(5)
        result = await client.list_indexes()
        assert len(result) == 0
