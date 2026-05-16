# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for search indexer model helper serialization."""

from __future__ import annotations

from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType,
)

DATA_SOURCE_NAME = "hotel-data-source"
CONNECTION_STRING = (
    "ResourceId=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/search/"
    "providers/Microsoft.Storage/storageAccounts/hotels"
)
CONTAINER_NAME = "hotel-documents"
REPLACEMENT_CONNECTION_STRING = "<unchanged>"


def create_data_source(connection_string=CONNECTION_STRING):
    return SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type=SearchIndexerDataSourceType.AZURE_BLOB,
        connection_string=connection_string,
        container=SearchIndexerDataContainer(name=CONTAINER_NAME),
    )


class TestSearchIndexerDataSourceConnectionSerialization:
    def test_connection_string_overload_serializes_as_nested_credentials(self):
        data_source = create_data_source()

        serialized = data_source.as_dict()

        assert serialized == {
            "name": DATA_SOURCE_NAME,
            "type": "azureblob",
            "credentials": {"connectionString": CONNECTION_STRING},
            "container": {"name": CONTAINER_NAME},
        }

    def test_connection_string_property_round_trips_through_credentials(self):
        data_source = create_data_source()

        data_source.connection_string = REPLACEMENT_CONNECTION_STRING

        assert data_source.connection_string == REPLACEMENT_CONNECTION_STRING
        assert data_source.credentials.connection_string == REPLACEMENT_CONNECTION_STRING
        assert data_source.as_dict()["credentials"] == {"connectionString": REPLACEMENT_CONNECTION_STRING}
