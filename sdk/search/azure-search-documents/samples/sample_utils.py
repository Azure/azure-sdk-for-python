# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------


def get_sample_run_tag():
    import datetime
    import os

    return os.environ.get("SAMPLE_RUN_TAG") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")


def preview_hotel_documents():
    return [
        {
            "id": "hotel-ca-1",
            "title": "Historic Harbor Hotel",
            "content": "Hotel guest benefits include complimentary wireless internet, breakfast, and parking.",
            "country": "Canada",
        },
        {
            "id": "hotel-ca-2",
            "title": "Mountain View Inn",
            "content": "Hotel guest benefits include complimentary wireless internet, breakfast, and parking.",
            "country": "Canada",
        },
        {
            "id": "hotel-us-1",
            "title": "Lakeside Hotel",
            "content": "Hotel guest benefits include complimentary wireless internet, breakfast, and parking.",
            "country": "United States",
        },
    ]


def preview_hotel_index(name):
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SearchableField,
        SemanticConfiguration,
        SemanticField,
        SemanticPrioritizedFields,
        SemanticSearch,
        SimpleField,
    )

    return SearchIndex(
        name=name,
        fields=[
            SimpleField(name="id", type="Edm.String", key=True, filterable=True),
            SearchableField(name="title", type="Edm.String"),
            SearchableField(name="content", type="Edm.String"),
            SimpleField(name="country", type="Edm.String", filterable=True, facetable=True),
        ],
        semantic_search=SemanticSearch(
            default_configuration_name="default",
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                    ),
                )
            ],
        ),
    )


