# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.core.exceptions import HttpResponseError
from azure.search.documents import SearchClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator

class TestSearchClient(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_get_document_count(self, **kwargs):
        endpoint = kwargs.pop("endpoint")
        api_key = kwargs.pop("api_key")
        index_name = kwargs.pop("index_name")
        client = SearchClient(endpoint, index_name, api_key)
        assert client.get_document_count() == 10

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_get_document(self, **kwargs):
        endpoint = kwargs.pop("endpoint")
        api_key = kwargs.pop("api_key")
        index_name = kwargs.pop("index_name")
        index_batch = kwargs.pop("index_batch")
        client = SearchClient(endpoint, index_name, api_key)
        for hotel_id in range(1, 11):
            result = client.get_document(key=str(hotel_id))
            expected = index_batch["value"][hotel_id - 1]
            assert result.get("hotelId") == expected.get("hotelId")
            assert result.get("hotelName") == expected.get("hotelName")
            assert result.get("description") == expected.get("description")

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_get_document_missing(self, **kwargs):
        endpoint = kwargs.pop("endpoint")
        api_key = kwargs.pop("api_key")
        index_name = kwargs.pop("index_name")
        client = SearchClient(endpoint, index_name, api_key)
        with pytest.raises(HttpResponseError):
            client.get_document(key="1000")
