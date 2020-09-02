# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
import json
from os.path import dirname, join, realpath

import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure_devtools.scenario_tests import ReplayableTest

from search_service_preparer import SearchServicePreparer

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

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
    async def test_async_get_document_count(
        self, api_key, endpoint, index_name, **kwargs
    ):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            assert await client.get_document_count() == 10

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_document(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            for hotel_id in range(1, 11):
                result = await client.get_document(key=str(hotel_id))
                expected = BATCH["value"][hotel_id - 1]
                assert result.get("hotelId") == expected.get("hotelId")
                assert result.get("hotelName") == expected.get("hotelName")
                assert result.get("description") == expected.get("description")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_document_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        async with client:
            with pytest.raises(HttpResponseError):
                await client.get_document(key="1000")
