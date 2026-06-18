# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates persisted retrieve defaults and freshness-aware retrieval using async clients.

USAGE:
    python sample_knowledge_source_freshness_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
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
index_name = f"hotels-freshness-{run_tag}"
knowledge_source_name = f"hotels-freshness-ks-{run_tag}"
knowledge_base_name = f"hotels-freshness-kb-{run_tag}"


async def main():
    await setup_hotel_index_async(index_name, service_endpoint, key)
    # [START sample_knowledge_source_freshness_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
        SearchIndexKnowledgeSourceParams,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        try:
            knowledge_source = SearchIndexKnowledgeSource(
                name=knowledge_source_name,
                description="Hotel knowledge source with persisted retrieve defaults",
                search_index_parameters=SearchIndexKnowledgeSourceParameters(
                    search_index_name=index_name,
                    base_filter="IsDeleted eq false",
                ),
            )
            await index_client.create_or_update_knowledge_source(knowledge_source)

            knowledge_base = KnowledgeBase(
                name=knowledge_base_name,
                description="Hotel freshness retrieval",
                knowledge_sources=[
                    KnowledgeSourceReference(
                        name=knowledge_source_name,
                        enable_freshness=True,
                        enable_image_serving=True,
                    )
                ],
                output_mode="extractiveData",
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
            )
            await index_client.create_or_update_knowledge_base(knowledge_base)
            retrieved_knowledge_base = await index_client.get_knowledge_base(knowledge_base_name)
            print(f"Retrieved: knowledge base '{retrieved_knowledge_base.name}'")

            retrieval_client = KnowledgeBaseRetrievalClient(
                service_endpoint, AzureKeyCredential(key), knowledge_base_name=knowledge_base_name
            )
            try:
                request = KnowledgeBaseRetrievalRequest(
                    include_activity=True,
                    intents=[
                        KnowledgeRetrievalSemanticIntent(
                            search="Which hotels were renovated recently and include parking?"
                        )
                    ],
                    knowledge_source_params=[
                        SearchIndexKnowledgeSourceParams(
                            knowledge_source_name=knowledge_source_name,
                            include_references=True,
                            include_reference_source_data=True,
                            always_query_source=True,
                            enable_image_serving=True,
                        )
                    ],
                )
                retrieval_result = await retrieval_client.retrieve(request)
                print_retrieval_summary(retrieval_result)
            finally:
                await retrieval_client.close()
            # [END sample_knowledge_source_freshness_preview_async]
        finally:
            await cleanup_resources_async(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
                index_name=index_name,
            )


if __name__ == "__main__":
    asyncio.run(main())
