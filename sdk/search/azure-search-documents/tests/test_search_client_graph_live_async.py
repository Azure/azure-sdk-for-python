# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchClient.graph``."""

from devtools_testutils import AzureRecordedTestCase

from _capabilities import require_capability
from _search_helpers_async import (
    live_test,
    make_index_client,
    make_search_client,
    safe_delete,
    upload_documents,
    wait_for_document_count,
)


class TestSearchClientGraphAsync(AzureRecordedTestCase):
    @live_test()
    async def test_graph_returns_scoped_rows_and_assertion_provenance(self, endpoint):
        require_capability(
            "azure.search.documents.aio.SearchClient.graph",
            "azure.search.documents.models.GraphQueryResult",
            "azure.search.documents.models.GraphQueryProvenanceParameters",
        )
        from azure.search.documents.models import GraphQueryProvenanceParameters, GraphQueryResult
        from _preview_helpers import graph_documents, graph_index_configuration

        index_name = self.get_resource_name("index-graph-query")
        async with make_index_client(endpoint) as index_client:
            try:
                await index_client.create_index(graph_index_configuration(index_name))
                async with make_search_client(endpoint, index_name) as search_client:
                    documents = graph_documents()
                    await upload_documents(search_client, documents)
                    await wait_for_document_count(self, search_client, len(documents))
                    result = await search_client.graph(
                        gql=(
                            "MATCH (h:Hotel)-[:locatedIn]->(c:City) "
                            "WHERE h.id = 'hotel:harbor' RETURN c.name AS city"
                        ),
                        filter="graph_name eq 'hotel-locations'",
                        include_statistics=True,
                        include_diagnostics=True,
                        provenance=GraphQueryProvenanceParameters(kind="ids", max_evidence_per_row=1),
                    )

                assert isinstance(result, GraphQueryResult)
                assert [row["city"] for row in result.value] == ["Seattle"]
                assert not any(diagnostic.severity == "error" for diagnostic in result.diagnostics or [])
                assert result.statistics.execution_mode == "execute"
                evidence = result.value[0].provenance
                assert evidence.kind == "ids"
                assert len(evidence.evidence) == 1
                assert evidence.evidence[0].edge_id == "assertion-seattle"
                assert evidence.evidence[0].chunk_id == "chunk-seattle"
                assert evidence.evidence[0].parent_id == "brochure-seattle"
            finally:
                await safe_delete(index_client.delete_index, index_name)
