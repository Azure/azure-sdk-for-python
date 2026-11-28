# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``KnowledgeBase`` configuration round trips."""

from __future__ import annotations

from azure.core import MatchConditions
from devtools_testutils import AzureRecordedTestCase

from _capabilities import require_capability
from _search_helpers import knowledge_base_resources, live_test

KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION = "Knowledge base configuration before replacement"
KNOWLEDGE_SOURCE_CONFIGURATION_DESCRIPTION = "Knowledge source for knowledge base configuration coverage"
REPLACEMENT_KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION = "Knowledge base configuration after replacement"
_KNOWLEDGE_BASE_CONFIGURATION_CAPABILITIES = (
    "azure.search.documents.indexes.SearchIndexClient.create_knowledge_base",
    "azure.search.documents.indexes.SearchIndexClient.create_knowledge_source",
    "azure.search.documents.indexes.SearchIndexClient.create_or_update_knowledge_base",
    "azure.search.documents.indexes.SearchIndexClient.delete_knowledge_base",
    "azure.search.documents.indexes.SearchIndexClient.delete_knowledge_source",
    "azure.search.documents.indexes.SearchIndexClient.get_knowledge_base",
    "azure.search.documents.indexes.models.KnowledgeBase",
    "azure.search.documents.indexes.models.KnowledgeSourceReference",
    "azure.search.documents.indexes.models.SearchIndexKnowledgeSource",
    "azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters",
)


class TestKnowledgeBaseConfiguration(AzureRecordedTestCase):
    @live_test()
    def test_create_or_update_knowledge_base_preserves_and_clears_tools(self, endpoint: str) -> None:
        require_capability(
            *_KNOWLEDGE_BASE_CONFIGURATION_CAPABILITIES,
            "azure.search.documents.indexes.models.KnowledgeBase.tools",
            "azure.search.documents.indexes.models.KnowledgeBaseTool",
            "azure.search.documents.indexes.models.KnowledgeBaseToolKnowledgeSourceReference",
        )
        from azure.search.documents.indexes.models import KnowledgeBaseTool, KnowledgeBaseToolKnowledgeSourceReference

        with knowledge_base_resources(self, endpoint, prefix="knowledge-base-tools") as context:
            base = context.knowledge_base
            base.tools = [
                KnowledgeBaseTool(
                    name="hotel-search",
                    description="Retrieve hotel information from the hotel source.",
                    knowledge_sources=[KnowledgeBaseToolKnowledgeSourceReference(name=context.knowledge_source_name)],
                )
            ]
            context.index_client.create_or_update_knowledge_base(base, match_condition=MatchConditions.IfNotModified)
            fetched = context.index_client.get_knowledge_base(context.knowledge_base_name)
            assert len(fetched.tools) == 1
            assert fetched.tools[0].name == "hotel-search"
            assert fetched.tools[0].description == base.tools[0].description
            assert [source.name for source in fetched.tools[0].knowledge_sources] == [context.knowledge_source_name]
            assert fetched.e_tag != base.e_tag

            fetched.tools = []
            context.index_client.create_or_update_knowledge_base(fetched, match_condition=MatchConditions.IfNotModified)
            cleared = context.index_client.get_knowledge_base(context.knowledge_base_name)
            assert not cleared.tools
            assert [source.name for source in cleared.knowledge_sources] == [context.knowledge_source_name]
            assert cleared.e_tag != fetched.e_tag

    @live_test()
    def test_create_or_update_knowledge_base_round_trips_references_description_and_etag(self, endpoint: str) -> None:
        require_capability(*_KNOWLEDGE_BASE_CONFIGURATION_CAPABILITIES)
        from azure.search.documents.indexes.models import KnowledgeBase, KnowledgeSourceReference

        with knowledge_base_resources(
            self,
            endpoint,
            prefix="knowledge-base-create-or-update-configuration",
            description=KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION,
            source_description=KNOWLEDGE_SOURCE_CONFIGURATION_DESCRIPTION,
        ) as context:
            knowledge_base_name = context.knowledge_base_name
            knowledge_source_name = context.knowledge_source_name
            original = context.knowledge_base

            assert original.name == knowledge_base_name
            assert original.description == KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION
            assert original.e_tag is not None
            assert len(original.knowledge_sources) == 1
            assert original.knowledge_sources[0].name == knowledge_source_name

            replacement = KnowledgeBase(
                name=knowledge_base_name,
                description=REPLACEMENT_KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION,
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
            )
            replacement.e_tag = original.e_tag

            result = context.index_client.create_or_update_knowledge_base(
                replacement,
                match_condition=MatchConditions.IfNotModified,
            )
            fetched = context.index_client.get_knowledge_base(knowledge_base_name)

            assert result.name == knowledge_base_name
            assert result.description == REPLACEMENT_KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION
            assert result.e_tag != original.e_tag
            assert len(result.knowledge_sources) == 1
            assert result.knowledge_sources[0].name == knowledge_source_name
            assert fetched.description == REPLACEMENT_KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION
            assert len(fetched.knowledge_sources) == 1
            assert fetched.knowledge_sources[0].name == knowledge_source_name
