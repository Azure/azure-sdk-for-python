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
            KnowledgeBaseRetrievalRequest,
            KnowledgeRetrievalLowReasoningEffort,
            KnowledgeRetrievalSemanticIntent,
            SearchIndexKnowledgeSourceParams,
        )

        index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
        knowledge_source = SearchIndexKnowledgeSource(
            name=knowledge_source_name,
            description="Hotel knowledge source for retrieval response preview",
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
                        max_output_documents=50,
                    )
                ],
            )
            message_result = retrieval_client.retrieve(message_request)
            print_retrieval_summary(message_result)
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
