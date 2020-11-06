# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure_devtools.scenario_tests import ReplayableTest
from search_service_preparer import SearchServicePreparer

CWD = dirname(realpath(__file__))

SCHEMA = open(join(CWD, "hotel_schema.json")).read()
try:
    BATCH = json.load(open(join(CWD, "hotel_small.json")))
except UnicodeDecodeError:
    BATCH = json.load(open(join(CWD, "hotel_small.json"), encoding='utf-8'))
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

TIME_TO_SLEEP = 3

class SearchClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_simple(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = list(client.search(search_text="hotel"))
        assert len(results) == 7

        results = list(client.search(search_text="motel"))
        assert len(results) == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_simple_with_top(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = list(client.search(search_text="hotel", top=3))
        assert len(results) == 3

        results = list(client.search(search_text="motel", top=3))
        assert len(results) == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_filter(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )

        select = ("hotelName", "category", "description")
        results = list(client.search(
            search_text="WiFi",
            filter="category eq 'Budget'",
            select=",".join(select),
            order_by="hotelName desc"
        ))
        assert [x["hotelName"] for x in results] == sorted(
            [x["hotelName"] for x in results], reverse=True
        )
        expected = {
            "category",
            "hotelName",
            "description",
            "@search.score",
            "@search.highlights",
        }
        assert all(set(x) == expected for x in results)
        assert all(x["category"] == "Budget" for x in results)

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_filter_array(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )

        select = ("hotelName", "category", "description")
        results = list(client.search(
            search_text="WiFi",
            filter="category eq 'Budget'",
            select=select,
            order_by="hotelName desc"
        ))
        assert [x["hotelName"] for x in results] == sorted(
            [x["hotelName"] for x in results], reverse=True
        )
        expected = {
            "category",
            "hotelName",
            "description",
            "@search.score",
            "@search.highlights",
        }
        assert all(set(x) == expected for x in results)
        assert all(x["category"] == "Budget" for x in results)

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_counts(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )

        results = client.search(search_text="hotel")
        assert results.get_count() is None

        results = client.search(search_text="hotel", include_total_count=True)
        assert results.get_count() == 7

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_coverage(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )

        results = client.search(search_text="hotel")
        assert results.get_coverage() is None

        results = client.search(search_text="hotel", minimum_coverage=50.0)
        cov = results.get_coverage()
        assert isinstance(cov, float)
        assert cov >= 50.0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_facets_none(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )

        select = ("hotelName", "category", "description")
        results = client.search(search_text="WiFi", select=",".join(select))
        assert results.get_facets() is None

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_search_facets_result(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )

        select = ("hotelName", "category", "description")
        results = client.search(search_text="WiFi",
                                facets=["category"],
                                select=",".join(select)
                                )
        assert results.get_facets() == {
            "category": [
                {"value": "Budget", "count": 4},
                {"value": "Luxury", "count": 1},
            ]
        }

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_autocomplete(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = client.autocomplete(search_text="mot", suggester_name="sg")
        assert results == [{"text": "motel", "query_plus_text": "motel"}]

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_suggest(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = client.suggest(search_text="mot", suggester_name="sg")
        assert results == [
            {"hotelId": "2", "text": "Cheapest hotel in town. Infact, a motel."},
            {"hotelId": "9", "text": "Secret Point Motel"},
        ]
