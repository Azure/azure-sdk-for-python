# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Asynchronously sets up GraphRAG Zero (Topic Graph) indexes, compares vector
    retrieval modes, and uses topic-aware Search and knowledge base retrieval.

USAGE:
    python sample_topic_graph_preview_async.py

    Install the sample-only dependencies: pip install openai azure-identity aiohttp
    Set AZURE_SEARCH_SERVICE_ENDPOINT, AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT, and AZURE_OPENAI_EMBEDDING_MODEL.
    Supported models are text-embedding-3-small and text-embedding-3-large.
    AZURE_OPENAI_EMBEDDING_DIMENSIONS optionally overrides the model's full size.

    DefaultAzureCredential selects the caller identity (for example, az login).
    Alternatively set AZURE_SEARCH_API_KEY and/or AZURE_OPENAI_API_KEY.
    Without an embedding key, the Search service's system-assigned identity also
    needs Cognitive Services OpenAI User on the embedding resource.
    Both Python and Search must be able to reach the embedding endpoint.

    Use a service supporting 2026-11-01-preview Topic Graph and semantic search.
    Optional AZURE_SEARCH_INDEX_NAME, AZURE_SEARCH_TOPIC_GRAPH_INDEX_NAME,
    AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME, and AZURE_SEARCH_KNOWLEDGE_BASE_NAME
    override the unique generated names. All names must be NEW; existing
    resources are never overwritten. Sidecar names must end in -topicgraph.

    Nine synthetic hotel documents and three sampled document vectors exercise
    the API, not production topic discovery or retrieval quality. No offline
    build tool is needed. Embedding/vectorization calls incur model usage.
    No resources are deleted, even after failure. Record the printed names
    and manage only these newly created sample resources separately.
