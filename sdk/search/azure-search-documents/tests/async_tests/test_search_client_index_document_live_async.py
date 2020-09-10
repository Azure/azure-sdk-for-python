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
from azure_devtools.scenario_tests import ReplayableTest
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from search_service_preparer import SearchServicePreparer

CWD = dirname(realpath(__file__))

SCHEMA = open(join(CWD, "..", "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "..", "hotel_small.json"), encoding='utf-8'))

from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

TIME_TO_SLEEP = 3

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


class SearchClientTestAsync(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_upload_documents_new(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        DOCUMENTS = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "1001", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]

        async with client:
            results = await client.upload_documents(DOCUMENTS)
            assert len(results) == 2
            assert set(x.status_code for x in results) == {201}

            # There can be some lag before a document is searchable
            if self.is_live:
                time.sleep(TIME_TO_SLEEP)

            assert await client.get_document_count() == 12
            for doc in DOCUMENTS:
                result = await client.get_document(key=doc["hotelId"])
                assert result["hotelId"] == doc["hotelId"]
                assert result["hotelName"] == doc["hotelName"]
                assert result["rating"] == doc["rating"]
                assert result["rooms"] == doc["rooms"]

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_upload_documents_existing(
        self, api_key, endpoint, index_name, **kwargs
    ):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        DOCUMENTS = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "3", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        async with client:
            results = await client.upload_documents(DOCUMENTS)
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200, 201}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_documents_existing(
        self, api_key, endpoint, index_name, **kwargs
    ):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            results = await client.delete_documents(
                [{"hotelId": "3"}, {"hotelId": "4"}]
            )
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200}

            # There can be some lag before a document is searchable
            if self.is_live:
                time.sleep(TIME_TO_SLEEP)

            assert await client.get_document_count() == 8

            with pytest.raises(HttpResponseError):
                await client.get_document(key="3")

            with pytest.raises(HttpResponseError):
                await client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_documents_missing(
        self, api_key, endpoint, index_name, **kwargs
    ):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            results = await client.delete_documents(
                [{"hotelId": "1000"}, {"hotelId": "4"}]
            )
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200}

            # There can be some lag before a document is searchable
            if self.is_live:
                time.sleep(TIME_TO_SLEEP)

            assert await client.get_document_count() == 9

            with pytest.raises(HttpResponseError):
                await client.get_document(key="1000")

            with pytest.raises(HttpResponseError):
                await client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_merge_documents_existing(
        self, api_key, endpoint, index_name, **kwargs
    ):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            results = await client.merge_documents(
                [{"hotelId": "3", "rating": 1}, {"hotelId": "4", "rating": 2}]
            )
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200}

            # There can be some lag before a document is searchable
            if self.is_live:
                time.sleep(TIME_TO_SLEEP)

            assert await client.get_document_count() == 10

            result = await client.get_document(key="3")
            assert result["rating"] == 1

            result = await client.get_document(key="4")
            assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_merge_documents_missing(
        self, api_key, endpoint, index_name, **kwargs
    ):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            results = await client.merge_documents(
                [{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}]
            )
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200, 404}

            # There can be some lag before a document is searchable
            if self.is_live:
                time.sleep(TIME_TO_SLEEP)

            assert await client.get_document_count() == 10

            with pytest.raises(HttpResponseError):
                await client.get_document(key="1000")

            result = await client.get_document(key="4")
            assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_merge_or_upload_documents(
        self, api_key, endpoint, index_name, **kwargs
    ):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            results = await client.merge_or_upload_documents(
                [{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}]
            )
            assert len(results) == 2
            assert set(x.status_code for x in results) == {200, 201}

            # There can be some lag before a document is searchable
            if self.is_live:
                time.sleep(TIME_TO_SLEEP)

            assert await client.get_document_count() == 11

            result = await client.get_document(key="1000")
            assert result["rating"] == 1

            result = await client.get_document(key="4")
            assert result["rating"] == 2
