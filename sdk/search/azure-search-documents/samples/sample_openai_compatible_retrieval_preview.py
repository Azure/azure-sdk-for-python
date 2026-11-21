# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Connect a knowledge base to a customer-controlled OpenAI-compatible provider,
    retrieve seeded hotel facts, and inspect typed search activity and references.
    A GPT-6 model profile selects Responses instead of Chat Completions, with
    an optional native Azure OpenAI GPT-6 configuration.

USAGE:
    python sample_openai_compatible_retrieval_preview.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT, AZURE_SEARCH_COMPATIBLE_CHAT_URI (the full
    HTTPS POST URL, including path/query), and AZURE_SEARCH_COMPATIBLE_CHAT_MODEL.
    Set exactly one of AZURE_SEARCH_COMPATIBLE_CHAT_HEADERS_JSON (a secret JSON
    header map) or AZURE_SEARCH_COMPATIBLE_CHAT_MI_AUDIENCE (the third-party Entra
    application's bare GUID). Optional AZURE_SEARCH_API_KEY authenticates Search.

    The URI/gateway must select the actual model: Search omits model in its
    provider request. A GPT-6 profile such as gpt-6-sol requires a real Responses
    endpoint with stateless tool continuation, not a Chat Completions URL.
    Requires November-preview compatible-provider support, semantic search, and
    one free index slot. No Web knowledge sources. New resources are cleaned up.

    Native Azure OpenAI GPT-6 alternative: set AZURE_SEARCH_GPT6_NATIVE=true and
    AZURE_OPENAI_ENDPOINT. AZURE_OPENAI_GPT6_DEPLOYMENT and AZURE_OPENAI_GPT6_MODEL
    default to gpt-6-sol. Optional AZURE_OPENAI_API_KEY authenticates the model;
    otherwise Search uses its identity. Compatible-provider variables are unused
    in this alternative; native model configuration supplies the deployment.
"""

import os
import uuid

from sample_utils import (
    cleanup_preview_resources,
    compatible_provider_auth,
    get_sample_run_tag,
    prepare_preview_hotel_index,
    preview_hotel_documents,
    validate_preview_retrieval,
    wait_for_knowledge_source_active,
)


def main():  # pylint: disable=too-many-locals
    # [START sample_openai_compatible_retrieval_preview]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeBaseModel,
        KnowledgeBaseOpenAICompatibleModel,
        KnowledgeBaseOpenAICompatibleParameters,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseMessage,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalLowReasoningEffort,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    provider: KnowledgeBaseModel
    if os.environ.get("AZURE_SEARCH_GPT6_NATIVE", "").lower() == "true":
        profile = os.environ.get("AZURE_OPENAI_GPT6_MODEL", "gpt-6-sol")
        if not profile.startswith("gpt-6"):
            raise ValueError("The native GPT-6 scenario requires a supported GPT-6 model profile.")
        provider = KnowledgeBaseAzureOpenAIModel(
            azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                deployment_name=os.environ.get("AZURE_OPENAI_GPT6_DEPLOYMENT", "gpt-6-sol"),
                model_name=profile,
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            )
        )
    else:
        profile = os.environ["AZURE_SEARCH_COMPATIBLE_CHAT_MODEL"]
        provider = KnowledgeBaseOpenAICompatibleModel(
            open_ai_compatible_parameters=KnowledgeBaseOpenAICompatibleParameters(
                uri=os.environ["AZURE_SEARCH_COMPATIBLE_CHAT_URI"],
                model_name=profile,
                **compatible_provider_auth("AZURE_SEARCH_COMPATIBLE_CHAT"),
            )
        )
    name = f"hotels-compatible-chat-{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    source_name, base_name = name + "-source", name + "-kb"
    documents = preview_hotel_documents()
    created: list[tuple[str, str]] = []
    with DefaultAzureCredential(process_timeout=60) as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        with SearchIndexClient(endpoint, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as indexes:
            try:
                prepare_preview_hotel_index(indexes, endpoint, credential, name, documents, created)
                indexes.create_or_update_knowledge_source(
                    SearchIndexKnowledgeSource(
                        name=source_name,
                        search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=name),
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                created.append(("knowledge_source", source_name))
                wait_for_knowledge_source_active(indexes, source_name)
                indexes.create_or_update_knowledge_base(
                    KnowledgeBase(
                        name=base_name,
                        knowledge_sources=[KnowledgeSourceReference(name=source_name)],
                        models=[provider],
                        retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
                        output_mode="extractiveData",
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                created.append(("knowledge_base", base_name))
                with KnowledgeBaseRetrievalClient(
                    endpoint=endpoint,
                    knowledge_base_name=base_name,
                    credential=credential,
                    api_version=ApiVersion.V2026_11_01_PREVIEW,
                ) as retrieval:
                    result = retrieval.retrieve(
                        KnowledgeBaseRetrievalRequest(
                            messages=[
                                KnowledgeBaseMessage(
                                    role="user",
                                    content=[
                                        KnowledgeBaseMessageTextContent(
                                            text=(
                                                "Find the hotel guest benefits, including internet, "
                                                "breakfast, and parking."
                                            )
                                        )
                                    ],
                                )
                            ],
                            include_activity=True,
                        )
                    )
                    activities = validate_preview_retrieval(
                        result, {document["id"] for document in documents}, {source_name}
                    )
                    print("Provider model profile:", profile)
                    print("Search activities:", len(activities))
                    print("Retrieved hotel evidence through the configured model provider.")
                    if profile.startswith("gpt-6"):
                        print(
                            "GPT-6 selects Responses. Confirm stateless tool continuation in provider "
                            "traces; returned Search activity alone does not prove that provider exchange."
                        )
            finally:
                cleanup_preview_resources(indexes, created)
    # [END sample_openai_compatible_retrieval_preview]


if __name__ == "__main__":
    main()
