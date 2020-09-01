# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath
import time

import pytest

from devtools_testutils import AzureMgmtTestCase
from azure_devtools.scenario_tests import ReplayableTest
from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    SearchIndex,
    SearchIndexerDataSourceConnection,
    SearchIndexer,
    SearchIndexerDataContainer,
)
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "hotel_schema.json")).read()
try:
    BATCH = json.load(open(join(CWD, "hotel_small.json")))
except UnicodeDecodeError:
    BATCH = json.load(open(join(CWD, "hotel_small.json"), encoding="utf-8"))
TIME_TO_SLEEP = 5
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net'

class SearchIndexersClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    def _prepare_indexer(self, endpoint, api_key, name="sample-indexer", ds_name="sample-datasource", id_name="hotels"):
        con_str = self.settings.AZURE_STORAGE_CONNECTION_STRING
        self.scrubber.register_name_pair(con_str, 'connection_string')
        container = SearchIndexerDataContainer(name='searchcontainer')
        data_source_connection = SearchIndexerDataSourceConnection(
            name=ds_name,
            type="azureblob",
            connection_string=con_str,
            container=container
        )
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        ds = client.create_data_source_connection(data_source_connection)

        index_name = id_name
        fields = [
        {
          "name": "hotelId",
          "type": "Edm.String",
          "key": True,
          "searchable": False
        }]
        index = SearchIndex(name=index_name, fields=fields)
        ind = SearchIndexClient(endpoint, AzureKeyCredential(api_key)).create_index(index)
        return SearchIndexer(name=name, data_source_name=ds.name, target_index_name=ind.name)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        result = client.create_indexer(indexer)
        assert result.name == "sample-indexer"
        assert result.target_index_name == "hotels"
        assert result.data_source_name == "sample-datasource"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        result = client.create_indexer(indexer)
        assert len(client.get_indexers()) == 1
        client.delete_indexer("sample-indexer")
        assert len(client.get_indexers()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_reset_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        result = client.create_indexer(indexer)
        assert len(client.get_indexers()) == 1
        result = client.reset_indexer("sample-indexer")
        assert client.get_indexer_status("sample-indexer").last_result.status in ('InProgress', 'reset')

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_run_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        result = client.create_indexer(indexer)
        assert len(client.get_indexers()) == 1
        start = time.time()
        client.run_indexer("sample-indexer")
        assert client.get_indexer_status("sample-indexer").status == 'running'

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        created = client.create_indexer(indexer)
        result = client.get_indexer("sample-indexer")
        assert result.name == "sample-indexer"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_list_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer1 = self._prepare_indexer(endpoint, api_key)
        indexer2 = self._prepare_indexer(endpoint, api_key, name="another-indexer", ds_name="another-datasource", id_name="another-index")
        created1 = client.create_indexer(indexer1)
        created2 = client.create_indexer(indexer2)
        result = client.get_indexers()
        assert isinstance(result, list)
        assert set(x.name for x in result) == {"sample-indexer", "another-indexer"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        created = client.create_indexer(indexer)
        assert len(client.get_indexers()) == 1
        indexer.description = "updated"
        client.create_or_update_indexer(indexer)
        assert len(client.get_indexers()) == 1
        result = client.get_indexer("sample-indexer")
        assert result.name == "sample-indexer"
        assert result.description == "updated"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_indexer_status(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        result = client.create_indexer(indexer)
        status = client.get_indexer_status("sample-indexer")
        assert status.status is not None

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_indexer_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        created = client.create_indexer(indexer)
        etag = created.e_tag


        indexer.description = "updated"
        client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.create_or_update_indexer(indexer, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_indexer_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        indexer = self._prepare_indexer(endpoint, api_key)
        result = client.create_indexer(indexer)
        etag = result.e_tag

        indexer.description = "updated"
        client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.delete_indexer(indexer, match_condition=MatchConditions.IfNotModified)
