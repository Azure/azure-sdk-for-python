# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Create an EKG edge-list graph and provenance index, upload hotel assertions,
    inspect a query plan, and query relationships with supporting evidence IDs.
    Optionally hydrate the supporting source text.

USAGE:
    python sample_graph_index_preview.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT. DefaultAzureCredential uses your developer
    login; alternatively set AZURE_SEARCH_API_KEY to an admin key.
    The service must support the 2026-11-01-preview graph API.
    Optional AZURE_SEARCH_GRAPH_INDEX_NAME and AZURE_SEARCH_GRAPH_SOURCE_INDEX_NAME
    override generated names. Both indexes must be NEW. SAMPLE_RUN_TAG controls
    the generated suffix; AZURE_SEARCH_GRAPH_NAME optionally names the graph.
    Set AZURE_SEARCH_GRAPH_HYDRATE=true only if hydration is already enabled and
    authorized. This sample never enables flags, changes access, or deletes data.
    All newly created resources are retained, including after failure.
"""

import os
import time
import uuid

from sample_utils import get_sample_run_tag, graph_hotel_documents, graph_hotel_index


def main():  # pylint: disable=too-many-locals,too-many-statements
    # [START sample_graph_index_preview]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import ApiVersion, SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SearchableField,
        SimpleField,
    )
    from azure.search.documents.models import (
        GraphQueryProvenanceHydrateDocumentsParameters,
        GraphQueryProvenanceParameters,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    run_tag = f"{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    graph_index = os.environ.get("AZURE_SEARCH_GRAPH_INDEX_NAME", f"hotels-ekg-{run_tag}")
    source_index = os.environ.get("AZURE_SEARCH_GRAPH_SOURCE_INDEX_NAME", f"hotels-ekg-source-{run_tag}")
    graph_name = os.environ.get("AZURE_SEARCH_GRAPH_NAME", "hotels")
    if graph_index == source_index:
        raise ValueError("The graph and provenance index names must be distinct and new.")
    print(f"New retained indexes: graph={graph_index}, provenance={source_index}")
    sources, assertions = graph_hotel_documents(graph_name)
    api_version = ApiVersion.V2026_11_01_PREVIEW

    with DefaultAzureCredential() as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        with SearchIndexClient(endpoint, credential, api_version=api_version) as indexes:
            indexes.create_or_update_index(
                SearchIndex(
                    name=source_index,
                    fields=[
                        SimpleField(name="uid", type="Edm.String", key=True, filterable=True),
                        SearchableField(name="snippet", type="Edm.String"),
                        SimpleField(name="snippet_parent_id", type="Edm.String", filterable=True),
                    ],
                ),
                match_condition=MatchConditions.IfMissing,
            )
            indexes.create_or_update_index(
                graph_hotel_index(graph_index, source_index),
                match_condition=MatchConditions.IfMissing,
            )
        with SearchClient(endpoint, source_index, credential, api_version=api_version) as source_client:
            results = source_client.upload_documents(sources)
            if not all(item.succeeded for item in results):
                raise RuntimeError("Source-document upload did not fully succeed.")
            with SearchClient(endpoint, graph_index, credential, api_version=api_version) as client:
                results = client.upload_documents(assertions)
                if not all(item.succeeded for item in results):
                    raise RuntimeError("Graph-assertion upload did not fully succeed.")
                for attempt in range(30):
                    if client.get_document_count() == 2 and source_client.get_document_count() == 2:
                        break
                    if attempt == 29:
                        raise TimeoutError("The two assertions and source chunks did not become visible.")
                    time.sleep(2)

                gql = (
                    "MATCH (h:Hotel)-[r:operatedBy]->(o:Organization) "
                    "WHERE h.id = 'hotel:harbor' "
                    "RETURN h.name AS hotel, o.name AS organization, r.predicate AS relationship"
                )
                graph_filter = "graph_name eq '" + graph_name.replace("'", "''") + "'"
                plan = client.graph(
                    gql=gql,
                    filter=graph_filter,
                    execution_mode="planOnly",
                    explain=["physicalPlan"],
                    include_statistics=True,
                    include_diagnostics=True,
                )
                if plan.value or not plan.statistics or plan.statistics.query_count != 0:
                    raise RuntimeError("Plan-only execution unexpectedly queried graph data.")
                print("Physical plan:", plan.explain)
                result = client.graph(
                    gql=gql,
                    filter=graph_filter,
                    provenance=GraphQueryProvenanceParameters(kind="ids", max_evidence_per_row=5),
                    include_statistics=True,
                    include_diagnostics=True,
                )
                if len(result.value) != 1 or result.value[0].get("organization") != "Contoso Hospitality":
                    raise RuntimeError("The graph query did not return the seeded hotel/operator relationship.")
                evidence = result.value[0].provenance
                if not evidence or not any(
                    item.edge_id == "assertion-1"
                    and item.chunk_id == "harbor-operator"
                    and item.parent_id == "harbor-brochure"
                    for item in evidence.evidence or []
                ):
                    raise RuntimeError("The graph row did not reference its supporting assertion and source.")
                print("Relationship:", result.value[0])
                print("Statistics:", result.statistics)
                for diagnostic in result.diagnostics or []:
                    print(diagnostic.code, diagnostic.message)

                if os.environ.get("AZURE_SEARCH_GRAPH_HYDRATE", "").lower() == "true":
                    hydrated = client.graph(
                        gql=gql,
                        filter=graph_filter,
                        provenance=GraphQueryProvenanceParameters(
                            kind="hydrate",
                            max_evidence_per_row=5,
                            hydrate_documents=GraphQueryProvenanceHydrateDocumentsParameters(select="uid,snippet"),
                        ),
                        include_statistics=False,
                    )
                    documents = hydrated.provenance_documents
                    if not documents or documents.get("harbor-operator", {}).get("snippet") != sources[0]["snippet"]:
                        raise RuntimeError("Hydration did not return the expected supporting source text.")
                    print("Hydrated source documents:", documents)
                else:
                    print("Hydration not requested; it requires existing service support and authorization.")
    # [END sample_graph_index_preview]


if __name__ == "__main__":
    main()
