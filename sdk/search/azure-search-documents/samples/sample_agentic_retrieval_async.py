# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates the end-to-end agentic retrieval scenario using async clients:
    create a knowledge source over an existing search index, create a knowledge
    base that references it, query the knowledge base with a semantic intent,
    stream typed retrieval payloads, and clean up.

    For knowledge source / knowledge base CRUD details (get, update, list),
    see sample_knowledge_source_crud_async.py and sample_knowledge_base_crud_async.py.

USAGE:
    python sample_agentic_retrieval_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
    4) SAMPLE_RUN_TAG - optional resource-name suffix for this run

    The existing index must have a semantic configuration.
"""

import asyncio
import os

from sample_utils import (
    cleanup_resources_async,
    get_sample_run_tag,
    print_retrieval_summary,
    wait_for_knowledge_source_active_async,
)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

run_tag = get_sample_run_tag()
knowledge_source_name = f"hotels-sample-knowledge-source-{run_tag}"
knowledge_base_name = f"hotels-sample-knowledge-base-{run_tag}"


async def setup_knowledge_base_async():
    # [START setup_knowledge_base_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.models import KnowledgeRetrievalMinimalReasoningEffort

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        knowledge_source = SearchIndexKnowledgeSource(
            name=knowledge_source_name,
            search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
        )
        await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
        print(f"Created: knowledge source '{knowledge_source_name}'")

        knowledge_base = KnowledgeBase(
            name=knowledge_base_name,
            knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
            output_mode="extractiveData",
            retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
        )
        await index_client.create_or_update_knowledge_base(knowledge_base)
        print(f"Created: knowledge base '{knowledge_base_name}'")
        await wait_for_knowledge_source_active_async(index_client, knowledge_source_name)
    # [END setup_knowledge_base_async]


async def retrieve_knowledge_base_async():
    # [START retrieve_knowledge_base_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
    )

    request = KnowledgeBaseRetrievalRequest(
        intents=[KnowledgeRetrievalSemanticIntent(search="hotels with free wifi")],
        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
        include_activity=True,
    )
    async with KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
    ) as retrieval_client:
        result = await retrieval_client.retrieve(request)

    print("Results: knowledge base retrieval")
    print_retrieval_summary(result)
    for message in result.response or []:
        for content in message.content or []:
            if isinstance(content, KnowledgeBaseMessageTextContent):
                print(content.text)
    # [END retrieve_knowledge_base_async]


async def retrieve_stream_knowledge_base_async():  # pylint: disable=too-many-locals
    # [START retrieve_stream_knowledge_base_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseActivityRecord,
        KnowledgeBaseActivityStartedEvent,
        KnowledgeBaseAnswerCompletedEvent,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseResponseCompletedEvent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeBaseRetrievalStartedEvent,
        KnowledgeBaseStreamErrorEvent,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
    )

    request = KnowledgeBaseRetrievalRequest(
        intents=[KnowledgeRetrievalSemanticIntent(search="hotels with free wifi")],
        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
        include_activity=True,
    )
    completed = False
    async with KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
    ) as retrieval_client:
        async with await retrieval_client.retrieve_stream(request) as stream:
            async for payload in stream:
                if isinstance(payload, KnowledgeBaseRetrievalStartedEvent):
                    print(f"Retrieval started: {payload.request_id}")
                elif isinstance(payload, KnowledgeBaseActivityStartedEvent):
                    print(f"Activity started: {payload.id}")
                elif isinstance(payload, KnowledgeBaseActivityRecord):
                    print(f"Activity completed: {payload.id}, elapsed {payload.elapsed_ms} ms")
                elif isinstance(payload, KnowledgeBaseAnswerCompletedEvent):
                    for content in payload.message.content or []:
                        if isinstance(content, KnowledgeBaseMessageTextContent):
                            print(content.text)
                elif isinstance(payload, list):
                    print(f"References received: {len(payload)}")
                    for reference in payload:
                        print(f"Reference: {reference.id}")
                elif isinstance(payload, KnowledgeBaseStreamErrorEvent):
                    raise HttpResponseError(message=f"{payload.error.code}: {payload.error.message}")
                elif isinstance(payload, KnowledgeBaseResponseCompletedEvent):
                    completed = True
                    print(f"Retrieval completed with status {payload.status_code}")
                    print_retrieval_summary(payload.response)
                else:
                    raise TypeError(f"Unexpected retrieval payload: {type(payload).__name__}")
    if not completed:
        raise RuntimeError("Retrieval stream ended without a completed response.")
    # [END retrieve_stream_knowledge_base_async]


async def cleanup_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        await cleanup_resources_async(
            index_client,
            knowledge_base_name=knowledge_base_name,
            knowledge_source_name=knowledge_source_name,
        )


async def main():
    try:
        await setup_knowledge_base_async()
        await retrieve_knowledge_base_async()
        await retrieve_stream_knowledge_base_async()
    finally:
        await cleanup_async()


if __name__ == "__main__":
    asyncio.run(main())
