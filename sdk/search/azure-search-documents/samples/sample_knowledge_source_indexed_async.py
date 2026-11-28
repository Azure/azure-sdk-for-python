# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Configure indexed SQL, indexed SharePoint, and web knowledge sources, then
    retrieve evidence with source-specific controls. Each scenario is opt-in.
    Only this run's knowledge bases and sources are deleted.

USAGE:
    python sample_knowledge_source_indexed_async.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_API_KEY (an admin key).
    For indexed sources, set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    and AZURE_OPENAI_EMBEDDING_MODEL. Grant the Search managed identity Cognitive
    Services OpenAI User on that resource.

    SQL: AZURE_SQL_CONNECTION_STRING and AZURE_SQL_TABLE_OR_VIEW. Provision a hotel
    table with a primary key and HotelName/Description text columns; optional
    AZURE_SQL_HIGH_WATER_MARK_COLUMN must be a suitable change-tracking column.
    The connection string may use managed identity; grant its identity SELECT.

    SharePoint: AZURE_SHAREPOINT_CONNECTION_STRING, using the service-supported
    SharePointOnlineEndpoint/ApplicationId/TenantId authentication configuration.
    Preconfigure the app's SharePoint read permissions and consent. This example
    selects defaultSiteLibrary and ingests user/group permissions.
    If using a user-assigned identity, set AZURE_SEARCH_USER_ASSIGNED_IDENTITY;
    optionally set AZURE_SEARCH_FEDERATED_IDENTITY_CLIENT_ID for a preconfigured
    federated identity. These identities and trust relationships are prerequisites.
    Permission-trimmed retrieval also needs AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION
    in the header format expected by the configured source.
    Optional AZURE_SHAREPOINT_APPLICATION_ID and AZURE_SHAREPOINT_FEDERATED_CREDENTIAL_ID
    enable a separate permission-index schema example. AZURE_SHAREPOINT_TENANT_ID
    optionally selects its tenant. This creates an empty index, not an indexer.

    Web: explicitly set AZURE_SEARCH_RUN_WEB_SAMPLE=true on a service supporting
    web knowledge sources. The request can incur web retrieval charges.
    SAMPLE_RUN_TAG optionally supplies a unique resource-name suffix.
