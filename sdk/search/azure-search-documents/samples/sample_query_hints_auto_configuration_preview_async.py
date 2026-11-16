# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Asynchronously seed country facets, configure automatic grounding, retrieve
    hotels, and verify generated query-hint filters and matching references.

USAGE:
    python sample_query_hints_auto_configuration_preview_async.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT, AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_CHAT_DEPLOYMENT, and AZURE_OPENAI_CHAT_MODEL.
    Optional AZURE_SEARCH_API_KEY and AZURE_OPENAI_API_KEY override identities.
    Requires the November preview, automatic hints, semantic search, native model
    access, and one free index slot. No document ACLs or sensitivity labels.
    AZURE_SEARCH_HINT_REFRESH=true additionally tests a new country after the
    60-second TTL; it does not prove a cache hit. New resources are cleaned up.
"""

import asyncio
import os
import uuid

from sample_utils import (
    cleanup_preview_resources_async,
    get_sample_run_tag,
    prepare_preview_hotel_index_async,
    preview_hotel_documents,
    validate_preview_auto_hint,
    wait_for_knowledge_source_active_async,
)


async def main():  # pylint: disable=too-many-locals,too-many-statements
    # [START sample_query_hints_auto_configuration_preview_async]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.aio import SearchClient
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceFilterHint,
        SearchIndexKnowledgeSourceFilterHintAutoConfiguration,
        SearchIndexKnowledgeSourceParameters,
        SearchIndexKnowledgeSourceQueryHints,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseMessage,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalLowReasoningEffort,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    model = KnowledgeBaseAzureOpenAIModel(
        azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
            resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
            deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            model_name=os.environ["AZURE_OPENAI_CHAT_MODEL"],
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        )
    )
    index_name = f"hotels-auto-hints-{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    source_name, base_name = index_name + "-source", index_name + "-kb"
    created: list[tuple[str, str]] = []
    async with DefaultAzureCredential(process_timeout=60) as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        async with SearchIndexClient(endpoint, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as indexes:
            try:
                await prepare_preview_hotel_index_async(
                    indexes, endpoint, credential, index_name, preview_hotel_documents(), created
                )
                async with SearchClient(
                    endpoint, index_name, credential, api_version=ApiVersion.V2026_11_01_PREVIEW
                ) as search:
                    facets = await (await search.search(search_text="*", facets=["country,count:16"])).get_facets()
                    print("Available country facets:", facets)
                    await indexes.create_or_update_knowledge_source(
                        SearchIndexKnowledgeSource(
                            name=source_name,
                            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                                search_index_name=index_name,
                                query_hints=SearchIndexKnowledgeSourceQueryHints(
                                    filters=[
                                        SearchIndexKnowledgeSourceFilterHint(
                                            field="country",
                                            auto_configuration=SearchIndexKnowledgeSourceFilterHintAutoConfiguration(
                                                cache_ttl=60, max_facet_value_count=16
                                            ),
                                            filter_instructions=(
                                                "When a country is specified, filter country using the exact "
                                                "country name from the resolved facet values."
                                            ),
                                        )
                                    ]
                                ),
                            ),
                        ),
                        match_condition=MatchConditions.IfMissing,
                    )
                    created.append(("knowledge_source", source_name))
                    await wait_for_knowledge_source_active_async(indexes, source_name)
                    stored = await indexes.get_knowledge_source(source_name)
                    if not isinstance(stored, SearchIndexKnowledgeSource):
                        raise RuntimeError("The created source must reference the sample search index.")
                    hints = stored.search_index_parameters.query_hints
                    if not hints or not hints.filters or not hints.filters[0].auto_configuration:
                        raise RuntimeError("The stored source did not preserve automatic facet grounding.")
                    if hints.filters[0].field_values is not None:
                        raise RuntimeError("This scenario must not supply manual grounding values.")
                    await indexes.create_or_update_knowledge_base(
                        KnowledgeBase(
                            name=base_name,
                            knowledge_sources=[KnowledgeSourceReference(name=source_name)],
                            models=[model],
                            retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
                            output_mode="extractiveData",
                        ),
                        match_condition=MatchConditions.IfMissing,
                    )
                    created.append(("knowledge_base", base_name))
                    async with KnowledgeBaseRetrievalClient(
                        endpoint=endpoint,
                        knowledge_base_name=base_name,
                        credential=credential,
                        api_version=ApiVersion.V2026_11_01_PREVIEW,
                    ) as retrieval:
                        countries = [("Canada", {"hotel-ca-1", "hotel-ca-2"})]
                        if os.environ.get("AZURE_SEARCH_HINT_REFRESH", "").lower() == "true":
                            countries.append(("Japan", {"hotel-jp-1"}))
                        for country, expected_keys in countries:
                            if country == "Japan":
                                document = {
                                    "id": "hotel-jp-1",
                                    "title": "Garden Hotel",
                                    "country": "Japan",
                                    "content": "Hotel guest benefits include complimentary internet and breakfast.",
                                }
                                if not all(item.succeeded for item in await search.upload_documents([document])):
                                    raise RuntimeError("The new country fixture could not be uploaded.")
                                for _ in range(30):
                                    if await search.get_document_count() == 4:
                                        break
                                    await asyncio.sleep(2)
                                else:
                                    raise TimeoutError("The new country fixture did not become searchable.")
                                print("Waiting 65 seconds before querying the newly added facet value.")
                                await asyncio.sleep(65)
                            result = await retrieval.retrieve(
                                KnowledgeBaseRetrievalRequest(
                                    messages=[
                                        KnowledgeBaseMessage(
                                            role="user",
                                            content=[
                                                KnowledgeBaseMessageTextContent(
                                                    text=f"Find hotel guest benefits for hotels in {country} only."
                                                )
                                            ],
                                        )
                                    ],
                                    include_activity=True,
                                )
                            )
                            validate_preview_auto_hint(result, country, source_name, expected_keys)
                    print("No request-time filter was supplied. TTL configuration alone is not cache-hit evidence.")
            finally:
                await cleanup_preview_resources_async(indexes, created)
    # [END sample_query_hints_auto_configuration_preview_async]


if __name__ == "__main__":
    asyncio.run(main())
