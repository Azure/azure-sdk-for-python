# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview retrieval request and response options.

USAGE:
    python sample_knowledge_retrieval_response_preview.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_OPENAI_ENDPOINT - endpoint for your Azure OpenAI resource
    4) AZURE_OPENAI_API_KEY - key for your Azure OpenAI resource
    5) AZURE_OPENAI_DEPLOYMENT - deployment name for your chat model
    6) AZURE_OPENAI_MODEL - model name for your chat model
"""

import os
from urllib.parse import urlparse

from sample_utils import (
    cleanup_resources,
    get_sample_run_tag,
    print_retrieval_summary,
    setup_hotel_index,
)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
run_tag = get_sample_run_tag()
index_name = f"hotels-retrieval-response-{run_tag}"
knowledge_source_name = f"hotels-retrieval-response-ks-{run_tag}"
knowledge_base_name = f"hotels-retrieval-response-kb-{run_tag}"


def main():
    index_client = None
    setup_hotel_index(index_name, service_endpoint, key)
    try:
        # [START sample_knowledge_retrieval_response_preview]
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents.indexes import SearchIndexClient
        from azure.search.documents.indexes.models import (
            AzureOpenAIVectorizerParameters,
            KnowledgeBase,
            KnowledgeBaseAzureOpenAIModel,
            KnowledgeSourceReference,
            SearchIndexFieldReference,
            SearchIndexKnowledgeSource,
            SearchIndexKnowledgeSourceParameters,
        )
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseMessage,
            KnowledgeBaseMessageTextContent,
            KnowledgeBaseResponseCompletedEvent,
            KnowledgeBaseRetrievalStartedEvent,
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseSearchIndexReference,
            KnowledgeBaseStreamErrorEvent,
            KnowledgeRetrievalLowReasoningEffort,
            KnowledgeRetrievalSemanticIntent,
            SearchIndexKnowledgeSourceParams,
        )

        index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
        knowledge_source = SearchIndexKnowledgeSource(
            name=knowledge_source_name,
            description="Hotel knowledge source for retrieval response preview",
            results_processing="rerank",
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name=index_name,
                source_data_fields=[
                    SearchIndexFieldReference(name="HotelId"),
                    SearchIndexFieldReference(name="HotelName"),
                    SearchIndexFieldReference(name="Description"),
                    SearchIndexFieldReference(name="Category"),
                    SearchIndexFieldReference(name="Tags"),
                    SearchIndexFieldReference(name="ParkingIncluded"),
                    SearchIndexFieldReference(name="LastRenovationDate"),
                    SearchIndexFieldReference(name="Rating"),
                ],
            ),
        )
        index_client.create_or_update_knowledge_source(knowledge_source)

        knowledge_base = KnowledgeBase(
            name=knowledge_base_name,
            description="Hotel retrieval response preview",
            knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
            models=[
                KnowledgeBaseAzureOpenAIModel(
                    azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                        resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                        api_key=os.environ["AZURE_OPENAI_API_KEY"],
                        deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"],
                        model_name=os.environ["AZURE_OPENAI_MODEL"],
                    )
                )
            ],
            retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
            output_mode="answerSynthesis",
        )
        index_client.create_or_update_knowledge_base(knowledge_base)
        retrieved_knowledge_base = index_client.get_knowledge_base(knowledge_base_name)
        print(f"Retrieved: knowledge base '{retrieved_knowledge_base.name}'")

        retrieval_client = KnowledgeBaseRetrievalClient(
            service_endpoint, AzureKeyCredential(key), knowledge_base_name=knowledge_base_name
        )
        try:
            semantic_request = KnowledgeBaseRetrievalRequest(
                include_activity=True,
                intents=[KnowledgeRetrievalSemanticIntent(search="Which hotels include parking?")],
                max_output_documents=50,
            )
            semantic_result = retrieval_client.retrieve(semantic_request)
            print_retrieval_summary(semantic_result)

            stream_event_types = []
            stream_request_id = None
            with retrieval_client.retrieve_stream(semantic_request) as stream:
                for event in stream:
                    stream_event_types.append(event.event_type)
                    if event.event_type == "retrieval.started" and isinstance(
                        event.data, KnowledgeBaseRetrievalStartedEvent
                    ):
                        stream_request_id = event.data.request_id
                    elif event.event_type == "response.completed" and isinstance(
                        event.data, KnowledgeBaseResponseCompletedEvent
                    ):
                        assert event.data.status_code in {200, 206}
                        print_retrieval_summary(event.data.response)
                    elif event.event_type == "error" and isinstance(event.data, KnowledgeBaseStreamErrorEvent):
                        error_message = event.data.error.message if event.data.error else "Retrieval failed"
                        raise RuntimeError(f"Streaming retrieval error: {error_message}")
            assert stream_event_types[0] == "retrieval.started"
            assert stream_event_types[-1] == "response.completed"
            assert stream_request_id

            message_request = KnowledgeBaseRetrievalRequest(
                include_activity=True,
                messages=[
                    KnowledgeBaseMessage(
                        role="user",
                        content=[KnowledgeBaseMessageTextContent(text="Summarize hotels with parking.")],
                    )
                ],
                knowledge_source_params=[
                    SearchIndexKnowledgeSourceParams(
                        knowledge_source_name=knowledge_source_name,
                        include_references=True,
                        include_reference_source_data=True,
                        results_processing="rerank",
                        max_output_documents=50,
                    )
                ],
            )
            message_result = retrieval_client.retrieve(message_request)
            print_retrieval_summary(message_result)
            search_references = [
                reference
                for reference in message_result.references or []
                if isinstance(reference, KnowledgeBaseSearchIndexReference)
            ]
            assert search_references
            search_host = urlparse(service_endpoint).netloc
            for reference in search_references:
                assert reference.citation_url is not None
                citation = urlparse(reference.citation_url)
                assert citation.scheme == "https"
                assert citation.netloc == search_host

            no_rerank_request = KnowledgeBaseRetrievalRequest(
                include_activity=True,
                intents=[KnowledgeRetrievalSemanticIntent(search="Which hotels include parking?")],
                knowledge_source_params=[
                    SearchIndexKnowledgeSourceParams(
                        knowledge_source_name=knowledge_source_name,
                        include_references=True,
                        results_processing="none",
                        max_output_documents=50,
                    )
                ],
            )
            no_rerank_result = retrieval_client.retrieve(no_rerank_request)
            assert all(reference.reranker_score is None for reference in no_rerank_result.references or [])
        finally:
            retrieval_client.close()
        # [END sample_knowledge_retrieval_response_preview]
    finally:
        if index_client:
            cleanup_resources(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
                index_name=index_name,
            )


if __name__ == "__main__":
    main()
