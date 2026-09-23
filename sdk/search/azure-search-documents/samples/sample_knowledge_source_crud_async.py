# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, list, and delete a knowledge source.
    A knowledge source is a reusable reference to source data (such as a search index)
    used by a knowledge base for agentic retrieval.

    To query a knowledge base built on this knowledge source, see
    sample_agentic_retrieval_async.py.

USAGE:
    python sample_knowledge_source_crud_async.py

    Set the following environment variables before running the standard CRUD scenarios:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_SEARCH_INDEX_NAME - target search index name. The index must have a
        semantic configuration (e.g., "hotels-sample-index").

    The private Blob ingestion scenario runs only when all of these optional variables are set:
    4) AZURE_STORAGE_RESOURCE_ID_CONNECTION_STRING - ResourceId connection string for private Blob ingestion
    5) AZURE_STORAGE_CONTAINER - Blob container with supported and fallback language fixtures
    6) AZURE_SEARCH_USER_ASSIGNED_IDENTITY - user-assigned identity assigned to the Search service
    7) AZURE_AI_SERVICES_ENDPOINT - AI Services endpoint used for language detection
    8) AZURE_AI_SERVICES_API_KEY - AI Services API key
    9) AZURE_SEARCH_EXPECTED_ANALYZER - analyzer expected for the supported-language fixture
    10) AZURE_SEARCH_EXPECTED_FALLBACK_ANALYZER - analyzer expected for the fallback fixture

    The storage and AI Services shared private links must already be approved. Shared private-link
    resources are control-plane resources and are not configured by this data-plane sample.