def prepare_preview_hotel_index(indexes, endpoint, credential, name, documents, created):
    import time
    from azure.core import MatchConditions
    from azure.search.documents import ApiVersion, SearchClient

    indexes.create_or_update_index(preview_hotel_index(name), match_condition=MatchConditions.IfMissing)
    created.append(("index", name))
    with SearchClient(endpoint, name, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as search:
        if not all(item.succeeded for item in search.upload_documents(documents)):
            raise RuntimeError("Some sample documents could not be uploaded.")
        for _ in range(30):
            if search.get_document_count() == len(documents):
                return
            time.sleep(2)
    raise TimeoutError("Sample documents did not become searchable within 60 seconds.")


async def prepare_preview_hotel_index_async(indexes, endpoint, credential, name, documents, created):
    import asyncio
    from azure.core import MatchConditions
    from azure.search.documents import ApiVersion
    from azure.search.documents.aio import SearchClient

    await indexes.create_or_update_index(preview_hotel_index(name), match_condition=MatchConditions.IfMissing)
    created.append(("index", name))
    async with SearchClient(endpoint, name, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as search:
        if not all(item.succeeded for item in await search.upload_documents(documents)):
            raise RuntimeError("Some sample documents could not be uploaded.")
        for _ in range(30):
            if await search.get_document_count() == len(documents):
                return
            await asyncio.sleep(2)
    raise TimeoutError("Sample documents did not become searchable within 60 seconds.")


def cleanup_preview_resources(indexes, created):
    import sys
    from azure.core import MatchConditions
    from azure.core.exceptions import AzureError, ResourceNotFoundError

    failures = []
    for kind, name in reversed(created):
        try:
            resource = getattr(indexes, "get_" + kind)(name)
            if not resource.e_tag:
                raise ValueError(f"Refusing to delete {kind} {name} without an ETag.")
            getattr(indexes, "delete_" + kind)(resource, match_condition=MatchConditions.IfNotModified)
        except ResourceNotFoundError:
            continue
        except AzureError:
            failures.append((kind, name))
    if failures:
        message = f"Sample cleanup incomplete; retained resources: {failures}"
        if sys.exc_info()[0] is None:
            raise RuntimeError(message)
        print(message)


async def cleanup_preview_resources_async(indexes, created):
    import sys
    from azure.core import MatchConditions
    from azure.core.exceptions import AzureError, ResourceNotFoundError

    failures = []
    for kind, name in reversed(created):
        try:
            resource = await getattr(indexes, "get_" + kind)(name)
            if not resource.e_tag:
                raise ValueError(f"Refusing to delete {kind} {name} without an ETag.")
            await getattr(indexes, "delete_" + kind)(resource, match_condition=MatchConditions.IfNotModified)
        except ResourceNotFoundError:
            continue
        except AzureError:
            failures.append((kind, name))
    if failures:
        message = f"Sample cleanup incomplete; retained resources: {failures}"
        if sys.exc_info()[0] is None:
            raise RuntimeError(message)
        print(message)


def validate_preview_retrieval(result, allowed_keys, source_names, expected_keys=None):
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseSearchIndexActivityRecord,
        KnowledgeBaseSearchIndexReference,
    )

    if not result.references or any(activity.error for activity in result.activity or []):
        raise RuntimeError("Retrieval must return references without activity errors.")
    if not all(isinstance(reference, KnowledgeBaseSearchIndexReference) for reference in result.references):
        raise RuntimeError("Expected search-index document references.")
    keys = {reference.doc_key for reference in result.references}
    if not keys.issubset(allowed_keys) or (expected_keys is not None and keys != expected_keys):
        raise RuntimeError(f"Unexpected document scope: {keys}")
    activities = [
        activity for activity in result.activity or [] if isinstance(activity, KnowledgeBaseSearchIndexActivityRecord)
    ]
    if not activities or any(activity.knowledge_source_name not in source_names for activity in activities):
        raise RuntimeError("Retrieval activity does not match the selected knowledge sources.")
    print("Referenced documents:", sorted(keys))
    return activities


def compatible_provider_auth(prefix):
    import json
    import os
    import re

    headers_text = os.environ.get(prefix + "_HEADERS_JSON")
    audience = os.environ.get(prefix + "_MI_AUDIENCE")
    if bool(headers_text) == bool(audience):
        raise ValueError(f"Set exactly one of {prefix}_HEADERS_JSON or {prefix}_MI_AUDIENCE.")
    if audience:
        if not re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", audience):
            raise ValueError("Managed identity audience must be the third-party application's bare GUID.")
        return {"managed_identity_audience": audience}
    if headers_text is None:
        raise ValueError("Provider headers are required when managed identity is not configured.")
    headers = json.loads(headers_text)
    if (
        not isinstance(headers, dict)
        or not headers
        or any(
            not isinstance(key, str) or not key or not isinstance(value, str) or not value
            for key, value in headers.items()
        )
    ):
        raise ValueError("Provider headers must be a nonempty JSON object of nonempty strings.")
    return {"headers": headers}


def validate_preview_auto_hint(result, country, source_name, expected_keys):
    activities = validate_preview_retrieval(result, expected_keys, {source_name}, expected_keys=expected_keys)
    filters = [
        activity.query_hint_processing.generated_filter
        for activity in activities
        if activity.query_hint_processing and activity.query_hint_processing.generated_filter
    ]
    if not any("country" in value and country in value for value in filters):
        raise RuntimeError("The planner did not report the expected automatically grounded country filter.")
    print("Generated query-hint filters:", filters)


def topic_graph_hotel_documents():
    topics = {
        "wellness": [
            (
                "Harbor Spa Hotel",
                "Relax at a waterfront hotel with a heated pool, spa treatments, and quiet rooms.",
            ),
            (
                "Garden Retreat",
                "Enjoy a peaceful hotel garden, morning yoga, and a full-service wellness spa.",
            ),
            (
                "Lakeside Sanctuary",
                "Recharge with lakeside walks, a sauna, and relaxing hotel massage treatments.",
            ),
        ],
        "dining": [
            (
                "Market Square Hotel",
                "Taste regional dishes at the hotel's restaurant near the lively food market.",
            ),
            (
                "Rooftop Dining Hotel",
                "Enjoy rooftop dining, a chef's tasting menu, and local wine at this city hotel.",
            ),
            (
                "Harbor Kitchen Inn",
                "Explore seafood restaurants and cooking classes at a hotel beside the harbor.",
            ),
        ],
        "adventure": [
            (
                "Mountain Trail Lodge",
                "Explore hiking trails and mountain biking routes from this outdoor adventure hotel.",
            ),
            (
                "River Adventure Inn",
                "Try guided kayaking, rafting, and riverside hiking from this active holiday hotel.",
            ),
            (
                "Forest Explorer Hotel",
                "Discover forest trails, climbing excursions, and wildlife tours near this hotel.",
            ),
        ],
    }
    return [
        {"id": f"{topic}-{number}", "title": title, "content": content, "topic": topic}
        for topic, hotels in topics.items()
        for number, (title, content) in enumerate(hotels, 1)
    ]


def graph_hotel_documents(graph_name):
    sources = [
        {
            "uid": "harbor-operator",
            "snippet": "Historic Harbor Hotel is operated by Contoso Hospitality.",
            "snippet_parent_id": "harbor-brochure",
        },
        {
            "uid": "harbor-location",
            "snippet": "Historic Harbor Hotel is located in Seattle.",
            "snippet_parent_id": "harbor-brochure",
        },
    ]
    assertions = [
        {
            "id": f"assertion-{number}",
            "edge_hash": f"fact-{number}",
            "subject": "Historic Harbor Hotel",
            "subject_type": "Hotel",
            "subject_id": "hotel:harbor",
            "predicate": predicate,
            "object": name,
            "object_string": name,
            "object_type": entity_type,
            "object_id": entity_id,
            "graph_name": graph_name,
            "edge_confidence": 1.0,
            "s_confidence": 1.0,
            "p_confidence": 1.0,
            "o_confidence": 1.0,
            "chunk_id": source["uid"],
            "parent_id": source["snippet_parent_id"],
            "subject_id_display_name": "Historic Harbor Hotel",
            "object_id_display_name": name,
        }
        for number, (predicate, name, entity_type, entity_id, source) in enumerate(
            [
                (
                    "operatedBy",
                    "Contoso Hospitality",
                    "Organization",
                    "organization:contoso",
                    sources[0],
                ),
                ("locatedIn", "Seattle", "Place", "place:seattle", sources[1]),
            ],
            1,
        )
    ]
    return sources, assertions


def graph_hotel_index(index_name, provenance_index_name):
    from azure.search.documents.indexes.models import (
        GraphFieldMappings,
        GraphProfile,
        SearchField,
        SearchIndex,
    )

    fields = [
        SearchField(
            name=name,
            type=field_type,
            key=name == "id",
            filterable=True,
            facetable=name
            in {
                "subject",
                "predicate",
                "object",
                "object_string",
                "object_double",
                "subject_type",
                "subject_id",
                "object_type",
                "object_id",
                "graph_name",
            },
            sortable=name
            in {
                "id",
                "subject",
                "object",
                "object_string",
                "object_double",
                "subject_id",
                "object_id",
                "graph_name",
            },
            retrievable=True,
        )
        for name, field_type in [
            ("id", "Edm.String"),
            ("edge_hash", "Edm.String"),
            ("subject", "Edm.String"),
            ("predicate", "Edm.String"),
            ("object", "Edm.String"),
            ("object_string", "Edm.String"),
            ("object_double", "Edm.Double"),
            ("object_bool", "Edm.Boolean"),
            ("object_datetime", "Edm.DateTimeOffset"),
            ("subject_type", "Edm.String"),
            ("subject_id", "Edm.String"),
            ("object_type", "Edm.String"),
            ("object_id", "Edm.String"),
            ("graph_name", "Edm.String"),
            ("edge_confidence", "Edm.Double"),
            ("s_confidence", "Edm.Double"),
            ("p_confidence", "Edm.Double"),
            ("o_confidence", "Edm.Double"),
            ("chunk_id", "Edm.String"),
            ("parent_id", "Edm.String"),
            ("subject_id_display_name", "Edm.String"),
            ("object_id_display_name", "Edm.String"),
        ]
    ]
    return SearchIndex(
        name=index_name,
        fields=fields,
        graph_profile=GraphProfile(
            kind="edgeList",
            provenance_index_name=provenance_index_name,
            fields=GraphFieldMappings(
                assertion_id_field="id",
                fact_id_field="edge_hash",
                subject_field="subject",
                predicate_field="predicate",
                object_field="object",
                object_string_field="object_string",
                object_double_field="object_double",
                object_bool_field="object_bool",
                object_date_time_field="object_datetime",
                subject_type_field="subject_type",
                subject_id_field="subject_id",
                object_type_field="object_type",
                object_id_field="object_id",
                graph_name_field="graph_name",
                confidence_field="edge_confidence",
                subject_confidence_field="s_confidence",
                predicate_confidence_field="p_confidence",
                object_confidence_field="o_confidence",
                source_chunk_id_field="chunk_id",
                source_parent_id_field="parent_id",
                subject_id_display_name_field="subject_id_display_name",
                object_id_display_name_field="object_id_display_name",
            ),
        ),
    )


def graph_hotel_ontology(include_founded_year=False):
    import json

    nodes: list[dict[str, object]] = [
        {"@id": f"ekg:{name}", "@type": "owl:Class", "rdfs:comment": description}
        for name, description in [
            ("Hotel", "A hotel property, distinct from the organization operating it."),
            ("Organization", "An organization operating hotel properties."),
            ("Place", "A geographic location."),
        ]
    ]
    for name, domain, range_name, description in [
        (
            "operatedBy",
            "Hotel",
            "Organization",
            "The organization operating the hotel.",
        ),
        ("locatedIn", "Hotel", "Place", "The city where the hotel is located."),
    ]:
        nodes.append(
            {
                "@id": f"ekg:{name}",
                "@type": "owl:ObjectProperty",
                "rdfs:domain": {"@id": f"ekg:{domain}"},
                "rdfs:range": {"@id": f"ekg:{range_name}"},
                "rdfs:comment": description,
            }
        )
    if include_founded_year:
        nodes.append(
            {
                "@id": "ekg:foundedYear",
                "@type": "owl:DatatypeProperty",
                "rdfs:domain": {"@id": "ekg:Hotel"},
                "rdfs:range": {"@id": "xsd:integer"},
                "rdfs:comment": "The year the hotel was founded.",
            }
        )
    return json.dumps(
        {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "ekg": "https://schema.search.azure.com/graph-extraction#",
            },
            "@graph": nodes,
        }
    )


