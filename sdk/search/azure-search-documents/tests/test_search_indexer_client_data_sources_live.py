# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchIndexerClient`` data source connection operations."""

from __future__ import annotations

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import live_test, make_indexer_client, safe_delete

DATA_SOURCE_TYPE = "azureblob"
DATA_SOURCE_DESCRIPTION = "Data source description"
REPLACEMENT_DATA_SOURCE_DESCRIPTION = "Replacement data source description"


def _build_data_source_connection(
    data_source_connection_name: str,
    storage_connection_string: str,
    storage_container_name: str,
    *,
    description: str = DATA_SOURCE_DESCRIPTION,
) -> SearchIndexerDataSourceConnection:
    return SearchIndexerDataSourceConnection(
        name=data_source_connection_name,
        type=DATA_SOURCE_TYPE,
        connection_string=storage_connection_string,
        container=SearchIndexerDataContainer(name=storage_container_name),
        description=description,
    )


class TestSearchIndexerClientDataSourceConnection(AzureRecordedTestCase):
    @live_test()
    def test_create_data_source_connection_returns_created_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-create"
        client = make_indexer_client(endpoint)

        try:
            result = client.create_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                )
            )

            assert isinstance(result, SearchIndexerDataSourceConnection)
            assert result.name == data_source_connection_name
            assert result.type == DATA_SOURCE_TYPE
            assert result.description == DATA_SOURCE_DESCRIPTION
            assert result.e_tag
        finally:
            safe_delete(client.delete_data_source_connection, data_source_connection_name)
            client.close()

    @live_test()
    def test_get_data_source_connection_returns_created_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-get"
        client = make_indexer_client(endpoint)

        try:
            client.create_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                )
            )

            result = client.get_data_source_connection(data_source_connection_name)

            assert isinstance(result, SearchIndexerDataSourceConnection)
            assert result.name == data_source_connection_name
            assert result.description == DATA_SOURCE_DESCRIPTION
            assert result.e_tag
        finally:
            safe_delete(client.delete_data_source_connection, data_source_connection_name)
            client.close()

    @live_test()
    def test_get_data_source_connections_and_names_return_created_resources(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        first_data_source_connection_name = "data-source-connection-list-first"
        second_data_source_connection_name = "data-source-connection-list-second"
        client = make_indexer_client(endpoint)

        try:
            for data_source_connection_name in [first_data_source_connection_name, second_data_source_connection_name]:
                client.create_data_source_connection(
                    _build_data_source_connection(
                        data_source_connection_name,
                        storage_connection_string,
                        storage_container_name,
                    )
                )

            data_source_connections = client.get_data_source_connections()
            data_source_connection_names = client.get_data_source_connection_names()

            assert isinstance(data_source_connections, list)
            assert all(isinstance(result, SearchIndexerDataSourceConnection) for result in data_source_connections)
            assert {first_data_source_connection_name, second_data_source_connection_name}.issubset(
                {result.name for result in data_source_connections}
            )
            assert {first_data_source_connection_name, second_data_source_connection_name}.issubset(
                set(data_source_connection_names)
            )
        finally:
            safe_delete(client.delete_data_source_connection, first_data_source_connection_name)
            safe_delete(client.delete_data_source_connection, second_data_source_connection_name)
            client.close()

    @live_test()
    def test_create_or_update_data_source_connection_replaces_existing_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-create-or-update"
        client = make_indexer_client(endpoint)

        try:
            client.create_or_update_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                )
            )
            result = client.create_or_update_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                    description=REPLACEMENT_DATA_SOURCE_DESCRIPTION,
                )
            )

            assert isinstance(result, SearchIndexerDataSourceConnection)
            assert result.name == data_source_connection_name
            assert result.description == REPLACEMENT_DATA_SOURCE_DESCRIPTION
            assert client.get_data_source_connection(data_source_connection_name).description == REPLACEMENT_DATA_SOURCE_DESCRIPTION
        finally:
            safe_delete(client.delete_data_source_connection, data_source_connection_name)
            client.close()

    @live_test()
    def test_create_or_update_data_source_connection_if_unchanged_uses_model_etag(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-create-or-update-if-unchanged"
        client = make_indexer_client(endpoint)

        try:
            data_source_connection = client.create_or_update_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                )
            )
            original_e_tag = data_source_connection.e_tag

            client.create_or_update_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                    description=REPLACEMENT_DATA_SOURCE_DESCRIPTION,
                )
            )

            data_source_connection.description = DATA_SOURCE_DESCRIPTION
            data_source_connection.e_tag = original_e_tag
            with pytest.raises(HttpResponseError):
                client.create_or_update_data_source_connection(
                    data_source_connection,
                    match_condition=MatchConditions.IfNotModified,
                )
        finally:
            safe_delete(client.delete_data_source_connection, data_source_connection_name)
            client.close()

    @live_test()
    def test_delete_data_source_connection_accepts_name(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-delete"
        client = make_indexer_client(endpoint)

        try:
            client.create_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                )
            )

            client.delete_data_source_connection(data_source_connection_name)

            assert data_source_connection_name not in client.get_data_source_connection_names()
        finally:
            safe_delete(client.delete_data_source_connection, data_source_connection_name)
            client.close()

    @live_test()
    def test_delete_data_source_connection_if_unchanged_uses_model_etag(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-delete-if-unchanged"
        client = make_indexer_client(endpoint)

        try:
            data_source_connection = client.create_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                )
            )
            original_e_tag = data_source_connection.e_tag

            client.create_or_update_data_source_connection(
                _build_data_source_connection(
                    data_source_connection_name,
                    storage_connection_string,
                    storage_container_name,
                    description=REPLACEMENT_DATA_SOURCE_DESCRIPTION,
                )
            )

            data_source_connection.e_tag = original_e_tag
            with pytest.raises(HttpResponseError):
                client.delete_data_source_connection(
                    data_source_connection,
                    match_condition=MatchConditions.IfNotModified,
                )

            assert data_source_connection_name in client.get_data_source_connection_names()
        finally:
            safe_delete(client.delete_data_source_connection, data_source_connection_name)
            client.close()
