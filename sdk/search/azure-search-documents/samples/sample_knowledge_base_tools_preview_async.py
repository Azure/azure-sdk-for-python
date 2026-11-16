# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Asynchronously configure named retrieval tools, verify source and saved-filter
    restrictions, and clear tools to restore normal knowledge-base retrieval.
    Uses the SDK's direct retrieval path, not MCP discovery or tools/call.

USAGE:
    python sample_knowledge_base_tools_preview_async.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and optionally AZURE_SEARCH_API_KEY.
    Requires 2026-11-01-preview, semantic search, KB Tools, and two free index
    slots. No model is required. Only newly created fixtures are cleaned up.
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


async def main():  # pylint: disable=too-many-locals,too-many-statements
    # [START sample_knowledge_base_tools_preview_async]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeBaseRetrieveDefaults,
        KnowledgeBaseTool,
        KnowledgeBaseToolKnowledgeSourceReference,
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
    tag = f"hotels-tools-{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    hotel_source, guide_source, base_name = tag + "-hotels", tag + "-guides", tag + "-kb"
    hotels = preview_hotel_documents()
    guides = [
        {
            "id": "hotel-guide",
            "title": "Hotel guest benefits guide",
            "content": "Hotel guest benefits include complimentary wireless internet, breakfast, and parking.",
            "country": "Canada",
        }
    ]
    all_keys = {document["id"] for document in hotels + guides}
    created: list[tuple[str, str]] = []
    async with DefaultAzureCredential(process_timeout=60) as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        async with SearchIndexClient(endpoint, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as indexes:
            try:
                for source_name, documents in ((hotel_source, hotels), (guide_source, guides)):
                    await prepare_preview_hotel_index_async(
                        indexes, endpoint, credential, source_name, documents, created
                    )
                    await indexes.create_or_update_knowledge_source(
                        SearchIndexKnowledgeSource(
                            name=source_name,
                            search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=source_name),
                        ),
                        match_condition=MatchConditions.IfMissing,
                    )
                    created.append(("knowledge_source", source_name))
                    await wait_for_knowledge_source_active_async(indexes, source_name)
                    await indexes.get_knowledge_source(source_name)

                await indexes.create_or_update_knowledge_base(
                    KnowledgeBase(
                        name=base_name,
                        knowledge_sources=[
                            KnowledgeSourceReference(name=hotel_source),
                            KnowledgeSourceReference(name=guide_source),
                        ],
                        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                        output_mode="extractiveData",
                        tools=[
                            KnowledgeBaseTool(
                                name="canada-hotels",
                                description=(
                                    "Find guest benefits at Canadian hotels, excluding the separate hotel guide."
                                ),
                                knowledge_sources=[
                                    KnowledgeBaseToolKnowledgeSourceReference(
                                        name=hotel_source,
                                        filter_add_on="country eq 'Canada'",
                                        always_query_source=True,
                                        fail_on_error=True,
                                    )
                                ],
                                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                                retrieve_defaults=KnowledgeBaseRetrieveDefaults(
                                    max_runtime_in_seconds=30,
                                    max_output_documents=3,
                                    max_output_size_in_tokens=5000,
                                ),
                            ),
                            KnowledgeBaseTool(
                                name="hotel-guides",
                                description="Find information in the separate hotel benefits guide.",
                                knowledge_sources=[KnowledgeBaseToolKnowledgeSourceReference(name=guide_source)],
                            ),
                        ],
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                created.append(("knowledge_base", base_name))
                stored = await indexes.get_knowledge_base(base_name)
                if not stored.tools or {tool.name for tool in stored.tools} != {"canada-hotels", "hotel-guides"}:
                    raise RuntimeError("The saved tool catalog does not match the configured tools.")
                print("Saved tools:", [tool.name for tool in stored.tools])
                async with KnowledgeBaseRetrievalClient(
                    endpoint=endpoint,
                    knowledge_base_name=base_name,
                    credential=credential,
                    api_version=ApiVersion.V2026_11_01_PREVIEW,
                ) as retrieval:
                    request = KnowledgeBaseRetrievalRequest(
                        intents=[KnowledgeRetrievalSemanticIntent(search="hotel guest benefits")],
                        include_activity=True,
                    )
                    baseline = await retrieval.retrieve(request)
                    validate_preview_retrieval(baseline, all_keys, {hotel_source, guide_source}, expected_keys=all_keys)
                    request.tool_name = "canada-hotels"
                    selected = await retrieval.retrieve(request)
                    validate_preview_retrieval(
                        selected, all_keys, {hotel_source}, expected_keys={"hotel-ca-1", "hotel-ca-2"}
                    )
                    request.tool_name = "hotel-guides"
                    guide_result = await retrieval.retrieve(request)
                    validate_preview_retrieval(guide_result, all_keys, {guide_source}, expected_keys={"hotel-guide"})
                    stored = await indexes.get_knowledge_base(base_name)
                    if not stored.e_tag:
                        raise RuntimeError("An ETag is required before clearing the tools.")
                    stored.tools = []
                    await indexes.create_or_update_knowledge_base(stored, match_condition=MatchConditions.IfNotModified)
                    if (await indexes.get_knowledge_base(base_name)).tools:
                        raise RuntimeError("Custom tools were not cleared.")
                    request.tool_name = None
                    restored = await retrieval.retrieve(request)
                    validate_preview_retrieval(restored, all_keys, {hotel_source, guide_source}, expected_keys=all_keys)
                    print("Clearing tools and tool_name restored normal knowledge-base retrieval.")
            finally:
                await cleanup_preview_resources_async(indexes, created)
    # [END sample_knowledge_base_tools_preview_async]


if __name__ == "__main__":
    asyncio.run(main())
