# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchClient`` search, autocomplete, and suggest operations."""

from __future__ import annotations

from devtools_testutils import AzureRecordedTestCase, remove_batch_sanitizers
from devtools_testutils.helpers import get_recording_id

from _capabilities import require_capability
from _search_helpers import (
    HOTEL_SUGGESTER_NAME,
    LARGE_HOTEL_DOCUMENT_COUNT,
    SEARCH_SELECT_FIELDS,
)
from _search_helpers_async import (
    hotel_index,
    index_resources,
    live_test,
    make_index_client,
    make_search_client,
    upload_documents,
    wait_for_document_count,
)


async def _collect(async_iterable):
    return [item async for item in async_iterable]


def _assert_budget_results(results):
    assert [result["HotelName"] for result in results] == sorted(
        [result["HotelName"] for result in results], reverse=True
    )
    assert all(result["Category"] == "Budget" for result in results)
    assert all(set(SEARCH_SELECT_FIELDS).issubset(result) for result in results)
    assert all("Rating" not in result for result in results)


class TestSearchClientSearchAsync(AzureRecordedTestCase):
    @live_test()
    async def test_search_agentic_returns_documents_and_reasoning_usage(self, endpoint):
        require_capability(
            "azure.search.documents.aio.SearchClient.search.agentic_options",
            "azure.search.documents.models.AgenticSearchOptions.max_runtime_in_seconds",
            "azure.search.documents.models.AgenticSearchDebugInfo",
        )
        from azure.search.documents.models import AgenticSearchDebugInfo, AgenticSearchOptions
        from _preview_helpers import knowledge_base_tool_documents

        # Preserve synthetic document IDs for the result-membership assertion.
        remove_batch_sanitizers(["AZSDK3430"], headers={"x-recording-id": get_recording_id()})
        async with index_resources(self, endpoint, semantic=True, prefix="index-search-agentic") as context:
            async with make_search_client(endpoint, context.index_name, credential=context.credential) as search_client:
                documents = knowledge_base_tool_documents()[0]
                await upload_documents(search_client, documents)
                await wait_for_document_count(self, search_client, len(documents))
                pager = await search_client.search(
                    search_text="Find hotels with complimentary wireless internet.",
                    query_type="agentic",
                    semantic_configuration_name="default",
                    agentic_options=AgenticSearchOptions(max_runtime_in_seconds=30),
                    debug="agentic",
                    select=["id", "content"],
                    top=2,
                )
                results = [result async for result in pager]
                assert results
                assert {result["id"] for result in results} <= {document["id"] for document in documents}
                diagnostics = (await pager.get_debug_info()).agentic
                assert isinstance(diagnostics, AgenticSearchDebugInfo)
                assert diagnostics.termination_reason != "modelFailed"
                assert diagnostics.sub_queries
                assert all(query.search and query.iteration >= 1 for query in diagnostics.sub_queries)
                assert diagnostics.usage.agentic_planning_tokens >= 0
                assert diagnostics.usage.reasoning_tokens >= 0
                assert diagnostics.usage.agentic_planning_tokens + diagnostics.usage.reasoning_tokens > 0

    @live_test()
    async def test_search_more_like_this_excludes_seed_document(self, endpoint):
        require_capability("azure.search.documents.aio.SearchClient.search.more_like_this")
        index_name = self.get_resource_name("index-search-more-like-this")

        async with hotel_index(self, endpoint, index_name) as (search_client, documents):
            results = await _collect(await search_client.search(more_like_this="8", select=["HotelId"], top=3))

            assert results
            result_ids = {result["HotelId"] for result in results}
            assert "8" not in result_ids
            assert result_ids <= {document["HotelId"] for document in documents}

    @live_test()
    async def test_search_random_scoring_preserves_seeded_order(self, endpoint):
        require_capability(
            "azure.search.documents.indexes.models.RandomScoringFunction",
            "azure.search.documents.indexes.models.RandomScoringParameters",
        )
        from azure.search.documents.indexes.models import RandomScoringFunction, RandomScoringParameters, ScoringProfile

        index_name = self.get_resource_name("index-search-random-scoring")
        async with hotel_index(self, endpoint, index_name) as (search_client, documents):
            async with make_index_client(endpoint) as index_client:
                index = await index_client.get_index(index_name)
                index.scoring_profiles = [
                    ScoringProfile(
                        name="random-hotels",
                        functions=[RandomScoringFunction(parameters=RandomScoringParameters(seed_parameter="seed"))],
                    )
                ]
                await index_client.create_or_update_index(index)

            options = {
                "search_text": "*",
                "scoring_profile": "random-hotels",
                "scoring_parameters": ["seed-42"],
                "select": ["HotelId"],
                "top": len(documents),
            }
            first = await _collect(await search_client.search(**options))
            second = await _collect(await search_client.search(**options))

            assert len(first) == len(documents)
            assert {result["HotelId"] for result in first} == {document["HotelId"] for document in documents}
            assert [(result["HotelId"], result["@search.score"]) for result in first] == [
                (result["HotelId"], result["@search.score"]) for result in second
            ]

    @live_test()
    async def test_search_returns_documents_matching_search_text(self, endpoint):
        index_name = self.get_resource_name("index-search-text")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            hotel_results = await _collect(await search_client.search(search_text="hotel"))
            motel_results = await _collect(await search_client.search(search_text="motel"))

            assert len(hotel_results) == 7
            assert len(motel_results) == 2

    @live_test()
    async def test_search_honors_top(self, endpoint):
        index_name = self.get_resource_name("index-search-top")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            assert len(await _collect(await search_client.search(search_text="hotel", top=3))) == 3
            assert len(await _collect(await search_client.search(search_text="motel", top=3))) == 2

    @live_test()
    async def test_search_accepts_filter_select_and_order_by(self, endpoint):
        index_name = self.get_resource_name("index-search-filter-select")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = await _collect(
                await search_client.search(
                    search_text="WiFi",
                    filter="Category eq 'Budget'",
                    select=SEARCH_SELECT_FIELDS,
                    order_by="HotelName desc",
                )
            )

            _assert_budget_results(results)

    @live_test()
    async def test_search_get_count_reads_first_page_metadata(self, endpoint):
        index_name = self.get_resource_name("index-search-count")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = await search_client.search(search_text="hotel", include_total_count=True)
            assert await results.get_count() == 7

    @live_test()
    async def test_search_get_coverage_reads_first_page_metadata(self, endpoint):
        index_name = self.get_resource_name("index-search-coverage")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = await search_client.search(search_text="hotel", minimum_coverage=50.0)
            coverage = await results.get_coverage()

            assert isinstance(coverage, float)
            assert coverage >= 50.0

    @live_test()
    async def test_search_get_facets_reads_first_page_metadata(self, endpoint):
        index_name = self.get_resource_name("index-search-facets")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = await search_client.search(search_text="WiFi", facets=["Category"], select=SEARCH_SELECT_FIELDS)
            assert await results.get_facets() == {
                "Category": [
                    {"value": "Budget", "count": 4},
                    {"value": "Boutique", "count": 1},
                    {"value": "Extended-Stay", "count": 1},
                    {"value": "Luxury", "count": 1},
                ]
            }

    @live_test()
    async def test_search_continues_across_service_pages(self, endpoint):
        index_name = self.get_resource_name("index-search-pages")

        async with hotel_index(
            self,
            endpoint,
            index_name,
            document_count=LARGE_HOTEL_DOCUMENT_COUNT,
        ) as (search_client, _):
            assert len(await _collect(await search_client.search(search_text=""))) == LARGE_HOTEL_DOCUMENT_COUNT

    @live_test()
    async def test_autocomplete_returns_completed_terms(self, endpoint):
        index_name = self.get_resource_name("index-autocomplete")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = await search_client.autocomplete(search_text="mot", suggester_name=HOTEL_SUGGESTER_NAME)

            assert any(result.text == "motel" for result in results)
            assert any(result.query_plus_text == "motel" for result in results)

    @live_test()
    async def test_suggest_returns_matching_documents(self, endpoint):
        index_name = self.get_resource_name("index-suggest")

        async with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = await search_client.suggest(search_text="mot", suggester_name=HOTEL_SUGGESTER_NAME)

            assert {(result["HotelId"], result.text) for result in results} == {
                ("4", "Economy Universe Motel"),
                ("6", "Thunderbird Motel"),
            }
