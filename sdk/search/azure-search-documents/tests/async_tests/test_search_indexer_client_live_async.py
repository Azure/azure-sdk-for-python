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
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureMgmtTestCase

from azure_devtools.scenario_tests import ReplayableTest
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer

from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    SearchIndex,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchIndexer,
)
from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "..", "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "..", "hotel_small.json"), encoding='utf-8'))
TIME_TO_SLEEP = 5
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net'

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

class SearchIndexersClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    async def _prepare_indexer(self, endpoint, api_key, name="sample-indexer", ds_name="sample-datasource", id_name="hotels"):
        con_str = self.settings.AZURE_STORAGE_CONNECTION_STRING
        self.scrubber.register_name_pair(con_str, 'connection_string')
        container = SearchIndexerDataContainer(name='searchcontainer')
        data_source_connection = SearchIndexerDataSourceConnection(
            name=ds_name,
            type="azureblob",
            connection_string=con_str,
            container=container
        )
        ds_client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        ds = await ds_client.create_data_source_connection(data_source_connection)

        index_name = id_name
        fields = [
        {
          "name": "hotelId",
          "type": "Edm.String",
          "key": True,
          "searchable": False
        }]
        index = SearchIndex(name=index_name, fields=fields)
        ind_client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        ind = await ind_client.create_index(index)
        return SearchIndexer(name=name, data_source_name=ds.name, target_index_name=ind.name)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert result.name == "sample-indexer"
        assert result.target_index_name == "hotels"
        assert result.data_source_name == "sample-datasource"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        await client.delete_indexer("sample-indexer")
        assert len(await client.get_indexers()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        created = await client.create_indexer(indexer)
        result = await client.get_indexer("sample-indexer")
        assert result.name == "sample-indexer"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_list_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer1 = await self._prepare_indexer(endpoint, api_key)
        indexer2 = await self._prepare_indexer(endpoint, api_key, name="another-indexer", ds_name="another-datasource", id_name="another-index")
        created1 = await client.create_indexer(indexer1)
        created2 = await client.create_indexer(indexer2)
        result = await client.get_indexers()
        assert isinstance(result, list)
        assert set(x.name for x in result) == {"sample-indexer", "another-indexer"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        created = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        indexer.description = "updated"
        await client.create_or_update_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        result = await client.get_indexer("sample-indexer")
        assert result.name == "sample-indexer"
        assert result.description == "updated"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_reset_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        await client.reset_indexer("sample-indexer")
        assert (await client.get_indexer_status("sample-indexer")).last_result.status in ('InProgress', 'reset')

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_run_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        start = time.time()
        await client.run_indexer("sample-indexer")
        assert (await client.get_indexer_status("sample-indexer")).status == 'running'

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_indexer_status(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        status = await client.get_indexer_status("sample-indexer")
        assert status.status is not None

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_indexer_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        created = await client.create_indexer(indexer)
        etag = created.e_tag


        indexer.description = "updated"
        await client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.create_or_update_indexer(indexer, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_indexer_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        etag = result.e_tag

        indexer.description = "updated"
        await client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.delete_indexer(indexer, match_condition=MatchConditions.IfNotModified)
