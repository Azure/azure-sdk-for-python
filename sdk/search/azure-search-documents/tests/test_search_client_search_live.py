# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.search.documents import SearchClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchClient(AzureRecordedTestCase):
    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_search_client(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key, retry_backoff_factor=60)
        self._test_get_search_simple(client)
        self._test_get_search_simple_with_top(client)
        self._test_get_search_filter(client)
        self._test_get_search_filter_array(client)
        self._test_get_search_counts(client)
        self._test_get_search_coverage(client)
        self._test_get_search_facets_none(client)
        self._test_get_search_facets_result(client)
        self._test_autocomplete(client)
        self._test_suggest(client)

    def _test_get_search_simple(self, client):
        results = list(client.search(search_text="hotel"))
        assert len(results) == 7

        results = list(client.search(search_text="motel"))
        assert len(results) == 2

    def _test_get_search_simple_with_top(self, client):
        results = list(client.search(search_text="hotel", top=3))
        assert len(results) == 3

        results = list(client.search(search_text="motel", top=3))
        assert len(results) == 2

    def _test_get_search_filter(self, client):
        select = ["hotelName", "category", "description"]
        results = list(
            client.search(
                search_text="WiFi",
                filter="category eq 'Budget'",
                select=",".join(select),
                order_by="hotelName desc",
            )
        )
        assert [x["hotelName"] for x in results] == sorted([x["hotelName"] for x in results], reverse=True)
        expected = {
            "category",
            "hotelName",
            "description",
            "@search.score",
            "@search.reranker_score",
            "@search.highlights",
            "@search.captions",
        }
        assert all(set(x) == expected for x in results)
        assert all(x["category"] == "Budget" for x in results)

    def _test_get_search_filter_array(self, client):
        select = ["hotelName", "category", "description"]
        results = list(
            client.search(
                search_text="WiFi",
                filter="category eq 'Budget'",
                select=select,
                order_by="hotelName desc",
            )
        )
        assert [x["hotelName"] for x in results] == sorted([x["hotelName"] for x in results], reverse=True)
        expected = {
            "category",
            "hotelName",
            "description",
            "@search.score",
            "@search.reranker_score",
            "@search.highlights",
            "@search.captions",
        }
        assert all(set(x) == expected for x in results)
        assert all(x["category"] == "Budget" for x in results)

    def _test_get_search_counts(self, client):
        results = client.search(search_text="hotel")
        assert results.get_count() is None

        results = client.search(search_text="hotel", include_total_count=True)
        assert results.get_count() == 7

    def _test_get_search_coverage(self, client):
        results = client.search(search_text="hotel")
        assert results.get_coverage() is None

        results = client.search(search_text="hotel", minimum_coverage=50.0)
        cov = results.get_coverage()
        assert isinstance(cov, float)
        assert cov >= 50.0

    def _test_get_search_facets_none(self, client):
        select = ("hotelName", "category", "description")
        results = client.search(search_text="WiFi", select=",".join(select))
        assert results.get_facets() is None

    def _test_get_search_facets_result(self, client):
        select = ("hotelName", "category", "description")
        results = client.search(search_text="WiFi", facets=["category"], select=",".join(select))
        assert results.get_facets() == {
            "category": [
                {"value": "Budget", "count": 4},
                {"value": "Luxury", "count": 1},
            ]
        }

    def _test_autocomplete(self, client):
        results = client.autocomplete(search_text="mot", suggester_name="sg")
        assert results == [{"text": "motel", "query_plus_text": "motel"}]

    def _test_suggest(self, client):
        results = client.suggest(search_text="mot", suggester_name="sg")
        assert results == [
            {"hotelId": "2", "text": "Cheapest hotel in town. Infact, a motel."},
            {"hotelId": "9", "text": "Secret Point Motel"},
        ]