def completed_graph_synchronization(status, previous_end_time=None):
    state = status.as_dict()
    completed = state.get("lastSynchronizationState") or {}
    if (
        state.get("currentSynchronizationState")
        or not completed.get("endTime")
        or completed["endTime"] == previous_end_time
    ):
        return None
    if completed.get("itemsUpdatesFailed", 0):
        raise RuntimeError("Graph synchronization completed with failed source documents.")
    return completed


def run_graph_indexer(indexer_client, indexer_name):
    from azure.core.exceptions import HttpResponseError

    execution = indexer_client.get_indexer_status(indexer_name).last_result
    if execution and execution.status == "inProgress":
        return
    try:
        indexer_client.run_indexer(indexer_name)
    except HttpResponseError as error:
        execution = indexer_client.get_indexer_status(indexer_name).last_result
        if error.status_code != 409 or not execution or execution.status != "inProgress":
            raise


async def run_graph_indexer_async(indexer_client, indexer_name):
    from azure.core.exceptions import HttpResponseError

    execution = (await indexer_client.get_indexer_status(indexer_name)).last_result
    if execution and execution.status == "inProgress":
        return
    try:
        await indexer_client.run_indexer(indexer_name)
    except HttpResponseError as error:
        execution = (await indexer_client.get_indexer_status(indexer_name)).last_result
        if error.status_code != 409 or not execution or execution.status != "inProgress":
            raise


