# pylint: disable=line-too-long
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for hand-written overload contracts on indexer models.

These tests verify the public API promises declared by `@overload`
signatures in `azure.search.documents.indexes.models._patch`:

* `SearchIndexerDataSourceConnection(connection_string=...)` is a
  hand-written alternative to passing `credentials=DataSourceCredentials(...)`.
* `SearchResourceEncryptionKey()` accepts a no-arg construction and
  exposes `is_service_level_key` as an optional preview-only field.

If a future regeneration changes the generated parent so these
constructions fail or serialize differently, these tests catch the
silent regression before it reaches customers.
"""

from __future__ import annotations

from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType,
    SearchResourceEncryptionKey,
)

from _capabilities import require_capability


DATA_SOURCE_NAME = "hotel-data-source"
CONNECTION_STRING = (
    "ResourceId=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/search/"
    "providers/Microsoft.Storage/storageAccounts/hotels"
)
CONTAINER_NAME = "hotel-documents"


def create_data_source(connection_string=CONNECTION_STRING):
    return SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type=SearchIndexerDataSourceType.AZURE_BLOB,
        connection_string=connection_string,
        container=SearchIndexerDataContainer(name=CONTAINER_NAME),
    )


class TestSearchIndexerDataSourceConnectionOverloads:
    def test_connection_string_overload_serializes_as_nested_credentials(self):
        data_source = create_data_source()

        serialized = data_source.as_dict()

        assert serialized == {
            "name": DATA_SOURCE_NAME,
            "type": "azureblob",
            "credentials": {"connectionString": CONNECTION_STRING},
            "container": {"name": CONTAINER_NAME},
        }


class TestSearchResourceEncryptionKeyOverloads:
    def test_search_resource_encryption_key_allows_service_level_key_without_vault_details(self):
        require_capability("azure.search.documents.indexes.models.SearchResourceEncryptionKey.is_service_level_key")

        encryption_key = SearchResourceEncryptionKey()
        encryption_key.is_service_level_key = True

        assert encryption_key.as_dict() == {"isServiceLevelKey": True}
