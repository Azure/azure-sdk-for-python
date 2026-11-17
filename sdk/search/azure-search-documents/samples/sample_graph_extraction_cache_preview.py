# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Extract an EKG from hotel documents using an inline ontology and enrichment
    cache, query relationships, and retrieve through a knowledge base.
    Optionally hydrate graph evidence with supporting source text.

USAGE:
    python sample_graph_extraction_cache_preview.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT, AZURE_STORAGE_CONNECTION_STRING,
    AZURE_STORAGE_CONTAINER, AZURE_STORAGE_FOLDER, AZURE_SEARCH_GRAPH_CACHE_CONNECTION_STRING,
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_CHAT_MODEL,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT, and AZURE_OPENAI_EMBEDDING_MODEL.
    First upload data/hotel_graph.txt into an approved, nonempty folder prefix
    with Blob content type text/plain.
    The sample reads that folder only and never uploads or deletes source blobs.

    Use a November-preview service supporting EKG extraction/cache/KB retrieval.
    Native Blob soft delete must already be enabled before ingestion. The cache
    requires GPv2 storage with Blob and Table endpoints and read/write access.
    ADLS Gen2, ACL ingestion, and sensitivity-label ingestion are not supported.
    ResourceId storage connections use Search's managed identity: source reads
    require Storage Blob Data Reader; cache writes require Storage Blob Data
    Contributor and Storage Table Data Contributor. Native OpenAI deployments
    must be reachable and authorized for Search (Cognitive Services OpenAI User
    when no AZURE_OPENAI_API_KEY is supplied). Optional AZURE_SEARCH_API_KEY uses
    an admin key instead of the caller's DefaultAzureCredential.

    Optional AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME, AZURE_SEARCH_KNOWLEDGE_BASE_NAME,
    AZURE_SEARCH_GRAPH_NAME, and SAMPLE_RUN_TAG customize new resource names.
    Set AZURE_SEARCH_GRAPH_HYDRATE=true only with existing hydration support.
    This sample does not demonstrate deferred attachment or ontology replacement.
    Cache hits need execution telemetry; unchanged chunks alone do not prove reuse.
    Resources and cache data are retained on failure and success.
    No permissions, flags, storage settings, or shared data change.
