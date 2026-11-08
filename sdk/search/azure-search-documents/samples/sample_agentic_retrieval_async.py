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
    The optional message-based planning and answer-synthesis scenario also needs:
    5) AZURE_OPENAI_ENDPOINT - Azure OpenAI endpoint
    6) AZURE_OPENAI_CHAT_DEPLOYMENT - an existing supported chat deployment
    7) AZURE_OPENAI_CHAT_MODEL - its model name (for example, gpt-5.4)
    Grant the Search service's managed identity Cognitive Services OpenAI User on
    that resource. Explicit intents bypass query planning; messages use the model.
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
        SearchIndexFieldReference,
    )
    from azure.search.documents.knowledgebases.models import KnowledgeRetrievalMinimalReasoningEffort

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        knowledge_source = SearchIndexKnowledgeSource(
            name=knowledge_source_name,
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name=index_name,
                base_filter="Rating ge 4",
                source_data_fields=[SearchIndexFieldReference(name="HotelName")],
            ),
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
        KnowledgeBaseAzureBlobActivityRecord,
        KnowledgeBaseAzureBlobReference,
        KnowledgeBaseFileActivityRecord,
        KnowledgeBaseFileReference,
        KnowledgeBaseIndexedOneLakeActivityRecord,
        KnowledgeBaseIndexedOneLakeReference,
        KnowledgeBaseIndexedSharePointActivityRecord,
        KnowledgeBaseIndexedSharePointReference,
        KnowledgeBaseIndexedSqlActivityRecord,
        KnowledgeBaseIndexedSqlReference,
        KnowledgeBaseModelAnswerSynthesisActivityRecord,
        KnowledgeBaseModelQueryPlanningActivityRecord,
        KnowledgeBaseSearchIndexActivityRecord,
        KnowledgeBaseSearchIndexReference,
        KnowledgeBaseWebActivityRecord,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
        KnowledgeRetrievalIntentType,
        KnowledgeRetrievalReasoningEffortKind,
        SearchIndexKnowledgeSourceParams,
    )
    from azure.search.documents.knowledgebases.types import (
        KnowledgeBaseRetrievalRequest as KnowledgeBaseRetrievalRequestInput,
        KnowledgeRetrievalIntent as KnowledgeRetrievalIntentInput,
        KnowledgeRetrievalMinimalReasoningEffort as KnowledgeRetrievalMinimalReasoningEffortInput,
        KnowledgeRetrievalReasoningEffort as KnowledgeRetrievalReasoningEffortInput,
        KnowledgeRetrievalSemanticIntent as KnowledgeRetrievalSemanticIntentInput,
    )

    request = KnowledgeBaseRetrievalRequest(
        intents=[KnowledgeRetrievalSemanticIntent(search="hotels with free wifi")],
        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
        include_activity=True,
        output_mode="extractiveData",
        max_output_documents=3,
        knowledge_source_params=[
            SearchIndexKnowledgeSourceParams(
                knowledge_source_name=knowledge_source_name,
                include_references=True,
                include_reference_source_data=True,
                always_query_source=True,
                fail_on_error=True,
                max_output_documents=3,
            )
        ],
    )
    async with KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
    ) as retrieval_client:
        result = await retrieval_client.retrieve(request)

        typed_intent: KnowledgeRetrievalSemanticIntentInput = {
            "type": KnowledgeRetrievalIntentType.SEMANTIC,
            "search": "hotels with free wifi",
        }
        intent_input: KnowledgeRetrievalIntentInput = typed_intent
        typed_effort: KnowledgeRetrievalMinimalReasoningEffortInput = {
            "kind": KnowledgeRetrievalReasoningEffortKind.MINIMAL
        }
        effort_input: KnowledgeRetrievalReasoningEffortInput = typed_effort
        typed_request: KnowledgeBaseRetrievalRequestInput = {
            "intents": [intent_input],
            "retrievalReasoningEffort": effort_input,
            "includeActivity": True,
            "outputMode": "extractiveData",
            "maxOutputDocuments": 3,
        }
        print_retrieval_summary(await retrieval_client.retrieve(typed_request))

    print("Results: knowledge base retrieval")
    print_retrieval_summary(result)
    for message in result.response or []:
        for content in message.content or []:
            if isinstance(content, KnowledgeBaseMessageTextContent):
                print(content.text)
    for activity in result.activity or []:
        print(f"Activity {activity.id}: {activity.started_at} to {activity.completed_at}")
        print(f"Warning: {activity.warning}")
        if isinstance(
            activity,
            (
                KnowledgeBaseSearchIndexActivityRecord,
                KnowledgeBaseAzureBlobActivityRecord,
                KnowledgeBaseIndexedOneLakeActivityRecord,
                KnowledgeBaseWebActivityRecord,
                KnowledgeBaseFileActivityRecord,
                KnowledgeBaseIndexedSharePointActivityRecord,
                KnowledgeBaseIndexedSqlActivityRecord,
            ),
        ):
            print(f"Source: {activity.knowledge_source_name}; documents: {activity.count}")
        elif isinstance(
            activity, (KnowledgeBaseModelQueryPlanningActivityRecord, KnowledgeBaseModelAnswerSynthesisActivityRecord)
        ):
            if activity.model is not None:
                print(f"Model: {activity.model.model_name}; deployment: {activity.model.deployment_id}")
            print(f"Input tokens: {activity.input_tokens}; output tokens: {activity.output_tokens}")
    for reference in result.references or []:
        if isinstance(reference, KnowledgeBaseSearchIndexReference):
            print(f"Document: {reference.doc_key}; source data: {reference.source_data}")
        if isinstance(
            reference,
            (
                KnowledgeBaseSearchIndexReference,
                KnowledgeBaseAzureBlobReference,
                KnowledgeBaseFileReference,
                KnowledgeBaseIndexedOneLakeReference,
                KnowledgeBaseIndexedSharePointReference,
                KnowledgeBaseIndexedSqlReference,
            ),
        ):
            print(f"Search-owned citation URL: {reference.citation_url}")
            # Following a citation URL requires Search authorization, not anonymous access.
    # [END retrieve_knowledge_base_async]


