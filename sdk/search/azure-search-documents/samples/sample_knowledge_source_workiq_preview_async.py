# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview Work IQ knowledge source setup and retrieval using async clients.

USAGE:
    python sample_knowledge_source_workiq_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION - raw bearer token for query source access
"""

import asyncio
import os

from sample_utils import (
    cleanup_resources_async,
    get_sample_run_tag,
    print_retrieval_summary,
)


service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
run_tag = get_sample_run_tag()
knowledge_source_name = f"hotels-workiq-ks-{run_tag}"
knowledge_base_name = f"hotels-workiq-kb-{run_tag}"


async def main():
    # [START sample_knowledge_source_workiq_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import KnowledgeBase, KnowledgeSourceReference, WorkIQKnowledgeSource
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
        WorkIQKnowledgeSourceParams,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        try:
            knowledge_source = WorkIQKnowledgeSource(
                name=knowledge_source_name,
                description="Hotel Work IQ knowledge source",
            )
            created_knowledge_source = await index_client.create_or_update_knowledge_source(knowledge_source)
            print(f"Created: knowledge source '{created_knowledge_source.name}'")

            retrieved_knowledge_source = await index_client.get_knowledge_source(knowledge_source_name)
            print(f"Retrieved: knowledge source '{retrieved_knowledge_source.name}'")

            knowledge_base = KnowledgeBase(
                name=knowledge_base_name,
                description="Hotel Work IQ knowledge base",
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                output_mode="extractiveData",
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
            )
            await index_client.create_or_update_knowledge_base(knowledge_base)

            retrieval_client = KnowledgeBaseRetrievalClient(
                service_endpoint, AzureKeyCredential(key), knowledge_base_name=knowledge_base_name
            )
            try:
                request = KnowledgeBaseRetrievalRequest(
                    include_activity=True,
                    intents=[KnowledgeRetrievalSemanticIntent(search="Find hotel information from Work IQ.")],
                    max_runtime_in_seconds=120,
                    knowledge_source_params=[
                        WorkIQKnowledgeSourceParams(
                            knowledge_source_name=knowledge_source_name,
                            include_references=True,
                            include_reference_source_data=True,
                        )
                    ],
                )
                retrieval_result = await retrieval_client.retrieve(
                    request,
                    query_source_authorization=os.environ["AZURE_SEARCH_QUERY_SOURCE_AUTHORIZATION"],
                )
            finally:
                await retrieval_client.close()
            print_retrieval_summary(retrieval_result)
            # [END sample_knowledge_source_workiq_preview_async]
        finally:
            await cleanup_resources_async(
                index_client,
                knowledge_base_name=knowledge_base_name,
                knowledge_source_name=knowledge_source_name,
            )


if __name__ == "__main__":
    asyncio.run(main())
