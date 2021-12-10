# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from os import environ
from os.path import dirname, join, realpath

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, test_proxy

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

    def _prepare_indexer(self, endpoint, api_key, storage_cs, container_name, name="sample-indexer", datasource_name="sample-datasource", index_name="hotels"):
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
        return SearchIndexer(name=name, data_source_name=ds.name, target_index_name=result_index.name)

    @search_decorator
    @recorded_by_proxy
    def test_create_indexer(self, **kwargs):
        search_endpoint = kwargs.get('search_service_endpoint')
        search_api_key = kwargs.get('search_service_api_key')
        storage_cs = kwargs.get('search_storage_connection_string')
        container_name = kwargs.get('search_storage_container_name')

        client = SearchIndexerClient(search_endpoint, search_api_key)
        indexer = self._prepare_indexer(search_endpoint, search_api_key, storage_cs, container_name)
        result = client.create_indexer(indexer)
        assert result.name == "sample-indexer"
        assert result.target_index_name == "hotels"
        assert result.data_source_name == "sample-datasource"

    # @recorded_by_proxy
    # def test_delete_indexer(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer = self._prepare_indexer(endpoint, api_key)
    #     result = client.create_indexer(indexer)
    #     assert len(client.get_indexers()) == 1
    #     client.delete_indexer("sample-indexer")
    #     assert len(client.get_indexers()) == 0

    # @recorded_by_proxy
    # def test_reset_indexer(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer = self._prepare_indexer(endpoint, api_key)
    #     result = client.create_indexer(indexer)
    #     assert len(client.get_indexers()) == 1
    #     result = client.reset_indexer("sample-indexer")
    #     assert client.get_indexer_status("sample-indexer").last_result.status.lower() in ('inprogress', 'reset')

    # @recorded_by_proxy
    # def test_run_indexer(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer = self._prepare_indexer(endpoint, api_key)
    #     result = client.create_indexer(indexer)
    #     assert len(client.get_indexers()) == 1
    #     start = time.time()
    #     client.run_indexer("sample-indexer")
    #     assert client.get_indexer_status("sample-indexer").status == 'running'

    # @recorded_by_proxy
    # def test_get_indexer(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer = self._prepare_indexer(endpoint, api_key)
    #     created = client.create_indexer(indexer)
    #     result = client.get_indexer("sample-indexer")
    #     assert result.name == "sample-indexer"

    # @recorded_by_proxy
    # def test_list_indexer(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer1 = self._prepare_indexer(endpoint, api_key)
    #     indexer2 = self._prepare_indexer(endpoint, api_key, name="another-indexer", ds_name="another-datasource", id_name="another-index")
    #     created1 = client.create_indexer(indexer1)
    #     created2 = client.create_indexer(indexer2)
    #     result = client.get_indexers()
    #     assert isinstance(result, list)
    #     assert set(x.name for x in result) == {"sample-indexer", "another-indexer"}

    # @recorded_by_proxy
    # def test_create_or_update_indexer(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer = self._prepare_indexer(endpoint, api_key)
    #     created = client.create_indexer(indexer)
    #     assert len(client.get_indexers()) == 1
    #     indexer.description = "updated"
    #     client.create_or_update_indexer(indexer)
    #     assert len(client.get_indexers()) == 1
    #     result = client.get_indexer("sample-indexer")
    #     assert result.name == "sample-indexer"
    #     assert result.description == "updated"

    # @recorded_by_proxy
    # def test_get_indexer_status(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer = self._prepare_indexer(endpoint, api_key)
    #     result = client.create_indexer(indexer)
    #     status = client.get_indexer_status("sample-indexer")
    #     assert status.status is not None

    # @recorded_by_proxy
    # def test_create_or_update_indexer_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
    #     client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
    #     indexer = self._prepare_indexer(endpoint, api_key)
    #     created = client.create_indexer(indexer)
    #     etag = created.e_tag


    #     indexer.description = "updated"
    #     client.create_or_update_indexer(indexer)

    #     indexer.e_tag = etag
    #     with pytest.raises(HttpResponseError):
    #         client.create_or_update_indexer(indexer, match_condition=MatchConditions.IfNotModified)

    # @search_decorator
    # @recorded_by_proxy
    # def test_delete_indexer_if_unchanged(self, **kwargs):
    #     search_endpoint = kwargs.get('search_service_endpoint')
    #     search_api_key = kwargs.get('search_service_api_key')
    #     storage_cs = kwargs.get('search_storage_connection_string')
    #     container = kwargs.get('search_storage_container_name')

    #     client = SearchIndexerClient(search_endpoint, AzureKeyCredential(search_api_key))
    #     indexer = self._prepare_indexer(search_endpoint, search_api_key, storage_cs, container)
    #     result = client.create_indexer(indexer)
    #     etag = result.e_tag

    #     indexer.description = "updated"
    #     client.create_or_update_indexer(indexer)

    #     indexer.e_tag = etag
    #     with pytest.raises(HttpResponseError):
    #         client.delete_indexer(indexer, match_condition=MatchConditions.IfNotModified)
