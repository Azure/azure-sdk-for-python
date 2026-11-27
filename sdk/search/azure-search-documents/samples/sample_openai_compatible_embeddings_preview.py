# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Configure an OpenAI-compatible query vectorizer, upload matching ada-002
    hotel embeddings, and compare a paraphrased spa query against a stored
    spa-description vector. This actually calls the configured provider
    through Search; it does not demonstrate managed ingestion-time embedding.

USAGE:
    python sample_openai_compatible_embeddings_preview.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_COMPATIBLE_EMBEDDING_URI
    to the complete embeddings POST URL. Set exactly one of
    AZURE_SEARCH_COMPATIBLE_EMBEDDING_HEADERS_JSON (secret header map) or
    AZURE_SEARCH_COMPATIBLE_EMBEDDING_MI_AUDIENCE (third-party application GUID).
    Optional AZURE_SEARCH_API_KEY authenticates Search. The provider URI/gateway
    must select text-embedding-ada-002 with 1536 dimensions to match the supplied
    fixtures; Search omits model in the outbound request. No redirects.
    Requires November-preview compatible vectorization and one free index slot.
    Only the newly created index is cleaned up.
"""

import json
import os
from pathlib import Path
import time
import uuid

from sample_utils import cleanup_preview_resources, compatible_provider_auth, get_sample_run_tag


def main():  # pylint: disable=too-many-locals
    # [START sample_openai_compatible_embeddings_preview]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import ApiVersion, SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        ExhaustiveKnnAlgorithmConfiguration,
        OpenAICompatibleVectorizer,
        OpenAICompatibleVectorizerParameters,
        SearchField,
        SearchIndex,
        SearchableField,
        SimpleField,
        VectorSearch,
        VectorSearchProfile,
    )
    from azure.search.documents.models import VectorizableTextQuery, VectorizedQuery

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    parameters = OpenAICompatibleVectorizerParameters(
        uri=os.environ["AZURE_SEARCH_COMPATIBLE_EMBEDDING_URI"],
        model_name="text-embedding-ada-002",
        dimensions=1536,
        **compatible_provider_auth("AZURE_SEARCH_COMPATIBLE_EMBEDDING"),
    )
    name = f"hotels-compatible-embedding-{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    data = Path(__file__).resolve().parent / "data"
    fixture = json.loads((data / "hotels_compatible_ada002.json").read_text(encoding="utf-8"))
    documents = fixture["documents"]
    query_vector = documents[0]["DescriptionVector"]
    if fixture["model"] != "text-embedding-ada-002" or any(
        len(document["DescriptionVector"]) != 1536 for document in documents
    ):
        raise ValueError("The stored vectors and compatible endpoint must use the same 1536-dimensional model.")
    created: list[tuple[str, str]] = []
    with DefaultAzureCredential(process_timeout=60) as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        with SearchIndexClient(endpoint, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as indexes:
            try:
                indexes.create_or_update_index(
                    SearchIndex(
                        name=name,
                        fields=[
                            SimpleField(name="HotelId", type="Edm.String", key=True),
                            SearchableField(name="HotelName", type="Edm.String"),
                            SearchableField(name="Description", type="Edm.String"),
                            SearchField(
                                name="DescriptionVector",
                                type="Collection(Edm.Single)",
                                searchable=True,
                                vector_search_dimensions=1536,
                                vector_search_profile_name="compatible-profile",
                            ),
                        ],
                        vector_search=VectorSearch(
                            algorithms=[ExhaustiveKnnAlgorithmConfiguration(name="exact")],
                            profiles=[
                                VectorSearchProfile(
                                    name="compatible-profile",
                                    algorithm_configuration_name="exact",
                                    vectorizer_name="compatible",
                                )
                            ],
                            vectorizers=[
                                OpenAICompatibleVectorizer(
                                    vectorizer_name="compatible", open_ai_compatible_parameters=parameters
                                )
                            ],
                        ),
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                created.append(("index", name))
                with SearchClient(endpoint, name, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as search:
                    if not all(item.succeeded for item in search.upload_documents(documents)):
                        raise RuntimeError("The vector fixtures could not be uploaded.")
                    for _ in range(30):
                        if search.get_document_count() == len(documents):
                            break
                        time.sleep(2)
                    else:
                        raise TimeoutError("The vector fixtures did not become searchable.")
                    control = list(
                        search.search(
                            vector_queries=[
                                VectorizedQuery(
                                    vector=query_vector,
                                    fields="DescriptionVector",
                                    k_nearest_neighbors=5,
                                    exhaustive=True,
                                )
                            ],
                            select=["HotelId", "HotelName"],
                            top=5,
                        )
                    )
                    generated = list(
                        search.search(
                            vector_queries=[
                                VectorizableTextQuery(
                                    text="Relaxing hotel with a pool and spa treatments.",
                                    fields="DescriptionVector",
                                    k_nearest_neighbors=5,
                                    exhaustive=True,
                                )
                            ],
                            select=["HotelId", "HotelName"],
                            top=5,
                        )
                    )
                    if (
                        not control
                        or not generated
                        or control[0]["HotelId"] != "spa"
                        or generated[0]["HotelId"] != "spa"
                    ):
                        raise RuntimeError("Provider-vectorized text did not retrieve the expected reference neighbor.")
                    print("Provider-vectorized hotel matches:", generated)
                    print("Both the stored spa vector and provider-vectorized paraphrase ranked the spa hotel first.")
            finally:
                cleanup_preview_resources(indexes, created)
    # [END sample_openai_compatible_embeddings_preview]


if __name__ == "__main__":
    main()
