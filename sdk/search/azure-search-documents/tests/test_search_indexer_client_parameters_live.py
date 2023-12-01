# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from sys import api_version
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    IndexingParameters,
    IndexingParametersConfiguration,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchIndexerParametersClientTest(AzureRecordedTestCase):
    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_create_blob_indexer(self, endpoint, api_key, **kwargs):
        storage_cs = kwargs.get("search_storage_connection_string")
        container_name = kwargs.get("search_storage_container_name")

        client =self._prepare_search_indexer_client(endpoint, api_key)
        index_client = self._prepare_search_index_client(endpoint, api_key)


        name = "create-blob"
        indexer = self._prepare_blob_indexer(client, index_client, storage_cs, name, container_name)
        result = client.create_indexer(indexer)
        assert result.name == name
        assert result.target_index_name == f"{name}-hotels"
        assert result.data_source_name == f"{name}-ds"

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_create_sql_indexer(self, endpoint, api_key, **kwargs):
        sql_cs = kwargs.get("search_sql_connection_string")
        table_name = kwargs.get("search_sql_table_name")

        client =self._prepare_search_indexer_client(endpoint, api_key)
        index_client = self._prepare_search_index_client(endpoint, api_key)

        name = "create-sql"
        indexer = self._prepare_sql_indexer(client, index_client, sql_cs, name, table_name)
        result = client.create_indexer(indexer)
        assert result.name == name
        assert result.target_index_name == f"{name}-hotels"
        assert result.data_source_name == f"{name}-ds"

    def _prepare_search_index_client(self, endpoint, api_key):
        return SearchIndexClient(endpoint, api_key, retry_backoff_factor=60, api_version="2023-11-01")

    def _prepare_search_indexer_client(self, endpoint, api_key):
        return SearchIndexerClient(endpoint, api_key, retry_backoff_factor=60, api_version="2023-11-01")

    def _prepare_blob_indexer(self, client, index_client, storage_cs, name, container_name):
        data_source_connection = SearchIndexerDataSourceConnection(
            name=f"{name}-ds",
            type="azureblob",
            connection_string=storage_cs,
            container=SearchIndexerDataContainer(name=container_name),
        )
        
        ds = client.create_data_source_connection(data_source_connection)

        fields = [{"name": "hotelId", "type": "Edm.String", "key": True, "searchable": False}]
        index = SearchIndex(name=f"{name}-hotels", fields=fields)
        ind = index_client.create_index(index)
        parameters_config = IndexingParametersConfiguration(parsing_mode="json")
        index_parameters = IndexingParameters(configuration=parameters_config)
        return SearchIndexer(name=name, data_source_name=ds.name, target_index_name=ind.name, parameters=index_parameters)
    
    def _prepare_sql_indexer(self, client, index_client, sql_cs, name, table_name):
        data_source_connection = SearchIndexerDataSourceConnection(
            name=f"{name}-ds",
            type="azuresql",
            connection_string=sql_cs,
            container=SearchIndexerDataContainer(name=table_name)
        )
        ds = client.create_data_source_connection(data_source_connection)

        fields = [{"name": "hotelId", "type": "Edm.String", "key": True, "searchable": False}]
        index = SearchIndex(name=f"{name}-hotels", fields=fields)
        ind = index_client.create_index(index)
        parameters_config = IndexingParametersConfiguration(query_timeout="00:06:00")
        index_parameters = IndexingParameters(configuration=parameters_config)
        return SearchIndexer(name=name, data_source_name=ds.name, target_index_name=ind.name, parameters=index_parameters)
