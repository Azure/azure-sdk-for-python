# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchClient`` search, autocomplete, and suggest operations."""

from __future__ import annotations

from devtools_testutils import AzureRecordedTestCase

from _search_helpers import (
    HOTEL_SUGGESTER_NAME,
    LARGE_HOTEL_DOCUMENT_COUNT,
    SEARCH_SELECT_FIELDS,
    hotel_index,
    live_test,
)


def _assert_budget_results(results):
    assert [result["HotelName"] for result in results] == sorted(
        [result["HotelName"] for result in results], reverse=True
    )
    assert all(result["Category"] == "Budget" for result in results)
    assert all(set(SEARCH_SELECT_FIELDS).issubset(result) for result in results)
    assert all("Rating" not in result for result in results)


class TestSearchClientSearch(AzureRecordedTestCase):
    @live_test()
    def test_search_returns_documents_matching_search_text(self, endpoint):
        index_name = self.get_resource_name("index-search-text")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            hotel_results = list(search_client.search(search_text="hotel"))
            motel_results = list(search_client.search(search_text="motel"))

            assert len(hotel_results) == 7
            assert len(motel_results) == 2

    @live_test()
    def test_search_honors_top(self, endpoint):
        index_name = self.get_resource_name("index-search-top")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            assert len(list(search_client.search(search_text="hotel", top=3))) == 3
            assert len(list(search_client.search(search_text="motel", top=3))) == 2

    @live_test()
    def test_search_accepts_filter_select_and_order_by(self, endpoint):
        index_name = self.get_resource_name("index-search-filter-select")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = list(
                search_client.search(
                    search_text="WiFi",
                    filter="Category eq 'Budget'",
                    select=SEARCH_SELECT_FIELDS,
                    order_by="HotelName desc",
                )
            )

            _assert_budget_results(results)

    @live_test()
    def test_search_get_count_reads_first_page_metadata(self, endpoint):
        index_name = self.get_resource_name("index-search-count")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            assert search_client.search(search_text="hotel", include_total_count=True).get_count() == 7

    @live_test()
    def test_search_get_coverage_reads_first_page_metadata(self, endpoint):
        index_name = self.get_resource_name("index-search-coverage")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            coverage = search_client.search(search_text="hotel", minimum_coverage=50.0).get_coverage()

            assert isinstance(coverage, float)
            assert coverage >= 50.0

    @live_test()
    def test_search_get_facets_reads_first_page_metadata(self, endpoint):
        index_name = self.get_resource_name("index-search-facets")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.search(search_text="WiFi", facets=["Category"], select=SEARCH_SELECT_FIELDS)

            assert results.get_facets() == {
                "Category": [
                    {"value": "Budget", "count": 4},
                    {"value": "Boutique", "count": 1},
                    {"value": "Extended-Stay", "count": 1},
                    {"value": "Luxury", "count": 1},
                ]
            }

    @live_test()
    def test_search_continues_across_service_pages(self, endpoint):
        index_name = self.get_resource_name("index-search-pages")

        with hotel_index(
            self,
            endpoint,
            index_name,
            document_count=LARGE_HOTEL_DOCUMENT_COUNT,
        ) as (search_client, _):
            assert (
                len(list(search_client.search(search_text="")))
                == LARGE_HOTEL_DOCUMENT_COUNT
            )

    @live_test()
    def test_autocomplete_returns_completed_terms(self, endpoint):
        index_name = self.get_resource_name("index-autocomplete")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.autocomplete(search_text="mot", suggester_name=HOTEL_SUGGESTER_NAME)

            assert any(result.text == "motel" for result in results)
            assert any(result.query_plus_text == "motel" for result in results)

    @live_test()
    def test_suggest_returns_matching_documents(self, endpoint):
        index_name = self.get_resource_name("index-suggest")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.suggest(search_text="mot", suggester_name=HOTEL_SUGGESTER_NAME)

            assert {(result["HotelId"], result.text) for result in results} == {
                ("4", "Economy Universe Motel"),
                ("6", "Thunderbird Motel"),
            }
