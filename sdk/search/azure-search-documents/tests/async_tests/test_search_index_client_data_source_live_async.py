# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
import json
from os.path import dirname, join, realpath

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureMgmtTestCase

from azure_devtools.scenario_tests import ReplayableTest
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer

from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
)
from azure.search.documents.indexes.aio import SearchIndexerClient

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

class SearchDataSourcesClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    def _create_data_source_connection(self, name="sample-datasource"):
        container = SearchIndexerDataContainer(name='searchcontainer')
        data_source_connection = SearchIndexerDataSourceConnection(
            name=name,
            type="azureblob",
            connection_string=CONNECTION_STRING,
            container=container
        )
        return data_source_connection

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        result = await client.create_data_source_connection(data_source_connection)
        assert result.name == "sample-datasource"
        assert result.type == "azureblob"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        result = await client.create_data_source_connection(data_source_connection)
        assert len(await client.get_data_source_connections()) == 1
        await client.delete_data_source_connection("sample-datasource")
        assert len(await client.get_data_source_connections()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = await client.create_data_source_connection(data_source_connection)
        result = await client.get_data_source_connection("sample-datasource")
        assert result.name == "sample-datasource"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_list_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection1 = self._create_data_source_connection()
        data_source_connection2 = self._create_data_source_connection(name="another-sample")
        created1 = await client.create_data_source_connection(data_source_connection1)
        created2 = await client.create_data_source_connection(data_source_connection2)
        result = await client.get_data_source_connections()
        assert isinstance(result, list)
        assert set(x.name for x in result) == {"sample-datasource", "another-sample"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = await client.create_data_source_connection(data_source_connection)
        assert len(await client.get_data_source_connections()) == 1
        data_source_connection.description = "updated"
        await client.create_or_update_data_source_connection(data_source_connection)
        assert len(await client.get_data_source_connections()) == 1
        result = await client.get_data_source_connection("sample-datasource")
        assert result.name == "sample-datasource"
        assert result.description == "updated"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_datasource_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = await client.create_data_source_connection(data_source_connection)
        etag = created.e_tag

        # Now update the data source connection
        data_source_connection.description = "updated"
        await client.create_or_update_data_source_connection(data_source_connection)

        # prepare data source connection
        data_source_connection.e_tag = etag # reset to the original data source connection
        data_source_connection.description = "changed"
        with pytest.raises(HttpResponseError):
            await client.create_or_update_data_source_connection(data_source_connection, match_condition=MatchConditions.IfNotModified)
            assert len(await client.get_data_source_connections()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_datasource_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = await client.create_data_source_connection(data_source_connection)
        etag = created.e_tag

        # Now update the data source connection
        data_source_connection.description = "updated"
        await client.create_or_update_data_source_connection(data_source_connection)

        # prepare data source connection
        data_source_connection.e_tag = etag # reset to the original data source connection
        with pytest.raises(HttpResponseError):
            await client.delete_data_source_connection(data_source_connection, match_condition=MatchConditions.IfNotModified)
            assert len(await client.get_data_source_connections()) == 1
