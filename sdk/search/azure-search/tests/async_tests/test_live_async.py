# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
import json
from os.path import dirname, join, realpath
import time

import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from search_service_preparer import SearchServicePreparer

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

CWD = dirname(realpath(__file__))

SCHEMA = open(join(CWD, "..", "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "..", "hotel_small.json")))

from azure.core.exceptions import HttpResponseError
from azure.search import AutocompleteQuery, SearchApiKeyCredential, SearchQuery, SuggestQuery
from azure.search.aio import SearchIndexClient


def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
    upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        trim_kwargs_from_test_function(test_fn, kwargs)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

    return run

class SearchIndexClientTestAsync(AzureMgmtTestCase):

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_async_get_document_count(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            assert await client.get_document_count() == 10

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_document(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            for hotel_id in range(1, 11):
                result = await client.get_document(key=str(hotel_id))
                expected = BATCH['value'][hotel_id-1]
                assert result.get("hotelId") == expected.get("hotelId")
                assert result.get("hotelName") == expected.get("hotelName")
                assert result.get("description") == expected.get("description")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_document_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            with pytest.raises(HttpResponseError):
                await client.get_document(key="1000")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_search_simple(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            results = []
            async for x in await client.search(query="hotel"):
                results.append(x)
            assert len(results) == 7

            results = []
            async for x in await client.search(query="motel"):
                results.append(x)
            assert len(results) == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_search_filter(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )

        query = SearchQuery(search_text="WiFi")
        query.filter("category eq 'Budget'")
        query.select("hotelName", "category", "description")
        query.order_by("hotelName desc")

        async with client:
            results = []
            async for x in await client.search(query=query):
                results.append(x)
            assert [x['hotelName'] for x in results] == sorted([x['hotelName'] for x in results], reverse=True)
            expected = {"category", "hotelName", "description", "@search.score", "@search.highlights"}
            assert all(set(x) == expected for x in results)
            assert all(x['category'] == "Budget" for x in results)

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_search_facets_none(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )

        query = SearchQuery(search_text="WiFi")
        query.select("hotelName", "category", "description")

        async with client:
            results = await client.search(query=query)
            assert await results.get_facets() is None

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_get_search_facets_result(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )

        query = SearchQuery(search_text="WiFi", facets=["category"])
        query.select("hotelName", "category", "description")

        async with client:
            results = await client.search(query=query)
            assert await results.get_facets() == {'category': [{'value': 'Budget', 'count': 4}, {'value': 'Luxury', 'count': 1}]}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_autocomplete(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            query = AutocompleteQuery(search_text="mot", suggester_name="sg")
            results = await client.autocomplete(query=query)
            assert results == [{'text': 'motel', 'query_plus_text': 'motel'}]

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_suggest(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            query = SuggestQuery(search_text="mot", suggester_name="sg")
            results = await client.suggest(query=query)
            assert results == [
                {'hotelId': '2', 'text': 'Cheapest hotel in town. Infact, a motel.'},
                {'hotelId': '9', 'text': 'Secret Point Motel'},
            ]

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_upload_documents_new(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        DOCUMENTS = [{
            'hotelId': '1000',
            'rating': 5,
            'rooms': [],
            'hotelName': 'Azure Inn',
        },
        {
            'hotelId': '1001',
            'rating': 4,
            'rooms': [],
            'hotelName': 'Redmond Hotel',
        }]

        async with client:
            results = await client.upload_documents(DOCUMENTS)
            assert len(results) == 2
            assert set(x.status_code for x in results) == {201}

            # There can be some lag before a document is searchable
            time.sleep(3)

            assert await client.get_document_count() == 12
            for doc in DOCUMENTS:
                result = await client.get_document(key=doc['hotelId'])
                assert result['hotelId'] == doc['hotelId']
                assert result['hotelName'] == doc['hotelName']
                assert result['rating'] == doc['rating']
                assert result['rooms'] == doc['rooms']

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_upload_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        DOCUMENTS = [{
            'hotelId': '1000',
            'rating': 5,
            'rooms': [],
            'hotelName': 'Azure Inn',
        },
        {
            'hotelId': '3',
            'rating': 4,
            'rooms': [],
            'hotelName': 'Redmond Hotel',
        }]
        async with client:
            results = await client.upload_documents(DOCUMENTS)
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200, 201}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_delete_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            results = await client.delete_documents([{"hotelId": "3"}, {"hotelId": "4"}])
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200}

            # There can be some lag before a document is searchable
            time.sleep(3)

            assert await client.get_document_count() == 8

            with pytest.raises(HttpResponseError):
                await client.get_document(key="3")

            with pytest.raises(HttpResponseError):
                await client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_delete_documents_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            results = await client.delete_documents([{"hotelId": "1000"}, {"hotelId": "4"}])
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200}

            # There can be some lag before a document is searchable
            time.sleep(3)

            assert await client.get_document_count() == 9

            with pytest.raises(HttpResponseError):
                await client.get_document(key="1000")

            with pytest.raises(HttpResponseError):
                await client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_merge_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            results = await client.merge_documents([{"hotelId": "3", "rating": 1}, {"hotelId": "4", "rating": 2}])
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200}

            # There can be some lag before a document is searchable
            time.sleep(3)

            assert await client.get_document_count() == 10

            result = await client.get_document(key="3")
            assert result["rating"] == 1

            result = await client.get_document(key="4")
            assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_merge_documents_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            results = await client.merge_documents([{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}])
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200, 404}

            # There can be some lag before a document is searchable
            time.sleep(3)

            assert await client.get_document_count() == 10

            with pytest.raises(HttpResponseError):
                await client.get_document(key="1000")

            result = await client.get_document(key="4")
            assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    @await_prepared_test
    async def test_merge_or_upload_documents(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(
            endpoint, index_name, SearchApiKeyCredential(api_key)
        )
        async with client:
            results = await client.merge_or_upload_documents([{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}])
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200, 201}

            # There can be some lag before a document is searchable
            time.sleep(3)

            assert await client.get_document_count() == 11

            result = await client.get_document(key="1000")
            assert result["rating"] == 1

            result = await client.get_document(key="4")
            assert result["rating"] == 2