async def retrieve_with_messages_async():
    variables = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_CHAT_DEPLOYMENT", "AZURE_OPENAI_CHAT_MODEL")
    if not all(os.environ.get(name) for name in variables):
        print("Skipping message planning and synthesis; set " + ", ".join(variables))
        return

    # [START retrieve_with_messages_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        CorsOptions,
        KnowledgeBaseAzureOpenAIModel,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseMessage,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalLowReasoningEffort,
        KnowledgeRetrievalMediumReasoningEffort,
    )

    async with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as index_client:
        knowledge_base = await index_client.get_knowledge_base(knowledge_base_name)
        knowledge_base.models = [
            KnowledgeBaseAzureOpenAIModel(
                azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                    resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                    deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
                    model_name=os.environ["AZURE_OPENAI_CHAT_MODEL"],
                )
            )
        ]
        knowledge_base.cors_options = CorsOptions(allowed_origins=["https://myapp.example.com"], max_age_in_seconds=300)
        knowledge_base.retrieval_instructions = "Prioritize hotels with free parking and describe their amenities."
        knowledge_base.answer_instructions = "Answer concisely using only retrieved hotel evidence and cite sources."
        knowledge_base.output_mode = "answerSynthesis"
        knowledge_base.retrieval_reasoning_effort = KnowledgeRetrievalLowReasoningEffort()
        await index_client.create_or_update_knowledge_base(knowledge_base)

    async with KnowledgeBaseRetrievalClient(
        service_endpoint, credential=AzureKeyCredential(key), knowledge_base_name=knowledge_base_name
    ) as retrieval_client:
        request = KnowledgeBaseRetrievalRequest(
            messages=[
                KnowledgeBaseMessage(
                    role="user",
                    content=[KnowledgeBaseMessageTextContent(text="Which highly rated hotels offer free parking?")],
                )
            ],
            include_activity=True,
            output_mode="answerSynthesis",
            retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
            max_output_documents=5,
        )
        result = await retrieval_client.retrieve(request)
        for message in result.response or []:
            for content in message.content or []:
                if isinstance(content, KnowledgeBaseMessageTextContent):
                    print(content.text)
        print_retrieval_summary(result)

        request.output_mode = "extractiveData"
        request.retrieval_reasoning_effort = KnowledgeRetrievalMediumReasoningEffort()
        request.max_output_documents = 3
        print_retrieval_summary(await retrieval_client.retrieve(request))
    # [END retrieve_with_messages_async]


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
                    if payload.status_code not in (200, 206):
                        raise RuntimeError(f"Unexpected completion status: {payload.status_code}")
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
        await retrieve_with_messages_async()
    finally:
        await cleanup_async()


if __name__ == "__main__":
    asyncio.run(main())
