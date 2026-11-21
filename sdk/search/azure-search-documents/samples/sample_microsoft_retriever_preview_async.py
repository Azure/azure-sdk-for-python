# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Explicitly select Microsoft Retriever 1 for a knowledge base, verify its saved
    model selection, and asynchronously retrieve seeded hotel facts with minimal effort.

USAGE:
    python sample_microsoft_retriever_preview_async.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and optionally AZURE_SEARCH_API_KEY.
    Requires a November-preview service enabled for Microsoft Retriever 1 and
    paid standard Knowledge Retrieval. This model has no free tier.
    This sample never changes the service's billing settings.
    No customer model endpoint or deployment is configured. Without a Search key,
    DefaultAzureCredential authenticates the caller. Only new owned resources
    are created and cleaned up. Extractive output does not demonstrate external
    model answer synthesis or billing reconciliation.
"""

import asyncio
import os
import uuid

from sample_utils import (
    cleanup_preview_resources_async,
    get_sample_run_tag,
    prepare_preview_hotel_index_async,
    preview_hotel_documents,
    validate_preview_retrieval,
    wait_for_knowledge_source_active_async,
)


async def main():  # pylint: disable=too-many-locals
    # [START sample_microsoft_retriever_preview_async]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeBaseMicrosoftRetriever1Model,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    name = f"hotels-mr1-{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    source_name, base_name = name + "-source", name + "-kb"
    documents = preview_hotel_documents()
    created: list[tuple[str, str]] = []
    async with DefaultAzureCredential() as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        async with SearchIndexClient(endpoint, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as indexes:
            try:
                await prepare_preview_hotel_index_async(indexes, endpoint, credential, name, documents, created)
                await indexes.create_or_update_knowledge_source(
                    SearchIndexKnowledgeSource(
                        name=source_name,
                        search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=name),
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                created.append(("knowledge_source", source_name))
                await wait_for_knowledge_source_active_async(indexes, source_name)
                await indexes.create_or_update_knowledge_base(
                    KnowledgeBase(
                        name=base_name,
                        knowledge_sources=[KnowledgeSourceReference(name=source_name)],
                        models=[KnowledgeBaseMicrosoftRetriever1Model()],
                        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                        output_mode="extractiveData",
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                created.append(("knowledge_base", base_name))
                stored = await indexes.get_knowledge_base(base_name)
                assert stored.models and len(stored.models) == 1
                assert isinstance(stored.models[0], KnowledgeBaseMicrosoftRetriever1Model)
                async with KnowledgeBaseRetrievalClient(
                    endpoint=endpoint,
                    knowledge_base_name=base_name,
                    credential=credential,
                    api_version=ApiVersion.V2026_11_01_PREVIEW,
                ) as retrieval:
                    result = await retrieval.retrieve(
                        KnowledgeBaseRetrievalRequest(
                            intents=[
                                KnowledgeRetrievalSemanticIntent(
                                    search="Find hotels offering complimentary wireless internet and breakfast."
                                )
                            ],
                            include_activity=True,
                        )
                    )
                    validate_preview_retrieval(result, {item["id"] for item in documents}, {source_name})
                    print("Saved model selection:", stored.models[0].kind)
                    print("Activity types:", [activity.type for activity in result.activity or []])
                    print("Minimal retrieval and extractive output used no customer model deployment.")
            finally:
                await cleanup_preview_resources_async(indexes, created)
    # [END sample_microsoft_retriever_preview_async]


if __name__ == "__main__":
    asyncio.run(main())
