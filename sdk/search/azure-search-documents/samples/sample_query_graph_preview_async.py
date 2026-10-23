# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    Asynchronously query an existing hotel graph and inspect provenance and diagnostics.
    Mirrors SearchIndexGraphDocuments.json from the pinned 2026-11-01-preview spec.
    This read-only sample does not create resources.

USAGE:
    python sample_query_graph_preview_async.py

    Set SEARCH_SERVICE_ENDPOINT, SEARCH_API_KEY, SEARCH_GRAPH_INDEX_NAME, and
    SEARCH_GRAPH_NAME. The graph must contain Hotel entities related to
    Organization entities through worksFor, with hotel:ada identifying a Hotel.
"""

import asyncio
import os
import uuid


async def sample_query_graph():
    # [START sample_query_graph_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.aio import SearchClient
    from azure.search.documents.models import GraphQueryProvenanceParameters

    run_tag = str(uuid.uuid4())
    graph_name = os.environ["SEARCH_GRAPH_NAME"].replace("'", "''")
    async with SearchClient(
        endpoint=os.environ["SEARCH_SERVICE_ENDPOINT"],
        index_name=os.environ["SEARCH_GRAPH_INDEX_NAME"],
        credential=AzureKeyCredential(os.environ["SEARCH_API_KEY"]),
        api_version=ApiVersion.V2026_11_01_PREVIEW,
    ) as client:
        result = await client.graph(
            gql=(
                "MATCH (h:Hotel)-[r:worksFor]->(o:Organization) "
                "WHERE h.id = 'hotel:ada' RETURN o.name AS organization"
            ),
            filter=f"graph_name eq '{graph_name}'",
            include_statistics=False,
            provenance=GraphQueryProvenanceParameters(kind="ids", max_evidence_per_row=5),
            client_request_id=run_tag,
            accept="application/json;odata.metadata=none",
        )
        for row in result.value:
            print(row)
            print(row.provenance)
        for diagnostic in result.diagnostics or []:
            print(diagnostic.code, diagnostic.message)
    # [END sample_query_graph_preview_async]


if __name__ == "__main__":
    asyncio.run(sample_query_graph())
