# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------


def get_sample_run_tag():
    import datetime
    import os

    return os.environ.get("SAMPLE_RUN_TAG") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")


def hotel_index(index_name):
    return {
        "name": index_name,
        "fields": [
            {"name": "HotelId", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "HotelName", "type": "Edm.String", "searchable": True},
            {"name": "Description", "type": "Edm.String", "searchable": True},
            {"name": "Category", "type": "Edm.String", "searchable": True, "filterable": True},
            {
                "name": "Tags",
                "type": "Collection(Edm.String)",
                "searchable": True,
                "filterable": True,
            },
            {"name": "ParkingIncluded", "type": "Edm.Boolean", "filterable": True},
            {"name": "IsDeleted", "type": "Edm.Boolean", "filterable": True},
            {
                "name": "LastRenovationDate",
                "type": "Edm.DateTimeOffset",
                "filterable": True,
                "sortable": True,
            },
            {"name": "Rating", "type": "Edm.Double", "filterable": True, "sortable": True},
        ],
        "semantic": {
            "defaultConfiguration": "default",
            "configurations": [
                {
                    "name": "default",
                    "prioritizedFields": {
                        "titleField": {"fieldName": "HotelName"},
                        "prioritizedContentFields": [{"fieldName": "Description"}],
                        "prioritizedKeywordsFields": [{"fieldName": "Category"}, {"fieldName": "Tags"}],
                    },
                }
            ],
        },
    }


def hotel_documents():
    return [
        {
            "HotelId": "1",
            "HotelName": "Historic Harbor Hotel",
            "Description": "A recently renovated waterfront hotel with free parking and a rooftop restaurant.",
            "Category": "Luxury",
            "Tags": ["waterfront", "parking", "renovated"],
            "ParkingIncluded": True,
            "IsDeleted": False,
            "LastRenovationDate": "2025-02-10T00:00:00Z",
            "Rating": 4.8,
        },
        {
            "HotelId": "2",
            "HotelName": "City Center Hotel",
            "Description": "A downtown hotel near museums and restaurants with fast Wi-Fi.",
            "Category": "Boutique",
            "Tags": ["downtown", "wifi"],
            "ParkingIncluded": False,
            "IsDeleted": False,
            "LastRenovationDate": "2023-06-15T00:00:00Z",
            "Rating": 4.2,
        },
        {
            "HotelId": "3",
            "HotelName": "Mountain View Inn",
            "Description": "A quiet mountain hotel with trail access, breakfast, and free parking.",
            "Category": "Resort",
            "Tags": ["mountain", "parking", "breakfast"],
            "ParkingIncluded": True,
            "IsDeleted": False,
            "LastRenovationDate": "2024-09-20T00:00:00Z",
            "Rating": 4.6,
        },
        {
            "HotelId": "4",
            "HotelName": "Closed Airport Hotel",
            "Description": "A former airport hotel that is no longer available for booking.",
            "Category": "Airport",
            "Tags": ["airport"],
            "ParkingIncluded": True,
            "IsDeleted": True,
            "LastRenovationDate": "2020-01-05T00:00:00Z",
            "Rating": 3.1,
        },
    ]


def setup_hotel_index(index_name, service_endpoint, key):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient

    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(service_endpoint, credential)
    try:
        index_client.create_or_update_index(hotel_index(index_name))
    finally:
        index_client.close()
    search_client = SearchClient(service_endpoint, index_name, credential)
    try:
        search_client.upload_documents(hotel_documents())
    finally:
        search_client.close()


async def setup_hotel_index_async(index_name, service_endpoint, key):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient
    from azure.search.documents.indexes.aio import SearchIndexClient

    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(service_endpoint, credential)
    async with index_client:
        await index_client.create_or_update_index(hotel_index(index_name))
    search_client = SearchClient(service_endpoint, index_name, credential)
    async with search_client:
        await search_client.upload_documents(hotel_documents())


def print_retrieval_summary(result):
    print(f"Activity records: {len(result.activity or [])}")
    print(f"References: {len(result.references or [])}")
    print(f"Response messages: {len(result.response or [])}")


def wait_for_knowledge_source_active(index_client, knowledge_source_name):
    import time

    for attempt in range(36):
        status = index_client.get_knowledge_source_status(knowledge_source_name)
        if status.synchronization_status == "active":
            return
        if attempt < 35:
            time.sleep(5)
    raise RuntimeError(f"Knowledge source did not become active: {status.synchronization_status}")


async def wait_for_knowledge_source_active_async(index_client, knowledge_source_name):
    import asyncio

    for attempt in range(36):
        status = await index_client.get_knowledge_source_status(knowledge_source_name)
        if status.synchronization_status == "active":
            return
        if attempt < 35:
            await asyncio.sleep(5)
    raise RuntimeError(f"Knowledge source did not become active: {status.synchronization_status}")


def setup_search_index_knowledge_source(knowledge_source_name, index_name, service_endpoint, key):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters

    with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as index_client:
        index_client.create_or_update_knowledge_source(
            SearchIndexKnowledgeSource(
                name=knowledge_source_name,
                search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
            )
        )


async def setup_search_index_knowledge_source_async(knowledge_source_name, index_name, service_endpoint, key):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters

    async with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as index_client:
        await index_client.create_or_update_knowledge_source(
            SearchIndexKnowledgeSource(
                name=knowledge_source_name,
                search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
            )
        )


def cleanup_knowledge_resources(service_endpoint, key, *, knowledge_base_name, knowledge_source_name):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as index_client:
        cleanup_resources(
            index_client,
            knowledge_base_name=knowledge_base_name,
            knowledge_source_name=knowledge_source_name,
        )


async def cleanup_knowledge_resources_async(service_endpoint, key, *, knowledge_base_name, knowledge_source_name):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    async with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as index_client:
        await cleanup_resources_async(
            index_client,
            knowledge_base_name=knowledge_base_name,
            knowledge_source_name=knowledge_source_name,
        )


def cleanup_resources(index_client, *, knowledge_base_name=None, knowledge_source_name=None, index_name=None):
    from azure.core.exceptions import ResourceNotFoundError

    for delete, name in (
        (index_client.delete_knowledge_base, knowledge_base_name),
        (index_client.delete_knowledge_source, knowledge_source_name),
        (index_client.delete_index, index_name),
    ):
        if not name:
            continue
        try:
            delete(name)
        except ResourceNotFoundError:
            pass


async def cleanup_resources_async(
    index_client, *, knowledge_base_name=None, knowledge_source_name=None, index_name=None
):
    from azure.core.exceptions import ResourceNotFoundError

    for delete, name in (
        (index_client.delete_knowledge_base, knowledge_base_name),
        (index_client.delete_knowledge_source, knowledge_source_name),
        (index_client.delete_index, index_name),
    ):
        if not name:
            continue
        try:
            await delete(name)
        except ResourceNotFoundError:
            pass