"""

import asyncio
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]
knowledge_source_name = "hotels-sample-knowledge-source"
private_blob_source_name = "hotels-private-blob-knowledge-source"
private_blob_environment_variables = (
    "AZURE_STORAGE_RESOURCE_ID_CONNECTION_STRING",
    "AZURE_STORAGE_CONTAINER",
    "AZURE_SEARCH_USER_ASSIGNED_IDENTITY",
    "AZURE_AI_SERVICES_ENDPOINT",
    "AZURE_AI_SERVICES_API_KEY",
    "AZURE_SEARCH_EXPECTED_ANALYZER",
    "AZURE_SEARCH_EXPECTED_FALLBACK_ANALYZER",
)


async def create_knowledge_source_async():
    # [START create_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
        ),
    )

    async with index_client:
        result = await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Created: knowledge source '{result.name}' -> index '{index_name}'")
    # [END create_knowledge_source_async]


async def get_knowledge_source_async():
    # [START get_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        result = await index_client.get_knowledge_source(knowledge_source_name)
    print(f"Retrieved: knowledge source '{result.name}'")
    # [END get_knowledge_source_async]


async def update_knowledge_source_async():
    # [START update_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndexFieldReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceFilterHint,
        SearchIndexKnowledgeSourceParameters,
        SearchIndexKnowledgeSourceQueryHints,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        description="Updated with source data fields",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            source_data_fields=[
                SearchIndexFieldReference(name="HotelId"),
                SearchIndexFieldReference(name="HotelName"),
            ],
            query_hints=SearchIndexKnowledgeSourceQueryHints(
                filters=[
                    SearchIndexKnowledgeSourceFilterHint(
                        field="Category",
                        field_values=["Luxury", "Boutique"],
                        filter_instructions="Use Category when the user asks for a hotel type.",
                    )
                ]
            ),
        ),
    )

    async with index_client:
        result = await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Updated: knowledge source '{result.name}'")
    # [END update_knowledge_source_async]


async def list_knowledge_sources_async():
    # [START list_knowledge_sources_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    companion_name = f"{knowledge_source_name}-page"
    companion = SearchIndexKnowledgeSource(
        name=companion_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
    )
    async with index_client:
        await index_client.create_or_update_knowledge_source(companion)
        try:
            sources = [
                source
                async for source in index_client.list_knowledge_sources(
                    search=knowledge_source_name,
                    page_size=1,
                    search_type="prefix",
                )
            ]
            source_names = [source.name for source in sources]
            assert set(source_names) == {knowledge_source_name, companion_name}
            assert len(source_names) == len(set(source_names))
            print(f"Paged through {len(sources)} knowledge sources without duplicates")
        finally:
            await index_client.delete_knowledge_source(companion_name)
    # [END list_knowledge_sources_async]


async def create_private_blob_knowledge_source_async():  # pylint: disable=too-many-locals
    missing_variables = [name for name in private_blob_environment_variables if not os.environ.get(name)]
    if missing_variables:
        print(
            "Skipping private Blob knowledge source scenario; set these optional variables: "
            + ", ".join(missing_variables)
        )
        return

    # [START create_private_blob_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
    from azure.search.documents.indexes.models import (
        AzureBlobKnowledgeSource,
        AzureBlobKnowledgeSourceParameters,
        SearchIndexerDataUserAssignedIdentity,
    )
    from azure.search.documents.knowledgebases.models import AIServices, KnowledgeSourceIngestionParameters

    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(service_endpoint, credential)
    indexer_client = SearchIndexerClient(service_endpoint, credential)
    private_source = AzureBlobKnowledgeSource(
        name=private_blob_source_name,
        azure_blob_parameters=AzureBlobKnowledgeSourceParameters(
            connection_string=os.environ["AZURE_STORAGE_RESOURCE_ID_CONNECTION_STRING"],
            container_name=os.environ["AZURE_STORAGE_CONTAINER"],
            ingestion_parameters=KnowledgeSourceIngestionParameters(
                identity=SearchIndexerDataUserAssignedIdentity(
                    resource_id=os.environ["AZURE_SEARCH_USER_ASSIGNED_IDENTITY"]
                ),
                content_extraction_mode="minimal",
                ai_services=AIServices(
                    uri=os.environ["AZURE_AI_SERVICES_ENDPOINT"],
                    api_key=os.environ["AZURE_AI_SERVICES_API_KEY"],
                ),
                network_access_mode="private",
            ),
        ),
    )
    async with index_client, indexer_client:
        try:
            created = await index_client.create_or_update_knowledge_source(private_source)
            assert isinstance(created, AzureBlobKnowledgeSource)
            assert created.azure_blob_parameters.ingestion_parameters is not None
            assert created.azure_blob_parameters.ingestion_parameters.network_access_mode == "private"
            resources = created.azure_blob_parameters.created_resources
            assert resources is not None
            data_source_name = resources.get("datasource")
            indexer_name = resources.get("indexer")
            generated_index_name = resources.get("index")
            assert data_source_name and indexer_name and generated_index_name

            assert (await indexer_client.get_data_source_connection(data_source_name)).name == data_source_name
            assert (await indexer_client.get_indexer_status(indexer_name)).status is not None
            generated_index = await index_client.get_index(generated_index_name)
            analyzers = {
                str(field.analyzer_name) for field in generated_index.fields if field.analyzer_name is not None
            }
            assert os.environ["AZURE_SEARCH_EXPECTED_ANALYZER"] in analyzers
            assert os.environ["AZURE_SEARCH_EXPECTED_FALLBACK_ANALYZER"] in analyzers
            print(f"Verified generated resources and analyzers: {sorted(analyzers)}")
        finally:
            await index_client.delete_knowledge_source(private_blob_source_name)
    # [END create_private_blob_knowledge_source_async]


async def delete_knowledge_source_async():
    # [START delete_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        await index_client.delete_knowledge_source(knowledge_source_name)
    print(f"Deleted: knowledge source '{knowledge_source_name}'")
    # [END delete_knowledge_source_async]


if __name__ == "__main__":
    asyncio.run(create_knowledge_source_async())
    asyncio.run(get_knowledge_source_async())
    asyncio.run(update_knowledge_source_async())
    asyncio.run(list_knowledge_sources_async())
    asyncio.run(create_private_blob_knowledge_source_async())
    asyncio.run(delete_knowledge_source_async())
