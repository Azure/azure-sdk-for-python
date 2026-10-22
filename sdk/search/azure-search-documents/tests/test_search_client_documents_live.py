# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchClient`` document lookup operations."""

from __future__ import annotations

import pytest

from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import HOTEL_DOCUMENT_COUNT, HOTEL_LOOKUP_FIELDS, MISSING_HOTEL_ID, hotel_index, live_test


class TestSearchClientDocumentLookup(AzureRecordedTestCase):
    @live_test()
    def test_get_document_count_returns_index_document_count(self, endpoint):
        index_name = self.get_resource_name("index-get-document-count")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT

    @live_test()
    def test_get_document_returns_lookup_document_for_key(self, endpoint):
        index_name = self.get_resource_name("index-get-document")

        with hotel_index(self, endpoint, index_name) as (search_client, index_documents):
            for expected_document in index_documents:
                result = search_client.get_document(key=expected_document["HotelId"])

                for field_name in HOTEL_LOOKUP_FIELDS:
                    assert result.get(field_name) == expected_document.get(field_name)

    @live_test()
    def test_get_document_raises_for_invalid_key(self, endpoint):
        index_name = self.get_resource_name("index-get-document-invalid-key")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            with pytest.raises(HttpResponseError):
                search_client.get_document(key=MISSING_HOTEL_ID)
