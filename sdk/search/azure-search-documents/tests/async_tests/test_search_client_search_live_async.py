# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError
from azure.search.documents.aio import SearchClient
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestClientTestAsync(AzureRecordedTestCase):
    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_search_client(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key, retry_backoff_factor=60)
        async with client:
            await self._test_get_search_simple(client)
            await self._test_get_search_simple_with_top(client)
            await self._test_get_search_filter(client)
            await self._test_get_search_filter_array(client)
            await self._test_get_search_counts(client)
            await self._test_get_search_coverage(client)
            await self._test_get_search_facets_none(client)
            await self._test_get_search_facets_result(client)
            await self._test_autocomplete(client)
            await self._test_suggest(client)

    async def _test_get_search_simple(self, client):
        results = []
        async for x in await client.search(search_text="hotel"):
            results.append(x)
        assert len(results) == 7

        results = []
        async for x in await client.search(search_text="motel"):
            results.append(x)
        assert len(results) == 2

    async def _test_get_search_simple_with_top(self, client):
        results = []
        async for x in await client.search(search_text="hotel", top=3):
            results.append(x)
        assert len(results) == 3

        results = []
        async for x in await client.search(search_text="motel", top=3):
            results.append(x)
        assert len(results) == 2

    async def _test_get_search_filter(self, client):
        results = []
        select = ["hotelName", "category", "description"]
        async for x in await client.search(
            search_text="WiFi",
            filter="category eq 'Budget'",
            select=",".join(select),
            order_by="hotelName desc",
        ):
            results.append(x)
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

    async def _test_get_search_filter_array(self, client):
        results = []
        select = ["hotelName", "category", "description"]
        async for x in await client.search(
            search_text="WiFi",
            filter="category eq 'Budget'",
            select=select,
            order_by="hotelName desc",
        ):
            results.append(x)
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

    async def _test_get_search_counts(self, client):
        results = await client.search(search_text="hotel")
        assert await results.get_count() is None

        results = await client.search(search_text="hotel", include_total_count=True)
        assert await results.get_count() == 7

    async def _test_get_search_coverage(self, client):
        results = await client.search(search_text="hotel")
        assert await results.get_coverage() is None

        results = await client.search(search_text="hotel", minimum_coverage=50.0)
        cov = await results.get_coverage()
        assert isinstance(cov, float)
        assert cov >= 50.0

    async def _test_get_search_facets_none(self, client):
        select = ("hotelName", "category", "description")
        results = await client.search(search_text="WiFi", select=",".join(select))
        assert await results.get_facets() is None

    async def _test_get_search_facets_result(self, client):
        select = ("hotelName", "category", "description")
        results = await client.search(search_text="WiFi", facets=["category"], select=",".join(select))
        assert await results.get_facets() == {
            "category": [
                {"value": "Budget", "count": 4},
                {"value": "Luxury", "count": 1},
            ]
        }

    async def _test_autocomplete(self, client):
        results = await client.autocomplete(search_text="mot", suggester_name="sg")
        assert results == [{"text": "motel", "query_plus_text": "motel"}]

    async def _test_suggest(self, client):
        results = await client.suggest(search_text="mot", suggester_name="sg")
        assert results == [
            {"hotelId": "2", "text": "Cheapest hotel in town. Infact, a motel."},
            {"hotelId": "9", "text": "Secret Point Motel"},
        ]

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_large.json")
    @recorded_by_proxy_async
    async def test_search_client_large(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key)
        async with client:
            await self._test_get_search_simple_large(client)

    async def _test_get_search_simple_large(self, client):
        results = []
        async for x in await client.search(search_text=""):
            results.append(x)
        assert len(results) == 60