def wait_for_graph_synchronization(index_client, indexer_client, source_name, indexer_name, previous_end_time=None):
    import time

    for attempt in range(60):
        status = index_client.get_knowledge_source_status(source_name)
        completed = completed_graph_synchronization(status, previous_end_time)
        execution = indexer_client.get_indexer_status(indexer_name).last_result
        if execution and execution.status in {"persistentFailure", "transientFailure"}:
            raise RuntimeError("Graph indexer failed; inspect its execution errors and dependency access.")
        if completed and execution and execution.status == "success":
            if execution.failed_item_count:
                raise RuntimeError("Graph indexer completed with failed source documents.")
            print(
                f"Completed synchronization: {completed['endTime']}; "
                f"graph statistics: {completed.get('graphStatistics')}"
            )
            print(f"Indexer warnings: {len(execution.warnings or [])}")
            return completed
        if attempt < 59:
            time.sleep(5)
    raise TimeoutError("No new successful graph synchronization completed within five minutes.")


async def wait_for_graph_synchronization_async(
    index_client, indexer_client, source_name, indexer_name, previous_end_time=None
):
    import asyncio

    for attempt in range(60):
        status = await index_client.get_knowledge_source_status(source_name)
        completed = completed_graph_synchronization(status, previous_end_time)
        execution = (await indexer_client.get_indexer_status(indexer_name)).last_result
        if execution and execution.status in {"persistentFailure", "transientFailure"}:
            raise RuntimeError("Graph indexer failed; inspect its execution errors and dependency access.")
        if completed and execution and execution.status == "success":
            if execution.failed_item_count:
                raise RuntimeError("Graph indexer completed with failed source documents.")
            print(
                f"Completed synchronization: {completed['endTime']}; "
                f"graph statistics: {completed.get('graphStatistics')}"
            )
            print(f"Indexer warnings: {len(execution.warnings or [])}")
            return completed
        if attempt < 59:
            await asyncio.sleep(5)
    raise TimeoutError("No new successful graph synchronization completed within five minutes.")


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


