# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath
import time

import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from search_service_preparer import SearchServicePreparer

CWD = dirname(realpath(__file__))

SCHEMA = open(join(CWD, "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "hotel_small.json")))

from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

TIME_TO_SLEEP = 3

class SearchClientTest(AzureMgmtTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_document_count(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        assert client.get_document_count() == 10

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_document(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        for hotel_id in range(1, 11):
            result = client.get_document(key=str(hotel_id))
            expected = BATCH["value"][hotel_id - 1]
            assert result.get("hotelId") == expected.get("hotelId")
            assert result.get("hotelName") == expected.get("hotelName")
            assert result.get("description") == expected.get("description")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_document_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        with pytest.raises(HttpResponseError):
            client.get_document(key="1000")

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

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_upload_documents_new(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        DOCUMENTS = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "1001", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        results = client.upload_documents(DOCUMENTS)
        assert len(results) == 2
        assert set(x.status_code for x in results) == {201}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 12
        for doc in DOCUMENTS:
            result = client.get_document(key=doc["hotelId"])
            assert result["hotelId"] == doc["hotelId"]
            assert result["hotelName"] == doc["hotelName"]
            assert result["rating"] == doc["rating"]
            assert result["rooms"] == doc["rooms"]

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_upload_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        DOCUMENTS = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "3", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        results = client.upload_documents(DOCUMENTS)
        assert len(results) == 2
        assert set(x.status_code for x in results) == {200, 201}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = client.delete_documents([{"hotelId": "3"}, {"hotelId": "4"}])
        assert len(results) == 2
        assert set(x.status_code for x in results) == {200}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 8

        with pytest.raises(HttpResponseError):
            client.get_document(key="3")

        with pytest.raises(HttpResponseError):
            client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_documents_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = client.delete_documents([{"hotelId": "1000"}, {"hotelId": "4"}])
        assert len(results) == 2
        assert set(x.status_code for x in results) == {200}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 9

        with pytest.raises(HttpResponseError):
            client.get_document(key="1000")

        with pytest.raises(HttpResponseError):
            client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_merge_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = client.merge_documents(
            [{"hotelId": "3", "rating": 1}, {"hotelId": "4", "rating": 2}]
        )
        assert len(results) == 2
        assert set(x.status_code for x in results) == {200}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 10

        result = client.get_document(key="3")
        assert result["rating"] == 1

        result = client.get_document(key="4")
        assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_merge_documents_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = client.merge_documents(
            [{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}]
        )
        assert len(results) == 2
        assert set(x.status_code for x in results) == {200, 404}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 10

        with pytest.raises(HttpResponseError):
            client.get_document(key="1000")

        result = client.get_document(key="4")
        assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_merge_or_upload_documents(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        results = client.merge_or_upload_documents(
            [{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}]
        )
        assert len(results) == 2
        assert set(x.status_code for x in results) == {200, 201}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 11

        result = client.get_document(key="1000")
        assert result["rating"] == 1

        result = client.get_document(key="4")
        assert result["rating"] == 2
