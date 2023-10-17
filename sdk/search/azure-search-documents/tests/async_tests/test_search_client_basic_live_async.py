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


class TestSearchClientAsync(AzureRecordedTestCase):
    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_get_document_count(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key)
        async with client:
            assert await client.get_document_count() == 10

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_get_document(self, endpoint, api_key, index_name, index_batch):
        client = SearchClient(endpoint, index_name, api_key)
        async with client:
            for hotel_id in range(1, 11):
                result = await client.get_document(key=str(hotel_id))
                expected = index_batch["value"][hotel_id - 1]
                assert result.get("hotelId") == expected.get("hotelId")
                assert result.get("hotelName") == expected.get("hotelName")
                assert result.get("description") == expected.get("description")

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_get_document_missing(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key)
        async with client:
            with pytest.raises(HttpResponseError):
                await client.get_document(key="1000")