def wait_for_indexer(indexer_client, indexer_name):
    import time

    for attempt in range(60):
        status = indexer_client.get_indexer_status(indexer_name)
        result = status.last_result
        if result is not None and result.status == "success":
            if result.failed_item_count:
                raise RuntimeError(f"Indexer completed with {result.failed_item_count} failed documents.")
            return
        if result is not None and result.status in {"persistentFailure", "transientFailure"}:
            raise RuntimeError(f"Indexer failed: {result.error_message}")
        if attempt < 59:
            time.sleep(5)
    raise TimeoutError(f"Indexer '{indexer_name}' did not complete within five minutes.")


async def wait_for_indexer_async(indexer_client, indexer_name):
    import asyncio

    for attempt in range(60):
        status = await indexer_client.get_indexer_status(indexer_name)
        result = status.last_result
        if result is not None and result.status == "success":
            if result.failed_item_count:
                raise RuntimeError(f"Indexer completed with {result.failed_item_count} failed documents.")
            return
        if result is not None and result.status in {"persistentFailure", "transientFailure"}:
            raise RuntimeError(f"Indexer failed: {result.error_message}")
        if attempt < 59:
            await asyncio.sleep(5)
    raise TimeoutError(f"Indexer '{indexer_name}' did not complete within five minutes.")


def cleanup_indexer_resources(indexer_client, index_client, *, indexer_name, data_source_name, index_name):
    from azure.core.exceptions import ResourceNotFoundError

    for delete, name in (
        (indexer_client.delete_indexer, indexer_name),
        (indexer_client.delete_data_source_connection, data_source_name),
        (index_client.delete_index, index_name),
    ):
        try:
            delete(name)
        except ResourceNotFoundError:
            pass


async def cleanup_indexer_resources_async(indexer_client, index_client, *, indexer_name, data_source_name, index_name):
    from azure.core.exceptions import ResourceNotFoundError

    for delete, name in (
        (indexer_client.delete_indexer, indexer_name),
        (indexer_client.delete_data_source_connection, data_source_name),
        (index_client.delete_index, index_name),
    ):
        try:
            await delete(name)
        except ResourceNotFoundError:
            pass


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
