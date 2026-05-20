# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchIndexerClient`` indexer operations."""

from __future__ import annotations

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerStatus,
)
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import live_test, make_index_client, make_indexer_client, safe_delete

DATA_SOURCE_TYPE = "azureblob"
INDEXER_DESCRIPTION = "Indexer description"
REPLACEMENT_INDEXER_DESCRIPTION = "Replacement indexer description"
STALE_INDEXER_ETAG = "stale-indexer-etag"


def _build_index(index_name: str) -> SearchIndex:
    return SearchIndex(
        name=index_name,
        fields=[
            SearchField(
                name="HotelId",
                type=SearchFieldDataType.STRING,
                key=True,
                searchable=False,
            )
        ],
    )


def _build_data_source_connection(
    data_source_connection_name: str,
    storage_connection_string: str,
    storage_container_name: str,
) -> SearchIndexerDataSourceConnection:
    return SearchIndexerDataSourceConnection(
        name=data_source_connection_name,
        type=DATA_SOURCE_TYPE,
        connection_string=storage_connection_string,
        container=SearchIndexerDataContainer(name=storage_container_name),
    )


def _resource_names(indexer_name: str) -> tuple[str, str]:
    scenario = indexer_name.removeprefix("indexer-")
    data_source_connection_name = f"data-source-connection-{scenario}"
    index_name = f"index-{scenario}"
    return data_source_connection_name, index_name


def _build_indexer(
    indexer_name: str,
    data_source_connection_name: str,
    index_name: str,
    *,
    description: str = INDEXER_DESCRIPTION,
) -> SearchIndexer:
    return SearchIndexer(
        name=indexer_name,
        data_source_name=data_source_connection_name,
        target_index_name=index_name,
        description=description,
    )


def _create_indexer_dependencies(
    client,
    index_client,
    storage_connection_string: str,
    storage_container_name: str,
    indexer_name: str,
) -> SearchIndexer:
    data_source_connection_name, index_name = _resource_names(indexer_name)
    client.create_data_source_connection(
        _build_data_source_connection(
            data_source_connection_name,
            storage_connection_string,
            storage_container_name,
        )
    )
    index_client.create_index(_build_index(index_name))
    return _build_indexer(indexer_name, data_source_connection_name, index_name)


def _delete_indexer_resources(client, index_client, indexer_name: str) -> None:
    data_source_connection_name, index_name = _resource_names(indexer_name)
    safe_delete(client.delete_indexer, indexer_name)
    safe_delete(client.delete_data_source_connection, data_source_connection_name)
    safe_delete(index_client.delete_index, index_name)


