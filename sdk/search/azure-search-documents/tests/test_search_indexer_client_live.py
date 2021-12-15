# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from os import environ
from os.path import dirname, join, realpath
import pytest
import random
import string


from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.search.documents.indexes.models import(
    SearchIndex,
    SearchIndexerDataSourceConnection,
    SearchIndexer,
    SearchIndexerDataContainer,
)
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from tests.search_service_preparer import search_decorator


class TestSearchIndexersClient(AzureRecordedTestCase):

    def _prepare_indexer(self, endpoint, api_key, storage_cs, container_name, indexer_name, datasource_name, index_name):
        container = SearchIndexerDataContainer(name=container_name)
        data_source_connection = SearchIndexerDataSourceConnection(
            name=datasource_name,
            type="azureblob",
            connection_string=storage_cs,
            container=container
        )
        client = SearchIndexerClient(endpoint, api_key)
        ds = client.create_data_source_connection(data_source_connection)
        fields = [{
            "name": "hotelId",
            "type": "Edm.String",
            "key": True,
            "searchable": False
        }]
        index = SearchIndex(name=index_name, fields=fields)
        result_index = SearchIndexClient(endpoint, api_key).create_index(index)
        return SearchIndexer(name=indexer_name, data_source_name=ds.name, target_index_name=result_index.name)

    def _parse_kwargs(self, **kwargs):
        search_endpoint = kwargs.get('search_service_endpoint')
        search_api_key = kwargs.get('search_service_api_key')
        storage_cs = kwargs.get('search_storage_connection_string')
        container_name = kwargs.get('search_storage_container_name')
        return (search_endpoint, search_api_key, storage_cs, container_name)

    def _random_tag(self, prefix="", length=10):
        allowed_chars = string.ascii_letters
        random_tag = "".join(random.choice(allowed_chars) for x in range(length)).lower()
        return "{}{}".format(prefix, random_tag)

    @search_decorator
    @recorded_by_proxy
    def test_indexer_crud(self, **kwargs):
        search_endpoint, search_api_key, storage_cs, container_name = self._parse_kwargs(**kwargs)
        indexer_name = self._random_tag(prefix="sample-indexer-")
        datasource_name = self._random_tag(prefix="sample-datasource-")
        index_name = self._random_tag("hotels-")
        client = SearchIndexerClient(search_endpoint, search_api_key)
        indexer_count = len(client.get_indexers())

        # Create indexer
        indexer = self._prepare_indexer(search_endpoint, search_api_key, storage_cs, container_name, indexer_name, datasource_name, index_name)
        result = client.create_indexer(indexer)
        assert result.name == indexer_name
        assert result.target_index_name == index_name
        assert result.data_source_name == datasource_name

        # Get indexer
        result = client.get_indexer(indexer_name)
        assert result.name == indexer_name

        # Run indexer
        client.run_indexer(indexer_name)
        assert client.get_indexer_status(indexer_name).status == 'running'

        # Reset indexer
        client.reset_indexer(indexer_name)
        assert client.get_indexer_status(indexer_name).last_result.status.lower() in ('inprogress', 'reset')

        # Get indexer status
        status = client.get_indexer_status(indexer_name)
        assert status.status is not None

        # List indexers
        indexer2_name = self._random_tag(prefix="sample-indexer2-")
        datasource2_name = self._random_tag(prefix="sample-datasource2-")
        index2_name = self._random_tag("hotels2-")
        indexer2 = self._prepare_indexer(search_endpoint, search_api_key, storage_cs, container_name, indexer2_name, datasource2_name, index2_name)
        client.create_indexer(indexer2)
        result = client.get_indexers()
        assert isinstance(result, list)
        assert len(result) == indexer_count + 2
        indexer_count = len(result)
        assert indexer_name in set(x.name for x in result)
        assert indexer2_name in set(x.name for x in result)

        # Delete indexer
        client.delete_indexer(indexer_name)
        client.delete_indexer(indexer2_name)
        assert len(client.get_indexers()) == indexer_count - 2

    @search_decorator
    @recorded_by_proxy
    def test_create_or_update_indexer(self, **kwargs):
        search_endpoint, search_api_key, storage_cs, container_name = self._parse_kwargs(**kwargs)
        indexer_name = self._random_tag(prefix="sample-indexer-")
        datasource_name = self._random_tag(prefix="sample-datasource-")
        index_name = self._random_tag("hotels-")
        client = SearchIndexerClient(search_endpoint, search_api_key)
        indexer = self._prepare_indexer(search_endpoint, search_api_key, storage_cs, container_name, indexer_name, datasource_name, index_name)

        start_count = len(client.get_indexers())
        client.create_indexer(indexer)
        assert(len(client.get_indexers())) == start_count + 1
        
        indexer.description = "updated"
        client.create_or_update_indexer(indexer)
        assert len(client.get_indexers()) == start_count + 1

        result = client.get_indexer(indexer_name)
        assert result.name == indexer_name
        assert result.description == "updated"

    @search_decorator
    @recorded_by_proxy
    def test_create_or_update_indexer_if_unchanged(self, **kwargs):
        search_endpoint, search_api_key, storage_cs, container_name = self._parse_kwargs(**kwargs)
        indexer_name = self._random_tag(prefix="sample-indexer-")
        datasource_name = self._random_tag(prefix="sample-datasource-")
        index_name = self._random_tag("hotels-")
        client = SearchIndexerClient(search_endpoint, search_api_key)
        indexer = self._prepare_indexer(search_endpoint, search_api_key, storage_cs, container_name, indexer_name, datasource_name, index_name)

        created = client.create_indexer(indexer)
        etag = created.e_tag

        indexer.description = "updated"
        client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.create_or_update_indexer(indexer, match_condition=MatchConditions.IfNotModified)

    @search_decorator
    @recorded_by_proxy
    def test_delete_indexer_if_unchanged(self, **kwargs):
        search_endpoint, search_api_key, storage_cs, container_name = self._parse_kwargs(**kwargs)
        indexer_name = self._random_tag(prefix="sample-indexer-")
        datasource_name = self._random_tag(prefix="sample-datasource-")
        index_name = self._random_tag("hotels-")
        client = SearchIndexerClient(search_endpoint, search_api_key)
        indexer = self._prepare_indexer(search_endpoint, search_api_key, storage_cs, container_name, indexer_name, datasource_name, index_name)

        result = client.create_indexer(indexer)
        etag = result.e_tag

        indexer.description = "updated"
        client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.delete_indexer(indexer, match_condition=MatchConditions.IfNotModified)
