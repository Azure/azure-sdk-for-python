# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Opt-in ADLS Gen2 permission ingestion, periodic ACL refresh, permission resync,
    and permission-trimmed search/document lookup. This is NOT a basic Blob example.
    It creates and deletes only run-tagged Search resources, never storage files.

USAGE:
    python sample_indexer_permissions_async.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_API_KEY (an admin key).
    Queries use DefaultAzureCredential (azure-identity) and require Search Index
    Data Reader for that caller. Resource management still uses the admin key.
    Opt in with AZURE_SEARCH_RUN_PERMISSION_SAMPLE=true and set:
    AZURE_STORAGE_RESOURCE_ID_CONNECTION_STRING - ResourceId=/subscriptions/.../
        providers/Microsoft.Storage/storageAccounts/<account>/; (no storage keys)
    AZURE_STORAGE_CONTAINER - a dedicated ADLS Gen2 filesystem with hierarchical
        namespace enabled and text hotel files with real named-user/group ACLs
    AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION - a source user token/header value in
        the format required by the service; never print or commit this value

    Enable Search RBAC. Give the Search service managed identity Storage Blob Data
    Reader, including the permissions needed to read the filesystem and ACLs.
    Configure directory traversal and file read ACLs for the test users/groups.
    Optional AZURE_SEARCH_USER_ASSIGNED_IDENTITY selects an identity already
    attached to Search; AZURE_SEARCH_FEDERATED_IDENTITY_CLIENT_ID requires an
    already-configured federated trust.

    To demonstrate elevated reads, additionally set AZURE_SEARCH_ENABLE_ELEVATED_READ=true
    only with a caller having Search Index Data Contributor or a custom role with
    the elevated-read permission. Default is false.
    SAMPLE_RUN_TAG optionally supplies a unique name suffix.

    This sample submits a permission resync request; it does not modify storage
    ACLs or assert that changed permissions have propagated. Service acceptance,
    permission enforcement, and resync recording require these real prerequisites.
"""

import asyncio
import os

from sample_utils import cleanup_indexer_resources_async, get_sample_run_tag, wait_for_indexer_async


async def main():  # pylint: disable=too-many-locals
    variables = (
        "AZURE_STORAGE_RESOURCE_ID_CONNECTION_STRING",
        "AZURE_STORAGE_CONTAINER",
        "AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION",
    )
    if os.environ.get("AZURE_SEARCH_RUN_PERMISSION_SAMPLE", "").lower() != "true":
        print(
            "Skipping ADLS permission ingestion; set AZURE_SEARCH_RUN_PERMISSION_SAMPLE=true after provisioning ACLs."
        )
        return
    if not all(os.environ.get(name) for name in variables):
        raise ValueError("ADLS permission ingestion requires " + ", ".join(variables))

    # [START sample_indexer_permissions_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents.aio import SearchClient
    from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
    from azure.search.documents.indexes.models import (
        FieldMapping,
        FieldMappingFunction,
        IndexerPermissionOption,
        IndexerResyncBody,
        IndexerResyncOption,
        IndexingParameters,
        IndexingParametersConfiguration,
        SearchFieldDataType,
        SearchIndex,
        SearchIndexer,
        SearchIndexerDataContainer,
        SearchIndexerDataSourceConnection,
        SearchIndexerDataUserAssignedIdentity,
        SimpleField,
        SearchableField,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
    name = f"hotels-permissions-{get_sample_run_tag()}"
    identity = None
    if os.environ.get("AZURE_SEARCH_USER_ASSIGNED_IDENTITY"):
        identity = SearchIndexerDataUserAssignedIdentity(
            resource_id=os.environ["AZURE_SEARCH_USER_ASSIGNED_IDENTITY"],
            federated_identity_client_id=os.environ.get("AZURE_SEARCH_FEDERATED_IDENTITY_CLIENT_ID"),
        )
    async with SearchIndexClient(endpoint, credential) as index_client, SearchIndexerClient(
        endpoint, credential
    ) as indexer_client:
        try:
            await index_client.create_index(
                SearchIndex(
                    name=name,
                    permission_filter_option="enabled",
                    fields=[
                        SimpleField(name="id", type=SearchFieldDataType.STRING, key=True),
                        SearchableField(name="content"),
                        SimpleField(
                            name="UserIds",
                            type=SearchFieldDataType.Collection(SearchFieldDataType.STRING),
                            permission_filter="userIds",
                            filterable=True,
                            hidden=True,
                        ),
                        SimpleField(
                            name="GroupIds",
                            type=SearchFieldDataType.Collection(SearchFieldDataType.STRING),
                            permission_filter="groupIds",
                            filterable=True,
                            hidden=True,
                        ),
                        SimpleField(
                            name="RbacScope",
                            type=SearchFieldDataType.STRING,
                            permission_filter="rbacScope",
                            filterable=True,
                            hidden=True,
                        ),
                    ],
                )
            )
            await indexer_client.create_data_source_connection(
                SearchIndexerDataSourceConnection(
                    name=name,
                    type="adlsgen2",
                    connection_string=os.environ["AZURE_STORAGE_RESOURCE_ID_CONNECTION_STRING"],
                    container=SearchIndexerDataContainer(name=os.environ["AZURE_STORAGE_CONTAINER"]),
                    identity=identity,
                    indexer_permission_options=[
                        IndexerPermissionOption.USER_IDS,
                        IndexerPermissionOption.GROUP_IDS,
                        IndexerPermissionOption.RBAC_SCOPE,
                    ],
                )
            )
            await indexer_client.create_indexer(
                SearchIndexer(
                    name=name,
                    data_source_name=name,
                    target_index_name=name,
                    parameters=IndexingParameters(configuration=IndexingParametersConfiguration(refresh_all_acls=True)),
                    field_mappings=[
                        FieldMapping(
                            source_field_name="metadata_storage_path",
                            target_field_name="id",
                            mapping_function=FieldMappingFunction(name="base64Encode"),
                        ),
                        FieldMapping(source_field_name="metadata_user_ids", target_field_name="UserIds"),
                        FieldMapping(source_field_name="metadata_group_ids", target_field_name="GroupIds"),
                        FieldMapping(source_field_name="metadata_rbac_scope", target_field_name="RbacScope"),
                    ],
                )
            )
            await wait_for_indexer_async(indexer_client, name)

            async with DefaultAzureCredential() as query_credential, SearchClient(
                endpoint, name, query_credential
            ) as search_client:
                authorization = os.environ["AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION"]
                elevated = os.environ.get("AZURE_SEARCH_ENABLE_ELEVATED_READ", "").lower() == "true"
                results = await search_client.search(
                    search_text="hotel",
                    select=["id", "content"],
                    top=1,
                    query_source_authorization=authorization,
                    enable_elevated_read=elevated,
                )
                async for document in results:
                    found = await search_client.get_document(
                        document["id"],
                        selected_fields=["id", "content"],
                        query_source_authorization=authorization,
                        enable_elevated_read=elevated,
                    )
                    print(f"Accessible document: {found['id']}")

            await indexer_client.resync(name, IndexerResyncBody(options=[IndexerResyncOption.PERMISSIONS]))
            print("Submitted permission-only resync; this is not evidence of completed ACL propagation.")
        finally:
            await cleanup_indexer_resources_async(
                indexer_client, index_client, indexer_name=name, data_source_name=name, index_name=name
            )
    # [END sample_indexer_permissions_async]


if __name__ == "__main__":
    asyncio.run(main())
