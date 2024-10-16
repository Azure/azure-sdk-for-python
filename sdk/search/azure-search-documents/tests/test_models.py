# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchResourceEncryptionKey,
    SearchIndexerSkillset,
    ShaperSkill,
    SearchIndexer,
)


def test_encryption_key_serialization():
    from azure.search.documents.indexes._generated.models import (
        SearchResourceEncryptionKey as SearchResourceEncryptionKeyGen,
    )

    container = SearchIndexerDataContainer(name="container_name")
    encryption_key = SearchResourceEncryptionKey(
        key_name="key",
        key_version="key_version",
        vault_uri="vault_uri",
        application_id="application_id",
    )
    data_source_connection = SearchIndexerDataSourceConnection(
        name="datasource-name",
        type="azureblob",
        connection_string="connection_string",
        container=container,
        encryption_key=encryption_key,
    )
    packed_data_source = data_source_connection._to_generated()
    assert isinstance(packed_data_source.encryption_key, SearchResourceEncryptionKeyGen)

    search_indexer = SearchIndexer(
        name="indexer-name",
        data_source_name="datasource-name",
        target_index_name="target-index-name",
        encryption_key=encryption_key,
    )
    packed_search_indexer = search_indexer._to_generated()
    assert isinstance(packed_search_indexer.encryption_key, SearchResourceEncryptionKeyGen)
