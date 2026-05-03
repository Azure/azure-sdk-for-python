# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchIndexerClient`` data source connection operations."""

from __future__ import annotations

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)
from devtools_testutils import AzureRecordedTestCase

from _search_helpers_async import live_test, make_indexer_client, safe_delete

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


class TestSearchIndexerClientDataSourceConnectionAsync(AzureRecordedTestCase):
    @live_test()
    async def test_create_data_source_connection_returns_created_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-create"
        client = make_indexer_client(endpoint)

        async with client:
            try:
                result = await client.create_data_source_connection(
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
                await safe_delete(client.delete_data_source_connection, data_source_connection_name)

    @live_test()
    async def test_get_data_source_connection_returns_created_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-get"
        client = make_indexer_client(endpoint)

        async with client:
            try:
                await client.create_data_source_connection(
                    _build_data_source_connection(
                        data_source_connection_name,
                        storage_connection_string,
                        storage_container_name,
                    )
                )

                result = await client.get_data_source_connection(data_source_connection_name)

                assert isinstance(result, SearchIndexerDataSourceConnection)
                assert result.name == data_source_connection_name
                assert result.description == DATA_SOURCE_DESCRIPTION
                assert result.e_tag
            finally:
                await safe_delete(client.delete_data_source_connection, data_source_connection_name)

    @live_test()
    async def test_get_data_source_connections_and_names_return_created_resources(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        first_data_source_connection_name = "data-source-connection-list-first"
        second_data_source_connection_name = "data-source-connection-list-second"
        client = make_indexer_client(endpoint)

        async with client:
            try:
                for data_source_connection_name in [first_data_source_connection_name, second_data_source_connection_name]:
                    await client.create_data_source_connection(
                        _build_data_source_connection(
                            data_source_connection_name,
                            storage_connection_string,
                            storage_container_name,
                        )
                    )

                data_source_connections = await client.get_data_source_connections()
                data_source_connection_names = await client.get_data_source_connection_names()

                assert isinstance(data_source_connections, list)
                assert all(isinstance(result, SearchIndexerDataSourceConnection) for result in data_source_connections)
                assert {first_data_source_connection_name, second_data_source_connection_name}.issubset(
                    {result.name for result in data_source_connections}
                )
                assert {first_data_source_connection_name, second_data_source_connection_name}.issubset(
                    set(data_source_connection_names)
                )
            finally:
                await safe_delete(client.delete_data_source_connection, first_data_source_connection_name)
                await safe_delete(client.delete_data_source_connection, second_data_source_connection_name)

    @live_test()
    async def test_create_or_update_data_source_connection_replaces_existing_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-create-or-update"
        client = make_indexer_client(endpoint)

        async with client:
            try:
                await client.create_or_update_data_source_connection(
                    _build_data_source_connection(
                        data_source_connection_name,
                        storage_connection_string,
                        storage_container_name,
                    )
                )
                result = await client.create_or_update_data_source_connection(
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
                existing = await client.get_data_source_connection(data_source_connection_name)
                assert existing.description == REPLACEMENT_DATA_SOURCE_DESCRIPTION
            finally:
                await safe_delete(client.delete_data_source_connection, data_source_connection_name)

    @live_test()
    async def test_create_or_update_data_source_connection_if_unchanged_uses_model_etag(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-create-or-update-if-unchanged"
        client = make_indexer_client(endpoint)

        async with client:
            try:
                data_source_connection = await client.create_or_update_data_source_connection(
                    _build_data_source_connection(
                        data_source_connection_name,
                        storage_connection_string,
                        storage_container_name,
                    )
                )
                original_e_tag = data_source_connection.e_tag

                await client.create_or_update_data_source_connection(
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
                    await client.create_or_update_data_source_connection(
                        data_source_connection,
                        match_condition=MatchConditions.IfNotModified,
                    )
            finally:
                await safe_delete(client.delete_data_source_connection, data_source_connection_name)

    @live_test()
    async def test_delete_data_source_connection_accepts_name(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-delete"
        client = make_indexer_client(endpoint)

        async with client:
            try:
                await client.create_data_source_connection(
                    _build_data_source_connection(
                        data_source_connection_name,
                        storage_connection_string,
                        storage_container_name,
                    )
                )

                await client.delete_data_source_connection(data_source_connection_name)

                assert data_source_connection_name not in await client.get_data_source_connection_names()
            finally:
                await safe_delete(client.delete_data_source_connection, data_source_connection_name)

    @live_test()
    async def test_delete_data_source_connection_if_unchanged_uses_model_etag(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        data_source_connection_name = "data-source-connection-delete-if-unchanged"
        client = make_indexer_client(endpoint)

        async with client:
            try:
                data_source_connection = await client.create_data_source_connection(
                    _build_data_source_connection(
                        data_source_connection_name,
                        storage_connection_string,
                        storage_container_name,
                    )
                )
                original_e_tag = data_source_connection.e_tag

                await client.create_or_update_data_source_connection(
                    _build_data_source_connection(
                        data_source_connection_name,
                        storage_connection_string,
                        storage_container_name,
                        description=REPLACEMENT_DATA_SOURCE_DESCRIPTION,
                    )
                )

                data_source_connection.e_tag = original_e_tag
                with pytest.raises(HttpResponseError):
                    await client.delete_data_source_connection(
                        data_source_connection,
                        match_condition=MatchConditions.IfNotModified,
                    )

                assert data_source_connection_name in await client.get_data_source_connection_names()
            finally:
                await safe_delete(client.delete_data_source_connection, data_source_connection_name)
