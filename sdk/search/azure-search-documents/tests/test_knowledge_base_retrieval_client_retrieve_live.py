# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``KnowledgeBaseRetrievalClient.retrieve``."""

from __future__ import annotations

from devtools_testutils import AzureRecordedTestCase

from _capabilities import require_capability
from _search_helpers import knowledge_base_resources, live_test

KNOWLEDGE_BASE_RETRIEVAL_DESCRIPTION = "Knowledge base for retrieval client live coverage"
KNOWLEDGE_SOURCE_RETRIEVAL_DESCRIPTION = "Knowledge source for retrieval client live coverage"
RETRIEVAL_QUERY = "hotels with complimentary wireless internet"
_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES = (
    "azure.search.documents.indexes.SearchIndexClient.create_knowledge_base",
    "azure.search.documents.indexes.SearchIndexClient.create_knowledge_source",
    "azure.search.documents.indexes.SearchIndexClient.delete_knowledge_base",
    "azure.search.documents.indexes.SearchIndexClient.delete_knowledge_source",
    "azure.search.documents.indexes.SearchIndexClient.get_knowledge_source_status",
    "azure.search.documents.indexes.models.KnowledgeBase",
    "azure.search.documents.indexes.models.KnowledgeSourceReference",
    "azure.search.documents.indexes.models.SearchIndexKnowledgeSource",
    "azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters",
)
_RETRIEVAL_CAPABILITIES = (
    "KnowledgeBaseRetrievalClient",
    "azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient.retrieve",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalResponse",
    "azure.search.documents.knowledgebases.models.KnowledgeRetrievalSemanticIntent",
)


class TestKnowledgeBaseRetrievalClient(AzureRecordedTestCase):
    @live_test()
    def test_retrieve_returns_knowledge_base_response(self, endpoint: str) -> None:
        require_capability(*_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES, *_RETRIEVAL_CAPABILITIES)
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseRetrievalResponse,
            KnowledgeRetrievalSemanticIntent,
        )

        with knowledge_base_resources(
            self,
            endpoint,
            prefix="knowledge-base-retrieve",
            wait_for_active=True,
            description=KNOWLEDGE_BASE_RETRIEVAL_DESCRIPTION,
            source_description=KNOWLEDGE_SOURCE_RETRIEVAL_DESCRIPTION,
        ) as context:
            knowledge_base_name = context.knowledge_base_name
            retrieval_request = KnowledgeBaseRetrievalRequest(
                intents=[KnowledgeRetrievalSemanticIntent(search=RETRIEVAL_QUERY)]
            )

            with KnowledgeBaseRetrievalClient(
                endpoint,
                credential=context.credential,
                knowledge_base_name=knowledge_base_name,
            ) as client:
                result = client.retrieve(retrieval_request)

            assert isinstance(result, KnowledgeBaseRetrievalResponse)
            assert hasattr(result, "response")
            assert hasattr(result, "references")
