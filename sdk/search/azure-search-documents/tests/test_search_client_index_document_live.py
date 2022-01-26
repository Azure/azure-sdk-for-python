# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import time

from azure.core.exceptions import HttpResponseError
from azure.search.documents import SearchClient

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator

TIME_TO_SLEEP = 3

class TestSearchClientIndexDocument(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_search_client_index_document(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key)
        # FIXME: Handle the document accounting
        self._test_upload_documents_new(client)
        self._test_upload_documents_existing(client)
        self._test_delete_documents_existing(client)
        self._test_delete_documents_missing(client)
        self._test_merge_documents_existing(client)
        self._test_merge_documents_missing(client)
        self._test_merge_or_upload_documents(client)
        # TODO: Workaround for #22787
        return {}

    def _test_upload_documents_new(self, client):
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

    def _test_upload_documents_existing(self, client):
        DOCUMENTS = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "3", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        results = client.upload_documents(DOCUMENTS)
        assert len(results) == 2
        assert set(x.status_code for x in results) == {200, 201}

    def _test_delete_documents_existing(self, client):
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

    def _test_delete_documents_missing(self, client):
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

    def _test_merge_documents_existing(self, client):
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

    def _test_merge_documents_missing(self, client):
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

    def _test_merge_or_upload_documents(self, client):
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
