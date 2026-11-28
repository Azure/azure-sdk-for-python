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
* Both data source constructor overloads accept nested models and TypedDicts.
* `SearchResourceEncryptionKey` accepts nested credentials and identity as
  models or TypedDicts, as well as flattened application credentials.
* `SearchResourceEncryptionKey()` accepts a no-arg construction and
  exposes `is_service_level_key` as an optional preview-only field.

If a future regeneration changes the generated parent so these
constructions fail or serialize differently, these tests catch the
silent regression before it reaches customers.
"""

from __future__ import annotations

import pytest

from azure.search.documents.indexes import types as index_types
from azure.search.documents.indexes.models import (
    AzureActiveDirectoryApplicationCredentials,
    DataSourceCredentials,
    HighWaterMarkChangeDetectionPolicy,
    SearchIndexerDataContainer,
    SearchIndexerDataNoneIdentity,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType,
    SearchIndexerDataUserAssignedIdentity,
    SearchResourceEncryptionKey,
    SoftDeleteColumnDeletionDetectionPolicy,
)

from _capabilities import require_capability

DATA_SOURCE_NAME = "hotel-data-source"
CONNECTION_STRING = (
    "ResourceId=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/search/"
    "providers/Microsoft.Storage/storageAccounts/hotels"
)
CONTAINER_NAME = "hotel-documents"
APPLICATION_ID = "00000000-0000-0000-0000-000000000000"
APPLICATION_SECRET = "not-a-real-application-secret"
KEY_NAME = "test-key"
VAULT_URI = "https://test-vault.vault.azure.net"
USER_ASSIGNED_IDENTITY = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/search/"
    "providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-identity"
)


def create_encryption_key_input() -> index_types.SearchResourceEncryptionKey:
    return {
        "keyVaultKeyName": KEY_NAME,
        "keyVaultKeyVersion": "test-version",
        "keyVaultUri": VAULT_URI,
        "accessCredentials": {"applicationId": APPLICATION_ID, "applicationSecret": APPLICATION_SECRET},
        "identity": {
            "@odata.type": "#Microsoft.Azure.Search.DataUserAssignedIdentity",
            "userAssignedIdentity": USER_ASSIGNED_IDENTITY,
        },
    }


def create_data_source_input() -> index_types.SearchIndexerDataSourceConnection:
    return {
        "name": DATA_SOURCE_NAME,
        "type": "azureblob",
        "credentials": {"connectionString": CONNECTION_STRING},
        "container": {"name": CONTAINER_NAME},
        "description": "Test data source",
        "identity": {"@odata.type": "#Microsoft.Azure.Search.DataNoneIdentity"},
        "indexerPermissionOptions": [],
        "dataChangeDetectionPolicy": {
            "@odata.type": "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy",
            "highWaterMarkColumnName": "updated_at",
        },
        "dataDeletionDetectionPolicy": {
            "@odata.type": "#Microsoft.Azure.Search.SoftDeleteColumnDeletionDetectionPolicy",
            "softDeleteColumnName": "is_deleted",
            "softDeleteMarkerValue": "true",
        },
        "@odata.etag": '"test-etag"',
        "encryptionKey": create_encryption_key_input(),
    }


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

    @pytest.mark.parametrize("flattened", [False, True])
    def test_search_indexer_data_source_connection_accepts_nested_typed_dicts(self, flattened: bool) -> None:
        payload = create_data_source_input()
        if flattened:
            data_source = SearchIndexerDataSourceConnection(
                name=payload["name"],
                type=payload["type"],
                connection_string=payload["credentials"]["connectionString"],
                container=payload["container"],
                description=payload["description"],
                identity=payload["identity"],
                indexer_permission_options=payload["indexerPermissionOptions"],
                data_change_detection_policy=payload["dataChangeDetectionPolicy"],
                data_deletion_detection_policy=payload["dataDeletionDetectionPolicy"],
                e_tag=payload["@odata.etag"],
                encryption_key=payload["encryptionKey"],
            )
        else:
            data_source = SearchIndexerDataSourceConnection(
                name=payload["name"],
                type=payload["type"],
                credentials=payload["credentials"],
                container=payload["container"],
                description=payload["description"],
                identity=payload["identity"],
                indexer_permission_options=payload["indexerPermissionOptions"],
                data_change_detection_policy=payload["dataChangeDetectionPolicy"],
                data_deletion_detection_policy=payload["dataDeletionDetectionPolicy"],
                e_tag=payload["@odata.etag"],
                encryption_key=payload["encryptionKey"],
            )

        assert data_source.as_dict() == payload
        assert data_source.credentials.connection_string == CONNECTION_STRING
        assert data_source.container.name == CONTAINER_NAME
        assert SearchIndexerDataSourceConnection(payload).as_dict() == payload

    def test_search_indexer_data_source_connection_preserves_nested_model_inputs(self) -> None:
        data_source = SearchIndexerDataSourceConnection(
            name=DATA_SOURCE_NAME,
            type=SearchIndexerDataSourceType.AZURE_BLOB,
            credentials=DataSourceCredentials(connection_string=CONNECTION_STRING),
            container=SearchIndexerDataContainer(name=CONTAINER_NAME),
            description="Test data source",
            identity=SearchIndexerDataNoneIdentity(),
            indexer_permission_options=[],
            data_change_detection_policy=HighWaterMarkChangeDetectionPolicy(high_water_mark_column_name="updated_at"),
            data_deletion_detection_policy=SoftDeleteColumnDeletionDetectionPolicy(
                soft_delete_column_name="is_deleted", soft_delete_marker_value="true"
            ),
            e_tag='"test-etag"',
            encryption_key=SearchResourceEncryptionKey(create_encryption_key_input()),
        )

        assert data_source.as_dict() == create_data_source_input()


class TestSearchResourceEncryptionKeyOverloads:
    @pytest.mark.parametrize("input_form", ["model", "typed_dict", "flattened"])
    def test_search_resource_encryption_key_nested_and_flattened_inputs_are_equivalent(self, input_form: str) -> None:
        payload = create_encryption_key_input()
        if input_form == "model":
            encryption_key = SearchResourceEncryptionKey(
                key_name=KEY_NAME,
                vault_uri=VAULT_URI,
                key_version="test-version",
                access_credentials=AzureActiveDirectoryApplicationCredentials(
                    application_id=APPLICATION_ID, application_secret=APPLICATION_SECRET
                ),
                identity=SearchIndexerDataUserAssignedIdentity(resource_id=USER_ASSIGNED_IDENTITY),
            )
        elif input_form == "typed_dict":
            encryption_key = SearchResourceEncryptionKey(
                key_name=KEY_NAME,
                vault_uri=VAULT_URI,
                key_version="test-version",
                access_credentials=payload["accessCredentials"],
                identity=payload["identity"],
            )
        else:
            encryption_key = SearchResourceEncryptionKey(
                key_name=KEY_NAME,
                vault_uri=VAULT_URI,
                key_version="test-version",
                application_id=APPLICATION_ID,
                application_secret=APPLICATION_SECRET,
                identity=payload["identity"],
            )

        assert encryption_key.as_dict() == payload
        assert encryption_key.application_id == APPLICATION_ID
        assert encryption_key.application_secret == APPLICATION_SECRET
        assert SearchResourceEncryptionKey(payload).as_dict() == payload

    def test_search_resource_encryption_key_retains_optional_vault_details(self) -> None:
        assert SearchResourceEncryptionKey().as_dict() == {}
        assert SearchResourceEncryptionKey(key_name=None, vault_uri=None).as_dict() == {}
        assert SearchResourceEncryptionKey(
            application_id=APPLICATION_ID, application_secret=APPLICATION_SECRET
        ).as_dict() == {"accessCredentials": {"applicationId": APPLICATION_ID, "applicationSecret": APPLICATION_SECRET}}

    def test_search_resource_encryption_key_allows_service_level_key_without_vault_details(self):
        require_capability("azure.search.documents.indexes.models.SearchResourceEncryptionKey.is_service_level_key")

        encryption_key = SearchResourceEncryptionKey()
        encryption_key.is_service_level_key = True

        assert encryption_key.as_dict() == {"isServiceLevelKey": True}
