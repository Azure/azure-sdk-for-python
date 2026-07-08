# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview knowledge base configuration using async clients.

USAGE:
    python sample_knowledge_base_configuration_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_OPENAI_ENDPOINT - endpoint for your Azure OpenAI resource
    4) AZURE_OPENAI_API_KEY - key for your Azure OpenAI resource
    5) AZURE_OPENAI_DEPLOYMENT - deployment name for your chat model
    6) AZURE_OPENAI_MODEL - model name for your chat model
"""

import asyncio
import os

from sample_utils import (
    cleanup_resources_async,
    get_sample_run_tag,
    print_retrieval_summary,
    setup_hotel_index_async,
)


service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
run_tag = get_sample_run_tag()
index_name = f"hotels-kb-config-{run_tag}"
knowledge_source_name = f"hotels-kb-config-ks-{run_tag}"
knowledge_base_name = f"hotels-kb-config-kb-{run_tag}"


async def main():
    await setup_hotel_index_async(index_name, service_endpoint, key)
    # [START sample_knowledge_base_configuration_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        CorsOptions,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseMessage,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalLowReasoningEffort,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        try:
            knowledge_source = SearchIndexKnowledgeSource(
                name=knowledge_source_name,
                description="Hotel knowledge source with default parking filter",
                search_index_parameters=SearchIndexKnowledgeSourceParameters(
                    search_index_name=index_name,
                    base_filter="ParkingIncluded eq true and IsDeleted eq false",
                ),
            )
            await index_client.create_or_update_knowledge_source(knowledge_source)
            retrieved_knowledge_source = await index_client.get_knowledge_source(knowledge_source_name)
            print(f"Retrieved: knowledge source '{retrieved_knowledge_source.name}'")

            knowledge_base = KnowledgeBase(
                name=knowledge_base_name,
                description="Hotel knowledge base with preview configuration",
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                cors_options=CorsOptions(allowed_origins=["https://app.contoso.com"], max_age_in_seconds=300),
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
            created_knowledge_base = await index_client.create_or_update_knowledge_base(knowledge_base)
            print(f"Created: knowledge base '{created_knowledge_base.name}'")
            retrieved_knowledge_base = await index_client.get_knowledge_base(knowledge_base_name)
            print(f"Retrieved: knowledge base '{retrieved_knowledge_base.name}'")

            retrieval_client = KnowledgeBaseRetrievalClient(
                service_endpoint, AzureKeyCredential(key), knowledge_base_name=knowledge_base_name
            )
            try:
                request = KnowledgeBaseRetrievalRequest(
                    include_activity=True,
                    messages=[
                        KnowledgeBaseMessage(
                            role="user",
                            content=[KnowledgeBaseMessageTextContent(text="Which hotels include parking?")],
                        )
                    ],
                )
                retrieval_result = await retrieval_client.retrieve(request)
            finally:
                await retrieval_client.close()
            print_retrieval_summary(retrieval_result)
            # [END sample_knowledge_base_configuration_preview_async]
        finally:
            await cleanup_resources_async(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
                index_name=index_name,
            )


if __name__ == "__main__":
    asyncio.run(main())
