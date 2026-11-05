# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Deterministic typed configurations used by preview wrapper tests."""

from _capabilities import require_capability


def graph_index_configuration(index_name):
    require_capability(
        "azure.search.documents.indexes.models.SearchIndex.graph_profile",
        "azure.search.documents.indexes.models.GraphProfile",
        "azure.search.documents.indexes.models.GraphFieldMappings",
    )
    from azure.search.documents.indexes.models import (
        GraphFieldMappings,
        GraphProfile,
        SearchFieldDataType,
        SearchIndex,
        SimpleField,
    )

    field_types = {
        "assertion_id": SearchFieldDataType.STRING,
        "fact_id": SearchFieldDataType.STRING,
        "subject": SearchFieldDataType.STRING,
        "predicate": SearchFieldDataType.STRING,
        "object": SearchFieldDataType.STRING,
        "object_string": SearchFieldDataType.STRING,
        "object_double": SearchFieldDataType.DOUBLE,
        "object_bool": SearchFieldDataType.BOOLEAN,
        "object_date_time": SearchFieldDataType.DATE_TIME_OFFSET,
        "subject_type": SearchFieldDataType.STRING,
        "subject_id": SearchFieldDataType.STRING,
        "object_type": SearchFieldDataType.STRING,
        "object_id": SearchFieldDataType.STRING,
        "confidence": SearchFieldDataType.DOUBLE,
        "subject_confidence": SearchFieldDataType.DOUBLE,
        "predicate_confidence": SearchFieldDataType.DOUBLE,
        "object_confidence": SearchFieldDataType.DOUBLE,
        "source_chunk_id": SearchFieldDataType.STRING,
        "source_parent_id": SearchFieldDataType.STRING,
        "graph_name": SearchFieldDataType.STRING,
        "subject_id_display_name": SearchFieldDataType.STRING,
        "object_id_display_name": SearchFieldDataType.STRING,
    }
    return SearchIndex(
        name=index_name,
        fields=[
            SimpleField(
                name=name,
                type=field_type,
                key=name == "assertion_id",
                filterable=True,
                facetable=True,
                sortable=True,
            )
            for name, field_type in field_types.items()
        ],
        graph_profile=GraphProfile(
            kind="edgeList",
            fields=GraphFieldMappings(**{name + "_field": name for name in field_types}),
        ),
    )


def graph_documents():
    return [
        {
            "assertion_id": f"assertion-{city.lower()}",
            "fact_id": f"fact-{city.lower()}",
            "subject": "Historic Harbor Hotel",
            "predicate": "locatedIn",
            "object": city,
            "object_string": city,
            "subject_type": "Hotel",
            "subject_id": "hotel:harbor",
            "object_type": "City",
            "object_id": f"city:{city.lower()}",
            "confidence": 1.0,
            "subject_confidence": 1.0,
            "predicate_confidence": 1.0,
            "object_confidence": 1.0,
            "source_chunk_id": f"chunk-{city.lower()}",
            "source_parent_id": f"brochure-{city.lower()}",
            "graph_name": graph_name,
            "subject_id_display_name": "Historic Harbor Hotel",
            "object_id_display_name": city,
        }
        for city, graph_name in (("Seattle", "hotel-locations"), ("Portland", "other-hotels"))
    ]


def knowledge_source_configuration(scenario):
    if scenario == "facet_hint":
        require_capability(
            "azure.search.documents.indexes.models.SearchIndexKnowledgeSourceFilterHint.auto_configuration"
        )
        from azure.search.documents.indexes.models import (
            SearchIndexKnowledgeSource,
            SearchIndexKnowledgeSourceFilterHint,
            SearchIndexKnowledgeSourceFilterHintAutoConfiguration,
            SearchIndexKnowledgeSourceParameters,
            SearchIndexKnowledgeSourceQueryHints,
        )

        return SearchIndexKnowledgeSource(
            name="hotels",
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name="hotels",
                query_hints=SearchIndexKnowledgeSourceQueryHints(
                    filters=[
                        SearchIndexKnowledgeSourceFilterHint(
                            field="category",
                            auto_configuration=SearchIndexKnowledgeSourceFilterHintAutoConfiguration(
                                cache_ttl=300, max_facet_value_count=16
                            ),
                        )
                    ]
                ),
            ),
        )

    require_capability("azure.search.documents.knowledgebases.models.KnowledgeSourceIngestionParameters.cache")
    from azure.search.documents.indexes.models import (
        AzureBlobKnowledgeSource,
        AzureBlobKnowledgeSourceParameters,
        KnowledgeSourceGraphExtractionParameters,
    )
    from azure.search.documents.knowledgebases.models import KnowledgeSourceCache, KnowledgeSourceIngestionParameters

    return AzureBlobKnowledgeSource(
        name="hotels",
        azure_blob_parameters=AzureBlobKnowledgeSourceParameters(
            connection_string="ResourceId=/subscriptions/test/resourceGroups/test/providers/Microsoft.Storage/storageAccounts/test",
            container_name="hotels",
            graph_extraction=KnowledgeSourceGraphExtractionParameters(graph_name="hotels-graph"),
            ingestion_parameters=KnowledgeSourceIngestionParameters(
                cache=KnowledgeSourceCache(
                    storage_connection_string="ResourceId=/subscriptions/test/resourceGroups/test/providers/Microsoft.Storage/storageAccounts/cache",
                    enable_reprocessing=True,
                )
            ),
        ),
    )


def assert_knowledge_source_configuration(body, scenario):
    if scenario == "facet_hint":
        hint = body["searchIndexParameters"]["queryHints"]["filters"][0]
        assert hint["autoConfiguration"] == {"cacheTtl": 300, "maxFacetValueCount": 16}
        assert "fieldValues" not in hint
    else:
        parameters = body["azureBlobParameters"]
        assert parameters["graphExtraction"] == {"graphName": "hotels-graph"}
        assert parameters["ingestionParameters"]["cache"]["enableReprocessing"] is True
        assert parameters["ingestionParameters"]["cache"]["storageConnectionString"].endswith("/cache")
