# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from unittest import mock

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, ApiVersion
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)

CREDENTIAL = AzureKeyCredential(key="test_api_key")


class TestSearchIndexClient:
    def test_index_init(self):
        client = SearchIndexClient("endpoint", CREDENTIAL)
        assert client._headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_index_credential_roll(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexClient("endpoint", credential, retry_backoff_factor=60)
        assert client._headers == {
            "api-key": "old_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }
        credential.update("new_api_key")
        assert client._headers == {
            "api-key": "new_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_get_search_client(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexClient("endpoint", credential)
        search_client = client.get_search_client("index")
        assert isinstance(search_client, SearchClient)

    def test_get_search_client_inherit_api_version(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexClient("endpoint", credential, api_version=ApiVersion.V2020_06_30)
        search_client = client.get_search_client("index")
        assert isinstance(search_client, SearchClient)
        assert search_client._api_version == ApiVersion.V2020_06_30

    @mock.patch(
        "azure.search.documents.indexes._generated.operations._search_service_client_operations.SearchServiceClientOperationsMixin.get_service_statistics"
    )
    def test_get_service_statistics(self, mock_get_stats):
        client = SearchIndexClient("endpoint", CREDENTIAL)
        client.get_service_statistics()
        assert mock_get_stats.called
        assert mock_get_stats.call_args[0] == ()
        assert mock_get_stats.call_args[1] == {"headers": client._headers}

    @mock.patch(
        "azure.search.documents.indexes._generated.operations._search_service_client_operations.SearchServiceClientOperationsMixin.get_service_statistics"
    )
    def test_get_service_statistics_v2020_06_30(self, mock_get_stats):
        client = SearchIndexClient("endpoint", CREDENTIAL, api_version=ApiVersion.V2020_06_30)
        client.get_service_statistics()
        assert mock_get_stats.called
        assert mock_get_stats.call_args[0] == ()
        assert mock_get_stats.call_args[1] == {"headers": client._headers}

    def test_index_endpoint_https(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexClient("endpoint", credential)
        assert client._endpoint.startswith("https")

        client = SearchIndexClient("https://endpoint", credential)
        assert client._endpoint.startswith("https")

        with pytest.raises(ValueError):
            client = SearchIndexClient("http://endpoint", credential)

        with pytest.raises(ValueError):
            client = SearchIndexClient(12345, credential)


class TestSearchIndexerClient:
    def test_indexer_init(self):
        client = SearchIndexerClient("endpoint", CREDENTIAL)
        assert client._headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_indexer_credential_roll(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexerClient("endpoint", credential)
        assert client._headers == {
            "api-key": "old_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }
        credential.update("new_api_key")
        assert client._headers == {
            "api-key": "new_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_indexer_endpoint_https(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexerClient("endpoint", credential)
        assert client._endpoint.startswith("https")

        client = SearchIndexerClient("https://endpoint", credential)
        assert client._endpoint.startswith("https")

        with pytest.raises(ValueError):
            client = SearchIndexerClient("http://endpoint", credential)

        with pytest.raises(ValueError):
            client = SearchIndexerClient(12345, credential)

    def test_datasource_with_empty_connection_string(self):
        container = SearchIndexerDataContainer(name="searchcontainer")
        data_source_connection = SearchIndexerDataSourceConnection(
            name="test", type="azureblob", connection_string="", container=container
        )
        packed_data_source_connection = data_source_connection._to_generated()
        assert packed_data_source_connection.credentials.connection_string == "<unchanged>"
