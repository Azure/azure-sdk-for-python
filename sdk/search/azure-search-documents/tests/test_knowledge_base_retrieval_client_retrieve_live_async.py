# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``KnowledgeBaseRetrievalClient.retrieve``."""

from __future__ import annotations

import time

from devtools_testutils import AzureRecordedTestCase

from _capabilities import require_capability
from _search_helpers import log_retrieval_stream_event, log_retrieval_stream_response
from _search_helpers_async import knowledge_base_resources, live_test

KNOWLEDGE_BASE_RETRIEVAL_DESCRIPTION = "Knowledge base for retrieval client live coverage"
KNOWLEDGE_SOURCE_RETRIEVAL_DESCRIPTION = "Knowledge source for retrieval client live coverage"
RETRIEVAL_QUERY = "hotels with complimentary wireless internet"
_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES = (
    "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_base",
    "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_source",
    "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_base",
    "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
    "azure.search.documents.indexes.aio.SearchIndexClient.get_knowledge_source_status",
    "azure.search.documents.indexes.models.KnowledgeBase",
    "azure.search.documents.indexes.models.KnowledgeSourceReference",
    "azure.search.documents.indexes.models.SearchIndexKnowledgeSource",
    "azure.search.documents.indexes.models.SearchIndexKnowledgeSourceParameters",
)
_RETRIEVAL_CAPABILITIES = (
    "KnowledgeBaseRetrievalClient.aio",
    "azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalClient.retrieve",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest.retrieval_reasoning_effort",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalResponse",
    "azure.search.documents.knowledgebases.models.KnowledgeRetrievalSemanticIntent",
)
_STREAM_CAPABILITIES = (
    "azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalClient.retrieve_stream",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalStartedEvent",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseResponseCompletedEvent",
)


class TestKnowledgeBaseRetrievalClientAsync(AzureRecordedTestCase):
    @live_test()
    async def test_retrieve_returns_knowledge_base_response(self, endpoint: str) -> None:
        require_capability(*_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES, *_RETRIEVAL_CAPABILITIES)
        from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseRetrievalResponse,
            KnowledgeRetrievalMinimalReasoningEffort,
            KnowledgeRetrievalSemanticIntent,
        )

        async with knowledge_base_resources(
            self,
            endpoint,
            prefix="knowledge-base-retrieve",
            wait_for_active=True,
            description=KNOWLEDGE_BASE_RETRIEVAL_DESCRIPTION,
            source_description=KNOWLEDGE_SOURCE_RETRIEVAL_DESCRIPTION,
        ) as context:
            knowledge_base_name = context.knowledge_base_name
            retrieval_request = KnowledgeBaseRetrievalRequest(
                intents=[KnowledgeRetrievalSemanticIntent(search=RETRIEVAL_QUERY)],
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                include_activity=True,
                output_mode="extractiveData",
            )

            async with KnowledgeBaseRetrievalClient(
                endpoint,
                credential=context.credential,
                knowledge_base_name=knowledge_base_name,
            ) as client:
                result = await client.retrieve(retrieval_request)

            assert isinstance(result, KnowledgeBaseRetrievalResponse)
            assert result.references
            assert result.activity

    @live_test()
    async def test_retrieve_stream_returns_typed_lifecycle_events(self, endpoint: str) -> None:
        require_capability(
            *_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES,
            *_RETRIEVAL_CAPABILITIES,
            *_STREAM_CAPABILITIES,
        )
        from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseActivityRecord,
            KnowledgeBaseActivityStartedEvent,
            KnowledgeBaseMessageTextContent,
            KnowledgeBaseResponseCompletedEvent,
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseRetrievalResponse,
            KnowledgeBaseRetrievalStartedEvent,
            KnowledgeBaseStreamErrorEvent,
            KnowledgeRetrievalMinimalReasoningEffort,
            KnowledgeRetrievalSemanticIntent,
            SearchIndexKnowledgeSourceParams,
        )

        async with knowledge_base_resources(
            self,
            endpoint,
            prefix="knowledge-base-retrieve-stream",
            wait_for_active=True,
            description=KNOWLEDGE_BASE_RETRIEVAL_DESCRIPTION,
            source_description=KNOWLEDGE_SOURCE_RETRIEVAL_DESCRIPTION,
        ) as context:
            retrieval_request = KnowledgeBaseRetrievalRequest(
                intents=[KnowledgeRetrievalSemanticIntent(search=RETRIEVAL_QUERY)],
                knowledge_source_params=[
                    SearchIndexKnowledgeSourceParams(
                        knowledge_source_name=context.knowledge_source_name,
                        include_references=True,
                        include_reference_source_data=True,
                    )
                ],
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                include_activity=True,
                output_mode="extractiveData",
            )

            async with KnowledgeBaseRetrievalClient(
                endpoint,
                credential=context.credential,
                knowledge_base_name=context.knowledge_base_name,
            ) as client:
                started_at = time.perf_counter()
                events = []
                stream = await client.retrieve_stream(
                    retrieval_request, raw_response_hook=log_retrieval_stream_response
                )
                async with stream:
                    async for event in stream:
                        log_retrieval_stream_event(event, event_number=len(events) + 1, started_at=started_at)
                        assert not isinstance(event, KnowledgeBaseStreamErrorEvent), f"Stream error: {event.as_dict()}"
                        events.append(event)

            assert events, "The SSE response did not yield any events"
            assert isinstance(events[0], KnowledgeBaseRetrievalStartedEvent)
            assert events[0].knowledge_base_name == context.knowledge_base_name
            assert events[0].output_mode == "extractiveData"
            assert isinstance(events[-1], KnowledgeBaseResponseCompletedEvent)
            assert isinstance(events[-1].response, KnowledgeBaseRetrievalResponse)
            assert any(isinstance(event, KnowledgeBaseActivityStartedEvent) for event in events[1:-1])
            assert any(isinstance(event, KnowledgeBaseActivityRecord) for event in events[1:-1])
            assert any(isinstance(event, list) and event for event in events[1:-1]), "No streamed references"
            assert events[-1].response.response, "The completed response did not contain any messages"
            assert any(
                isinstance(content, KnowledgeBaseMessageTextContent) and content.text
                for message in events[-1].response.response
                for content in message.content
            ), "The completed response did not contain any text"
            assert events[-1].response.references
            assert events[-1].response.activity
            assert events[-1].status_code in (200, 206)
            assert (
                sum(
                    isinstance(event, (KnowledgeBaseResponseCompletedEvent, KnowledgeBaseStreamErrorEvent))
                    for event in events
                )
                == 1
            )
