# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Deterministic typed configurations used by preview wrapper tests."""

from _capabilities import require_capability


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