"""

import asyncio
import os
import time

from sample_utils import get_sample_run_tag, print_retrieval_summary, topic_graph_hotel_documents


async def main():  # pylint: disable=too-many-locals,too-many-statements
    # [START sample_topic_graph_preview_async]
    from openai import AsyncAzureOpenAI
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
    from azure.search.documents.aio import SearchClient
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizer,
        AzureOpenAIVectorizerParameters,
        HnswAlgorithmConfiguration,
        HnswParameters,
        KnowledgeBase,
        KnowledgeSourceReference,
        SearchField,
        SearchIndex,
        SearchIndexFieldReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
        SemanticConfiguration,
        SemanticField,
        SemanticPrioritizedFields,
        SemanticSearch,
        VectorSearch,
        VectorSearchProfile,
        VectorSearchTopicGraphProfile,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalSemanticIntent,
        SearchIndexKnowledgeSourceParams,
    )
    from azure.search.documents.models import (
        BalancedVectorQueryTopicGraph,
        DiverseVectorQueryTopicGraph,
        NoneVectorQueryTopicGraph,
        VectorizableTextQuery,
        VectorizedQuery,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    embedding_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    model = os.environ["AZURE_OPENAI_EMBEDDING_MODEL"]
    model_dimensions = {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}
    dimensions = int(os.environ.get("AZURE_OPENAI_EMBEDDING_DIMENSIONS", model_dimensions[model]))
    run_tag = get_sample_run_tag()
    index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME", f"hotels-grz-{run_tag}")
    sidecar_name = os.environ.get("AZURE_SEARCH_TOPIC_GRAPH_INDEX_NAME", f"hotels-grz-{run_tag}-topicgraph")
    source_name = os.environ.get("AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME", f"hotels-grz-source-{run_tag}")
    base_name = os.environ.get("AZURE_SEARCH_KNOWLEDGE_BASE_NAME", f"hotels-grz-base-{run_tag}")
    if not sidecar_name.endswith("-topicgraph"):
        raise ValueError("Use a NEW sidecar index name ending in -topicgraph.")
    print(f"New sample resources: corpus={index_name}, sidecar={sidecar_name}, source={source_name}, KB={base_name}")
    print("Resources are retained, including after failure; this sample never deletes resources.")
    documents = topic_graph_hotel_documents()
    query_text = "Which hotels offer relaxation, interesting dining, and outdoor adventures?"
    embedding_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    async with DefaultAzureCredential() as identity:
        credential = AzureKeyCredential(search_key) if search_key else identity
        token_provider = (
            None
            if embedding_key
            else get_bearer_token_provider(identity, "https://cognitiveservices.azure.com/.default")
        )
        async with SearchIndexClient(endpoint, credential, api_version="2026-11-01-preview") as index_client:
            corpus = SearchIndex(
                name=index_name,
                fields=[
                    SearchField(name="id", type="Edm.String", key=True, filterable=True),
                    SearchField(name="title", type="Edm.String", searchable=True),
                    SearchField(name="content", type="Edm.String", searchable=True),
                    SearchField(name="topic", type="Edm.String", filterable=True, facetable=True),
                    SearchField(
                        name="content_vector",
                        type="Collection(Edm.Single)",
                        searchable=True,
                        stored=True,
                        retrievable=False,
                        vector_search_dimensions=dimensions,
                        vector_search_profile_name="vectors",
                    ),
                ],
                vector_search=VectorSearch(
                    algorithms=[HnswAlgorithmConfiguration(name="cosine", parameters=HnswParameters(metric="cosine"))],
                    profiles=[
                        VectorSearchProfile(
                            name="vectors", algorithm_configuration_name="cosine", vectorizer_name="embeddings"
                        )
                    ],
                    vectorizers=[
                        AzureOpenAIVectorizer(
                            vectorizer_name="embeddings",
                            parameters=AzureOpenAIVectorizerParameters(
                                resource_url=embedding_endpoint,
                                deployment_name=deployment,
                                model_name=model,
                                api_key=embedding_key,
                            ),
                        )
                    ],
                ),
                semantic_search=SemanticSearch(
                    default_configuration_name="hotels",
                    configurations=[
                        SemanticConfiguration(
                            name="hotels",
                            prioritized_fields=SemanticPrioritizedFields(
                                title_field=SemanticField(field_name="title"),
                                content_fields=[SemanticField(field_name="content")],
                            ),
                        )
                    ],
                ),
            )
            # IfMissing sends If-None-Match: *; a name collision fails instead of updating an index.
            await index_client.create_or_update_index(corpus, match_condition=MatchConditions.IfMissing)
            sidecar = SearchIndex(
                name=sidecar_name,
                fields=[
                    SearchField(name="id", type="Edm.String", key=True),
                    SearchField(name="subject_id", type="Edm.String", retrievable=True),
                    SearchField(
                        name="object_vector",
                        type="Collection(Edm.Single)",
                        searchable=True,
                        stored=True,
                        retrievable=True,
                        vector_search_dimensions=dimensions,
                        vector_search_profile_name="centroids",
                    ),
                ],
                vector_search=VectorSearch(
                    algorithms=[HnswAlgorithmConfiguration(name="cosine", parameters=HnswParameters(metric="cosine"))],
                    profiles=[VectorSearchProfile(name="centroids", algorithm_configuration_name="cosine")],
                ),
            )
            await index_client.create_or_update_index(sidecar, match_condition=MatchConditions.IfMissing)
            await index_client.get_index(sidecar_name)
            corpus = await index_client.get_index(index_name)
            if corpus.vector_search is None:
                raise RuntimeError("The corpus vector configuration was not returned.")
            corpus.vector_search.topic_graph_profiles = [
                VectorSearchTopicGraphProfile(
                    name="hotel-topics",
                    index_name=sidecar_name,
                    default_kind="balanced",
                    default_min_diversity_pool_size=1000,
                )
            ]
            next(field for field in corpus.fields if field.name == "content_vector").topic_graph_profile = (
                "hotel-topics"
            )
            await index_client.create_or_update_index(corpus, match_condition=MatchConditions.IfNotModified)
            linked = await index_client.get_index(index_name)
            if linked.vector_search is None or not linked.vector_search.topic_graph_profiles:
                raise RuntimeError("The linked topic profile was not returned.")
            print(f"Topic profile: {linked.vector_search.topic_graph_profiles[0].as_dict()}")

            async with AsyncAzureOpenAI(
                azure_endpoint=embedding_endpoint,
                api_version="2024-02-01",
                api_key=embedding_key,
                azure_ad_token_provider=token_provider,
            ) as embedding_client:
                embeddings = await embedding_client.embeddings.create(
                    model=deployment,
                    input=[document["content"] for document in documents] + [query_text],
                    dimensions=dimensions,
                    encoding_format="float",
                )
            vectors = [item.embedding for item in sorted(embeddings.data, key=lambda item: item.index)]
            if len(vectors) != len(documents) + 1 or any(len(vector) != dimensions for vector in vectors):
                raise RuntimeError("Embedding response does not match the fixture's count and dimensions.")
            for document, vector in zip(documents, vectors):
                document["content_vector"] = vector
            # Sampled document vectors are mock topic representatives, not computed cluster centroids.
            representatives = [
                {
                    "id": f"mock-{documents[i]['topic']}",
                    "subject_id": documents[i]["topic"],
                    "object_vector": vectors[i],
                }
                for i in (0, 3, 6)
            ]
            async with SearchClient(
                endpoint, index_name, credential, api_version="2026-11-01-preview"
            ) as search_client:
                async with SearchClient(
                    endpoint, sidecar_name, credential, api_version="2026-11-01-preview"
                ) as sidecar_client:
                    if not all(item.succeeded for item in await search_client.upload_documents(documents)):
                        raise RuntimeError("Corpus upload failed.")
                    if not all(item.succeeded for item in await sidecar_client.upload_documents(representatives)):
                        raise RuntimeError("Sidecar upload failed.")
                    deadline = time.monotonic() + 60
                    while (
                        await search_client.get_document_count() != 9 or await sidecar_client.get_document_count() != 3
                    ):
                        if time.monotonic() >= deadline:
                            raise TimeoutError("Corpus and sidecar documents did not become visible.")
                        await asyncio.sleep(2)
                modes = [
                    ("none", NoneVectorQueryTopicGraph()),
                    ("diverse", DiverseVectorQueryTopicGraph(diversity_factor=0.2, min_diversity_pool_size=500)),
                    ("balanced", BalancedVectorQueryTopicGraph(min_diversity_pool_size=500)),
                ]
                for label, mode in modes:
                    results = [
                        result
                        async for result in await search_client.search(
                            vector_queries=[
                                VectorizedQuery(
                                    vector=vectors[-1], fields="content_vector", k_nearest_neighbors=6, topic_graph=mode
                                )
                            ],
                            select=["id", "title", "topic", "content"],
                            top=6,
                        )
                    ]
                    if len(results) != 6 or len({result["id"] for result in results}) != 6:
                        raise RuntimeError(f"{label} did not return six unique documents.")
                    print(f"{label}: {[(result['id'], result['topic']) for result in results]}")
                text_results = [
                    result
                    async for result in await search_client.search(
                        vector_queries=[
                            VectorizableTextQuery(text=query_text, fields="content_vector", k_nearest_neighbors=6)
                        ],
                        select=["id", "title", "topic", "content"],
                        top=6,
                    )
                ]
                if len(text_results) != 6:
                    raise RuntimeError(
                        "Text vectorization with inherited balanced settings returned too few documents."
                    )
                print(f"Text query, inherited balanced profile: {[result['id'] for result in text_results]}")

            source = SearchIndexKnowledgeSource(
                name=source_name,
                description="Synthetic hotel Topic Graph walkthrough",
                results_processing="none",
                search_index_parameters=SearchIndexKnowledgeSourceParameters(
                    search_index_name=index_name,
                    semantic_configuration_name="hotels",
                    source_data_fields=[
                        SearchIndexFieldReference(name=name) for name in ("id", "title", "content", "topic")
                    ],
                    search_fields=[
                        SearchIndexFieldReference(name=name) for name in ("title", "content", "content_vector")
                    ],
                    topic_graph=DiverseVectorQueryTopicGraph(diversity_factor=0.2, min_diversity_pool_size=500),
                ),
            )
            await index_client.create_or_update_knowledge_source(source, match_condition=MatchConditions.IfMissing)
            stored = await index_client.get_knowledge_source(source_name)
            print(f"Stored source settings: {stored.as_dict()['searchIndexParameters']['topicGraph']}")
            await index_client.create_or_update_knowledge_base(
                KnowledgeBase(
                    name=base_name,
                    knowledge_sources=[KnowledgeSourceReference(name=source_name)],
                    output_mode="extractiveData",
                    retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                ),
                match_condition=MatchConditions.IfMissing,
            )
            base = await index_client.get_knowledge_base(base_name)
            print(f"Knowledge base sources: {[source.name for source in base.knowledge_sources]}")
            async with KnowledgeBaseRetrievalClient(
                endpoint, credential, knowledge_base_name=base_name, api_version="2026-11-01-preview"
            ) as retrieval_client:
                overrides = [
                    ("stored diverse", None),
                    (
                        "runtime diverse",
                        DiverseVectorQueryTopicGraph(diversity_factor=0.25, min_diversity_pool_size=2000),
                    ),
                    ("runtime balanced", BalancedVectorQueryTopicGraph()),
                    ("runtime none", NoneVectorQueryTopicGraph()),
                ]
                for label, override in overrides:
                    result = await retrieval_client.retrieve(
                        KnowledgeBaseRetrievalRequest(
                            intents=[KnowledgeRetrievalSemanticIntent(search=query_text)],
                            retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
                            output_mode="extractiveData",
                            include_activity=True,
                            max_runtime_in_seconds=60,
                            max_output_documents=6,
                            knowledge_source_params=[
                                SearchIndexKnowledgeSourceParams(
                                    knowledge_source_name=source_name,
                                    always_query_source=True,
                                    fail_on_error=True,
                                    include_references=True,
                                    include_reference_source_data=True,
                                    results_processing="none",
                                    topic_graph=override,
                                )
                            ],
                        )
                    )
                    if not result.references or not result.activity:
                        raise RuntimeError(f"{label} retrieval did not return references and activity.")
                    print(f"Retrieve with {label}:")
                    print_retrieval_summary(result)
    # [END sample_topic_graph_preview_async]


if __name__ == "__main__":
    asyncio.run(main())
