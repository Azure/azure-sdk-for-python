# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchIndexClient`` knowledge base operations."""

from __future__ import annotations

from azure.core import MatchConditions
from azure.search.documents.indexes.models import KnowledgeBase, KnowledgeSourceKind, KnowledgeSourceReference
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import knowledge_base_resources, live_test, poll_until

KNOWLEDGE_BASE_DESCRIPTION = "Knowledge base for SearchIndexClient live coverage"
KNOWLEDGE_SOURCE_DESCRIPTION = "Knowledge source for SearchIndexClient knowledge base coverage"
REPLACEMENT_KNOWLEDGE_BASE_DESCRIPTION = "Knowledge base replacement for SearchIndexClient live coverage"


def _knowledge_base_resources(test_case: AzureRecordedTestCase, endpoint: str, *, sdk_verb: str, scenario: str = ""):
    resource_name = f"knowledge-base-{sdk_verb}"
    if scenario:
        resource_name = f"{resource_name}-{scenario}"
    return knowledge_base_resources(
        test_case,
        endpoint,
        prefix=resource_name,
        description=KNOWLEDGE_BASE_DESCRIPTION,
        source_description=KNOWLEDGE_SOURCE_DESCRIPTION,
    )


class TestSearchIndexClientKnowledgeBases(AzureRecordedTestCase):
    @live_test()
    def test_create_knowledge_base_returns_resource(self, endpoint: str) -> None:
        with _knowledge_base_resources(self, endpoint, sdk_verb="create") as context:
            knowledge_base_name = context.knowledge_base_name
            knowledge_source_name = context.knowledge_source_name
            result = context.knowledge_base

            assert result.name == knowledge_base_name
            assert result.description == KNOWLEDGE_BASE_DESCRIPTION
            assert result.e_tag is not None
            assert len(result.knowledge_sources) == 1
            assert result.knowledge_sources[0].name == knowledge_source_name

    @live_test()
    def test_create_or_update_knowledge_base_uses_model_name_and_etag(self, endpoint: str) -> None:
        with _knowledge_base_resources(self, endpoint, sdk_verb="create-or-update") as context:
            knowledge_base_name = context.knowledge_base_name
            knowledge_source_name = context.knowledge_source_name
            replacement = KnowledgeBase(
                name=knowledge_base_name,
                description=REPLACEMENT_KNOWLEDGE_BASE_DESCRIPTION,
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
            )
            replacement.e_tag = context.knowledge_base.e_tag

            result = context.index_client.create_or_update_knowledge_base(
                replacement,
                match_condition=MatchConditions.IfNotModified,
            )

            assert result.name == knowledge_base_name
            assert result.description == REPLACEMENT_KNOWLEDGE_BASE_DESCRIPTION
            assert result.e_tag != context.knowledge_base.e_tag
            assert len(result.knowledge_sources) == 1
            assert result.knowledge_sources[0].name == knowledge_source_name

    @live_test()
    def test_get_knowledge_base_returns_named_resource(self, endpoint: str) -> None:
        with _knowledge_base_resources(self, endpoint, sdk_verb="get") as context:
            knowledge_base_name = context.knowledge_base_name
            knowledge_source_name = context.knowledge_source_name

            result = context.index_client.get_knowledge_base(knowledge_base_name)

            assert result.name == knowledge_base_name
            assert result.description == KNOWLEDGE_BASE_DESCRIPTION
            assert len(result.knowledge_sources) == 1
            assert result.knowledge_sources[0].name == knowledge_source_name

    @live_test()
    def test_list_knowledge_bases_includes_created_resource(self, endpoint: str) -> None:
        with _knowledge_base_resources(self, endpoint, sdk_verb="list") as context:
            knowledge_base_name = context.knowledge_base_name

            results = list(context.index_client.list_knowledge_bases())

            assert any(knowledge_base.name == knowledge_base_name for knowledge_base in results)

    @live_test()
    def test_delete_knowledge_base_accepts_model_and_etag(self, endpoint: str) -> None:
        with _knowledge_base_resources(self, endpoint, sdk_verb="delete") as context:
            knowledge_base_name = context.knowledge_base_name

            assert context.knowledge_base.e_tag is not None
            context.index_client.delete_knowledge_base(
                context.knowledge_base,
                match_condition=MatchConditions.IfNotModified,
            )
            results = list(context.index_client.list_knowledge_bases())

            assert all(knowledge_base.name != knowledge_base_name for knowledge_base in results)


class TestSearchIndexClientKnowledgeSourceStatus(AzureRecordedTestCase):
    @live_test()
    def test_get_knowledge_source_status_reaches_active_search_index_source(self, endpoint: str) -> None:
        with _knowledge_base_resources(self, endpoint, sdk_verb="get", scenario="source-status") as context:
            knowledge_source_name = context.knowledge_source_name

            results = poll_until(
                lambda: context.index_client.get_knowledge_source_status(knowledge_source_name),
                predicate=lambda status: status.synchronization_status == "active",
            )

            assert results[0].kind == KnowledgeSourceKind.SEARCH_INDEX
            assert results[0].synchronization_status in {"creating", "active"}
            assert results[-1].synchronization_status == "active"
            if results[-1].statistics is not None:
                assert results[-1].statistics.total_synchronization >= 0
                assert results[-1].statistics.average_items_processed_per_synchronization >= 0
            if results[-1].current_synchronization_state is not None:
                assert results[-1].current_synchronization_state.items_updates_processed >= 0
            if results[-1].last_synchronization_state is not None:
                assert results[-1].last_synchronization_state.items_updates_processed >= 0