"""

import asyncio
import os

from sample_utils import (
    cleanup_resources_async,
    get_sample_run_tag,
    print_retrieval_summary,
    wait_for_knowledge_source_active_async,
)


async def configure_sharepoint_permission_index_async():
    variables = ("AZURE_SHAREPOINT_APPLICATION_ID", "AZURE_SHAREPOINT_FEDERATED_CREDENTIAL_ID")
    if not all(os.environ.get(name) for name in variables):
        print("Skipping SharePoint permission schema; set " + ", ".join(variables))
        return

    # [START configure_sharepoint_permission_index_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchFieldDataType,
        SearchIndex,
        SharePointConnectorAppRegistration,
        SimpleField,
    )

    index_name = f"hotels-sharepoint-permissions-{get_sample_run_tag()}"
    index = SearchIndex(
        name=index_name,
        permission_filter_option="enabled",
        share_point_connector_app_registration=SharePointConnectorAppRegistration(
            application_id=os.environ["AZURE_SHAREPOINT_APPLICATION_ID"],
            federated_credential_id=os.environ["AZURE_SHAREPOINT_FEDERATED_CREDENTIAL_ID"],
            tenant_id=os.environ.get("AZURE_SHAREPOINT_TENANT_ID"),
        ),
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.STRING, key=True),
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
                name="OrganizationLinkExpires",
                type=SearchFieldDataType.DATE_TIME_OFFSET,
                organization_access_expiration=True,
                filterable=True,
                hidden=True,
            ),
            SimpleField(
                name="SharePointSiteUrl",
                type=SearchFieldDataType.STRING,
                sharepoint_site_url=True,
                filterable=True,
                hidden=True,
            ),
        ],
    )
    async with SearchIndexClient(
        os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"], AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
    ) as index_client:
        try:
            created = await index_client.create_index(index)
            print(f"Configured SharePoint permission schema: {created.name}")
        finally:
            await cleanup_resources_async(index_client, index_name=index_name)
    # [END configure_sharepoint_permission_index_async]


async def main():  # pylint: disable=too-many-locals
    # [START sample_knowledge_source_indexed_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        ContentColumnMapping,
        EmbeddingColumnMapping,
        IndexedSharePointKnowledgeSource,
        IndexedSharePointKnowledgeSourceParameters,
        IndexedSqlKnowledgeSource,
        IndexedSqlKnowledgeSourceParameters,
        KnowledgeBase,
        KnowledgeSource,
        KnowledgeSourceReference,
        SearchIndexerDataUserAssignedIdentity,
        WebKnowledgeSource,
        WebKnowledgeSourceDomain,
        WebKnowledgeSourceDomains,
        WebKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        IndexedSharePointKnowledgeSourceParams,
        IndexedSqlKnowledgeSourceParams,
        KnowledgeBaseIndexedSharePointActivityRecord,
        KnowledgeBaseIndexedSharePointReference,
        KnowledgeBaseIndexedSqlActivityRecord,
        KnowledgeBaseIndexedSqlReference,
        KnowledgeBaseWebActivityRecord,
        KnowledgeBaseWebReference,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
        KnowledgeSourceAzureOpenAIVectorizer,
        KnowledgeSourceIngestionParameters,
        KnowledgeSourceParams,
        WebKnowledgeSourceParams,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
    run_tag = get_sample_run_tag()
    sources: list[tuple[KnowledgeSource, KnowledgeSourceParams]] = []
    embedding_variables = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "AZURE_OPENAI_EMBEDDING_MODEL")
    embedding = None
    if all(os.environ.get(name) for name in embedding_variables):
        embedding = KnowledgeSourceAzureOpenAIVectorizer(
            azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                deployment_name=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
                model_name=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
            )
        )

    if embedding and os.environ.get("AZURE_SQL_CONNECTION_STRING") and os.environ.get("AZURE_SQL_TABLE_OR_VIEW"):
        sql_source = IndexedSqlKnowledgeSource(
            name=f"hotels-sql-{run_tag}",
            indexed_sql_parameters=IndexedSqlKnowledgeSourceParameters(
                connection_string=os.environ["AZURE_SQL_CONNECTION_STRING"],
                table_or_view=os.environ["AZURE_SQL_TABLE_OR_VIEW"],
                high_water_mark_column_name=os.environ.get("AZURE_SQL_HIGH_WATER_MARK_COLUMN"),
                content_columns=[
                    ContentColumnMapping(name="HotelName", source_field="HotelName", search_field_type="Edm.String"),
                    ContentColumnMapping(
                        name="Description", source_field="Description", search_field_type="Edm.String"
                    ),
                ],
                embedding_columns=[EmbeddingColumnMapping(name="DescriptionVector", source_field="Description")],
                ingestion_parameters=KnowledgeSourceIngestionParameters(
                    content_extraction_mode="minimal", embedding_model=embedding
                ),
            ),
        )
        sources.append(
            (
                sql_source,
                IndexedSqlKnowledgeSourceParams(
                    knowledge_source_name=sql_source.name,
                    include_references=True,
                    include_reference_source_data=True,
                    always_query_source=True,
                    fail_on_error=True,
                    max_output_documents=3,
                ),
            )
        )
    else:
        print("Skipping indexed SQL; configure the SQL table, connection, and embedding deployment.")

    if embedding and os.environ.get("AZURE_SHAREPOINT_CONNECTION_STRING"):
        identity = None
        if os.environ.get("AZURE_SEARCH_USER_ASSIGNED_IDENTITY"):
            identity = SearchIndexerDataUserAssignedIdentity(
                resource_id=os.environ["AZURE_SEARCH_USER_ASSIGNED_IDENTITY"],
                federated_identity_client_id=os.environ.get("AZURE_SEARCH_FEDERATED_IDENTITY_CLIENT_ID"),
            )
        sharepoint_source = IndexedSharePointKnowledgeSource(
            name=f"hotels-sharepoint-{run_tag}",
            indexed_share_point_parameters=IndexedSharePointKnowledgeSourceParameters(
                connection_string=os.environ["AZURE_SHAREPOINT_CONNECTION_STRING"],
                container_name="defaultSiteLibrary",
                ingestion_parameters=KnowledgeSourceIngestionParameters(
                    embedding_model=embedding,
                    identity=identity,
                    ingestion_permission_options=["userIds", "groupIds"],
                    content_extraction_mode="minimal",
                ),
            ),
        )
        sources.append(
            (
                sharepoint_source,
                IndexedSharePointKnowledgeSourceParams(
                    knowledge_source_name=sharepoint_source.name,
                    include_references=True,
                    include_reference_source_data=True,
                    always_query_source=True,
                    fail_on_error=True,
                    max_output_documents=3,
                ),
            )
        )
    else:
        print("Skipping indexed SharePoint; configure the connector app, connection, and embedding deployment.")

    if os.environ.get("AZURE_SEARCH_RUN_WEB_SAMPLE", "").lower() == "true":
        web_source = WebKnowledgeSource(
            name=f"hotels-web-{run_tag}",
            web_parameters=WebKnowledgeSourceParameters(
                domains=WebKnowledgeSourceDomains(
                    allowed_domains=[WebKnowledgeSourceDomain(address="learn.microsoft.com", include_subpages=True)]
                ),
                language="en",
                market="en-US",
                count=3,
                freshness="Month",
            ),
        )
        sources.append(
            (
                web_source,
                WebKnowledgeSourceParams(
                    knowledge_source_name=web_source.name,
                    include_references=True,
                    always_query_source=True,
                    fail_on_error=True,
                    max_output_documents=3,
                    language="en",
                    market="en-US",
                    count=3,
                    freshness="Month",
                ),
            )
        )
    else:
        print("Skipping web retrieval; set AZURE_SEARCH_RUN_WEB_SAMPLE=true to opt in.")

    async with SearchIndexClient(endpoint, credential) as index_client:
        for source, source_params in sources:
            base_name = f"{source.name}-kb"
            try:
                await index_client.create_or_update_knowledge_source(source)
                await wait_for_knowledge_source_active_async(index_client, source.name)
                await index_client.create_or_update_knowledge_base(
                    KnowledgeBase(
                        name=base_name,
                        knowledge_sources=[KnowledgeSourceReference(name=source.name)],
                        output_mode="extractiveData",
                        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                    )
                )
                async with KnowledgeBaseRetrievalClient(
                    endpoint, credential=credential, knowledge_base_name=base_name
                ) as retrieval_client:
                    result = await retrieval_client.retrieve(
                        KnowledgeBaseRetrievalRequest(
                            intents=[KnowledgeRetrievalSemanticIntent(search="Find hotel information")],
                            knowledge_source_params=[source_params],
                            include_activity=True,
                            output_mode="extractiveData",
                            max_output_documents=3,
                        ),
                        query_source_authorization=os.environ.get("AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION"),
                    )
                    print_retrieval_summary(result)
                    for activity in result.activity or []:
                        if isinstance(
                            activity,
                            (
                                KnowledgeBaseIndexedSqlActivityRecord,
                                KnowledgeBaseIndexedSharePointActivityRecord,
                                KnowledgeBaseWebActivityRecord,
                            ),
                        ):
                            print(f"Source: {activity.knowledge_source_name}; documents: {activity.count}")
                            print(f"Activity period: {activity.started_at} through {activity.completed_at}")
                    for reference in result.references or []:
                        if isinstance(
                            reference,
                            (
                                KnowledgeBaseIndexedSqlReference,
                                KnowledgeBaseIndexedSharePointReference,
                            ),
                        ):
                            print(f"Search-owned citation URL: {reference.citation_url}")
                        elif isinstance(reference, KnowledgeBaseWebReference):
                            print(f"Web citation: {reference.title}: {reference.url}")
                        print(f"Source data: {reference.source_data}")
            finally:
                await cleanup_resources_async(
                    index_client, knowledge_base_name=base_name, knowledge_source_name=source.name
                )
    # [END sample_knowledge_source_indexed_async]


async def run():
    await main()
    await configure_sharepoint_permission_index_async()


if __name__ == "__main__":
    asyncio.run(run())
