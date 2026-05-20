# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``KnowledgeBaseRetrievalClient.retrieve``."""

from __future__ import annotations

from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeBaseRetrievalResponse,
    KnowledgeRetrievalSemanticIntent,
)
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import knowledge_base_resources, live_test

KNOWLEDGE_BASE_RETRIEVAL_DESCRIPTION = "Knowledge base for retrieval client live coverage"
KNOWLEDGE_SOURCE_RETRIEVAL_DESCRIPTION = "Knowledge source for retrieval client live coverage"
RETRIEVAL_QUERY = "hotels with complimentary wireless internet"


class TestKnowledgeBaseRetrievalClient(AzureRecordedTestCase):
    @live_test()
    def test_retrieve_returns_knowledge_base_response(self, endpoint: str) -> None:
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