class TestSearchIndexerClientIndexer(AzureRecordedTestCase):
    @live_test()
    def test_create_indexer_returns_created_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-create"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            indexer = _create_indexer_dependencies(
                client,
                index_client,
                storage_connection_string,
                storage_container_name,
                indexer_name,
            )

            result = client.create_indexer(indexer)

            assert isinstance(result, SearchIndexer)
            assert result.name == indexer_name
            assert result.data_source_name == indexer.data_source_name
            assert result.target_index_name == indexer.target_index_name
            assert result.description == INDEXER_DESCRIPTION
            assert result.e_tag
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_get_indexer_returns_created_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-get"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            client.create_indexer(
                _create_indexer_dependencies(
                    client,
                    index_client,
                    storage_connection_string,
                    storage_container_name,
                    indexer_name,
                )
            )

            result = client.get_indexer(indexer_name)

            assert isinstance(result, SearchIndexer)
            assert result.name == indexer_name
            assert result.description == INDEXER_DESCRIPTION
            assert result.e_tag
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_get_indexers_and_names_return_created_resources(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        first_indexer_name = "indexer-list-first"
        second_indexer_name = "indexer-list-second"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            for indexer_name in [first_indexer_name, second_indexer_name]:
                client.create_indexer(
                    _create_indexer_dependencies(
                        client,
                        index_client,
                        storage_connection_string,
                        storage_container_name,
                        indexer_name,
                    )
                )

            indexers = client.get_indexers()
            indexer_names = client.get_indexer_names()

            assert isinstance(indexers, list)
            assert all(isinstance(result, SearchIndexer) for result in indexers)
            assert {first_indexer_name, second_indexer_name}.issubset({result.name for result in indexers})
            assert {first_indexer_name, second_indexer_name}.issubset(set(indexer_names))
        finally:
            _delete_indexer_resources(client, index_client, first_indexer_name)
            _delete_indexer_resources(client, index_client, second_indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_create_or_update_indexer_replaces_existing_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-create-or-update"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            indexer = _create_indexer_dependencies(
                client,
                index_client,
                storage_connection_string,
                storage_container_name,
                indexer_name,
            )
            client.create_or_update_indexer(indexer)
            indexer.description = REPLACEMENT_INDEXER_DESCRIPTION

            result = client.create_or_update_indexer(indexer)

            assert isinstance(result, SearchIndexer)
            assert result.name == indexer_name
            assert result.description == REPLACEMENT_INDEXER_DESCRIPTION
            assert client.get_indexer(indexer_name).description == REPLACEMENT_INDEXER_DESCRIPTION
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_create_or_update_indexer_if_unchanged_uses_model_etag(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-create-or-update-if-unchanged"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            indexer = client.create_or_update_indexer(
                _create_indexer_dependencies(
                    client,
                    index_client,
                    storage_connection_string,
                    storage_container_name,
                    indexer_name,
                )
            )
            indexer.description = REPLACEMENT_INDEXER_DESCRIPTION
            indexer.e_tag = STALE_INDEXER_ETAG

            with pytest.raises(HttpResponseError):
                client.create_or_update_indexer(indexer, match_condition=MatchConditions.IfNotModified)
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_delete_indexer_accepts_name(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-delete"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            client.create_indexer(
                _create_indexer_dependencies(
                    client,
                    index_client,
                    storage_connection_string,
                    storage_container_name,
                    indexer_name,
                )
            )

            client.delete_indexer(indexer_name)

            assert indexer_name not in client.get_indexer_names()
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_delete_indexer_if_unchanged_uses_model_etag(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-delete-if-unchanged"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            indexer = client.create_indexer(
                _create_indexer_dependencies(
                    client,
                    index_client,
                    storage_connection_string,
                    storage_container_name,
                    indexer_name,
                )
            )
            indexer.e_tag = STALE_INDEXER_ETAG

            with pytest.raises(HttpResponseError):
                client.delete_indexer(indexer, match_condition=MatchConditions.IfNotModified)

            assert indexer_name in client.get_indexer_names()
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_reset_indexer_accepts_name(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-reset"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            client.create_indexer(
                _create_indexer_dependencies(
                    client,
                    index_client,
                    storage_connection_string,
                    storage_container_name,
                    indexer_name,
                )
            )

            client.reset_indexer(indexer_name)
            result = client.get_indexer_status(indexer_name)

            assert isinstance(result, SearchIndexerStatus)
            assert result.name == indexer_name
            assert result.status is not None
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_run_indexer_updates_status(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-run"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            client.create_indexer(
                _create_indexer_dependencies(
                    client,
                    index_client,
                    storage_connection_string,
                    storage_container_name,
                    indexer_name,
                )
            )

            client.run_indexer(indexer_name)
            result = client.get_indexer_status(indexer_name)

            assert isinstance(result, SearchIndexerStatus)
            assert result.name == indexer_name
            assert result.status == "running"
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()

    @live_test()
    def test_get_indexer_status_returns_status_resource(self, endpoint, **kwargs):
        storage_connection_string = kwargs.get("search_storage_connection_string")
        storage_container_name = kwargs.get("search_storage_container_name")
        indexer_name = "indexer-status"
        client = make_indexer_client(endpoint)
        index_client = make_index_client(endpoint)

        try:
            client.create_indexer(
                _create_indexer_dependencies(
                    client,
                    index_client,
                    storage_connection_string,
                    storage_container_name,
                    indexer_name,
                )
            )

            result = client.get_indexer_status(indexer_name)

            assert isinstance(result, SearchIndexerStatus)
            assert result.name == indexer_name
            assert result.status is not None
        finally:
            _delete_indexer_resources(client, index_client, indexer_name)
            client.close()
            index_client.close()
