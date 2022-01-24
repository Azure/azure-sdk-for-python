# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import HttpResponseError
from azure.search.documents import SearchClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import search_decorator

class TestSearchClient(AzureRecordedTestCase):

    def _parse_kwargs(self, **kwargs):
        search_endpoint = kwargs.pop('search_service_endpoint')
        search_api_key = kwargs.pop('search_service_api_key')
        index_name = kwargs.pop('index_name')
        return (search_endpoint, search_api_key, index_name)

    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_get_document_count(self, variables, **kwargs):
        search_endpoint, search_api_key, index_name = self._parse_kwargs(**kwargs)
        client = SearchClient(search_endpoint, index_name, search_api_key)
        assert client.get_document_count() == 10

    # @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    # @recorded_by_proxy
    # def test_get_document(self, variables, **kwargs):
    #     search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
    #     variables = self._update_variables(variables)
    #     index_name = self._parse_variables(variables)
    #     client = SearchClient(search_endpoint, index_name, search_api_key)
    #     for hotel_id in range(1, 11):
    #         result = client.get_document(key=str(hotel_id))
    #         expected = {} #BATCH["value"][hotel_id - 1]
    #         assert result.get("hotelId") == expected.get("hotelId")
    #         assert result.get("hotelName") == expected.get("hotelName")
    #         assert result.get("description") == expected.get("description")

    # @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    # @recorded_by_proxy
    # def test_get_document_missing(self, variables, **kwargs):
    #     search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
    #     variables = self._update_variables(variables)
    #     index_name = self._parse_variables(variables)
    #     client = SearchClient(search_endpoint, index_name, search_api_key)
    #     with pytest.raises(HttpResponseError):
    #         client.get_document(key="1000")