"""

import os
import uuid

from sample_utils import (
    get_sample_run_tag,
    graph_hotel_ontology,
    print_retrieval_summary,
    wait_for_graph_synchronization,
    wait_for_knowledge_source_active,
)


def main():  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
    # [START sample_graph_extraction_cache_preview]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import ApiVersion, SearchClient
    from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
    from azure.search.documents.indexes.models import (
        AzureBlobKnowledgeSource,
        AzureBlobKnowledgeSourceParameters,
        AzureOpenAIVectorizerParameters,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeSourceGraphExtractionParameters,
        KnowledgeSourceGraphOntology,
        KnowledgeSourceReference,
    )
    from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        AgentRuntimeGraphHydrateDocumentsParams,
        AgentRuntimeGraphParams,
        AgentRuntimeGraphProvenanceParams,
        AzureBlobKnowledgeSourceParams,
        KnowledgeBaseMessage,
        KnowledgeBaseMessageTextContent,
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalLowReasoningEffort,
        KnowledgeSourceAzureOpenAIVectorizer,
        KnowledgeSourceCache,
        KnowledgeSourceIngestionParameters,
    )
    from azure.search.documents.models import GraphQueryProvenanceParameters

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    folder = os.environ["AZURE_STORAGE_FOLDER"].strip()
    if not folder or not folder.strip("/\\") or folder.startswith(("/", "\\")):
        raise ValueError("Use an approved nonempty Blob folder prefix, not the container root.")
    run_tag = f"{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    source_name = os.environ.get("AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME", f"hotels-ekg-cache-{run_tag}")
    base_name = os.environ.get("AZURE_SEARCH_KNOWLEDGE_BASE_NAME", f"hotels-ekg-base-{run_tag}")
    graph_name = os.environ.get("AZURE_SEARCH_GRAPH_NAME", "hotels")
    api_version = ApiVersion.V2026_11_01_PREVIEW
    print(f"New retained resources: source={source_name}, KB={base_name}, graph={graph_name}")
    print("Source blobs are read-only. Generated Search resources and enrichment cache data are retained.")
    chat = KnowledgeBaseAzureOpenAIModel(
        azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
            resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
            deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            model_name=os.environ["AZURE_OPENAI_CHAT_MODEL"],
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        )
    )
    ontology = KnowledgeSourceGraphOntology(kind="inline", name="hotel-relationships", value=graph_hotel_ontology())
    graph_extraction = KnowledgeSourceGraphExtractionParameters(graph_name=graph_name, ontology=ontology)
    source = AzureBlobKnowledgeSource(
        name=source_name,
        description="Hotel graph extraction with an inline ontology and enrichment cache.",
        azure_blob_parameters=AzureBlobKnowledgeSourceParameters(
            connection_string=os.environ["AZURE_STORAGE_CONNECTION_STRING"],
            container_name=os.environ["AZURE_STORAGE_CONTAINER"],
            folder_path=folder,
            is_adls_gen2=False,
            ingestion_parameters=KnowledgeSourceIngestionParameters(
                embedding_model=KnowledgeSourceAzureOpenAIVectorizer(
                    azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                        resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                        deployment_name=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
                        model_name=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
                        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                    )
                ),
                chat_completion_model=chat,
                content_extraction_mode="minimal",
                disable_image_verbalization=True,
                cache=KnowledgeSourceCache(
                    storage_connection_string=os.environ["AZURE_SEARCH_GRAPH_CACHE_CONNECTION_STRING"],
                    enable_reprocessing=True,
                ),
            ),
            graph_extraction=graph_extraction,
        ),
    )
    with DefaultAzureCredential() as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        with (
            SearchIndexClient(endpoint, credential, api_version=api_version) as indexes,
            SearchIndexerClient(endpoint, credential, api_version=api_version) as indexers,
        ):
            indexes.create_or_update_knowledge_source(source, match_condition=MatchConditions.IfMissing)
            wait_for_knowledge_source_active(indexes, source_name)
            stored = indexes.get_knowledge_source(source_name)
            cache = stored.as_dict()["azureBlobParameters"]["ingestionParameters"]["cache"]
            if "storageConnectionString" in cache:
                raise RuntimeError("The write-only cache connection string was returned by GET.")
            resources = stored.as_dict()["azureBlobParameters"]["createdResources"]
            if not all(
                isinstance(resources.get(kind), str) and resources[kind].startswith(source_name + "-")
                for kind in ("datasource", "indexer", "skillset", "index", "graphIndex")
            ):
                raise RuntimeError("The source did not return its own generated resource names.")
            print("Generated resources:", resources)
            data_source = indexers.get_data_source_connection(resources["datasource"])
            if data_source.container.query != folder:
                raise RuntimeError("The generated data source does not preserve the approved Blob folder scope.")
            indexers.get_indexer(resources["indexer"])
            indexers.get_skillset(resources["skillset"])
            profile = indexes.get_index(resources["graphIndex"]).graph_profile
            if not profile or profile.provenance_index_name != resources["index"]:
                raise RuntimeError("The managed graph is not bound to its generated provenance index.")
            fields = profile.fields
            graph_filter = fields.graph_name_field + " eq '" + graph_name.replace("'", "''") + "'"
            wait_for_graph_synchronization(indexes, indexers, source_name, resources["indexer"])

            with (
                SearchClient(endpoint, resources["index"], credential, api_version=api_version) as chunks,
                SearchClient(
                    endpoint,
                    resources["graphIndex"],
                    credential,
                    api_version=api_version,
                ) as graph,
            ):
                if chunks.get_document_count() == 0:
                    raise RuntimeError("Ingestion completed without searchable source chunks.")
                assertions = list(
                    graph.search(
                        search_text="*",
                        filter=graph_filter,
                        select=[
                            fields.assertion_id_field,
                            fields.subject_field,
                            fields.predicate_field,
                            fields.object_field,
                            fields.source_chunk_id_field,
                            fields.source_parent_id_field,
                        ],
                        top=50,
                    )
                )
                if not assertions:
                    raise RuntimeError("Synchronization completed without extracting any graph assertions.")
                print("Extracted assertions:", assertions)
                result = graph.graph(
                    gql=(
                        "MATCH (h:Hotel)-[r:operatedBy]->(o:Organization) "
                        "RETURN h.name AS hotel, o.name AS organization LIMIT 10"
                    ),
                    filter=graph_filter,
                    provenance=GraphQueryProvenanceParameters(kind="ids", max_evidence_per_row=5),
                    include_statistics=True,
                    include_diagnostics=True,
                )
                expected = {
                    "Historic Harbor Hotel": "Contoso Hospitality",
                    "Mountain View Inn": "Alpine Hospitality",
                }
                matching_rows = [
                    row for row in result.value if (row.get("hotel"), row.get("organization")) in expected.items()
                ]
                if not matching_rows:
                    raise RuntimeError("No extracted hotel/operator relationship agrees with data/hotel_graph.txt.")
                if not any(row.provenance and row.provenance.evidence for row in matching_rows):
                    raise RuntimeError("Extracted relationships did not return source provenance.")
                print("Extracted hotel/operator relationships:", result.value)

                indexes.create_or_update_knowledge_base(
                    KnowledgeBase(
                        name=base_name,
                        knowledge_sources=[KnowledgeSourceReference(name=source_name)],
                        models=[chat],
                        retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
                        output_mode="extractiveData",
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                with KnowledgeBaseRetrievalClient(
                    endpoint=endpoint,
                    knowledge_base_name=base_name,
                    credential=credential,
                    api_version=api_version,
                ) as retrieval:
                    response = retrieval.retrieve(
                        KnowledgeBaseRetrievalRequest(
                            messages=[
                                KnowledgeBaseMessage(
                                    role="user",
                                    content=[
                                        KnowledgeBaseMessageTextContent(
                                            text="Using the knowledge graph, which organizations operate the hotels?"
                                        )
                                    ],
                                )
                            ],
                            include_activity=True,
                            output_mode="extractiveData",
                            knowledge_source_params=[
                                AzureBlobKnowledgeSourceParams(
                                    knowledge_source_name=source_name,
                                    include_references=True,
                                    include_reference_source_data=True,
                                    graph_parameters=AgentRuntimeGraphParams(
                                        include_query=True,
                                        provenance=AgentRuntimeGraphProvenanceParams(kind="none"),
                                    ),
                                )
                            ],
                        )
                    )
                    print_retrieval_summary(response)
                    activities = [item.as_dict() for item in response.activity or [] if item.type == "graphSearch"]
                    references = [item for item in response.references or [] if item.type == "graphSearch"]
                    if not references or not any(
                        item.get("graphSearchArguments", {}).get("gql") for item in activities
                    ):
                        raise RuntimeError("KB retrieval did not return graph references and generated GQL.")
                    print("Graph retrieval activities:", activities)
                    for reference in references:
                        print("Graph reference:", reference.source_data)

                    if os.environ.get("AZURE_SEARCH_GRAPH_HYDRATE", "").lower() == "true":
                        schema = indexes.get_index(resources["index"])
                        text_field = next(
                            (
                                field.name
                                for field in schema.fields
                                if field.name in {"snippet", "content"} and field.retrievable is not False
                            ),
                            None,
                        )
                        key_field = next(field.name for field in schema.fields if field.key)
                        if not text_field:
                            raise RuntimeError(
                                "The provenance index does not expose a supported retrievable text field."
                            )
                        hydrated = retrieval.retrieve(
                            KnowledgeBaseRetrievalRequest(
                                messages=[
                                    KnowledgeBaseMessage(
                                        role="user",
                                        content=[
                                            KnowledgeBaseMessageTextContent(
                                                text=(
                                                    "Using only the knowledge graph's operatedBy relationship, "
                                                    "which organizations operate the hotels? "
                                                    "Include supporting source text from graph provenance."
                                                )
                                            )
                                        ],
                                    )
                                ],
                                include_activity=True,
                                output_mode="extractiveData",
                                knowledge_source_params=[
                                    AzureBlobKnowledgeSourceParams(
                                        knowledge_source_name=source_name,
                                        include_references=True,
                                        include_reference_source_data=True,
                                        graph_parameters=AgentRuntimeGraphParams(
                                            include_query=True,
                                            provenance=AgentRuntimeGraphProvenanceParams(
                                                kind="hydrate",
                                                hydrate_documents=AgentRuntimeGraphHydrateDocumentsParams(
                                                    select=f"{key_field},{text_field}",
                                                    top=5,
                                                ),
                                            ),
                                        ),
                                    )
                                ],
                            )
                        )
                        if not any(
                            item.type == "graphSearch" and (item.source_data or {}).get(text_field)
                            for item in hydrated.references or []
                        ):
                            raise RuntimeError("Hydrated KB retrieval did not return supporting source text.")
                        print_retrieval_summary(hydrated)
                        print(
                            "Hydrated graph references:",
                            [item.source_data for item in hydrated.references or []],
                        )
                    else:
                        print("Hydration not requested; graph-row retrieval does not prove source hydration.")

                print("Cache is configured; cache hits require separate execution/service telemetry.")
    # [END sample_graph_extraction_cache_preview]


if __name__ == "__main__":
    main()
