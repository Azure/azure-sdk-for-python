# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``KnowledgeBase`` configuration round trips."""

from __future__ import annotations

from azure.core import MatchConditions
from azure.search.documents.indexes.models import KnowledgeBase, KnowledgeSourceReference
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import knowledge_base_resources, live_test

KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION = "Knowledge base configuration before replacement"
KNOWLEDGE_SOURCE_CONFIGURATION_DESCRIPTION = "Knowledge source for knowledge base configuration coverage"
REPLACEMENT_KNOWLEDGE_BASE_CONFIGURATION_DESCRIPTION = "Knowledge base configuration after replacement"


class TestKnowledgeBaseConfiguration(AzureRecordedTestCase):
    @live_test()
    def test_create_or_update_knowledge_base_round_trips_references_description_and_etag(
        self, endpoint: str
    ) -> None:
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
