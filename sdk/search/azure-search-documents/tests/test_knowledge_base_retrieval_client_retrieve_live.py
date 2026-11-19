# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``KnowledgeBaseRetrievalClient.retrieve``."""

from __future__ import annotations

from azure.core import MatchConditions
from devtools_testutils import AzureRecordedTestCase

from _capabilities import require_capability
from _search_helpers import (
    knowledge_base_resources,
    knowledge_source_resources,
    live_test,
    make_search_client,
    poll_until,
    upload_documents,
    wait_for_document_count,
)

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
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest.retrieval_reasoning_effort",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalResponse",
    "azure.search.documents.knowledgebases.models.KnowledgeRetrievalSemanticIntent",
)
_STREAM_CAPABILITIES = (
    "azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient.retrieve_stream",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalStartedEvent",
    "azure.search.documents.knowledgebases.models.KnowledgeBaseResponseCompletedEvent",
)


class TestKnowledgeBaseRetrievalClient(AzureRecordedTestCase):
    @live_test()
    def test_retrieve_tool_name_limits_sources_and_clearing_restores_kb_retrieval(self, endpoint: str) -> None:
        require_capability(
            *_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES,
            *_RETRIEVAL_CAPABILITIES,
            "azure.search.documents.indexes.SearchIndexClient.create_or_update_knowledge_base",
            "azure.search.documents.indexes.SearchIndexClient.get_knowledge_base",
            "azure.search.documents.indexes.models.KnowledgeBase.tools",
            "azure.search.documents.indexes.models.KnowledgeBaseTool",
            "azure.search.documents.indexes.models.KnowledgeBaseToolKnowledgeSourceReference",
            "azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest.tool_name",
            "azure.search.documents.knowledgebases.models.KnowledgeRetrievalMinimalReasoningEffort",
            "azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexActivityRecord",
            "azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexReference",
        )
        from azure.search.documents.indexes.models import (
            KnowledgeBaseTool,
            KnowledgeBaseToolKnowledgeSourceReference,
            KnowledgeSourceReference,
        )
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseSearchIndexActivityRecord,
            KnowledgeBaseSearchIndexReference,
            KnowledgeRetrievalMinimalReasoningEffort,
            KnowledgeRetrievalSemanticIntent,
        )
        from _preview_helpers import knowledge_base_tool_documents

        with knowledge_source_resources(self, endpoint, prefix="retrieve-tool-excluded") as excluded:
            with knowledge_base_resources(
                self, endpoint, prefix="retrieve-tool-selected", wait_for_active=True
            ) as context:
                for resource, documents in zip((context, excluded), knowledge_base_tool_documents()):
                    with make_search_client(
                        endpoint, resource.index_name, credential=context.credential
                    ) as search_client:
                        upload_documents(search_client, documents)
                        wait_for_document_count(self, search_client, len(documents))
                poll_until(
                    lambda: context.index_client.get_knowledge_source_status(excluded.knowledge_source_name),
                    predicate=lambda status: status.synchronization_status == "active",
                    interval=5 if self.is_live else 0,
                )
                tool_name = "selected-hotels"
                base = context.knowledge_base
                base.knowledge_sources.append(KnowledgeSourceReference(name=excluded.knowledge_source_name))
                base.retrieval_reasoning_effort = KnowledgeRetrievalMinimalReasoningEffort()
                base.tools = [
                    KnowledgeBaseTool(
                        name=tool_name,
                        description="Retrieve hotels from the selected hotel source.",
                        knowledge_sources=[
                            KnowledgeBaseToolKnowledgeSourceReference(name=context.knowledge_source_name)
                        ],
                        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                    )
                ]
                context.index_client.create_or_update_knowledge_base(
                    base, match_condition=MatchConditions.IfNotModified
                )
                fetched = context.index_client.get_knowledge_base(context.knowledge_base_name)
                assert len(fetched.tools) == 1
                assert fetched.tools[0].name == tool_name
                assert [source.name for source in fetched.tools[0].knowledge_sources] == [context.knowledge_source_name]

                with KnowledgeBaseRetrievalClient(
                    endpoint, credential=context.credential, knowledge_base_name=context.knowledge_base_name
                ) as client:
                    request = KnowledgeBaseRetrievalRequest(
                        intents=[KnowledgeRetrievalSemanticIntent(search=RETRIEVAL_QUERY)],
                        include_activity=True,
                    )
                    baseline = client.retrieve(request)
                    assert {reference.doc_key for reference in baseline.references} == {
                        "hotel-selected-1",
                        "hotel-selected-2",
                        "hotel-excluded",
                    }

                    request.tool_name = tool_name
                    result = client.retrieve(request)
                    assert result.references
                    assert all(
                        isinstance(reference, KnowledgeBaseSearchIndexReference) for reference in result.references
                    )
                    assert {reference.doc_key for reference in result.references} == {
                        "hotel-selected-1",
                        "hotel-selected-2",
                    }
                    activities = [
                        activity
                        for activity in result.activity
                        if isinstance(activity, KnowledgeBaseSearchIndexActivityRecord)
                    ]
                    assert activities
                    assert {activity.knowledge_source_name for activity in activities} == {
                        context.knowledge_source_name
                    }
                    assert all(activity.error is None for activity in result.activity)

                    fetched.tools = []
                    context.index_client.create_or_update_knowledge_base(
                        fetched, match_condition=MatchConditions.IfNotModified
                    )
                    assert not context.index_client.get_knowledge_base(context.knowledge_base_name).tools
                    request.tool_name = None
                    restored = client.retrieve(request)
                    assert {reference.doc_key for reference in restored.references} == {
                        "hotel-selected-1",
                        "hotel-selected-2",
                        "hotel-excluded",
                    }

    @live_test()
    def test_retrieve_returns_knowledge_base_response(self, endpoint: str) -> None:
        require_capability(*_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES, *_RETRIEVAL_CAPABILITIES)
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseRetrievalResponse,
            KnowledgeRetrievalMinimalReasoningEffort,
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
                intents=[KnowledgeRetrievalSemanticIntent(search=RETRIEVAL_QUERY)],
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
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

    @live_test()
    def test_retrieve_stream_returns_typed_lifecycle_events(self, endpoint: str) -> None:
        require_capability(
            *_KNOWLEDGE_BASE_RESOURCE_CAPABILITIES,
            *_RETRIEVAL_CAPABILITIES,
            *_STREAM_CAPABILITIES,
        )
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseResponseCompletedEvent,
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseRetrievalResponse,
            KnowledgeBaseRetrievalStartedEvent,
            KnowledgeBaseStreamErrorEvent,
            KnowledgeRetrievalMinimalReasoningEffort,
            KnowledgeRetrievalSemanticIntent,
        )

        with knowledge_base_resources(
            self,
            endpoint,
            prefix="knowledge-base-retrieve-stream",
            wait_for_active=True,
            description=KNOWLEDGE_BASE_RETRIEVAL_DESCRIPTION,
            source_description=KNOWLEDGE_SOURCE_RETRIEVAL_DESCRIPTION,
        ) as context:
            retrieval_request = KnowledgeBaseRetrievalRequest(
                intents=[KnowledgeRetrievalSemanticIntent(search=RETRIEVAL_QUERY)],
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
            )

            with KnowledgeBaseRetrievalClient(
                endpoint,
                credential=context.credential,
                knowledge_base_name=context.knowledge_base_name,
            ) as client:
                with client.retrieve_stream(retrieval_request) as stream:
                    events = list(stream)

            assert isinstance(events[0], KnowledgeBaseRetrievalStartedEvent)
            assert isinstance(events[-1], KnowledgeBaseResponseCompletedEvent)
            assert events[-1].status_code in (200, 206)
            assert isinstance(events[-1].response, KnowledgeBaseRetrievalResponse)
            assert not any(isinstance(event, KnowledgeBaseStreamErrorEvent) for event in events)
            assert sum(isinstance(event, KnowledgeBaseResponseCompletedEvent) for event in events) == 1
