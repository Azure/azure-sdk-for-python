# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchIndexer, SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection)
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchIndexerClientTest(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_search_indexers(self, endpoint, api_key, **kwargs):
        storage_cs = kwargs.get("search_storage_connection_string")
        container_name = kwargs.get("search_storage_container_name")
        client = SearchIndexerClient(endpoint, api_key)
        index_client = SearchIndexClient(endpoint, api_key)
        self._test_create_indexer(client, index_client, storage_cs, container_name)
        self._test_delete_indexer(client, index_client, storage_cs, container_name)
        self._test_get_indexer(client, index_client, storage_cs, container_name)
        self._test_list_indexer(client, index_client, storage_cs, container_name)
        self._test_create_or_update_indexer(client, index_client, storage_cs, container_name)
        self._test_reset_indexer(client, index_client, storage_cs, container_name)
        self._test_run_indexer(client, index_client, storage_cs, container_name)
        self._test_get_indexer_status(client, index_client, storage_cs, container_name)
        self._test_create_or_update_indexer_if_unchanged(client, index_client, storage_cs, container_name)
        self._test_delete_indexer_if_unchanged(client, index_client, storage_cs, container_name)

    def _prepare_indexer(self, client, index_client, storage_cs, name, container_name):
        data_source_connection = SearchIndexerDataSourceConnection(
            name=f"{name}-ds",
            type="azureblob",
            connection_string=storage_cs,
            container=SearchIndexerDataContainer(name=container_name)
        )
        ds = client.create_data_source_connection(data_source_connection)

        fields = [
        {
          "name": "hotelId",
          "type": "Edm.String",
          "key": True,
          "searchable": False
        }]
        index = SearchIndex(name=f"{name}-hotels", fields=fields)
        ind = index_client.create_index(index)
        return SearchIndexer(name=name, data_source_name=ds.name, target_index_name=ind.name)

    def _test_create_indexer(self, client, index_client, storage_cs, container_name):
        name = "create"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        result = client.create_indexer(indexer)
        assert result.name == name
        assert result.target_index_name == f"{name}-hotels"
        assert result.data_source_name == f"{name}-ds"

    def _test_delete_indexer(self, client, index_client, storage_cs, container_name):
        name = "delete"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        client.create_indexer(indexer)
        expected = len(client.get_indexers()) - 1
        client.delete_indexer(name)
        assert len(client.get_indexers()) == expected

    def _test_get_indexer(self, client, index_client, storage_cs, container_name):
        name = "get"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        client.create_indexer(indexer)
        result = client.get_indexer(name)
        assert result.name == name

    def _test_list_indexer(self, client, index_client, storage_cs, container_name):
        name1 = "list1"
        name2 = "list2"
        indexer1 = self._prepare_indexer(client, index_client, storage_cs, name1, container_name)
        indexer2 = self._prepare_indexer(client, index_client, storage_cs, name2, container_name)
        client.create_indexer(indexer1)
        client.create_indexer(indexer2)
        result = client.get_indexers()
        assert isinstance(result, list)
        assert set(x.name for x in result).intersection([name1, name2]) == set([name1, name2])

    def _test_create_or_update_indexer(self, client, index_client, storage_cs, container_name):
        name = "cou"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        client.create_indexer(indexer)
        expected = len(client.get_indexers())
        indexer.description = "updated"
        client.create_or_update_indexer(indexer)
        assert len(client.get_indexers()) == expected
        result = client.get_indexer(name)
        assert result.name == name
        assert result.description == "updated"

    def _test_reset_indexer(self, client, index_client, storage_cs, container_name):
        name = "reset"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        client.create_indexer(indexer)
        client.reset_indexer(name)
        assert (client.get_indexer_status(name)).last_result.status.lower() in ('inprogress', 'reset')

    def _test_run_indexer(self, client, index_client, storage_cs, container_name):
        name = "run"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        client.create_indexer(indexer)
        client.run_indexer(name)
        assert (client.get_indexer_status(name)).status == 'running'

    def _test_get_indexer_status(self, client, index_client, storage_cs, container_name):
        name = "get-status"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        client.create_indexer(indexer)
        status = client.get_indexer_status(name)
        assert status.status is not None

    def _test_create_or_update_indexer_if_unchanged(self, client, index_client, storage_cs, container_name):
        name = "couunch"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        created = client.create_indexer(indexer)
        etag = created.e_tag

        indexer.description = "updated"
        client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.create_or_update_indexer(indexer, match_condition=MatchConditions.IfNotModified)

    def _test_delete_indexer_if_unchanged(self, client, index_client, storage_cs, container_name):
        name = "delunch"
        indexer = self._prepare_indexer(client, index_client, storage_cs, name, container_name)
        result = client.create_indexer(indexer)
        etag = result.e_tag

        indexer.description = "updated"
        client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.delete_indexer(indexer, match_condition=MatchConditions.IfNotModified)
